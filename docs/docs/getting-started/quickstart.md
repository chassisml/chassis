
First, you will need to set up a [Python virtual enviornment](https://realpython.com/what-is-pip/#using-pip-in-a-python-virtual-environment) and install the Chassis SDK. Include `[quickstart]` to install the extra dependencies required to use the quickstart model. 


```bash
pip install chassisml[quickstart]
```

## Build Container

With the SDK installed, you can now begin to build your first model container. Chassis's quickstart mode provides a pre-trained scikit-learn digits classification model as a simple import, so you do not need to bring your own model.


!!! example "Container Build"
    === "Python"
        Paste the below code snippet into your Python file (Jupyter notebook or script in other preferred IDE) to build a model container from the Chassis quickstart scikit-learn model.


        ```python
        import cloudpickle
        import chassis.guides as guides
        from chassis.builder import DockerBuilder
        cloudpickle.register_pickle_by_value(guides)

        model = guides.QuickstartDigitsClassifier
        results = model.test(guides.DigitsSampleData)
        print(results)

        builder = DockerBuilder(model)
        job_results = builder.build_image("my-first-chassis-model")
        print(job_results)
        ```

        Execute this snippet to kick off the local Docker build.

This local container build should take just under a minute. Confirm the new container is available with the following command:

```bash
docker images
```

Expected output:

```
REPOSITORY                 TAG       IMAGE ID       CREATED         SIZE
my-first-chassis-model     latest    5c4ec0cfeb99   4 minutes ago   377MB
```

Congratulations! You just built your first ML container from a scikit-learn digits classification model. Next, run a sample inference through this container with Chassis's OMI inference client.

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
    === "Python"
        The below inference code leverages Chassis's `OMIClient` for inference. This client provides a convenience wrapper around a gRPC client that allows you to interact with the gRPC server within your model container. 

        ```python
        from chassis.client import OMIClient
        from chassis.guides import DigitsSampleData

        with OMIClient("localhost", 45000) as client:
            status = client.status()
            res = client.run(DigitsSampleData)
            result = res.outputs[0].output["results.json"]
            print(f"Result: {result}")
        ```

        Execute this code to perform an inference against your running container. 

A successful inference run should yield the following result:

```
Result: b'[{"data": {"result": {"classPredictions": [{"class": 5, "score": 0.71212}]}}}]'
```

!!! info "What's next?"
    After completing this quickstart guide, you might be wondering how to integrate *your own* model into this workflow. This guide intentionally abstracts out much of the model configuration for a quick and easy experience to get up and running.

    Visit the **[Full Chassis Workflow](full-workflow.md)** guide to learn how to use Chassis with your own model!  

