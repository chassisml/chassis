import os
import sys
import kfserving

import numpy as np
import pandas as pd

import base64
from loguru import logger
from typing import Dict
from uuid import uuid4

import mlflow

MODEL_DIR = os.getenv('MODEL_DIR')
class KFServing(kfserving.KFModel):
    def __init__(self, name: str, protocol: str):
        super().__init__(name)
        self.name = name
        self.protocol = protocol
        self.ready = False
        self.model = None

    def load(self):
        self.model = mlflow.pyfunc.load_model(MODEL_DIR)
        self.ready = True

    def predict(self, request: Dict) -> Dict:
        if self.protocol == 'v1':
            return self._predictv1(request)
        elif self.protocol == 'v2':
            return self._predictv2(request)

    # https://github.com/kubeflow/kfserving/tree/master/docs/samples/v1beta1/sklearn/v1#run-a-prediction
    def _predictv1(self, request):
        input_data = request['instances']
        preds = []
        for instance in input_data:
            preds.append(self.model.predict(base64.b64decode(instance)))

        return { 'predictions': preds }

    # https://github.com/kubeflow/kfserving/tree/master/docs/samples/v1beta1/sklearn/v2#testing-deployed-model
    def _predictv2(self, request):
        output_data = {
            'id': str(uuid4()),
            'model_name': self.name,
            'model_version': None,
            'outputs': []
        }

        for inputs in request.get('inputs', []):
            prediction_data = []
            input_data = inputs.get('data', [])
            for instance in input_data:
                prediction_data.append(self.model.predict(base64.b64decode(instance)))

            prediction_data_len = len(prediction_data)

            prediction_output_data = {
                'data': prediction_data,
                'datatype': inputs.get('datatype'),
                'name': inputs.get('name'),
                'parameters': None,
                'shape': prediction_data_len,
            }
            output_data['outputs'].append(prediction_output_data)

        return output_data

def start_server():
    envs = {
        'HTTP_PORT': os.getenv('HTTP_PORT'),
        'MODEL_NAME': os.getenv('MODEL_NAME'),
        'PROTOCOL': os.getenv('PROTOCOL'),
    }

    for env in envs:
        if not envs.get(env):
            logger.critical(f'No {env} environment variable defined.')
            sys.exit(1)

    logger.debug(f'Initializing KFServer instance with protocol {envs.get("PROTOCOL")} in port {envs.get("HTTP_PORT")}')

    model = KFServing(
        envs.get('MODEL_NAME'),
        envs.get('PROTOCOL')
    )
    model.load()

    kfserving.KFServer(
        http_port=envs.get('HTTP_PORT'),
    ).start([model])
