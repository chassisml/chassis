# Install Service Manually

<!-- TODO: add link to google colab notebook -->

!!! info "Different Connection Options"
    Before following this guide, note that you can connect to the Chassis service in one of two ways:
    
    1. Continue following this guide to install the Chassis service locally on a private Kubernetes cluster
    2. Bypass this guide and follow the [instructions](../getting-started/getting-started.md) to connect to our [publicly-hosted](https://modzy.com/chassis-ml-sign-up/) and free instance of the service 

## Install required dependencies

- [X] Install [Docker Desktop](https://docs.docker.com/get-docker/)
    * Try to run `docker ps`
        * If you get a permissions error, follow instructions [here](https://docs.docker.com/engine/install/linux-postinstall/)
- [X] Install [Helm](https://helm.sh/docs/intro/install/)

*Note: If you prefer to use Minikube for your Kubernetes distribution, make sure it can access the internet. Otherwise, your Chassis build jobs will fail.*

## Enable Kubernetes

Follow [these](https://docs.docker.com/desktop/kubernetes/) instructions to enable Kubernetes in Docker Desktop.

## Add the Helm repository

```bash
helm repo add chassis https://modzy.github.io/chassis
```

After that we just need to update the Helm repos to fetch `Chassis` data.

```bash
helm repo update
```

## Configure private Docker registry settings *(Optional)*

By default, installing the Chassis service will push all container images to a *public* Docker Hub account, which requires you to have valid credentials. If instead you have access to a private Docker registry, you can add a few lines of configuration before installing the `Chassis` service using helm. *Note: only [HTTP API v2](https://docs.docker.com/registry/spec/api/) compliant Docker registries are supported.*

**1. Generate Kuberentes secret containing registry credentials**

We first need to generate a Kubernetes secret of type `dockerconfigjson` that contains Docker registry credentials with push/pull permissions.

```bash
kubectl create secret docker-registry <registry-secret-name> \
  --docker-server=<private-registry-url> \
  --docker-email=<private-registry-email> \
  --docker-username=<private-registry-user> \
  --docker-password=<private-registry-password>
```

Visit [Managing Secrets using kubectl](https://kubernetes.io/docs/tasks/configmap-secret/managing-secret-using-kubectl/) for more details.

**2. Create Values File for Helm Chart**

Next, we will create a `values.yml` file to modify a few of the default values in the Chassis helm chart. This is where you can specify the base URL of your private registry and provide the name of the secret generated in the previous step. 

``` yaml title="values.yml"
registry:
  url: "https://my-private-registry.com"
  credentialsSecretName: "<registry-secret-name>"
  repositoryPrefix: ""

image:
  pullPolicy: IfNotPresent
  tag: "1f20586e050416239b055faa18baf35ce5707a32" # Commit hash for latest version of Chassis service
```

For more details and different registry examples, visit the [Private Registry Support guide](../how-to-guides/private-registry.md).

## Install `Chassis` service

Now we just need to install `Chassis` as normal using Helm.

=== "Public Docker Hub (default)"

    ``` bash
    helm install chassis chassis/chassis
    ```

=== "Private Registry"

    ``` bash
    helm install chassis chassis/chassis -f values.yaml
    ```



## Check the installation

After having installed the service we can check that the `Chassis` service is correctly deployed.

```bash
kubectl get svc/chassis
```

Then you should see an output similar to this.

```bash
NAME      TYPE       CLUSTER-IP       EXTERNAL-IP   PORT(S)          AGE
chassis   NodePort   10.106.209.207   <none>        5000:30496/TCP   15s
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

To conclude, we may want to query the service just to see that it answers as we expect.

To do that, we need to port forward the service.

```bash
kubectl port-forward svc/chassis 5000:5000
```

Now that we have access to the service we can query it.

```bash
curl localhost:5000
```

Which should output an alive message.

## Begin Using the Service

Congratulations, you have now successfully deployed the service in a private Kubernetes cluster. To get started, make sure you set up a [Python virtual enviornment](https://realpython.com/what-is-pip/#using-pip-in-a-python-virtual-environment) and install the `chassisml` SDK.

```bash
pip install chassisml
```

For more resources, check out our [tutorials](../tutorials/ds-connect.md) and [how-to guides](../how-to-guides/frameworks.md)
