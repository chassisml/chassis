use std::borrow::Cow;
use std::collections::HashMap;

pub(crate) type ModelInputData<'a> = HashMap<String, Cow<'a, [u8]>>;
pub(crate) type ModelOutputData = HashMap<String, Vec<u8>>;
pub(crate) type BatchedModelInputData<'a> = Vec<ModelInputData<'a>>;
pub(crate) type BatchedModelOutputData = Vec<ModelOutputData>;
