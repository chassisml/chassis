use actix_web::{get, post, HttpResponse, Responder};
use handlebars::Handlebars;
use kube::Client;
use std::env;
use std::path::PathBuf;

pub mod routes {
    pub mod build;
    pub mod contexts;
    pub mod jobs;
}
mod manager;

pub type Error = Box<dyn std::error::Error>;

pub const PORT: u16 = 8080;

pub struct AppState<'a> {
    kube_client: Client,
    context_path: PathBuf,
    service_name: String,
    pod_name: String,
    port: String,
    template_registry: Handlebars<'a>,
    build_timeout: u64,
    build_ttl_after_finished: u64,
    build_resources: String,
    registry_url: String,
    registry_prefix: String,
    registry_credentials_secret_name: String,
    registry_insecure: bool,
}

impl AppState<'_> {
    pub async fn new(
        service_name: String,
        pod_name: String,
        context_path: PathBuf,
        build_timeout: u64,
        build_ttl_after_finished: u64,
        build_resources: String,
        registry_url: String,
        registry_prefix: String,
        registry_credentials_secret_name: String,
        registry_insecure: bool,
    ) -> Result<AppState<'static>, Error> {
        let kube_client = Client::try_default().await.unwrap();
        let mut template_registry = Handlebars::new();
        let job_template = include_str!(concat!(env!("CARGO_MANIFEST_DIR"), "/manifests/job.yaml"));
        template_registry.register_template_string("job", job_template)?;
        Ok(AppState {
            kube_client,
            context_path,
            service_name,
            pod_name,
            port: PORT.to_string(),
            template_registry,
            build_timeout,
            build_ttl_after_finished,
            build_resources,
            registry_url,
            registry_prefix,
            registry_credentials_secret_name,
            registry_insecure,
        })
    }
}

#[get("/")]
pub async fn root() -> impl Responder {
    HttpResponse::Ok().body("Alive!")
}

#[get("/health")]
pub async fn health() -> impl Responder {
    HttpResponse::Ok().body("Chassis Server Up and Running!")
}

#[get("/healthz")]
pub async fn healthz() -> impl Responder {
    HttpResponse::Ok().body("")
}

#[get("/version")]
pub async fn version() -> impl Responder {
    HttpResponse::Ok().body("1.5.0")
}

#[post("/test")]
pub async fn test() -> impl Responder {
    HttpResponse::Gone().body("The /test route has been deprecated and removed.")
}
