from __future__ import annotations

import docker
from docker.errors import BuildError as DockerBuildError

from .buildable import Buildable
from .options import BuildOptions, DefaultBuildOptions
from .response import BuildError, BuildResponse
from .utils import sanitize_image_name


class DockerBuilder:
    """
    Enables building Chassis images locally using Docker.

    To use this builder, you need to have Docker installed and have access to
    the Docker socket. If your Docker socket is in a non-standard location, use
    the appropriate Docker environment variables to tell the Docker SDK how to
    connect. Any environment variable supported by the official Docker Python
    SDK is supported.
    """

    def __init__(self, package: Buildable, options: BuildOptions = DefaultBuildOptions):
        """
        Init.

        Args:
            package: Chassis model object that serves as the primary model code
                     to be containerized.
            options: Object that provides specific build configuration options.
                     See [chassis.builder.options.BuildOptions][] for more
                     details.
        """
        self._client = docker.from_env()
        self._context = package.prepare_context(options)

    def build_image(self, name: str, tag="latest", cache=False, show_logs=False, clean_context=True) -> BuildResponse:
        """
        Builds a local container image using the host machine Docker daemon.

        To enable faster builds if you're iterating, you can set `cache=True`
        to not remove intermediate containers when the build completes. This
        uses more disk space but can significantly speed up subsequent builds.

        To see the full log output during the Docker build, set `show_logs=True`.

        Note:
            The logs will be printed at the end and will not stream as it's
            executing.

        This method will automatically remove the build context (e.g. the
        temporary folder that all the files were staged in) at the end of the
        build. If you need to troubleshoot the files that are available to the
        Dockerfile, set `clean_context=False` and the directory will not be
        removed at the end of the build, allowing you to inspect it. If you want
        to inspect the context contents _before_ building, see
        [chassisml.ChassisModel.prepare_context][].

        Args:
            name (str): Name of container image repository
            tag (str): Tag of container image.
            cache (bool): If True caches container image layers.
            show_logs (bool): If True shows logs of the completed job.
            clean_context (bool): If False does not remove build context folder.

        Returns:
            A `BuildResponse` object with details from the build job.

        Raises:
            BuildError: If build job fails

        Example:
        ```python
        from chassisml import ChassisModel
        from chassis.builder import DockerBuilder

        model = ChassisModel(process_fn=predict)
        builder = DockerBuilder(model)
        res = builder.build_image(name="chassis-model")
        ```
        """
        try:
            platform = self._context.platforms[0]
            if len(self._context.platforms) > 1:
                print(f"Warning: DockerBuilder only supports a single platform at a time. We will use the first one: {platform}")
            print("Starting Docker build...", end="", flush=True)
            image, logs = self._client.images.build(
                path=self._context.base_dir,
                tag=sanitize_image_name(name, tag),
                rm=not cache,
                forcerm=not cache,
                platform=platform,
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
        finally:
            if clean_context:
                print("Cleaning local context")
                self._context.cleanup()
