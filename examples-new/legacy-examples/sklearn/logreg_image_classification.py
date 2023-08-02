import json
import time
from typing import Mapping

from chassis.builder import DockerBuilder
from chassisml import ChassisModel, ChassisClient

from sklearn.linear_model import LogisticRegression
from sklearn import datasets
import numpy as np


"""
Model Development
"""
# Import and normalize data
X_digits, y_digits = datasets.load_digits(return_X_y=True)
X_digits = X_digits / X_digits.max()

n_samples = len(X_digits)

# Split data into training and test sets
X_train = X_digits[: int(0.9 * n_samples)]
y_train = y_digits[: int(0.9 * n_samples)]
X_test = X_digits[int(0.9 * n_samples) :]
y_test = y_digits[int(0.9 * n_samples) :]

# Train Model
logistic = LogisticRegression(max_iter=1000)
print(
    "LogisticRegression mean accuracy score: %f"
    % logistic.fit(X_train, y_train).score(X_test, y_test)
)

# Save small sample input to use for testing later
sample = X_test[:5].tolist()
with open("data/digits_sample.json", 'w') as out:
    json.dump(sample, out)

def process(input_bytes):
    inputs = np.array(json.loads(input_bytes))
    inference_results = logistic.predict(inputs)
    structured_results = []
    for inference_result in inference_results:
        structured_output = {
            "data": {
                "result": {"classPredictions": [{"class": str(inference_result), "score": str(1)}]}
            }
        }
        structured_results.append(structured_output)
    return structured_results


'''
Create Model
'''
# legacy way
# chassis_client = ChassisClient("https://chassis.app.modzy.com")
# model = chassis_client.create_model(process_fn=process)
# new way
model = ChassisModel(process_fn=process, legacy_predict_fn=True)

# add pip requirements
model.add_requirements(["scikit-learn", "numpy"])

# test model
sample_filepath = './data/digits_sample.json'
results = model.test(sample_filepath)
print(results)

# build container
builder = DockerBuilder(model)
start_time = time.time()
res = builder.build_image(name="sklearn-1.5-log-regression", tag="0.0.2", show_logs=True)
end_time = time.time()
print(res)
print(f"Container image built in {round((end_time-start_time)/60, 5)} minutes")