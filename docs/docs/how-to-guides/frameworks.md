# Building Containers for Specific Frameworks

If you built your model using a common machine learning framework, you have come to the right place! This page provides tutorials for leveraging Chassis to create containers out of your models built from the most popular ML frameworks available.

**NOTE**: This list of frameworks is *not* all-inclusive; instead, it is just a collection of examples from commonly-used frameworks we have seen data scientists gravitate towards. 

Can't find the framework you are looking for? Feel free to fork this repository, add an example or two from your framework of choice, and open a PR. Or come chat with us directly on [Discord](https://discord.gg/tdfXFY2y)!

!!! Requirements
    *These tutorials assume you have already installed the `chassisml` Python SDK and have connected to the Chassis service either on your local machine or on chassis.modzy.com within your Python IDE. You also will need an account with [Dockerhub](https://hub.docker.com/signup).* 
    
    For help getting started, visit our [Tutorials](https://chassis.ml/tutorials/devops-deploy/) page.

## PyTorch

This tutorial builds a simple Image Classification model with a ResNet50 architecture, avaialable directly in PyTorch's [Torvision model library](https://pytorch.org/vision/stable/models.html).

To follow along, you can reference the Jupyter notebook example and data files [here](https://github.com/modzy/chassis/blob/main/chassisml-sdk/examples/pytorch/pytorch_resnet50_image_classification.ipynb).

Import required dependencies.

```python
import chassisml
import pickle
import cv2
import torch
import numpy as np
import torchvision.models as models
from torchvision import transforms
```

Load model, labels, and any other dependencies required for inference.

```python
model = models.resnet50(pretrained=True)
model.eval()

labels = pickle.load(open('./data/imagenet_labels.pkl','rb'))

transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])        

device = 'cpu'
```

Next, define `context` dictionary and `process` function that will be passed as input parameters to create a `ChassisModel` object.

```python
context = {
    "model": model,
    "labels": labels,
    "transform": transform,
    "device": device
}

def process(input_bytes,context):
    
    # preprocess
    decoded = cv2.imdecode(np.frombuffer(input_bytes, np.uint8), -1)
    img_t = context['transform'](decoded)
    batch_t = torch.unsqueeze(img_t, 0).to(device)
    
    # run inference
    predictions = context['model'](batch_t)
    
    # postprocess
    percentage = torch.nn.functional.softmax(predictions, dim=1)[0]

    _, indices = torch.sort(predictions, descending=True)
    inference_result = {
        "classPredictions": [
            {"class": context['labels'][idx.item()], "score": percentage[idx].item()}
        for idx in indices[0][:5] ]
    }

    structured_output = {
        "data": {
            "result": inference_result,
            "explanation": None,
            "drift": None,
        }
    }
    
    return structured_output
```

Initialize Chassis Client and create Chassis model. Replace the URL with your Chassis connection. If you followed these installation instructions, keep the local host URL as is, but if you are connected to the Modzy-hosted Chassis instance, replace the URL with "https://chassis.modzy.com". 

```python
chassis_client = chassisml.ChassisClient("http://localhost:5000")
chassis_model = chassis_client.create_model(context=context,process_fn=process)
```

Test `chassis_model` locally.

```python
sample_filepath = './data/airplane.jpg'
results = chassis_model.test(sample_filepath)
print(results)
```

Before kicking off the Chassis job, we can test our `ChassisModel` in the environment that will be built within the container. **Note**: Chassis will infer the required packages, functions, or variables required to successfully run inference within the `process` function. This step ensures when the conda environment is created within the Docker container, your model will run.

```python
test_env_result = chassis_model.test_env(sample_filepath)
print(test_env_result)
```

Lastly, publish your model with your Docker credentials.

```python
dockerhub_user = <my.username>
dockerhob_pass = <my.password>

response = chassis_model.publish(
    model_name="PyTorch ResNet50 Image Classification",
    model_version="0.0.1",
    registry_user=dockerhub_user,
    registry_pass=dockerhub_pass,
)

job_id = response.get('job_id')
final_status = chassis_client.block_until_complete(job_id)
```

## Scikit-learn

## XGBoost

## LightGBM

## Fastai

## MXNet

## ONNX

## PMML

## Tensorflow & Keras

*Coming Soon*

## Spacy

*Coming Soon*

## Spark MLlib

*Coming Soon*
