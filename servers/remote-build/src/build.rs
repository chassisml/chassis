use crate::contexts::save_context;
use crate::kubernetes::create_job_object;
use crate::{AppState, Error};
use actix_multipart::form::tempfile::TempFile;
use actix_multipart::form::MultipartForm;
use actix_web::http::header::USER_AGENT;
use actix_web::{post, web, HttpRequest, HttpResponse, Responder};
use k8s_openapi::api::batch::v1::Job;
use kube::api::PostParams;
use kube::runtime::conditions;
use kube::runtime::wait::await_condition;
use kube::{Api, Client};
use log::{debug, error, info};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

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
    state: web::Data<AppState<'_>>,
) -> impl Responder {
    // First ensure that the caller is using a new-enough SDK.
    if let Some(e) = verify_user_agent(&req) {
        info!("Received request from invalid client.");
        return e;
    }

    // TODO - gracefully handle errors
    let build_config: BuildConfig = serde_json::from_reader(&form.build_config.file).unwrap();

    // Create a UUID for this build job.
    let job_id = Uuid::new_v4().to_string();
    debug!("Created job id: {}", &job_id);

    // Save the context to our cache directory.
    let build_context_url = match save_context(&state, &job_id, form.build_context) {
        Ok(u) => u,
        Err(e) => {
            error!("error saving context: {e}");
            return HttpResponse::InternalServerError().json(BuildImageResponse {
                error: true,
                error_message: e.to_string(),
                job_id: job_id.to_string(),
            });
        }
    };

    // Construct the Kubernetes Job object.
    let job = match create_job_object(
        &build_config,
        &job_id,
        &build_context_url,
        &state.template_registry,
    ) {
        Ok(j) => j,
        Err(e) => {
            return HttpResponse::InternalServerError().json(BuildImageResponse {
                error: true,
                error_message: e.to_string(),
                job_id: job_id.to_string(),
            });
        }
    };

    // Apply the Kubernetes Job object.
    return match start_build_job(state.kube_client.clone(), job).await {
        Ok(_) => {
            println!("Job started: {}", job_id);
            HttpResponse::Ok().json(BuildImageResponse {
                error: false,
                error_message: "".to_string(),
                job_id: job_id.to_string(),
            })
        }
        Err(e) => HttpResponse::InternalServerError().json(BuildImageResponse {
            error: true,
            error_message: e.to_string(),
            job_id: job_id.to_string(),
        }),
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

async fn start_build_job(client: Client, job: Job) -> Result<(), Error> {
    // Apply Job object to Kubernetes.
    let jobs: Api<Job> = Api::default_namespaced(client);
    jobs.create(&PostParams::default(), &job).await?;

    // Start a listener to determine when the job finishes.
    let job_name = job.metadata.name.as_ref().unwrap();
    tokio::spawn(cleanup_job(jobs.clone(), job_name.to_string()));

    Ok(())
}

async fn cleanup_job(jobs: Api<Job>, job_name: String) {
    // Set up the condition for when the job finishes.
    let finish_condition = await_condition(jobs, job_name.as_str(), conditions::is_job_completed());
    info!("Waiting until job {} completes", job_name);
    // Run the watcher but cancel it if it takes longer than an hour.
    let job_result =
        tokio::time::timeout(std::time::Duration::from_secs(3600), finish_condition).await;
    if job_result.is_err() {
        error!("Job {} has failed", job_name);
        // TODO - do something with error logs?
        return;
    }
    info!("Job {} has completed", job_name);
    // TODO - log elapsed time?

    // Call any webhooks.

    // If job was successful, then delete the Job from Kubernetes so we don't accumulate Job
    // records for successful runs.

    // Delete any Kubernetes secrets for this job.

    // Remove the build context from object storage.
}
