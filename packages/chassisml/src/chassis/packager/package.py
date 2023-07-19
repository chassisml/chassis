import os.path
import platform
import shutil
import tempfile
from shutil import copy, copytree

import cloudpickle
from jinja2 import Environment, PackageLoader, select_autoescape

from chassis.metadata import ModelMetadata
from chassis.protos.v1.model_pb2 import StatusResponse
from chassis.runtime import PACKAGE_DATA_PATH, python_pickle_filename_for_key
from .packageable import Packageable

env = Environment(
    loader=PackageLoader(package_name="chassis.packager"),
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


class Package:

    def __init__(self, model_name: str, model_version: str, model: Packageable, metadata: ModelMetadata = None):
        self.model_name = model_name
        self.model_version = model_version
        self.model = model
        if metadata is not None:
            self.metadata = metadata
        else:
            md = ModelMetadata.default()
            md.info.model_name = model_name
            md.info.model_version = model_version
            self.metadata = md

        # Initialize the variables we'll use to hold path references.
        self._base_dir = None
        self._chassis_dir = None
        self._data_dir = None

    def create(self, base_dir=None, arch="amd64", use_gpu=False, python_version="3.9"):
        self._base_dir = base_dir if not None else tempfile.mkdtemp()
        self._chassis_dir = os.path.join(self._base_dir, "chassis")
        self._data_dir = os.path.join(self._base_dir, PACKAGE_DATA_PATH)

        self._prepare_context(arch=arch, python_version=python_version, use_gpu=use_gpu)
        self._write_requirements(self.model.requirements)
        self._write_python_modules(self.model.python_modules)

    def cleanup(self):
        if os.path.exists(self._base_dir):
            shutil.rmtree(self._base_dir)

    def _write_additional_files(self, files: set[str]):
        for file in files:
            copy(file, os.path.join(self._data_dir, os.path.basename(file)))

    def _write_requirements(self, reqs=None):
        if reqs is None:
            reqs = []
        requirements_template = env.get_template("requirements.txt")
        # Convert to a set then back to a list to unique the entries in case there are duplicates.
        additional_requirements = list(set(reqs))
        # Sort the list so that our requirements.txt is stable for Docker caching.
        additional_requirements.sort()
        rendered_template = requirements_template.render(
            additional_requirements="\n".join(additional_requirements)
        )
        with open(os.path.join(self._base_dir, "requirements.txt"), "wb") as f:
            f.write(rendered_template.encode("utf-8"))

    def _write_python_modules(self, modules: dict):
        for key, m in modules.items():
            output_filename = python_pickle_filename_for_key(key)
            with open(os.path.join(self._data_dir, output_filename), "wb") as f:
                cloudpickle.dump({key: m}, f)

    def _write_metadata(self, md: ModelMetadata):
        sr = StatusResponse()
        sr.model_info.CopyFrom(md.info)
        sr.description.CopyFrom(md.description)
        sr.inputs.MergeFrom(md.inputs)
        sr.outputs.MergeFrom(md.outputs)
        sr.resources.CopyFrom(md.resources)
        sr.timeout.CopyFrom(md.timeout)
        sr.features.CopyFrom(md.features)

        data = sr.SerializeToString()

        with open(os.path.join(self._data_dir, "model_info"), "wb") as f:
            f.write(data)

    def _prepare_context(self, arch="amd64", python_version="3.9", use_gpu=False):
        print("Using build directory: " + self._base_dir)
        # Ensure the target directories exist.
        if not os.path.exists(self._chassis_dir):
            os.makedirs(self._chassis_dir, exist_ok=True)
        if not os.path.exists(self._data_dir):
            os.makedirs(self._data_dir, exist_ok=True)

        # Render and save Dockerfile to package location.
        dockerfile_template = env.get_template("Dockerfile")
        rendered_template = dockerfile_template.render(
            arch=_convert_arch_to_container_arch(arch),
            python_version=python_version,
            needs_cross_compiling=_needs_cross_compiling(arch),
            use_gpu=use_gpu,
        )
        with open(os.path.join(self._base_dir, "Dockerfile"), "wb") as f:
            f.write(rendered_template.encode("utf-8"))

        # Save .dockerignore to package location.
        dockerignore_template = env.get_template(".dockerignore")
        dockerignore = dockerignore_template.render()
        with open(os.path.join(self._base_dir, ".dockerignore"), "wb") as f:
            f.write(dockerignore.encode("utf-8"))

        # Save an empty requirements.txt so we ensure the file is there.
        # It will be overwritten if the user calls `write_requirements`.
        self._write_requirements("")

        # Save a default model.yaml file to ensure the file is there.
        # It may be overwritten if the user calls `write_metadata`.
        self._write_metadata(self.metadata)

        # Save the entrypoint file.
        entrypoint_template = env.get_template("entrypoint.py")
        with open(os.path.join(self._base_dir, "entrypoint.py"), "wb") as f:
            f.write(entrypoint_template.render().encode("utf-8"))

        # # Copy any Chassis libraries we need.
        self._copy_libraries(dockerignore.splitlines())

    def _copy_libraries(self, ignore_patterns: list[str]):
        root = os.path.join(os.path.dirname(__file__), "..", "..")
        ignore = shutil.ignore_patterns(*ignore_patterns)
        copytree(os.path.join(root, "chassis", "runtime"), os.path.join(self._chassis_dir, "runtime"), ignore=ignore)
        copytree(os.path.join(root, "chassis", "metadata"), os.path.join(self._chassis_dir, "metadata"), ignore=ignore)
        copytree(os.path.join(root, "chassis", "server", "omi"), os.path.join(self._chassis_dir, "server", "omi"), ignore=ignore)
        # TODO - kserve
