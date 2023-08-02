import io
import time
from typing import Mapping

from chassis.builder import DockerBuilder, BuildOptions
from chassisml import ChassisModel, ChassisClient

import numpy as np
import tensorflow as tf

# define variables needed for inference
img_height = 180
img_width = 180
class_names = ['daisy', 'dandelion', 'roses', 'sunflowers', 'tulips']

# load model
tf_model = tf.keras.saving.load_model("model")

# define predict function
def predict(inputs: Mapping[str, bytes]) -> dict[str, bytes]:
    # preprocessing
    image_bytes = inputs['image']
    img = tf.keras.utils.load_img(
        io.BytesIO(image_bytes), target_size=(img_height, img_width)
    )

    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0) # Create a batch    
    
    # inference
    predictions = tf_model.predict(img_array)
    scores = tf.nn.softmax(predictions[0])
    
    # formatting
    indices = np.argsort(scores)[::-1]
    inference_result = {
        "classPredictions": [
            {"class": class_names[index], "score": round(scores[index].numpy().item(),4)} for index in indices
        ]
    }    
    
    structured_output = {
        "data": {
            "result": inference_result,
            "explanation": None,
            "drift": None,
        }
    }    
    
    return {"results.json": structured_output}


'''
Create Model
'''
model = ChassisModel(process_fn=predict)

# add pip requirements
model.add_requirements(["tensorflow", "numpy"])

# test model
sunflower_url = "https://storage.googleapis.com/download.tensorflow.org/example_images/592px-Red_sunflower.jpg"
sunflower_path = tf.keras.utils.get_file('Red_sunflower', origin=sunflower_url)
results = model.test(sunflower_path)
print(results)

# build container
builder = DockerBuilder(model)
start_time = time.time()
res = builder.build_image(name="1.5-tf-img-classification", tag="0.0.1", show_logs=True)
end_time = time.time()
print(res)
print(f"Container image built in {round((end_time-start_time)/60, 5)} minutes")
    
    
    