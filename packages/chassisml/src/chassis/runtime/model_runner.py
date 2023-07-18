from typing import Dict, List


class ModelRunner:

    def __init__(self, predict_fn, supports_batch: bool = False, batch_size: int = 1):
        self.predict_fn = predict_fn
        self.supports_batch = supports_batch
        self.batch_size = batch_size

    def predict(self, inputs: List[Dict[str, bytes]]) -> List[Dict[str, bytes]]:
        if self.supports_batch:
            return self._predict_batch(inputs)
        else:
            return self._predict_single(inputs)

    def _predict_single(self, inputs: List[Dict[str, bytes]]) -> List[Dict[str, bytes]]:
        outputs = []
        for input_item in inputs:
            try:
                output = self.predict_fn(input_item)
            except Exception as e:
                # TODO - is there more information we can include here like a backtrace?
                output = {"error": e}
            outputs.append(output)
        return outputs

    def _predict_batch(self, inputs: List[Dict[str, bytes]]) -> List[Dict[str, bytes]]:
        # TODO - split inputs into groups of self.batch_size
        return self.predict_fn(inputs)
