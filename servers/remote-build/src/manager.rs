use crate::routes::build::BuildConfig;
use crate::{AppState, Error};
use actix_multipart::form::tempfile::TempFile;
use actix_web::web;
use log::debug;
use std::sync::Arc;
use uuid::Uuid;

mod context;
mod kubernetes;

pub(crate) struct BuildManager {
    state: web::Data<AppState<'static>>,
    job_id: String,
    config: Option<BuildConfig>,
}

impl BuildManager {
    pub(crate) fn new(
        state: web::Data<AppState<'static>>,
        config: BuildConfig,
    ) -> Result<Self, Error> {
        // Create a UUID for this build job.
        let job_id = Uuid::new_v4().to_string();
        debug!("Created job id: {}", &job_id);
        Ok(BuildManager {
            state,
            job_id,
            config: Some(config),
        })
    }

    pub(crate) fn for_job(
        state: web::Data<AppState<'static>>,
        job_id: &String,
    ) -> Result<Self, Error> {
        Ok(BuildManager {
            state,
            job_id: job_id.to_owned(),
            config: None,
        })
    }

    pub(crate) async fn build(
        state: web::Data<AppState<'static>>,
        config: BuildConfig,
        context: TempFile,
    ) -> Result<String, Error> {
        // Construct our manager.
        let manager = Arc::new(Self::new(state, config)?);

        // Save the context we were given.
        let build_context_url = manager.save_context(context)?;
        // Construct the Kubernetes Job object.
        let job = manager.create_job_object(&build_context_url)?;
        let _ = manager.start_build_job(job).await?;

        // Save the job ID before moving the manager into the spawned task.
        let job_id = manager.job_id.to_owned();

        // Start a listener to determine when the job finishes.
        let m2 = manager.clone();
        tokio::spawn(async move { m2.cleanup_job().await });

        Ok(job_id)
    }
}
