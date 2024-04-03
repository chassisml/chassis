from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StatusRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ModelInfo(_message.Message):
    __slots__ = ("model_name", "model_version", "model_author", "model_type", "source")
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    MODEL_VERSION_FIELD_NUMBER: _ClassVar[int]
    MODEL_AUTHOR_FIELD_NUMBER: _ClassVar[int]
    MODEL_TYPE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    model_name: str
    model_version: str
    model_author: str
    model_type: str
    source: str
    def __init__(self, model_name: _Optional[str] = ..., model_version: _Optional[str] = ..., model_author: _Optional[str] = ..., model_type: _Optional[str] = ..., source: _Optional[str] = ...) -> None: ...

class ModelDescription(_message.Message):
    __slots__ = ("summary", "details", "technical", "performance")
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    TECHNICAL_FIELD_NUMBER: _ClassVar[int]
    PERFORMANCE_FIELD_NUMBER: _ClassVar[int]
    summary: str
    details: str
    technical: str
    performance: str
    def __init__(self, summary: _Optional[str] = ..., details: _Optional[str] = ..., technical: _Optional[str] = ..., performance: _Optional[str] = ...) -> None: ...

class ModelInput(_message.Message):
    __slots__ = ("filename", "accepted_media_types", "max_size", "description")
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    ACCEPTED_MEDIA_TYPES_FIELD_NUMBER: _ClassVar[int]
    MAX_SIZE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    filename: str
    accepted_media_types: _containers.RepeatedScalarFieldContainer[str]
    max_size: str
    description: str
    def __init__(self, filename: _Optional[str] = ..., accepted_media_types: _Optional[_Iterable[str]] = ..., max_size: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class ModelOutput(_message.Message):
    __slots__ = ("filename", "media_type", "max_size", "description")
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    MEDIA_TYPE_FIELD_NUMBER: _ClassVar[int]
    MAX_SIZE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    filename: str
    media_type: str
    max_size: str
    description: str
    def __init__(self, filename: _Optional[str] = ..., media_type: _Optional[str] = ..., max_size: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class ModelResources(_message.Message):
    __slots__ = ("required_ram", "num_cpus", "num_gpus")
    REQUIRED_RAM_FIELD_NUMBER: _ClassVar[int]
    NUM_CPUS_FIELD_NUMBER: _ClassVar[int]
    NUM_GPUS_FIELD_NUMBER: _ClassVar[int]
    required_ram: str
    num_cpus: float
    num_gpus: int
    def __init__(self, required_ram: _Optional[str] = ..., num_cpus: _Optional[float] = ..., num_gpus: _Optional[int] = ...) -> None: ...

class ModelTimeout(_message.Message):
    __slots__ = ("status", "run")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RUN_FIELD_NUMBER: _ClassVar[int]
    status: str
    run: str
    def __init__(self, status: _Optional[str] = ..., run: _Optional[str] = ...) -> None: ...

class ModelFeatures(_message.Message):
    __slots__ = ("adversarial_defense", "batch_size", "retrainable", "results_format", "drift_format", "explanation_format")
    ADVERSARIAL_DEFENSE_FIELD_NUMBER: _ClassVar[int]
    BATCH_SIZE_FIELD_NUMBER: _ClassVar[int]
    RETRAINABLE_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FORMAT_FIELD_NUMBER: _ClassVar[int]
    DRIFT_FORMAT_FIELD_NUMBER: _ClassVar[int]
    EXPLANATION_FORMAT_FIELD_NUMBER: _ClassVar[int]
    adversarial_defense: bool
    batch_size: int
    retrainable: bool
    results_format: str
    drift_format: str
    explanation_format: str
    def __init__(self, adversarial_defense: bool = ..., batch_size: _Optional[int] = ..., retrainable: bool = ..., results_format: _Optional[str] = ..., drift_format: _Optional[str] = ..., explanation_format: _Optional[str] = ...) -> None: ...

class StatusResponse(_message.Message):
    __slots__ = ("status_code", "status", "message", "model_info", "description", "inputs", "outputs", "resources", "timeout", "features")
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    MODEL_INFO_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    status: str
    message: str
    model_info: ModelInfo
    description: ModelDescription
    inputs: _containers.RepeatedCompositeFieldContainer[ModelInput]
    outputs: _containers.RepeatedCompositeFieldContainer[ModelOutput]
    resources: ModelResources
    timeout: ModelTimeout
    features: ModelFeatures
    def __init__(self, status_code: _Optional[int] = ..., status: _Optional[str] = ..., message: _Optional[str] = ..., model_info: _Optional[_Union[ModelInfo, _Mapping]] = ..., description: _Optional[_Union[ModelDescription, _Mapping]] = ..., inputs: _Optional[_Iterable[_Union[ModelInput, _Mapping]]] = ..., outputs: _Optional[_Iterable[_Union[ModelOutput, _Mapping]]] = ..., resources: _Optional[_Union[ModelResources, _Mapping]] = ..., timeout: _Optional[_Union[ModelTimeout, _Mapping]] = ..., features: _Optional[_Union[ModelFeatures, _Mapping]] = ...) -> None: ...

class InputItem(_message.Message):
    __slots__ = ("input",)
    class InputEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(self, key: _Optional[str] = ..., value: _Optional[bytes] = ...) -> None: ...
    INPUT_FIELD_NUMBER: _ClassVar[int]
    input: _containers.ScalarMap[str, bytes]
    def __init__(self, input: _Optional[_Mapping[str, bytes]] = ...) -> None: ...

class RunRequest(_message.Message):
    __slots__ = ("inputs", "detect_drift", "explain")
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    DETECT_DRIFT_FIELD_NUMBER: _ClassVar[int]
    EXPLAIN_FIELD_NUMBER: _ClassVar[int]
    inputs: _containers.RepeatedCompositeFieldContainer[InputItem]
    detect_drift: bool
    explain: bool
    def __init__(self, inputs: _Optional[_Iterable[_Union[InputItem, _Mapping]]] = ..., detect_drift: bool = ..., explain: bool = ...) -> None: ...

class OutputItem(_message.Message):
    __slots__ = ("output", "success")
    class OutputEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(self, key: _Optional[str] = ..., value: _Optional[bytes] = ...) -> None: ...
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    output: _containers.ScalarMap[str, bytes]
    success: bool
    def __init__(self, output: _Optional[_Mapping[str, bytes]] = ..., success: bool = ...) -> None: ...

class RunResponse(_message.Message):
    __slots__ = ("status_code", "status", "message", "outputs")
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    status: str
    message: str
    outputs: _containers.RepeatedCompositeFieldContainer[OutputItem]
    def __init__(self, status_code: _Optional[int] = ..., status: _Optional[str] = ..., message: _Optional[str] = ..., outputs: _Optional[_Iterable[_Union[OutputItem, _Mapping]]] = ...) -> None: ...

class ShutdownRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ShutdownResponse(_message.Message):
    __slots__ = ("status_code", "status", "message")
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    status: str
    message: str
    def __init__(self, status_code: _Optional[int] = ..., status: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...
