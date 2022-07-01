![Chassis logo](https://github.com/modzy/chassis/blob/main/docs/docs/images/chassis-logo.png)

# Containerizing your models easily

## Goals

- Provide the MLOps community with a simple way to convert AI/ML models written in standard AI/ML frameworks into [OMI](https://www.openmodel.ml) compliant containers that can run anywhere
- Provide the MLOps community [documentation](https://chassis.ml/) and [usage](https://github.com/modzy/chassis/tree/main/chassisml-sdk/examples) examples accessible to Data Scientists and DevOps engineers of all skill levels

## Overview
 
Chassis converts AI Models into containers that can be run anywhere e.g. converts a Sklearn Random forrest classifier into a Docker container that can be run locally by a docker deamon, on [KServe](https://www.kubeflow.org/docs/external-add-ons/kserve/kserve/), or via [Modzy](http://www.modzy.com).

Chassis runs as a Kubernetes service that can be [deployed](https://chassis.ml/tutorials/devops-deploy/) into your preferred cluster using Chassis-provided Helm charts. Chassis works by making a series of reasonable assumptions related to the resources needed for production inference with standard AI/ML models. The Chassis service then uses those assumptions to programmatically carry out the DevOps steps required to wrap your AI/ML model into a production level Docker image before uploading it to dockerhub for you to use. 

Interacting with Chassis is most easily accomplaished through the officially supported [Python SDK](https://pypi.org/project/chassisml/); however, Chassis's RESTful API architecture allows for any modern program to access chassis through HTTP requests.

Chassis's development and usage paradigms are governed by 3 principles:

**Simple**

- No DevOps knowledge needed
- Just make a request to build your image using the python SDK
- Small set of dependencies: mlflow, flask
- Supports multiple deployment platforms


**Fast**

- Start building the image as soon as you make the request
- Automatically upload the image to Docker Hub
- Images are production level and ready to be deployed

**Secure**

- Using [Kaniko](https://github.com/GoogleContainerTools/kaniko/) to securely build the image

## Getting Started

Follow one of our tutorials to easily get started and see how Chassis works:

- [Install with Helm](https://modzy.github.io/chassis/tutorials/devops-deploy) into a Cluster
- [Build an image](https://modzy.github.io/chassis/tutorials/ds-connect)
- [Deploy to KServe](https://modzy.github.io/chassis/tutorials/ds-deploy) the built image

## Contributors

A full list of contributors, which includes individuals that have contributed entries, can be found [here](https://github.com/modzy/chassis/graphs/contributors).
