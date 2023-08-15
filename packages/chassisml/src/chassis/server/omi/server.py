from __future__ import annotations

import asyncio
import logging
import os
import signal
import traceback
from time import time as t
from typing import Mapping, Optional, Union

from grpclib.health.service import Health
from grpclib.reflection.service import ServerReflection
from grpclib.server import Server, Stream
from grpclib.utils import graceful_exit

from chassis.protos.v1.model_grpc import ModzyModelBase
from chassis.protos.v1.model_pb2 import (
    OutputItem,
    RunRequest,
    RunResponse,
    ShutdownResponse,
    StatusResponse,
)
from chassis.runtime import ModelRunner, PACKAGE_DATA_PATH

GRPC_SERVER_PORT = 45000

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def log_stack_trace():
    # TODO: we could potentially extract even more information from: stack_trace = e.__traceback__ if we notice
    #   that things are very hard to debug from the platform in the current state.
    stack_trace_formatted = traceback.format_exc()
    LOGGER.critical(stack_trace_formatted)


class ModzyModel(ModzyModelBase):
    def __init__(self) -> None:
        self.model: Optional[ModelRunner] = None

        with open(os.path.join(PACKAGE_DATA_PATH, "model_info"), "rb") as f:
            data = f.read()

        sr = StatusResponse()
        sr.ParseFromString(data)
        self.metadata = sr

    def _build_status_response(self, status_code: int, message: str) -> StatusResponse:
        status = "OK"
        if status_code != 200:
            status = "Internal Server Error"
        sr = StatusResponse()
        sr.MergeFrom(self.metadata)
        sr.status_code = status_code
        sr.status = status
        sr.message = message
        return sr

    async def Status(self, stream: Stream):
        _ = await stream.recv_message()
        start_status_call = t()
        if self.model is None:
            self.model = ModelRunner.load()
            if self.model is None:
                # If there is a problem in loading the model, catch it and report the error
                message = "Model Failed to Initialize."
                log_stack_trace()
                status_response = self._build_status_response(500, message)
            else:
                message = "Model Initialized Successfully."
                LOGGER.info(message)
                status_response = self._build_status_response(200, message)
        else:
            # The model is treated as a singleton that cannot be reloaded. If the model has already been initialized,
            message = "Model Already Initialized."
            LOGGER.warning(message)
            status_response = self._build_status_response(200, message)
        LOGGER.info(
            f"The model is {'not ' if self.model is None else ''}loaded.\n"
            f"Features: "
            f"Batch Size {self.metadata.features.batch_size}, "
            f"Adversarial Defence = {self.metadata.features.adversarial_defense}, "
            f"Drift Detection = {len(self.metadata.features.drift_format) > 0}, "
            f"Explainable = {len(self.metadata.features.explanation_format) > 0}, "
            f"Retrainable = {self.metadata.features.retrainable}"
        )
        LOGGER.info(f"Completed call to Status Route in {t() - start_status_call}")
        await stream.send_message(status_response)

    async def Run(self, stream: Stream):
        request: RunRequest = await stream.recv_message()
        start_run_call = t()
        response = RunResponse()
        outputs = []

        if self.model is None:
            # If the model has not been initialized, every input in the batch produces an error
            for _ in request.inputs:
                output_item = create_output_item(
                    "Failed to process model input. Model has not been initialized for inference."
                )
                response.outputs.append(output_item)
            return response
        else:
            try:
                input_length = len(request.inputs)
                raw_outputs = self.model.predict([input_item.input for input_item in
                                                  request.inputs])
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

    async def Shutdown(self, stream: Stream):
        _ = await stream.recv_message()
        shutdown_response = ShutdownResponse(
            status_code=200,
            status="OK",
            message="Model Shutdown Successfully.",
        )
        self.model = None
        await stream.send_message(shutdown_response)
        # Currently there is a problem calling `close()` on the gRPC server object.
        # This is a much less graceful way to handle it but it works.
        # NOTE: we have to call kill twice because the first one attempts a graceful
        # shutdown which is the thing that's broken. If a second signal is sent then
        # it will kill the process.
        os.kill(os.getpid(), signal.SIGTERM)
        os.kill(os.getpid(), signal.SIGTERM)


def create_output_item(message, data: Optional[Mapping[str, bytes]] = None):
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
    return os.getenv("PSC_MODEL_PORT", default=GRPC_SERVER_PORT)


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
