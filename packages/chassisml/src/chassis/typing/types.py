from typing import Any, Callable, Union

ClassicPredictFunction = Callable[[bytes], dict[str, bytes]]

NormalPredictFunction = Callable[[dict[str, bytes]], dict[str, Any]]
BatchPredictFunction = Callable[[list[dict[str, bytes]]], list[dict[str, Any]]]

PredictFunction = Union[NormalPredictFunction, BatchPredictFunction]
