use crate::proto::openmodel::v2::DataResult;
use crate::proto::openmodel::v2::PredictionOutput;
use crate::types::ModelOutputData;

#[tracing::instrument(name = "Format", skip(outputs))]
pub fn format_as_predict_result(
    outputs: &ModelOutputData,
) -> Result<Vec<PredictionOutput>, anyhow::Error> {
    let results = outputs
        .iter()
        .map(|(k, v)| {
            let mut data = DataResult::default();
            data.data = v.clone();
            PredictionOutput {
                key: k.to_string(),
                result: Some(crate::proto::openmodel::v2::prediction_output::Result::Data(data)),
            }
        })
        .collect();
    Ok(results)
}
