from typing import List, Type, TypeVar

from chassis.protos.v1.model_pb2 import (ModelDescription, ModelFeatures, ModelInfo, ModelInput, ModelOutput, ModelResources, ModelTimeout, StatusResponse)

T = TypeVar("T", bound="ModelMetadata")


class ModelMetadata:

    def __init__(self, info: ModelInfo = None, description: ModelDescription = None, inputs: List[ModelInput] = None, outputs: List[ModelOutput] = None, resources: ModelResources = None, timeout: ModelTimeout = None, features: ModelFeatures = None):
        self._info: ModelInfo = info if info is not None else ModelInfo(source="chassis", model_type="grpc")
        self._description = description if description is not None else ModelDescription()
        self._inputs = inputs if inputs is not None else []
        self._outputs = outputs if outputs is not None else []
        self._resources = resources if resources is not None else ModelResources(
            required_ram="512M",
            num_cpus=1,
            num_gpus=0,
        )
        self._timeout = timeout if timeout is not None else ModelTimeout(
            status="60s",
            run="60s",
        )
        self._features = features if features is not None else ModelFeatures(
            batch_size=1,
        )

    @property
    def model_name(self):
        return self._info.model_name

    @model_name.setter
    def model_name(self, name):
        self._info.model_name = name

    @property
    def model_version(self):
        return self._info.model_version

    @model_version.setter
    def model_version(self, version):
        self._info.model_version = version

    @property
    def model_author(self):
        return self._info.model_author

    @model_author.setter
    def model_author(self, author):
        self._info.model_author = author

    @property
    def summary(self):
        return self._description.summary

    @summary.setter
    def summary(self, summary):
        self._description.summary = summary

    @property
    def details(self):
        return self._description.details

    @details.setter
    def details(self, details):
        self._description.details = details

    @property
    def technical(self):
        return self._description.technical

    @technical.setter
    def technical(self, technical):
        self._description.technical = technical

    @property
    def performance(self):
        return self._description.performance

    @performance.setter
    def performance(self, performance):
        self._description.performance = performance

    def add_input(self, key: str, accepted_media_types: list[str] = None, max_size: str = "1M", description: str = ""):
        if accepted_media_types is None:
            accepted_media_types = ["application/octet-stream"]
        self._inputs = self._inputs + [ModelInput(
            filename=key,
            accepted_media_types=accepted_media_types,
            max_size=max_size,
            description=description,
        )]

    def add_output(self, key: str, media_type: str = "application/octet-stream", max_size: str = "1M", description: str = ""):
        self._outputs = self._outputs + [ModelOutput(
            filename=key,
            media_type=media_type,
            max_size=max_size,
            description=description,
        )]

    @property
    def required_ram(self):
        return self._resources.required_ram

    @required_ram.setter
    def required_ram(self, required_ram):
        self._resources.required_ram = required_ram

    @property
    def num_cpus(self):
        return self._resources.num_cpus

    @num_cpus.setter
    def num_cpus(self, num_cpus):
        self._resources.num_cpus = num_cpus

    @property
    def num_gpus(self):
        return self._resources.num_gpus

    @num_gpus.setter
    def num_gpus(self, num_gpus):
        self._resources.num_gpus = num_gpus

    @property
    def status_timeout(self):
        return self._timeout.status

    @status_timeout.setter
    def status_timeout(self, status_timeout):
        self._timeout.status = status_timeout

    @property
    def run_timeout(self):
        return self._timeout.run

    @run_timeout.setter
    def run_timeout(self, run_timeout):
        self._timeout.run = run_timeout

    @property
    def batch_size(self):
        return self._features.batch_size

    @batch_size.setter
    def batch_size(self, batch_size):
        self._features.batch_size = batch_size

    # TODO - adversarial defense, retrainable, results/drift/explanation formats

    def serialize(self) -> bytes:
        sr = StatusResponse()
        sr.model_info.CopyFrom(self._info)
        sr.description.CopyFrom(self._description)
        sr.inputs.MergeFrom(self._inputs)
        sr.outputs.MergeFrom(self._outputs)
        sr.resources.CopyFrom(self._resources)
        sr.timeout.CopyFrom(self._timeout)
        sr.features.CopyFrom(self._features)
        return sr.SerializeToString()

    @classmethod
    def default(cls: Type[T]) -> T:
        md = cls()
        return md

    @classmethod
    def legacy(cls: Type[T]) -> T:
        md = cls()
        md._inputs = [
            ModelInput(
                filename="input",
                accepted_media_types=["application/octet-stream"],
                max_size="10M",
            )
        ]
        md._outputs = [
            ModelOutput(
                filename="results.json",
                media_type="application/json",
                max_size="1M",
            )
        ]
        md._resources = ModelResources(
            required_ram="512M",
            num_cpus=1,
            num_gpus=0,
        )
        md._timeout = ModelTimeout(
            status="60s",
            run="60s",
        )
        return md
