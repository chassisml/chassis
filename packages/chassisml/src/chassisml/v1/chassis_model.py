import _io
import os
import string
from typing import List, Mapping, Union

from chassis.metadata import ModelMetadata
from chassis.builder import BuildContext
from chassis.builder import DockerBuilder
from chassis.builder import Buildable, BuildOptions
from chassis.runtime import ModelRunner, PYTHON_MODEL_KEY
from chassis.typing import PredictFunction
from .helpers import deprecated


class ChassisModel(Buildable):

    def __init__(self, process_fn: PredictFunction, batch_size=1, legacy_predict_fn=False, chassis_client=None):
        self.runner = ModelRunner(process_fn, batch_size=batch_size, is_legacy_fn=legacy_predict_fn)
        self.python_modules[PYTHON_MODEL_KEY] = self.runner
        if legacy_predict_fn:
            self.metadata = ModelMetadata.legacy()
        if chassis_client is not None:
            self.chassis_client = chassis_client

    def test(self, test_input: Union[str, bytes, _io.BufferedReader, Mapping[str, bytes], List[Mapping[str, bytes]]]) -> List[Mapping[str, bytes]]:
        if isinstance(test_input, _io.BufferedReader):
            result = self.runner.predict([{"input": test_input.read()}])
        elif isinstance(test_input, bytes):
            result = self.runner.predict([{"input": test_input}])
        elif isinstance(test_input, str):
            if os.path.exists(test_input):
                data = open(test_input, 'rb').read()
                result = self.runner.predict([{"input": data}])
            else:
                result = self.runner.predict([{"input": test_input.encode()}])
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
                return self.test([{"input": test_input.encode()} for _ in range(self.runner.batch_size)])
        else:
            print("Invalid input. Must be buffered reader, bytes, valid filepath, or text input.")
            return False

    def test_env(self, test_input_path, conda_env=None, fix_env=True):
        pass

    def save(self, path: str = None, requirements: Union[str, dict] = None, overwrite=False, fix_env=False, gpu=False, arm64=False, conda_env=None) -> BuildContext:
        deprecated()

        # Append any additional requirements.
        self.parse_conda_env(conda_env)
        self.add_requirements(requirements)

        if path is not None and not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

        options = BuildOptions(base_dir=path, arch="arm64" if arm64 else "amd64", use_gpu=gpu)
        return self.prepare_context(options)

    def publish(self, model_name: str, model_version: str, registry_user=None, registry_pass=None, requirements=None, fix_env=True, gpu=False, arm64=False, sample_input_path=None, webhook=None, conda_env=None):
        deprecated()

        # Append any additional requirements.
        self.parse_conda_env(conda_env)
        self.add_requirements(requirements)

        # Update the model name and version in the metadata.
        self.metadata.model_name = model_name
        self.metadata.model_version = model_version

        # Create the build options.
        options = BuildOptions(
            arch="arm64" if arm64 else "amd64",
            use_gpu=gpu,
        )

        # Construct the image name from the model name.
        image_name = "-".join(model_name.translate(str.maketrans('', '', string.punctuation)).lower().split())
        # If presented with registry credentials, prefix the image name with the username of the registry user.
        # This is primarily aimed at supporting images pushed to Docker Hub.
        image_path = f"{registry_user + '/' if (registry_user and registry_pass) else ''}{image_name}"

        # Create the remote builder.
        builder = DockerBuilder(package=self, options=options)
        builder.build_image(image_path, model_version)

    def parse_conda_env(self, conda_env):
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
            pip_dependencies = conda_env["dependencies"][1]["pip"]
            self.add_requirements(pip_dependencies)
            # TODO - add python version?
