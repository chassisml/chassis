use crate::manager::BuildManager;
use crate::routes::build::BuildStatusResponse;
use crate::AppState;
use actix_web::{get, web, Error, HttpResponse, Responder};
use k8s_openapi::api::batch::v1::JobStatus;
use log::error;
use serde::Serialize;

#[derive(Serialize)]
struct JobStatusResponse {
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
    let status = job.status.expect("job has no status");

    let mut build_status = BuildStatusResponse {
        image_tag: None,
        logs: None,
        success: false,
        completed: false,
        error_message: None,
        remote_build_id: job_id.to_string(),
    };

    let mut job_failed = false;
    if let Some(f) = status.failed {
        if f > 0 {
            job_failed = true;
            build_status.success = false;
            build_status.completed = true;
            build_status.error_message =
                Some("Build failed. Check logs for more information".to_string());
            build_status.logs = manager.get_job_logs().await;
        }
    }

    if let Some(s) = status.succeeded {
        if s > 0 {
            if job_failed {
                error!("something funky is going on; job both failed and succeeded")
            }
            let annotations = &job.metadata.annotations.expect("job has no annotations");
            let destination = annotations
                .get("chassisml.io/destination")
                .expect("job missing destination label");
            build_status.image_tag = Some(destination.to_string());
            build_status.logs = manager.get_job_logs().await;
            build_status.success = true;
            build_status.completed = true;
        }
    }

    Ok(HttpResponse::Ok().json(build_status))
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
