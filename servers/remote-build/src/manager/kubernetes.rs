use crate::manager::BuildManager;
use crate::Error;
use k8s_openapi::api::batch::v1::Job;
use k8s_openapi::api::core::v1::Pod;
use kube::api::{ListParams, LogParams, PostParams};
use kube::runtime::conditions;
use kube::runtime::wait::await_condition;
use kube::Api;
use lazy_static::lazy_static;
use log::{error, info};
use regex::Regex;
use serde_json::json;

lazy_static! {
    static ref MULTIPLE_SLASH_REGEX: Regex = Regex::new(r"/{2,}").unwrap();
}

impl BuildManager {
    pub(crate) fn create_job_object(&self, context_url: &String) -> Result<Job, Error> {
        let job_name = self.get_job_name();
        let mut addtl_options = "".to_string();
        if self.is_insecure_registry() {
            addtl_options += ",registry.insecure=true"
        }
        let timeout = self.get_timeout();
        let data = json!({
            "JOB_NAME": job_name,
            "JOB_IDENTIFIER": &self.job_id,
            "IMAGE_NAME": self.build_image_name(),
            "CONTEXT_URL": context_url,
            "TIMEOUT": timeout,
            "TTL_AFTER_FINISHED": self.state.build_ttl_after_finished,
            "ADDTL_OPTIONS": addtl_options,
            "RESOURCES": self.state.build_resources,
            "CREDS": self.get_secret_name(),
        });
        let manifest = &self.state.template_registry.render("job", &data)?;
        let job: Job = serde_yaml::from_str(manifest.as_str())?;
        Ok(job)
    }

    fn build_image_name(&self) -> String {
        let mut parts: Vec<&str> = vec![];
        let build_config = self.config.as_ref().expect("build config is not available");
        if !self.state.registry_url.is_empty() {
            parts.push(&self.state.registry_url);
        }
        if !self.state.registry_prefix.is_empty() {
            parts.push(&self.state.registry_prefix);
        }
        parts.push(&build_config.image_name);
        let mut url = parts.join("/");
        url = MULTIPLE_SLASH_REGEX
            .replace_all(url.as_str(), "/")
            .to_string();
        if url.starts_with("/") {
            url = url[1..].to_string();
        }
        return format!("{}:{}", url, &build_config.tag);
    }

    pub fn get_job_name(&self) -> String {
        format!("chassis-remote-build-job-{}", &self.job_id)
    }

    fn get_timeout(&self) -> u64 {
        match self
            .config
            .as_ref()
            .expect("build config not available")
            .timeout
        {
            Some(t) => t,
            None => self.state.build_timeout,
        }
    }

    fn is_insecure_registry(&self) -> bool {
        // If the state registry URL is not empty, then use the value from state.
        if !self.state.registry_url.is_empty() {
            return self.state.registry_insecure;
        }
        return false;
    }

    fn get_secret_name(&self) -> Option<String> {
        // If we have a static registry configured and a secret name is given then return it.
        if !self.state.registry_url.is_empty() {
            if !self.state.registry_credentials_secret_name.is_empty() {
                return Some(self.state.registry_credentials_secret_name.to_string());
            };
        }
        None
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
            ListParams::default().labels(format!("job-name={}", self.get_job_name()).as_str());
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
        let job = self.wait_for_job_completion().await;

        // If we got a Job back then call webhooks, etc.
        match job {
            Some(job) => {
                info!("Job {} has completed: {:?}", &self.job_id, job.status);

                // TODO - log elapsed time?

                // Call any webhooks.
                match &self.config {
                    Some(build_config) => {
                        if let Some(_wh) = &build_config.webhook {
                            info!("Running webhook(s)")
                            // TODO - actually call webhook.
                        }
                    }
                    None => {
                        error!("cleanup_job called without access to build_config");
                    }
                };
            }
            None => {
                // TODO - what to do here??
            }
        }

        // Always do the following actions.

        // Remove the build context from the context cache.
        self.clean_context().await;
    }

