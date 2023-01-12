# Private Docker Registry Support

By default, installing the Chassis service will push all container images to a *public* Docker Hub account, which requires you to have valid credentials. If instead you have access to a private Docker registry and prefer your Chassis-built containers get pushed to your own registry, this guide walks through the process (and some examples) of setting up the Chassis service with the proper configuration.

!!! info "Important Notes"
    * Only [HTTP API v2](https://docs.docker.com/registry/spec/api/) compliant Docker registries are supported
    * This configuration is only available if you deploy and host the service. The publicly-hosted version only pushes public images to your Docker Hub account 

## Generate Kubernetes Secrets

We first need to generate a Kubernetes secret of type `dockerconfigjson` that contains Docker registry credentials with push/pull permissions. This command varies slightly depending on your Docker registry.

=== "Docker Registry"
    ```bash
    kubectl create secret docker-registry <registry-secret-name> \
        --docker-server=<private-registry-url> \
        --docker-email=<private-registry-email> \
        --docker-username=<private-registry-user> \
        --docker-password=<private-registry-password>
    ```  
=== "Amazon ECR"
    ```bash
    kubectl create secret docker-registry <registry-secret-name> \
        --docker-server=<AWS-Account>.dkr.ecr.<AWS-region>.amazonaws.com \
        --docker-username=AWS \
        --docker-password=$(aws ecr get-login-password)
    ```    
=== "Azure Container Registry"
    ```bash
    kubectl create secret docker-registry <registry-secret-name> \
        --docker-server=<container-registry-name>.azurecr.io \
        --docker-username=<service-principal-ID> \
        --docker-password=<service-principal-password>
    ```  
=== "Google GCR"
    We will use the JSON key method to generate a secret with valid GCR credentials. To do so, log into your Google Cloud Console, navigate to your service account and either generate a new JSON key or download an existing JSON key file. Use this file to generate your Kubernetes secret:

    ```bash
    kubectl create secret docker-registry <registry-secret-name> \
        --docker-server=<container-registry-name>.gcr.io \
        --docker-username=_json_key \
        --docker-password="$(cat ~/json-key-file.json)"
    ```
    Replace `~/json-key-file,json` with the path to your JSON key file.      


## Create `values.yml` file

After our Kubernetes secret is successfully generated, we will need to add this secret to a `values.yml` file that will ultimately be used to modify a few values in the Chassis helm chart. In this yaml file, we will also specify the URL of our private registry. See examples for the above registry types below: 

=== "Docker Registry"
    ``` yaml title="values.yml"
    registry:
        url: "<private-registry-url>"
        credentialsSecretName: "<registry-secret-name>"
        repositoryPrefix: ""

    image:
        pullPolicy: IfNotPresent
        tag: "1f20586e050416239b055faa18baf35ce5707a32" # Commit hash for latest version of Chassis service
    ```
=== "Amazon ECR"
    ``` yaml title="values.yml"
    registry:
        url: "<AWS-Account>.dkr.ecr.<AWS-region>.amazonaws.com"
        credentialsSecretName: "<registry-secret-name>"
        repositoryPrefix: ""

    image:
        pullPolicy: IfNotPresent
        tag: "1f20586e050416239b055faa18baf35ce5707a32" # Commit hash for latest version of Chassis service
    ```
=== "Azure Container Registry"
    ``` yaml title="values.yml"
    registry:
        url: "<container-registry-name>.azurecr.io"
        credentialsSecretName: "<registry-secret-name>"
        repositoryPrefix: ""

    image:
        pullPolicy: IfNotPresent
        tag: "1f20586e050416239b055faa18baf35ce5707a32" # Commit hash for latest version of Chassis service
    ```
=== "Google GCR"
    ``` yaml title="values.yml"
    registry:
        url: "<container-registry-name>.gcr.io"
        credentialsSecretName: "<registry-secret-name>"
        repositoryPrefix: ""

    image:
        pullPolicy: IfNotPresent
        tag: "1f20586e050416239b055faa18baf35ce5707a32" # Commit hash for latest version of Chassis service
    ```

## Install `Chassis` Service

Now, we just need to use our newly generated `values.yml` file to install the Chassis service using `helm`.

``` bash
helm install chassis chassis/chassis -f values.yml
```

Visit this [Installation guide](../tutorials/deploy-manual.md) for full installation details.


