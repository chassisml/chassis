
!!! tip "Welcome!"
    In this getting started guide, you will learn how to use the **[Chassis SDK](https://pypi.org/project/chassisml/)** to build your first ML container locally on your computer.  

    Check out the **[Quickstart]()** guide to build a container from a preset model, or follow the **[Build your first model]()** guide to implement it yourself!

!!! warning "What you will need"
    This quickstart guide requires two prerequisites to follow along:

    1. Python (v3.8 or greater supported)
    2. Docker (Installation instructions **[here](https://www.docker.com/products/docker-desktop/)**) 

    You can verify Docker it is successfully installed by typing `docker run hello-world` in your terminal.  


## Installation

To get started, set up a [Python virtual enviornment](https://realpython.com/what-is-pip/#using-pip-in-a-python-virtual-environment) and install the Chassis SDK along with the other Python dependencies needed to execute the sample code.


```bash
pip install chassisml scikit-learn numpy
```

## Build Container

Build your first model container in a few simple steps:

1. Open a Python file (this may be a Jupyter notebook file or Python script in your preferred IDE), and call it `quickstart.py`
2. Paste the below code into your Python file

```python
import time
import json
import pickle
import numpy as np
from typing import Mapping
from chassisml import ChassisModel # (1)
from chassis.builder import DockerBuilder # (2)

# load model # (3)
# TODO - configure this to import from URL or hosted file
model = pickle.load(open("<path-to-publicly-hosted-model-file>", "rb")) 

# define predict function # (4)
# TODO - edit and/or change model predict function
def predict(inputs: Mapping[str, bytes]) -> dict[str, bytes]:
    input_processed = np.array(json.loads(inputs['input']))
    inference_results = model.predict(input_processed)
    structured_results = []
    for inference_result in inference_results:
        structured_output = {
            "data": {
                "result": {"classPredictions": [{"class": str(inference_result), "score": str(1)}]}
            }
        }
        structured_results.append(structured_output)
    return {'results.json': json.dumps(structured_results).encode()}


# create chassis model # (5)
chassis_model = ChassisModel(process_fn=predict)
# add pip requirements # (6)
chassis_model.add_requirements(["scikit-learn", "numpy"])

# test model # (7)
sample_data = "TODO"
results = chassis_model.test(sunflower_path)
print(results)

# build container # (8)
builder = DockerBuilder(chassis_model)
start_time = time.time()
res = builder.build_image(name="quickstart-chassis-model", tag="0.0.1", show_logs=True)
end_time = time.time()
print(res)
print(f"Container image built in {round((end_time-start_time)/60, 5)} minutes")
```

1. First, we will import the `ChassisModel` class from the Chassis SDK. If you have not already done so, make sure you install it via PyPi: `pip install chassisml`
2. In addition to the `ChassisModel` object, we need to import a Builder option. The two available options, `DockerBuilder` and `RemoteBuilder`, will both build the same container but in different execution environments. Since we'd like to build a container locally with Docker, we will import the `DockerBuilder` object.  
3. Next, we will load our model. For this example, we have a pre-trained Scikit-learn classifier saved as a pickle file (`./model.pkl`). When integrating Chassis into your own code, this can be done however you load your model. It could be loaded from a pickle file, checkpoint file, multiple configuration files, etc. The *key* is that you load your model into memory so it can be accessed in the below `process` function. 
4. Here, we will define a *single* predict function, which you can think of as an inference function for your model. This function can access in-memory objects (e.g., `model` loaded above), and the only requirement is it must convert input data in raw bytes form to the data type your model expects. See this [guide](../how-to-guides/common-data-types.md) for help on converting common data types. In this example, we process the raw bytes data using `numpy` and `json`, pass this processed data through to our model for predictions (`model.predict`), and perform some postprocessing to return the results in a human-readable manner. You can customize this function based on your model and preferences.    
5. Now, we will simply create a `ChassisModel` object directly from our process function.
6. With our `ChassisModel` object defined, there are a few optional methods we can call. Here, we will add the Python libraries our model will need to run. You can pass a list of packages you would list in a `requirements.txt` file that will be installed with Pip.
7. Before kicking off the Chassis job, we can test our `ChassisModel` object by passing through sample data.
8. After our test has passed, we can define our builder object, which as mentioned before, will be `DockerBuilder`. This builder object uses your local Docker installation to build a model container and store it on your machine. First, we will simply pass our `ChassisModel` object to our builder, and build the container image using the `build_image` function.

Finally, run your script.

```bash
python quickstart.py
```

In just about 60 (***TODO - probably less***) seconds, the Chassis job will complete. Congratulations! You just built your first ML container from a Scikit learn digits classification model. Verify your container build by running the following command in your terminal:

```bash
docker images
```

The output should look something like this:
```
TODO - fill in
```

## Run Inference

TODO - need to add inference client

