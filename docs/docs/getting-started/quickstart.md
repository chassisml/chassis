## Installation

To get started, set up a [Python virtual enviornment](https://realpython.com/what-is-pip/#using-pip-in-a-python-virtual-environment) and install the Chassis SDK along with the other Python dependencies needed to execute the sample code.


```bash
pip install chassisml[quickstart]
```

## Build Container

Now, simply paste the below code snippet into your preferred Python file (Jupyter notebook or script in other IDE).

!!! example Example
    === "Python"

        ```python
        from chassis.builder import DockerBuilder
        from chassis.guides import QuickstartDigitsClassifier, DigitsSampleData

        model = QuickstartDigitsClassifier
        results = model.test(DigitsSampleData)

        builder = DockerBuilder(model)
        job_results = builder.build_image("my-first-chassis-model")
        print(job_results)
        ```


## Run Inference

TODO - need to add inference client