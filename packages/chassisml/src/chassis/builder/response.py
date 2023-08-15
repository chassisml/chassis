from __future__ import annotations

import dataclasses
from typing import Optional

from docker.errors import BuildError as DockerBuildError


@dataclasses.dataclass
class BuildResponse:
    """
    An object representing the status of a Chassis build.

    This object is used for both local and remote builds. For local builds, this
    object will be returned exactly once at the end of the build process with
    all fields set except for `remote_build_id`.

    For remote builds, this object will be returned each time
    [chassis.builder.RemoteBuilder.get_build_status][] is called and will only
    have all its fields set once the build is complete.

    Attributes:
        image_tag: The URI where the built image was pushed.
        logs: Build logs, if requested.
        success: Whether the build was successful or not.
        completed: Whether the build is finished or not.
        error_message: The error message, if applicable.
        remote_build_id: The unique ID of a remote build, if applicable.
    """

    image_tag: Optional[str]
    logs: Optional[str]
    success: bool
    completed: bool
    error_message: Optional[str]
    remote_build_id: Optional[str]

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
    def __init__(self, error: DockerBuildError, logs: Optional[str] = None):
        super().__init__(error)
        self.logs = logs
