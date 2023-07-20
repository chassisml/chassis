use actix_multipart::form::json::Json;
use actix_multipart::form::tempfile::TempFile;
use actix_multipart::form::MultipartForm;
use actix_web::http::header::USER_AGENT;
use actix_web::{post, HttpRequest, HttpResponse, Responder};
use serde::Deserialize;

#[derive(Debug, MultipartForm)]
pub struct BuildImageForm {
    #[multipart(limit = "1 MiB")]
    build_config: Json<BuildConfig>,
    #[multipart(limit = "20 GiB")]
    build_context: TempFile,
}

#[derive(Debug, Deserialize)]
pub struct BuildConfig {
    image_name: String,
    tag: String,
    publish: bool,
    webhook: String,
    registry_creds: String,
}

#[post("/build")]
pub async fn build_image(
    req: HttpRequest,
    MultipartForm(form): MultipartForm<BuildImageForm>,
) -> impl Responder {
    if let Some(e) = verify_user_agent(&req) {
        return e;
    }
    HttpResponse::Ok().body("build")
}

fn verify_user_agent(req: &HttpRequest) -> Option<HttpResponse> {
    let headers = req.headers();
    let user_agent = headers.get(USER_AGENT);
    let error_response =
        Some(HttpResponse::BadRequest().body("This remote build server requires Chassis v1.5+."));
    if user_agent.is_none() {
        return error_response;
    }
    if let Ok(ua) = user_agent.unwrap().to_str() {
        if ua != "ChassisClient/1.5" {
            return error_response;
        }
    }
    return None;
}

fn create_job_object(image_name: &str, module_name: &str, model_name: &str) {}
