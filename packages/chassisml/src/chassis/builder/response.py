import dataclasses
from typing import Union

from docker.errors import BuildError as DockerBuildError


@dataclasses.dataclass
class BuildResponse:
    image_tag: str
    logs: str
    success: bool
    error_message: Union[str, None]


class BuildError(RuntimeError):
    def __init__(self, error: DockerBuildError, logs: str = None):
        super().__init__(error)
        self.logs = logs
