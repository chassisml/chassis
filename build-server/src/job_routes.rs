use crate::AppState;
use actix_web::{get, web, Error, HttpResponse, Responder};
use k8s_openapi::api::batch::v1::{Job, JobStatus};
use k8s_openapi::api::core::v1::Pod;
use kube::api::{ListParams, LogParams};
use kube::{Api, ResourceExt};
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
    state: web::Data<AppState<'_>>,
) -> Result<HttpResponse, Error> {
    let jobs: Api<Job> = Api::default_namespaced(state.kube_client.clone());
    let job = match jobs.get(job_id.as_str()).await {
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
        job_status.logs = get_logs(&job_id, &state).await
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
    state: web::Data<AppState<'_>>,
) -> Result<HttpResponse, Error> {
    match get_logs(&job_id, &state).await {
        Some(l) => Ok(HttpResponse::Ok().body(l)),
        None => Ok(HttpResponse::NotFound().body("not found")),
    }
}

async fn get_logs(job_id: &String, state: &web::Data<AppState<'_>>) -> Option<String> {
    let pods: Api<Pod> = Api::default_namespaced(state.kube_client.clone());
    let list_params = ListParams::default().labels(format!("job-name={}", job_id).as_str());
    let job_pods = match pods.list(&list_params).await {
        Ok(p) => p,
        Err(_) => return None,
    };
    let job_pod = match job_pods.items.get(0) {
        Some(p) => p,
        None => return None,
    };
    let pod_name = match &job_pod.metadata.name {
        Some(n) => n,
        None => return None,
    };
    let logs = pods
        .logs(
            pod_name.as_str(),
            &LogParams {
                ..LogParams::default()
            },
        )
        .await;
    match logs {
        Ok(l) => Some(l),
        Err(_) => None,
    }
}