    async fn wait_for_job_completion(&self) -> Option<Job> {
        // Set up the condition for when the job finishes.
        let jobs: Api<Job> = Api::default_namespaced(self.state.kube_client.clone());
        let job_name = self.get_job_name();
        let finish_condition =
            await_condition(jobs, job_name.as_str(), conditions::is_job_completed());
        info!("Waiting until job {} completes", &self.job_id);
        // Run the watcher but cancel it if it takes longer than an hour.
        let timeout = self.get_timeout();
        // Add 10 seconds to the timeout to give the job time to terminate if it also reaches the
        // timeout.
        let timeout = timeout + 10;
        let job_result =
            tokio::time::timeout(std::time::Duration::from_secs(timeout), finish_condition).await;
        return match job_result {
            Err(e) => {
                error!(
                    "Job {} did not complete within the allotted time: {e}",
                    &self.job_id
                );
                None
            }
            Ok(job_result) => match job_result {
                Err(e) => {
                    error!("{e}");
                    None
                }
                Ok(j) => j,
            },
        };
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
    use k8s_openapi::apimachinery::pkg::api::resource::Quantity;
    use kube::Client;
    use serde_json::json;
    use std::path::PathBuf;

    async fn get_default_app_state() -> AppState<'static> {
        let kube_client = Client::try_default().await.unwrap();
        let mut template_registry = Handlebars::new();
        let job_template = include_str!(concat!(env!("CARGO_MANIFEST_DIR"), "/manifests/job.yaml"));
        template_registry
            .register_template_string("job", job_template)
            .expect("failure registering job template");
        AppState {
            kube_client,
            context_path: PathBuf::from("/tmp".to_string()),
            service_name: "test".to_string(),
            pod_name: "test-0".to_string(),
            port: "8080".to_string(),
            template_registry,
            build_timeout: 3600,
            build_ttl_after_finished: 3600,
            build_resources: "{}".to_string(),
            registry_url: "my-registry:5000".to_string(),
            registry_prefix: "".to_string(),
            registry_credentials_secret_name: "".to_string(),
            registry_insecure: true,
        }
    }

    fn get_default_build_config() -> BuildConfig {
        BuildConfig {
            image_name: "image".to_string(),
            tag: "tag".to_string(),
            webhook: None,
            timeout: None,
        }
    }

    async fn get_default_test_manager() -> BuildManager {
        get_custom_test_manager(None, None).await
    }

    async fn get_custom_test_manager(
        state: Option<AppState<'static>>,
        config: Option<BuildConfig>,
    ) -> BuildManager {
        let state = web::Data::new(state.unwrap_or(get_default_app_state().await));
        let build_config = config.unwrap_or(get_default_build_config());
        BuildManager::new(state, build_config).unwrap()
    }

    #[tokio::test]
    #[should_panic]
    async fn test_build_image_name_without_registry_url() {
        let mut state = get_default_app_state().await;
        state.registry_url = "".to_string();
        let _manager = get_custom_test_manager(Some(state), None).await;
    }

    #[tokio::test]
    async fn test_build_image_name_with_registry_url() {
        let manager = get_default_test_manager().await;
        assert_eq!(manager.build_image_name(), "my-registry:5000/image:tag")
    }

    #[tokio::test]
    async fn test_build_image_name_with_registry_url_and_prefix() {
        let mut state = get_default_app_state().await;
        state.registry_prefix = "prefix".to_string();
        let manager = get_custom_test_manager(Some(state), None).await;
        assert_eq!(
            manager.build_image_name(),
            "my-registry:5000/prefix/image:tag"
        )
    }

    #[tokio::test]
    async fn test_build_image_name_with_registry_url_and_trailing_slash() {
        let mut build_config = get_default_build_config();
        build_config.image_name = "username/image".to_string();
        let mut state = get_default_app_state().await;
        state.registry_url = "my-registry:5000/".to_string();
        let manager = get_custom_test_manager(Some(state), Some(build_config)).await;
        assert_eq!(
            manager.build_image_name(),
            "my-registry:5000/username/image:tag"
        )
    }

    #[tokio::test]
    async fn test_create_job_object() {
        let context_url = "http://test-0:8080/contexts/abc123".to_string();
        let manager = get_default_test_manager().await;

        let job = manager
            .create_job_object(&context_url)
            .expect("unable to create job object");
        let labels = job.metadata.labels.unwrap();
        let annotations = job.metadata.annotations.unwrap();
        assert!(labels.contains_key("chassisml.io/job-identifier"));
        assert!(annotations.contains_key("chassisml.io/destination"));
        assert!(job
            .metadata
            .name
            .unwrap()
            .starts_with("chassis-remote-build-job-"));
    }

    #[tokio::test]
    async fn test_create_job_object_with_insecure_registry() {
        let context_url = "http://test-0:8080/contexts/abc123".to_string();
        let manager = get_default_test_manager().await;
        let job = manager
            .create_job_object(&context_url)
            .expect("unable to create job object");
        let containers = job.spec.unwrap().template.spec.unwrap().containers;
        let args = containers[0].args.as_ref().unwrap();
        assert!(args
            .iter()
            .any(|line| { line.contains(",registry.insecure=true") }));
    }

