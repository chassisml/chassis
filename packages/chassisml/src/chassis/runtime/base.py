import abc
from typing import Mapping, Sequence

from chassis.ftypes import PredictionResult


class ModelBase(metaclass=abc.ABCMeta):
    def init(self):
        pass

    def predict(self, inputs: Mapping[str, bytes]) -> PredictionResult:
        raise "Not Implemented"

    def predict_batch(self, inputs: Sequence[Mapping[str, bytes]]) -> Sequence[PredictionResult]:
        return [self.predict(i) for i in inputs]

    def predict_v1(self, inputs: Sequence[Mapping[str, bytes]]) -> Sequence[Mapping[str, bytes]]:
        original_outputs = self.predict_batch(inputs)
        outputs = []
        for oo in original_outputs:
            d: dict[str, bytes] = dict()
            for o in oo.outputs:
                if o.text is not None and len(o.text) > 0:
                    d[o.key] = o.text.encode()
                else:
                    d[o.key] = o.data.data
            outputs.append(d)
        return outputs
