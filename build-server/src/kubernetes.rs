use crate::build::BuildConfig;
use crate::Error;
use handlebars::Handlebars;
use k8s_openapi::api::batch::v1::Job;
use serde_json::json;

pub(crate) fn create_job_object(
    build_config: &BuildConfig,
    job_id: &str,
    context_url: &String,
    templates: &Handlebars,
) -> Result<Job, Error> {
    let job_name = build_job_name(job_id);
    let image_name = &build_config.image_name;
    let data = json!({
        "JOB_NAME": job_name,
        "JOB_IDENTIFIER": job_id,
        "IMAGE_NAME": image_name,
        "CPU_CORES": "2",
        "MEMORY": "8Gi",
    });
    let manifest = templates.render("job", &data)?;
    let job: Job = serde_yaml::from_str(manifest.as_str())?;
    Ok(job)
}

fn build_job_name(job_id: &str) -> String {
    format!("chassis-remote-build-job-{}", job_id)
}

#[cfg(test)]
mod tests {
    use super::create_job_object;
    use crate::build::BuildConfig;
    use crate::AppState;
    use actix_web::web;
    use handlebars::Handlebars;
    use kube::Client;

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
            context_dir: "/tmp".to_string(),
            pod_name: "test-0".to_string(),
            port: "8080".to_string(),
            template_registry,
        });

        let build_config = BuildConfig {
            image_name: "".to_string(),
            tag: "".to_string(),
            publish: false,
            webhook: "".to_string(),
            registry_creds: "".to_string(),
        };
        let context_url = "http://test-0:8080/contexts/abc123".to_string();

        let job = create_job_object(
            &build_config,
            "abc123",
            &context_url,
            &state.template_registry,
        )
        .expect("unable to create job object");
        assert!(job
            .metadata
            .labels
            .unwrap()
            .contains_key("chassisml.io/job-identifier"));
        assert_eq!(
            job.metadata.name.unwrap(),
            "chassis-remote-build-job-abc123"
        );
    }
}
