import io
import time
import json
from PIL import Image
from typing import Mapping, Dict
from ultralytics import YOLO

from chassisml import ChassisModel
from chassis.builder import DockerBuilder, BuildOptions, BuildContext

# Load a model
# model = YOLO('yolov8n.pt')  # pretrained YOLOv8n model

# image = 'https://github.com/ultralytics/yolov5/raw/master/data/images/zidane.jpg'
image = "data/sempre-bcam-4.png"

# names = model.model.names
# with open("names.json", "w") as out:
#     json.dump(names, out)
    
# import cloudpickle
# test = cloudpickle.dumps(model)
# import sys
# sys.exit()

model = None
    
# create predict function
def predict(inputs: Mapping[str, bytes]) -> Dict[str, bytes]:
    global model, names
    if model is None:
        print("loading model")
        model = YOLO("data/yolov8n.pt")
        names = model.model.names
    # load data
    img = Image.open(io.BytesIO(inputs['image'])).convert("RGB")
    
    # run inference
    boxes = model.predict(img, save_conf=True, stream=False)[0].boxes
    
    # format output
    final_output = []
    for box, score, cls in zip(boxes.xywh, boxes.conf, boxes.cls):
        detection_output = {}
        detection_output["class"] = names[int(cls)]
        detection_output["score"] = round(score.item(), 4)
        detection_output["bounding_box"] = {
            "x": box[0].item(),
            "y": box[1].item(),
            "width": box[2].item(),
            "height": box[3].item()             
        }
        final_output.append(detection_output)
    
    output = {
        'detections': final_output
    }    
    
    return {'results.json': json.dumps(output).encode()}      

# create chassis model object
chassis_model = ChassisModel(predict)
chassis_model.add_requirements(["torch", "ultralytics"])
chassis_model.add_apt_packages(["libgl1", "libglib2.0-0"])
chassis_model.additional_files.add("./yolov8n.pt")
chassis_model.metadata.model_name = "YOLOv8 Object Detection"  
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
    description="Object detections with label, confidence score, and bounding box in xywh format"
)

# test model
img = open("data/sempre-bcam-4.png", "rb").read()
results = chassis_model.test({"image": img})
print(results)

# define builder object
# options = BuildOptions(base_dir=")
context = BuildOptions(base_dir="tmp-context")
# chassis_model.prepare_context(context)
builder = DockerBuilder(package=chassis_model)    

# local docker mode
start_time = time.time()
res = builder.build_image(name="yolov8-object-detection", show_logs=True)
end_time = time.time()
print(res)
print(f"Container image built in {round((end_time-start_time)/60, 5)} minutes")
    
