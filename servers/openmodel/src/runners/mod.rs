use crate::proto::openmodel::v2::PredictResponse;
use crate::types::{BatchedModelInputData, BatchedModelOutputData, ModelInputData};

pub(crate) mod python;
mod python_interchange;

pub(crate) trait ModelRunner {
    fn predict(&self, inputs: ModelInputData) -> Result<PredictResponse, anyhow::Error>;
    fn predict_v1(
        &self,
        inputs: BatchedModelInputData,
    ) -> Result<BatchedModelOutputData, anyhow::Error>;
}
