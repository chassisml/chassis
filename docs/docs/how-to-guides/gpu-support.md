# GPU Support

Data scientists who spend most of their time building and training new machine learning models are likely familiar with two buzzwords that are often brought up when discussing the required resources needed to conduct such experiments: *Graphics Processing Unit (GPU)* and *batch processing*. GPUs are designed to quickly process large quantities of data concurrently and in turn makes the batch processing of data more efficient. This is pivotal process for not only model training, but also model inference.

If you are familiar with the Chassisml service, you will know that by default, Chassisml will automatically create containers that run on CPU. But what if there is a real need for *batch* inference in a production setting that processes significantly quicker running on a GPU? 

This page walks through the process of implementing both GPU and batch inference support.

To follow along, you can reference the Jupyter notebook example and data files [here](https://github.com/modzy/chassis/blob/main/chassisml-sdk/examples/pytorch/pytorch_resnet50_image_classification_batch_gpu.ipynb).

## Enable Batch Processing

Batch processing goes hand in hand with GPU support. Enabling GPU support does accerate the model inferences execution, but to truly unlock the full potential of a GPU, batch processing is critical. So, we will build a simple Image Classification model with a ResNet50 architecture, avaialable directly in PyTorch's [Torvision model library](https://pytorch.org/vision/stable/models.html), and implement a batch processing function that takes advantage of GPU access.

!!! Note
    To add this support, you *must* have access to a GPU to test locally before submitting a Chassisml job. Most Python ML frameworks will also require you to set up [CUDA](https://developer.nvidia.com/cuda-toolkit) on your machine.  

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

Next, we will load the pretrained ResNet50 model, define a data transformation object, and define a `device` variable (this is how we cast both our model and data to the GPU).

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

##Enable GPU Support

Up until this point, creating a container that can run on GPU has been *very* similar to the normal Chassisml workflow, with the one difference being the need to define a `batch_process_fn` method. The last procedural difference is a simple flag to turn on GPU support.

Turn this flag on and publish our model with your specified Docker credentials.


```python
dockerhub_user = <my.username>
dockerhob_pass = <my.password>

response = chassis_model.publish(
    model_name="PyTorch ResNet50 Image Classification",
    model_version="0.0.1",
    registry_user=dockerhub_user,
    registry_pass=dockerhub_pass,
    gpu=True
)

job_id = response.get('job_id')
final_status = chassis_client.block_until_complete(job_id)
```

