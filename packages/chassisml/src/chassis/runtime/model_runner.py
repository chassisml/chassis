from typing import Any, Dict, List

from chassis.typing import PredictFunction


class ModelRunner:

    def __init__(self, predict_fn: PredictFunction, batch_size: int = 1):
        self.predict_fn = predict_fn
        self.supports_batch = batch_size > 1
        self.batch_size = batch_size

    def predict(self, inputs: List[Dict[str, bytes]]) -> List[Dict[str, Any]]:
        if self.supports_batch:
            return self._predict_batch(inputs)
        else:
            return self._predict_single(inputs)

    def _predict_single(self, inputs: List[Dict[str, bytes]]) -> List[Dict[str, Any]]:
        outputs = []
        for input_item in inputs:
            try:
                output = self.predict_fn(input_item)
            except Exception as e:
                # TODO - is there more information we can include here like a backtrace?
                output = {"error": e}
            outputs.append(output)
        return outputs

    def _predict_batch(self, inputs: List[Dict[str, bytes]]) -> List[Dict[str, Any]]:
        # TODO - split inputs into groups of self.batch_size
        return self.predict_fn(inputs)
