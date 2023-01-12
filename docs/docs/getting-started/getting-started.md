# Getting Started

!!! success "Welcome!"
     In this getting started guide, you will learn how to use the [Chassis SDK](https://pypi.org/project/chassisml/) to build your first ML container by connecting to the publicly-hosted Chassis service.
     Connecting to this service eliminates the need for you to deploy and stand up a [private Kubernetes cluster](../tutorials/deploy-manual.md). Each chassis job run on our hosted service has enough resources to containerize even the most memory intensive ML models (up to 8GB RAM and 2 CPUs).  

## Installation

To get started, make sure you set up a [Python virtual enviornment](https://realpython.com/what-is-pip/#using-pip-in-a-python-virtual-environment) and install the Chassis SDK (Python 3.6 and above supported).

```bash
pip install chassisml
```

## Try it out

Follow these steps to build your first model container (*estimated time: 5 minutes*)

1. Clone the Chassis repository into your environment: `git clone https://github.com/modzy/chassis.git`
2. Install [Jupyter](https://jupyter.org/install) in your conda or virtual environment if it is not already installed
3. Execute the Python code below

!!! info "Note"
     * To follow along with the example code, you must create a free [Docker Hub](https://hub.docker.com/signup) account if you do not already have one
     * You have the option of either opening and running the pre-configured [Example Notebook](https://github.com/modzy/chassis/blob/main/getting-started/Getting%20Started%20with%20Chassis.ipynb) or following the below instructions
     * The example code connects to the publicly-hosted Kubernetes service through this URL: **`https://chassis.app.modzy.com`**, which is hosted and managed in [Modzy's](https://modzy.com) public cloud

In your Python environment, install the remaining dependencies required to run the example code.

```bash
pip install scikit-learn numpy
```

Finally, create a file in the `./getting-started/` directory called `example.py` and add this code:

```python
import json
import pickle
import chassisml
import numpy as np

# load model
model = pickle.load(open("./model.pkl", "rb"))

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
sample_filepath = './digits_sample.json'
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

Next, run your script.

```bash
python example.py
```

In just a few minutes, the Chassis job will complete. Congratulations! You just built your first ML container from a Scikit learn digits classification model. Check out our [Tutorials](../tutorials/ds-postman.md) to learn about different ways to run this container.

