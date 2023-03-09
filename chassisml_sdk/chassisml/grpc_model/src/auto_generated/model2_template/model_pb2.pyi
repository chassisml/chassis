from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class InputItem(_message.Message):
    __slots__ = ["input"]
    class InputEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(self, key: _Optional[str] = ..., value: _Optional[bytes] = ...) -> None: ...
    INPUT_FIELD_NUMBER: _ClassVar[int]
    input: _containers.ScalarMap[str, bytes]
    def __init__(self, input: _Optional[_Mapping[str, bytes]] = ...) -> None: ...

class ModelDescription(_message.Message):
    __slots__ = ["details", "performance", "summary", "technical"]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    PERFORMANCE_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    TECHNICAL_FIELD_NUMBER: _ClassVar[int]
    details: str
    performance: str
    summary: str
    technical: str
    def __init__(self, summary: _Optional[str] = ..., details: _Optional[str] = ..., technical: _Optional[str] = ..., performance: _Optional[str] = ...) -> None: ...

class ModelFeatures(_message.Message):
    __slots__ = ["adversarial_defense", "batch_size", "drift_format", "explanation_format", "results_format", "retrainable"]
    ADVERSARIAL_DEFENSE_FIELD_NUMBER: _ClassVar[int]
    BATCH_SIZE_FIELD_NUMBER: _ClassVar[int]
    DRIFT_FORMAT_FIELD_NUMBER: _ClassVar[int]
    EXPLANATION_FORMAT_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FORMAT_FIELD_NUMBER: _ClassVar[int]
    RETRAINABLE_FIELD_NUMBER: _ClassVar[int]
    adversarial_defense: bool
    batch_size: int
    drift_format: str
    explanation_format: str
    results_format: str
    retrainable: bool
    def __init__(self, adversarial_defense: bool = ..., batch_size: _Optional[int] = ..., retrainable: bool = ..., results_format: _Optional[str] = ..., drift_format: _Optional[str] = ..., explanation_format: _Optional[str] = ...) -> None: ...

class ModelInfo(_message.Message):
    __slots__ = ["model_author", "model_name", "model_type", "model_version", "source"]
    MODEL_AUTHOR_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    MODEL_TYPE_FIELD_NUMBER: _ClassVar[int]
    MODEL_VERSION_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    model_author: str
    model_name: str
    model_type: str
    model_version: str
    source: str
    def __init__(self, model_name: _Optional[str] = ..., model_version: _Optional[str] = ..., model_author: _Optional[str] = ..., model_type: _Optional[str] = ..., source: _Optional[str] = ...) -> None: ...

class ModelInput(_message.Message):
    __slots__ = ["accepted_media_types", "description", "filename", "max_size"]
    ACCEPTED_MEDIA_TYPES_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    MAX_SIZE_FIELD_NUMBER: _ClassVar[int]
    accepted_media_types: _containers.RepeatedScalarFieldContainer[str]
    description: str
    filename: str
    max_size: str
    def __init__(self, filename: _Optional[str] = ..., accepted_media_types: _Optional[_Iterable[str]] = ..., max_size: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class ModelOutput(_message.Message):
    __slots__ = ["description", "filename", "max_size", "media_type"]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    MAX_SIZE_FIELD_NUMBER: _ClassVar[int]
    MEDIA_TYPE_FIELD_NUMBER: _ClassVar[int]
    description: str
    filename: str
    max_size: str
    media_type: str
    def __init__(self, filename: _Optional[str] = ..., media_type: _Optional[str] = ..., max_size: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class ModelResources(_message.Message):
    __slots__ = ["num_cpus", "num_gpus", "required_ram"]
    NUM_CPUS_FIELD_NUMBER: _ClassVar[int]
    NUM_GPUS_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_RAM_FIELD_NUMBER: _ClassVar[int]
    num_cpus: float
    num_gpus: int
    required_ram: str
    def __init__(self, required_ram: _Optional[str] = ..., num_cpus: _Optional[float] = ..., num_gpus: _Optional[int] = ...) -> None: ...

class ModelTimeout(_message.Message):
    __slots__ = ["run", "status"]
    RUN_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    run: str
    status: str
    def __init__(self, status: _Optional[str] = ..., run: _Optional[str] = ...) -> None: ...

class OutputItem(_message.Message):
    __slots__ = ["output", "success"]
    class OutputEntry(_message.Message):
        __slots__ = ["key", "value"]
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

class RunRequest(_message.Message):
    __slots__ = ["detect_drift", "explain", "inputs"]
    DETECT_DRIFT_FIELD_NUMBER: _ClassVar[int]
    EXPLAIN_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    detect_drift: bool
    explain: bool
    inputs: _containers.RepeatedCompositeFieldContainer[InputItem]
    def __init__(self, inputs: _Optional[_Iterable[_Union[InputItem, _Mapping]]] = ..., detect_drift: bool = ..., explain: bool = ...) -> None: ...

class RunResponse(_message.Message):
    __slots__ = ["message", "outputs", "status", "status_code"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    message: str
    outputs: _containers.RepeatedCompositeFieldContainer[OutputItem]
    status: str
    status_code: int
    def __init__(self, status_code: _Optional[int] = ..., status: _Optional[str] = ..., message: _Optional[str] = ..., outputs: _Optional[_Iterable[_Union[OutputItem, _Mapping]]] = ...) -> None: ...

class ShutdownRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class ShutdownResponse(_message.Message):
    __slots__ = ["message", "status", "status_code"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    message: str
    status: str
    status_code: int
    def __init__(self, status_code: _Optional[int] = ..., status: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class StatusRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class StatusResponse(_message.Message):
    __slots__ = ["description", "features", "inputs", "message", "model_info", "outputs", "resources", "status", "status_code", "timeout"]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    MODEL_INFO_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    description: ModelDescription
    features: ModelFeatures
    inputs: _containers.RepeatedCompositeFieldContainer[ModelInput]
    message: str
    model_info: ModelInfo
    outputs: _containers.RepeatedCompositeFieldContainer[ModelOutput]
    resources: ModelResources
    status: str
    status_code: int
    timeout: ModelTimeout
    def __init__(self, status_code: _Optional[int] = ..., status: _Optional[str] = ..., message: _Optional[str] = ..., model_info: _Optional[_Union[ModelInfo, _Mapping]] = ..., description: _Optional[_Union[ModelDescription, _Mapping]] = ..., inputs: _Optional[_Iterable[_Union[ModelInput, _Mapping]]] = ..., outputs: _Optional[_Iterable[_Union[ModelOutput, _Mapping]]] = ..., resources: _Optional[_Union[ModelResources, _Mapping]] = ..., timeout: _Optional[_Union[ModelTimeout, _Mapping]] = ..., features: _Optional[_Union[ModelFeatures, _Mapping]] = ...) -> None: ...
