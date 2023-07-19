from typing import Any, List, Mapping

from chassis.typing import PredictFunction


class ModelRunner:

    def __init__(self, predict_fn: PredictFunction, batch_size: int = 1, is_legacy_fn=False):
        self.predict_fn = predict_fn
        self.supports_batch = batch_size > 1
        self.batch_size = batch_size
        self.legacy = is_legacy_fn

    def predict(self, inputs: List[Mapping[str, bytes]]) -> List[Mapping[str, Any]]:
        if self.legacy:
            return self._predict_legacy(inputs)
        if self.supports_batch:
            return self._predict_batch(inputs)
        else:
            return self._predict_single(inputs)

    def _predict_single(self, inputs: List[Mapping[str, bytes]]) -> List[Mapping[str, Any]]:
        outputs = []
        for input_item in inputs:
            try:
                output = self.predict_fn(input_item)
            except Exception as e:
                # TODO - is there more information we can include here like a backtrace?
                output = {"error": e}
            outputs.append(output)
        return outputs

    def _predict_batch(self, inputs: List[Mapping[str, bytes]]) -> List[Mapping[str, Any]]:
        # TODO - split inputs into groups of self.batch_size
        return self.predict_fn(inputs)

    def _predict_legacy(self, inputs: List[Mapping[str, bytes]]) -> List[Mapping[str, Any]]:
        if self.batch_size == 1:
            outputs = []
            for input_item in inputs:
                output = self.predict_fn(input_item["input"])
                outputs.append({"results.json": output})
            return outputs
        else:
            adjusted_inputs = [input_item["input"] for input_item in inputs]
            # TODO - split inputs into groups of self.batch_size
            outputs = self.predict_fn(adjusted_inputs)
            adjusted_outputs = [{"results.json": o} for o in outputs]
            return adjusted_outputs
