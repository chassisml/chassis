from typing import List, Type, TypeVar

from chassis.protos.v1.model_pb2 import (ModelDescription, ModelFeatures, ModelInfo, ModelInput, ModelOutput, ModelResources, ModelTimeout)

T = TypeVar("T", bound="ModelMetadata")


class ModelMetadata:
    info: ModelInfo
    description: ModelDescription
    inputs: List[ModelInput]
    outputs: List[ModelOutput]
    resources: ModelResources
    timeout: ModelTimeout
    features: ModelFeatures

    def __init__(self, info: ModelInfo = None, description: ModelDescription = None, inputs: List[ModelInput] = None, outputs: List[ModelOutput] = None, resources: ModelResources = None, timeout: ModelTimeout = None, features: ModelFeatures = None):
        md = ModelMetadata.default()
        self.info = info if info is not None else md.info
        self.description = description if description is not None else md.description
        self.inputs = inputs if inputs is not None else md.inputs
        self.outputs = outputs if outputs is not None else md.outputs
        self.resources = resources if resources is not None else md.resources
        self.timeout = timeout if timeout is not None else md.timeout
        self.features = features if features is not None else md.features

    @classmethod
    def default(cls: Type[T]) -> T:
        md = cls()
        md.info = ModelInfo(source="chassis", model_type="grpc")
        md.description = ModelDescription()
        md.inputs = [
            ModelInput(
                filename="input",
                accepted_media_types=["application/octet-stream"],
                max_size="10M",
            )
        ]
        md.outputs = [
            ModelOutput(
                filename="results.json",
                media_type="application/json",
                max_size="1M",
            )
        ]
        md.resources = ModelResources(
            required_ram="512M",
            num_cpus=1,
            num_gpus=0,
        )
        md.timeout = ModelTimeout(
            status="60s",
            run="60s",
        )
        md.features = ModelFeatures(
            batch_size=1,
        )
        return md
