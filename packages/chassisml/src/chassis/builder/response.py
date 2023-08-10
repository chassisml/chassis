from __future__ import annotations

import dataclasses
from typing import Union

from docker.errors import BuildError as DockerBuildError


@dataclasses.dataclass
class BuildResponse:
    image_tag: Union[str, None]
    logs: Union[str, None]
    success: bool
    completed: bool
    error_message: Union[str, None]
    remote_build_id: Union[str, None]

    def __str__(self):
        lines = []
        if self.remote_build_id is not None:
            lines.append(f"Remote Build ID: {self.remote_build_id}")
        lines.append(f"Completed:       {self.completed}")
        lines.append(f"Success:         {self.success}")
        if self.image_tag is not None:
            lines.append(f"Image Tag:       {self.image_tag}")
        if self.error_message is not None:
            lines.append(f"Error:           {self.error_message}")
        return "\n".join(lines)


class BuildError(RuntimeError):
    def __init__(self, error: DockerBuildError, logs: str = None):
        super().__init__(error)
        self.logs = logs
