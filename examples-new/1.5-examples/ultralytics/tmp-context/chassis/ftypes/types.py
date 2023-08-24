from __future__ import annotations

from typing import Any, Callable, Mapping, Sequence, Union

LegacyNormalPredictFunction = Callable[[bytes], Any]
LegacyBatchPredictFunction = Callable[[Sequence[bytes]], Sequence[Any]]

NormalPredictFunction = Callable[[Mapping[str, bytes]], Mapping[str, bytes]]
BatchPredictFunction = Callable[[Sequence[Mapping[str, bytes]]], Sequence[Mapping[str, bytes]]]

LegacyPredictFunction = Union[LegacyNormalPredictFunction, LegacyBatchPredictFunction]
PredictFunction = Union[LegacyPredictFunction, NormalPredictFunction, BatchPredictFunction]
