import time
import io
import json
import torch
from PIL import Image
from typing import Mapping, Dict
from torchvision.models import resnet50, ResNet50_Weights

from chassisml import ChassisModel
from chassis.builder import DockerBuilder

# load and initialize model with the best available weights
weights = ResNet50_Weights.DEFAULT
model = resnet50(weights=weights)
model.eval()

# define the inference transforms
preprocess = weights.transforms()

def predict(inputs: Mapping[str, bytes]) -> Dict[str, bytes]:
    
    # preprocess
    decoded = Image.open(io.BytesIO(inputs['image'])).convert("RGB")
    batch = preprocess(decoded).unsqueeze(0)
    
    # run inference and apply softmax
    prediction = model(batch).squeeze(0).softmax(0)
    
    # postprocess and format results
    _, indices = torch.sort(prediction, descending=True)
    print(indices[:5])
    inference_result = {
        "classPredictions": [
            {"class": weights.meta["categories"][idx.item()], "score": round(prediction[idx].item(),4)}
        for idx in indices[:5] ]
    }

    structured_output = {
        "data": {
            "result": inference_result,
            "explanation": None,
            "drift": None,
        }
    }
    
    return {'results.json', json.dumps(structured_output).encode()}

# create chassis model object
chassis_model = ChassisModel(process_fn=predict)                        
# add metadata & requirements
chassis_model.add_requirements(["torch", "torchvision", "Pillow"])      
chassis_model.metadata.model_name = "ResNet 50 Image Classification"  
chassis_model.metadata.model_version = "0.0.1"
chassis_model.metadata.add_input(                                                                    
    key="image",
    accepted_media_types=["image/jpeg", "image/png"],
    max_size="10M",
    description="Image to be classified by model"
)
chassis_model.metadata.add_output(
    key="results.json",
    media_type="application/json",
    max_size="1M",
    description="Classification predictions including human-readable label and the corresponding confidence score"
)

# test model
img_bytes = open("data/airplane.jpg", 'rb').read()
results = chassis_model.test({"image": img_bytes})
print(results)

# define builder object
builder = DockerBuilder(package=chassis_model)    

# local docker mode
start_time = time.time()
res = builder.build_image(name="resnet50-image-classification", show_logs=True)
end_time = time.time()
print(res)
print(f"Container image built in {round((end_time-start_time)/60, 5)} minutes")
