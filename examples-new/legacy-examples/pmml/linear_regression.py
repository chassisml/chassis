import time
from typing import Mapping

from chassis.builder import DockerBuilder
from chassisml import ChassisModel, ChassisClient

import pandas as pd
from io import StringIO
from sklearn_pmml_model.linear_model import PMMLLinearRegression

'''
Load model and data
'''
# Prepare data
df = pd.read_csv('data/categorical-test.csv')
Xte = df.iloc[:, 1:]

# Create sample data for testing later
with open("data/sample_regression.csv", "w") as f:
    Xte[:10].to_csv(f, index=False)
    
# Load model
clf = PMMLLinearRegression(pmml="models/linear-model-lm.pmml")

'''
Define process function
'''
def process(input_bytes):
    # load data
    inputs = pd.read_csv(StringIO(str(input_bytes, "utf-8")))
    
    # predictions
    output = clf.predict(inputs)
    
    # process output
    inference_result = {
        "predictions": [
            {"row": i+1, "score": score.item()} for i, score in enumerate(output)
        ]
    }    
    
    # format output
    structured_output = {
        "data": {
            "result": inference_result,
            "explanation": None,
            "drift": None,
        }
    }
    return structured_output


'''
Create Model
'''
# legacy way
# chassis_client = ChassisClient("https://chassis.app.modzy.com")
# model = chassis_client.create_model(process_fn=process)
# new way
model = ChassisModel(process_fn=process, legacy_predict_fn=True)

# add pip requirements
model.add_requirements(["sklearn-pmml-model", "pandas"])

# test model
sample_filepath = './data/sample_regression.csv'
results = model.test(sample_filepath)
print(results)

# build container
builder = DockerBuilder(model)
start_time = time.time()
res = builder.build_image(name="1.5-pmml-lin-regression", tag="0.0.1", show_logs=True)
end_time = time.time()
print(res)
print(f"Container image built in {round((end_time-start_time)/60, 5)} minutes")