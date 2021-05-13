import json
import os

import numpy as np
import mxnet as mx
from PIL import Image

from flask_psc_model import ModelBase, load_metadata

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(THIS_DIR, 'weights/model')
LABELS_PATH = os.path.join(THIS_DIR, 'resources/labels.json')


class FactorizationMachines(ModelBase):
    #: load the `model.yaml` metadata file from up the filesystem hierarchy;
    #: this will be used to avoid hardcoding the below filenames in this file
    metadata = load_metadata(__file__)

    #: a list of input filenames; specifying the `input_filenames` attribute is required to configure the model app
    input_filenames = list(metadata.inputs)

    #: a list of output filenames; specifying the `output_filenames` attribute is required to configure the model app
    output_filenames = list(metadata.outputs)

    def __init__(self):
        print("LOADING Factorization machines parameters...")
        self.model = mx.module.Module.load(MODEL_DIR, 0, False, label_names=['out_label'])
        self.labels = []
        with open(LABELS_PATH, "r") as f:
            self.labels = json.load(f)

        self.V = self.model._arg_params['v'].asnumpy()
        self.w = self.model._arg_params['Linear_Plus_Bias_weight'].asnumpy()
        self.b = self.model._arg_params['Linear_Plus_Bias_bias'].asnumpy()
        print("Factorization machine LOADED")


    def preprocess(self, X):
        linear_output = np.matmul(X, self.w.T)
        v = self.V.T
        t0 = np.matmul(X, v)
        t1 = np.power(X, 2)
        t2 = np.power(v, 2)
        term = t0 ** 2 - np.matmul(t1, t2)
        factor_output = 0.5 * np.sum(term, axis = 1)

        return np.mean(self.b + linear_output + factor_output, axis=0)


    def postprocess(self, probability):
        class_result = int(probability>0.5)
        return {"result": self.labels[str(class_result)],
                "confidence": str(probability if class_result else 1-probability) }


    def run(self, input_path, output_path):
        input_file_size = os.stat(input_path).st_size

        if input_file_size == 0:
            raise ValueError("The input path references an empty file")
        elif input_file_size > (784):
            raise ValueError("The size of the incoming array is out of the allowed limits")

        # read in data
        try:
            image = Image.open(input_path)
        except:
            raise ValueError("There is an error with the format of the input file")

        # perform the preprocessing
        feature_vector = np.array(image).reshape((1,-1))
        result = self.preprocess(feature_vector/255)

        # perform inference
        pred_proba = 1.0 / (1.0 + np.exp(-result[0]))

        # post process
        post_results = self.postprocess(pred_proba)

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

    model = FactorizationMachines()
    model.run(args.input, args.output)
