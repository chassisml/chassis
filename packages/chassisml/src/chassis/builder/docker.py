import string

import docker
from docker.errors import BuildError as DockerBuildError

from .buildable import Buildable
from .options import BuildOptions, DefaultBuildOptions
from .response import BuildError, BuildResponse
from .utils import sanitize_image_name


class DockerBuilder:

    def __init__(self, package: Buildable, options: BuildOptions = DefaultBuildOptions):
        self.client = docker.from_env()
        self.context = package.prepare_context(options)

    def build_image(self, name: str, tag="latest", cache=False, show_logs=False, clean_context=True) -> BuildResponse:
        try:
            print("Starting Docker build...", end="", flush=True)
            image, logs = self.client.images.build(
                path=self.context.base_dir,
                tag=sanitize_image_name(name, tag),
                rm=not cache,
                forcerm=not cache,
                platform=self.context.platform,
            )
            print("Done!")
            log_output = ""
            if show_logs:
                for log_line in logs:
                    if "stream" in log_line:
                        log_output += log_line["stream"]
                print("Logs:")
                print(log_output)
            print(f"Image ID: {image.id}")
            print(f"Image Tags: {image.tags}")
            if clean_context:
                print("Cleaning context")
                self.context.cleanup()
            return BuildResponse(image_tag=image.tags[0], logs=log_output, success=True, completed=True, error_message=None, remote_build_id=None)
        except DockerBuildError as e:
            print("Error :(")
            log_output = ""
            print("Error in Docker build process. Full logs below:\n\n")
            for log_line in e.build_log:
                if "stream" in log_line:
                    log_output += log_line["stream"]
            print("Logs:")
            print(log_output)
            raise BuildError(e, logs=log_output)
