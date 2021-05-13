import json
import os
import math

import pickle as pkl
import numpy as np
from PIL import Image
import xgboost as xgb
import tempfile

from flask_psc_model import ModelBase, load_metadata

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(THIS_DIR, 'weights/xgboost-model')
LABELS_PATH = os.path.join(THIS_DIR, 'resources/labels.json')

class XGBoost(ModelBase):

    #: load the `model.yaml` metadata file from up the filesystem hierarchy;
    #: this will be used to avoid hardcoding the below filenames in this file
    metadata = load_metadata(__file__)

    #: a list of input filenames; specifying the `input_filenames` attribute is required to configure the model app
    input_filenames = list(metadata.inputs)

    #: a list of output filenames; specifying the `output_filenames` attribute is required to configure the model app
    output_filenames = list(metadata.outputs)

    def __init__(self):
        print("LOADING XG Boost model parameters...")
        self.model = pkl.load(open(MODEL_DIR, "rb"))

        if XGBoost.metadata.tags[0]=="classification":
            self.labels = []
            with open(LABELS_PATH, "r") as f:
                self.labels = json.load(f)

        print("XG Boost LOADED")

    def convert_size_to_bytes(size_str):
        multipliers = {
            'kilobyte':  1024,
            'megabyte':  1024 ** 2,
            'gigabyte':  1024 ** 3,
            'terabyte':  1024 ** 4,
            'petabyte':  1024 ** 5,
            'exabyte':   1024 ** 6,
            'zetabyte':  1024 ** 7,
            'yottabyte': 1024 ** 8,
            'kb': 1024,
            'mb': 1024**2,
            'gb': 1024**3,
            'tb': 1024**4,
            'pb': 1024**5,
            'eb': 1024**6,
            'zb': 1024**7,
            'yb': 1024**8,
        }

        for suffix in multipliers:
            size_str = size_str.lower().strip().strip('s')
            if size_str.lower().endswith(suffix):
                return int(float(size_str[0:-len(suffix)]) * multipliers[suffix])
        else:
            if size_str.endswith('b'):
                size_str = size_str[0:-1]
            elif size_str.endswith('byte'):
                size_str = size_str[0:-4]
        return int(size_str)

    def preprocess(self, X):
        feature_vector = np.array(X).reshape((-1, 1))
        X_matrix = feature_vector/255
        X_svm = bytes(' '.join(['{}:{}'.format(i + 1, el) for i, el in enumerate(X_matrix)]), 'utf-8')
        temp_file_location = None
        try:
            with tempfile.NamedTemporaryFile(delete=False) as libsvm_file:
                temp_file_location = libsvm_file.name
                libsvm_file.write(X_svm)

            dmatrix = xgb.DMatrix(temp_file_location)
        finally:
            if temp_file_location and os.path.exists(temp_file_location):
                os.remove(temp_file_location)

        return dmatrix

    def postprocess(self, predictions):
        if XGBoost.metadata.tags[0]=="classification":
            class_result = np.argmax(predictions)
            result_dict = {"result": self.labels[str(class_result)],
                           "confidence": str(np.max(predictions)) }
        else:
            result = [math.ceil(float(num)) for num in predictions]
            result_dict = {"result": str(result[0])}

        return result_dict

    def run(self, input_path, output_path):
        first_input = XGBoost.input_filenames[0]
        input_file_size = os.stat(input_path).st_size

        max_size = XGBoost.convert_size_to_bytes(XGBoost.metadata.inputs[first_input].maxSize + "b")
        if input_file_size == 0:
            raise ValueError("The input path references an empty file")
        elif input_file_size > max_size:
            raise ValueError("The size of the incoming array is out of the allowed limits")

        # read in data
        try:
            media_type = XGBoost.metadata.inputs[first_input].acceptedMediaTypes[0]
            if "image" in media_type:
                image = Image.open(input_path)
                # perform the preprocessing
                X_matrix = self.preprocess(image)
            elif "libsvm" in media_type:
                X_matrix = xgb.DMatrix(input_path)
            else:
                raise ValueError(f"The media type: '{media_type}' is not supported as an input type in this XGBoost implementation")
        except:
            raise ValueError("There is an error with the format of the input file")

        # call prediction function
        predictions_prob = self.model.predict(X_matrix, output_margin=True)

        # post process
        post_results = self.postprocess(predictions_prob)

        with open(output_path, 'w') as out:
            json.dump(post_results, out)

if __name__ == '__main__':
    # run the model independently from the full application; can be useful for testing
    #
    # to run from the repository root:
    #     python -m model_lib.model /path/to/input.txt /path/to/output.json
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='the input data filepath')
    parser.add_argument('output', help='the output results filepath')
    args = parser.parse_args()

    model = XGBoost()
    model.run(args.input, args.output)
