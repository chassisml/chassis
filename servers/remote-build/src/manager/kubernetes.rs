use crate::manager::BuildManager;
use crate::Error;
use k8s_openapi::api::batch::v1::Job;
use k8s_openapi::api::core::v1::Pod;
use kube::api::{ListParams, LogParams, PostParams};
use kube::runtime::conditions;
use kube::runtime::wait::await_condition;
use kube::Api;
use log::{error, info};
use serde_json::json;

impl BuildManager {
    pub(crate) fn create_job_object(&self, context_url: &String) -> Result<Job, Error> {
        let job_name = self.get_job_name();
        let build_config = match &self.config {
            Some(bc) => bc,
            None => return Err("build config not available".into()),
        };
        let image_name = &build_config.image_name;
        let data = json!({
            "JOB_NAME": job_name,
            "JOB_IDENTIFIER": &self.job_id,
            "IMAGE_NAME": image_name,
            "CONTEXT_URL": context_url,
            "CPU_CORES": "2", // TODO
            "MEMORY": "8Gi", // TODO
        });
        let manifest = &self.state.template_registry.render("job", &data)?;
        let job: Job = serde_yaml::from_str(manifest.as_str())?;
        Ok(job)
    }

    pub fn get_job_name(&self) -> String {
        format!("chassis-remote-build-job-{}", &self.job_id)
    }

    fn create_docker_config_secret(&self) -> Result<(), Error> {
        let registry = "https://index.docker.io/v1/";
        let auth_string = "";

        let data = json!({
            "auths": {
                registry: {
                    "auth": auth_string
                }
            }
        });
        Ok(())
    }

    pub async fn get_job(&self) -> Result<Job, Error> {
        let jobs: Api<Job> = Api::default_namespaced(self.state.kube_client.clone());
        let job_name = self.get_job_name();
        match jobs.get(job_name.as_str()).await {
            Ok(j) => Ok(j),
            Err(_) => Err("job not found".into()),
        }
    }

    pub async fn get_job_logs(&self) -> Option<String> {
        let pods: Api<Pod> = Api::default_namespaced(self.state.kube_client.clone());
        let list_params =
            ListParams::default().labels(format!("job-name={}", &self.job_id).as_str());
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

    pub async fn start_build_job(&self, job: Job) -> Result<(), Error> {
        // Apply Job object to Kubernetes.
        let jobs: Api<Job> = Api::default_namespaced(self.state.kube_client.clone());
        jobs.create(&PostParams::default(), &job).await?;
        Ok(())
    }

    pub async fn cleanup_job(&self) {
        // Set up the condition for when the job finishes.
        let jobs: Api<Job> = Api::default_namespaced(self.state.kube_client.clone());
        let job_name = self.get_job_name();
        let finish_condition =
            await_condition(jobs, job_name.as_str(), conditions::is_job_completed());
        let build_config = match &self.config {
            Some(bc) => bc,
            None => {
                error!("cleanup_job called without access to build_config");
                return;
            }
        };
        info!("Waiting until job {} completes", &self.job_id);
        // Run the watcher but cancel it if it takes longer than an hour.
        let timeout: u64 = match build_config.timeout {
            Some(t) => t,
            None => self.state.build_timeout,
        };
        let job_result =
            tokio::time::timeout(std::time::Duration::from_secs(timeout), finish_condition).await;
        match job_result {
            Err(_) => {
                error!("Job {} did not complete within the allotted time", job_name);
                // TODO - do something with error logs?
            }
            Ok(job_result) => {
                info!("Job {} has completed", job_name);
                // TODO - log elapsed time?
                // Determine if the job was successful or not.
                // If job was successful, then delete the Job from Kubernetes so we don't accumulate Job
                // records for successful runs.
            }
        }

        // Call any webhooks.
        if let Some(wh) = &build_config.webhook {
            info!("Running webhook(s)")
            // TODO - actually call webhook.
        }

        // Delete any Kubernetes secrets for this job.

        // Remove the build context from object storage.
    }
}
// -------------------------------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use crate::manager::BuildManager;
    use crate::routes::build::BuildConfig;
    use crate::AppState;
    use actix_web::web;
    use handlebars::Handlebars;
    use kube::Client;
    use std::path::PathBuf;

    #[tokio::test]
    async fn test_create_job_object() {
        let kube_client = Client::try_default().await.unwrap();
        let mut template_registry = Handlebars::new();
        let job_template = include_str!(concat!(env!("CARGO_MANIFEST_DIR"), "/manifests/job.yaml"));
        template_registry
            .register_template_string("job", job_template)
            .expect("failure registering job template");

        let state = web::Data::new(AppState {
            kube_client,
            context_path: PathBuf::from("/tmp".to_string()),
            service_name: "test".to_string(),
            pod_name: "test-0".to_string(),
            port: "8080".to_string(),
            template_registry,
            build_timeout: 3600,
        });

        let build_config = BuildConfig {
            image_name: "".to_string(),
            tag: "".to_string(),
            publish: false,
            webhook: None,
            registry_creds: None,
            timeout: None,
        };
        let context_url = "http://test-0:8080/contexts/abc123".to_string();
        let manager = BuildManager::new(state, build_config).unwrap();

        let job = manager
            .create_job_object(&context_url)
            .expect("unable to create job object");
        assert!(job
            .metadata
            .labels
            .unwrap()
            .contains_key("chassisml.io/job-identifier"));
        assert!(job
            .metadata
            .name
            .unwrap()
            .starts_with("chassis-remote-build-job-"));
    }
}
