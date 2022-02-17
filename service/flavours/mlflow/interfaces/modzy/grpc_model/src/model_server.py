import logging
import os
import traceback
from concurrent import futures
from time import time as t
from typing import Dict, List

import grpc
from grpc_reflection.v1alpha import reflection

from ...grpc_model import GRPC_SERVER_PORT as _GRPC_SERVER_PORT
from ...grpc_model.src.auto_generated.model2_template.model_pb2 import (
    DESCRIPTOR,
    ModelDescription,
    ModelFeatures,
    ModelInfo,
    ModelInput,
    ModelOutput,
    ModelResources,
    ModelTimeout,
    OutputItem,
    RunResponse,
    ShutdownResponse,
    StatusResponse,
)
from ...grpc_model.src.auto_generated.model2_template.model_pb2_grpc import (
    ModzyModelServicer,
    add_ModzyModelServicer_to_server,
)
from ...grpc_model.src.utils import (
    InputOutputMismatchException,
    ModelVersionNotSynchronizedException,
    model_version_is_synchronized,
    parse_complete_model_yaml,
)
from ...model_lib.src.model import ExampleModel

MAX_WORKERS = 1

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def log_stack_trace():
    # TODO: we could potentially extract even more information from: stack_trace = e.__traceback__ if we notice
    #   that things are very hard to debug from the platform in the current state.
    stack_trace_formatted = traceback.format_exc()
    LOGGER.critical(stack_trace_formatted)


class ModzyModel(ModzyModelServicer):
    def __init__(self):

        self.model = None
        (info, description, inputs, outputs, resources, timeout, features) = parse_complete_model_yaml()

        self.adversarial_defense = features[0]
        self.batch_size = features[1]
        self.drift_detection = features[4] is not None
        self.explainable = features[5] is not None
        self.retrainable = features[2]

        self.info = ModelInfo(
            model_name=info[0], model_version=info[1], model_author=info[2], model_type=info[3], source=info[4]
        )

        self.description = ModelDescription(
            summary=description[0], details=description[1], technical=description[2], performance=description[3]
        )

        self.inputs = [
            ModelInput(
                filename=input_[0],
                accepted_media_types=["not provided"] if input_[1] == [None] else input_[1],
                max_size=input_[2],
                description=input_[3],
            )
            for input_ in inputs
        ]

        self.outputs = [
            ModelOutput(filename=output[0], media_type=output[1], max_size=output[2], description=output[3])
            for output in outputs
        ]

        self.resources = ModelResources(required_ram=resources[0], num_cpus=resources[1], num_gpus=resources[2])

        self.timeout = ModelTimeout(status=timeout[0], run=timeout[1])

        self.features = ModelFeatures(
            adversarial_defense=features[0],
            batch_size=features[1],
            retrainable=features[2],
            results_format=features[3],
            drift_format=features[4],
            explanation_format=features[5],
        )

    def Status(self, request, context):
        start_status_call = t()
        if self.model is None:
            try:
                # If this is the first time calling the `Status` route, then attempt to load the model
                self.model = ExampleModel()
                message = "Model Initialized Successfully."
                LOGGER.info(message)
                status_response = StatusResponse(
                    status_code=200,
                    status="OK",
                    message=message,
                    model_info=self.info,
                    description=self.description,
                    inputs=self.inputs,
                    outputs=self.outputs,
                    resources=self.resources,
                    timeout=self.timeout,
                    features=self.features,
                )

            except Exception as e:
                # If there is a problem in loading the model, catch it and report the error
                message = "Model Failed to Initialize."
                LOGGER.critical(f"{message} Error: {e}")
                log_stack_trace()
                status_response = StatusResponse(
                    status_code=500,
                    status="Internal Server Error",
                    message=message,
                    model_info=self.info,
                    description=self.description,
                    inputs=self.inputs,
                    outputs=self.outputs,
                    resources=self.resources,
                    timeout=self.timeout,
                    features=self.features,
                )
        else:
            # The model is treated as a singleton that cannot be reloaded. If the model has already been initialized,
            message = "Model Already Initialized."
            LOGGER.warning(message)
            status_response = StatusResponse(
                status_code=200,
                status="OK",
                message=message,
                model_info=self.info,
                description=self.description,
                inputs=self.inputs,
                outputs=self.outputs,
                resources=self.resources,
                timeout=self.timeout,
                features=self.features,
            )
        LOGGER.info(
            f"The model is {'not ' if self.model is None else ''}loaded.\n"
            f"Features: "
            f"Batch Size {self.batch_size}, "
            f"Adversarial Defence = {self.adversarial_defense}, "
            f"Drift Detection = {self.drift_detection}, "
            f"Explainable = {self.explainable}, "
            f"Retrainable = {self.retrainable}"
        )
        LOGGER.info(f"Completed call to Status Route in {t() - start_status_call}")
        return status_response

    def Run(self, request, context):
        start_run_call = t()
        response = RunResponse()
        outputs = []

        if self.model is None:
            # If the model has not been initialized, every input in the batch produces an error
            for _ in range(request.inputs):
                output_item = create_output_item(
                    "Failed to process model input. Model has not been initialized for inference."
                )
                response.outputs.append(output_item)
            return response
        else:
            batch_process = False
            current_batch_size = len(request.inputs)
            if current_batch_size > 1:
                try:
                    raw_outputs: List[Dict[str, bytes]] = self.model.handle_input_batch(
                        [input_item.input for input_item in request.inputs], request.detect_drift, request.explain, self.inputs[0].filename
                    )
                    if current_batch_size != len(raw_outputs):
                        LOGGER.critical(
                            f"The number of outputs from `handle_discrete_input_batch` ({len(raw_outputs)}) does not"
                            f" match the number of inputs ({current_batch_size}). Attempting to fall back."
                        )
                        batch_process = False
                        raise InputOutputMismatchException

                    for i, raw_output in enumerate(raw_outputs):
                        # TODO: It would probably be useful to have an example of explanation/drift metadata here
                        output_item = create_output_item(
                            f"Processed item {i + 1} in batch process of size {current_batch_size}.", raw_output
                        )
                        outputs.append(output_item)
                    batch_process = True
                except NotImplementedError:
                    LOGGER.info("No custom batch processing method found. Implement `handle_discrete_input_batch`.")
                    batch_process = False
                except InputOutputMismatchException:
                    pass
                except Exception as e:
                    LOGGER.critical(f"The batch processing method implemented encountered a fatal error: {e}")
                    log_stack_trace()
                    batch_process = False

            if not batch_process:
                for i, input_item in enumerate(request.inputs):
                    try:
                        raw_output: Dict[str, bytes] = self.model.handle_single_input(
                            input_item.input, request.detect_drift, request.explain, self.inputs[0].filename
                        )
                        # TODO: It would probably be useful to have an example of explanation/drift metadata here
                        output_item = create_output_item(f"Processed item {i + 1} as single input.", raw_output)
                    except Exception as e:
                        # TODO: we could potentially extract even more information from: stack_trace = e.__traceback__
                        log_stack_trace()
                        output_item = create_output_item(
                            f"Failed to process model input. Exception Encountered: {e}"
                        )
                    outputs.append(output_item)

        response = RunResponse(
            status_code=200,
            status="OK",
            message="Inference executed",
        )
        response.outputs.extend(outputs)
        num_inputs = len(request.inputs)
        run_route_time = t() - start_run_call
        LOGGER.info(
            f"Completed call to Run Route with {num_inputs} inputs in {run_route_time}. "
            f"Inputs per second: {num_inputs / run_route_time}"
        )
        return response

    def Shutdown(self, request, context):
        shutdown_response = ShutdownResponse(
            status_code=200,
            status="OK",
            message="Model Shutdown Successfully.",
        )
        self.model = None
        return shutdown_response


