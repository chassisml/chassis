
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
        import chassis.guides as guides
        from chassis.builder import DockerBuilder

        # Import a pre-trained scikit-learn digit classification model with pre-defined container metadata
        model = guides.QuickstartDigitsClassifier
        # Test the model with a picture of a handwritten "5"
        results = model.test(guides.DigitsSampleData)
        # View test results
        print(results)

        # Configure container builder option as Docker
        builder = DockerBuilder(model)
        # Build container for the model locally
        job_results = builder.build_image("my-first-chassis-model")
        # View container info after the build completes
        print(job_results)
        ```

        Execute this snippet to kick off the local Docker build.

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

Congratulations! You just built your first ML container from a scikit-learn digits classification model. Next, run a sample inference through this container with Chassis's OMI inference client.

## Run Inference

To quickly test your new model container, you can leverage Chassis's `OMIClient.test_container` convenience function. When executed, this function will spin up your container, run inference on sample data, and return the prediction results.

Open a Python file (new or existing) and paste the following inference code. Again, we will use Chassis's quickstart mode to import load a sample piece of data.

!!! example "Inference"
    === "Python"
        The below inference code leverages Chassis's `OMIClient`. This client provides a convenience wrapper around a gRPC client that allows you to interact with the gRPC server within your model container.

        ```python
        import asyncio
        from chassis.client import OMIClient
        from chassis.guides import DigitsSampleData

        async def run_test():
            # Execute the test_container method to spin up the container, run inference, and return the results
            res = await OMIClient.test_container(container_name="my-first-chassis-model", inputs=DigitsSampleData, pull=False)
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

!!! info "What's next?"
    After completing this quickstart guide, you might be wondering how to integrate *your own* model into this workflow. This guide intentionally abstracts out much of the model configuration for a quick and easy experience to get up and running.

    Visit the **[Full Chassis Workflow](full-workflow.md)** guide to learn how to use Chassis with your own model!

