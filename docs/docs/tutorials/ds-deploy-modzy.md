# Deploy Model to Modzy

<!-- TODO: add link to google colab notebook -->

To deploy a model to Modzy, we must first create a model following the same steps outlined in the [Build a Model](https://chassis.ml/tutorials/ds-connect/) tutorial. If you have already worked throgh this, the following snippet of code is exactly the same.
## Create the model

You can copy this code directly to your Python editor of choice, assuming you have installed the Chassisml SDK and other required packages: 
```bash
pip install chassisml scikit-learn mlflow joblib requests
```

```python
'''
import depedencies
'''
import chassisml
import sklearn
from joblib import dump, load

'''
create model
'''
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

'''
build process method
'''
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

'''
connect to Chassis client and build Chassis model
'''
# create Chassis model
chassis_model = chassis_client.create_model(process_fn=process)

# test Chassis model locally (can pass filepath, bufferedreader, bytes, or text here):
sample_filepath = './examples/modzy/input_sample.json'
results = chassis_model.test(sample_filepath)
print(results)

# test environment and model within Chassis service, must pass filepath here:
test_env_result = chassis_model.test_env(sample_filepath)
print(test_env_result)

'''
define Docker Hub credentials
'''
dockerhub_user = <my.username>
dockerhob_pass = <my.password>
```

## Define Modzy data

At this point, we have built a valid Chassis model that can be published directly to Docker Hub, as demonstrated in [here](https://chassis.ml/tutorials/ds-connect/#build-the-image-and-publish-to-modzy). 

Now in this tutorial, we will take it a step further and deploy this model directly to Modzy by simply modifying the `publish` method.

To follow along, you must first define the following Modzy-specific fields:

* *Modzy Credentials*
    * `modzy_url`: Valid URL to Modzy instance (e.g., "https://app.modzy.com")
    * `modzy_api_key`: Valid API key associated with your Modzy account. Sign up for a free account [here](https://www.modzy.com/try-free/)
* `modzy_sample_input_filepath`: Sample data to run through model container for inference example

```python
MODZY_URL = "<my-modzy-instance-url>"
MODZY_API_KEY = "<my-modzy-api-key>"
MODZY_SAMPLE_FILEPATH = sample_filepath
```
## Deploy to Modzy

We can now make the job request to the Chassisml service, which will build a container image with our model, push that image to Docker Hub, and deploy the built image all the way through to Modzy.  

```python
dockerhub_user = <my.username>
dockerhob_pass = <my.password>

response = chassis_model.publish(
    model_name="Sklearn Digits",
    model_version="0.0.1",
    registry_user=dockerhub_user,
    registry_pass=dockerhub_pass,
    modzy_url=MODZY_URL,
    modzy_api_key=MODZY_API_KEY,
    modzy_sample_input_path=MODZY_SAMPLE_FILEPATH
)

job_id = response.get('job_id')
final_status = chassis_client.block_until_complete(job_id)
```

If everything has gone well we should see something similar to this.

```bash
Publishing container... Ok!
```

Print status of job completion and your new model URL:
```python
if final_status["result"] is not None:
    print("New model URL: {}".format(final_status["result"]["container_url"]))
else:
    print("Chassis job failed \n\n {}".format(final_status))
```

## Submit Inference Job to Modzy

Pending a successful Chassis job completion, we can now submit an inference to our model sitting in the Modzy platform. To do so, the only additional requirement we need is the Modzy Python SDK.

```bash
pip install modzy-sdk
```

Once this is successfully installed in our envrionment, we can establish our connection to the Modzy API client.

```python
from modzy import ApiClient

client = ApiClient(base_url=MODZY_URL, api_key=MODZY_API_KEY)
```

Next, define three pieces of information we need to submit an inference to our model.

```python
input_name = final_status['result']['inputs'][0]['name']
model_id = final_status['result'].get("model").get("modelId")
model_version = final_status['result'].get("version")
```

Finally, submit an inference job, retrieve the results, and print them to your console.

```python
inference_job = client.jobs.submit_file(model_id, model_version, {input_name: sample_filepath})
inference_job_result = client.results.block_until_complete(inference_job, timeout=None)
inference_job_results_json = inference_job_result.get_first_outputs()['results.json']
print(inference_job_results_json)
```