# How a DevOps person would deploy the Containerizer

## Add and install helm repo

```bash
helm repo add containerizer https://mlopsworks.github.io/containerizer
helm repo update
```

```bash
helm install containerizer containerizer/containerizer
```

## Check pods

You can see both minio and containerizer deployed in your cluster just listing the pods.

```bash
kubectl get pods
```
