#Overview

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

- Deploy the built image - this is up to the platform that you deploy the container into, like KServe or Modzy

## Intro Video

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