# Model Containerizer for K8s

![Chassis logo](images/chassis-logo.png){: style="width:200px; margin-bottom:10px;" }

* Build [MLflow](https://mlflow.org/) models directly into DevOps-ready container images for inference
* Supports parallel builds in Kubernetes jobs, using [Kaniko](https://github.com/GoogleContainerTools/kaniko), no Docker socket required!
* Generates [Open Model Interface](https://openmodel.ml) compatible images that are multi-purpose and portable, they work on multiple platforms: KFServing and Modzy
* Try the test drive today, then deploy our Helm chart to your K8s cluster to use it for real

## Test Drive

The fastest way to get started is to use the test drive functionality provided by [Testfaster](https://testfaster.ci). Click on the "Launch Test Drive" button below (opens a new window).

<a href="https://testfaster.ci/launch?embedded=true&repo=https://github.com/combinator-ml/terraform-k8s-chassis&file=examples/testfaster/.testfaster.yml" target="_blank">:computer: Launch Test Drive :computer:</a>

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
  <iframe width="1280" height="720" src="https://www.youtube.com/embed/3i4ynyECo_I" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>

## Getting Started

Follow one of our tutorials to easily get started and see how Chassis works:

- [Install with Helm](tutorials/devops-deploy.md) into a Kubernetes cluster
- [Build a container image](tutorials/ds-connect) from an MLflow model
- [Deploy to KFServing](tutorials/ds-deploy.md) the built image

## Shameless plug

Chassis is developed by [Modzy](https://modzy.com), a commercial ModelOps platform designed to run any kind of machine learning and artifical intelligence model in production, at scale, with enterprise grade security, governance, and compliance. The design of Chassis grew out of Modzy's internal research and development to provide a way to easily containerize MLflow models to publish into the [Modzy catalog](https://www.modzy.com/marketplace/) and to support all kinds of models, both present and future, with first-class support for emerging capabilities like drift detection, explainability, and adversarial defense.

## Contributors

A full list of contributors can be found [here](https://github.com/modzy/chassis/graphs/contributors).
