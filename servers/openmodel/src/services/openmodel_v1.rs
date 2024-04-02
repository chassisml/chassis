use std::path::PathBuf;
use std::str::FromStr;
use std::sync::Arc;

use bytes::Bytes;
use lazy_static::lazy_static;
use prost::Message;
use tokio::sync::broadcast::Sender;
use tonic::{Code, Request, Response, Status};
use tracing::info;

use crate::config::ChassisConfig;
use crate::preprocessor::preprocess_v1;
use crate::proto::openmodel::v1::modzy_model_server::ModzyModel;
use crate::proto::openmodel::v1::{
    OutputItem, RunRequest, RunResponse, ShutdownRequest, ShutdownResponse, StatusRequest,
    StatusResponse,
};
use tonic_health::server::HealthReporter;

use crate::runners::python::PythonModelRunner;
use crate::runners::ModelRunner;

lazy_static! {
    static ref MODEL_METADATA: StatusResponse = {
        // Attempt to find the model metadata file. First check to see if the
        // MODEL_METADATA_PATH has been explicitly set. If so, use that. If not,
        // We expect that MODEL_DIR could be set and we can expect that its file
        // structure is the standard Chassis-generated layout. Finally, if neither
        // are set then let's assume we're inside a standard container and look
        // at the default data directory path for a Chassis-generated container.
        let metadata_path = match std::env::var("MODEL_METADATA_PATH") {
            Ok(p) => PathBuf::from(p),
            Err(_) => match std::env::var("MODEL_DIR") {
                Ok(model_dir) => PathBuf::from(model_dir).join("model_info"),
                Err(_) => PathBuf::from_str("/app/data/model_info")
                    .expect("unable to create path to model metadata"),
            },
        };
        let metadata_file = std::fs::read(metadata_path).expect("unable to read metadata");
        let metadata_buf = Bytes::from(metadata_file);
        let mut decoded_metadata =
            StatusResponse::decode(metadata_buf).expect("unable to decode metadata");
        decoded_metadata.status_code = 200;
        decoded_metadata.status = "200 OK".into();
        decoded_metadata
    };
}

#[derive(Debug)]
pub struct OpenModelV1Service {
    config: ChassisConfig,
    #[allow(dead_code)]
    health_reporter: HealthReporter,
    tx_shutdown: Sender<()>,
    // The following property needs to be wrapped in an Arc so that the struct can be cloned to
    // various tokio threads without re-loading or re-creating the Python runner.
    runner: Arc<PythonModelRunner>,
}

impl OpenModelV1Service {
    pub fn configure(
        config: ChassisConfig,
        runner: Arc<PythonModelRunner>,
        tx_shutdown: Sender<()>,
        health_reporter: HealthReporter,
    ) -> Result<Self, anyhow::Error> {
        Ok(Self {
            config,
            health_reporter,
            tx_shutdown,
            runner,
        })
    }
}

#[tonic::async_trait]
impl ModzyModel for OpenModelV1Service {
    #[tracing::instrument(name = "Status", skip(self, _request))]
    async fn status(
        &self,
        _request: Request<StatusRequest>,
    ) -> Result<Response<StatusResponse>, Status> {
        Ok(Response::new(MODEL_METADATA.clone()))
    }

    #[tracing::instrument(
        name = "Predict",
        skip(self, request),
        fields(
            model_identifier = tracing::field::Empty,
            model_version = tracing::field::Empty,
            batch_size = tracing::field::Empty,
            data_processed = tracing::field::Empty,
        )
    )]
    async fn run(&self, request: Request<RunRequest>) -> Result<Response<RunResponse>, Status> {
        tracing::Span::current().record(
            "model_identifier",
            &tracing::field::display(self.config.model.identifier.as_str()),
        );
        tracing::Span::current().record(
            "model_version",
            &tracing::field::display(self.config.model.version.as_str()),
        );

        // Consume the gRPC request wrapper into the protobuf payload.
        let request = request.into_inner();

        let (inputs, total_size_in_bytes) = preprocess_v1(request.inputs)
            .map_err(|e| Status::new(Code::Internal, e.to_string()))?;
        tracing::Span::current().record(
            "batch_size",
            &tracing::field::display(format!("{}", inputs.len())),
        );
        tracing::Span::current().record(
            "data_processed",
            &tracing::field::display(format!("{}", total_size_in_bytes as u64)),
        );

        let outputs: Vec<OutputItem> = self
            .runner
            .predict_v1(inputs)
            .map_err(|e| Status::new(Code::Internal, e.to_string()))?
            .iter()
            .map(|o| {
                OutputItem {
                    output: o.clone(),
                    // TODO - actually set this properly
                    success: true,
                }
            })
            .collect();

        // Return the response.
        Ok(Response::new(RunResponse {
            status_code: 200,
            status: "OK".to_string(),
            message: "Inference executed".to_string(),
            outputs,
        }))
    }

    #[tracing::instrument(name = "Shutdown", skip(self, _request))]
    async fn shutdown(
        &self,
        _request: Request<ShutdownRequest>,
    ) -> Result<Response<ShutdownResponse>, Status> {
        info!("Shutdown request received. Shutting down the server.");
        let _ = self.tx_shutdown.send(());
        Ok(Response::new(ShutdownResponse {
            status_code: 0,
            status: "".to_string(),
            message: "".to_string(),
        }))
    }
}
