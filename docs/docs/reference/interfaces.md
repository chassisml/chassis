# Interfaces

Chassis containers currently support two different interfaces: the [Open Model Interface](https://modzy.github.io/openmodelinterface/) (OMI) and [KServe v1](https://kserve.github.io/website/0.10/modelserving/data_plane/v1_protocol/). These interfaces provide a way to interact with containerized models, primiarly for running inferences. When building a model container with Chassis, its possible to specify which of these two interfaces you wish to use. Below you'll find more information about how to interact with model containers using each type of interface provided.

## OMI
The Open Model Interace is a specification for a multi-platform [OCI-compliant](https://opencontainers.org) container image designed specifically for machine learning models.

The OMI server provides a gRPC interface defined by OMI's [protofile](../protos/chassis/protos/v1/model.proto). This interface provides three remote procedure calls (RPCs) that are used to interact with a chassis contianer: `Run`, `Status`, and `Shutdown`. The Run RPC is most important, as it provides a simple way to run inferences through models packaged into chassis container images.

| RPC      | Input                                                                                                     | Description                                                                    | Example Response                                                                                                                                                                                                                                                                                                                             |
|----------|-----------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Status   | None                                                                                                      | Returns the status of a running model.                                         | {     "inputs": [...],     "outputs": [...],     "status_code": 200,     "status": "OK",     "message": "Model Initialized Successfully.",     "model_info": {         "model_name": "Digits Classifier",         "model_version": "0.0.1",         "model_author": "",         "model_type": "grpc",         "source": "chassis"     }... } |
| Run      | A run request message which includes one or more key value pairs, each representing a single model input. | Submits data to a running model for inference and returns the model's results. | [{"data": {"result": {"classPredictions": [{"class": 5, "score": 0.71212}]}}}]                                                                                                                                                                                                                                                               |
| Shutdown | None                                                                                                      | Sends the model container a shutdown message.                                  | {    "status_code": 200, "status": "OK", "message": "Model Shutdown Successfully." }                                                                                                                                                                                                                                                         |

!!! tip "Best ways to work with OMI models"
    Because OMI models use gRPC rather than RESTful APIs, there are 3 ways to build applications that can interact with an OMI model:

    1. [RECOMMENDED] Via the [OMI Python client](../sdk/chassis/client/omi/) which is automatically installed when you `pip install chassisml`
    2. By building a language-specific client directly from the OMI [protofile](https://github.com/modzy/chassis/blob/main/protos/chassis/protos/v1/model.proto) (best option for non-Python applications)
    3. By building a language-specific client using [server reflection](https://grpc.github.io/grpc/core/md_doc_server_reflection_tutorial.html) on a running chassis model container


## KServe V1
KServe's V1 protocol offers a standardized prediction workflow across all model frameworks. This protocol version is still supported, but it is recommended that users migrate to the V2 protocol for better performance and standardization among serving runtimes. However, if a use case requires a more flexible schema than protocol v2 provides, v1 protocol is still an option.

| API         | Verb | Path                            | Request Payload      | Response Payload                        |
|-------------|------|---------------------------------|----------------------|-----------------------------------------|
| List Models | GET  | /v1/models                      |                      | {"models": [<model_name>]}              |
| Model Ready | GET  | /v1/models/<model_name>         |                      | {"name": <model_name>,"ready": $bool}   |
| Predict     | POST | /v1/models/<model_name>:predict | {"instances": []} ** | {"predictions": []}                     |
| Explain     | POST | /v1/models/<model_name>:explain | {"instances": []} ** | {"predictions": [], "explanations": []} |

See Kserve's documentation for full details:
[https://kserve.github.io/website/0.10/modelserving/data_plane/v1_protocol/](https://kserve.github.io/website/0.10/modelserving/data_plane/v1_protocol/)