from google.protobuf import duration_pb2 as _duration_pb2
from openmodel.v2 import container_pb2 as _container_pb2
from openmodel.v2 import results_pb2 as _results_pb2
from openmodel.v2 import explanations_pb2 as _explanations_pb2
from openmodel.v2 import drift_pb2 as _drift_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StatusRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StatusResponse(_message.Message):
    __slots__ = ("status",)
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_STATUS: _ClassVar[StatusResponse.Status]
        OK: _ClassVar[StatusResponse.Status]
    UNKNOWN_STATUS: StatusResponse.Status
    OK: StatusResponse.Status
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: StatusResponse.Status
    def __init__(self, status: _Optional[_Union[StatusResponse.Status, str]] = ...) -> None: ...

class ContainerInfoRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PredictRequest(_message.Message):
    __slots__ = ("inputs", "tags")
    class Input(_message.Message):
        __slots__ = ("key", "text", "data")
        KEY_FIELD_NUMBER: _ClassVar[int]
        TEXT_FIELD_NUMBER: _ClassVar[int]
        DATA_FIELD_NUMBER: _ClassVar[int]
        key: str
        text: str
        data: bytes
        def __init__(self, key: _Optional[str] = ..., text: _Optional[str] = ..., data: _Optional[bytes] = ...) -> None: ...
    class TagsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    inputs: _containers.RepeatedCompositeFieldContainer[PredictRequest.Input]
    tags: _containers.ScalarMap[str, str]
    def __init__(self, inputs: _Optional[_Iterable[_Union[PredictRequest.Input, _Mapping]]] = ..., tags: _Optional[_Mapping[str, str]] = ...) -> None: ...

class PredictResponse(_message.Message):
    __slots__ = ("outputs", "explanation", "drift", "success", "error", "timings", "tags")
    class Timings(_message.Message):
        __slots__ = ("model_execution", "preprocessing", "postprocessing", "formatting", "total")
        MODEL_EXECUTION_FIELD_NUMBER: _ClassVar[int]
        PREPROCESSING_FIELD_NUMBER: _ClassVar[int]
        POSTPROCESSING_FIELD_NUMBER: _ClassVar[int]
        FORMATTING_FIELD_NUMBER: _ClassVar[int]
        TOTAL_FIELD_NUMBER: _ClassVar[int]
        model_execution: _duration_pb2.Duration
        preprocessing: _duration_pb2.Duration
        postprocessing: _duration_pb2.Duration
        formatting: _duration_pb2.Duration
        total: _duration_pb2.Duration
        def __init__(self, model_execution: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., preprocessing: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., postprocessing: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., formatting: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., total: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...
    class TagsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    EXPLANATION_FIELD_NUMBER: _ClassVar[int]
    DRIFT_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    TIMINGS_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    outputs: _containers.RepeatedCompositeFieldContainer[_results_pb2.PredictionOutput]
    explanation: _explanations_pb2.Explanation
    drift: _drift_pb2.ModelDrift
    success: bool
    error: str
    timings: PredictResponse.Timings
    tags: _containers.ScalarMap[str, str]
    def __init__(self, outputs: _Optional[_Iterable[_Union[_results_pb2.PredictionOutput, _Mapping]]] = ..., explanation: _Optional[_Union[_explanations_pb2.Explanation, _Mapping]] = ..., drift: _Optional[_Union[_drift_pb2.ModelDrift, _Mapping]] = ..., success: bool = ..., error: _Optional[str] = ..., timings: _Optional[_Union[PredictResponse.Timings, _Mapping]] = ..., tags: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ShutdownRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ShutdownResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
