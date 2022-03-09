# Build a Model (Data Science)

<!-- TODO: confirm test drive stuff -->

<!-- !!! note
    If you just want to try Chassis, you can use the test drive, which will deploy it for you so that you can go straight to building a MLflow model into a Docker container and pushing it to your Docker Hub account in the `svc_demo.ipynb` sample notebook:

    <a href="https://testfaster.ci/launch?embedded=true&repo=https://github.com/combinator-ml/terraform-k8s-chassis&file=examples/testfaster/.testfaster.yml" target="_blank">:computer: Launch Test Drive :computer:</a> -->

In this tutorial, we will:

* Connect to the Chassis service with the Python SDK
* Load our model into memory (model can be saved as a file to be loaded or trained and loaded from scratch)
* Define a `process` function for inferencing
* Submit a job request to the Chassis service

After completing these steps, we will have a new container image uploaded to Docker Hub that we will be able to use locally or deploy to a serving platform of our choice.

Please note that in addition to the tutorial on this page, there are example Jupyter notebooks available in the Chassis repo [here](https://github.com/modzy/chassis/tree/main/chassisml-sdk/examples). Instructions to run those notebooks are provided in the README in that repo subdirectory.

## Install the SDK

First step is to install the SDK and additional packages required for this tutorial using `pip`.

```bash
pip install chassisml scikit-learn mlflow joblib requests
```

## Build or import the model

We can start from an existing model saved locally or create a new one, as long as the model can be loaded into memory. In this tutorial, we will create a simple classifier with the Scikit-Learn library. 

### Import required libraries

Since we are going to train our own model as an example, we need to import all the libraries that we will need to do that.

```python
import chassisml
import sklearn
from joblib import dump, load
```

### Create the model

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
```

## Define Process Method

Notice our Scikit-Learn model (`clf`) is now loaded into memory, which is exactly what we need to format it the way Chassis expects.

This means we can now prepare the process function, which must take raw bytes as input. This function is responsible for preprocessing the bytes, running inference, and returning formatted results. It can leverage anything (variables, functions, objects) defined in our environment. Notice we reference our model `clf` as defined above:

```python
def process(input_bytes):
    inputs = np.array(json.loads(input_bytes))/2
    inference_results = clf.predict(inputs)
    structured_results = []
    for inference_result in inference_results:
        structured_output = {
            "data": {
                "result": {"classPredictions": [{"class": str(inference_result), "score": str(1)}]}
            }
        }
        structured_results.append(structured_output)
    return structured_results
```

The process function can call other functions if needed. 

Next, we initialize our Chassis client, which we'll use to communicate with the Chassis service. Here, we assume our instance of Chassis is running locally on port 5000:

```python
chassis_client = chassisml.ChassisClient("http://localhost:5000")
```

Now let's create a Chassis model with our process function, test it locally with a local input file, and then also test the creation of the environment and the execution of the model with a sample input file within that created environment (this will occur within the Chassis service):

```python
# create Chassis model
chassis_model = chassis_client.create_model(process_fn=process)

# test Chassis model locally (can pass filepath, bufferedreader, bytes, or text here):
sample_filepath = './examples/modzy/input_sample.json'
results = chassis_model.test(sample_filepath)
print(results)

# test environment and model within Chassis service, must pass filepath here:
test_env_result = chassis_model.test_env(sample_filepath)
print(test_env_result)
```

## Build the image and publish to Modzy

Now that we have our model in the proper Chassis format, we need to make a request against the Chassis service to build the Docker image that exposes it. You can optionally define your desired conda environment and pass it to `publish()`, but if you don't, Chassis will automatically infer the dependencies for you based on what is required to run the `process` function. We just need to provide a model name and semantic version, dockerhub credentials, and we can optionally provide a sample input file and Modzy API key if we'd like to publish the model to Modzy:

```python
dockerhub_user = <my.username>
dockerhob_pass = <my.password>

response = chassis_model.publish(
    model_name="Sklearn Digits",
    model_version="0.0.1",
    registry_user=dockerhub_user,
    registry_pass=dockerhub_pass,
)

job_id = response.get('job_id')
final_status = chassis_client.block_until_complete(job_id)
```

The `block_until_complete` call will terminate once the Chassis job completes.

## Pull the image

Now that the process has completely finished we can pull and see our built image. The image name will be the `model_name` specified in the `publish()` call, but lowercase and with dashes instead of spaces. The image tag will be the `model_version`.

```bash
docker pull <my.username>/sklearn-digits:0.0.1
```

```bash
docker images <my.username>/sklearn-digits:0.0.1
```

If everything has gone as expected we will see something similar to this.

```bash
REPOSITORY                        TAG       IMAGE ID       CREATED         SIZE
<my.username>/sklearn-digits            latest    0e5c5815f2ec   3 minutes ago   2.19GB
```
<!-- 
## Run an inference job in Modzy

If you provided the required arguments to `publish()` to publish the model to Modzy, you can use the Modzy SDK to submit an inference job to your newly-published model. 

```python
from modzy import ApiClient

client = ApiClient(base_url='https://your.modzy.com/api', api_key=modzy_api_key)

input_name = final_status['result']['inputs'][0]['name']
model_id = final_status['result'].get("model").get("modelId")
model_version = final_status['result'].get("version")

inference_job = client.jobs.submit_file(model_id, model_version, {input_name: sample_filepath})
inference_job_result = client.results.block_until_complete(inference_job, timeout=None)
inference_job_results_json = inference_job_result.get_first_outputs()['results.json']
print(inference_job_results_json)
``` -->
