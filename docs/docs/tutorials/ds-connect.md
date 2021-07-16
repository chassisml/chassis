# How a Data Scientist connects to chassis and builds a model

In order to connect to `Chassis` service we are going to use the SDK. We will transform our model into MLFlow format and we will upload it by making a request. After that, the image that have been created will be uploaded to Docker Hub and we will be able to use it.

## Install the SDK

First step is to install the SDK using `pip`.

```bash
pip install chassisml
```

## Import required libraries



## XXX

First of all he needs to import the SDK.

```python
import chassis
```

Some variables are required to be able to build de docker image. In particular, we must define the name and version of the model and of course we must provide the path.

```python
image_data = {
    'name': 'sdk-test-sklearn',
    'version': '0.0.1',
    'model_name': 'digits',
    'model_path': '../../builder_service/test/sklearn/example_model',
}
```

## Create the image

The method `publish` makes a request against the service so that it starts to run the containerization process.

Some important fields must be defined. (XXX: this is going to change pretty much).

```python
res = chassis.publish(
    api_key=api_key,
    module=sklearn,
    image_data=image_data,
    deploy=False,
    image_type=chassis.Constants.IMAGE_GREY,
    base_url='http://url_of_the_service'
)
```

This variable `res` contains two values: `error` and `job_id`.

## Get the results

You can get the status of the job by making a request against the builder. This can be done using the SDK.

```python
job_id = res.get('job_id')
chassis.get_job_status(job_id)
```
