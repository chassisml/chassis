import os
import json
from typing import Dict, List

import mlflow.pyfunc

"""
The required output structure for a successful inference run for a models is the following JSON:

{
    "data": {
        "result": <inference-result>,
        "explanation": <explanation-data>,
        "drift": <drift-data>,
    }
}

The `data` key is required and stores a dictionary which represents the output for a specific input. The only top-level
key within these dictionaries that is required is `result`, however, `explanation` and `drift` are additional keys that
may be included if your particular model supports drift detection or explainability. All three of these keys
(`result`, `explanation`, and `drift`) are required to have a particular format in order to provide platform support.
This format type must be specified in the model.yaml file for the version that you are releasing, and the structure for
this format type must be followed. If no formats are specified, it is possible to define your own custom structure on a
per-model basis.

The required output structure for a failed inference run for a models is the following JSON:

{
    "error_message": <error-message>
}

Here, all error information that you can extract can be loaded into a single string and returned. This could be a JSON
string with a structured error log, or a stack trace dumped to a string.

Specifications:
This section details the currently supported specifications for the "result", "explanation", and "drift" fields of each
successful output JSON. These correspond to specifications selected in the `resultsFormat`, `driftFormat`,
`explanationFormat` of the model.yaml file for the particular version of the model.

* `resultsFormat`:

The currently supported types for resultsFormat, concrete specifications, and descriptions can be found in
grpc_model.src.results_format_specifications.

* `driftFormat`

2A) imageRLE

explanation: {
    "maskRLE": <rle-mask>,
    "dimensions": {
        "height": <pixel-height>
        "width": <pixel-width>
    }
}

Here, the <rle-mask> is a fortran ordered run-length encoding.

* `explanationFormat`

3A) ResNet50

drift: {
    {
        "layer1": <layer-data>
        "layer2": <layer-data>
        "layer3": <layer-data>
        "layer4": <layer-data>
    }
}

"""


def get_success_json_structure(inference_result, explanation_result, drift_result) -> Dict[str, bytes]:
    output_item_json = {
        "data": {
            "result": inference_result,
            "explanation": explanation_result,
            "drift": drift_result,
        }
    }
    return {"results.json": json.dumps(output_item_json, separators=(",", ":")).encode()}


def get_failure_json_structure(error_message: str) -> Dict[str, bytes]:
    error_json = {"error_message": error_message}

    return {"error": json.dumps(error_json).encode()}

MODEL_DIR = os.getenv('MODEL_DIR')

class ExampleModel:
    # Note: Throwing unhandled exceptions that contain lots of information about the issue is expected and encouraged
    # for models when they encounter any issues or internal errors.

    def __init__(self):
        """
        This constructor should perform all initialization for your model. For example, all one-time tasks such as
        loading your model weights into memory should be performed here.

        This corresponds to the Status remote procedure call.
        """
        self.model = mlflow.pyfunc.load_model(MODEL_DIR)

        if hasattr(self.model._model_impl.python_model,"batch_input"):
            self.batch_input = self.model._model_impl.python_model.batch_input
        else:
            self.batch_input = False

    def handle_single_input(self, model_input: Dict[str, bytes], detect_drift: bool, explain: bool, input_filename: str) -> Dict[str, bytes]:

        output_bytes = self.model.predict(model_input[input_filename])

        return {"results.json": output_bytes}

    def handle_input_batch(self, model_inputs: List[Dict[str, bytes]], detect_drift: bool, explain: bool, input_filename: str) -> List[Dict[str, bytes]]:
        """
        This is an optional method that will be attempted to be called when more than one inputs to the model
        are ready to be processed. This enables a user to provide a more efficient means of handling inputs in batch
        that takes advantage of specific properties of their model.

        If you are not implementing custom batch processing, this method should raise a NotImplementedError. If you are
        implementing custom batch processing, then any unhandled exception will be interpreted as a fatal error that
        will result in the entire batch failing. If you would like to allow individual elements of the batch to fail
        without failing the entire batch, then you must handle the exception within this function, and ensure the JSON
        structure for messages with an error has a top level "error" key with a detailed description of the error
        message.

        This corresponds to the Run remote procedure call for batch inputs.

        {
            "error": "your error message here"
        }

        """
        
        if self.batch_input:
            inputs = [model_input[input_filename] for model_input in model_inputs]
            outputs = self.model._model_impl.python_model.batch_predict(None,inputs)
            return [{"results.json": output} for output in outputs]
        else:
            raise NotImplementedError
            