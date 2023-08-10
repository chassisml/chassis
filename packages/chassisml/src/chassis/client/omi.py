from __future__ import annotations

import asyncio
from typing import List, Mapping

from grpclib.client import Channel

from chassis.protos.v1.model_grpc import ModzyModelStub
from chassis.protos.v1.model_pb2 import RunRequest, InputItem, RunResponse, ShutdownRequest, StatusRequest, StatusResponse


class OMIClient:
    """
    Provides a convenient client for interacting with a model running the OMI (Open Model Interface)
    server.

    Example:
        ```python
        with OMIClient("localhost", 45000) as client:
            status = client.status()
            print(f"Status: {status}")
            res = client.run([{"input": b"testing one two three"}])
            result = res.outputs[0].output["results.json"]
            print(f"Result: {result}")
        ```
    """

    def __init__(self, host: str, port: int = 45000):
        self._host = host
        self._port = port
        self._channel = Channel(host, port, ssl=False)
        self.client = ModzyModelStub(self._channel)

    def __del__(self):
        self._channel.close()

    def __enter__(self) -> 'OMIClient':
        try:
            status_response: StatusResponse = self.status()
            if status_response.status_code != 200:
                raise "Model did not initialize successfully"
        except Exception as e:
            print(f"Error connecting to model running on '{self._host}:{self._port}': {e}")
            raise e
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._channel.close()

    def status(self) -> StatusResponse:
        """
        Queries the model to get its status.

        The first time this method is called it will
        also initialize the model, giving it the opportunity to load any assets or perform
        any setup required to perform inferences.

        Returns:
            StatusResponse
        """
        coroutine = self.client.Status(StatusRequest())
        loop = asyncio.get_event_loop()
        res: StatusResponse = loop.run_until_complete(coroutine)
        return res

    def run(self, inputs: List[Mapping[str, bytes]], detect_drift: bool = False, explain: bool = False) -> RunResponse:
        """
        Perform an inference.

        The `inputs` parameter represents a batch of inputs to send to the model. If the model supports
        batch, then it will process the inputs in groups according to its batch size. If the model does
        not support batch, then it will loop through each input and process it individually.

        Each input in `inputs` is a dictionary that allows multiple pieces of data to be supplied to the model
        for each discrete inference. The key should match the key name expected by the model (e.g. the first
        value supplied in the `ChassisModel.metadata.add_input() method`) and the value should always be
        of type `bytes`. The bytes should be decodable using one of the model's declared media type for
        that key (e.g. `the accepted_media_types` argument in `ChassisModel.metadata.add_input()`).

        To enable drift detection and/or explainability on models that support it, you can set the
        appropriate parameters to `True`.

        In the `RunResponse` object, you will be given a similar structure to the inputs. The `outputs`
        property will be an array that corresponds to the batch of inputs. The index of each item in
        `outputs` will be the inference result for the corresponding index in the `inputs` array. And
        similarly to inputs, each inference result will be a dictionary that can return multiple pieces of
        data per inference. The key and media type of the bytes value should match the values supplied
        in `ChassisModel.metadata.add_output()`.

        Args:
            inputs (List[Mapping[str, bytes]]): The batch of inputs to supply to the model. See above for more information.
            detect_drift (bool): Whether to enable drift detection on models that support it. Default = False
            explain (bool): Whether to enable explainability on models that support it. Default = False

        Returns:
            RunResponse: see above for more details
        """
        req = RunRequest(
            inputs=[
                InputItem(input=i)
                for i in inputs
            ],
            detect_drift=detect_drift,
            explain=explain,
        )
        coroutine = self.client.Run(req)
        loop = asyncio.get_event_loop()
        res: RunResponse = loop.run_until_complete(coroutine)
        return res

    def shutdown(self):
        """
        Tells the model to shut itself down. The container will immediately shut down upon receiving this call.
        """
        coroutine = self.client.Shutdown(ShutdownRequest())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(coroutine)
