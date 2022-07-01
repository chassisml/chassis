# Connect to Hosted Service

!!! success "Welcome!"
     Connecting to this service eliminates the need for you to deploy and stand up a private Kubernetes cluster. Each chassis build job run on our hosted service has enough resources to containerize even the most memory intensive ML models (up to 8GB RAM and 2 CPUs). Follow the instructions on this page to connect and get started using Chassis right away.  

## Download Chassis SDK

To get started, make sure you set up a [Python virtual enviornment](https://realpython.com/what-is-pip/#using-pip-in-a-python-virtual-environment) and install the `chassisml` SDK.

```bash
pip install chassisml
```

## Get Chassis Connection URL

[Sign up](https://chassis.modzy.com){ .md-button .md-button--primary} for the publicly-hosted service.

Next, when you receive your connection link, use the URL and `ChassisClient` object to establish connection to the running service. The information you receive will look something like this:

```python
chassis_client = chassisml.ChassisClient("https://chassis-xxxxxxxxxx.modzy.com")
```

## Begin Using Chassis

With your environment set up and connection URL in hand, you can now start to integrate the service into your MLOps pipelines. 

Check out this [example](https://github.com/modzy/chassis/blob/main/chassisml_sdk/examples/sklearn/sklearn_svm_image_classification_public_hosted.ipynb) to follow along and see Chassis in action. Just insert your URL into the aforementioned client connection and you're well on your way. 
