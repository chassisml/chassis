use crate::{AppState, Error};
use actix_files::NamedFile;
use actix_multipart::form::tempfile::TempFile;
use actix_web::{delete, get, web, HttpResponse};
use std::path::{Path, PathBuf};
use tokio::fs;

#[get("/contexts/{job_id}")]
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
    fs::remove_file(path).await?;
    Ok(HttpResponse::Ok().body(""))
}

pub(crate) fn get_context_url(state: &web::Data<AppState<'_>>, job_id: &str) -> String {
    format!(
        "http://{}:{}/contexts/{}",
        &state.pod_name,
        &state.port,
        job_id.to_string()
    )
}

fn get_context_cache_path<P: AsRef<Path>>(state: &web::Data<AppState<'_>>, job_id: &P) -> PathBuf {
    Path::new(&state.context_dir)
        .join(&job_id)
        .join("context.zip")
}

pub(crate) fn save_context(
    state: &web::Data<AppState<'_>>,
    job_id: &str,
    context: TempFile,
) -> Result<String, Error> {
    let path = get_context_cache_path(&state, &job_id);
    context.file.persist(path)?;
    Ok(get_context_url(&state, &job_id))
}
