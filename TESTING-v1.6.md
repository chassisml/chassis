# Testing v1.6

In order to test changes slated for v1.6 before it's ready to be released, you'll need to
do a few manual things.

## Building the new base image

To build the new base image that has a pre-compiled Rust server that handles gRPC for
both the current (e.g. v1.5) container spec and a new gRPC server for an experimental
Open Model v2 container spec, you'll need to run the following command from the root
directory:

    docker build -t openmodel-server-python-3.11 -f servers/openmodel/Dockerfile .

Once that image is in your local Docker image cache, you can put together a new
script/notebook to build a new-format Chassis model.

NOTE: Currently it is hard-coded to link against Python 3.11 though in the future we
will use CI to do matrix builds for all the permutations of Python versions that we
want to support (e.g. 3.9, 3.10, 3.11, etc.)

## Constructing a new-format Chassis model

Below is a sample script that will allow you to build a new-format Chassis model. The
new format has some new internals behind the scenes and a new interface that will be
used to extend the new format with additional functionality in the future. Starting with
v1.6, the intention is to deprecate `chassisml.ChassisModel` and start moving everyone
over to `chassisml.v2.OpenModelContainer`.

```python
from typing import Mapping
import openmodel.v2.container_pb2
from chassis.builder import DockerBuilder, BuildOptions
from chassisml.v2 import OpenModelContainer, OpenModelContainerInfo, PredictionResult
from chassis.runtime import SimpleFunctionModel
from chassis.ftypes import PredictionOutput, ModelDrift, DataDrift
import random


def predict_v2(inputs: Mapping[str, bytes]) -> PredictionResult:
    i = []
    for k, v in inputs.items():
        i.append(f"{k}={v.decode()}")
    return PredictionResult(
        outputs=[
            PredictionOutput(
                key="result",
                text=f"Received inputs: {', '.join(i)}",
            )
        ],
        success=True,
        drift=ModelDrift(
            data_drift=DataDrift(score=max(0.0, min(1.0, random.normalvariate(mu=500, sigma=100.0) / 1000)))
        ),
    )


container_info = OpenModelContainerInfo(
    name="Chassis v2 Test Model",
    version="2.0.0",
    author=openmodel.v2.container_pb2.OpenModelContainerInfo.Author(
        name="Author Name",
        email="author_name@example.com",
    )
)
model = OpenModelContainer(
    info=container_info,
    model=SimpleFunctionModel(predict=predict_v2)
)

# Prepare Context
context_options = BuildOptions(arch="arm64", python_version="3.11")
builder = DockerBuilder(model, options=context_options)
builder.build_image("chassis-v1.6-test")
```

This branch is still very much a work in progress so let me (Nathan) know
if you run into any issues.