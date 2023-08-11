from __future__ import annotations

import asyncio
import time
from typing import List, Mapping, Union

import docker
from docker.models.containers import Container
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

    def __init__(self, host: str, port: int = 45000, timeout: int = 10):
        self._host = host
        self._port = port
        self._timeout = timeout
        self._channel = Channel(host, port, ssl=False)
        self.client = ModzyModelStub(self._channel)

    def __del__(self):
        self._channel.close()

    def __enter__(self) -> OMIClient:
        for _ in range(self._timeout * 2):
            try:
                status_response: StatusResponse = self.status()
                if status_response.status_code != 200:
                    raise "Model did not initialize successfully"
                return self
            except Exception:
                time.sleep(0.5)
        print(f"Error connecting to model running on '{self._host}:{self._port}'")
        raise "Model server failed to become available in the allotted time"

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

    @classmethod
    def test_container(cls, container_name: str, inputs: List[Mapping[str, bytes]], tag: str = "latest", port: int = 45000, timeout: int = 10, pull: bool = True, detect_drift: bool = False, explain: bool = False):
        """
        Tests a container. This method will use your local Docker engine to spin up the named container,
        perform an inference against it with the given `inputs`, and return the result.

        Args:
            container_name (str): The full name of the container without the tag.
            inputs (list[map[str, bytes]]): A batch of input(s) to perform inference on. See `OMIClient.run` for more information.
            tag (str): The tag of the image to test. Default = "latest"
            port (int): The port on the host that the container should map to. Default = 45000
            timeout (int): A timeout in seconds to wait for the model container to become available. Default = 10
            pull (bool): Whether to pull the image if it doesn't exist in your local image cache. Default = True
            detect_drift (bool): Whether to enable drift detection on models that support it. Default = False
            explain (bool): Whether to enable explainability on models that support it. Default = False


        Returns:
            RunResponse: see `OMIClient.run` for more information.
        """
        # Concat the container name and tag to get the full reference.
        container_tag = f"{container_name}:{tag}"
        # Grab an instance of the Docker client using the current environment.
        docker_client = docker.from_env()
        # List local images that match the supplied repository name.
        local_images = docker_client.images.list(container_name)
        # Check to see if the image (and tag) exist already.
        image_present = False
        for img in local_images:
            if container_tag in img.tags:
                image_present = True
                break

        # If the image is not present then either pull it or return an error if `pull=False`.
        if not image_present:
            if not pull:
                print("Image not present in local image cache and `pull` is set to False")
                return
            print("Pulling image...", end="", flush=True)
            docker_client.images.pull(container_name, tag)
            print("Done!")

        container: Union[Container, None] = None
        try:
            # Start the container configured to expose the port to `localhost`.
            container = docker_client.containers.run(
                image=container_tag,
                auto_remove=True,
                detach=True,
                environment={
                    "PSC_MODEL_PORT": "45000"
                },
                ports={
                    "45000/tcp": port,
                },
                remove=True,
            )

            # Use the OMIClient to run an inference.
            with cls("localhost", port, timeout=timeout) as omi_client:
                return omi_client.run(inputs, detect_drift=detect_drift, explain=explain)
        finally:
            # No matter what happens, kill the container at the end.
            if container is not None:
                container.kill()