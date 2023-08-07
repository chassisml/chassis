import io
import time
import numpy as np
from typing import Mapping

from chassis.builder import DockerBuilder, RemoteBuilder, BuildOptions
from chassisml import ChassisModel, ChassisClient

import yolov5
from PIL import Image

# load model
model = yolov5.load('keremberke/yolov5n-license-plate')

# set model params
model.conf = 0.2  # NMS confidence threshold
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
def predict(input_bytes: Mapping[str, bytes]) -> dict[str, bytes]:
    # load data
    img = Image.open(io.BytesIO(input_bytes['input'])).convert("RGB")
    
    # run inference
    results = model(img, size=640)
    preds = xyxy2xywh(results.pred[0].detach().numpy())
    
    final_output = []
    # format output
    for det in preds:
        # print(det.shape)
        detection_output = {}
        detection_output["class"] = labels[int(det[5].item())]
        detection_output["score"] = det[4].item()
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
    
    return {'results.json': output}    


# create chassis model object
chassis_model = ChassisModel(predict)
chassis_model.add_requirements(["yolov5", "Pillow", "opencv-python-headless"])

# test model
img_path = "data/sempre-bcam-4.png"
results = chassis_model.test(img_path)
print(results)

# local docker mode
builder = DockerBuilder(chassis_model)
start_time = time.time()
res = builder.build_image(name="bmunday131/yolov5-object-detection", tag="0.0.1", show_logs=True)
end_time = time.time()
print(res)
print(f"Container image built in {round((end_time-start_time)/60, 5)} minutes")
    
# server mode
# chassis_client = ChassisClient("http://localhost:8080")

# # new way
# builder = RemoteBuilder(chassis_client, chassis_model)
# start_time = time.time()
# res = builder.build_image(name="yolov5-object-detection", tag="0.0.1")
# end_time = time.time()
# print(res)
# print(f"Container image built in {round((end_time-start_time)/60, 5)} minutes")
    
    