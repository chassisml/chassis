use anyhow::Context;
use axum::routing::get;
use axum::Router;
use std::sync::Arc;
use tokio::signal;
use tokio::signal::unix::{signal, SignalKind};
use tonic::transport::Server;
use tracing::info;

use crate::config::{load_configuration, ChassisConfig};
use crate::proto::openmodel::v2::inference_service_server::InferenceServiceServer;

use crate::metrics::metrics_handler;
use crate::proto::openmodel::v1::modzy_model_server::ModzyModelServer;
use crate::runners::python::PythonModelRunner;
use crate::services::openmodel_v1::OpenModelV1Service;
use crate::services::openmodel_v2::OpenModelV2Service;
use crate::telemetry::init_tracing_subscriber;
use crate::util::graceful_shutdown;

pub struct OpenModelServer {
    config: Option<ChassisConfig>,
    metrics_enabled: bool,
    reflection_enabled: bool,
    v1_service_enabled: bool,
    v2_service_enabled: bool,
}

impl OpenModelServer {
    pub fn build() -> Self {
        OpenModelServer {
            config: None,
            metrics_enabled: true,
            reflection_enabled: true,
            v1_service_enabled: true,
            v2_service_enabled: false,
        }
    }

    pub fn with_config(mut self, config: ChassisConfig) -> Self {
        self.config = Some(config);
        self
    }

    pub fn enable_metrics(mut self, enabled: bool) -> Self {
        self.metrics_enabled = enabled;
        self
    }

    pub fn enable_reflection(mut self, enabled: bool) -> Self {
        self.reflection_enabled = enabled;
        self
    }

    pub fn enable_v1_service(mut self, enabled: bool) -> Self {
        self.v1_service_enabled = enabled;
        self
    }

    pub fn enable_v2_service(mut self, enabled: bool) -> Self {
        self.v2_service_enabled = enabled;
        self
    }

    pub async fn start(self) -> Result<(), anyhow::Error> {
        // If no config was provided, try loading it from the environment.
        let config = self.config.unwrap_or(load_configuration()?);

        // Configure tracing.
        init_tracing_subscriber(config.log.level.clone(), std::io::stdout, &config);

        // Configure the reflection service.
        let mut reflection_service = tonic_reflection::server::Builder::configure();
        reflection_service = reflection_service
            .register_encoded_file_descriptor_set(tonic_health::pb::FILE_DESCRIPTOR_SET);
        if self.v1_service_enabled {
            reflection_service = reflection_service.register_encoded_file_descriptor_set(
                crate::proto::openmodel::v1::FILE_DESCRIPTOR_SET,
            );
        }
        if self.v2_service_enabled {
            reflection_service = reflection_service.register_encoded_file_descriptor_set(
                crate::proto::openmodel::v2::FILE_DESCRIPTOR_SET,
            );
        }

        // Configure the gRPC health service.
        let (mut health_reporter, health_service) = tonic_health::server::health_reporter();
        if self.v1_service_enabled {
            health_reporter
                .set_serving::<ModzyModelServer<OpenModelV1Service>>()
                .await;
        }
        if self.v2_service_enabled {
            health_reporter
                .set_serving::<InferenceServiceServer<OpenModelV2Service>>()
                .await;
        }

        // Create the shutdown channels for the model and metrics servers.
        let (tx_graceful_shutdown, mut rx_graceful_shutdown) =
            tokio::sync::broadcast::channel::<()>(1);

        // Start the metrics server if enabled.
        let metrics_server = match self.metrics_enabled {
            true => {
                // Start the metrics server.
                let metrics_addr = format!("0.0.0.0:{}", config.metrics.port);
                info!("Metrics server listening on {}", metrics_addr);
                let metrics_listener = tokio::net::TcpListener::bind(&metrics_addr)
                    .await
                    .context("unable to start metrics server")?;
                let metrics_app = Router::new().route("/metrics", get(metrics_handler));
                let rx_metrics_shutdown = tx_graceful_shutdown.subscribe();
                Some(tokio::spawn(async move {
                    axum::serve(metrics_listener, metrics_app)
                        .with_graceful_shutdown(graceful_shutdown(rx_metrics_shutdown))
                        .await
                        .expect("unable to start metrics server");
                }))
            }
            false => None,
        };

        // Configure the model server address.
        let model_addr = format!("0.0.0.0:{}", config.model.port)
            .parse()
            .expect("invalid model server address");

        // Create the model runner.
        let runner = Arc::new(PythonModelRunner::init(config.clone())?);

        // Build the model server.
        let mut model_server_builder = Server::builder().add_service(health_service);
        if self.reflection_enabled {
            model_server_builder = model_server_builder.add_service(
                reflection_service
                    .build()
                    .context("unable to create the gRPC reflection server")?,
            );
        } else {
            // If reflection is not enabled then we don't need to keep the service around and
            // taking up memory.
            drop(reflection_service);
        }
        if self.v1_service_enabled {
            let v1_service = OpenModelV1Service::configure(
                config.clone(),
                runner.clone(),
                tx_graceful_shutdown.clone(),
                health_reporter.clone(),
            )?;
            model_server_builder =
                model_server_builder.add_service(ModzyModelServer::new(v1_service));
        }
        if self.v2_service_enabled {
            let v2_service = OpenModelV2Service::configure(
                config.clone(),
                runner.clone(),
                tx_graceful_shutdown.clone(),
                health_reporter.clone(),
            )?;
            model_server_builder =
                model_server_builder.add_service(InferenceServiceServer::new(v2_service));
        }

        // Start the model server.
        let model_server = tokio::spawn(async move {
            let rx_model_shutdown = tx_graceful_shutdown.subscribe();
            model_server_builder
                .serve_with_shutdown(model_addr, graceful_shutdown(rx_model_shutdown))
                .await
                .expect("unable to start model server");
        });

        // Now that we've spawned our servers, listen for any of the various shutdown signals and then
        // gracefully shut everything down.
        let mut term_signal =
            signal(SignalKind::terminate()).expect("must be run on a UNIX-compatible system");
        let graceful = tokio::select! {
            _ = term_signal.recv() => false,
            _ = signal::ctrl_c() => false,
            _ = rx_graceful_shutdown.recv() => true,
        };

        info!("Received a shutdown signal.");

        // Only attempt a graceful shutdown if requested. A graceful shutdown will occur when the
        // shutdown signal is sent from the gRPC endpoint. Otherwise, we'll let the process clean
        // itself up.
        if graceful {
            // Wait until the model server stops.
            model_server.await.expect("model server did not shut down");
            // Wait until the metrics server stops.
            if let Some(metrics_server) = metrics_server {
                metrics_server
                    .await
                    .expect("metrics server did not shut down");
            }
            info!("Servers have shut down.");
        }

        info!("Exiting.");

        Ok(())
    }
}
