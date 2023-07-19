import _io
import os
from typing import Any, Union

from chassis.builder import DockerBuilder
from chassis.packager import Package, Packageable
from chassis.runtime import ModelRunner, PYTHON_MODEL_KEY
from chassis.typing import PredictFunction
from .helpers import deprecated


class ChassisModel(Packageable):

    def __init__(self, process_fn: PredictFunction, batch_size=1, chassis_client=None):
        self.runner = ModelRunner(process_fn, batch_size=batch_size)
        self.python_modules[PYTHON_MODEL_KEY] = self.runner
        if chassis_client is not None:
            self.chassis_client = chassis_client

    def test(self, test_input: Union[str, bytes, _io.BufferedReader, dict[str, bytes], list[dict[str, bytes]]]) -> list[dict[str, Any]]:
        if isinstance(test_input, _io.BufferedReader):
            result = self.runner.predict([{"input": test_input.read()}])
        elif isinstance(test_input, bytes):
            result = self.runner.predict([{"input": test_input}])
        elif isinstance(test_input, str):
            if os.path.exists(test_input):
                data = open(test_input, 'rb').read()
                result = self.runner.predict([{"input": data}])
            else:
                result = self.runner.predict([{"input": bytes(test_input, encoding='utf8')}])
        elif isinstance(test_input, dict):
            result = self.runner.predict([test_input])
        elif isinstance(test_input, list):
            result = self.runner.predict(test_input)
        else:
            raise ValueError("Invalid input. Must be buffered reader, bytes, valid filepath, or text input.")
        return result

    def test_batch(self, test_input: Union[str, bytes, _io.BufferedReader]):
        deprecated("The `test` method now supports supplying batches of inputs.")
        if not self.runner.supports_batch:
            raise NotImplementedError("Batch inference not implemented.")

        if isinstance(test_input, _io.BufferedReader):
            data = test_input.read()
            inputs = [{"input": data} for _ in range(self.runner.batch_size)]
            return self.test(inputs)
        elif isinstance(test_input, bytes):
            return self.test([{"input": test_input} for _ in range(self.runner.batch_size)])
        elif isinstance(test_input, str):
            if os.path.exists(test_input):
                data = open(test_input, "rb").read()
                inputs = [{"input": data} for _ in range(self.runner.batch_size)]
                return self.test(inputs)
            else:
                return self.test([{"input": test_input.encode("utf8")} for _ in range(self.runner.batch_size)])
        else:
            print("Invalid input. Must be buffered reader, bytes, valid filepath, or text input.")
            return False

    def test_env(self, test_input_path, conda_env=None, fix_env=True):
        pass

    def save(self, path: str = None, requirements: Union[str, dict] = None, overwrite=False, fix_env=False, gpu=False, arm64=False, conda_env=None) -> Package:
        self._parse_conda_env(conda_env)

        if path is not None and not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

        self.add_requirements(requirements)

        package = Package(
            model_name="Chassis Model",
            model_version="0.0.1",
            model=self,
        )
        package.create(path, "arm64" if arm64 else "amd64", gpu, "3.9")

        return package

    def build_with_docker(self, tag: str = None, cache=False):
        """
        Builds a container from model details and package information.

        Args:
            tag (str): Optional tag to override default. By default, Chassis will create the repository name and tag based on model name and version. But this tag can optionally override the version tag
            cache (bool): Set to True to enable Docker's intermediate layer caching. Will speed up iterative builds but takes up more disk space.
        """
        package = None
        try:
            package = self.save()
            builder = DockerBuilder(package)
            builder.build_image(name=package.model_name, tag=tag if not None else package.model_version, arch=package.arch, cache=cache)
        finally:
            if package is not None:
                package.cleanup()

    def publish(self, model_name: str, model_version: str, registry_user=None, registry_pass=None, requirements=None, fix_env=True, gpu=False, arm64=False, sample_input_path=None, webhook=None, conda_env=None):
        self._parse_conda_env(conda_env)
        pass

    def _parse_conda_env(self, conda_env):
        """
        If supplied, the input parameter will look like this:

        ```python
        env = {
            "name": "sklearn-chassis",
            "channels": ['conda-forge'],
            "dependencies": [
                "python=3.8.5",
                {
                    "pip": [
                        "scikit-learn",
                        "numpy",
                        "chassisml"
                    ]
                }
            ]
        }
        ```

        :param conda_env:
        :return:
        """
        if conda_env is not None:
            deprecated()
            pip_dependencies = conda_env["dependencies"][1]["pip"]
            self.add_requirements(pip_dependencies)
            # TODO - add python version?
