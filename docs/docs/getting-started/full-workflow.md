

In this guide, we will transform a pre-trained scikit-learn digits classification model into a `ChassisModel` object that we will use to build a container.

If you did not follow the **[Quickstart Guide](./quickstart.md)**, you will need to first set up a [Python virtual enviornment](https://realpython.com/what-is-pip/#using-pip-in-a-python-virtual-environment) and install the Chassis SDK. Include `--pre` to install the pre-release beta version and `[quickstart]` to install the extra dependencies required to use the quickstart model.


```bash
pip install --pre chassisml[quickstart]
```

## Build Container

Next, open a Python file (new or existing) and paste the following inference code. If you did follow the Quickstart guide, you will notice there is more code in the below example. That is because this example demonstrates the process of taking an in-memory model object, constructing a custom `predict` function, and using both to create your own `ChassisModel` object.

!!! example "Model Configuration & Container Build"

    Paste the below code snippet into your Python file (Jupyter notebook or script in other preferred IDE) to build a model container from scratch using a pre-trained model and sample data file embedded in the Chassis library. Make sure to check out the code annotations for detailed descriptions of each step!

    ```python
    import time
    import json
    import pickle
    import cloudpickle
    import numpy as np
    from typing import Mapping
    from chassisml import ChassisModel # (1)
    from chassis.builder import DockerBuilder # (2)
    import chassis.guides as guides

    # load model # (3)
    model = pickle.load(guides.DigitsClassifier)

    # define predict function # (4)
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
    chassis_model = ChassisModel(process_fn=predict)                # (5)
    chassis_model.add_requirements(["scikit-learn", "numpy"])       # (6)
    chassis_model.metadata.model_name = "Digits Classifier"         # (7)
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

    # test model # (8)
    results = chassis_model.test(guides.DigitsSampleData)
    print(results)

    # build container # (9)
    builder = DockerBuilder(chassis_model)
    start_time = time.time()
    res = builder.build_image(name="my-first-chassis-model", tag="0.0.1", show_logs=True)
    end_time = time.time()
    print(res)
    print(f"Container image built in {round((end_time-start_time)/60, 5)} minutes")
    ```

    1. First, we will import the `ChassisModel` class from the Chassis SDK. If you have not already done so, make sure you install it via PyPi: `pip install chassisml`
    2. In addition to the `ChassisModel` object, we need to import a Builder object. The two available options, `DockerBuilder` and `RemoteBuilder`, will both build the same container but in different execution environments. Since we'd like to build a container locally with Docker, we will import the `DockerBuilder` object.
    3. Next, we will load our model. For this example, we have a pre-trained Scikit-learn classifier embedded into the Chassis library (`chassis.guides.DigitsClassifier`). When integrating Chassis into your own code, this can be done however you load your model. You might load your model from a pickle file, checkpoint file, multiple configuration files, etc. The *key* is that you load your model into memory so it can be accessed in the below `predict` function.
    4. Here, we will define a *single* predict function, which you can think of as an inference function for your model. This function can access in-memory objects (e.g., `model` loaded above), and the only requirement is it must convert input data from raw bytes form to the data type your model expects. See this **[guide](../guides/common-data-types.md)** for help on converting common data types. In this example, we process the raw bytes data using `numpy` and `json`, pass this processed data through to our model for predictions (`model.predict`), and perform some postprocessing to return the results in a human-readable manner. You can customize this function based on your model and preferences.
    5. Now, we will simply create a `ChassisModel` object directly from our predict function.
    6. With our `ChassisModel` object defined, there are a few optional methods we can call. Here, we will add the Python libraries our model will need to run. You can pass a list of packages you would list in a `requirements.txt` file that will be installed with Pip.
    7. In the next few lines, we will define the four minimum metadata fields that are required before building our container. These fields represent your model's name, version, inputs, and outputs. *NOTE: There are many other optional fields you can choose to document if preferred.*
    8. Before kicking off the Chassis job, we can test our `ChassisModel` object by passing through sample data. For convenience, we can use the sample data embedded in the Chassis library specific to this Digits Classifier.
    9. After our test has passed, we can define our builder object, which as mentioned before, will be `DockerBuilder`. This builder object uses your local Docker daemon to build a model container and store it on your machine. First, we will simply pass our `ChassisModel` object to our builder, and build the container image using the `build_image` function.

    Execute this snippet to kick off the local Docker build

This local container build should take just under a minute. The `job_results` of a successful build will display the details of your new container (*note: the "Image ID" digest will be different for each build*):

```
Generating Dockerfile...Done!
Copying libraries...Done!
Writing metadata...Done!
Compiling pip requirements...Done!
Copying files...Done!
Starting Docker build...Done!
Image ID: sha256:d222014ffe7bacd27382fb00cb8686321e738d7c80d65f0290f4c303459d3d65
Image Tags: ['my-first-chassis-model:latest']
Cleaning local context
Completed:       True
Success:         True
Image Tag:       my-first-chassis-model:latest
```

Congratulations! You just transformed a scikit-learn digits classifier into a production container! Next, run a sample inference through this container with Chassis's OMI inference client.

## Run Inference

Before submitting data to your model container, you must first spin it up. To do so, open a terminal on your machine and run the container:

```bash
docker run --rm -it -p 45000:45000 my-first-chassis-model
```

When your container is spun up and running, you should see the following message in your logs:

```
Serving on: 45000
```

Next, open a Python file (new or existing) and paste the following inference code. Again, we will use a convenience import with Chassis's quickstart mode to load a sample piece of data.

!!! example "Inference"
    === "Jupyter Notebook"

        The below inference code leverages Chassis's `OMIClient` for inference. This client provides a convenience wrapper around a gRPC client that allows you to interact with the gRPC server within your model container.

        ```python
        from chassis.client import OMIClient
        from chassis.guides import DigitsSampleData

        # Call and view results of status RPC
        status = await client.status()
        print(f"Status: {status}")
        # Submit inference with quickstart sample data
        res = await client.run(DigitsSampleData)
        # Parse results from output item
        result = res.outputs[0].output["results.json"]
        # View results
        print(f"Result: {result}")

        ```

        Execute this code to perform an inference against your running container.

    === "Other Python IDE"

        The below inference code leverages Chassis's `OMIClient` for inference. Notice this code is slighly different than when running it in a Jupyter notebook, due to the built-in async functionality that comes with IPython.

        ```python
        import asyncio
        from chassis.client import OMIClient
        from chassis.guides import DigitsSampleData

        async def run_test():
            # Instantiate OMI Client connection to model running on localhost:45000
            async with OMIClient("localhost", 45000) as client:
                # Call and view results of status RPC
                status = await client.status()
                print(f"Status: {status}")
                # Submit inference with quickstart sample data
                res = await client.run(DigitsSampleData)
                # Parse results from output item
                result = res.outputs[0].output["results.json"]
                # View results
                print(f"Result: {result}")

        if __name__ == '__main__':
            asyncio.run(run_test())
        ```

        Execute this code to perform an inference against your running container.

A successful inference run should yield the following result:

```
Result: b'[{"data": {"result": {"classPredictions": [{"class": 5, "score": 0.71212}]}}}]'
```

