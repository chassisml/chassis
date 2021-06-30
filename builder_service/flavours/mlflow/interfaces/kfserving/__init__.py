import numpy as np
import pandas as pd
from uuid import uuid4
from loguru import logger
from flask import Blueprint, request
from ..common import MLFlowFlavour

kfserving_blueprint = Blueprint('kfserving_blueprint', __name__)

mlflow_flavour = MLFlowFlavour()

@kfserving_blueprint.route('/v2/health/live')
@kfserving_blueprint.route('/v2/health/ready')
def live():
    return 'Alive'

# https://github.com/kubeflow/kfserving/tree/master/docs/samples/v1beta1/sklearn/v1#run-a-prediction
@kfserving_blueprint.route('/v1/models/<model_name>:predict', methods=['POST'])
def predictv1(model_name):
    logger.debug(f'Ignoring model_name: {model_name}')

    data = request.get_json(force=True)
    input_data = pd.DataFrame(data['instances'])

    prediction_data = mlflow_flavour.predict(input_data)

    return { 'predictions': prediction_data }

# https://github.com/kubeflow/kfserving/tree/master/docs/samples/v1beta1/sklearn/v2#testing-deployed-model
@kfserving_blueprint.route('/v2/models/<model_name>/infer', defaults={'model_version': None}, methods=['POST'])
@kfserving_blueprint.route('/v2/models/<model_name>/versions/<model_version>/infer', methods=['POST'])
def predictv2(model_name, model_version):
    logger.debug(f'Ignoring model_name: {model_name} and model_version: {model_version}')

    data = request.get_json(force=True)

    output_data = {
        'id': str(uuid4()),
        'model_name': model_name,
        'model_version': model_version,
        'outputs': []
    }

    for inputs in data.get('inputs', []):
        input_data = pd.DataFrame(inputs.get('data', []))
        prediction_data = mlflow_flavour.predict(input_data)
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
