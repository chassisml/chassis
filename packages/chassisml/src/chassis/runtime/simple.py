from typing import Mapping

from chassis.ftypes import V2PredictFunction, PredictionResult
from .base import ModelBase


class SimpleFunctionModel(ModelBase):
    def __init__(self, predict: V2PredictFunction):
        self._predict_fn = predict

    def predict(self, inputs: Mapping[str, bytes]) -> PredictionResult:
        return self._predict_fn(inputs)
