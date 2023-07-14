import os.path
import platform
import shutil
import tempfile
from distutils.dir_util import copy_tree
from shutil import copy

from jinja2 import Environment, PackageLoader, select_autoescape

from .packageable import PACKAGE_DATA_PATH

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

    def __init__(self, model_name: str, model_version: str, batch_size: int = 1, python_version: str = "3.9", arch: str = "amd64", use_gpu: bool = False, base_dir: str = None):
        self.model_name = model_name
        self.model_version = model_version
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
        with open(os.path.join(self.base_dir, "model.pkl"), "wb") as f:
            block(f)

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
        with open(os.path.join(self.base_dir, ".dockerignore"), "wb") as f:
            f.write(dockerignore_template.render().encode("utf-8"))

        # Save an empty requirements.txt so we ensure the file is there.
        # It will be overridden if the user calls `write_requirements`.
        self.write_requirements("")

        # # Save the entrypoint file.
        # entrypoint_template = env.get_template("entrypoint.py")
        # with open(os.path.join(self.base_dir, "entrypoint.py"), "wb") as f:
        #     f.write(entrypoint_template.render().encode("utf-8"))

        # # Copy any Chassis libraries we need.
        self._copy_libraries()

    def cleanup(self):
        shutil.rmtree(self.base_dir)

    def _copy_libraries(self):
        root = os.path.join(os.path.dirname(__file__), "..", "..")
        # copy(os.path.join(root, "metadata.py"), self.chassis_dir)
        copy_tree(os.path.join(root, "chassis", "runtime"), os.path.join(self.chassis_dir, "runtime"))
