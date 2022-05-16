# Connect to Hosted Service

!!! success "Welcome!"
     Connecting to this service eliminates the need for you to manually deploy and stand up a private Kubernetes cluster. We take care of that for you! This page will allow you to connect and start using Chassis right away.  

## Download Chassis SDK

To get started, make sure you set up a [Python virtual enviornment](https://realpython.com/what-is-pip/#using-pip-in-a-python-virtual-environment) and install the `chassisml` SDK.

```bash
pip install chassisml
```

## Get Chassis Connection URL

**[Sign up](https://chassis.modzy.com)** for the publicly-hosted service.

Next, when you receive your connection link, use the URL and `ChassisClient` object to establish connection to the running service. The information you receive will look something like this:

```python
chassis_client = chassisml.ChassisClient("https://chassis-xxxxxxxxxx.modzy.com")
```

## Begin Using Chassis

With your environment set up and connection URL in hand, you can now start to integrate the service into your MLOps pipelines. 

Check out this [example](https://github.com/modzy/chassis/blob/main/chassisml_sdk/examples/sklearn/sklearn_svm_image_classification_public_hosted.ipynb) to follow along and see Chassis in action. Just insert your URL into the aforementioned client connection and you're well on your way. 
