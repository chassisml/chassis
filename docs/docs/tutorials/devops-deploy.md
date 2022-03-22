# Deploy Chassis (DevOps)

<!-- TODO: add link to google colab notebook -->

## Install required dependencies

* Install [Docker Desktop](https://docs.docker.com/get-docker/)
    * Try to run `docker ps`
        * If you get a permissions error, follow instructions [here](https://docs.docker.com/engine/install/linux-postinstall/)
* Install [Kubectl](https://kubernetes.io/docs/tasks/tools/)
* Install [Helm](https://helm.sh/docs/intro/install/)
* Install [Minikube](https://minikube.sigs.k8s.io/docs/start/)
    * Start cluster: `minikube start`

## Add the Helm repository

```bash
helm repo add chassis https://modzy.github.io/chassis
```

After that we just need to update the Helm repos to fetch `Chassis` data.

```bash
helm repo update
```

## Install `Chassis` service

Now we just need to install `Chassis` as normal using Helm.

```bash
helm install chassis chassis/chassis
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
