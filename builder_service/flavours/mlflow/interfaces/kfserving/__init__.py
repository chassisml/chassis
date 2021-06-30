import os
import sys
import kfserving

import numpy as np
import pandas as pd

from loguru import logger
from typing import Dict
from uuid import uuid4

from ..common import MLFlowFlavour


class KFServing(kfserving.KFModel):
    def __init__(self, name: str, protocol: str):
        super().__init__(name)
        self.name = name
        self.protocol = protocol
        self.ready = False
        self.model = None

    def load(self):
        self.model = MLFlowFlavour()
        self.ready = True

    def predict(self, request: Dict) -> Dict:
        if self.protocol == 'v1':
            return self._predictv1(request)
        elif self.protocol == 'v2':
            return self._predictv2(request)

    # https://github.com/kubeflow/kfserving/tree/master/docs/samples/v1beta1/sklearn/v1#run-a-prediction
    def _predictv1(self, request):
        input_data = pd.DataFrame(request['instances'])

        prediction_data = self.model.predict(input_data)

        return { 'predictions': prediction_data }

    # https://github.com/kubeflow/kfserving/tree/master/docs/samples/v1beta1/sklearn/v2#testing-deployed-model
    def _predictv2(self, request):
        output_data = {
            'id': str(uuid4()),
            'model_name': self.name,
            'model_version': None,
            'outputs': []
        }

        for inputs in request.get('inputs', []):
            input_data = pd.DataFrame(inputs.get('data', []))
            prediction_data = self.model.predict(input_data)
            prediction_data_len = prediction_data.shape if isinstance(prediction_data, np.ndarray) \
                                                        else len(prediction_data)

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
