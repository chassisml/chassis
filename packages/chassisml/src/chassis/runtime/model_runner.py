from __future__ import annotations

import os
import json
import cloudpickle
from typing import List, Mapping, Optional, Sequence, cast

from chassis.ftypes import BatchPredictFunction, LegacyBatchPredictFunction, LegacyNormalPredictFunction, NormalPredictFunction, PredictFunction
from .numpy_encoder import NumpyEncoder
from .constants import (PACKAGE_DATA_PATH, PYTHON_MODEL_KEY,
                        python_pickle_filename_for_key)


def batch(items: Sequence, size: int):
    """
    Yields lists of size `size` until all items have been exhausted.

    Args:
        items: The batch of inputs to perform inference on.
        size: The batch size that the model supports.
    """
    for i in range(0, len(items), size):
        yield items[i:i + size]


class ModelRunner:
    """
    This class abstracts all the potentially different `predict` method
    signatures into a single API that can be used by the model servers.

    When initializing the model, pass in a Python function that adheres to
    any of the defined signatures indicated by [chassis.ftypes.PredictFunction][]
    type alias. If your model supports batch predictions, set the `batch_size`
    to the number of inputs that your model can process at once.
    """

    @classmethod
    def load(cls) -> Optional[ModelRunner]:
        """
        Convenience function used by model servers to load a cloudpickle'd
        model in the model container.
        """
        try:
            # If this is the first time calling the `Status` route, then
            # attempt to load the model.
            filename = python_pickle_filename_for_key(PYTHON_MODEL_KEY)
            with open(os.path.join(PACKAGE_DATA_PATH, filename), "rb") as f:
                modules = cloudpickle.load(f)
            model: ModelRunner = modules[PYTHON_MODEL_KEY]
            if model is None:
                raise "Model not found"
            message = "Model Initialized Successfully."
            print(message)
            return model
        except Exception as e:
            # If there is a problem in loading the model, catch it and report
            # the error.
            message = "Model Failed to Initialize."
            print(f"{message} Error: {e}")
            return None

    def __init__(self, predict_fn: PredictFunction, batch_size: int = 1,
                 is_legacy_fn: bool = False):
        """
        Init.

        Args:
            predict_fn: Single predict function of type `PredictFunction` that
                represents a model inference function.
            batch_size: Integer representing the batch size your model supports.
                If your model does not support batching, the default value is 1
            is_legacy_fn: If `True`, predict_fn follows legacy format (not typed,
                only single input and output supported, returns dictionary)
        """
        self.predict_fn = predict_fn
        self.supports_batch = batch_size > 1
        self.batch_size = batch_size
        self.legacy = is_legacy_fn

    def predict(self, inputs: Sequence[Mapping[str, bytes]]) -> Sequence[Mapping[str, bytes]]:
        """
        Performs an inference against the model.

        Args:
            inputs: Mapping of input name (str) to input data (bytes) which the
                predict function is expected to process for inference.

        Returns:
            List of outputs the `predict_fn` returns
        """
        if self.legacy:
            return self._predict_legacy(inputs)
        if self.supports_batch:
            return self._predict_batch(inputs)
        else:
            return self._predict_single(inputs)

    def _predict_single(self, inputs: Sequence[Mapping[str, bytes]]) -> Sequence[Mapping[str, bytes]]:
        # Since the predict function could be any of a number of types,
        # we need to cast it to the particular type we're expecting to
        # avoid mypy errors.
        predict_fn = cast(NormalPredictFunction, self.predict_fn)
        outputs: List[Mapping[str, bytes]] = []
        for input_item in inputs:
            try:
                output: Mapping[str, bytes] = predict_fn(input_item)
            except Exception as e:
                print(f"Error: {e}")
                # TODO - is there more information we can include here like a backtrace?
                # TODO - convert the error to bytes
                output = {"error": f"{e}".encode()}
            outputs.append(output)
        return outputs

    def _predict_batch(self, inputs: Sequence[Mapping[str, bytes]]) -> Sequence[Mapping[str, bytes]]:
        # Since the predict function could be any of a number of types,
        # we need to cast it to the particular type we're expecting to
        # avoid mypy errors.
        predict_fn = cast(BatchPredictFunction, self.predict_fn)
        outputs: List[Mapping[str, bytes]] = []
        # Split inputs into groups of self.batch_size
        batches = batch(inputs, self.batch_size)
        for b in batches:
            outputs.extend(predict_fn(b))
        return outputs

    def _predict_legacy(self, inputs: Sequence[Mapping[str, bytes]]) -> Sequence[Mapping[str, bytes]]:
        outputs: List[Mapping[str, bytes]] = []
        if self.batch_size == 1:
            # Since the predict function could be any of a number of types,
            # we need to cast it to the particular type we're expecting to
            # avoid mypy errors.
            predict_fn = cast(LegacyNormalPredictFunction, self.predict_fn)
            for input_item in inputs:
                output = predict_fn(input_item["input"])
                outputs.append({"results.json": json.dumps(output, separators=(
                    ",", ":"), cls=NumpyEncoder).encode()})
            return outputs
        else:
            # Since the predict function could be any of a number of types,
            # we need to cast it to the particular type we're expecting to
            # avoid mypy errors.
            batch_predict_fn = cast(LegacyBatchPredictFunction, self.predict_fn)
            adjusted_inputs = [input_item["input"] for input_item in inputs]
            # Split inputs into groups of self.batch_size
            batches = batch(adjusted_inputs, self.batch_size)
            for b in batches:
                outputs.extend(batch_predict_fn(b))
            adjusted_outputs: List[Mapping[str, bytes]] = [
                {"results.json": json.dumps(o, separators=(",", ":"), cls=NumpyEncoder).encode()}
                for o in outputs]
            return adjusted_outputs
