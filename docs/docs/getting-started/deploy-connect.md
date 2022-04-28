# Connect to Hosted Service

!!! success "Welcome!"
     Connecting to this service eliminates the need for you to manually deploy and stand up a private Kubernetes cluster. We take care of that for you! This page will allow you to quickly connect and begin containerizing your models right away.  

## Download Chassis SDK

## Get Chassis Connection URL

**[Sign up](https://chassis.modzy.com)** for the publicly-hosted service.

Next, when you receive your connection link, use the URL and `ChassisClient` object to establish connection to the running service. The information you receive will look something like this:

## Example Code

```python
chassis_client = chassisml.ChassisClient("https://chassis-xxxxxxxxxx.modzy.com")
```

## Begin Using the Service

TODO: add in notebook

Congratulations, you are all set to use the Chassis hosted service running on Google Cloud. To get started, make sure you set up a Python virtual enviornment and install the `chassisml` SDK.

```bash
pip install chassisml
```

For more resources, check out our [tutorials](../tutorials/ds-connect.md) and [how-to guides](../how-to-guides/frameworks.md)
