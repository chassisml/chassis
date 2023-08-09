from grpclib.client import Channel

from chassis.protos.v1.model_grpc import ModzyModelStub
from chassis.protos.v1.model_pb2 import RunRequest, RunResponse, ShutdownRequest, StatusRequest, StatusResponse


class OMIClient:
    """
    Provides a convenient client for interacting with a model running the OMI (Open Model Interface)
    server.

    Example:
        ```python
        async def client_test():
            async with OMIClient("localhost", 45000) as client:
                status = await client.status()
                print(f"Status: {status}")
                req = RunRequest(
                    inputs=[
                        InputItem(input={"input": b"testing one two three"})
                    ]
                )
                res = await client.run(req)
                result = res.outputs[0].output["results.json"]
                print(f"Result: {result}")

        asyncio.run(client_test())
        ```
    """

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.channel = Channel(host, port, ssl=False)
        self.client = ModzyModelStub(self.channel)

    def __del__(self):
        self.channel.close()

    async def __aenter__(self) -> 'OMIClient':
        try:
            status_response: StatusResponse = await self.client.Status(StatusRequest())
            if status_response.status_code != 200:
                raise "Model did not initialize successfully"
        except Exception as e:
            print(f"Error connecting to model running on '{self.host}:{self.port}': {e}")
            raise e
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.channel.close()

    async def status(self) -> StatusResponse:
        return await self.client.Status(StatusRequest())

    async def run(self, req: RunRequest) -> RunResponse:
        return await self.client.Run(req)

    async def shutdown(self):
        await self.client.Shutdown(ShutdownRequest())
