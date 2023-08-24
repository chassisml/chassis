import json
from typing import Mapping

from chassis.builder import DockerBuilder
from chassisml import ChassisModel


def predict(inputs: Mapping[str, bytes]) -> dict[str, bytes]:
    result = {"Message": inputs["input"].decode()}
    return {"results.json": json.dumps(result).encode()}


model = ChassisModel(process_fn=predict)
model.metadata.add_input
context = model.prepare_context(arch="arm64")
builder = DockerBuilder(context)
builder.build_image("echo-model:latest")