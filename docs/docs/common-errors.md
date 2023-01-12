# Frequently Asked Questions

## Service Congifuration and Setup

**Does Chassis only build and push *public* container images to Docker Hub?**

No, as a configuration step before you install the Chassis helm charts, you can set up a private Docker registry that Chassis will use as the destination to push all container images. However, note that this is only available if you set up Chassis manually. Follow our [manual install](./tutorials/deploy-manual.md) and [private registry support](./how-to-guides/private-registry.md) guides for more details.  

**Why am I getting an OOM error in Kubernetes when I run a Chassis job?**

If you are seeing an OOM error, you likely installed Chassis in a local Kubernetes cluster (e.g., minikube, Kubernetes in Docker Desktop, etc.). If the pod that was running your Chassis job has an `OOM` status, that means the pod did not have enough memory to complete the process. To further verify this, check the logs of the pod: 

```bash
kubectl logs chassis-builder-job-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx-xxxx kaniko
``` 

If the logs do not end in an error, or in other words, the job seemingly just stops randomly, this likely means the pod was killed mid-process due to a lack of RAM, which can happen when building container images for larger models (typically ~3-5GB or higher). To fix this, stop your cluster and before restarting it, make sure you have allocated enough RAM and CPUs to complete your jobs.  

## SDK and User Workflow

**What is the purpose of the `process` function?**

Amongst other benefits the service provides, Chassis abstracts any user interaction with containers, Kubernetes, or web servers - all of which are essential technologies to operationalize machine learning models. In doing so, Chassis performs a lot of automatic inferring of package dependencies, objects, or utility functions your model requires to run inference. Consequently, the `process` function gives users the opportunity to include all relevent inference code in a single function. In short, you can think of the `process` function as your model inference function that can access previously defined functions, model objects, variables, and dependencies. Chassis will simply take everything included in this function, serialize it as a `ChassisModel` object, and build a Docker container out of these assets.   

**What are the required format(s) of my `process` function's input and outputs?**

Throughout the site's tutorials, examples, and how-to-guides, you have likely seen mention of a `process` function. This function acts as your model inferencing function and is required to create your `ChassisModel` object. There are two things you must consider when creating your `process` function:

1. The input parameter for this method will *always* be of type `bytes`. As a result, you must adjust your code to process the input data as raw bytes. This data format is likely different than you are used to working with (e.g., if your model normally expects a text string, say "Hello World!", you will need to decode the raw bytes into the expected format, or a text string). If working with raw bytes is unfamiliar to you, no need to worry! We document and include code snippets for decoding raw bytes in many common data types. Check out [Support for Common Data Types](./how-to-guides/common-data-types.md) to learn more.
2. The output of your `process` function *must* be JSON serializable. In other words, the Chassis service will take the output of your process function and feed it to a `json.dumps()` method. For example, if you wanted your model to return JSON, your `process` function should simply return a `Dict` object, which can be serialized with a `json.dumps()` method. 

## General

**What is Chassis?**

Check out our [Conceptual Guides](./conceptual-guides/overview.md) page to learn more!

**How can Chassis be used?**

Chassis is a powerful tool that can be used to accelerate and automate workflows. For data scientists, Chassis provides an inuitive interface to automatically build containers out of models without any prior knowledge of Docker. Machine learning engineers and DevOps teams can leverage the Chassis API to enhance CI/CD processes with automatic model containerization and deployment to their serving platform of choice. Below are some examples of Chassis in action:

* [Jupyter Notebook Examples](https://github.com/modzy/chassis/tree/main/chassisml_sdk/examples)
* [GitHub Actions Example](https://github.com/modzy/github-workflow-model-deployment)
