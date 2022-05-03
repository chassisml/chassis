![Chassis logo](images/chassis-positive.png){: style="width:200px; margin-bottom:10px;" }

# Build ML Model Containers. Automatically.

Turn your machine learning models into portable container images that can run just about anywhere using Chassis. For a deeper dive and better understanding of what Chassis is, learn more [here](./conceptual-guides/overview.md).

<br>

| Easy to Connect | Requires Installation|
| :-----------: | :-----------: |
| Quickest and easiest way to start using Chassis. <br> No DevOps experience required. <br><br> *Preferred* <br><br> [Connect to Chassis Service    :material-connection:{ .icon-color }](./getting-started/deploy-connect.md){ .button-styling .primary-button } <br><br> |  More involved installation. <br> Requires a moderate understanding of <br> Kubernetes, Helm, and Docker. <br><br><br> [Install Chassis on Your Machine   :octicons-download-16:{ .icon-color }](./getting-started/deploy-manual.md){ .button-styling } <br><br> |

## How it Works

After connecting to the Chassis service, your workflow will involve a few simple steps: 

### Set Up Environment

Create your workspace environment, open a Jupyter Notebook or other Python editor, and install the Chassisml SDK.

```bash
pip install chassisml
``` 

### Load Your Model

Train your model or load your pre-trained model into memory (`.pth`, `.pkl`, `.h5`, `.joblib`, or other file format - all model types and formats are supported!).

```python
model = framework.load("path/to/model.file")
```

### Write Process Function

The `process` function will use your model to perform any required preprocessing and inference execution on the incoming `input_bytes` data. 

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

**NOTE**: Depending on how you connect to the service, you will need to identify the URL on which the service is running and can be accessed. If you are connecting to the publicly-hosted version, make sure to **[sign up](https://chassis.modzy.com)** to access this URL. Otherwise if you are deploying manually and connecting to a locally running instance, your URL will look something like *http://localhost:5000*.

Once you have this URL, replace ```<chassis-instance-url>``` in the below line with your URL.

``` py
chassis_client = chassisml.ChassisClient("<chassis-instance-url>")
chassis_model = chassis_client.create_model(process_fn=process)
```
### Publish Chassis Model

``` py
response = chassis_model.publish(
    model_name="Sample ML Model",
    model_version="0.0.1",
    registry_user=dockerhub_user,
    registry_pass=dockerhub_pass,
) 
```

### Run and Query Model

Run your model locally or on your preferred serving platform and begin making inference calls right away.


<div id="logos-container">
  <div class="logo-box1"><img src="images/docker.png" ></div>
  <div class="logo-box2"><img src="images/modzy.png" ></div>
  <div class="logo-box3"><img src="images/kserve.png" ></div>
  <div class="logo-box4"><img src="images/postman/postman-logo.png" ></div>
  <span class="stretch"></span>
</div>
<br>
