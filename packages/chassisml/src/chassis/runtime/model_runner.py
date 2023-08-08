import os
import json
import cloudpickle
from typing import List, Mapping, Type, TypeVar, Union

from chassis.typing import PredictFunction
from .numpy_encoder import NumpyEncoder
from .constants import PACKAGE_DATA_PATH, PYTHON_MODEL_KEY, python_pickle_filename_for_key

T = TypeVar("T", bound="ModelRunner")


def batch(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


class ModelRunner:

    @classmethod
    def load(cls: Type[T]) -> Union[T, None]:
        try:
            # If this is the first time calling the `Status` route, then attempt to load the model
            filename = python_pickle_filename_for_key(PYTHON_MODEL_KEY)
            with open(os.path.join(PACKAGE_DATA_PATH, filename), "rb") as f:
                modules = cloudpickle.load(f)
            model: T = modules[PYTHON_MODEL_KEY]
            if model is None:
                raise "Model not found"
            message = "Model Initialized Successfully."
            print(message)
            return model
        except Exception as e:
            # If there is a problem in loading the model, catch it and report the error
            message = "Model Failed to Initialize."
            print(f"{message} Error: {e}")
            return None

    def __init__(self, predict_fn: PredictFunction, batch_size: int = 1, is_legacy_fn=False):
        self.predict_fn = predict_fn
        self.supports_batch = batch_size > 1
        self.batch_size = batch_size
        self.legacy = is_legacy_fn

    def predict(self, inputs: List[Mapping[str, bytes]]) -> List[Mapping[str, bytes]]:
        if self.legacy:
            return self._predict_legacy(inputs)
        if self.supports_batch:
            return self._predict_batch(inputs)
        else:
            return self._predict_single(inputs)

    def _predict_single(self, inputs: List[Mapping[str, bytes]]) -> List[Mapping[str, bytes]]:
        outputs = []
        for input_item in inputs:
            try:
                output = self.predict_fn(input_item)
            except Exception as e:
                print(f"Error: {e}")
                # TODO - is there more information we can include here like a backtrace?
                # TODO - convert the error to bytes
                output = {"error": e}
            outputs.append(output)
        return outputs

    def _predict_batch(self, inputs: List[Mapping[str, bytes]]) -> List[Mapping[str, bytes]]:
        outputs = []
        # Split inputs into groups of self.batch_size
        batches = batch(inputs, self.batch_size)
        for b in batches:
            outputs.extend(self.predict_fn(b))
        return outputs

    def _predict_legacy(self, inputs: List[Mapping[str, bytes]]) -> List[Mapping[str, bytes]]:
        if self.batch_size == 1:
            outputs = []
            for input_item in inputs:
                output = self.predict_fn(input_item["input"])
                outputs.append({"results.json": json.dumps(output, separators=(",", ":"), cls=NumpyEncoder).encode()})
            return outputs
        else:
            adjusted_inputs = [input_item["input"] for input_item in inputs]
            # Split inputs into groups of self.batch_size
            outputs = []
            batches = batch(adjusted_inputs, self.batch_size)
            for b in batches:
                outputs.extend(self.predict_fn(b))
            adjusted_outputs = [{"results.json": json.dumps(o, separators=(",", ":"), cls=NumpyEncoder).encode()} for o in outputs]
            return adjusted_outputs
