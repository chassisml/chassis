from openmodel.v2 import types_pb2 as _types_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Explanation(_message.Message):
    __slots__ = ("none", "image", "text")
    NONE_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    none: NoExplanation
    image: ImageExplanation
    text: TextExplanation
    def __init__(self, none: _Optional[_Union[NoExplanation, _Mapping]] = ..., image: _Optional[_Union[ImageExplanation, _Mapping]] = ..., text: _Optional[_Union[TextExplanation, _Mapping]] = ...) -> None: ...

class NoExplanation(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ImageExplanation(_message.Message):
    __slots__ = ("mask",)
    MASK_FIELD_NUMBER: _ClassVar[int]
    mask: _types_pb2.ImageMask
    def __init__(self, mask: _Optional[_Union[_types_pb2.ImageMask, _Mapping]] = ...) -> None: ...

class TextExplanation(_message.Message):
    __slots__ = ("class_results",)
    class TextSpanScore(_message.Message):
        __slots__ = ("text_span", "score")
        TEXT_SPAN_FIELD_NUMBER: _ClassVar[int]
        SCORE_FIELD_NUMBER: _ClassVar[int]
        text_span: _types_pb2.TextSpan
        score: float
        def __init__(self, text_span: _Optional[_Union[_types_pb2.TextSpan, _Mapping]] = ..., score: _Optional[float] = ...) -> None: ...
    class ClassResults(_message.Message):
        __slots__ = ("scores",)
        CLASS_FIELD_NUMBER: _ClassVar[int]
        SCORES_FIELD_NUMBER: _ClassVar[int]
        scores: _containers.RepeatedCompositeFieldContainer[TextExplanation.TextSpanScore]
        def __init__(self, scores: _Optional[_Iterable[_Union[TextExplanation.TextSpanScore, _Mapping]]] = ..., **kwargs) -> None: ...
    CLASS_RESULTS_FIELD_NUMBER: _ClassVar[int]
    class_results: _containers.RepeatedCompositeFieldContainer[TextExplanation.ClassResults]
    def __init__(self, class_results: _Optional[_Iterable[_Union[TextExplanation.ClassResults, _Mapping]]] = ...) -> None: ...
