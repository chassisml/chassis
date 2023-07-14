from __future__ import annotations

import abc
import os
import posixpath
from typing import Union

PACKAGE_DATA_PATH = "data"


class Packageable(metaclass=abc.ABCMeta):
    packaged = False
    requirements: set[str] = set()
    additional_files: set[str] = set()

    # python_modules: dict = {}

    def merge_package(self, package: Packageable):
        self.requirements = self.requirements.union(package.requirements)
        self.additional_files = self.additional_files.union(package.additional_files)
        # self.python_modules.update(package.python_modules)

    def add_requirements(self, reqs: Union[str, list]):
        if type(reqs) == str:
            self.requirements = self.requirements.union(reqs.splitlines())
        elif type(reqs) == list:
            self.requirements = self.requirements.union(reqs)

    def get_packaged_path(self, path: str):
        return posixpath.join(PACKAGE_DATA_PATH, os.path.basename(path))
