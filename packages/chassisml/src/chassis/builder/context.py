import os.path
import shutil
import tempfile
from typing import Union

from chassis.runtime import PACKAGE_DATA_PATH


class BuildContext:
    def __init__(self, base_dir: Union[str, None] = None, platforms: list[str] = None):
        self.base_dir = base_dir if base_dir is not None else tempfile.mkdtemp()
        self.chassis_dir = os.path.join(self.base_dir, "chassis")
        self.data_dir = os.path.join(self.base_dir, PACKAGE_DATA_PATH)
        if platforms is None:
            platforms = ["linux/amd64"]
        self.platforms: list[str] = platforms

    def cleanup(self):
        if os.path.exists(self.base_dir):
            shutil.rmtree(self.base_dir)
