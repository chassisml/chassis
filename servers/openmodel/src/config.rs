use serde::Deserialize;
use serde_aux::field_attributes::deserialize_number_from_string;

#[derive(Debug, Deserialize, Clone)]
pub struct ChassisConfig {
    pub model: ModelConfig,
    pub metrics: MetricsConfig,
    pub telemetry: TelemetryConfig,
    pub log: LogConfig,
}

#[derive(Debug, Deserialize, Clone)]
pub struct ModelConfig {
    pub identifier: String,
    pub version: String,
    #[serde(deserialize_with = "deserialize_number_from_string")]
    pub port: u16,
    pub dir: String,
}

#[derive(Debug, Deserialize, Clone)]
pub struct MetricsConfig {
    #[serde(deserialize_with = "deserialize_number_from_string")]
    pub port: u16,
}

#[derive(Debug, Deserialize, Clone)]
pub struct TelemetryConfig {
    pub enabled: bool,
    pub endpoint: Option<String>,
}

#[derive(Debug, Deserialize, Clone)]
pub struct LogConfig {
    pub level: String,
}

pub fn load_configuration() -> Result<ChassisConfig, config::ConfigError> {
    let config = config::Config::builder()
        .add_source(config::Environment::default().separator("_"))
        .set_default("log.level", "info")?
        .set_default("telemetry.enabled", false)?
        .set_default("model.port", 9090)?
        .set_default("model.dir", "/app/data")?
        .set_default("metrics.port", 8080)?
        .build()?;

    config.try_deserialize::<ChassisConfig>()
}
