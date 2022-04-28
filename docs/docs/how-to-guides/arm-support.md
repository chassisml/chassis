# OS & Arm Support

AI/ML models, Docker containers, and processors - what are they, how do they work together, and why mention them in relation to Chassisml?

If you are familiar with the Chassisml service, you know that it is a tool Data Scientists can leverage to push their AI/ML models into a production application, without having any DevOps knowledge or experience. The way in which this happens is by auto-packaging model code into a Docker container, which allows the model to be shipped to various ModelOps/MLOps/Model serving platforms, across both the commercial and open-source landscapes. In most cases, these containers are built to run on *Intel* processors, which are more commonly found in larger devices such as desktop computers. This is great for running models in data centers or cloud-based infrastructure, but it does not bode well for running these models on any sort of mobile or edge device.

*ARM* processors come in handy in these situations. As AI edge processing becomes more and more desirable (think AI running directly on a drone or security camera as an example), it is critical to be able to compile containers into an ARM-architecture supported format. 

This page walks through the process of automatically building a model container that can run on ARM, with the option to also make it GPU-compatible on an ARM architecture. 
## Enable Arm Support

To get started, we will install our required dependencies.

```python
import chassisml
import pickle
import cv2
import torch
import getpass
import numpy as np
import torchvision.models as models
from torchvision import transforms
```

Next, we will load the pretrained ResNet50 model, define a data transformation object, and define a `device` variable. This is how we cast both our model and data to the CPU (`device="cpu"`) or GPU (`device="cuda"`).

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
model.to(device)
```

Most deep learning frameworks have built-in support for batch processing. This support includes different dataloader functionalities that will take an entire folder of data in some cases and process it in a way that can be fed to a neural network in the proper tensor form. We will define a `batch_process` function that takes a *list* of inputs, formats them into the structure our model expects, and runs inference on the batch of data.

```python
def batch_process(inputs):
    
    # preprocess list of inputs
    images = []
    for input_bytes in inputs:
        decoded = cv2.imdecode(np.frombuffer(input_bytes, np.uint8), -1)
        resized = cv2.resize(decoded, (224, 224)).reshape((1,224,224,3))
        images.append(resized)
    images_arr = np.concatenate(images)
    batch_t = torch.stack(tuple(transform(i) for i in images_arr), dim=0).to(device)

    # run batch inference and add softmax layer
    output = model(batch_t)
    probs = torch.nn.functional.softmax(output, dim=1)
    softmax_preds = probs.detach().cpu().numpy()
    
    # postprocess
    all_formatted_results = []
    for preds in softmax_preds: 
        indices = np.argsort(preds)[::-1]
        classes = [labels[idx] for idx in indices[:5]]
        scores = [float(preds[idx]) for idx in indices[:5]]
        preds = [{"class": "{}".format(label), "score": round(float(score),3)} for label, score in zip(classes, scores)]
        preds.sort(key = lambda x: x["score"],reverse=True)
        results = {"classPredictions": preds}
        all_formatted_results.append(results)
    
    # output list of formatted results
    return all_formatted_results
```

When we create our `ChassisModel` object, we will pass this batch_process function through as a parameter. **NOTE:** If you would also like to define a `process` function that only performs inference on a single piece of data instead of batch, you can do so as well and pass both through as parameters. In this case, our `batch_process` will work if we pass through either a single piece of data or batch.

Now, initialize Chassis Client and create Chassis model. Replace the URL with your Chassis connection. If you followed these [installation instructions](https://chassis.ml/tutorials/devops-deploy/), keep the local host URL as is, but if you are connected to the Modzy-hosted Chassis instance, replace the URL with "https://chassis.modzy.com".

```python
chassis_client = chassisml.ChassisClient("http://localhost:5000")
chassis_model = chassis_client.create_model(batch_process_fn=batch_process,batch_size=4)
```

Test `chassis_model` locally (both single and batch data).

```python
sample_filepath = './data/airplane.jpg'
results = chassis_model.test(sample_filepath)
print(results)

results = chassis_model.test_batch(sample_filepath)
print(results)
```

Up until this point, creating a container that can run on ARM has been exactly the same as the normal Chassisml workflow. To enable ARM support, all we need to do is turn on the `arm64` flag.

Turn this flag on and publish our model with your specified Docker credentials.

```python
dockerhub_user = <my.username>
dockerhob_pass = <my.password>

response = chassis_model.publish(
    model_name="PyTorch ResNet50 Image Classification",
    model_version="0.0.1",
    registry_user=dockerhub_user,
    registry_pass=dockerhub_pass,
    arm64=True
)

job_id = response.get('job_id')
final_status = chassis_client.block_until_complete(job_id)
```

## Enable Arm + GPU Support

!!! info Note
    The ARM + GPU option is in *alpha* and has only been tested on the NVIDIA Jetson Nano device. 

Enabling ARM & GPU support requires one more flag set to true during the `publish` method. Repeate the steps outlined in the above section with the one difference being a slight change the `device` variable.

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

device = 'cuda'
model.to(device)
```

Next, publish your model with both the `arm64` and `gpu` flags turned on.

```python
dockerhub_user = <my.username>
dockerhob_pass = <my.password>

response = chassis_model.publish(
    model_name="PyTorch ResNet50 Image Classification",
    model_version="0.0.1",
    registry_user=dockerhub_user,
    registry_pass=dockerhub_pass,
    arm64=True,
    gpu=True
)

job_id = response.get('job_id')
final_status = chassis_client.block_until_complete(job_id)
```