from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ModelDrift(_message.Message):
    __slots__ = ("data_drift",)
    DATA_DRIFT_FIELD_NUMBER: _ClassVar[int]
    data_drift: DataDrift
    def __init__(self, data_drift: _Optional[_Union[DataDrift, _Mapping]] = ...) -> None: ...

class DataDrift(_message.Message):
    __slots__ = ("score",)
    SCORE_FIELD_NUMBER: _ClassVar[int]
    score: float
    def __init__(self, score: _Optional[float] = ...) -> None: ...
