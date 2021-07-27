# Model Containerizer for K8s

![Chassis logo](images/chassis-logo.png){: style="width:400px; margin-bottom:10px;" }

* Build [MLflow](https://mlflow.org/) models directly into DevOps-ready container images for inference
* Supports parallel builds in Kubernetes jobs, using [Kaniko](https://github.com/GoogleContainerTools/kaniko), no Docker socket required!
* Generates [Open Model Interface](https://openmodel.ml) compatible images that are multi-purpose and portable, they work on multiple platforms: KFServing and Modzy
* Try the test drive today, then deploy our Helm chart to your K8s cluster to use it for real

## About Chassis

Chassis makes it easy to create a deployable docker image from your trained ML model.

The idea behind this project is to provide Data Scientists with a way to package their models into a Docker image. This image will manage to build the inference service compatible with several common platforms for free.

At the moment, Chassis images are compatible with KFServing and Modzy gRPC. This means you can deploy your built image into these platforms once it has been built.

Deploy Chassis, send your model to it and start using the built image to predict your data.

## Test Drive

The fastest way to get started is to use the test drive functionality provided by [Testfaster](https://testfaster.ci). Click on the "Launch Test Drive" button below (opens a new window).

<a href="https://testfaster.ci/launch?embedded=true&repo=https://github.com/combinator-ml/terraform-k8s-chassis&file=examples/testfaster/.testfaster.yml" target="\_blank">:computer: Launch Test Drive :computer:</a>

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

## Non-goals

Some non-goals of this project are:

- Deploy the built image - this is up to the platform that you deploy the container into, like KFServing or Modzy

## Getting Started

Follow one of our tutorials to easily get started and see how Chassis works:

- [Install with Helm](tutorials/devops-deploy.md) into a Cluster
- [Build a container image](tutorials/ds-connect) from an MLflow model
- [Deploy to KFServing](tutorials/ds-deploy.md) the built image

## Talk & Demo

<style>
.video-wrapper {
  position: relative;
  display: block;
  height: 0;
  padding: 0;
  overflow: hidden;
  padding-bottom: 56.25%;
  border: 1px solid gray;
}
.video-wrapper > iframe {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: 0;
}
</style>

<div class="video-wrapper">
  <iframe width="1280" height="720" src="https://www.youtube.com/embed/d_8OIfQOa3I" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>

## Shameless plug

Chassis is developed by [Modzy](https://modzy.com), a commercial ModelOps platform designed to run any kind of machine learning and artifical intelligence model in production, at scale, with enterprise grade security, governance, and compliance. The design of Chassis grew out of Modzy's internal research and development to provide a way to easily containerize MLflow models to publish into the [Modzy catalog](https://www.modzy.com/marketplace/) and to support all kinds of models, both present and future, with first-class support for emerging capabilities like drift detection, explainability, and adversarial defense.

## Contributors

A full list of contributors can be found [here](https://github.com/modzy/chassis/graphs/contributors).
