from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Point(_message.Message):
    __slots__ = ("x", "y")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    x: int
    y: int
    def __init__(self, x: _Optional[int] = ..., y: _Optional[int] = ...) -> None: ...

class BoundingBox(_message.Message):
    __slots__ = ("x", "y", "width", "height")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    x: int
    y: int
    width: int
    height: int
    def __init__(self, x: _Optional[int] = ..., y: _Optional[int] = ..., width: _Optional[int] = ..., height: _Optional[int] = ...) -> None: ...

class ImageMask(_message.Message):
    __slots__ = ("original_width", "original_height", "rle", "image", "points")
    ORIGINAL_WIDTH_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    RLE_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    original_width: int
    original_height: int
    rle: _containers.RepeatedScalarFieldContainer[int]
    image: _containers.RepeatedScalarFieldContainer[bytes]
    points: _containers.RepeatedCompositeFieldContainer[Point]
    def __init__(self, original_width: _Optional[int] = ..., original_height: _Optional[int] = ..., rle: _Optional[_Iterable[int]] = ..., image: _Optional[_Iterable[bytes]] = ..., points: _Optional[_Iterable[_Union[Point, _Mapping]]] = ...) -> None: ...

class TextSpan(_message.Message):
    __slots__ = ("start", "end", "text")
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    start: int
    end: int
    text: str
    def __init__(self, start: _Optional[int] = ..., end: _Optional[int] = ..., text: _Optional[str] = ...) -> None: ...

class Tensor(_message.Message):
    __slots__ = ("shape", "data_type", "bool_data", "int32_data", "int64_data", "uint32_data", "uint64_data", "float32_data", "float64_data", "raw_data")
    class DataType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_TENSOR_DATA_TYPE: _ClassVar[Tensor.DataType]
        BOOL: _ClassVar[Tensor.DataType]
        INT32: _ClassVar[Tensor.DataType]
        INT64: _ClassVar[Tensor.DataType]
        UINT32: _ClassVar[Tensor.DataType]
        UINT64: _ClassVar[Tensor.DataType]
        FLOAT32: _ClassVar[Tensor.DataType]
        FLOAT64: _ClassVar[Tensor.DataType]
    UNKNOWN_TENSOR_DATA_TYPE: Tensor.DataType
    BOOL: Tensor.DataType
    INT32: Tensor.DataType
    INT64: Tensor.DataType
    UINT32: Tensor.DataType
    UINT64: Tensor.DataType
    FLOAT32: Tensor.DataType
    FLOAT64: Tensor.DataType
    SHAPE_FIELD_NUMBER: _ClassVar[int]
    DATA_TYPE_FIELD_NUMBER: _ClassVar[int]
    BOOL_DATA_FIELD_NUMBER: _ClassVar[int]
    INT32_DATA_FIELD_NUMBER: _ClassVar[int]
    INT64_DATA_FIELD_NUMBER: _ClassVar[int]
    UINT32_DATA_FIELD_NUMBER: _ClassVar[int]
    UINT64_DATA_FIELD_NUMBER: _ClassVar[int]
    FLOAT32_DATA_FIELD_NUMBER: _ClassVar[int]
    FLOAT64_DATA_FIELD_NUMBER: _ClassVar[int]
    RAW_DATA_FIELD_NUMBER: _ClassVar[int]
    shape: _containers.RepeatedScalarFieldContainer[int]
    data_type: Tensor.DataType
    bool_data: _containers.RepeatedScalarFieldContainer[bool]
    int32_data: _containers.RepeatedScalarFieldContainer[int]
    int64_data: _containers.RepeatedScalarFieldContainer[int]
    uint32_data: _containers.RepeatedScalarFieldContainer[int]
    uint64_data: _containers.RepeatedScalarFieldContainer[int]
    float32_data: _containers.RepeatedScalarFieldContainer[float]
    float64_data: _containers.RepeatedScalarFieldContainer[float]
    raw_data: _containers.RepeatedScalarFieldContainer[bytes]
    def __init__(self, shape: _Optional[_Iterable[int]] = ..., data_type: _Optional[_Union[Tensor.DataType, str]] = ..., bool_data: _Optional[_Iterable[bool]] = ..., int32_data: _Optional[_Iterable[int]] = ..., int64_data: _Optional[_Iterable[int]] = ..., uint32_data: _Optional[_Iterable[int]] = ..., uint64_data: _Optional[_Iterable[int]] = ..., float32_data: _Optional[_Iterable[float]] = ..., float64_data: _Optional[_Iterable[float]] = ..., raw_data: _Optional[_Iterable[bytes]] = ...) -> None: ...
