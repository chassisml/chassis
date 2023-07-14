import os.path
import shutil
import tempfile

from .packageable import PACKAGE_DATA_PATH


class Package:

    def __init__(self, model_name: str, model_version: str, batch_size: int = 1, python_version: str = "3.9", arch: str = "amd64", use_gpu: bool = False, base_dir: str = None):
        self.model_name = model_name
        self.model_version = model_version
        self.batch_size = batch_size
        self.python_version = python_version
        self.arch = arch
        self.use_gpu = use_gpu

        self.base_dir = base_dir if not None else tempfile.mkdtemp()
        self.data_dir = os.path.join(self.base_dir, PACKAGE_DATA_PATH)

    def cleanup(self):
        shutil.rmtree(self.base_dir)
