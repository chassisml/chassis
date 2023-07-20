from typing import Callable, List, Mapping, Union

LegacyNormalPredictFunction = Callable[[bytes], bytes]
LegacyBatchPredictFunction = Callable[[List[bytes]], List[bytes]]

NormalPredictFunction = Callable[[Mapping[str, bytes]], Mapping[str, bytes]]
BatchPredictFunction = Callable[[List[Mapping[str, bytes]]], List[Mapping[str, bytes]]]

LegacyPredictFunction = Union[LegacyNormalPredictFunction, LegacyBatchPredictFunction]
PredictFunction = Union[LegacyPredictFunction, NormalPredictFunction, BatchPredictFunction]
