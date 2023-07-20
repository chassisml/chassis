mod build;
mod job_routes;

use actix_web::{get, post, web, App, HttpResponse, HttpServer, Responder};
use build::build_image;
use job_routes::{download_job_tar, get_job_logs, get_job_status};
use kube::Client;

#[get("/")]
async fn root() -> impl Responder {
    HttpResponse::Ok().body("Alive!")
}

#[get("/health")]
async fn health() -> impl Responder {
    HttpResponse::Ok().body("Chassis Server Up and Running!")
}

#[get("/version")]
async fn version() -> impl Responder {
    HttpResponse::Ok().body("1.5.0")
}

#[post("/test")]
async fn test() -> impl Responder {
    HttpResponse::Gone().body("The /test route has been deprecated and removed.")
}

pub struct AppState {
    kube_client: Client,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let kube_client = Client::try_default().await.unwrap();
    let state = web::Data::new(AppState { kube_client });
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
