# Install Remote Service

This tutorial provides end-to-end instructions for installing the Chassis service on a remote Kubernetes cluster. 

!!! warning "What you will need"
    To follow this tutorial, make sure you have met the following requirements

    - [x] **Kubernetes**: we recommend any non-development Kubernetes distribution to stand up and host the service 
    - [x] **Docker registry**: required to stand up remote service. *Note*: only [HTTP API v2](https://docs.docker.com/registry/spec/api/) compliant Docker registries are supported 
    - [x] **Helm**: used to install the Chassis helm chart. Follow these [installation instructions](https://helm.sh/docs/intro/install/) if needed


With these prerequisites met, you can now install the Chassis remote service with your custom configuration, all using helm.

## Add the Helm repository

First, add the Chassis helm repository to your cluster.

```bash
helm repo add chassis https://modzy.github.io/chassis
```

Next, update the Helm repositories to fetch `Chassis` data.

```bash
helm repo update
```

## Configure private Docker registry settings

To install the remote Chassis service, you must configure the Chassis values yaml file with your own Docker registry (only [Docker v2](https://docs.docker.com/registry/spec/api/) registries are supported). When properly configured, the remote service will build container images and push them to this registry.  

If your registry is private and requires credentials, you can generate a Kubernetes secret and pass the name of this secret into your `values.yml` file.

**1. Generate Kuberentes secret containing registry credentials (*Optional*)**

If your registry requires credentials, generate a Kubernetes secret of type `dockerconfigjson` that contains Docker registry credentials with push/pull permissions.

!!! example "Kubernetes Secret"

    === "Terminal"
        
        Run this code directly in your terminal

        ```bash
        kubectl create secret docker-registry <registry-secret-name> \
          --docker-server=<private-registry-url> \
          --docker-email=<private-registry-email> \
          --docker-username=<private-registry-user> \
          --docker-password=<private-registry-password>
        ```

        ***Note:*** Keep the name of your secret (`<registry-secret-name>`) for the next step

Visit [Managing Secrets using kubectl](https://kubernetes.io/docs/tasks/configmap-secret/managing-secret-using-kubectl/) for more details.

**2. Create Values File for Helm Chart**

Next, create a `values.yml` file that contains fields required to install the remote service. Below is an example file that contains most of the fields you might want to change. Follow these guidelines when filling out your file:

- [x] **Registry** (Mandatory): Section to add in your Docker registry configuration, including the url, secret name if it requires credentials to access, repository prefix, and whether or not it is insecure
- [x] **Persistence** (*Optional*): Configuration of persistence volumes
- [x] **Builder** (*Optional*): Configuration for service-specific fields, including timeouts, resources allocated to builder pods, and duration of time until removing finished jobs

!!! example "Values File"

    === "YAML"

        **Note**: If you are using a Docker registry that requires credentials, make sure you paste the name of the Kubernetes secret you created above in the `credentialsSecretName` field under the `registry` section. 

        ``` yaml title="values.yml"
        registry:
          # The base URL to the destination registry that Chassis will push final
          url: ""
          # The name of a Kubernetes secret of type "dockerconfigjson"
          credentialsSecretName: "" # "<registry-secret-name>" - same name as Kubernetes secret created above
          # Optional prefix to be applied to image repositories created by Chassis
          repositoryPrefix: ""
          # Set to true if the registry is considered insecure. An insecure registry
          # is one that is hosted using HTTP or uses an untrusted TLS certificate.
          insecure: false

        persistence:
          # The max context size that the API supports is 20Gi so setting the value to
          # lower than 20Gi could result in undefined behavior. If you need to support
          # deploying multiple large models simultaneously then you should increase
          # this value.
          size: 20Gi
          accessMode: ReadWriteOnce
          #storageClass: default

        builder:
          # Set the timeout for how long a build job can take before it is canceled.
          timeout: 3600 # in seconds; 3600 == one hour
          # Set the amount of time before the Job is cleaned up and removed from
          # Kubernetes.
          ttlSecondsAfterFinished: 3600 # in seconds; 3600 == one hour
          # Set the resource requests and limits used by the builder job pods.
          resources: {}
          # limits:
          #   cpu: 100m
          #   memory: 128Mi
          # requests:
          #   cpu: 100m
          #   memory: 128Mi
        ```


## Install `Chassis` service

Now we just need to install `Chassis` as normal using Helm.

!!! example "Install Service"

    === "Terminal"
        ``` bash
        helm install chassis chassis/chassis -f values.yaml
        ```

## Check the installation

After having installed the service we can check that the `Chassis` service is correctly deployed.

!!! example "Check Service"

    === "Terminal"
        ``` bash
        kubectl get svc/chassis
        ```

Then you should see an output similar to this.

```bash
NAME      TYPE       CLUSTER-IP       EXTERNAL-IP   PORT(S)          AGE
chassis   NodePort   10.106.209.207   <none>        80:30496/TCP   15s
```

We can also check that the pod that runs the service is correctly running.

```bash
kubectl get pods
```

Where we should find our pod listed.

```bash
NAME                       READY   STATUS    RESTARTS   AGE
(...)
chassis-5c574d459c-rclx9   1/1     Running   0          22s
(...)
```

### Query the service

To conclude, we can query the service just to see that it answers as we expect.

To do that, we need to port forward the service.

```bash
kubectl port-forward svc/chassis 8080:8080
```

Now that we have access to the service we can query it.

```bash
curl localhost:8080
```

Which should output an alive message.

## Begin Using Remote Service

Congratulations, you have now successfully deployed the service in a private Kubernetes cluster. To get started, make sure you set up a [Python virtual enviornment](https://realpython.com/what-is-pip/#using-pip-in-a-python-virtual-environment) and install the `chassisml` SDK.

```bash
pip install chassisml
```

For more resources, check out our [tutorials](../tutorials/index.md) and [how-to guides](../how-to-guides/index.md).
