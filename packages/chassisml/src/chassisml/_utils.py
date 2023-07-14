import json
from typing import Any

import numpy as np


class NumpyEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, np.float32) or isinstance(o, np.float64):
            return float(o)
        if isinstance(o, np.int32) or isinstance(o, np.int64):
            return int(o)
        return json.JSONEncoder.default(self, o)
