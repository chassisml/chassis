use actix_web::{web, App, HttpServer};
use chassis_build_server::build::build_image;
use chassis_build_server::job_routes::{download_job_tar, get_job_logs, get_job_status};
use chassis_build_server::PORT;
use chassis_build_server::{health, root, test, version, AppState};
use chrono::{DateTime, Utc};
use fern::colors::ColoredLevelConfig;
use log::{info, LevelFilter};

#[tokio::main]
async fn main() -> std::io::Result<()> {
    // Set up the logger.
    setup_logger(LevelFilter::Info).expect("error configuring logger");

    // Initialize our shared app state.
    let app_data = AppState::new().await.expect("error initializing app state");
    let state = web::Data::new(app_data);

    // Start the server.
    info!("Starting server on port {}", PORT);
    HttpServer::new(move || {
        App::new()
            .app_data(state.clone())
            .service(root)
            .service(health)
            .service(version)
            .service(test)
            .service(build_image)
            .service(get_job_status)
            .service(download_job_tar)
            .service(get_job_logs)
    })
    .bind((PORT))?
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
