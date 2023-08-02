from __future__ import annotations

import abc
import os
import platform
import posixpath
import shutil
from shutil import copy, copytree
from typing import Union

import cloudpickle
from jinja2 import Environment, PackageLoader, select_autoescape

from chassis.builder import BuildContext
from chassis.metadata import ModelMetadata
from chassis.protos.v1.model_pb2 import StatusResponse
from chassis.runtime import PACKAGE_DATA_PATH, python_pickle_filename_for_key
from .options import BuildOptions, DefaultBuildOptions

env = Environment(
    loader=PackageLoader(package_name="chassis.builder"),
    autoescape=select_autoescape()
)


def _needs_cross_compiling(arch: str):
    host_arch = platform.machine()
    if host_arch.lower() in ["x86_64", "amd64"]:
        return arch.lower().startswith("arm")
    return False


def _convert_arch_to_container_arch(arch):
    if arch == "arm64":
        return "aarch64"
    elif arch == "arm" or arch == "arm32":
        return "armv7hf"
    return arch


def _copy_libraries(context: BuildContext, server: str, ignore_patterns: list[str]):
    root = os.path.join(os.path.dirname(__file__), "..", "..")
    ignore = shutil.ignore_patterns(*ignore_patterns)
    copytree(os.path.join(root, "chassis", "runtime"), os.path.join(context.chassis_dir, "runtime"), ignore=ignore)
    copytree(os.path.join(root, "chassis", "metadata"), os.path.join(context.chassis_dir, "metadata"), ignore=ignore)
    copytree(os.path.join(root, "chassis", "typing"), os.path.join(context.chassis_dir, "typing"), ignore=ignore)
    copytree(os.path.join(root, "chassis", "server", server), os.path.join(context.chassis_dir, "server", server), ignore=ignore)


class Buildable(metaclass=abc.ABCMeta):
    packaged = False
    metadata = ModelMetadata.default()
    requirements: set[str] = set()
    additional_files: set[str] = set()
    python_modules: dict = {}

    def merge_package(self, package: Buildable):
        self.requirements = self.requirements.union(package.requirements)
        self.additional_files = self.additional_files.union(package.additional_files)
        self.python_modules.update(package.python_modules)

    def add_requirements(self, reqs: Union[str, list]):
        if type(reqs) == str:
            self.requirements = self.requirements.union(reqs.splitlines())
        elif type(reqs) == list:
            self.requirements = self.requirements.union(reqs)

    def get_packaged_path(self, path: str):
        return posixpath.join(PACKAGE_DATA_PATH, os.path.basename(path))

    def prepare_context(self, options: BuildOptions = DefaultBuildOptions) -> BuildContext:
        container_arch = _convert_arch_to_container_arch(options.arch)
        context = BuildContext(base_dir=options.base_dir, platform="{}/{}".format("linux", container_arch))

        print("Using build directory: " + context.base_dir)
        # Ensure the target directories exist.
        if not os.path.exists(context.chassis_dir):
            os.makedirs(context.chassis_dir, exist_ok=True)
        if not os.path.exists(context.data_dir):
            os.makedirs(context.data_dir, exist_ok=True)

        # Render and save Dockerfile to package location.
        dockerfile_template = env.get_template("Dockerfile")
        rendered_template = dockerfile_template.render(
            arch=container_arch,
            python_version=options.python_version,
            needs_cross_compiling=_needs_cross_compiling(options.arch),
            use_gpu=options.use_gpu,
        )
        with open(os.path.join(context.base_dir, "Dockerfile"), "wb") as f:
            f.write(rendered_template.encode())

        # Save .dockerignore to package location.
        dockerignore_template = env.get_template(".dockerignore")
        dockerignore = dockerignore_template.render()
        with open(os.path.join(context.base_dir, ".dockerignore"), "wb") as f:
            f.write(dockerignore.encode())

        # Save the entrypoint file.
        entrypoint_template = env.get_template("entrypoint.py")
        with open(os.path.join(context.base_dir, "entrypoint.py"), "wb") as f:
            f.write(entrypoint_template.render().encode())

        # # Copy any Chassis libraries we need.
        _copy_libraries(context, options.server, dockerignore.splitlines())

        self._write_metadata(context)
        self._write_requirements(context)
        self._write_additional_files(context)
        self._write_python_modules(context)

        return context

    def _write_additional_files(self, context: BuildContext):
        for file in self.additional_files:
            copy(file, os.path.join(context.data_dir, os.path.basename(file)))

    def _write_requirements(self, context: BuildContext):
        requirements_template = env.get_template("requirements.txt")
        # Convert to a set then back to a list to unique the entries in case there are duplicates.
        additional_requirements = list(set(self.requirements))
        # Sort the list so that our requirements.txt is stable for Docker caching.
        additional_requirements.sort()
        rendered_template = requirements_template.render(
            additional_requirements="\n".join(additional_requirements)
        )
        with open(os.path.join(context.base_dir, "requirements.txt"), "wb") as f:
            f.write(rendered_template.encode("utf-8"))

    def _write_python_modules(self, context: BuildContext):
        for key, m in self.python_modules.items():
            output_filename = python_pickle_filename_for_key(key)
            with open(os.path.join(context.data_dir, output_filename), "wb") as f:
                cloudpickle.dump({key: m}, f)

    def _write_metadata(self, context: BuildContext):
        data = self.metadata.serialize()
        with open(os.path.join(context.data_dir, "model_info"), "wb") as f:
            f.write(data)