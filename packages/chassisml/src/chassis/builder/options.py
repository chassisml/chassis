import dataclasses
import platform
from typing import Union


@dataclasses.dataclass
class BuildOptions:
    base_dir: str = None
    arch: Union[str, list[str]] = platform.machine() or "amd64"
    python_version: str = "3.9"
    cuda_version: str = None
    server: str = "omi"


DefaultBuildOptions = BuildOptions()
