import sys

import cloudpickle

from .quickstart import QuickstartDigitsClassifier, DigitsClassifier, DigitsSampleData

current_module = sys.modules[__name__]
cloudpickle.register_pickle_by_value(current_module)
