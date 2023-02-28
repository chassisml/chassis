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
import chassisml # (1)
import numpy as np

# load model # (2)
model = pickle.load(open("./model.pkl", "rb"))

# define process function # (3)
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

# connect to Chassis client # (4)
chassis_client = chassisml.ChassisClient("https://chassis.app.modzy.com/")

# create Chassis model # (5)
chassis_model = chassis_client.create_model(process_fn=process)

# test Chassis model # (6)
sample_filepath = './digits_sample.json'
results = chassis_model.test(sample_filepath)
print(results)

# publish model to Dockerhub # (7)
docker_user = "<insert-Docker Hub username>"
docker_pass = "<insert-Docker Hub password>"
model_name = "My First Chassis Model"

response = chassis_model.publish(
    model_name=model_name,
    model_version="0.0.1",
    registry_user=docker_user,
    registry_pass=docker_pass,
    arm64=False # (8)
) # (9)

# wait for job to complete and print result # (10)
job_id = response.get('job_id')
final_status = chassis_client.block_until_complete(job_id)
if final_status['status']['succeeded'] == 1:
    print("Job Completed. View your new container image here: https://hub.docker.com/repository/docker/{}/{}".format(docker_user, "-".join(model_name.lower().split(" "))))
else:
    print("Job Failed. See logs below:\n\n{}".format(final_status['logs']))
```

1. First, we will import the Chassis SDK. If you have not already done so, make sure you install it via PyPi: `pip install chassisml`
2. Next, we will load our model. For this example, we have a pre-trained Scikit-learn classifier saved as a pickle file (`./model.pkl`). When integrating Chassis into your own code, this can be done however you load your model. It could be loaded from a pickle file, checkpoint file, multiple configuration files, etc. The *key* is that you load your model into memory so it can be accessed in the below `process` function. 
3. Here, we will define our `process` function, which you can think of as an inference function for your model. This function can access objects loaded into memory (e.g., `model` loaded above), and the only requirement is it must convert input data in raw bytes form to the data type your model expects. See this [guide](../how-to-guides/common-data-types.md) for help on converting common data types. In this example, we process the raw bytes data using `numpy` and `json`, pass this processed data through to our model for predictions (`model.predict`), and perform some postprocessing to return the results in a human-readable manner. You can customize this function based on your model and preferences.    
4. Here, we will connect to the publicly-hosted Chassis service.
5. Now, we will simply create a `ChassisModel` object directly from our process function. See the [reference docs](../chassisml_sdk-reference.md#chassisml-python-sdk.chassisml.chassisml.ChassisClient.create_model) for more details on this method.
6. Before kicking off the Chassis job, we can test our `ChassisModel` object by passing through a sample data path.
7. Here is where you will need to add in your own Docker Hub credentials for the `docker_user` and `docker_pass` variables. Chassis will use these credentials when the container image is built and it is time to push it to a container registry.
8. Chassis can build containers that compile for both AMD and ARM chipsets. By default, the `arm64` flag is set to False, but if changed to True in this line, the resulting container will be able to run on any device with an ARM 64 chip. 
9. Finally, kick off the Chassis job. If you follow this example code as-is, this execution should take 4-5 minutes to complete. To see more parameter options for this method, view the [reference docs](../chassisml_sdk-reference.md#chassisml-python-sdk.chassisml.chassisml.ChassisModel.publish)
10. After a successful Chassis job, these next few lines of code will check the final status of your job and print your the URL to your newly-built container!

Next, run your script.

```bash
python example.py
```

In just a few minutes, the Chassis job will complete. Congratulations! You just built your first ML container from a Scikit learn digits classification model. Check out our [Tutorials](../tutorials/ds-postman.md) to learn about different ways to run this container.

