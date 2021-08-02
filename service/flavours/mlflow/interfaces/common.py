import os
import numpy as np
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
        # Input data must be a numpy array.
        if type(input_data).__module__ != np.__name__:
            input_data = np.array(input_data)

        predictions = self.model.predict(input_data)

        return predictions
