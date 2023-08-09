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

        asyncio.run(client_test())
        ```
    """

    def __init__(self, host: str, port: int):
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
        coroutine = self.client.Status(StatusRequest())
        loop = asyncio.get_event_loop()
        res: StatusResponse = loop.run_until_complete(coroutine)
        return res

    def run(self, inputs: List[Mapping[str, bytes]], detect_drift: bool = False, explain: bool = False) -> RunResponse:
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
        coroutine = self.client.Shutdown(ShutdownRequest())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(coroutine)
