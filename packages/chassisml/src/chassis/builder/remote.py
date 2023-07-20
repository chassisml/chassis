import base64
import dataclasses
import json
import os.path
import shutil
import tempfile

import requests
import validators

from chassisml import ChassisClient
from .context import BuildContext


@dataclasses.dataclass
class Credentials:
    username: str
    password: str

    def encoded(self) -> str:
        authorization_string = f"{self.username}:{self.password}"
        # The base64 encoder requires bytes and returns bytes so we need to encode the
        # input string and then decode the resulting bytes back to a string before
        # returning the value.
        return base64.b64encode(authorization_string.encode()).decode()


class RemoteBuilder:
    def __init__(self, client: ChassisClient, context: BuildContext):
        self.client = client
        self.context = context

    def build_image(self, name: str, tag="latest", credentials: Credentials = None, webhook: str = None, clean_context=True):
        if webhook is not None and validators.url(webhook):
            raise ValueError("Provided webhook is not a valid URL")

        tmpdir = None
        build_context = None
        try:
            # Zip up the build context.
            tmpdir = tempfile.mkdtemp()
            package_filename = os.path.join(tmpdir, "package.zip")
            shutil.make_archive(package_filename, "zip", self.context.base_dir)

            # Construct the build arguments.
            build_config = {
                "image_name": name,
                "tag": tag,
                "publish": True,
                "webhook": webhook,
            }

            # If registry credentials were provided, add them to the build config.
            if credentials is not None:
                build_config["registry_creds"] = credentials.encoded()

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
            print("Starting build job... ", end="", flush=True)
            response = requests.post("", headers=headers, files=files, verify=self.client.ssl_verification)
            response.raise_for_status()

            print("Ok!")

            if clean_context:
                print("Cleaning context")
                self.context.cleanup()

            return response.json()
        finally:
            # Clean up
            print("Cleaning up")
            if build_context is not None and not build_context.closed:
                build_context.close()
            if tmpdir is not None and os.path.exists(tmpdir):
                shutil.rmtree(tmpdir)
