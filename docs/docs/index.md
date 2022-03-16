![Chassis logo](images/chassis-positive.png){: style="width:200px; margin-bottom:10px;" }

# Build ML Model Containers. Automatically.

Turn machine learning models into portable container images that can run just about anywhere.

After setting up your model environment, get started quickly by adding the Chassisml SDK.

```bash
pip install chassisml
```

### Load Your Model

```python
model = framework.load("path/to/model.file")
```

### Write Process Function

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

*NOTE: Initialize client by pointing to running Chassis instance*

``` py
chassis_client = chassisml.ChassisClient("http://localhost:5000")
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

*NOTE: Run your model locally or on your preferred serving platform and begin making inference calls right away.*


<div id="logos-container">
  <div class="logo-box1"><img src="images/docker.png" ></div>
  <div class="logo-box2"><img src="images/modzy.png" ></div>
  <div class="logo-box3"><img src="images/kserve.png" ></div>
  <div class="logo-box4"><img src="images/postman/postman-logo.png" ></div>
  <span class="stretch"></span>
</div>
<br>

### Try it Yourself

To start building your own ML containers, check out the [Deploy Chassis](tutorials/devops-deploy.md) tutorial to host an instance on a private k8s cluster.

*Coming Soon:* Publicly-hosted version of Chassis!

<br>
