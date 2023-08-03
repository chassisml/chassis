use crate::manager::BuildManager;
use crate::Error;
use k8s_openapi::api::batch::v1::Job;
use k8s_openapi::api::core::v1::Pod;
use kube::api::{DeleteParams, ListParams, LogParams, PostParams};
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
        // Otherwise, use the value passed in from the build config.
        return self
            .config
            .as_ref()
            .expect("build config not available")
            .insecure_registry;
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

    async fn delete_job(&self) -> Result<(), Error> {
        let jobs: Api<Job> = Api::default_namespaced(self.state.kube_client.clone());
        let job_name = self.get_job_name();
        jobs.delete(job_name.as_str(), &DeleteParams::foreground())
            .await?;
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

        // Delete any Kubernetes secrets for this job.
        // TODO

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

    async fn get_test_manager() -> BuildManager {
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
            build_ttl_after_finished: 3600,
            build_resources: "{}".to_string(),
            registry_url: "".to_string(),
            registry_prefix: "".to_string(),
            registry_credentials_secret_name: "".to_string(),
            registry_insecure: true,
        });

        let build_config = BuildConfig {
            image_name: "".to_string(),
            tag: "".to_string(),
            publish: false,
            insecure_registry: false,
            webhook: None,
            registry_creds: None,
            timeout: None,
        };
        BuildManager::new(state, build_config).unwrap()
    }

    #[tokio::test]
    async fn test_build_image_name_without_registry_url() {
        let mut manager = get_test_manager().await;
        let config = manager.config.as_mut().unwrap();
        config.image_name = "username/image".to_string();
        config.tag = "tag".to_string();
        assert_eq!(manager.build_image_name(), "username/image:tag")
    }

    #[tokio::test]
    async fn test_build_image_name_with_registry_url() {
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
            build_ttl_after_finished: 3600,
            build_resources: "{}".to_string(),
            registry_url: "my-registry:5000".to_string(),
            registry_prefix: "".to_string(),
            registry_credentials_secret_name: "".to_string(),
            registry_insecure: true,
        });

        let build_config = BuildConfig {
            image_name: "image".to_string(),
            tag: "tag".to_string(),
            publish: false,
            insecure_registry: false,
            webhook: None,
            registry_creds: None,
            timeout: None,
        };
        let manager = BuildManager::new(state, build_config).unwrap();
        assert_eq!(manager.build_image_name(), "my-registry:5000/image:tag")
    }

    #[tokio::test]
    async fn test_build_image_name_with_registry_url_and_prefix() {
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
            build_ttl_after_finished: 3600,
            build_resources: "{}".to_string(),
            registry_url: "my-registry:5000".to_string(),
            registry_prefix: "prefix".to_string(),
            registry_credentials_secret_name: "".to_string(),
            registry_insecure: true,
        });

        let build_config = BuildConfig {
            image_name: "image".to_string(),
            tag: "tag".to_string(),
            publish: false,
            insecure_registry: false,
            webhook: None,
            registry_creds: None,
            timeout: None,
        };
        let manager = BuildManager::new(state, build_config).unwrap();
        assert_eq!(
            manager.build_image_name(),
            "my-registry:5000/prefix/image:tag"
        )
    }

    #[tokio::test]
    async fn test_build_image_name_with_registry_url_and_trailing_slash() {
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
            build_ttl_after_finished: 3600,
            build_resources: "{}".to_string(),
            registry_url: "my-registry:5000/".to_string(),
            registry_prefix: "".to_string(),
            registry_credentials_secret_name: "".to_string(),
            registry_insecure: true,
        });

        let build_config = BuildConfig {
            image_name: "username/image".to_string(),
            tag: "tag".to_string(),
            publish: false,
            insecure_registry: false,
            webhook: None,
            registry_creds: None,
            timeout: None,
        };
        let manager = BuildManager::new(state, build_config).unwrap();
        assert_eq!(
            manager.build_image_name(),
            "my-registry:5000/username/image:tag"
        )
    }

    #[tokio::test]
    async fn test_create_job_object() {
        let context_url = "http://test-0:8080/contexts/abc123".to_string();
        let manager = get_test_manager().await;

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
            build_ttl_after_finished: 3600,
            build_resources: "{}".to_string(),
            registry_url: "my-registry:5000/".to_string(),
            registry_prefix: "".to_string(),
            registry_credentials_secret_name: "".to_string(),
            registry_insecure: true,
        });

        let build_config = BuildConfig {
            image_name: "username/image".to_string(),
            tag: "tag".to_string(),
            publish: false,
            insecure_registry: false,
            webhook: None,
            registry_creds: None,
            timeout: None,
        };
        let context_url = "http://test-0:8080/contexts/abc123".to_string();
        let manager = BuildManager::new(state, build_config).unwrap();
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
            build_ttl_after_finished: 3600,
            build_resources: "{}".to_string(),
            registry_url: "my-registry:5000/".to_string(),
            registry_prefix: "".to_string(),
            registry_credentials_secret_name: "".to_string(),
            registry_insecure: false,
        });

        let build_config = BuildConfig {
            image_name: "username/image".to_string(),
            tag: "tag".to_string(),
            publish: false,
            insecure_registry: false,
            webhook: None,
            registry_creds: None,
            timeout: None,
        };
        let context_url = "http://test-0:8080/contexts/abc123".to_string();
        let manager = BuildManager::new(state, build_config).unwrap();
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
        let kube_client = Client::try_default().await.unwrap();
        let mut template_registry = Handlebars::new();
        let job_template = include_str!(concat!(env!("CARGO_MANIFEST_DIR"), "/manifests/job.yaml"));
        template_registry
            .register_template_string("job", job_template)
            .expect("failure registering job template");

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

        let state = web::Data::new(AppState {
            kube_client,
            context_path: PathBuf::from("/tmp".to_string()),
            service_name: "test".to_string(),
            pod_name: "test-0".to_string(),
            port: "8080".to_string(),
            template_registry,
            build_timeout: 3600,
            build_ttl_after_finished: 3600,
            build_resources: resources,
            registry_url: "my-registry:5000/".to_string(),
            registry_prefix: "".to_string(),
            registry_credentials_secret_name: "".to_string(),
            registry_insecure: false,
        });

        let build_config = BuildConfig {
            image_name: "username/image".to_string(),
            tag: "tag".to_string(),
            publish: false,
            insecure_registry: false,
            webhook: None,
            registry_creds: None,
            timeout: None,
        };
        let context_url = "http://test-0:8080/contexts/abc123".to_string();
        let manager = BuildManager::new(state, build_config).unwrap();
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
    async fn test_create_job_object_with_insecure_registry_from_config() {
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
            build_ttl_after_finished: 3600,
            build_resources: "{}".to_string(),
            registry_url: "".to_string(),
            registry_prefix: "".to_string(),
            registry_credentials_secret_name: "".to_string(),
            registry_insecure: false,
        });

        let build_config = BuildConfig {
            image_name: "my-registry:5000/username/image".to_string(),
            tag: "tag".to_string(),
            publish: false,
            insecure_registry: true,
            webhook: None,
            registry_creds: None,
            timeout: None,
        };
        let context_url = "http://test-0:8080/contexts/abc123".to_string();
        let manager = BuildManager::new(state, build_config).unwrap();
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
    async fn test_create_job_object_with_secure_registry_from_config() {
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
            build_ttl_after_finished: 3600,
            build_resources: "{}".to_string(),
            registry_url: "".to_string(),
            registry_prefix: "".to_string(),
            registry_credentials_secret_name: "".to_string(),
            registry_insecure: false,
        });

        let build_config = BuildConfig {
            image_name: "my-registry:5000/username/image".to_string(),
            tag: "tag".to_string(),
            publish: false,
            insecure_registry: false,
            webhook: None,
            registry_creds: None,
            timeout: None,
        };
        let context_url = "http://test-0:8080/contexts/abc123".to_string();
        let manager = BuildManager::new(state, build_config).unwrap();
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
    async fn test_create_job_object_with_default_timeout() {
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
            build_ttl_after_finished: 3600,
            build_resources: "{}".to_string(),
            registry_url: "".to_string(),
            registry_prefix: "".to_string(),
            registry_credentials_secret_name: "".to_string(),
            registry_insecure: false,
        });

        let build_config = BuildConfig {
            image_name: "my-registry:5000/username/image".to_string(),
            tag: "tag".to_string(),
            publish: false,
            insecure_registry: false,
            webhook: None,
            registry_creds: None,
            timeout: None,
        };
        let context_url = "http://test-0:8080/contexts/abc123".to_string();
        let manager = BuildManager::new(state, build_config).unwrap();
        let job = manager
            .create_job_object(&context_url)
            .expect("unable to create job object");
        assert_eq!(job.spec.unwrap().active_deadline_seconds, Some(3600));
    }

    #[tokio::test]
    async fn test_create_job_object_with_user_timeout() {
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
            build_ttl_after_finished: 3600,
            build_resources: "{}".to_string(),
            registry_url: "".to_string(),
            registry_prefix: "".to_string(),
            registry_credentials_secret_name: "".to_string(),
            registry_insecure: false,
        });

        let build_config = BuildConfig {
            image_name: "my-registry:5000/username/image".to_string(),
            tag: "tag".to_string(),
            publish: false,
            insecure_registry: false,
            webhook: None,
            registry_creds: None,
            timeout: Some(10),
        };
        let context_url = "http://test-0:8080/contexts/abc123".to_string();
        let manager = BuildManager::new(state, build_config).unwrap();
        let job = manager
            .create_job_object(&context_url)
            .expect("unable to create job object");
        assert_eq!(job.spec.unwrap().active_deadline_seconds, Some(10));
    }

    #[tokio::test]
    async fn test_create_job_object_with_ttl_after_finished() {
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
            build_ttl_after_finished: 600,
            build_resources: "{}".to_string(),
            registry_url: "".to_string(),
            registry_prefix: "".to_string(),
            registry_credentials_secret_name: "".to_string(),
            registry_insecure: false,
        });

        let build_config = BuildConfig {
            image_name: "my-registry:5000/username/image".to_string(),
            tag: "tag".to_string(),
            publish: false,
            insecure_registry: false,
            webhook: None,
            registry_creds: None,
            timeout: Some(10),
        };
        let context_url = "http://test-0:8080/contexts/abc123".to_string();
        let manager = BuildManager::new(state, build_config).unwrap();
        let job = manager
            .create_job_object(&context_url)
            .expect("unable to create job object");
        assert_eq!(job.spec.unwrap().ttl_seconds_after_finished, Some(600));
    }
}
