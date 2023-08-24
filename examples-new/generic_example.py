from typing import Mapping
from chassisml import ChassisModel
from chassis.builder import DockerBuilder

# NOTE: The below code snippet is pseudo code that
# intends to demonstrate the general workflow when 
# using Chassis and will not execute as is. Substitute
# with your own Python framework, any revelant utility 
# methods, and syntax specific to your model.

import framework 
import preprocess, postprocessmodel

# load model
model = framework.load("path/to/model/file")

# define predict function
def predict(input_data: Mapping[str, bytes]) -> dict[str, bytes]:
    # preprocess data
    data = preprocess(input_data['input'])
    # perform inference
    predictions = model.predict(data)
    # process output
    output = postprocess(predictions)
    return {"results.json": output}    

# create ChassisModel object
model = ChassisModel(predict)
builder = DockerBuilder(model)
# build container with local Docker option
build_response = builder.build_image(name="My First Chassis Model", tag="0.0.1")