    #[tokio::test]
    async fn test_create_job_object_with_secure_registry() {
        let mut state = get_default_app_state().await;
        state.registry_insecure = false;
        let context_url = "http://test-0:8080/contexts/abc123".to_string();
        let manager = get_custom_test_manager(Some(state), None).await;
        let job = manager
            .create_job_object(&context_url)
            .expect("unable to create job object");
        let containers = job.spec.unwrap().template.spec.unwrap().containers;
        let args = containers[0].args.as_ref().unwrap();
        assert!(args
            .iter()
            .all(|line| { !line.contains(",registry.insecure=true") }));
    }

    #[tokio::test]
    async fn test_create_job_object_with_resources() {
        let resources = json!({
            "requests": {
                "cpu": "4",
                "memory": "32Gi",
            },
            "limits": {
                "cpu": "8000m",
                "memory": "128Gi",
            }
        })
        .to_string();

        let mut state = get_default_app_state().await;
        state.build_resources = resources;

        let context_url = "http://test-0:8080/contexts/abc123".to_string();
        let manager = get_custom_test_manager(Some(state), None).await;
        let job = manager
            .create_job_object(&context_url)
            .expect("unable to create job object");
        let containers = job.spec.unwrap().template.spec.unwrap().containers;
        let resources = containers[0].resources.as_ref().unwrap();
        let requests = resources.requests.as_ref().unwrap();
        let limits = resources.limits.as_ref().unwrap();
        assert_eq!(requests["cpu"], Quantity("4".to_string()));
        assert_eq!(requests["memory"], Quantity("32Gi".to_string()));
        assert_eq!(limits["cpu"], Quantity("8000m".to_string()));
        assert_eq!(limits["memory"], Quantity("128Gi".to_string()));
    }

    #[tokio::test]
    async fn test_create_job_object_with_default_timeout() {
        let context_url = "http://test-0:8080/contexts/abc123".to_string();
        let manager = get_default_test_manager().await;
        let job = manager
            .create_job_object(&context_url)
            .expect("unable to create job object");
        assert_eq!(job.spec.unwrap().active_deadline_seconds, Some(3600));
    }

    #[tokio::test]
    async fn test_create_job_object_with_user_timeout() {
        let mut build_config = get_default_build_config();
        build_config.timeout = Some(10);
        let context_url = "http://test-0:8080/contexts/abc123".to_string();
        let manager = get_custom_test_manager(None, Some(build_config)).await;
        let job = manager
            .create_job_object(&context_url)
            .expect("unable to create job object");
        assert_eq!(job.spec.unwrap().active_deadline_seconds, Some(10));
    }

    #[tokio::test]
    async fn test_create_job_object_with_ttl_after_finished() {
        let mut state = get_default_app_state().await;
        state.build_ttl_after_finished = 600;

        let context_url = "http://test-0:8080/contexts/abc123".to_string();
        let manager = get_custom_test_manager(Some(state), None).await;
        let job = manager
            .create_job_object(&context_url)
            .expect("unable to create job object");
        assert_eq!(job.spec.unwrap().ttl_seconds_after_finished, Some(600));
    }

    #[tokio::test]
    async fn test_create_job_object_without_registry_credentials() {
        let context_url = "http://test-0:8080/contexts/abc123".to_string();
        let manager = get_default_test_manager().await;
        let job = manager
            .create_job_object(&context_url)
            .expect("unable to create job object");
        let spec = job.spec.unwrap().template.spec.unwrap();
        let volumes = &spec.volumes.unwrap();
        assert_eq!(volumes.len(), 1);
        assert!(volumes.iter().all(|v| {
            if let Some(s) = v.secret.as_ref() {
                s.secret_name != Some("my-registry-creds".to_string())
            } else {
                true
            }
        }));
        let volume_mounts = spec.containers[0].volume_mounts.as_ref().unwrap();
        assert_eq!(volume_mounts.len(), 1);
        assert!(volume_mounts.iter().all(|vm| vm.name != "creds"))
    }

    #[tokio::test]
    async fn test_create_job_object_with_registry_credentials() {
        let mut state = get_default_app_state().await;
        state.registry_credentials_secret_name = "my-registry-creds".to_string();

        let context_url = "http://test-0:8080/contexts/abc123".to_string();
        let manager = get_custom_test_manager(Some(state), None).await;
        let job = manager
            .create_job_object(&context_url)
            .expect("unable to create job object");
        let spec = job.spec.unwrap().template.spec.unwrap();
        let volumes = &spec.volumes.unwrap();
        assert_eq!(volumes.len(), 2);
        assert!(volumes.iter().any(|v| {
            if let Some(s) = v.secret.as_ref() {
                s.secret_name == Some("my-registry-creds".to_string())
            } else {
                false
            }
        }));
        let volume_mounts = spec.containers[0].volume_mounts.as_ref().unwrap();
        assert_eq!(volume_mounts.len(), 2);
        assert!(volume_mounts.iter().any(|vm| vm.name == "creds"))
    }
}
