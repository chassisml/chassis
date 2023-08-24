from __future__ import annotations

import dataclasses
import platform
from typing import List, Optional, Union


@dataclasses.dataclass
class BuildOptions:
    """
    Configures how the resulting Chassis container will be built.

    By default, it will configure the build to use:
        - your machine's native CPU architecture (or `amd64` if it can't be
          determined by `platform.machine()`)
        - use Python 3.9 as the Python version in the container
        - the Open Model Interface server

    When using [chassis.builder.DockerBuilder][], only a single architecture is
    supported. When using [chassis.builder.RemoteBuilder][], a multi-architecture
    build can be specified. To do a multi-architecture build, supply a list of
    architectures that you want to build for. The `RemoteBuilder` will then
    build each variant and deploy them all under a manifest located at the image
    tag. Clients that then pull that image tag will receive the container
    image appropriate for their native architecture.

    When setting the Python version, you can use either minor version or full
    patch version (e.g. "3.9" or "3.9.17"). The version will be used to set the
    base image to the corresponding official `python` image on Docker Hub.

    To enable GPU support, you can set `cuda_version` to a string. The string
    should match the version on one of the available image tags for `nvidia/cuda`
    on Docker Hub. Note: Due to limitations with the `nvidia/cuda` image, only
    Python 3.8 is currently supported for GPU-enabled images.

    Chassis supports building container images that support either the
    Open Model Interface standard or the standard(s) supported by KServe.
    Use "omi" or "kserve" as the `server` value.

    Unless `base_dir` is provided, a temporary directory will be used to stage
    all the resources. If `base_dir` is supplied, it will use that directory,
    which is expected to already exist and be empty. Setting `base_dir` is
    mostly useful for testing, developing Chassis itself, or if you want to use
    something other than Docker (but that supports using Dockerfiles) to build
    the container.

    Attributes:
        arch: List of target platforms to build and compile container versions.
            See above for more information.
        python_version: Python version to build into container. Python v3.8 or
            greater supported.
        cuda_version: CUDA version if model supports GPU.
        server: Server specification to build. "omi" and "kserve" supported.
        base_dir: Optional directory path to save the build context.
    """
    base_dir: Optional[str] = None
    arch: Union[str, List[str]] = platform.machine() or "amd64"
    python_version: str = "3.9"
    cuda_version: Optional[str] = None
    server: str = "omi"


DefaultBuildOptions = BuildOptions()
