# Getting Started

## Installation
Install Chassis on your machine or in a virtual environment via [PyPi](https://pypi.org/project/chassisml/):

```bash
pip install chassisml
```

## Quick Example
Follow this example to build your first container from a simple Scikit-learn classifier.

> **Note**: To follow along with the example code below, you must create a free [Docker Hub](https://hub.docker.com/signup) account if you do not already have one. We also recommend setting up a virtual environment to run the below code. Chassis currently supports Python 3.6 and above.

Open a local Python environment (Jupyter notebook or preferred IDE), and install the following additional requirements. Or, simply follow along in the [Getting Started Notebook](./Getting%20Started%20with%20Chassis.ipynb).

```bash
pip install scikit-learn
```

If you choose to follow along in your own Python environment, copy and execute this example code into your Python editor.
```python
import json
import pickle
import chassisml
import numpy as np

# load model
model = pickle.load(open("getting-started/model.pkl", "rb"))

# define process function
def process(input_bytes):
    inputs = np.array(json.loads(input_bytes))
    inference_results = model.predict(inputs)
    structured_results = []
    for inference_result in inference_results:
        structured_output = {
            "data": {
                "result": {"classPredictions": [{"class": str(inference_result), "score": str(1)}]}
            }
        }
        structured_results.append(structured_output)
    return structured_results

# connect to Chassis client
chassis_client = chassisml.ChassisClient("https://chassis.app.modzy.com/")

# create Chassis model
chassis_model = chassis_client.create_model(process_fn=process)

# test Chassis model
sample_filepath = 'getting-started/digits_sample.json'
results = chassis_model.test(sample_filepath)
print(results)

# publish model to Dockerhub
docker_user = "<insert-Docker Hub username>"
docker_pass = "<insert-Docker Hub password>"
model_name = "My First Chassis Model"

response = chassis_model.publish(
    model_name=model_name,
    model_version="0.0.1",
    registry_user=docker_user,
    registry_pass=docker_pass
)

# wait for job to complete and print result
job_id = response.get('job_id')
final_status = chassis_client.block_until_complete(job_id)
if final_status['status']['succeeded'] == 1:
    print("Job Completed. View your new container image here: https://hub.docker.com/repository/docker/{}/{}".format(docker_user, "-".join(model_name.lower().split(" "))))
else:
    print("Job Failed. See logs below:\n\n{}".format(final_status['logs']))
```
