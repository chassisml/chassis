from typing import Any, Callable, List, Mapping, Union

LegacyNormalPredictFunction = Callable[[bytes], Any]
LegacyBatchPredictFunction = Callable[[List[bytes]], List[Any]]

NormalPredictFunction = Callable[[Mapping[str, bytes]], Mapping[str, bytes]]
BatchPredictFunction = Callable[[List[Mapping[str, bytes]]], List[Mapping[str, bytes]]]

LegacyPredictFunction = Union[LegacyNormalPredictFunction, LegacyBatchPredictFunction]
PredictFunction = Union[LegacyPredictFunction, NormalPredictFunction, BatchPredictFunction]
