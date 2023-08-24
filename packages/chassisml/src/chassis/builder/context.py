from __future__ import annotations

import os.path
import shutil
import tempfile
from typing import List, Optional

from chassis.runtime import PACKAGE_DATA_PATH


class BuildContext:
    """
    This class provides configuration options for the build context of a
    Chassis model container.
    """

    def __init__(self, base_dir: Optional[str] = None,
                 platforms: Optional[List[str]] = None):
        """
        Init.

        Args:
            base_dir: Optional directory path to save build context of model container
            platforms: List of target platforms to build and compile container
                       versions. If multiple provided, the `RemoteBuilder` will
                       build a separate version for each architecture and push them
                       to the designated registry under the same container repository
                       and tag.
        """
        self.base_dir = base_dir if base_dir is not None else tempfile.mkdtemp()
        self.chassis_dir = os.path.join(self.base_dir, "chassis")
        self.data_dir = os.path.join(self.base_dir, PACKAGE_DATA_PATH)
        if platforms is None:
            platforms = ["linux/amd64"]
        self.platforms: List[str] = platforms

    def cleanup(self):
        """
        Removes the folder used to stage files for the context.
        """
        if os.path.exists(self.base_dir):
            shutil.rmtree(self.base_dir)
