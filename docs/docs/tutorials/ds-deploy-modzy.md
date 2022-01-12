# Deploy Model to Modzy

!!! note
    If you just want to try Chassis, you can use the test drive, which will deploy Chassis and KFServing for you so you can use Chassis to containerize an MLflow model, push it to your Docker Hub account, and then publish it to the KFServing instance running inside the test drive, in the `kfserving.ipynb` sample notebook:

    <a href="https://testfaster.ci/launch?embedded=true&repo=https://github.com/combinator-ml/terraform-k8s-chassis&file=examples/testfaster/.testfaster.yml" target="_blank">:computer: Launch Test Drive :computer:</a>


## Create the model

The first steps we must follow here are the same ones that we can read in the [Build a Model](https://chassis.ml/tutorials/ds-connect/) tutorial.

We should follow exactly the same steps in case we don't have already our MLFlow model. In other case we can go directly to the step where we build the image. Basically we should:

* Install the SDK
* Import required libraries
* Create the model
* Transform the model to MLFlow

## Build the image

Once we have finished the previous steps, we need to define not only the data that Chassis needs to build the image, but also the data that Modzy will need to deploy our model.

So, we are going to assume that we have already generated our `registry_auth` for uploading the image to Docker Hub and we just have the data required for Chassis.

```python
image_data = {
    'name': '<user>/chassisml-sklearn-demo:latest',
    'model_name': 'digits',
    'model_path': './mlflow_custom_pyfunc_svm',
    'registry_auth': 'XxXxXxXx'
}
```

### Define Modzy data

At this point, we are going to define the data that we need to deploy the model to Modzy. These are the fields that we need to take into account.

* `metadata_path`: this is the path to the [model.yaml](https://models.modzy.com/docs/model-packaging/model-packaging-python-template/yaml-file_) file that is needed to define all information about the model. Chassis has a default one, but you should define your own based on [this example](https://github.com/modzy/chassis/blob/main/chassisml-sdk/examples/modzy/model.yaml)
* `sample_input_path`: this is the path to the [sample input](https://models.modzy.com/docs/model-deployment/model-deployment/input-outputs) that is needed when deploying the model. An example that fits the model we built in this tutorial can be found [here](https://github.com/modzy/chassis/blob/main/chassisml-sdk/examples/modzy/input_sample.json)
* `deploy`: if it is `True`, then Chassis will manage to deploy the model into Modzy platform. Otherwise you can do this manually through the Modzy UI
* `api_key`: you should have your own [api key](https://models.modzy.com/docs/how-to-guides/api-keys) from Modzy in order to let Chassis deploy the model for you

```python
modzy_data = {
    'metadata_path': './modzy/model.yaml',
    'sample_input_path': './modzy/input_sample.json',
    'deploy': True,
    'api_key': 'XxXxXxXx.XxXxXxXx'
}
```

Notice that if `deploy` is False this means that you can avoid defining the rest of the fields. Anyway, `metadata_path` should be defined in case you will eventually deploy the model to Modzy. This is important because the model will use this information when being deployed to Modzy, so it needs to be updated.

## Make the request

Now that we have defined both the data for Chassis and the data for Modzy, we are able to make the request against Chassis service to build the image and deploy it to Modzy.

Take into account that `base_url` should point to the address of the cluster where Chassis is running. In this case, that we want the built image to be deployed to Modzy, the cluster where Chassis is running needs to have access (VPN) to Modzy server. Otherwise, Modzy server will be unreachable by Chassis and it will not be possible to deploy the model.

```python
res = chassisml.publish(
    image_data=image_data,
    modzy_data=modzy_data,
    upload=True,
    # ^ Needed because Chassis will deploy the model
    # to Modzy based on the Docker Hub uploaded image
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

## Check the job status

Notice that unlike in the [KFServing tutorial](https://chassis.ml/tutorials/ds-deploy/), here we don't need to define the `INTERFACE` environment variable since Modzy is the default one.

We must wait until it has finished, which may take several minutes. We can use the job id to check the status of the job. Once it has finished we should see something similar to this.

```python
{'result': {'containerImage': {'containerImageSize': 0,
  (...)
   'uploadStatus': 'IN_PROGRESS'},
  'container_url': 'https://integration.modzy.engineering/models/<model_id>/<model_version>',
  (...)
  'inputs': [{'acceptedMediaTypes': 'application/json',
    'description': 'numpy array 2d',
    'maximumSize': 1024000,
    'name': 'input.json'}],
  'isActive': False,
  'isAvailable': True,
  'longDescription': 'It classifies digits.',
  'model': {'author': 'Integration',
   'modelId': '<model_id>'
   'createdByEmail': 'cmillan@sciling.com',
   (...)
   'visibility': {'scope': 'ALL'}},
  'outputs': [{'description': 'numpy 2d array',
    'maximumSize': 1024000,
    'mediaType': 'application/json',
    'name': 'results.json'}],
    (...)
  'timeout': {'run': 60000, 'status': 60000},
  'version': '0.1.0'},
 'status': {'active': None,
  'completion_time': 'Thu, 05 Aug 2021 16:29:36 GMT',
  'conditions': [{'last_probe_time': 'Thu, 05 Aug 2021 16:29:36 GMT',
    'last_transition_time': 'Thu, 05 Aug 2021 16:29:36 GMT',
    'message': None,
    'reason': None,
    'status': 'True',
    'type': 'Complete'}],
  'failed': None,
  'start_time': 'Thu, 05 Aug 2021 16:14:38 GMT',
  'succeeded': 1}}
```

Two top keys can be seen:

* `result`: in case `deploy` was `True` this will contain some information related to the model deployed in Modzy. In particular we can see the full url to the model if we access the `container_url` key.
* `status`: this contains the information about the Kubernetes job that has built the image (and uploaded it to Modzy in case `deploy` was `True` as explained above)

## Query the model

Now we are ready to query our model deployed in Modzy.

Again, we will need VPN access to Modzy server to make a request against our model and to get the results. If we already have access, then we can use this json as a [request to the model](https://models.modzy.com/docs/jobs/jobs/submit-job-text).

### Make the request

This should be the contents of our `request_body.json` file.

```json
{
  "model": {
    "identifier": "<model_id>",
    "version": "<model_version>"
  },
  "input": {
    "type": "text",
    "sources": {
      "input": {
        "<input_name>": "<data_that_we_want_to_predict>"
      }
    }
  }
}
```

Here there are some fields that we need to define.

* `model_id`: we can get this from the `result` obtained above
* `model_version`: we can get this from the `result` obtained above
* `data_that_we_want_to_predict`: this is the data to predict, that in our example can be the [data sample](https://github.com/modzy/chassis/blob/main/chassisml-sdk/examples/modzy/input_sample.json)

So we can make the request like this.

```bash
curl -X POST \
-H 'Authorization: ApiKey <api_key>' \
-H 'Content-Type: application/json' \
-d@request_body.json \
"https://integration.modzy.engineering/api/jobs"
```

Which should output some information about the job that will run. Inside this information we can see the `job_id`, which we will use to get the results.

```json
{
  "model": {
    "identifier":"<model_id>",
    "version":"<model_version>",
    (...)
  },
  "status":"SUBMITTED",
  "totalInputs":1,
  "jobIdentifier":"<job_identifier>",
  (...)
  "team":{
    (...)
  },
  "user":{
  (...)
  },
  "jobInputs":{
    "identifier":["input"]
  },
  (...)
}
```

### Get the results

Once the job has finished, we can make a request agains Modzy again to see the results.

```bash
curl -X GET \
-H 'Authorization: ApiKey <api_key>' \
"https://integration.modzy.engineering/api/results/<job_id>"
```

And we will see the inference output.

```json
{
  "jobIdentifier": "<job_id>",
  "total": 1,
  "completed": 1,
  "failed": 0,
  "finished": true,
  (...)
  "results": {
    "input": {
      "status": "SUCCESSFUL",
      (...)
      "results.json": [{
        "data": {
          "result": {
            "classPredictions": [{
              "class": "4",
              "score": "1"
            }]
          },
          "explanation": null,
          "drift": null
        }
      }, {
        "data": {
          "result": {
            "classPredictions": [{
              "class": "8",
              "score": "1"
            }]
          },
          "explanation": null,
          "drift": null
        }
      }, {
        "data": {
          "result": {
            "classPredictions": [{
              "class": "8",
              "score": "1"
            }]
          },
          "explanation": null,
          "drift": null
        }
      }, {
        "data": {
          "result": {
            "classPredictions": [{
              "class": "4",
              "score": "1"
            }]
          },
          "explanation": null,
          "drift": null
        }
      }, {
        "data": {
          "result": {
            "classPredictions": [{
              "class": "8",
              "score": "1"
            }]
          },
          "explanation": null,
          "drift": null
        }
      }],
      "voting": {
        (...)
      }
    }
  }
}
```
