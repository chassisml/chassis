import time
import json
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from chassis.builder import DockerBuilder
from chassisml import ChassisClient, ChassisModel

# load model
tokenizer = AutoTokenizer.from_pretrained("bhadresh-savani/distilbert-base-uncased-emotion")
distilbert_model = AutoModelForSequenceClassification.from_pretrained("bhadresh-savani/distilbert-base-uncased-emotion")

# define labels from model config
labels = distilbert_model.config.id2label

# define process function
# define process function that will serve as our inference function
def process(input_bytes):
    # decode and preprocess data bytes
    text = input_bytes.decode()
    inputs = tokenizer(text, return_tensors="pt")
    
    # run preprocessed data through model
    with torch.no_grad():
        logits = distilbert_model(**inputs).logits
        softmax = torch.nn.functional.softmax(logits, dim=1).detach().cpu().numpy()
        
    # postprocess 
    indices = np.argsort(softmax)[0][::-1]
    results = {
        "data": {
            "result": {
                "classPredictions": [{"class": labels[i], "score": softmax[0][i]} for i in indices]
            }
        }
    }
    
    return results


'''
Create Model
'''
# legacy way
# chassis_client = ChassisClient("https://chassis.app.modzy.com")
# model = chassis_client.create_model(process_fn=process)
# new way
model = ChassisModel(process_fn=process, legacy_predict_fn=True)

# add pip requirements
model.add_requirements(["transformers", "numpy", "torch"])

# test model
sample_filepath = './data/input.txt'
results = model.test(sample_filepath)
print(results)

# build container
builder = DockerBuilder(model)
start_time = time.time()
res = builder.build_image(name="1.5-transformers-distilbert-classification", tag="0.0.1", show_logs=True)
end_time = time.time()
print(res)
print(f"Container image built in {round((end_time-start_time)/60, 5)} minutes")