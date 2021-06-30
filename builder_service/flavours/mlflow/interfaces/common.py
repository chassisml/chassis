import os
import mlflow.pyfunc
from loguru import logger

MODEL_DIR = os.getenv('MODEL_DIR')


class MLFlowFlavour:

    def __init__(self):
        self.model = None

        self.load_model()

    def load_model(self):
        self.model = mlflow.pyfunc.load_model(MODEL_DIR)

    def predict(self, input_data):
        logger.debug(f'input_data shape: {input_data.shape}')

        predictions = self.model.predict(input_data)

        return predictions
