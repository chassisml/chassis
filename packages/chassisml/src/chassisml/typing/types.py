from typing import Callable, Union

ClassicPredictFunction = Callable[[bytes], dict[str, bytes]]

SingleInputPredictFunction = Callable[[dict[str, bytes]], dict[str, bytes]]
BatchPredictFunction = Callable[[list[dict[str, bytes]]], list[dict[str, bytes]]]

PredictFunction = Union[ClassicPredictFunction, SingleInputPredictFunction, BatchPredictFunction]
