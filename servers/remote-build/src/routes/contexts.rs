use crate::manager::BuildManager;
use crate::{AppState, Error};
use actix_files::NamedFile;
use actix_web::{get, web};

#[get("/contexts/{job_id}/context.zip")]
pub async fn get_context(
    job_id: web::Path<String>,
    state: web::Data<AppState<'static>>,
) -> Result<NamedFile, Error> {
    let manager = BuildManager::for_job(state, &job_id)?;
    Ok(NamedFile::open(manager.get_context_cache_path())?)
}
