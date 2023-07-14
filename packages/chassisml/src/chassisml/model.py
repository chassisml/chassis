import _io
import json
import os
import urllib.parse
from typing import Union

from ._utils import NumpyEncoder

routes = {
    'build': '/build',
    'job': '/job',
    'test': '/test'
}


def _gen_predict_method(process_fn, batch=False, batch_to_single=False):
    def predict(_, model_input):
        if batch_to_single:
            output = process_fn([model_input])[0]
        else:
            output = process_fn(model_input)
        if batch:
            return [json.dumps(out, separators=(",", ":"), cls=NumpyEncoder).encode() for out in output]
        else:
            return json.dumps(output, separators=(",", ":"), cls=NumpyEncoder).encode()

    return predict


class ChassisModel:
    """
    The Chassis Model object.

    Attributes:
        predict (function): predict function.
            Will wrap user-provided function which takes two arguments: model_input (bytes) and model_context (dict).
        chassis_build_url (str): The build url for the Chassis API.
        ssl_verification (Union[str, bool]): Can be path to certificate to use during requests to service, True (use verification), or False (don't use verification).
    """

    def __init__(self, process_fn, batch_process_fn, batch_size, chassis_base_url, chassis_auth_header, ssl_verification):
        if process_fn and batch_process_fn:
            if not batch_size:
                raise ValueError("Both batch_process_fn and batch_size must be provided for batch support")
            self.predict = _gen_predict_method(process_fn)
            self.batch_predict = _gen_predict_method(batch_process_fn, batch=True)
            self.batch_input = True
            self.batch_size = batch_size
        elif process_fn and not batch_process_fn:
            self.predict = _gen_predict_method(process_fn)
            self.batch_input = False
            self.batch_size = None
        elif batch_process_fn and not process_fn:
            if not batch_size:
                raise ValueError("Both batch_process_fn and batch_size must be provided for batch support")
            self.predict = _gen_predict_method(batch_process_fn, batch_to_single=True)
            self.batch_predict = _gen_predict_method(batch_process_fn, batch=True)
            self.batch_input = True
            self.batch_size = batch_size
        else:
            raise ValueError("At least one of process_fn or batch_process_fn must be provided.")

        self.chassis_build_url = urllib.parse.urljoin(chassis_base_url, routes["build"])
        self.chassis_test_url = urllib.parse.urljoin(chassis_base_url, routes["test"])
        self.chassis_auth_header = chassis_auth_header
        self.ssl_verification = ssl_verification

    def test(self, test_input: Union[str, bytes, _io.BufferedReader]):
        """
        Runs a sample inference test on a single input on chassis model locally

        Args:
            test_input (Union[str, bytes, BufferedReader]): Single sample input data to test model

        Returns:
            bytes: raw model predictions returned by `process_fn` method

        Examples:
        ```python
        chassis_model = chassis_client.create_model(process_fn=process)
        sample_filepath = './sample_data.json'
        results = chassis_model.test(sample_filepath)
        ```
        """
        if isinstance(test_input, _io.BufferedReader):
            result = self.predict(None, test_input.read())
        elif isinstance(test_input, bytes):
            result = self.predict(None, test_input)
        elif isinstance(test_input, str):
            if os.path.exists(test_input):
                result = self.predict(None, open(test_input, 'rb').read())
            else:
                result = self.predict(None, bytes(test_input, encoding='utf8'))
        else:
            print("Invalid input. Must be buffered reader, bytes, valid filepath, or text input.")
            return False
        return result

    def test_batch(self, test_input: Union[str, bytes, _io.BufferedReader]):
        """
        Takes a single input file, creates a batch of size `batch_size` defined in `ChassisModel.create_model`, and runs a batch job against chassis model locally if `batch_process_fn` is defined.

        Args:
            test_input (Union[str, bytes, BufferedReader]): Batch of sample input data to test model

        Returns:
            bytes: raw model predictions returned by `batch_process_fn` method

        Examples:
        ```python
        chassis_model = chassis_client.create_model(process_fn=process)
        sample_input = sample_filepath = './sample_data.json'
        results = chassis_model.test_batch(sample_filepath)
        ```
        """
        if not self.batch_input:
            raise NotImplementedError("Batch inference not implemented.")

        if hasattr(self, 'batch_predict'):
            batch_method = self.batch_predict
        else:
            batch_method = self.predict

        if isinstance(test_input, _io.BufferedReader):
            results = batch_method(None, [test_input.read() for _ in range(self.batch_size)])
        elif isinstance(test_input, bytes):
            results = batch_method(None, [test_input for _ in range(self.batch_size)])
        elif isinstance(test_input, str):
            if os.path.exists(test_input):
                results = batch_method(None, [open(test_input, 'rb').read() for _ in range(self.batch_size)])
            else:
                results = batch_method(None, [bytes(test_input, encoding='utf8') for _ in range(self.batch_size)])
        else:
            print("Invalid input. Must be buffered reader, bytes, valid filepath, or text input.")
            return False
        return results

    def save(self, path: str, requirements: Union[str, dict] = None, overwrite=False, fix_env=False, gpu=False, arm64=False):
        pass

    def publish(self, model_name: str, model_version: str, registry_user=None, registry_pass=None, requirements=None, fix_env=True, gpu=False, arm64=False, sample_input_path=None, webhook=None):
        pass
