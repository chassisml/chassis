use crate::manager::BuildManager;
use crate::AppState;
use actix_web::{get, web, Error, HttpResponse, Responder};
use k8s_openapi::api::batch::v1::JobStatus;
use kube::ResourceExt;
use serde::Serialize;

#[derive(Serialize)]
struct JobStatusResponse {
    result: String,
    status: Option<JobStatus>,
    logs: Option<String>,
}

#[get("/job/{job_id}")]
pub async fn get_job_status(
    job_id: web::Path<String>,
    state: web::Data<AppState<'static>>,
) -> Result<HttpResponse, Error> {
    let manager = match BuildManager::for_job(state, &job_id) {
        Ok(m) => m,
        Err(e) => return Ok(HttpResponse::InternalServerError().body(e.to_string())),
    };
    let job = match manager.get_job().await {
        Ok(j) => j,
        Err(_) => return Ok(HttpResponse::NotFound().body("job not found")),
    };
    let annotations = &job.annotations();
    let result = match annotations.get("result") {
        Some(r) => r.to_string(),
        None => String::from(""),
    };
    let status = job.status;

    let mut job_status = JobStatusResponse {
        result: result.to_owned(),
        status: status.to_owned(),
        logs: None,
    };

    if status.is_some() && status.unwrap().failed > Some(0) {
        job_status.logs = manager.get_job_logs().await
    }

    Ok(HttpResponse::Ok().json(job_status))
}

#[get("/job/{job_id}/download-tar")]
pub async fn download_job_tar(_job_id: web::Path<String>) -> impl Responder {
    HttpResponse::Gone().body("The download-tar route has been deprecated and removed.")
}

#[get("/job/{job_id}/logs")]
pub async fn get_job_logs(
    job_id: web::Path<String>,
    state: web::Data<AppState<'static>>,
) -> Result<HttpResponse, Error> {
    let manager = match BuildManager::for_job(state, &job_id) {
        Ok(m) => m,
        Err(e) => return Ok(HttpResponse::InternalServerError().body(e.to_string())),
    };
    match manager.get_job_logs().await {
        Some(l) => Ok(HttpResponse::Ok().body(l)),
        None => Ok(HttpResponse::NotFound().body("not found")),
    }
}
