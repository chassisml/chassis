use lazy_static::lazy_static;
use prometheus::{
    register_histogram_vec, register_int_counter_vec, Encoder, HistogramOpts, HistogramVec,
    IntCounterVec, Opts, TextEncoder,
};

lazy_static! {
    pub static ref INFERENCE_REQUESTS: IntCounterVec = register_int_counter_vec!(
        Opts::new("inference_requests", "Inference Requests"),
        &["model_identifier", "model_version"]
    )
    .expect("metric can be created");
    pub static ref INFERENCES_PERFORMED: IntCounterVec = register_int_counter_vec!(
        Opts::new("inferences_performed", "Inferences Performed"),
        &["model_identifier", "model_version"]
    )
    .expect("metric can be created");
    pub static ref INFERENCE_FAILURES: IntCounterVec = register_int_counter_vec!(
        Opts::new("inference_failures", "Inference Failures"),
        &["model_identifier", "model_version"]
    )
    .expect("metric can be created");
    pub static ref DATA_PROCESSED_SIZE_IN_BYTES: IntCounterVec = register_int_counter_vec!(
        Opts::new(
            "data_processed_size_in_bytes",
            "Data processed by model (in bytes)"
        ),
        &["model_identifier", "model_version"]
    )
    .expect("metric can be created");
    pub static ref RESPONSE_CODE_COLLECTOR: IntCounterVec = register_int_counter_vec!(
        Opts::new("response_code", "Response Codes"),
        &["env", "statuscode", "type"]
    )
    .expect("metric can be created");
    pub static ref RESPONSE_TIME_COLLECTOR: HistogramVec = register_histogram_vec!(
        HistogramOpts::new("response_time", "Response Times"),
        &["env"]
    )
    .expect("metric can be created");
    pub static ref DATA_DRIFT_COLLECTOR: HistogramVec = register_histogram_vec!(
        "data_drift",
        "Data Drift",
        &["model_identifier", "model_version"],
        vec![0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    )
    .expect("metric can be created");
}

pub(crate) async fn metrics_handler() -> String {
    let mut buffer = Vec::new();
    let encoder = TextEncoder::new();
    let metric_families = prometheus::gather();
    if let Err(e) = encoder.encode(&metric_families, &mut buffer) {
        eprintln!("could not encode custom metrics: {}", e);
    };
    let res = String::from_utf8(buffer.clone()).unwrap_or_else(|e| {
        eprintln!("custom metrics could not be encoded as UTF-8: {}", e);
        String::default()
    });
    buffer.clear();
    res
}
