from __future__ import annotations

import docker
from docker.errors import BuildError as DockerBuildError

from .buildable import Buildable
from .options import BuildOptions, DefaultBuildOptions
from .response import BuildError, BuildResponse
from .utils import sanitize_image_name


class DockerBuilder:
    def __init__(self, package: Buildable, options: BuildOptions = DefaultBuildOptions):
        '''Builder object that uses the local Docker daemon on the host machine to build containers from `Buildable` objects
        
        Args:
            package (Buildable): Chassis model object that serves as the primary model code to be containerized
            options (BuildOptions): Object that provides specific build configuration options. See `chassis.builder.BuildOptions` for more details
        '''
        self.client = docker.from_env()
        self.context = package.prepare_context(options)

    def build_image(self, name: str, tag="latest", cache=False, show_logs=False, clean_context=True) -> BuildResponse:
        '''Builds a local container image using the host machine Docker daemon
        
        Args:
            name (str): Name of container image repository
            tag (str): Tag of container image
            cache (bool): If True caches container image layers 
            show_logs (bool): If True shows logs of the completed job (success or failure)
            clean_context (bool): If False does not remove build context folder
        
        Returns:
            BuildResponse: `BuildResponse` object with details from the build job
            
        Raises:
            BuildError: If build job fails
            
        Examples:
        ```python
        from chassisml import ChassisModel
        from chassis.builder import DockerBuilder
        
        model = ChassisModel(process_fn=predict)
        builder = DockerBuilder(model)
        res = builder.build_image(name="chassis-model")
        ```
        '''

        try:
            platform = self.context.platforms[0]
            if len(self.context.platforms) > 1:
                print(f"Warning: DockerBuilder only supports a single platform at a time. We will use the first one: {platform}")
            print("Starting Docker build...", end="", flush=True)
            image, logs = self.client.images.build(
                path=self.context.base_dir,
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
                self.context.cleanup()
