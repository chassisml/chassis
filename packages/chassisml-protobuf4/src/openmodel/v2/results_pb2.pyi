from google.api import field_behavior_pb2 as _field_behavior_pb2
from openmodel.v2 import types_pb2 as _types_pb2
from openmodel.v2 import explanations_pb2 as _explanations_pb2
from openmodel.v2 import drift_pb2 as _drift_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PredictionOutput(_message.Message):
    __slots__ = ("key", "classification", "multi_classification", "object_detection", "segmentation", "named_entity", "text", "image", "data")
    KEY_FIELD_NUMBER: _ClassVar[int]
    CLASSIFICATION_FIELD_NUMBER: _ClassVar[int]
    MULTI_CLASSIFICATION_FIELD_NUMBER: _ClassVar[int]
    OBJECT_DETECTION_FIELD_NUMBER: _ClassVar[int]
    SEGMENTATION_FIELD_NUMBER: _ClassVar[int]
    NAMED_ENTITY_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    key: str
    classification: ClassificationResult
    multi_classification: MultiClassificationResult
    object_detection: ObjectDetectionResult
    segmentation: SegmentationResult
    named_entity: NamedEntityResult
    text: TextResult
    image: ImageResult
    data: DataResult
    def __init__(self, key: _Optional[str] = ..., classification: _Optional[_Union[ClassificationResult, _Mapping]] = ..., multi_classification: _Optional[_Union[MultiClassificationResult, _Mapping]] = ..., object_detection: _Optional[_Union[ObjectDetectionResult, _Mapping]] = ..., segmentation: _Optional[_Union[SegmentationResult, _Mapping]] = ..., named_entity: _Optional[_Union[NamedEntityResult, _Mapping]] = ..., text: _Optional[_Union[TextResult, _Mapping]] = ..., image: _Optional[_Union[ImageResult, _Mapping]] = ..., data: _Optional[_Union[DataResult, _Mapping]] = ...) -> None: ...

class ClassificationResult(_message.Message):
    __slots__ = ("class_predictions",)
    class Prediction(_message.Message):
        __slots__ = ("score",)
        CLASS_FIELD_NUMBER: _ClassVar[int]
        SCORE_FIELD_NUMBER: _ClassVar[int]
        score: float
        def __init__(self, score: _Optional[float] = ..., **kwargs) -> None: ...
    CLASS_PREDICTIONS_FIELD_NUMBER: _ClassVar[int]
    class_predictions: _containers.RepeatedCompositeFieldContainer[ClassificationResult.Prediction]
    def __init__(self, class_predictions: _Optional[_Iterable[_Union[ClassificationResult.Prediction, _Mapping]]] = ...) -> None: ...

class MultiClassificationResult(_message.Message):
    __slots__ = ("classifications",)
    CLASSIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    classifications: _containers.RepeatedCompositeFieldContainer[ClassificationResult]
    def __init__(self, classifications: _Optional[_Iterable[_Union[ClassificationResult, _Mapping]]] = ...) -> None: ...

class ObjectDetectionResult(_message.Message):
    __slots__ = ("detections",)
    class Detection(_message.Message):
        __slots__ = ("score", "bounding_box")
        CLASS_FIELD_NUMBER: _ClassVar[int]
        SCORE_FIELD_NUMBER: _ClassVar[int]
        BOUNDING_BOX_FIELD_NUMBER: _ClassVar[int]
        score: float
        bounding_box: _types_pb2.BoundingBox
        def __init__(self, score: _Optional[float] = ..., bounding_box: _Optional[_Union[_types_pb2.BoundingBox, _Mapping]] = ..., **kwargs) -> None: ...
    DETECTIONS_FIELD_NUMBER: _ClassVar[int]
    detections: _containers.RepeatedCompositeFieldContainer[ObjectDetectionResult.Detection]
    def __init__(self, detections: _Optional[_Iterable[_Union[ObjectDetectionResult.Detection, _Mapping]]] = ...) -> None: ...

class SegmentationResult(_message.Message):
    __slots__ = ("segments",)
    class Segment(_message.Message):
        __slots__ = ("score", "image_mask", "bounding_box")
        CLASS_FIELD_NUMBER: _ClassVar[int]
        SCORE_FIELD_NUMBER: _ClassVar[int]
        IMAGE_MASK_FIELD_NUMBER: _ClassVar[int]
        BOUNDING_BOX_FIELD_NUMBER: _ClassVar[int]
        score: float
        image_mask: _types_pb2.ImageMask
        bounding_box: _types_pb2.BoundingBox
        def __init__(self, score: _Optional[float] = ..., image_mask: _Optional[_Union[_types_pb2.ImageMask, _Mapping]] = ..., bounding_box: _Optional[_Union[_types_pb2.BoundingBox, _Mapping]] = ..., **kwargs) -> None: ...
    SEGMENTS_FIELD_NUMBER: _ClassVar[int]
    segments: _containers.RepeatedCompositeFieldContainer[SegmentationResult.Segment]
    def __init__(self, segments: _Optional[_Iterable[_Union[SegmentationResult.Segment, _Mapping]]] = ...) -> None: ...

class NamedEntityResult(_message.Message):
    __slots__ = ("entities",)
    class NamedEntity(_message.Message):
        __slots__ = ("entity_group", "score", "text_span")
        ENTITY_GROUP_FIELD_NUMBER: _ClassVar[int]
        SCORE_FIELD_NUMBER: _ClassVar[int]
        TEXT_SPAN_FIELD_NUMBER: _ClassVar[int]
        entity_group: str
        score: float
        text_span: _types_pb2.TextSpan
        def __init__(self, entity_group: _Optional[str] = ..., score: _Optional[float] = ..., text_span: _Optional[_Union[_types_pb2.TextSpan, _Mapping]] = ...) -> None: ...
    ENTITIES_FIELD_NUMBER: _ClassVar[int]
    entities: _containers.RepeatedCompositeFieldContainer[NamedEntityResult.NamedEntity]
    def __init__(self, entities: _Optional[_Iterable[_Union[NamedEntityResult.NamedEntity, _Mapping]]] = ...) -> None: ...

class TextResult(_message.Message):
    __slots__ = ("text",)
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class ImageResult(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    def __init__(self, data: _Optional[bytes] = ...) -> None: ...

class DataResult(_message.Message):
    __slots__ = ("data", "content_type")
    DATA_FIELD_NUMBER: _ClassVar[int]
    CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    content_type: str
    def __init__(self, data: _Optional[bytes] = ..., content_type: _Optional[str] = ...) -> None: ...
