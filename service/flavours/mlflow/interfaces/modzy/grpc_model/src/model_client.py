"""
This is an example of a gRPC Python client for interacting with the Python gRPC Server.
"""

import json
import logging
from typing import Dict

import grpc

from ...grpc_model.src.auto_generated.model2_template.model_pb2 import InputItem, RunRequest, RunResponse, StatusRequest
from ...grpc_model.src.auto_generated.model2_template.model_pb2_grpc import ModzyModelStub
from ...grpc_model.src.model_server import get_server_port

HOST = "localhost"
BATCH_SIZE = 8

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def run(model_input):
    def create_input(input_text: Dict[str, bytes]) -> InputItem:
        input_item = InputItem()
        for input_filename, input_contents in input_text.items():
            input_item.input[input_filename] = input_contents
        return input_item

    def unpack_and_report_outputs(run_response: RunResponse):
        for output_item in run_response.outputs:
            if "error" in output_item.output:
                output = output_item.output["error"]
            else:
                output = output_item.output["results.json"]
            LOGGER.info(f"gRPC client received: {json.loads(output.decode())}")

    port = get_server_port()
    LOGGER.info(f"Connecting to gRPC server on {HOST}:{port}")
    with grpc.insecure_channel(f"{HOST}:{port}") as grpc_channel:
        grpc_client_stub = ModzyModelStub(grpc_channel)
        try:
            grpc_client_stub.Status(StatusRequest())  # Initialize the model
        except Exception:
            LOGGER.error(
                f"It appears that the Model Server is unreachable. Did you ensure it is running on {HOST}:{port}?"
            )
            return

        LOGGER.info(f"Sending single input.")
        run_request = RunRequest(inputs=[create_input(model_input)])
        single_response = grpc_client_stub.Run(run_request)
        unpack_and_report_outputs(single_response)

        LOGGER.info("~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~")

        LOGGER.info(f"Sending batch of input.")
        run_request_batch = RunRequest(inputs=[create_input(model_input) for _ in range(BATCH_SIZE)])
        batch_response = grpc_client_stub.Run(run_request_batch)
        unpack_and_report_outputs(batch_response)


if __name__ == "__main__":
    # For each of the required input files that you have specified in your model.yaml file, add a key with the name of
    # the file to the dictionary below, where the value is the content of your test file as bytes
    test_inputs = {"input.txt": b"Hello, my name is Douglas"}

    run(test_inputs)

    """
    An example pattern for loading in image data from a file

    with open("/path/to/image", "rb") as f:
       test_inputs = {"image": f.read()}
    """
