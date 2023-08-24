import io
import time
import json
import numpy as np
from typing import Mapping

from chassis.builder import DockerBuilder, RemoteBuilder, BuildOptions
from chassisml import ChassisModel, ChassisClient

import yolov5
from PIL import Image

# load model
model = yolov5.load('keremberke/yolov5n-license-plate')

# set model params
# model.conf = 0.0  # NMS confidence threshold
model.iou = 0.45  # NMS IoU threshold
model.agnostic = False  # NMS class-agnostic
model.multi_label = False  # NMS multiple labels per box
model.max_det = 1000  # maximum number of detections per image

# define class labels for postprocessing
labels = ["license_plate"]

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
def predict(inputs: Mapping[str, bytes]) -> dict[str, bytes]:
    # load data
    img = Image.open(io.BytesIO(inputs['image'])).convert("RGB")
    
    # run inference
    results = model(img, size=640)
    preds = xyxy2xywh(results.pred[0].detach().numpy())
    
    final_output = []
    # format output
    for det in preds:
        # print(det.shape)
        detection_output = {}
        detection_output["class"] = labels[int(det[5].item())]
        detection_output["score"] = round(det[4].item(), 4)
        detection_output["bounding_box"] = {
            "x": det[0].item(),
            "y": det[1].item(),
            "width": det[2].item(),
            "height": det[3].item()            
        }
        final_output.append(detection_output)
    
    output = {
        'detections': final_output
    }
    
    return {'results.json': json.dumps(output).encode()}    


# create chassis model object
chassis_model = ChassisModel(predict)
chassis_model.add_requirements(["yolov5", "Pillow", "opencv-python-headless"])
chassis_model.metadata.model_name = "YOLOv5 LP Detection"  
chassis_model.metadata.model_version = "0.0.1"
chassis_model.metadata.add_input(                                                                    
    key="image",
    accepted_media_types=["image/jpeg", "image/png"],
    max_size="10M",
    description="Image data"
)
chassis_model.metadata.add_output(
    key="results.json",
    media_type="application/json",
    max_size="1M",
    description="LP detections with label, confidence score, and bounding box in xywh format"
)

# test model
img = open("data/sempre-bcam-4.png", "rb").read()
results = chassis_model.test({"image": img})
print(results)

# define builder object
# options = BuildOptions(base_dir=")
# chassis_model.prepare_context(context)
builder = DockerBuilder(package=chassis_model)    

# local docker mode
start_time = time.time()
res = builder.build_image(name="yolov5-lp-detection", show_logs=True)
end_time = time.time()
print(res)
print(f"Container image built in {round((end_time-start_time)/60, 5)} minutes")
    