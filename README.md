![Chassis logo](https://github.com/modzy/chassis/blob/main/docs/docs/images/chassis-logo.png)

# Containerizing your models easily

## Goals

Chassis is a Kubernetes service that can be deployed in your preferred cluster using Helm. It works by creating jobs that can be run in parallel to create Docker images that package ML models. It provides integration with most common deployment platforms so your model will be ready to be deployed in a simple way.

It also provides a python SDK that makes it very easy to communicate with Chassis service in order to build your image.

**Simple**

- Just make a request to build your image using the python SDK
- Small set of dependencies: mlflow, flask
- Supports multiple deployment platforms
- No DevOps knowledge needed

**Fast**

- Start building the image as soon as you make the request
- Automatically upload the image to Docker Hub
- Image ready to be deployed

**Secure**

- Using [Kaniko](https://github.com/GoogleContainerTools/kaniko/) to securely build the image

## Getting Started

Follow one of our tutorials to easily get started and see how Chassis works:

- [Install with Helm](https://modzy.github.io/chassis/tutorials/devops-deploy.html) into a Cluster
- [Build and image](https://modzy.github.io/chassis/tutorials/ds-connect.html)
- [Deploy to KFServing](https://modzy.github.io/chassis/tutorials/ds-deploy.html) the built image

## Contributors

A full list of contributors, which includes individuals that have contributed entries, can be found [here](https://github.com/modzy/chassis/graphs/contributors).
