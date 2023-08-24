import time
import json
import torch
import numpy as np
from typing import Mapping, Dict
from transformers import AutoTokenizer, AutoModelForSequenceClassification #

from chassisml import ChassisModel #
from chassis.builder import DockerBuilder #

# load model with AutoTokenizer package #
tokenizer = AutoTokenizer.from_pretrained("bhadresh-savani/distilbert-base-uncased-emotion")
distilbert_model = AutoModelForSequenceClassification.from_pretrained("bhadresh-savani/distilbert-base-uncased-emotion")

# define labels from model config #
labels = distilbert_model.config.id2label

# define predict function #
def predict(inputs: Mapping[str, bytes]) -> Dict[str, bytes]:
    text = inputs['input.txt'].decode()
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
                "classPredictions": [{"class": labels[i], "score": round(softmax[0][i].item(), 4)} for i in indices]
            }
        }
    }        
    return {'results.json': json.dumps(results).encode()}

# create chassis model object
chassis_model = ChassisModel(process_fn=predict)                       # 
# add metadata & requirements
chassis_model.add_requirements(["transformers", "torch", "numpy"])     # 
chassis_model.metadata.model_name = "DistilBERT Text Classification"   # 
chassis_model.metadata.model_version = "0.0.1"
chassis_model.metadata.add_input(                                                                    
    key="input.txt",
    accepted_media_types=["text/plain"],
    max_size="10M",
    description="Input text to be classified by model"
)
chassis_model.metadata.add_output(
    key="results.json",
    media_type="application/json",
    max_size="1M",
    description="Classification predictions of six emotions classes and the corresponding confidence score"
)

# test model  # 
text = open("data/input.txt", 'rb').read()
results = chassis_model.test({"input.txt": text})
print(results)

# define builder object # 
builder = DockerBuilder(package=chassis_model)    

# local docker mode #
start_time = time.time()
res = builder.build_image(name="distilbert-text-classification", show_logs=True)
end_time = time.time()
print(res)
print(f"Container image built in {round((end_time-start_time)/60, 5)} minutes")
