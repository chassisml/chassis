from __future__ import annotations

import base64
import os
import sys
from typing import Dict, Optional, Union
from uuid import uuid4
import kserve
from kserve import InferRequest, InferResponse
from kserve.protocol.grpc.grpc_predict_v2_pb2 import ModelInferRequest

from chassis.protos.v1.model_pb2 import StatusResponse
from chassis.runtime import ModelRunner, PACKAGE_DATA_PATH


class KServe(kserve.Model):
    def __init__(self, name: str, protocol: str):
        super().__init__(name)
        self.name = name
        self.protocol = protocol
        self.ready = False
        self.model: Optional[ModelRunner] = None

        with open(os.path.join(PACKAGE_DATA_PATH, "model_info"), "rb") as f:
            data = f.read()

        sr = StatusResponse()
        sr.ParseFromString(data)
        self.metadata: StatusResponse = sr

    def load(self) -> bool:
        self.model = ModelRunner.load()
        self.ready = self.model is not None
        return self.ready

    def predict(self, payload: Union[Dict, InferRequest, ModelInferRequest],
                headers: Optional[Dict[str, str]] = None) -> Union[Dict, InferResponse]:
        if self.protocol == "v1":
            return self._predictv1(payload, headers)
        elif self.protocol == "v2":
            return self._predictv2(payload, headers)
        raise ValueError("Unsupported protocol version")

    def _predictv1(self, payload: Union[Dict, InferRequest, ModelInferRequest],
                   headers: Optional[Dict[str, str]] = None) -> Union[Dict, InferResponse]:
        if self.model is None:
            raise RuntimeError("Model not available")
        input_key: str = self.metadata.inputs[0].filename
        output_key: str = self.metadata.outputs[0].filename
        instances = [{input_key: base64.b64decode(instance)} for instance in payload["instances"]]
        outputs = self.model.predict(instances)
        predictions = [o[output_key].decode() for o in outputs]
        return {"predictions": predictions}

    def _predictv2(self, payload: Union[Dict, InferRequest, ModelInferRequest],
                   headers: Optional[Dict[str, str]] = None) -> Union[Dict, InferResponse]:
        if self.model is None:
            raise RuntimeError("Model not available")
        output_data = {
            "id": str(uuid4()),
            "model_name": self.metadata.model_info.model_name,
            "model_version": self.metadata.model_info.model_version,
            "outputs": [],
        }

        input_key = self.metadata.inputs[0].filename
        output_key = self.metadata.outputs[0].filename
        for inputs in payload.get("inputs", []):
            input_data = inputs.get("data", [])
            instances = [{input_key: base64.b64decode(instance)} for instance in input_data]
            outputs = self.model.predict(instances)
            predictions = [o[output_key].decode() for o in outputs]
            prediction_data_len = len(predictions)
            prediction_output_data = {
                "data": predictions,
                "datatype": inputs.get("datatype"),
                "name": inputs.get("name"),
                "parameters": None,
                "shape": prediction_data_len,
            }
            output_data["outputs"].append(prediction_output_data)

        return output_data


def serve():
    env = {
        "HTTP_PORT": os.getenv("HTTP_PORT", "45000"),
        "MODEL_NAME": os.getenv("MODEL_NAME", "default"),
        "PROTOCOL": os.getenv("PROTOCOL", "v2"),
    }

    for e in env:
        if not env.get(e):
            print(f"No {e} environment variable defined.")
            sys.exit(1)

    print(f"Initializing KServe instance with protocol {env.get('PROTOCOL')} on port {env.get('HTTP_PORT')}")

    model = KServe(
        env.get("MODEL_NAME"),
        env.get("PROTOCOL"),
    )
    model.load()

    kserve.ModelServer(
        http_port=int(env.get("HTTP_PORT")),
        enable_docs_url=True,
    ).start([model])
