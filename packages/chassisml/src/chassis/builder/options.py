import dataclasses


@dataclasses.dataclass
class BuildOptions:
    base_dir: str = None
    arch: str = "amd64"
    use_gpu: bool = False
    python_version: str = "3.9"
    server: str = "omi"


DefaultBuildOptions = BuildOptions()
