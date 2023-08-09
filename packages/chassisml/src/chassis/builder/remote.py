from __future__ import annotations

import json
import os.path
import shutil
import tempfile
import urllib.parse
from typing import TYPE_CHECKING
from .buildable import Buildable
from .options import BuildOptions, DefaultBuildOptions
import requests
import validators
from .utils import sanitize_image_name

from .response import BuildResponse
if TYPE_CHECKING:
    # This import is placed like this to prevent a circular dependency while still allowing type checking in an IDE.
    from chassisml.v1.chassis_client import ChassisClient


class RemoteBuilder:
    def __init__(self, client: ChassisClient, package: Buildable, options: BuildOptions = DefaultBuildOptions):
        '''Builder object that connects to a remote Kubernetes Chassis server to build containers from `Buildable` objects
        
        Args:
            client (ChassisClient): Chassis client that handles all communication with remote Chassis service
            package (Buildable): Chassis model object that serves as the primary model code to be containerized
            options (BuildOptions): Object that provides specific build configuration options. See `chassis.builder.BuildOptions` for more details
        '''        
        self.client = client
        self.context = package.prepare_context(options)

    def build_image(self, name: str, tag="latest", timeout: int = 3600, webhook: str = None, clean_context=True) -> BuildResponse:
        '''Kicks off a remote container build job and pushes to pre-configured Docker registry
        
        Args:
            name (str): Name of container image repository
            tag (str): Tag of container image
            timeout (int): Timeout value passed to build config object
            webhook (str): TODO
            clean_context (bool): If False does not remove build context folder
        
        Returns:
            BuildResponse: `BuildResponse` object with details from the build job
            
        Raises:
            ValueError: If webhook is not valid URL
            
        Examples:
        ```python
        from chassisml import ChassisModel, ChassisClient
        from chassis.builder import RemoteBuilder
        
        model = ChassisModel(process_fn=predict)
        client = ChassisClient("http://localhost:8080)
        builder = RemoteBuilder(client, model)
        res = builder.build_image(name="chassis-model")      
        ```
        '''        
        if webhook is not None and not validators.url(webhook):
            raise ValueError("Provided webhook is not a valid URL")

        tmpdir = None
        build_context = None
        try:
            # Zip up the build context.
            tmpdir = tempfile.mkdtemp()
            package_basename = os.path.join(tmpdir, "package")
            package_filename = shutil.make_archive(package_basename, "zip", self.context.base_dir)

            # Construct the build arguments.
            build_config = {
                "image_tag": sanitize_image_name(name, tag),
                "platform": ",".join(self.context.platforms),
                "webhook": webhook,
                "timeout": timeout,
            }

            # Construct our request headers.
            headers = {
                "User-Agent": "ChassisClient/1.5"
            }
            if self.client.auth_header is not None:
                headers["Authorization"] = self.client.auth_header

            # Compile the files we're going to upload.
            build_context = open(package_filename, "rb")
            files = [
                ("build_config", json.dumps(build_config)),
                ("build_context", build_context),
            ]

            # Submit the build request.
            url = urllib.parse.urljoin(self.client.base_url, "/build")
            response = requests.post(url, headers=headers, files=files, verify=self.client.ssl_verification)
            response.raise_for_status()

            obj = response.json()
            build_response = BuildResponse(**obj)
            print(f"Job has been submitted with id {build_response.remote_build_id}")

            if clean_context:
                print("Cleaning local context")
                self.context.cleanup()

            return build_response
        finally:
            # Clean up
            if build_context is not None and not build_context.closed:
                build_context.close()
            if tmpdir is not None and os.path.exists(tmpdir):
                shutil.rmtree(tmpdir)
