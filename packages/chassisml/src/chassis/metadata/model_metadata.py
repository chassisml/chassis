from __future__ import annotations

from typing import List, Optional

from chassis.protos.v1.model_pb2 import (ModelDescription, ModelFeatures,
                                         ModelInfo, ModelInput, ModelOutput,
                                         ModelResources, ModelTimeout,
                                         StatusResponse)


class ModelMetadata:
    """
    This class provides an interface for customizing metadata embedded into
    the model container.
    """

    def __init__(self,
                 info: Optional[ModelInfo] = None,
                 description: Optional[ModelDescription] = None,
                 inputs: Optional[List[ModelInput]] = None,
                 outputs: Optional[List[ModelOutput]] = None,
                 resources: Optional[ModelResources] = None,
                 timeout: Optional[ModelTimeout] = None,
                 features: Optional[ModelFeatures] = None):
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
    def model_name(self) -> str:
        """The human-readable name of the model."""
        return self._info.model_name

    @model_name.setter
    def model_name(self, name):
        self._info.model_name = name

    @property
    def model_version(self) -> str:
        """The semantic-versioning compatible version of the model."""
        return self._info.model_version

    @model_version.setter
    def model_version(self, version):
        self._info.model_version = version

    @property
    def model_author(self) -> str:
        """
        The name and optional email of the author.

        Example:
            John Smith <john.smith@example.com>
        """
        return self._info.model_author

    @model_author.setter
    def model_author(self, author):
        self._info.model_author = author

    @property
    def summary(self) -> str:
        """A short summary of what the model does and how to use it."""
        return self._description.summary

    @summary.setter
    def summary(self, summary):
        self._description.summary = summary

    @property
    def details(self) -> str:
        """
        A longer description of the model that contains useful information
        that was unsuitable to put in the Summary.
        """
        return self._description.details

    @details.setter
    def details(self, details):
        self._description.details = details

    @property
    def technical(self) -> str:
        """
        Technical information about the model such as how it was trained, any
        known biases, the dataset that was used, etc.
        """
        return self._description.technical

    @technical.setter
    def technical(self, technical):
        self._description.technical = technical

    @property
    def performance(self) -> str:
        """Performance information about the model."""
        return self._description.performance

    @performance.setter
    def performance(self, performance):
        self._description.performance = performance

    def has_inputs(self) -> bool:
        """
        Returns:
            `True` if at least one input has been defined.
        """
        return len(self._inputs) > 0

    def add_input(self, key: str, accepted_media_types: Optional[List[str]] = None,
                  max_size: str = "1M", description: str = ""):
        """
        Defines an input to the model. Inputs are identified by a string `key`
        that will be used to retrieve them from the dictionary of inputs during
        inference.

        Since all input values are sent as `bytes`, each input should define
        one or more MIME types that are suitable for decoding the bytes into a
        usable object.

        Additionally, each input can be set to have a maximum size to easily
        reject requests with inputs that are too large.

        Finally, you can give each input a description which can be used in
        documentation to explain any further details about the input
        requirements, such as indicating whether color channels need to be
        stripped from the image, etc.

        Args:
             key: Key name to represent the input. E.g., "input", "image", etc.
             accepted_media_types: Acceptable mime type(s) for the respective
                input. For more information on common mime types, visit
                [https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types]()
             max_size: Maximum acceptable size of input. This value should
                include an integer followed by a letter indicating the unit of
                measure (e.g., "3M" = 3 MB, "1.5G" = 1.5 GB, etc.)
             description: Short description of the input

        Example:
        ```python
        from chassisml import ChassisModel
        model = ChassisModel(process_fn=predict)
        model.metadata.add_input(
            "image",
            ["image/png", "image/jpeg"],
            "10M",
            "Image to be classified by computer vision model"
        )
        ```
        """
        if accepted_media_types is None:
            accepted_media_types = ["application/octet-stream"]
        self._inputs = self._inputs + [ModelInput(
            filename=key,
            accepted_media_types=accepted_media_types,
            max_size=max_size,
            description=description,
        )]

    def has_outputs(self) -> bool:
        """
        Returns:
            `True` if at least one output has been defined.
        """
        return len(self._outputs) > 0

    def add_output(self, key: str, media_type: str = "application/octet-stream",
                   max_size: str = "1M", description: str = ""):
        """
        Defines an output from the model. Outputs are identified by a string
        `key` that will be used to retrieve them from the dictionary of outputs
        received after inference.

        Since all output values are sent as `bytes`, each output should define
        the MIME type that is suitable for decoding the bytes into a usable
        object.

        Additionally, each output should be set to have a maximum size to
        prevent results that are too large for practical use.

        Finally, you can give each output a description which can be used in
        documentation to explain any further details about the output.


        Args:
             key: Key name to represent the output. E.g., "results.json",
                "results", "output", etc.
             media_type: Acceptable mime type for the respective output. For
                more information on common mime types, visit
                [https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types]()
             max_size: Maximum acceptable size of output. This value should
                include an integer followed by a letter indicating the unit of
                measure (e.g., "3M" = 3 MB, "1.5G" = 1.5 GB, etc.)
             description: Short description of the output

        Example:
        ```python
        from chassisml import ChassisModel
        model = ChassisModel(process_fn=predict)
        model.metadata.add_input(
            "results.json",
            ["application/json"],
            "1M,
            "Classification results of computer vision model with class name and confidence score in JSON format"
        )
        ```
        """
        self._outputs = self._outputs + [ModelOutput(
            filename=key,
            media_type=media_type,
            max_size=max_size,
            description=description,
        )]

    @property
    def required_ram(self) -> str:
        """
        The amount of RAM required to run the model. This string can be any
        value accepted by Docker or Kubernetes.
        """
        return self._resources.required_ram

    @required_ram.setter
    def required_ram(self, required_ram):
        self._resources.required_ram = required_ram

    @property
    def num_cpus(self) -> float:
        """The number of fractional CPU cores required to run the model."""
        return self._resources.num_cpus

    @num_cpus.setter
    def num_cpus(self, num_cpus):
        self._resources.num_cpus = num_cpus

    @property
    def num_gpus(self) -> int:
        """The number of GPUs required to run the model."""
        return self._resources.num_gpus

    @num_gpus.setter
    def num_gpus(self, num_gpus):
        self._resources.num_gpus = num_gpus

    @property
    def status_timeout(self) -> str:
        """
        The amount of time after which a model should be considered to have
        failed initializing itself.
        """
        return self._timeout.status

    @status_timeout.setter
    def status_timeout(self, status_timeout):
        self._timeout.status = status_timeout

    @property
    def run_timeout(self) -> str:
        """
        The amount of time after which an inference should be considered to
        have failed.
        """
        return self._timeout.run

    @run_timeout.setter
    def run_timeout(self, run_timeout):
        self._timeout.run = run_timeout

    @property
    def batch_size(self) -> int:
        """
        The batch size supported by this model. For models that don't support
        batch, set this to 1.
        """
        return self._features.batch_size

    @batch_size.setter
    def batch_size(self, batch_size):
        self._features.batch_size = batch_size

    # TODO - adversarial defense, retrainable, results/drift/explanation formats

    def serialize(self) -> bytes:
        """
        For internal use only.

        This method will take the values of this object and serialize them in
        the protobuf message that the final container expects to receive.

        Returns:
            The serialized protobuf object.
        """
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
    def default(cls) -> ModelMetadata:
        """
        A ModelMetadata object that corresponds to the defaults used by Chassis
        v1.5+.

        The defaults are blank values for all properties. You are responsible
        for setting any appropriate values for your model.

        Note:
            It is always required to set the `model_name`, `model_version`
            fields and to add at least one input and one output.

        Returns:
            An empty `ModelMetadata` object.
        """
        md = cls()
        return md

    @classmethod
    def legacy(cls) -> ModelMetadata:
        """
        A ModelMetadata object that corresponds to the values used before
        Chassis v1.5.

        Returns:
            A partially filled `ModelMetadata` object.
        """
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
