from typing import Any, Callable, Union

LegacyNormalPredictFunction = Callable[[bytes], Any]
LegacyBatchPredictFunction = Callable[[list[bytes]], list[Any]]

NormalPredictFunction = Callable[[dict[str, bytes]], dict[str, Any]]
BatchPredictFunction = Callable[[list[dict[str, bytes]]], list[dict[str, Any]]]

LegacyPredictFunction = Union[LegacyNormalPredictFunction, LegacyBatchPredictFunction]
PredictFunction = Union[LegacyPredictFunction, NormalPredictFunction, BatchPredictFunction]
