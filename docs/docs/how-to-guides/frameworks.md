# Building Containers for Common Machine Learning and Deep Learning Frameworks

If you build models using a common machine learning framework and you want a way to containerize them automatically, you have come to the right place! This page provides guides for leveraging Chassis to create containers out of your models built from the most popular ML frameworks available.

**NOTE**: This list of frameworks is *not* all-inclusive; instead, it is just a collection of examples from commonly-used frameworks we have seen data scientists gravitate towards. 

Can't find the framework you are looking for? Feel free to fork this repository, add an example or two from your framework of choice, and open a PR. Or come chat with us directly on [Discord](https://discord.gg/tdfXFY2y)!

!!! warning "Requirements"
    *To follow these how-to guides, you must first install the `chassisml` Python SDK and connect to the Chassis service either on your [local machine](../getting-started/deploy-manual.md) or to our [publicly-hosted](../getting-started/deploy-connect.md) instance within your Python IDE. You also will need an account with [Dockerhub](https://hub.docker.com/signup).* 
    
    For help getting started, visit our [Tutorials](https://chassis.ml/tutorials/devops-deploy/) page.

## PyTorch

This guide builds a simple Image Classification model with a ResNet50 architecture, avaialable directly in PyTorch's [Torvision model library](https://pytorch.org/vision/stable/models.html).

To follow along, you can reference the Jupyter notebook example and data files [here](https://github.com/modzy/chassis/blob/main/chassisml_sdk/examples/pytorch/pytorch_resnet50_image_classification.ipynb).

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

Next, define `process` function that will be passed as the input parameter to create a `ChassisModel` object.

```python
def process(input_bytes):
    
    # preprocess
    decoded = cv2.imdecode(np.frombuffer(input_bytes, np.uint8), -1)
    img_t = transform(decoded)
    batch_t = torch.unsqueeze(img_t, 0).to(device)
    
    # run inference
    predictions = model(batch_t)
    
    # postprocess
    percentage = torch.nn.functional.softmax(predictions, dim=1)[0]

    _, indices = torch.sort(predictions, descending=True)
    inference_result = {
        "classPredictions": [
            {"class": labels[idx.item()], "score": percentage[idx].item()}
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

Initialize Chassis Client and create Chassis model. Replace the URL with your Chassis connection. If you followed these [installation instructions](https://chassis.ml/tutorials/devops-deploy/), keep the local host URL as is, but if you are connected to the publicly-hosted Chassis instance, replace the URL with the URL you receive after [signing up](https://modzy.com/chassis-ml-sign-up/). 

```python
chassis_client = chassisml.ChassisClient("http://localhost:5000")
chassis_model = chassis_client.create_model(process_fn=process)
```

Test `chassis_model` locally.

```python
sample_filepath = './data/airplane.jpg'
results = chassis_model.test(sample_filepath)
print(results)
```

Before kicking off the Chassis job, we can test our `ChassisModel` in the environment that will be built within the container. **Note**: Chassis will infer the required packages, functions, or variables required to successfully run inference within the `process` function. This step ensures when the conda environment is created within the Docker container, your model will run.

**NOTE**: `test_env` function not available in [publicly-hosted](../getting-started/deploy-connect.md) service.

```python
test_env_result = chassis_model.test_env(sample_filepath)
print(test_env_result)
```

Lastly, publish your model with your Docker credentials.

```python
dockerhub_user = <my.username>
dockerhub_pass = <my.password>

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

This guide trains a Logistic Regression classifier on the [Digits Dataset](https://scikit-learn.org/stable/auto_examples/datasets/plot_digits_last_image.html) and auto-containerizes via the `chassisml` Python SDK. Visit the original classification exercise [here](https://scikit-learn.org/stable/auto_examples/exercises/plot_digits_classification_exercise.html#sphx-glr-auto-examples-exercises-plot-digits-classification-exercise-py).

To follow along, you can reference the Jupyter notebook example and data files [here](https://github.com/modzy/chassis/blob/main/chassisml_sdk/examples/sklearn/sklearn_logreg_image_classification.ipynb).

Import required dependencies.

```python
import chassisml
import numpy as np
import getpass
import json
from sklearn.linear_model import LogisticRegression
from sklearn import datasets
```

Load dataset, perform data preprocessing, and train the model.

```python
# Import and normalize data
X_digits, y_digits = datasets.load_digits(return_X_y=True)
X_digits = X_digits / X_digits.max()

n_samples = len(X_digits)

# Split data into training and test sets
X_train = X_digits[: int(0.9 * n_samples)]
y_train = y_digits[: int(0.9 * n_samples)]
X_test = X_digits[int(0.9 * n_samples) :]
y_test = y_digits[int(0.9 * n_samples) :]

# Train Model
logistic = LogisticRegression(max_iter=1000)
print(
    "LogisticRegression mean accuracy score: %f"
    % logistic.fit(X_train, y_train).score(X_test, y_test)
)

# Save small sample input to use for testing later
sample = X_test[:5].tolist()
with open("data/digits_sample.json", 'w') as out:
    json.dump(sample, out)
```

Next, prepare a `process` function that will be passed as the input parameter to create a `ChassisModel` object.

```python
def process(input_bytes):
    inputs = np.array(json.loads(input_bytes))
    inference_results = logistic.predict(inputs)
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

Initialize Chassis Client and create Chassis model. Replace the URL with your Chassis connection. If you followed these [installation instructions](https://chassis.ml/tutorials/devops-deploy/), keep the local host URL as is, but if you are connected to the publicly-hosted Chassis instance, replace the URL with the URL you receive after [signing up](https://modzy.com/chassis-ml-sign-up/). 

```python
chassis_client = chassisml.ChassisClient("http://localhost:5000")
chassis_model = chassis_client.create_model(process_fn=process)
```

Test `chassis_model` locally.

```python
sample_filepath = './data/digits_sample.json'
results = chassis_model.test(sample_filepath)
print(results)
```

Manually construct a conda environment to pass through as parameter to Chassis job. **NOTE:** By default, Chassis will infer all required dependencies, objects, and functions based on what is referenced within the `process` method. However, if you prefer to manually define your environment, you can do so as well.

```python
env = {
    "name": "sklearn-chassis",
    "channels": ['conda-forge'],
    "dependencies": [
        "python=3.8.5",
        {
            "pip": [
                "scikit-learn",
                "numpy",
                "chassisml"
            ] 
        }
    ]
}
```

Before kicking off the Chassis job, we can test our `ChassisModel` in the environment that will be built within the container. **Note**: Chassis will infer the required packages, functions, or variables required to successfully run inference within the `process` function. This step ensures when the conda environment is created within the Docker container, your model will run.

**NOTE**: `test_env` function not available in [publicly-hosted](../getting-started/deploy-connect.md) service.

```python
test_env_result = chassis_model.test_env(sample_filepath)
print(test_env_result)
```

Lastly, publish your model with your Docker credentials.

```python
dockerhub_user = <my.username>
dockerhub_pass = <my.password>

response = chassis_model.publish(
    model_name="Sklearn Logistic Regression Digits Image Classification",
    model_version="0.0.1",
    registry_user=dockerhub_user,
    registry_pass=dockerhub_pass,
    conda_env=env
)

job_id = response.get('job_id')
final_status = chassis_client.block_until_complete(job_id)
```
## XGBoost

This guide trains an XGBoost regression model that predicts housing prices based on a series of features in the [Boston Housing tabular dataset](https://www.kaggle.com/prasadperera/the-boston-housing-dataset). 

To follow along, you can reference the Jupyter notebook example and data files [here](https://github.com/modzy/chassis/blob/main/chassisml_sdk/examples/xgboost/xgboost_house_price_predictions.ipynb).

Import required dependencies.

```python
import cv2
import chassisml
from io import StringIO
import numpy as np
import pandas as pd
import getpass
import json
import xgboost as xgb
from sklearn.datasets import load_boston
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
```

Load dataset, build XGBoost regressor model, and train the model.

```python
# load data
boston = load_boston()
X = pd.DataFrame(boston.data, columns=boston.feature_names)
y = pd.Series(boston.target)
X_train, X_test, y_train, y_test = train_test_split(X, y)

# save sample data for testing later
with open("data/sample_house_data.csv", "w") as f:
    X_test[:10].to_csv(f, index=False)

# build XGBoost regressor
regressor = xgb.XGBRegressor(
    n_estimators=100,
    reg_lambda=1,
    gamma=0,
    max_depth=3
)

# train model
regressor.fit(X_train, y_train)
```

The `fit()` execution will print the following in your notebook:
```
XGBRegressor(base_score=0.5, booster='gbtree', colsample_bylevel=1,
             colsample_bynode=1, colsample_bytree=1, enable_categorical=False,
             gamma=0, gpu_id=-1, importance_type=None,
             interaction_constraints='', learning_rate=0.300000012,
             max_delta_step=0, max_depth=3, min_child_weight=1, missing=nan,
             monotone_constraints='()', n_estimators=100, n_jobs=12,
             num_parallel_tree=1, predictor='auto', random_state=0, reg_alpha=0,
             reg_lambda=1, scale_pos_weight=1, subsample=1, tree_method='exact',
             validate_parameters=1, verbosity=None)
```

Run inference on your `X_test` subset and evaluate model performance.

```python
# run inference
y_pred = regressor.predict(X_test)
# evaluate model
mean_squared_error(y_test, y_pred)
>>>> 7.658965947061991
```

Next, prepare a `process` function that will be passed as the input parameter to create a `ChassisModel` object.

```python
def process(input_bytes):
    # load data
    inputs = pd.read_csv(StringIO(str(input_bytes, "utf-8")))    
    
    # run inference
    preds = regressor.predict(inputs)
    
    # structure results
    inference_result = {
        "housePricePredictions": [
            {"row": i+1, "price": preds[i].round(0)*1000} for i in range(len(preds))
        ]
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

Initialize Chassis Client and create Chassis model. Replace the URL with your Chassis connection. If you followed these [installation instructions](https://chassis.ml/tutorials/devops-deploy/), keep the local host URL as is, but if you are connected to the publicly-hosted Chassis instance, replace the URL with the URL you receive after [signing up](https://modzy.com/chassis-ml-sign-up/). 

```python
chassis_client = chassisml.ChassisClient("http://localhost:5000")
chassis_model = chassis_client.create_model(process_fn=process)
```

Test `chassis_model` locally.

```python
sample_filepath = './data/sample_house_data.csv'
results = chassis_model.test(sample_filepath)
print(results)
```

Before kicking off the Chassis job, we can test our `ChassisModel` in the environment that will be built within the container. **Note**: Chassis will infer the required packages, functions, or variables required to successfully run inference within the `process` function. This step ensures when the conda environment is created within the Docker container, your model will successfully run.

**NOTE**: `test_env` function not available in [publicly-hosted](../getting-started/deploy-connect.md) service.

```python
test_env_result = chassis_model.test_env(sample_filepath)
print(test_env_result)
```

Lastly, publish your model with your Docker credentials.

```python
dockerhub_user = <my.username>
dockerhub_pass = <my.password>

response = chassis_model.publish(
    model_name="XGBoost Boston Housing Price Predictions",
    model_version="0.0.1",
    registry_user=dockerhub_user,
    registry_pass=dockerhub_pass,
)

job_id = response.get('job_id')
final_status = chassis_client.block_until_complete(job_id)
```
## LightGBM

This guide builds a LightGBM classifier model to predict the likelihood of women being diagnosed with Breast Cancer. This guide was adapted from this [Kaggle notebook](https://www.kaggle.com/prashant111/lightgbm-classifier-in-python). 

To follow along, you can reference the Jupyter notebook example and data files [here](https://github.com/modzy/chassis/blob/main/chassisml_sdk/examples/lightgbm/lightgbm_classification.ipynb).

Import required dependencies.

```python
import chassisml
import numpy as np
import getpass
import json
import pandas as pd
from io import StringIO
import lightgbm as lgb
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
```

Load dataset, perform data preprocessing, build and then train LightGBM classifier model.

```python
# load breast cancer dataset
df = pd.read_csv('./data/Breast_cancer_data.csv')

# preprocess data
X = df[['mean_radius','mean_texture','mean_perimeter','mean_area','mean_smoothness']]
y = df['diagnosis']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state = 0)

# build and train model
clf = lgb.LGBMClassifier()
clf.fit(X_train, y_train)
```

Run inference on your test subset and evaluate model accuracy
```python
y_pred=clf.predict(X_test)
accuracy=accuracy_score(y_pred, y_test)
print('LightGBM Model accuracy score: {0:0.4f}'.format(accuracy_score(y_test, y_pred)))
```

You should see this in your console:
```
LightGBM Model accuracy score: 0.9298
```

Next, prepare a `process` function that will be passed as the input parameter to create a `ChassisModel` object.

```python
labels = ["No Cancer", "Cancer"]
def process(input_bytes):
    inputs = pd.read_csv(StringIO(str(input_bytes, "utf-8")))
    preds = clf.predict_proba(inputs)
    
    inference_result = {
        "classPredictions": [
            {"row": i+1, "class": labels[np.argmax(pred)], "score": np.max(pred)} for i, pred in enumerate(preds)
        ]
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

Initialize Chassis Client and create Chassis model. Replace the URL with your Chassis connection. If you followed these [installation instructions](https://chassis.ml/tutorials/devops-deploy/), keep the local host URL as is, but if you are connected to the publicly-hosted Chassis instance, replace the URL with the URL you receive after [signing up](https://modzy.com/chassis-ml-sign-up/). 

```python
chassis_client = chassisml.ChassisClient("http://localhost:5000")
chassis_model = chassis_client.create_model(process_fn=process)
```

Test `chassis_model` locally.

```python
sample_filepath = 'data/sample_cancer_data.csv'
results = chassis_model.test(sample_filepath)
print(results)
```

Before kicking off the Chassis job, we can test our `ChassisModel` in the environment that will be built within the container. **Note**: Chassis will infer the required packages, functions, or variables required to successfully run inference within the `process` function. This step ensures when the conda environment is created within the Docker container, your model will successfully run.

**NOTE**: `test_env` function not available in [publicly-hosted](../getting-started/deploy-connect.md) service.

```python
test_env_result = chassis_model.test_env(sample_filepath)
print(test_env_result)
```

Lastly, publish your model with your Docker credentials.

```python
dockerhub_user = <my.username>
dockerhub_pass = <my.password>

response = chassis_model.publish(
    model_name="Chassis LightGBM Breast Cancer Classification",
    model_version="0.0.1",
    registry_user=dockerhub_user,
    registry_pass=dockerhub_pass,
)

job_id = response.get('job_id')
final_status = chassis_client.block_until_complete(job_id)
```
## Fastai

This builds off Fastai's [Tabular training tutorial](https://docs.fast.ai/tutorial.tabular.html), which predicts the income of adults based on various education and socioeconomic factors.  

To follow along, you can reference the Jupyter notebook example and data files [here](https://github.com/modzy/chassis/blob/main/chassisml_sdk/examples/fastai/fastai_tabular_training.ipynb).

Import required dependencies.

```python
import os
import chassisml
import numpy as np
import getpass
import json
import pandas as pd
from io import StringIO
from fastai.tabular.all import TabularDataLoaders, RandomSplitter, TabularPandas, tabular_learner, Categorify, FillMissing, Normalize, range_of, accuracy
```

Begin by loading and preprocessing dataset. 

```python
df = pd.read_csv("./data/adult_sample/adult.csv")
df.head()

dls = TabularDataLoaders.from_csv("./data/adult_sample/adult.csv", path=os.path.join(os.getcwd(), "data/adult_sample"), y_names="salary",
    cat_names = ['workclass', 'education', 'marital-status', 'occupation', 'relationship', 'race'],
    cont_names = ['age', 'fnlwgt', 'education-num'],
    procs = [Categorify, FillMissing, Normalize])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state = 0)

splits = RandomSplitter(valid_pct=0.2)(range_of(df))
to = TabularPandas(df, procs=[Categorify, FillMissing,Normalize],
                   cat_names = ['workclass', 'education', 'marital-status', 'occupation', 'relationship', 'race'],
                   cont_names = ['age', 'fnlwgt', 'education-num'],
                   y_names='salary',
                   splits=splits)

# save test subset
test_df = df.copy()
test_df.drop(['salary'], axis=1, inplace=True)
test_df[:20].to_csv("./data/sample_adult_data.csv", index=False)

# rebuild dataloaders with preprocessed data
dls = to.dataloaders(bs=64)
```

Now, we will build and train our model.

```python
learn = tabular_learner(dls, metrics=accuracy)
learn.fit_one_cycle(1)
```

The output of this training experiment should look similar to the following table:

| epoch | train_loss | valid_loss | accuracy | time |
| ----- | ---------- | ---------- | -------- | ---- |
| 0     | 0.370123   | 0.364591   | 0.832002 | 00:03| 

View the full results of the training experiment.

```python
learn.show_results()
```

Now, we will test the inference flow that works with the Fastai framework.

```python
test_df = pd.read_csv("./data/sample_adult_data.csv")
dl = learn.dls.test_dl(test_df)
preds = learn.get_preds(dl=dl)[0].numpy()
```

Next, prepare a `process` function that will be passed as the input parameter to create a `ChassisModel` object.

```python
labels = ['<50k', '>50k']
def process(input_bytes):
    inputs = pd.read_csv(StringIO(str(input_bytes, "utf-8")))
    dl = learn.dls.test_dl(inputs)
    preds = learn.get_preds(dl=dl)[0].numpy()
    
    inference_result = {
        "classPredictions": [
            {
                "row": i+1,
                "predictions": [
                    {"class": labels[j], "score": round(pred[j], 4)} for j in range(2)
                ]
            } for i, pred in enumerate(preds)
        ]
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

Initialize Chassis Client and create Chassis model. Replace the URL with your Chassis connection. If you followed these [installation instructions](https://chassis.ml/tutorials/devops-deploy/), keep the local host URL as is, but if you are connected to the publicly-hosted Chassis instance, replace the URL with the URL you receive after [signing up](https://modzy.com/chassis-ml-sign-up/). 

```python
chassis_client = chassisml.ChassisClient("http://localhost:5000")
chassis_model = chassis_client.create_model(process_fn=process)
```

Test `chassis_model` locally.

```python
sample_filepath = './data/sample_adult_data.csv'
results = chassis_model.test(sample_filepath)
print(results)
```

Before kicking off the Chassis job, we can test our `ChassisModel` in the environment that will be built within the container. **Note**: Chassis will infer the required packages, functions, or variables required to successfully run inference within the `process` function. This step ensures when the conda environment is created within the Docker container, your model will successfully run.

**NOTE**: `test_env` function not available in [publicly-hosted](../getting-started/deploy-connect.md) service.

```python
test_env_result = chassis_model.test_env(sample_filepath)
print(test_env_result)
```

Lastly, publish your model with your Docker credentials.

```python
dockerhub_user = <my.username>
dockerhub_pass = <my.password>

response = chassis_model.publish(
    model_name="Fast AI Salary Prediction",
    model_version="0.0.1",
    registry_user=dockerhub_user,
    registry_pass=dockerhub_pass,
)

job_id = response.get('job_id')
final_status = chassis_client.block_until_complete(job_id)
```
## MXNet

This guide leverages the [MXNet framework](https://mxnet.apache.org/versions/1.9.0/) to build a simple Image Classification model with a MobileNet architecture, avaialable directly in MXNet's [Gluon Model Zoo](https://mxnet.apache.org/api/python/docs/api/gluon/model_zoo/index.html). This guide is an adaptation of MXNet's [tutorial](https://mxnet.apache.org/versions/1.6/api/python/docs/tutorials/packages/gluon/image/pretrained_models.html#Loading-the-model) for using pretrained models. 

To follow along, you can reference the Jupyter notebook example and data files [here](https://github.com/modzy/chassis/blob/main/chassisml_sdk/examples/mxnet/mxnet_mobilenet_image_classification.ipynb).

Import required dependencies.

```python
import cv2
import chassisml
import numpy as np
import getpass
import json
import mxnet as mx
import mxnet.image as mxnet_img
from mxnet import gluon, nd
from mxnet.gluon.model_zoo import vision
import matplotlib.pyplot as plt
```

Load pretrained `MobileNet` model from [Gluon Model Zoo](https://mxnet.apache.org/api/python/docs/api/gluon/model_zoo/index.html)

```python
ctx = mx.cpu()
mobileNet = vision.mobilenet0_5(pretrained=True, ctx=ctx)
```

Next, load ImageNet labels file and sample dog image for testing. We will visualize this image in our notebook for reference.

```python
# load imagenet labels for postprocessing
imagenet_labels = np.array(json.load(open('data/image_net_labels.json', 'r')))
print(imagenet_labels[4])

# load sample image
filename = "data/dog.jpg"

# visualize image to test
image = mx.image.imread(filename)
plt.imshow(image.asnumpy())
```

An image of a boxer dog should appear under this cell.

Now, we will define an inference method specific to the MXNet framework.

```python
def predict(model, image, categories, k=3):
    predictions = model(transform(image)).softmax()
    top_pred = predictions.topk(k=k)[0].asnumpy()
    probs = []
    labels = []
    for index in top_pred:
        probability = predictions[0][int(index)]
        probs.append(probability.asscalar())
        category = categories[int(index)]
        labels.append(category)
    
    return probs, labels
```

Test this function locally to ensure your model is behaving how you intend it to.

```python
# test model
probs, labels = predict(mobileNet, image, imagenet_labels, 3)
print(probs)
print(labels)
>>> [0.84015656, 0.13626784, 0.006610237]
>>> ['boxer', 'bull mastiff', 'Rhodesian ridgeback']
```

Next, define `process` function that will be passed as the input parameter to create a `ChassisModel` object.

```python
def process(input_bytes):
    # read image bytes
    img = mxnet_img.imdecode(input_bytes)
    
    # run inference
    probs, labels = predict(mobileNet, img, imagenet_labels, 3)
    
    # structure results
    inference_result = {
        "classPredictions": [
            {"class": labels[i], "score": probs[i]}
        for i in range(len(probs)) ]
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

Initialize Chassis Client and create Chassis model. Replace the URL with your Chassis connection. If you followed these [installation instructions](https://chassis.ml/tutorials/devops-deploy/), keep the local host URL as is, but if you are connected to the publicly-hosted Chassis instance, replace the URL with the URL you receive after [signing up](https://modzy.com/chassis-ml-sign-up/). 

```python
chassis_client = chassisml.ChassisClient("http://localhost:5000")
chassis_model = chassis_client.create_model(process_fn=process)
```

Test `chassis_model` locally.

```python
sample_filepath = './data/dog.jpg'
results = chassis_model.test(sample_filepath)
print(results)
```

Before kicking off the Chassis job, we can test our `ChassisModel` in the environment that will be built within the container. **Note**: Chassis will infer the required packages, functions, or variables required to successfully run inference within the `process` function. This step ensures when the conda environment is created within the Docker container, your model will run.

**NOTE**: `test_env` function not available in [publicly-hosted](../getting-started/deploy-connect.md) service.

```python
test_env_result = chassis_model.test_env(sample_filepath)
print(test_env_result)
```

Lastly, publish your model with your Docker credentials.

```python
dockerhub_user = <my.username>
dockerhub_pass = <my.password>

response = chassis_model.publish(
    model_name="MXNET MobileNet Image Classifiction",
    model_version="0.0.1",
    registry_user=dockerhub_user,
    registry_pass=dockerhub_pass,
)

job_id = response.get('job_id')
final_status = chassis_client.block_until_complete(job_id)
```
## ONNX

This guide leverages the `chassisml` SDK to auto-containerize a pretrained model from the [ONNX Model Zoo](https://github.com/onnx/models/tree/main/vision/classification/mobilenet). 

To follow along, you can reference the Jupyter notebook example and data files [here](https://github.com/modzy/chassis/blob/main/chassisml_sdk/examples/onnx/onnx_mobilenet_image_classification.ipynb).

Import required dependencies.

```python
import cv2
import pickle
import tempfile
import chassisml
import numpy as np
import getpass
from shutil import rmtree
import json
import onnx
from onnx import backend
from onnx import numpy_helper
import onnxruntime as ort
import matplotlib.pyplot as plt
```

Load pretrained `MobileNet` model from [ONNX Model Zoo](https://github.com/onnx/models/tree/main/vision/classification/mobilenet) and confirm it is a valid ONNX model.

```python
model = onnx.load("models/mobilenetv2-7.onnx")
onnx.checker.check_model(model)
```

Next, load sample data and execute a few minor preprocessing steps.

```python
# format sample data and reshape
img = cv2.cvtColor(cv2.imread('data/dog.jpg'), cv2.COLOR_BGR2RGB)
img_show = cv2.resize(img, (224,224))

sample_img = np.reshape(img_show, (1,3,224,224)).astype(np.float32)

# load imagenet labels
labels = pickle.load(open('./data/imagenet_labels.pkl','rb'))

# visualize image
plt.figure()
plt.imshow(img)
plt.colorbar()
plt.grid(False)
plt.show()
```

An image of a yellow lab dog should appear under this cell.

Now, we will create an ONNX runtime inference session and test our model locally. **NOTE:** Some frameworks have their own ONNX runtime compatibility built in, but ONNX Runtime (ORT) can be used to run models built in many common frameworks - including PyTorch, Tensorflow, TFLite, Scikit-Learn, to name a few - but saved in the standardized ONNX format. 

```python
# create onnx runtime inference session and print top prediction
session = ort.InferenceSession("models/mobilenetv2-7.onnx")
results = session.run(None, {"input": sample_img})
print("Top Prediction: {}".format(labels[results[0].argmax()]))
>>> "Top Prediction: sunglass"
```

Next, define `process` function that will be passed as the input parameter to create a `ChassisModel` object. One strict requirement to use Chassis is that your model *must* be able to be loaded into memory and perform an inference call from it's loaded, pre-trained state. Due to the unique ORT syntax that requires a *model file* be passed through as a parameter when creating an ORT inference session (which means it must be loaded to memory as a part of the inference session instantiation, not loaded before), we will get a little creative and leverage Python's [tempfile](https://docs.python.org/3/library/tempfile.html) library to take the loaded model, save it to a temporary directory as a `.onnx` file, and load it back in during inference.  

```python
def process(input_bytes):
    # save model to filepath for inference
    tmp_dir = tempfile.mkdtemp()
    import onnx
    onnx.save(model, "{}/model.onnx".format(tmp_dir))
    
    # preprocess data
    decoded = cv2.cvtColor(cv2.imdecode(np.frombuffer(input_bytes, np.uint8), -1), cv2.COLOR_BGR2RGB)
    img = cv2.resize(decoded, (224,224))
    img = np.reshape(img, (1,3,224,224)).astype(np.float32)
    
    # run inference
    session = ort.InferenceSession("{}/model.onnx".format(tmp_dir))
    results = session.run(None, {"input": img})
    
    # postprocess
    inference_result = labels[results[0].argmax()]
    
    # format results
    structured_result = {
        "data": {
            "result": {"classPredictions": [{"class": str(inference_result)}]}
        }
    }
    
    # remove temp directory
    rmtree(tmp_dir)
    return structured_result
```

Initialize Chassis Client and create Chassis model. Replace the URL with your Chassis connection. If you followed these [installation instructions](https://chassis.ml/tutorials/devops-deploy/), keep the local host URL as is, but if you are connected to the publicly-hosted Chassis instance, replace the URL with the URL you receive after [signing up](https://modzy.com/chassis-ml-sign-up/). 

```python
chassis_client = chassisml.ChassisClient("http://localhost:5000")
chassis_model = chassis_client.create_model(process_fn=process)
```

Test `chassis_model` locally.

```python
sample_filepath = './data/dog.jpg'
results = chassis_model.test(sample_filepath)
print(results)
```

Before kicking off the Chassis job, we can test our `ChassisModel` in the environment that will be built within the container. **Note**: Chassis will infer the required packages, functions, or variables required to successfully run inference within the `process` function. This step ensures when the conda environment is created within the Docker container, your model will run.

**NOTE**: `test_env` function not available in [publicly-hosted](../getting-started/deploy-connect.md) service.

```python
test_env_result = chassis_model.test_env(sample_filepath)
print(test_env_result)
```

Lastly, publish your model with your Docker credentials.

```python
dockerhub_user = <my.username>
dockerhub_pass = <my.password>

response = chassis_model.publish(
    model_name="ONNX MobileNet Image Classifiction",
    model_version="0.0.1",
    registry_user=dockerhub_user,
    registry_pass=dockerhub_pass,
)

job_id = response.get('job_id')
final_status = chassis_client.block_until_complete(job_id)
```
## PMML

Predictive Model Markup Language (PMML) is an XML-based model format that is widely accepted and used to save machine learning models. This guide leverages the `chassisml` SDK to auto-containerize a pretrained model from this [PMML Scikit-Learn package model library](https://github.com/iamDecode/sklearn-pmml-model/tree/master/models). 

To follow along, you can reference the Jupyter notebook example and data files [here](https://github.com/modzy/chassis/blob/main/chassisml_sdk/examples/pmml/pmml_iris_forest_classification.ipynb).

Import required dependencies.

```python
import chassisml
import numpy as np
import getpass
import json
from io import StringIO
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
from sklearn_pmml_model.ensemble import PMMLForestClassifier
```

First, load and preprocess training data.
```python
# Prepare data
iris = load_iris()
X = pd.DataFrame(iris.data)
X.columns = np.array(iris.feature_names)
y = pd.Series(np.array(iris.target_names)[iris.target])
y.name = "Class"
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.33, random_state=123)

# Create sample data for testing later
with open("data/sample_iris.csv", "w") as f:
    Xte[:10].to_csv(f, index=False)
```

Next, load the `.pmml` model file with the `sklearn_pmml` convenience package. We can then run a sample inference test with our test subset. 

```python
# Load model
clf = PMMLForestClassifier(pmml="models/randomForest.pmml")
labels = clf.classes_.tolist()

# Test model
clf.predict(Xte)
clf.score(Xte, yte)
```

Now, we will define some pre- and post-processing methods that our model can use during inference.

```python
def preprocess_inputs(raw_input_bytes):
    # load data
    inputs = pd.read_csv(StringIO(str(raw_input_bytes, "utf-8")))
    return inputs

def postprocess_outputs(raw_predictions):
    # process output
    inference_result = {
        "result":[
            {
                "row": i+1,
                "classPredictions": [
                    {"class": labels[idx], "score": results[idx]}
                    for idx in np.argsort(results)[::-1]
                ]  
            } for i, results in enumerate(raw_predictions)
        ] 

    }    
    
    
    # format output
    structured_output = {
        "data": {
            "result": inference_result["result"],
            "explanation": None,
            "drift": None,
        }
    }
    
    return structured_output
```

Next, define `process` function that will be passed as the input parameter to create a `ChassisModel` object. 

```python
def process(input_bytes):
    # load data
    inputs = preprocess_inputs(input_bytes)
    # make predictions
    output = clf.predict_proba(inputs)
    # process output
    structured_output = postprocess_outputs(output)
    return structured_output
```

Initialize Chassis Client and create Chassis model. Replace the URL with your Chassis connection. If you followed these [installation instructions](https://chassis.ml/tutorials/devops-deploy/), keep the local host URL as is, but if you are connected to the publicly-hosted Chassis instance, replace the URL with the URL you receive after [signing up](https://modzy.com/chassis-ml-sign-up/). 

```python
chassis_client = chassisml.ChassisClient("http://localhost:5000")
chassis_model = chassis_client.create_model(process_fn=process)
```

Test `chassis_model` locally.

```python
sample_filepath = './data/sample_iris.csv'
results = chassis_model.test(sample_filepath)
print(results)
```

Before kicking off the Chassis job, we can test our `ChassisModel` in the environment that will be built within the container. **Note**: Chassis will infer the required packages, functions, or variables required to successfully run inference within the `process` function. This step ensures when the conda environment is created within the Docker container, your model will run.

**NOTE**: `test_env` function not available in [publicly-hosted](../getting-started/deploy-connect.md) service.

```python
test_env_result = chassis_model.test_env(sample_filepath)
print(test_env_result)
```

Lastly, publish your model with your Docker credentials.

```python
dockerhub_user = <my.username>
dockerhub_pass = <my.password>

response = chassis_model.publish(
    model_name="PMML Random Forest Iris Classification",
    model_version="0.0.1",
    registry_user=dockerhub_user,
    registry_pass=dockerhub_pass,
)

job_id = response.get('job_id')
final_status = chassis_client.block_until_complete(job_id)
```
## Tensorflow & Keras

*Coming Soon*
## Spacy

*Coming Soon*
## Spark MLlib

*Coming Soon*
