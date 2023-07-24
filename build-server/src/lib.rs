use actix_web::{get, post, HttpResponse, Responder};
use handlebars::Handlebars;
use kube::Client;
use std::env;

pub mod build;
mod contexts;
pub mod job_routes;
mod kubernetes;

pub type Error = Box<dyn std::error::Error>;

const POD_NAME_KEY: &str = "POD_NAME";
const CONTEXT_DIR_KEY: &str = "CHASSIS_CONTEXT_DIR";

pub struct AppState<'a> {
    kube_client: Client,
    context_dir: String,
    pod_name: String,
    port: String,
    template_registry: Handlebars<'a>,
}

impl AppState<'_> {
    pub async fn new() -> Result<AppState<'static>, Error> {
        let kube_client = Client::try_default().await.unwrap();
        let pod_name = env::var(POD_NAME_KEY)?;
        let context_dir = env::var(CONTEXT_DIR_KEY)?;
        let mut template_registry = Handlebars::new();
        let job_template = include_str!(concat!(env!("CARGO_MANIFEST_DIR"), "/manifests/job.yaml"));
        template_registry.register_template_string("job", job_template)?;
        Ok(AppState {
            kube_client,
            context_dir,
            pod_name,
            port: "8080".to_string(),
            template_registry,
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

#[get("/version")]
pub async fn version() -> impl Responder {
    HttpResponse::Ok().body("1.5.0")
}

#[post("/test")]
pub async fn test() -> impl Responder {
    HttpResponse::Gone().body("The /test route has been deprecated and removed.")
}
