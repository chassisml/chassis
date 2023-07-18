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
