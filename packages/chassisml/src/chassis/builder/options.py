from __future__ import annotations

import dataclasses
import platform
from typing import List, Union


@dataclasses.dataclass
class BuildOptions:
    '''Object for configuring custom build options
    
    Attributes:
        base_dir (str): Optional directory path to save build context of model container
        arch (Union[str, list[str]]): List of target platforms to build and compile container versions. If multiple provided, the `RemoteBuilder` will build a separate version for each architecture and push them to the designated registry under the same container repository and tag 
        python_version (str): Python version to build into container. Python v3.8 or greater supported
        cuda_version (str): CUDA version if model supports GPU
        server (str): Server specification to build. "omi" and "kserve" supported
    '''
    base_dir: str = None
    arch: Union[str, List[str]] = platform.machine() or "amd64"
    python_version: str = "3.9"
    cuda_version: str = None
    server: str = "omi"


DefaultBuildOptions = BuildOptions()
