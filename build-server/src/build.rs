use actix_multipart::form::json::Json;
use actix_multipart::form::tempfile::TempFile;
use actix_multipart::form::text::Text;
use actix_multipart::form::MultipartForm;
use actix_web::{post, HttpResponse, Responder};
use serde::Deserialize;

#[derive(Debug, MultipartForm)]
struct BuildImageForm {
    #[multipart(limit = "1 MiB")]
    image_data: Json<BuildJobRequest>,
    #[multipart(limit = "20 GiB")]
    model: TempFile,
    metadata_data: Option<TempFile>,
}

#[derive(Deserialize)]
struct BuildJobRequest {
    model_name: String,
    name: String,
    gpu: bool,
    arm64: bool,
    publish: bool,
    registry_auth: String,
    webhook: String,
}

#[post("/build")]
pub async fn build_image(MultipartForm(form): MultipartForm<BuildImageForm>) -> impl Responder {
    HttpResponse::Ok().body("build")
}
