import os
import json
import pickle
import numpy as np
from typing import Dict, Mapping

from chassisml import ChassisModel

# load data
ROOT = os.path.abspath(os.path.dirname(__file__))
digits_clf = pickle.load(open(os.path.join(ROOT, "data", "logistic.pkl"), "rb"))
digits_sample = os.path.join(ROOT, "data", "digits_sample.json")


# define predict function
def predict(input_bytes: Mapping[str, bytes]) -> Dict[str, bytes]:
    inputs = np.array(json.loads(input_bytes['input']))
    inference_results = digits_clf.predict_proba(inputs)
    structured_results = []
    for inference_result in inference_results:
        structured_output = {
            "data": {
                "result": {"classPredictions": [{"class": np.argmax(inference_result).item(), "score": round(np.max(inference_result).item(), 5)}]}
            }
        }
        structured_results.append(structured_output)
    return {'results.json': json.dumps(structured_results).encode()}


# define chassis model object and add required dependencies
chassis_model = ChassisModel(predict)
chassis_model.add_requirements(["scikit-learn", "numpy"])
chassis_model.metadata.model_name = "Digits Classifier"
chassis_model.metadata.model_version = "0.0.1"
chassis_model.metadata.add_input(
    key="input",
    accepted_media_types=["application/json"],
    max_size="10M",
    description="Numpy array representation of digits image"
)
chassis_model.metadata.add_output(
    key="results.json",
    media_type="application/json",
    max_size="1M",
    description="Top digit classification and corresponding confidence score"
)
# results = chassis_model.test(digits_sample)
# results = chassis_model.test(open(digits_sample, "rb").read())
# print(results)

# define objects for quickstart import
QuickstartDigitsClassifier = chassis_model
DigitsClassifier = open(os.path.join(ROOT, "data", "logistic.pkl"), "rb")
DigitsSampleData = [{"input": open(digits_sample, "rb").read()}]
