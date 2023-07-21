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
        self.info = info if info is not None else ModelInfo(source="chassis", model_type="grpc")
        self.description = description if description is not None else ModelDescription()
        self.inputs = inputs if inputs is not None else [
            ModelInput(
                filename="input",
                accepted_media_types=["application/octet-stream"],
                max_size="10M",
            )
        ]
        self.outputs = outputs if outputs is not None else [
            ModelOutput(
                filename="results.json",
                media_type="application/json",
                max_size="1M",
            )
        ]
        self.resources = resources if resources is not None else ModelResources(
            required_ram="512M",
            num_cpus=1,
            num_gpus=0,
        )
        self.timeout = timeout if timeout is not None else ModelTimeout(
            status="60s",
            run="60s",
        )
        self.features = features if features is not None else ModelFeatures(
            batch_size=1,
        )

    @classmethod
    def default(cls: Type[T]) -> T:
        md = cls()
        return md
