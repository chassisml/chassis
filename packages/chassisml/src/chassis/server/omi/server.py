import asyncio
import logging
import os
import traceback
from time import time as t
from typing import Dict, Union

import cloudpickle
from grpclib.health.service import Health
from grpclib.reflection.service import ServerReflection
from grpclib.server import Server
from grpclib.utils import graceful_exit

from chassis.protos.v1.model_grpc import ModzyModelBase
from chassis.protos.v1.model_pb2 import (
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
from chassis.runtime import ModelRunner
from . import GRPC_SERVER_PORT as _GRPC_SERVER_PORT
from .utils import (
    parse_complete_model_yaml,
)

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def log_stack_trace():
    # TODO: we could potentially extract even more information from: stack_trace = e.__traceback__ if we notice
    #   that things are very hard to debug from the platform in the current state.
    stack_trace_formatted = traceback.format_exc()
    LOGGER.critical(stack_trace_formatted)


class ModzyModel(ModzyModelBase):
    def __init__(self):
        self.model: Union[ModelRunner, None] = None
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

    def _build_status_response(self, status_code: int, message: str):
        status = "OK"
        if status_code != 200:
            status = "Internal Server Error"
        return StatusResponse(
            status_code=status_code,
            status=status,
            message=message,
            model_info=self.info,
            description=self.description,
            inputs=self.inputs,
            outputs=self.outputs,
            resources=self.resources,
            timeout=self.timeout,
            features=self.features,
        )

    async def Status(self, stream):
        request = await stream.recv_message()
        start_status_call = t()
        if self.model is None:
            try:
                # If this is the first time calling the `Status` route, then attempt to load the model
                with open("data/model.pkl", "rb") as f:
                    self.model: ModelRunner = cloudpickle.load(f)
                message = "Model Initialized Successfully."
                LOGGER.info(message)
                status_response = self._build_status_response(200, message)
            except Exception as e:
                # If there is a problem in loading the model, catch it and report the error
                message = "Model Failed to Initialize."
                LOGGER.critical(f"{message} Error: {e}")
                log_stack_trace()
                status_response = self._build_status_response(500, message)
        else:
            # The model is treated as a singleton that cannot be reloaded. If the model has already been initialized,
            message = "Model Already Initialized."
            LOGGER.warning(message)
            status_response = self._build_status_response(200, message)
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
        await stream.send_message(status_response)

    async def Run(self, stream):
        request = await stream.recv_message()
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
            try:
                input_length = len(request.inputs)
                raw_outputs = self.model.predict([input_item.input for input_item in request.inputs])
                for i, raw_output in enumerate(raw_outputs):
                    # TODO: It would probably be useful to have an example of explanation/drift metadata here
                    output_item = create_output_item(
                        f"Processed item {i + 1} of {input_length}.", raw_output
                    )
                    outputs.append(output_item)
            except Exception as e:
                LOGGER.critical(f"Encountered a fatal error: {e}")
                log_stack_trace()

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
        await stream.send_message(response)

    async def Shutdown(self, stream):
        request = await stream.recv_message()
        shutdown_response = ShutdownResponse(
            status_code=200,
            status="OK",
            message="Model Shutdown Successfully.",
        )
        self.model = None
        await stream.send_message(shutdown_response)


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


async def serve():
    services = [ModzyModel(), Health()]
    services = ServerReflection.extend(services)

    # TODO - do we need to increase max message size?
    server = Server(services)

    server_port = get_server_port()
    with graceful_exit([server]):
        await server.start("0.0.0.0", server_port)
        print(f"Serving on :{server_port}")
        await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(serve())
