use crate::manager::BuildManager;
use crate::AppState;
use actix_multipart::form::tempfile::TempFile;
use actix_multipart::form::MultipartForm;
use actix_web::http::header::USER_AGENT;
use actix_web::{post, web, HttpRequest, HttpResponse, Responder};
use log::{error, info};
use serde::{Deserialize, Serialize};

#[derive(Debug, MultipartForm)]
pub struct BuildImageForm {
    #[multipart(limit = "1 MiB")]
    build_config: TempFile,
    #[multipart(limit = "20 GiB")]
    build_context: TempFile,
}

#[derive(Debug, Deserialize)]
pub struct BuildConfig {
    pub image_name: String,
    pub tag: String,
    pub publish: bool,
    pub webhook: Option<String>,
    pub registry_creds: Option<String>,
    pub timeout: Option<u64>,
}

#[derive(Debug, Serialize)]
pub struct BuildImageResponse {
    error: bool,
    error_message: String,
    job_id: String,
}

#[post("/build")]
pub async fn build_image(
    req: HttpRequest,
    MultipartForm(form): MultipartForm<BuildImageForm>,
    state: web::Data<AppState<'static>>,
) -> impl Responder {
    // First ensure that the caller is using a new-enough SDK.
    if let Some(e) = verify_user_agent(&req) {
        info!("Received request from invalid client.");
        return e;
    }

    // Deserialize the build config.
    let build_config: BuildConfig = match serde_json::from_reader(&form.build_config.file) {
        Ok(bc) => bc,
        Err(e) => {
            error!("error deserializing build_config: {e}");
            return HttpResponse::BadRequest().json(BuildImageResponse {
                error: true,
                error_message: "invalid build config".to_string(),
                job_id: "".to_string(),
            });
        }
    };

    return match BuildManager::build(state.clone(), build_config, form.build_context).await {
        Ok(m) => {
            println!("Job started: {}", &m);
            HttpResponse::Ok().json(BuildImageResponse {
                error: false,
                error_message: "".to_string(),
                job_id: m,
            })
        }
        Err(e) => {
            error!("error saving context: {e}");
            return HttpResponse::InternalServerError().json(BuildImageResponse {
                error: true,
                error_message: e.to_string(),
                job_id: "".to_string(),
            });
        }
    };
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
