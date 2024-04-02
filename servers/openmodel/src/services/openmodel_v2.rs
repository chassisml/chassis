use crate::config::ChassisConfig;
use crate::metrics::{
    DATA_DRIFT_COLLECTOR, DATA_PROCESSED_SIZE_IN_BYTES, INFERENCES_PERFORMED, INFERENCE_REQUESTS,
};
use crate::preprocessor::preprocess;
use crate::proto::openmodel::v2::inference_service_server::InferenceService;
use crate::proto::openmodel::v2::predict_response::Timings;
use crate::proto::openmodel::v2::{
    ContainerInfoRequest, OpenModelContainer, PredictRequest, PredictResponse, ShutdownRequest,
    ShutdownResponse, StatusRequest, StatusResponse,
};
use crate::runners::python::PythonModelRunner;
use crate::runners::ModelRunner;
use bytes::Bytes;
use lazy_static::lazy_static;
use prost::Message;
use std::path::PathBuf;
use std::str::FromStr;
use std::sync::Arc;
use std::time::Instant;
use tokio::sync::broadcast::Sender;
use tonic::{Code, Request, Response, Status};
use tonic_health::server::HealthReporter;
use tracing::info;

lazy_static! {
    static ref CONTAINER_INFO: OpenModelContainer = {
        // Attempt to find the model metadata file. First check to see if the
        // CONTAINER_METADATA_PATH has been explicitly set. If so, use that. If not,
        // We expect that MODEL_DIR could be set and we can expect that its file
        // structure is the standard Chassis-generated layout. Finally, if neither
        // are set then let's assume we're inside a standard container and look
        // at the default data directory path for a Chassis-generated container.
        let container_info_path = match std::env::var("CONTAINER_METADATA_PATH") {
            Ok(p) => PathBuf::from(p),
            Err(_) => match std::env::var("MODEL_DIR") {
                Ok(model_dir) => PathBuf::from(model_dir).join("container_info"),
                Err(_) => PathBuf::from_str("/app/data/container_info")
                    .expect("unable to create path to model metadata"),
            },
        };
        let data = std::fs::read(container_info_path).expect("unable to read container info");
        let data_buf = Bytes::from(data);
        OpenModelContainer::decode(data_buf).expect("unable to decode container info")
    };
}

pub struct OpenModelV2Service {
    config: ChassisConfig,
    #[allow(dead_code)]
    health_reporter: HealthReporter,
    tx_shutdown: Sender<()>,
    // The following property needs to be wrapped in an Arc so that the struct can be cloned to
    // various tokio threads without re-loading or re-creating the Python runner.
    runner: Arc<PythonModelRunner>,
}

impl OpenModelV2Service {
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

    fn set_trace_fields(&self) {
        tracing::Span::current().record(
            "model_identifier",
            &tracing::field::display(self.config.model.identifier.as_str()),
        );
        tracing::Span::current().record(
            "model_version",
            &tracing::field::display(self.config.model.version.as_str()),
        );
    }
}

#[tonic::async_trait]
impl InferenceService for OpenModelV2Service {
    #[tracing::instrument(
        name = "Status",
        skip(self, _request),
        fields(
            model_identifier = tracing::field::Empty,
            model_version = tracing::field::Empty,
        )
    )]
    async fn status(
        &self,
        _request: Request<StatusRequest>,
    ) -> Result<Response<StatusResponse>, Status> {
        self.set_trace_fields();
        Ok(Response::new(StatusResponse {
            status: crate::proto::openmodel::v2::status_response::Status::Ok.into(),
        }))
    }

    #[tracing::instrument(
        name = "GetContainerInfo",
        skip(self, _request),
        fields(
            model_identifier = tracing::field::Empty,
            model_version = tracing::field::Empty,
        )
    )]
    async fn get_container_info(
        &self,
        _request: Request<ContainerInfoRequest>,
    ) -> Result<Response<OpenModelContainer>, Status> {
        self.set_trace_fields();
        Ok(Response::new(CONTAINER_INFO.clone()))
    }

    #[tracing::instrument(
        name = "Predict",
        skip(self, request),
        fields(
            model_identifier = tracing::field::Empty,
            model_version = tracing::field::Empty,
            data_processed = tracing::field::Empty,
        )
    )]
    async fn predict(
        &self,
        request: Request<PredictRequest>,
    ) -> Result<Response<PredictResponse>, Status> {
        let rpc_start = Instant::now();
        self.set_trace_fields();
        let labels = &[
            self.config.model.identifier.as_str(),
            self.config.model.version.as_str(),
        ];
        INFERENCE_REQUESTS.with_label_values(labels).inc();

        // Consume the gRPC request wrapper into the protobuf payload.
        let request = request.into_inner();

        // Clone the tags here before the request gets moved and is no longer accessible.
        // let tags = request.get_ref().tags.clone();

        let preprocessing_start = Instant::now();
        let (inputs, total_size_in_bytes) =
            preprocess(request.inputs).map_err(|e| Status::new(Code::Internal, e.to_string()))?;
        tracing::Span::current().record(
            "data_processed",
            &tracing::field::display(format!("{}", total_size_in_bytes as u64)),
        );
        DATA_PROCESSED_SIZE_IN_BYTES
            .with_label_values(labels)
            .inc_by(total_size_in_bytes as u64);
        let preprocessing_duration = preprocessing_start.elapsed();

        let model_start = Instant::now();
        let mut response = self
            .runner
            .predict(inputs)
            .map_err(|e| Status::new(Code::Internal, e.to_string()))?;
        INFERENCES_PERFORMED.with_label_values(labels).inc();
        let model_duration = model_start.elapsed();

        // Record drift metrics.
        if let Some(drift) = response.drift.as_ref() {
            if let Some(data_drift) = drift.data_drift.as_ref() {
                DATA_DRIFT_COLLECTOR
                    .with_label_values(labels)
                    .observe(data_drift.score);
            }
        }

        let rpc_duration = rpc_start.elapsed();
        // Extend the response with some information that we've been tracking here.
        response.timings = Some(Timings {
            model_execution: prost_types::Duration::try_from(model_duration).ok(),
            preprocessing: prost_types::Duration::try_from(preprocessing_duration).ok(),
            postprocessing: prost_types::Duration::from_str("0").ok(),
            formatting: prost_types::Duration::from_str("0").ok(),
            total: prost_types::Duration::try_from(rpc_duration).ok(),
        });
        response.tags = request.tags;
        Ok(Response::new(response))
    }

    #[tracing::instrument(
        name = "Shutdown",
        skip(self, _request),
        fields(
            model_identifier = tracing::field::Empty,
            model_version = tracing::field::Empty,
        )
    )]
    async fn shutdown(
        &self,
        _request: Request<ShutdownRequest>,
    ) -> Result<Response<ShutdownResponse>, Status> {
        self.set_trace_fields();
        info!("Shutdown request received via gRPC request.");
        let _ = self.tx_shutdown.send(());
        Ok(Response::new(ShutdownResponse {}))
    }
}
