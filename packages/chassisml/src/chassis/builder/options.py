import dataclasses
from typing import Union


@dataclasses.dataclass
class BuildOptions:
    base_dir: str = None
    arch: Union[str, list[str]] = "amd64"
    use_gpu: bool = False
    python_version: str = "3.9"
    server: str = "omi"


DefaultBuildOptions = BuildOptions()
