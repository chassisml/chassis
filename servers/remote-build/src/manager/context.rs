use crate::manager::BuildManager;
use crate::Error;
use actix_multipart::form::tempfile::TempFile;
use log::error;
use std::path::PathBuf;
use tokio::fs;

impl BuildManager {
    pub(crate) fn get_context_cache_path(&self) -> PathBuf {
        self.state
            .context_path
            .clone()
            .join(&self.job_id)
            .join("context.zip")
    }

    fn get_context_url(&self) -> String {
        format!(
            "http://{}.{}:{}/contexts/{}/context.zip",
            &self.state.pod_name, &self.state.service_name, &self.state.port, &self.job_id
        )
    }

    pub(crate) fn save_context(&self, context: TempFile) -> Result<String, Error> {
        let path = self.get_context_cache_path();
        // Ensure the context directory exists.
        // TODO - don't panic here
        let dir_name = path.parent().expect("context path doesn't have a parent");
        std::fs::create_dir(dir_name)?;
        context.file.persist(path)?;
        Ok(self.get_context_url())
    }

    pub(crate) async fn clean_context(&self) {
        let path = self.get_context_cache_path();
        let parent = match path.parent() {
            Some(p) => p,
            None => {
                error!("context path doesn't have a parent: {}", path.display());
                return;
            }
        };
        fs::remove_dir_all(parent)
            .await
            .expect("unable to remove context");
    }
}
