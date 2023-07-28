use crate::{AppState, Error};
use actix_files::NamedFile;
use actix_multipart::form::tempfile::TempFile;
use actix_web::{delete, get, web, HttpResponse};
use log::debug;
use std::path::{Path, PathBuf};
use tokio::fs;

#[get("/contexts/{job_id}/context.zip")]
pub async fn get_context(
    job_id: web::Path<String>,
    state: web::Data<AppState<'_>>,
) -> Result<NamedFile, Error> {
    Ok(NamedFile::open(get_context_cache_path(
        &state,
        &job_id.as_str(),
    ))?)
}

#[delete("/contexts/{job_id}")]
pub async fn delete_context(
    job_id: web::Path<String>,
    state: web::Data<AppState<'_>>,
) -> Result<HttpResponse, Error> {
    let path = get_context_cache_path(&state, &job_id.as_str());
    // TODO - handle error properly.
    let parent = path.parent().unwrap();
    fs::remove_file(parent).await?;
    Ok(HttpResponse::Ok().body(""))
}

pub(crate) fn get_context_url(state: &web::Data<AppState<'_>>, job_id: &str) -> String {
    format!(
        "http://{}.{}:{}/contexts/{}/context.zip",
        &state.pod_name,
        &state.service_name,
        &state.port,
        job_id.to_string()
    )
}

fn get_context_cache_path<P: AsRef<Path>>(state: &web::Data<AppState<'_>>, job_id: &P) -> PathBuf {
    state.context_path.clone().join(&job_id).join("context.zip")
}

pub(crate) fn save_context(
    state: &web::Data<AppState<'_>>,
    job_id: &str,
    context: TempFile,
) -> Result<String, Error> {
    let path = get_context_cache_path(&state, &job_id);
    debug!("saving context to path: {}", &path.to_str().unwrap());
    // Ensure the context directory exists.
    // TODO - don't panic here
    let dir_name = path.parent().expect("context path doesn't have a parent");
    debug!("parent: {}", dir_name.to_str().unwrap());
    std::fs::create_dir(dir_name)?;
    debug!("context dir exists: {}", dir_name.exists());
    debug!("tempfile exists: {}", context.file.path().exists());
    debug!("tempfile path: {}", context.file.path().to_str().unwrap());
    context.file.persist(path)?;
    Ok(get_context_url(&state, &job_id))
}
