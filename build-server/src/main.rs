use actix_web::{web, App, HttpServer};
use chassis_build_server::build::build_image;
use chassis_build_server::job_routes::{download_job_tar, get_job_logs, get_job_status};
use chassis_build_server::{health, root, test, version, AppState};

#[tokio::main]
async fn main() -> std::io::Result<()> {
    let app_data = AppState::new().await.expect("error initializing app state");
    let state = web::Data::new(app_data);
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
    .bind(("0.0.0.0", 8080))?
    .run()
    .await
}
