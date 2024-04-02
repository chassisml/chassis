use crate::proto::openmodel::v2::{
    prediction_output, DataDrift, DataResult, ModelDrift, PredictResponse, PredictionOutput,
    TextResult,
};
use pyo3::FromPyObject;

#[derive(Debug, FromPyObject)]
pub struct PredictionResultProxy {
    pub outputs: Vec<PredictionOutputProxy>,
    pub success: bool,
    pub error: Option<String>,
    pub drift: Option<ModelDriftProxy>,
}

impl Into<PredictResponse> for PredictionResultProxy {
    fn into(self) -> PredictResponse {
        let mut predict_response = PredictResponse::default();
        predict_response.success = self.success;
        predict_response.error = self.error.unwrap_or("".to_string());
        predict_response.outputs = self.outputs.into_iter().map(|o| o.into()).collect();
        predict_response.drift = self.drift.map(|dd| dd.into());
        predict_response
    }
}

#[derive(Debug, FromPyObject)]
pub enum PredictionOutputProxy {
    TextOutput { key: String, text: String },
    DataOutput { key: String, data: DataOutputProxy },
}

impl Into<PredictionOutput> for PredictionOutputProxy {
    fn into(self) -> PredictionOutput {
        let mut prediction_output = PredictionOutput::default();
        match self {
            PredictionOutputProxy::TextOutput { key, text } => {
                prediction_output.key = key;
                prediction_output.result =
                    Some(prediction_output::Result::Text(TextResult { text }))
            }
            PredictionOutputProxy::DataOutput { key, data } => {
                prediction_output.key = key;
                prediction_output.result = Some(prediction_output::Result::Data(data.into()))
            }
        }
        prediction_output
    }
}

#[derive(Debug, FromPyObject)]
pub struct DataOutputProxy {
    data: Vec<u8>,
    content_type: Option<String>,
}

impl Into<DataResult> for DataOutputProxy {
    fn into(self) -> DataResult {
        DataResult {
            data: self.data,
            content_type: self
                .content_type
                .unwrap_or("application/octet-stream".to_string()),
        }
    }
}

#[derive(Debug, FromPyObject)]
pub struct ModelDriftProxy {
    pub data_drift: Option<DataDriftProxy>,
}

impl Into<ModelDrift> for ModelDriftProxy {
    fn into(self) -> ModelDrift {
        ModelDrift {
            data_drift: self.data_drift.map(|dd| dd.into()),
        }
    }
}
#[derive(Debug, FromPyObject)]
pub struct DataDriftProxy {
    pub score: f64,
}

impl Into<DataDrift> for DataDriftProxy {
    fn into(self) -> DataDrift {
        DataDrift { score: self.score }
    }
}
