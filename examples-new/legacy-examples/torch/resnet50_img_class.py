import time
import pickle
import cv2
import torch
import numpy as np
import torchvision.models as models
from torchvision import transforms

from chassis.builder import DockerBuilder
from chassisml import ChassisModel, ChassisClient

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


'''
Create Model
'''
# legacy way
# chassis_client = ChassisClient("https://chassis.app.modzy.com")
# chassis_model = chassis_client.create_model(process_fn=process)
# new way
chassis_model = ChassisModel(process_fn=process, legacy_predict_fn=True)

# add pip requirements
chassis_model.add_requirements(["https://download.pytorch.org/whl/torch/torch-2.0.0+cpu.cxx11.abi-cp39-cp39-linux_x86_64.whl", "torchvision", "opencv-python-headless", "numpy"])

# test model
sample_filepath = './data/airplane.jpg'
results = chassis_model.test(sample_filepath)
print(results)

# build container
builder = DockerBuilder(chassis_model,  "./tmp-dir")
start_time = time.time()
res = builder.build_image(name="bmunday131/torch-resnet-50-img-class-cpu", tag="0.0.2", show_logs=True)
end_time = time.time()
print(res)
print(f"Container image built in {round((end_time-start_time)/60, 5)} minutes")

