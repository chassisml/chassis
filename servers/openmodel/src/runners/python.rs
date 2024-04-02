use crate::config::ChassisConfig;
use crate::proto::openmodel::v2::PredictResponse;
use crate::runners::python_interchange::PredictionResultProxy;
use crate::runners::ModelRunner;
use crate::types::{BatchedModelInputData, BatchedModelOutputData, ModelInputData};
use anyhow::Context;
use pyo3::prelude::PyModule;
use pyo3::{IntoPy, Py, PyAny, Python};
use std::path::PathBuf;
use tracing::info;

const PYTHON_MODEL_KEY: &str = "__chassis_model";

#[derive(Debug)]
pub struct PythonModelRunner {
    runner: Py<PyAny>,
}

impl PythonModelRunner {
    pub fn init(config: ChassisConfig) -> Result<Self, anyhow::Error> {
        let model_dir = PathBuf::from(config.model.dir);
        let model_file = model_dir.join("model.pkl");
        let predict_fn = load_python_module(model_file, PYTHON_MODEL_KEY)?;
        Ok(PythonModelRunner { runner: predict_fn })
    }
}

impl ModelRunner for PythonModelRunner {
    #[tracing::instrument(name = "Call Python for OpenModel v2", skip(inputs))]
    fn predict(&self, inputs: ModelInputData) -> Result<PredictResponse, anyhow::Error> {
        Python::with_gil(|py| {
            // Step 1: Take all the inputs and convert them to Python runtime objects.
            let py_inputs = inputs.into_py(py);

            // Step 2: Grab the model we previously loaded and get a callable reference to the predict
            // function.
            let predict_fn = &self
                .runner
                .getattr(py, "predict")
                .context("model runner does not have a predict method")?;

            // Step 3: Pass the Python-ified inputs into the predict function. Ideally, there will be
            // at most one additional allocation for the Python object's backing memory. Even better
            // would be to figure out how to do this without an additional allocation.
            let py_outputs = predict_fn.call1(py, (py_inputs,))?;

            // Step 4: Take returned Python response and convert it back into Rust types.
            let outputs: PredictionResultProxy = py_outputs.extract(py)?;

            // Step 5: Convert (again) to the expected gRPC response.
            let response: PredictResponse = outputs.into();
            Ok(response)
        })
    }

    #[tracing::instrument(name = "Call Python for OpenModel v1", skip(inputs), fields(batch_size = tracing::field::Empty))]
    fn predict_v1(
        &self,
        inputs: BatchedModelInputData,
    ) -> Result<BatchedModelOutputData, anyhow::Error> {
        tracing::Span::current().record(
            "batch_size",
            &tracing::field::display(format!("{}", inputs.len())),
        );

        Python::with_gil(|py| {
            // Step 1: Take all the inputs and convert them to Python runtime objects.
            let py_inputs = inputs.into_py(py);

            // Step 2: Grab the model we previously loaded and get a callable reference to the predict
            // function.
            let predict_fn = &self
                .runner
                .getattr(py, "predict")
                .context("model runner does not have a predict method")?;

            // Step 3: Pass the Python-ified inputs into the predict function. Ideally, there will be
            // at most one additional allocation for the Python object's backing memory. Even better
            // would be to figure out how to do this without an additional allocation.
            let py_outputs = predict_fn.call1(py, (py_inputs,))?;

            // Step 4: Take returned Python response and convert it back into Rust types.
            let outputs: BatchedModelOutputData = py_outputs.extract(py)?;
            Ok(outputs)
        })
    }
}

fn load_python_module(pkl_file: PathBuf, key: &str) -> Result<Py<PyAny>, anyhow::Error> {
    let loader_code = include_str!(concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/python/cloudpickle_load.py"
    ));
    let pkl_file = pkl_file
        .canonicalize()
        .context("pkl file is not a valid path")?;
    let pkl_file = pkl_file
        .to_str()
        .context("unable to convert pkl file path to str")?;
    info!("Loading pkl file: {}", pkl_file);
    Python::with_gil(|py| -> Result<Py<PyAny>, anyhow::Error> {
        // Initialize/hydrate our internal Python file that handles loading the cloudpickle
        // file.
        let loader =
            PyModule::from_code(py, loader_code, "cloudpickle_load.py", "cloudpickle_load")
                .context("unable to hydrate cloudpickle loader")?;
        // This module has a function named "load". Grab it.
        let load_fn = loader
            .getattr("load")
            .context("load function missing from cloudpickle_load.py")?;
        // Call the load function with the pkl_file path.
        let module = load_fn
            .call1((pkl_file,))
            .context("error loading pkl file")?;
        // Grab a reference to the function named `key` in the module.
        let key_fn = module.get_item(key).context("function key missing")?;
        // Cast the function to a PyFunction that is not GIL-locked so we can store
        // a reference to it outside a GIL-protected context.
        let key_fn = key_fn.extract().context("function key is not a function")?;
        // Return the predict function.
        Ok(key_fn)
    })
}
