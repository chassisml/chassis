import time
import json
import pickle
import numpy as np
from typing import Mapping
from chassisml import ChassisModel # 
from chassis.builder import DockerBuilder # 
import chassis.guides as guides

# load model # 
model = pickle.load(guides.DigitsClassifier) 

# define predict function # 
def predict(input_bytes: Mapping[str, bytes]) -> dict[str, bytes]:
    inputs = np.array(json.loads(input_bytes['input']))
    inference_results = model.predict_proba(inputs)
    structured_results = []
    for inference_result in inference_results:
        structured_output = {
            "data": {
                "result": {"classPredictions": [{"class": np.argmax(inference_result).item(), "score": round(np.max(inference_result).item(), 5)}]}
            }
        }
        structured_results.append(structured_output)
    return {'results.json': json.dumps(structured_results).encode()}

# create chassis model object, add required dependencies, and define metadata
chassis_model = ChassisModel(process_fn=predict)                # 
chassis_model.add_requirements(["scikit-learn", "numpy"])       # 
chassis_model.metadata.model_name = "Digits Classifier"         # 
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
    description="Top digit prediction and confidence score"
)    

# test model # 
results = chassis_model.test(guides.DigitsSampleData)
print(results)

# build container # 
builder = DockerBuilder(chassis_model)
start_time = time.time()
res = builder.build_image(name="my-first-chassis-model", tag="0.0.1", show_logs=True)
end_time = time.time()
print(res)
print(f"Container image built in {round((end_time-start_time)/60, 5)} minutes")
