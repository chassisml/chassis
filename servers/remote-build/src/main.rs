use actix_multipart::form::tempfile::TempFileConfig;
use actix_web::middleware::Logger;
use actix_web::{web, App, HttpServer};
use chassis_build_server::routes::build::build_image;
use chassis_build_server::routes::contexts::get_context;
use chassis_build_server::routes::jobs::{download_job_tar, get_job_logs, get_job_status};
use chassis_build_server::PORT;
use chassis_build_server::{health, healthz, root, test, version, AppState};
use chrono::{DateTime, Utc};
use fern::colors::ColoredLevelConfig;
use log::{info, LevelFilter};
use std::env;
use std::path::PathBuf;

const SERVICE_NAME_KEY: &str = "SERVICE_NAME";
const POD_NAME_KEY: &str = "POD_NAME";
const DATA_DIR_KEY: &str = "CHASSIS_DATA_DIR";
const BUILD_TIMEOUT_KEY: &str = "BUILD_TIMEOUT";
const BUILD_RESOURCES_KEY: &str = "BUILD_RESOURCES";
const LOG_LEVEL_KEY: &str = "LOG_LEVEL";
const REGISTRY_URL_KEY: &str = "REGISTRY_URL";
const REGISTRY_PREFIX_KEY: &str = "REGISTRY_PREFIX";
const REGISTRY_CREDENTIALS_SECRET_NAME_KEY: &str = "REGISTRY_CREDENTIALS_SECRET_NAME";
const REGISTRY_INSECURE: &str = "REGISTRY_INSECURE";

#[tokio::main]
async fn main() -> std::io::Result<()> {
    // Set up the logger.
    let log_level: LevelFilter = match env::var(LOG_LEVEL_KEY) {
        Ok(v) => match v.as_str() {
            "debug" => LevelFilter::Debug,
            _ => LevelFilter::Info,
        },
        Err(_) => LevelFilter::Info,
    };
    setup_logger(log_level).expect("error configuring logger");

    // Read environment variables.
    let service_name = env::var(SERVICE_NAME_KEY)
        .expect(format!("the {} environment variable must be set", SERVICE_NAME_KEY).as_str());
    let pod_name = env::var(POD_NAME_KEY)
        .expect(format!("the {} environment variable must be set", POD_NAME_KEY).as_str());
    let data_dir = env::var(DATA_DIR_KEY)
        .expect(format!("the {} environment variable must be set", DATA_DIR_KEY).as_str());
    let build_timeout_string = env::var(BUILD_TIMEOUT_KEY)
        .expect(format!("the {} environment variable must be set", BUILD_TIMEOUT_KEY).as_str());
    let build_timeout: u64 = build_timeout_string
        .trim()
        .parse()
        .expect(format!("{} must be an integer", BUILD_TIMEOUT_KEY).as_str());
    let build_resources = env::var(BUILD_RESOURCES_KEY).expect(
        format!(
            "the {} environment variable must be set",
            BUILD_RESOURCES_KEY
        )
        .as_str(),
    );
    let registry_url: String = env::var(REGISTRY_URL_KEY)
        .expect(format!("the {} environment variable must be set", REGISTRY_URL_KEY).as_str());
    let registry_prefix: String = env::var(REGISTRY_PREFIX_KEY).expect(
        format!(
            "the {} environment variable must be set",
            REGISTRY_PREFIX_KEY
        )
        .as_str(),
    );
    let registry_credentials_secret_name: String = env::var(REGISTRY_CREDENTIALS_SECRET_NAME_KEY)
        .expect(
            format!(
                "the {} environment variable must be set",
                REGISTRY_CREDENTIALS_SECRET_NAME_KEY
            )
            .as_str(),
        );
    let registry_insecure: bool = env::var(REGISTRY_INSECURE)
        .expect(format!("the {} environment variable must be set", REGISTRY_INSECURE).as_str())
        .parse()
        .expect(
            format!(
                "the {} environment variable must be either 'true' or 'false'",
                REGISTRY_INSECURE
            )
            .as_str(),
        );

    // Create data directories.
    let data_path = PathBuf::from(&data_dir);
    let context_path = (&data_path).join("contexts");
    let tmp_path = (&data_path).join("tmp");
    // Note: Use create_dir_all here so that it doesn't error on subsequent launches when
    // the directories already exist.
    std::fs::create_dir_all(&context_path).expect("unable to create context directory");
    std::fs::create_dir_all(&tmp_path).expect("unable to create tmp directory");

    // Initialize our shared app state.
    let app_data = AppState::new(
        service_name,
        pod_name,
        context_path,
        build_timeout,
        build_resources,
        registry_url,
        registry_prefix,
        registry_credentials_secret_name,
        registry_insecure,
    )
    .await
    .expect("error initializing app state");

    // Configure where uploaded tempfiles get stored.
    let tempfile_config = TempFileConfig::default().directory(&tmp_path);

    let state = web::Data::new(app_data);
    let tempfile_appdata = web::Data::new(tempfile_config);

    // Start the server.
    info!("Starting server on 0.0.0.0:{}", PORT);
    HttpServer::new(move || {
        let logger = Logger::default();
        App::new()
            .wrap(logger)
            .app_data(state.clone())
            .app_data(tempfile_appdata.clone())
            .service(root)
            .service(health)
            .service(healthz)
            .service(version)
            .service(test)
            .service(build_image)
            .service(get_job_status)
            .service(download_job_tar)
            .service(get_job_logs)
            .service(get_context)
    })
    .bind(("0.0.0.0", PORT))?
    .run()
    .await
}

fn setup_logger(log_level: LevelFilter) -> Result<(), fern::InitError> {
    let colors = ColoredLevelConfig::new();
    fern::Dispatch::new()
        .format(move |out, message, record| {
            let now: DateTime<Utc> = Utc::now();
            out.finish(format_args!(
                "[{} {} {}:{}] {}",
                now.to_rfc3339(),
                colors.color(record.level()),
                record.file().unwrap_or(""),
                record.line().unwrap_or(0),
                message,
            ))
        })
        .level(log_level)
        .chain(std::io::stdout())
        .apply()?;
    Ok(())
}
