import io
import time
import json
import numpy as np
from typing import Mapping

from chassis.builder import DockerBuilder, RemoteBuilder, BuildOptions
from chassisml import ChassisModel, ChassisClient
from chassis.metadata import ModelMetadata

# Use a pipeline as a high-level helper
from PIL import Image
from transformers import pipeline

# load model in pipeline form
pipe = pipeline("object-detection", model="hustvl/yolos-tiny")

# postprocessing
def xyxy2xywh(x):
    # Convert nx4 boxes from [x1, y1, x2, y2] to [x, y, w, h] where xy1=top-left, xy2=bottom-right
    y = np.copy(x)
    y[..., 0] = (x[..., 0] + x[..., 2]) / 2  # x center
    y[..., 1] = (x[..., 1] + x[..., 3]) / 2  # y center
    y[..., 2] = x[..., 2] - x[..., 0]  # width
    y[..., 3] = x[..., 3] - x[..., 1]  # height
    return y  


# create predict function
def predict(input_bytes: Mapping[str, bytes]) -> dict[str, bytes]:
    # load data
    img = Image.open(io.BytesIO(input_bytes['input'])).convert("RGB")
    
    # run inference
    results = pipe(img)
    if len(results) > 0:
        bbox_list = []
        for result in results:
            bbox = [result['box']['xmin'], result['box']['ymin'], result['box']['xmax'],result['box']['ymax']]
            bbox_list.append(bbox)
        bbox_numpy = xyxy2xywh(np.array(bbox_list))
        final_output = []
        # format output
        for result, box in zip(results, bbox_numpy):
            # print(det.shape)
            detection_output = {}
            detection_output["class"] = result['label']
            detection_output["score"] = round(result['score'], 5)
            detection_output["bounding_box"] = {
                "x": box[0].item(),
                "y": box[1].item(),
                "width": box[2].item(),
                "height": box[3].item()            
            }
            final_output.append(detection_output)        
    else:
        final_output = []
    
    output = {
        'detections': final_output
    }
    
    return {'results.json': json.dumps(output).encode()}    


# create chassis model object
chassis_model = ChassisModel(predict)
chassis_model.add_requirements(["transformers", "Pillow", "numpy", "torch"])
chassis_model.metadata.add_input("input", ["image/jpeg", "image/png"], "10M", "Imagery")
chassis_model.metadata.add_output("results.json", "application/json")

# test model
# img_path = "data/sempre-bcam-4.png"
img_path = "data/license-plate.jpg"
results = chassis_model.test(img_path)
print(results)

# local docker mode
builder = DockerBuilder(chassis_model)
start_time = time.time()
res = builder.build_image(name="bmunday131/yolos-tiny-obj-detection", tag="0.0.2", show_logs=True)
end_time = time.time()
print(res)
print(f"Container image built in {round((end_time-start_time)/60, 5)} minutes")