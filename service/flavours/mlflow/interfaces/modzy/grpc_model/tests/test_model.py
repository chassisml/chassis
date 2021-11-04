import json
import os
from typing import Dict, Tuple

import pytest

from grpc_model import TEST_CASES as _TEST_CASES
from grpc_model.src.auto_generated.model2_template.model_pb2 import InputItem, RunRequest, StatusRequest
from grpc_model.src.utils import extract_inputs_outputs_from_yaml
from model_lib.src.model import ExampleModel


@pytest.fixture()
def test_inputs_and_outputs(request) -> Tuple[Dict[str, bytes]]:
    test_case_directory = _TEST_CASES / request.param
    inputs, outputs = extract_inputs_outputs_from_yaml()
    model_input = {}
    for input_filename in inputs:
        input_file_path = test_case_directory / input_filename
        assert os.path.exists(input_file_path) and os.path.isfile(input_file_path), (
            f"Your test case is missing one of the required files specified in your model.yaml. "
            f"We expected to find a file with name {input_filename} on path {input_file_path}"
        )
        with open(input_file_path, "rb") as f:
            model_input[input_filename] = f.read()

    expected_model_output = {}
    for output_filename in outputs:
        output_file_path = test_case_directory / output_filename
        assert os.path.exists(output_file_path) and os.path.isfile(output_file_path), (
            f"Your test case is missing one of the required files specified in your model.yaml. "
            f"We expected to find a file with name {output_filename} on path {output_file_path}"
        )
        # TODO: In the future, we may need to add dedicated support for image files
        file_extension = os.path.splitext(output_file_path)[-1]
        if file_extension == ".json":
            with open(output_file_path, "rb") as f:
                expected_model_output[output_filename] = json.dumps(
                    json.loads(f.read()), separators=(",", ":")
                ).encode()
        else:
            with open(output_file_path, "rb") as f:
                expected_model_output[output_filename] = f.read()
    yield model_input, expected_model_output


class TestModzyModelWrapper:
    """
    This is take the user defined test cases and run them against the model itself to make sure that they are
    producing the desired outputs.
    """

    def test_model_initialization(self):
        ExampleModel()

    @pytest.mark.parametrize("detect_drift", [True, False])
    @pytest.mark.parametrize("explain", [True, False])
    @pytest.mark.parametrize("test_inputs_and_outputs", os.listdir(_TEST_CASES), indirect=True)
    def test_handle_discrete_inputs(self, test_inputs_and_outputs, detect_drift, explain):
        model_input, expected_model_output = test_inputs_and_outputs

        model = ExampleModel()
        actual_output = model.handle_single_input(model_input, detect_drift, explain)

        assert actual_output == expected_model_output  # TODO: is this deep dict comparison correct/sufficient?


@pytest.fixture(scope="module")
def grpc_add_to_server():
    from grpc_model.src.auto_generated.model2_template.model_pb2_grpc import add_ModzyModelServicer_to_server

    return add_ModzyModelServicer_to_server


@pytest.fixture(scope="module")
def grpc_servicer():
    from grpc_model.src.model_server import ModzyModel

    modzy_model = ModzyModel()
    return modzy_model


@pytest.fixture(scope="module")
def grpc_stub(grpc_channel):
    from grpc_model.src.auto_generated.model2_template.model_pb2_grpc import ModzyModelStub

    modzy_model_stub = ModzyModelStub(grpc_channel)
    return modzy_model_stub  # This is a fake channel passed in by pytest-grpc


@pytest.mark.parametrize("batch_size", [1, 8])
@pytest.mark.parametrize("detect_drift", [True, False])
@pytest.mark.parametrize("explain", [True, False])
@pytest.mark.parametrize("test_inputs_and_outputs", os.listdir(_TEST_CASES), indirect=True)
def test_example_model_grpc_integration(grpc_stub, batch_size, detect_drift, explain, test_inputs_and_outputs):
    """
    This takes the user defined test cases and run them through the gRPC server to make sure that they are
    producing the desired outputs and the server and the encoding-decoding is functioning smoothly.
    """
    model_input, expected_output = test_inputs_and_outputs

    run_request = RunRequest()
    for _ in range(batch_size):
        input_item = InputItem(input=model_input)
        run_request.inputs.append(input_item)
    run_request.detect_drift = False
    run_request.explain = False

    # TODO: is there a way to pull this out as a fixture so that it's not called every time?
    #  (only worthwhile if this actually becomes a problem for complex models)
    grpc_stub.Status(StatusRequest())
    actual_run_response = grpc_stub.Run(run_request)

    for i, output_item in enumerate(actual_run_response.outputs):
        assert output_item.success
        assert output_item.output == expected_output
