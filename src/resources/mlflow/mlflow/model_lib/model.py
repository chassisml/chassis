import json
import os
import mlflow
import pandas as pd
import numpy as np
import sys
from pandas.errors import ParserError
from mlflow.exceptions import MlflowException

from flask_psc_model import ModelBase, load_metadata

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
WEIGHTS_DIR = os.path.join(THIS_DIR, "weights")
#RUN_DIR = os.path.join(WEIGHTS_DIR, "run_assets")


class GeneralMLFlowModel(ModelBase):

    #: load the `model.yaml` metadata file from up the filesystem hierarchy;
    #: this will be used to avoid hardcoding the below filenames in this file
    metadata = load_metadata(__file__)

    #: a list of input filenames; specifying the `input_filenames` attribute is required to configure the model app
    input_filenames = list(metadata.inputs)

    #: a list of output filenames; specifying the `output_filenames` attribute is required to configure the model app
    output_filenames = list(metadata.outputs)

    def __init__(self):
        """Load the model files and do any initialization.

        A single instance of this model class will be reused multiple times to perform inference
        on multiple input files so any slow initialization steps such as reading in a data
        files or loading an inference graph to GPU should be done here.

        This function should require no arguments, or provide appropriate defaults for all arguments.

        NOTE: The `__init__` function and `run` function may not be called from the same thread so extra
        care may be needed if using frameworks such as Tensorflow that make use of thread locals.
        """

        # load model weights from
        try:
            self.model = mlflow.pyfunc.load_model(WEIGHTS_DIR)
        except Exception as e:
            print(e)

    def run(self, input_path, output_path):
        """Run the model on the given input file paths and write to the given output file paths.

        The input files paths followed by the output file paths will be passed into this function as
        positional arguments in the same order as specified in `input_filenames` and `output_filenames`.
        """

        input_column_names = self.model.metadata.signature.inputs.column_names()
        output_column_names = self.model.metadata.signature.outputs.column_names()

        # validate input file meets the correct format based on the inferred signature
        try:
            # read data
            processed_data = pd.read_csv(input_path, sep=',')
            if processed_data.empty:
                raise ValueError
        except ParserError:
            raise ValueError("Invalid CSV File")
        except ValueError:
            raise ValueError("Input CSV is either empty or does not contain valid data")

        try:
            predictions = self.model.predict(processed_data)
        except MlflowException as e:
            if "Note that there were extra inputs" in str(e):
                raise ValueError("Raw MLflow error: {}. \n\nAdditional Explanation: Input data does not adhere to the data structure defined in the MLFlow Model Signature. The input csv file must contain the following column names in order: \n\n{}.".format(e, input_column_names))
            else:
                raise ValueError("Input data does not adhere to the data structure defined in the MLFlow Model Signature based on the format of the training data. The input csv file must contain the following column names in order: \n\n{}.".format(input_column_names))

        # process predictions to write to output
        results = {}
        output_column_names = self.model.metadata.signature.outputs.column_names()

        results[output_column_names[0]] = list(predictions[0].to_list())

        with open(output_path, 'w', encoding='utf-8') as out_file:
            json.dump(results, out_file)


if __name__ == '__main__':
    # run the model independently from the full application; can be useful for testing
    #
    # to run from the repository root:
    #     python -m model_lib.model /path/to/input.txt /path/to/output.json
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='the input data filepath')
    parser.add_argument('--output', default='results.json', help='the output results filepath')
    args = parser.parse_args()

    model = GeneralMLFlowModel()
    model.run(args.input, args.output)
