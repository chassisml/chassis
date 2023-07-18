import os.path
import platform
import shutil
import tempfile
from shutil import copy, copytree

from jinja2 import Environment, PackageLoader, select_autoescape

from chassis.metadata import ModelMetadata
from chassis.protos.v1.model_pb2 import StatusResponse
from .packageable import PACKAGE_DATA_PATH

env = Environment(
    loader=PackageLoader(package_name="chassisml.packager"),
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

    def __init__(self, model_name: str, model_version: str, metadata: ModelMetadata = None, batch_size: int = 1, python_version: str = "3.9", arch: str = "amd64", use_gpu: bool = False, base_dir: str = None):
        self.model_name = model_name
        self.model_version = model_version
        if metadata is not None:
            self.metadata = metadata
        else:
            md = ModelMetadata.default()
            md.info.model_name = model_name
            md.info.model_version = model_version
            self.metadata = md
        self.metadata.info.model_name = model_name
        self.batch_size = batch_size
        self.python_version = python_version
        self.arch = arch
        self.use_gpu = use_gpu

        self.base_dir = base_dir if not None else tempfile.mkdtemp()
        self.chassis_dir = os.path.join(self.base_dir, "chassis")
        self.data_dir = os.path.join(self.base_dir, PACKAGE_DATA_PATH)

    def write_additional_files(self, files: set[str]):
        for file in files:
            copy(file, os.path.join(self.data_dir, os.path.basename(file)))

    def write_requirements(self, reqs=None):
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
        with open(os.path.join(self.base_dir, "requirements.txt"), "wb") as f:
            f.write(rendered_template.encode("utf-8"))

    def write_model_pickle_file(self, block):
        with open(os.path.join(self.data_dir, "model.pkl"), "wb") as f:
            block(f)

    def write_metadata(self, md: ModelMetadata):
        sr = StatusResponse()
        sr.model_info.CopyFrom(md.info)
        sr.description.CopyFrom(md.description)
        sr.inputs.MergeFrom(md.inputs)
        sr.outputs.MergeFrom(md.outputs)
        sr.resources.CopyFrom(md.resources)
        sr.timeout.CopyFrom(md.timeout)
        sr.features.CopyFrom(md.features)

        data = sr.SerializeToString()

        with open(os.path.join(self.data_dir, "model_info"), "wb") as f:
            f.write(data)

    def prepare_context(self):
        print("Using build directory: " + self.base_dir)
        # Ensure the target directories exist.
        if not os.path.exists(self.chassis_dir):
            os.makedirs(self.chassis_dir, exist_ok=True)
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)

        # Render and save Dockerfile to package location.
        dockerfile_template = env.get_template("Dockerfile")
        rendered_template = dockerfile_template.render(
            arch=_convert_arch_to_container_arch(self.arch),
            python_version=self.python_version,
            needs_cross_compiling=_needs_cross_compiling(self.arch)
        )
        with open(os.path.join(self.base_dir, "Dockerfile"), "wb") as f:
            f.write(rendered_template.encode("utf-8"))

        # Save .dockerignore to package location.
        dockerignore_template = env.get_template(".dockerignore")
        dockerignore = dockerignore_template.render()
        with open(os.path.join(self.base_dir, ".dockerignore"), "wb") as f:
            f.write(dockerignore.encode("utf-8"))

        # Save an empty requirements.txt so we ensure the file is there.
        # It will be overwritten if the user calls `write_requirements`.
        self.write_requirements("")

        # Save a default model.yaml file to ensure the file is there.
        # It may be overwritten if the user calls `write_metadata`.
        self.write_metadata(self.metadata)

        # Save the entrypoint file.
        entrypoint_template = env.get_template("entrypoint.py")
        with open(os.path.join(self.base_dir, "entrypoint.py"), "wb") as f:
            f.write(entrypoint_template.render().encode("utf-8"))

        # # Copy any Chassis libraries we need.
        self._copy_libraries(dockerignore.splitlines())

    def cleanup(self):
        shutil.rmtree(self.base_dir)

    def _copy_libraries(self, ignore_patterns: list[str]):
        root = os.path.join(os.path.dirname(__file__), "..", "..")
        ignore = shutil.ignore_patterns(*ignore_patterns)
        copytree(os.path.join(root, "chassis", "runtime"), os.path.join(self.chassis_dir, "runtime"), ignore=ignore)
        copytree(os.path.join(root, "chassis", "metadata"), os.path.join(self.chassis_dir, "metadata"), ignore=ignore)
        copytree(os.path.join(root, "chassis", "server", "omi"), os.path.join(self.chassis_dir, "server", "omi"), ignore=ignore)
        # TODO - kserve