def create_output_item(message, data: Dict[str, bytes] = None):
    output_item = OutputItem()
    if data is None:
        # Deals with output items that encapsulate errors
        error_message = message
        LOGGER.error(error_message)

        output_item.success = False
        data = error_message.encode()
        output_item.output["error"] = data
    else:
        LOGGER.info(message)

        output_item.success = True
        for output_filename, file_contents in data.items():
            output_item.output[output_filename] = file_contents
    return output_item


def get_server_port():
    return os.getenv("PSC_MODEL_PORT", default=_GRPC_SERVER_PORT)


def serve():
    model_service = ModzyModel()
    grpc_server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=MAX_WORKERS),
        options=[
            # TODO: this could potentially be filled out using the batch size and the input size with additional logic
            ("grpc.max_send_message_length", 250 * 1024 * 1024),
            ("grpc.max_receive_message_length", 250 * 1024 * 1024),
        ],
    )
    add_ModzyModelServicer_to_server(model_service, grpc_server)

    SERVICE_NAMES = [x.full_name for x in DESCRIPTOR.services_by_name['ModzyModel'].methods]
    SERVICE_NAMES.append(reflection.SERVICE_NAME)
    SERVICE_NAMES_2 = (DESCRIPTOR.services_by_name['ModzyModel'].full_name, reflection.SERVICE_NAME)
    #reflection.enable_server_reflection(tuple(SERVICE_NAMES), grpc_server)
    reflection.enable_server_reflection(SERVICE_NAMES_2, grpc_server)

    server_port = get_server_port()
    grpc_server.add_insecure_port(f"[::]:{server_port}")  # TODO: is this insecure port really what we want?
    grpc_server.start()
    LOGGER.info(f"gRPC Server running on port {server_port}")
    grpc_server.wait_for_termination()


if __name__ == "__main__":
    serve()
