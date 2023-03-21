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
PORT = get_server_port()
BATCH_SIZE = 8

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def override_server_URL(_host=HOST, _port=get_server_port()):
    global HOST
    global PORT
    HOST = _host
    PORT = _port

def run(model_input):
    def create_input(input_text: Dict[str, bytes]) -> InputItem:
        input_item = InputItem()
        for input_filename, input_contents in input_text.items():
            input_item.input[input_filename] = input_contents
        return input_item

    def unpack_and_report_outputs(run_response: RunResponse):
        unpacked_results = []
        for output_item in run_response.outputs:
            if "error" in output_item.output:
                output = output_item.output["error"]
                unpacked_results.append(output)
            else:
                output = output_item.output["results.json"]
                unpacked_results.append(output)

            LOGGER.info(f"gRPC client received: {json.loads(output.decode())}")
        return unpacked_results


    port = PORT
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


        results = []
        if type(model_input) == list:
            LOGGER.info(f"Sending batch of input.")
            #run_request_batch = RunRequest(inputs=[create_input(model_input) for _ in range(BATCH_SIZE)])

            process_cycles = int(len(model_input)/BATCH_SIZE)
            for index in range(process_cycles):
                run_request_batch = RunRequest(inputs=[create_input(input_data) for input_data in model_input[(index*BATCH_SIZE):((index+1)*BATCH_SIZE)]])
                batch_response = grpc_client_stub.Run(run_request_batch)
                results = results + unpack_and_report_outputs(batch_response)

            #process last < BATCH_SIZE group
            run_request_batch = RunRequest(inputs=[create_input(input_data) for input_data in
                                                   model_input[(process_cycles * BATCH_SIZE):]])
            batch_response = grpc_client_stub.Run(run_request_batch)
            results = results + unpack_and_report_outputs(batch_response)

        else:
            LOGGER.info(f"Sending single input.")
            run_request = RunRequest(inputs=[create_input(model_input)])
            single_response = grpc_client_stub.Run(run_request)
            results = results + unpack_and_report_outputs(single_response)

        return results






if __name__ == "__main__":
    # For each of the required input files that you have specified in your model.yaml file, add a key with the name of
    # the file to the dictionary below, where the value is the content of your test file as bytes
    test_inputs = {"input.json": b"[[0.0, 0.0, 0.0, 1.0, 12.0, 6.0, 0.0, 0.0, 0.0, 0.0, 0.0, 11.0, 15.0, 2.0, 0.0, 0.0, 0.0, 0.0, 8.0, 16.0, 6.0, 1.0, 2.0, 0.0, 0.0, 4.0, 16.0, 9.0, 1.0, 15.0, 9.0, 0.0, 0.0, 13.0, 15.0, 6.0, 10.0, 16.0, 6.0, 0.0, 0.0, 12.0, 16.0, 16.0, 16.0, 16.0, 1.0, 0.0, 0.0, 1.0, 7.0, 4.0, 14.0, 13.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 14.0, 9.0, 0.0, 0.0], [0.0, 0.0, 8.0, 16.0, 3.0, 0.0, 1.0, 0.0, 0.0, 0.0, 16.0, 14.0, 5.0, 14.0, 12.0, 0.0, 0.0, 0.0, 8.0, 16.0, 16.0, 9.0, 0.0, 0.0, 0.0, 0.0, 3.0, 16.0, 14.0, 1.0, 0.0, 0.0, 0.0, 0.0, 12.0, 16.0, 16.0, 2.0, 0.0, 0.0, 0.0, 0.0, 16.0, 11.0, 16.0, 4.0, 0.0, 0.0, 0.0, 3.0, 16.0, 16.0, 16.0, 6.0, 0.0, 0.0, 0.0, 0.0, 10.0, 16.0, 10.0, 1.0, 0.0, 0.0], [0.0, 0.0, 5.0, 12.0, 8.0, 0.0, 1.0, 0.0, 0.0, 0.0, 11.0, 16.0, 5.0, 13.0, 6.0, 0.0, 0.0, 0.0, 2.0, 15.0, 16.0, 12.0, 1.0, 0.0, 0.0, 0.0, 0.0, 10.0, 16.0, 6.0, 0.0, 0.0, 0.0, 0.0, 1.0, 15.0, 16.0, 7.0, 0.0, 0.0, 0.0, 0.0, 8.0, 16.0, 16.0, 11.0, 0.0, 0.0, 0.0, 0.0, 11.0, 16.0, 16.0, 9.0, 0.0, 0.0, 0.0, 0.0, 6.0, 12.0, 12.0, 3.0, 0.0, 0.0], [0.0, 0.0, 0.0, 3.0, 15.0, 4.0, 0.0, 0.0, 0.0, 0.0, 4.0, 16.0, 12.0, 0.0, 0.0, 0.0, 0.0, 0.0, 12.0, 15.0, 3.0, 4.0, 3.0, 0.0, 0.0, 7.0, 16.0, 5.0, 3.0, 15.0, 8.0, 0.0, 0.0, 13.0, 16.0, 13.0, 15.0, 16.0, 2.0, 0.0, 0.0, 12.0, 16.0, 16.0, 16.0, 13.0, 0.0, 0.0, 0.0, 0.0, 4.0, 5.0, 16.0, 8.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 16.0, 4.0, 0.0, 0.0], [0.0, 0.0, 10.0, 14.0, 8.0, 1.0, 0.0, 0.0, 0.0, 2.0, 16.0, 14.0, 6.0, 1.0, 0.0, 0.0, 0.0, 0.0, 15.0, 15.0, 8.0, 15.0, 0.0, 0.0, 0.0, 0.0, 5.0, 16.0, 16.0, 10.0, 0.0, 0.0, 0.0, 0.0, 12.0, 15.0, 15.0, 12.0, 0.0, 0.0, 0.0, 4.0, 16.0, 6.0, 4.0, 16.0, 6.0, 0.0, 0.0, 8.0, 16.0, 10.0, 8.0, 16.0, 8.0, 0.0, 0.0, 1.0, 8.0, 12.0, 14.0, 12.0, 1.0, 0.0]]"}

    run(test_inputs)

    """
    An example pattern for loading in image data from a file

    with open("/path/to/image", "rb") as f:
       test_inputs = {"image": f.read()}
    """
