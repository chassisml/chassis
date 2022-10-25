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

<!-- JSDelivr -->
* <img height="16" width="16" src="https://cdn.jsdelivr.net/npm/simple-icons@v5/icons/opencontainersinitiative.svg" /> **Creates production ML container images for your models** that comply with OCI and OMI specs
* <img height="16" width="16" src="https://cdn.jsdelivr.net/npm/simple-icons@v5/icons/docker.svg" /> **Stores ML model containers on Docker Hub** or your container registry of choice
* <img height="16" width="16" src="https://cdn.jsdelivr.net/npm/simple-icons@v5/icons/grpc.svg" /> **Adds a gRPC API** for model serving on Kubernetes, Docker, Kserve, and/or Modzy


## Installing the service

### Use free public chassis service
Get started quickly by signing up for a free publicly-hosted service at: https://www.modzy.com/chassis-ml-sign-up/

After signing up, you'll receive a URL to this free instance that looks something like

`https://chassis-xxxxxxxxxx.modzy.com`

### Private installation
Full installation tutorial via <img height="16" width="16" src="https://cdn.jsdelivr.net/npm/simple-icons@v5/icons/docker.svg" /> Docker and <img height="16" width="16" src="https://cdn.jsdelivr.net/npm/simple-icons@v5/icons/helm.svg" /> HELM can be found here: https://chassis.ml/getting-started/deploy-manual/

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
The process function will use your model to perform any required preprocessing and inference execution on the incoming `input_bytes` data.

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

## Features
Chassis is a Kubernetes service that is accessible via a Python library that automatically converts Python code and ML models into production containers. Full feature list below:

- Creates "baked-in" container images for ML models
- Adds gRPC inference API to any ML model
- Saves model images to any container registry including Docker Hub
- Supports model serving on Kserve, Modzy, or Docker/K8s
- Supports CPUs and GPUs
- Optional GPU batch processing mode
- Supports Lime, SHAP explainability
- Cross-compiles to both ARM and x86
- [OCI](https://opencontainers.org) and [OMI](https://openmodel.ml) compliant

## Documentation

📘 [Full Docs](https://chassis.ml)

☁️ [Full Install Tutorial](https://chassis.ml/getting-started/deploy-manual/)

🧑‍🏫 [Model Packaging Tutorial](https://chassis.ml/tutorials/ds-connect/)

Framework-specific Guides:
|  |  |  |  |  |
|---|---|---|---|---|
| <!-- JSDelivr --> <img height="16" width="16" src="https://cdn.jsdelivr.net/npm/simple-icons@v5/icons/pytorch.svg" /> [Pytorch](https://chassis.ml/how-to-guides/frameworks/#pytorch) | <!-- JSDelivr --> <img height="16" width="16" src="https://cdn.jsdelivr.net/npm/simple-icons@v5/icons/scikitlearn.svg" /> [SciKit-Learn](https://chassis.ml/how-to-guides/frameworks/#scikit-learn) | <!-- JSDelivr --> <img height="16" width="16" src="https://cdn.jsdelivr.net/npm/simple-icons@v5/icons/onnx.svg" /> [ONNX](https://chassis.ml/how-to-guides/frameworks/#onnx) | <!-- JSDelivr --> <img height="16" width="16" src="https://cdn.jsdelivr.net/npm/simple-icons@v5/icons/keras.svg" />  [Keras](https://chassis.ml/how-to-guides/frameworks/#tensorflow-keras) | <!-- JSDelivr --> <img height="16" width="16" src="https://cdn.jsdelivr.net/npm/simple-icons@v5/icons/tensorflow.svg" />  [Tensorflow](https://chassis.ml/how-to-guides/frameworks/#tensorflow-keras) |
| [spaCy](https://chassis.ml/how-to-guides/frameworks/#spacy) | <!-- JSDelivr --> <img height="16" width="16" src="https://cdn.jsdelivr.net/npm/simple-icons@v5/icons/apachespark.svg" />  [Spark MLlib](https://chassis.ml/how-to-guides/frameworks/#spark-mllib) | [XGBoost](https://chassis.ml/how-to-guides/frameworks/#xgboost) | [LightGBM](https://chassis.ml/how-to-guides/frameworks/#lightgbm) | [Fastai](https://chassis.ml/how-to-guides/frameworks/#fastai) |
| [MXNet](https://chassis.ml/how-to-guides/frameworks/#mxnet) | [PMML](https://chassis.ml/how-to-guides/frameworks/#pmml) |  |  |  |

## Support

Join the `#chassisml` channel on [Modzy's Discord Server](https://discord.gg/eW4kHSm3Z5) where our maintainers meet to plan changes and improvements.

We also have a `#chassis-model-builder` Slack channel on the [MLOps.community Slack](https://go.mlops.community/slack)!


## Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->
