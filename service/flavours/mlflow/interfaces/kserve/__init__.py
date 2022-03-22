import os
import sys
import kserve

import numpy as np
import pandas as pd

import base64
from loguru import logger
from typing import Dict
from uuid import uuid4

import mlflow

MODEL_DIR = os.getenv('MODEL_DIR')
class KServe(kserve.Model):
    def __init__(self, name: str, protocol: str):
        super().__init__(name)
        self.name = name
        self.protocol = protocol
        self.ready = False
        self.model = None

    def load(self):
        self.model = mlflow.pyfunc.load_model(MODEL_DIR)

        if hasattr(self.model._model_impl.python_model,"batch_input"):
            self.batch_input = self.model._model_impl.python_model.batch_input
            self.batch_size = self.model._model_impl.python_model.batch_size
        else:
            self.batch_input = False

        self.ready = True

    def predict(self, request: Dict) -> Dict:
        if self.protocol == 'v1':
            return self._predictv1(request)
        elif self.protocol == 'v2':
            return self._predictv2(request)

    def _predictv1(self, request):
        input_data = request['instances']

        if self.batch_input:
            batch_outputs = []
            instances = [base64.b64decode(instance) for instance in input_data]
            batches = split_list(instances,self.batch_size)
            for batch in batches:
                batch_outputs.append(self.model._model_impl.python_model.batch_predict(None,batch))
            preds = [item.decode()for batch in batch_outputs for item in batch]
        else:
            preds = []
            for instance in input_data:
                preds.append(self.model.predict(base64.b64decode(instance)).decode())

        return { 'predictions': preds }

    def _predictv2(self, request):
        output_data = {
            'id': str(uuid4()),
            'model_name': self.name,
            'model_version': None,
            'outputs': []
        }

        for inputs in request.get('inputs', []):
            input_data = inputs.get('data', [])

            if self.batch_input:
                batch_outputs = []
                instances = [base64.b64decode(instance) for instance in input_data]
                batches = split_list(instances,self.batch_size)
                for batch in batches:
                    batch_outputs.append(self.model._model_impl.python_model.batch_predict(None,batch))
                prediction_data = [item.decode() for batch in batch_outputs for item in batch]
            else:
                prediction_data = []
                for instance in input_data:
                    prediction_data.append(self.model.predict(base64.b64decode(instance)).decode())

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

    logger.debug(f'Initializing KServe instance with protocol {envs.get("PROTOCOL")} in port {envs.get("HTTP_PORT")}')

    model = KServe(
        envs.get('MODEL_NAME'),
        envs.get('PROTOCOL')
    )
    model.load()

    kserve.ModelServer(
        http_port=envs.get('HTTP_PORT'),
    ).start([model])

def split_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]