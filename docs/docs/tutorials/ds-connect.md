# Build a Model (Data Scientists)

!!! note
    If you just want to try Chassis, you can use the test drive, which will deploy it for you so that you can go straight to building a MLflow model into a Docker container and pushing it to your Docker Hub account in the `svc_demo.ipynb` sample notebook:

    <a href="https://testfaster.ci/launch?embedded=true&repo=https://github.com/combinator-ml/terraform-k8s-chassis&file=examples/testfaster/.testfaster.yml" target="_blank">:computer: Launch Test Drive :computer:</a>


In order to connect to Chassis service we are going to use the SDK. We will transform our model into MLFlow format and we will upload it by making a request. After that, the image that have been created will be uploaded to Docker Hub and we will be able to use it.

## Install the SDK

First step is to install the SDK using `pip`.

```bash
pip install chassisml
```

## Build or import the model

We can start from an existing model or create a new one. After that, we will need to transform it to MLFlow format so Chassis service will be able to manage it.

### Import required libraries

Since we are going to train our own model as an example, we need to import all the libraries that we will need to do that.

```python
import chassisml
import sklearn
import mlflow.pyfunc
from joblib import dump, load
```

### Create the model

Just as an example we are going to create and train a simple SKLearn model.

```python
from sklearn import datasets, svm
from sklearn.model_selection import train_test_split

digits = datasets.load_digits()
data = digits.images.reshape((len(digits.images), -1))

# Create a classifier: a support vector classifier
clf = svm.SVC(gamma=0.001)

# Split data into 50% train and 50% test subsets
X_train, X_test, y_train, y_test = train_test_split(
    data, digits.target, test_size=0.5, shuffle=False)

# Learn the digits on the train subset
clf.fit(X_train, y_train)
dump(clf, './model.joblib')
```

## Transform the model to MLFlow

Once that we have our model we transform it to MLFlow format.

```python
class CustomModel(mlflow.pyfunc.PythonModel):
    _model = load('./model.joblib')
    
    def load_context(self, context):
        self.model = self._model

    def predict(self, context, input_dict):
        processed_inputs = self.pre_process(input_dict['input_data_bytes'])
        inference_results = self.model.predict(processed_inputs)
        return self.post_process(inference_results)

    def pre_process(self, input_bytes):
        import json
        import numpy as np
        inputs = np.array(json.loads(input_bytes))
        return inputs / 2

    def post_process(self, inference_results):
        structured_results = []
        for inference_result in inference_results:
            inference_result = {
                "classPredictions": [
                    {"class": str(inference_result), "score": str(1)}
                ]
            }
            structured_output = {
                "data": {
                    "result": inference_result,
                    "explanation": None,
                    "drift": None,
                }
            }
            structured_results.append(structured_output)
        return structured_results
```

Notice that the SKLearn model that we created before is loaded into memory so that it will be packaged inside the MLFlow model. This way, in the `load_context` function we just need to point to the model that is already loaded in memory.

All other functions like `predict`, `pre_process` or `post_process` are completely up to you and the requirements of your model.

This is the conda environment that we are going to define in this case for our model.

```python
conda_env = {
    'channels': ['defaults', 'conda-forge', 'pytorch'],
    'dependencies': [
        'python=3.8.5',
        'pytorch',
        'torchvision',
        'pip',
        {
            'pip': [
                'mlflow',
                'lime',
                'sklearn'
            ],
        },
    ],
    'name': 'linear_env'
}
```

Finally we just save the MLFlow model in the directory we prefer.

```python
model_save_path = 'mlflow_custom_pyfunc_svm'

mlflow.pyfunc.save_model(
    path=model_save_path,
    python_model=CustomModel(),
    conda_env=conda_env
)
```

## Build the image

Now that we have our model in MLFlow format we need to make a request against the Chassis service to build the Docker image that exposes it.

### Define data

There is some model and image related data that we need to define before we send our model to Chassis.

In case we want Chassis to upload our image to Docker Hub we can pass the credentials in base64 format.

```bash
echo -n "<user>:<password>" | base64
```

Which we are going to asume that outputs `XxXxXxXx`.

This is an example of the data that we could use.

```python
image_data = {
    'name': '<user>/chassisml-sklearn-demo:latest',
    'model_name': 'digits',
    'model_path': './mlflow_custom_pyfunc_svm',
    'registry_auth': 'XxXxXxXx'
}
```

As we can see, we must define the following fields:

* `name`: tag of the image
* `model_name`: name of the model we trained before
* `model_path`: the directory where we have stored our MLFlow model
* `registry_path`: credentials in case we want to upload the image

### Make the request

Now we can make the request to let Chassis build our image by making a request.

We can decide if we want Chassis to upload the image to Docker Hub and we can also modify the address of the service.

Take into account that `base_url` should point to the address of the cluster where Chassis is running.

```python
res = chassisml.publish(
    image_data=image_data,
    upload=True, # True if we want Chassis to upload the image
    base_url='http://localhost:5000'
)

error = res.get('error')
job_id = res.get('job_id')

if error:
    print('Error:', error)
else:
    print('Job ID:', job_id)
```

If everything has gone well we should see something similar to this.

```bash
Publishing container... Ok!
Job ID: chassis-builder-job-a3864869-a509-4658-986b-25cb4ddd604d
```

### Check the job status

As we have seen, we have been assigned to an uid that we can use to check the status of the job that is building our image.

```python
chassisml.get_job_status(job_id)
```

And we should see something like this in case the job has not finished yet.

```python
{'active': 1,
 'completion_time': None,
 'conditions': None,
 'failed': None,
 'start_time': 'Fri, 09 Jul 2021 09:01:43 GMT',
 'succeeded': None}
```

On the other hand, if the job has already finished and our image has been correctly built this could be the output.

```python
{'active': None,
 'completion_time': 'Fri, 09 Jul 2021 09:13:37 GMT',
 'conditions': [{'last_probe_time': 'Fri, 09 Jul 2021 09:13:37 GMT',
   'last_transition_time': 'Fri, 09 Jul 2021 09:13:37 GMT',
   'message': None,
   'reason': None,
   'status': 'True',
   'type': 'Complete'}],
 'failed': None,
 'start_time': 'Fri, 09 Jul 2021 09:01:43 GMT',
 'succeeded': 1}
```

## Pull the image

Now that the process has completely finished we can pull and see our built image.

```bash
docker pull <user>/chassisml-sklearn-demo:latest
```

```bash
docker images <user>/chassisml-sklearn-demo:latest
```

If everything has gone as expected we will see something similar to this.

```bash
REPOSITORY                        TAG       IMAGE ID       CREATED         SIZE
<user>/chassisml-sklearn-demo     latest    0e5c5815f2ec   3 minutes ago   2.19GB
```
