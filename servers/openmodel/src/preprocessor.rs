use crate::proto::openmodel::v1::InputItem;
use crate::proto::openmodel::v2::predict_request::input::Source;
use crate::proto::openmodel::v2::predict_request::Input;
use crate::types::{BatchedModelInputData, ModelInputData};
use std::borrow::Cow;
use std::collections::HashMap;

#[tracing::instrument(name = "Preprocess v2", skip(inputs))]
pub fn preprocess<'a>(inputs: Vec<Input>) -> Result<(ModelInputData<'a>, usize), anyhow::Error> {
    let mut total_size_in_bytes: usize = 0;
    let mut input_data: ModelInputData = HashMap::with_capacity(inputs.len());
    for input in inputs {
        if let Some(source) = input.source {
            let val = match source {
                Source::Text(t) => Cow::from(t.into_bytes()),
                Source::Data(d) => Cow::from(d),
            };
            total_size_in_bytes += val.len();
            input_data.insert(input.key, val);
        }
    }
    Ok((input_data, total_size_in_bytes))
}

#[tracing::instrument(name = "Preprocess v1", skip(inputs))]
pub fn preprocess_v1<'a>(
    inputs: Vec<InputItem>,
) -> Result<(BatchedModelInputData<'a>, usize), anyhow::Error> {
    let mut total_size_in_bytes: usize = 0;
    let mut batched_inputs: BatchedModelInputData = Vec::with_capacity(inputs.len());
    for (idx, input_item) in inputs.into_iter().enumerate() {
        let mut input_data: ModelInputData = HashMap::with_capacity(input_item.input.len());
        for (key, val) in input_item.input {
            total_size_in_bytes += val.len();
            let val = Cow::from(val);
            input_data.insert(key, val);
        }
        batched_inputs.insert(idx, input_data);
    }
    Ok((batched_inputs, total_size_in_bytes))
}
