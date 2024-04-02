use crate::config::ChassisConfig;
use opentelemetry::trace::TraceError;
use opentelemetry::KeyValue;
use opentelemetry_otlp::WithExportConfig;
use opentelemetry_sdk::runtime::Tokio;
use opentelemetry_sdk::trace::Tracer;
use opentelemetry_sdk::Resource;
use tonic::metadata::MetadataMap;
use tracing_bunyan_formatter::{BunyanFormattingLayer, JsonStorageLayer};
use tracing_subscriber::fmt::MakeWriter;
use tracing_subscriber::layer::SubscriberExt;
use tracing_subscriber::util::SubscriberInitExt;
use tracing_subscriber::{EnvFilter, Registry};

/// Initialize a tracing subscriber and set it to be the global default subscriber.
///
/// Note: This function should only be called once!
pub fn init_tracing_subscriber<Sink>(env_filter: String, sink: Sink, config: &ChassisConfig)
where
    Sink: for<'a> MakeWriter<'a> + Send + Sync + 'static,
{
    let service_name = format!(
        "{}-{}",
        config.model.identifier.as_str(),
        config.model.version.as_str()
    );

    let env_filter =
        EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new(env_filter));
    let formatting_layer = BunyanFormattingLayer::new(service_name.clone(), sink);

    let registry = Registry::default()
        .with(env_filter)
        .with(JsonStorageLayer)
        .with(formatting_layer);

    if config.telemetry.enabled {
        let endpoint = config
            .telemetry
            .endpoint
            .as_ref()
            .expect("tracing endpoint not set but telemetry is enabled")
            .as_str();
        let metadata = MetadataMap::default();
        // if let Some(md) = config.metadata.as_ref() {
        //     for (k, v) in md {
        //         metadata.insert(
        //             AsciiMetadataKey::from_bytes(k.to_ascii_lowercase().as_bytes())
        //                 .expect("Metadata keys must only contain ASCII characters"),
        //             v.parse().expect("Unable to parse metadata value"),
        //         );
        //     }
        // }

        let tracer = init_tracer(service_name.as_str(), endpoint, &metadata)
            .expect("Failed to initialize tracer");
        let telemetry_layer = tracing_opentelemetry::layer().with_tracer(tracer);
        registry.with(telemetry_layer).init()
    } else {
        registry.init()
    }
}

fn init_tracer(
    service_name: &str,
    endpoint: &str,
    metadata: &MetadataMap,
) -> Result<Tracer, TraceError> {
    opentelemetry_otlp::new_pipeline()
        .tracing()
        .with_exporter(
            opentelemetry_otlp::new_exporter()
                .tonic()
                .with_endpoint(endpoint)
                .with_metadata(metadata.clone()),
        )
        .with_trace_config(
            opentelemetry_sdk::trace::config().with_resource(Resource::new(vec![KeyValue::new(
                "service.name",
                service_name.to_string(),
            )])),
        )
        .install_batch(Tokio)
}
