# How a DevOps person would deploy Chassis

## Add and install helm repo

```bash
helm repo add chassis https://mlopsworks.github.io/chassis
helm repo update
```

```bash
helm install chassis modzy/chassis
```

## Check pods

You can see both minio and chassis deployed in your cluster just listing the pods.

```bash
kubectl get pods
```
