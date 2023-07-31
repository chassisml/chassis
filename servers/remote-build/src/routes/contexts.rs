use crate::manager::BuildManager;
use crate::{AppState, Error};
use actix_files::NamedFile;
use actix_web::{delete, get, web, HttpResponse};
use tokio::fs;

#[get("/contexts/{job_id}/context.zip")]
pub async fn get_context(
    job_id: web::Path<String>,
    state: web::Data<AppState<'static>>,
) -> Result<NamedFile, Error> {
    let manager = BuildManager::for_job(state, &job_id)?;
    Ok(NamedFile::open(manager.get_context_cache_path())?)
}

#[delete("/contexts/{job_id}")]
pub async fn delete_context(
    job_id: web::Path<String>,
    state: web::Data<AppState<'static>>,
) -> Result<HttpResponse, Error> {
    let manager = BuildManager::for_job(state, &job_id)?;
    let path = manager.get_context_cache_path();
    // TODO - handle error properly.
    let parent = path.parent().unwrap();
    fs::remove_file(parent).await?;
    Ok(HttpResponse::Ok().body(""))
}
