from __future__ import annotations

import dataclasses
from typing import Any, Callable, Mapping, Optional, Sequence, Union

LegacyNormalPredictFunction = Callable[[bytes], Any]
LegacyBatchPredictFunction = Callable[[Sequence[bytes]], Sequence[Any]]

NormalPredictFunction = Callable[[Mapping[str, bytes]], Mapping[str, bytes]]
BatchPredictFunction = Callable[[Sequence[Mapping[str, bytes]]], Sequence[Mapping[str, bytes]]]

LegacyPredictFunction = Union[LegacyNormalPredictFunction, LegacyBatchPredictFunction]
PredictFunction = Union[LegacyPredictFunction, NormalPredictFunction, BatchPredictFunction]


@dataclasses.dataclass
class DataDrift:
    score: float


@dataclasses.dataclass
class ModelDrift:
    data_drift: Optional[DataDrift] = None


@dataclasses.dataclass
class DataOutput:
    data: bytes
    content_type: Optional[str] = None


@dataclasses.dataclass
class PredictionOutput:
    key: str
    text: Optional[str] = None
    data: Optional[DataOutput] = None


@dataclasses.dataclass
class PredictionResult:
    outputs: list[PredictionOutput]
    success: bool = True
    error: Optional[str] = None
    drift: Optional[ModelDrift] = None


V2PredictFunction = Callable[[Mapping[str, bytes]], PredictionResult]
