<div align="center">

![chassis-banner-v1.2.png](https://github.com/modzy/chassis/blob/feat/readme-overhaul/chassis%20banner%20v1.2.png)

![GitHub contributors](https://img.shields.io/github/contributors/modzy/chassis?logo=GitHub&style=flat)
![GitHub last commit](https://img.shields.io/github/last-commit/modzy/chassis?logo=GitHub&style=flat)
![GitHub issues](https://img.shields.io/github/issues-raw/modzy/chassis?logo=github&style=flat)
![GitHub](https://img.shields.io/github/license/modzy/chassis?logo=apache&style=flat)

![GitHub Workflow Status](https://img.shields.io/github/workflow/status/modzy/chassis/CI?logo=github)
![PyPI](https://img.shields.io/pypi/v/chassisml?logo=pypi&style=flat)
![PyPI - Downloads](https://img.shields.io/pypi/dm/chassisml?logo=pypi&style=flat)

</div>

* **Simple service for model serving** 
* **Stores containers on Docker Hub** or your container registry of choice
* **Serve models with your favorite server** including Kubernets, Docker, Kserve, and Modzy


## Installation

### Use free public instance
Get started quickly by signing-up for a free publicly service at: https://www.modzy.com/chassis-ml-sign-up/

After signing up, you'll receive a URL to this free instance that looks something like

`https://chassis-xxxxxxxxxx.modzy.com`
## Usage/Examples

### Set Up Environment
Create your workspace environment, open a Jupyter Notebook or other Python editor, and install the Chassisml SDK.


```python
pip install chassisml
```

### Load Your Model
Train your model or load your pre-trained model into memory (`.pth`, `.pkl`, `.h5`, `.joblib`, or other file format - all model types and formats are supported!).
```python
model = framework.load("path/to/model.file")
```

### Write Process Function
The process function will use your model to perform any required preprocessing and inference execution on the incoming input_bytes data.

```python
def process(input_bytes):
  # preprocess
  data = preprocess(input_bytes)

  # run inference
  predictions = model.predict(data)

  # post process predictions
  formatted_results = postprocess(predictions)

  return formatted_results
```
### Initialize Client and Create Chassis Model

```python
chassis_client = chassisml.ChassisClient("<chassis-instance-url>")
chassis_model = chassis_client.create_model(process_fn=process)
```

### Publish Chassis Model
```python
response = chassis_model.publish(
    model_name="Sample ML Model",
    model_version="0.0.1",
    registry_user=dockerhub_user,
    registry_pass=dockerhub_pass,
) 
```

## Documentation

📘 [Full Docs](https://chassis.mln)

☁️ [Full Install Tutorial](https://chassis.ml/getting-started/deploy-manual/)

🧑‍🏫 [Model Deployment Tutorial](https://chassis.ml/tutorials/ds-connect/)


## Support

Join the `#chassisml` channel on [Modzy's Discord Server](https://discord.gg/eW4kHSm3Z5) where our maintainers meet to plan changes and improvements.

We also have a `#chassis-model-builder` Slack channel on the [MLOps.community Slack](https://go.mlops.community/slack)!


## Contributors

A full list of contributors, which includes individuals that have contributed entries, can be found [here](https://github.com/modzy/chassis/graphs/contributors).
