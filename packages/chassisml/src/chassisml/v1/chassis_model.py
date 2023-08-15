from __future__ import annotations

import _io
import os
import string
from typing import List, Mapping, Optional, Sequence, Union

from chassis.metadata import ModelMetadata
from chassis.builder import BuildContext
from chassis.builder import DockerBuilder
from chassis.builder import Buildable, BuildOptions
from chassis.runtime import ModelRunner, PYTHON_MODEL_KEY
from chassis.ftypes import PredictFunction
from .helpers import deprecated

DEFAULT_CUDA_VERSION = "11.0.3"


class ChassisModel(Buildable):
    """
    The Chassis Model Object.

    This class inherits from [chassis.builder.Buildable][] and is the main
    object that gets fed into a Chassis builder object
    (i.e., [chassis.builder.DockerBuilder][] or [chassis.builder.RemoteBuilder][])
    """

    def __init__(self, process_fn: PredictFunction, batch_size: int = 1,
                 legacy_predict_fn: bool = False, chassis_client=None):
        """
        Init.

        Args:
            process_fn: Single predict function of type `PredictFunction` that
                represents a model inference function.
            batch_size: Integer representing the batch size your model supports.
                If your model does not support batching, the default value is 1.
            legacy_predict_fn: For internal backwards-compatibility use only.
            chassis_client: For internal backwards-compatibility use only.
        """
        self.runner = ModelRunner(process_fn, batch_size=batch_size,
                                  is_legacy_fn=legacy_predict_fn)
        self.python_modules[PYTHON_MODEL_KEY] = self.runner
        if legacy_predict_fn:
            self.metadata = ModelMetadata.legacy()
        if chassis_client is not None:
            self.chassis_client = chassis_client

    def test(self, test_input: Union[str, bytes, _io.BufferedReader, Mapping[str, bytes], Sequence[Mapping[str, bytes]]]) -> Sequence[Mapping[str, bytes]]:
        """
        Runs a test inference against the model before it is packaged.

        This method supports multiple input types

        - Single input: A map-like object with a string for the key and
            bytes as the value.
        - Batch input: A list of map-like objects with strings for keys and
            bytes for values.

        The following input types are also supported but considered deprecated
            and may be removed in a future release

        - File: A BufferedReader object. Use of this type assumes that your
            predict function expects the input key to be "input".
        - bytes: Any arbitrary bytes. Use of this type assumes that your
            predict function expects the input key to be "input".
        - str: A string. If the string maps to a filesystem location, then
            the file at that location will be read and used as the value.
            If not the string itself is used as the value. Use of this type
            assumes that your predict function expects the input key to
            be "input".

        Args:
            test_input: Sample input data used to test the model.
                See above for more information.

        Returns:
            Results returned by your model's predict function based on the
                `test_input` sample data fed to this function.

        Example:
        ```python
        from chassisml import ChassisModel
        chassis_model = ChassisModel(process_fn=predict)
        results = chassis_model.test(sample_data)
        ```
        """

        if isinstance(test_input, _io.BufferedReader):
            deprecated("Use of a BufferedReader as input will be removed in a future release.")
            result = self.runner.predict([{"input": test_input.read()}])
        elif isinstance(test_input, bytes):
            deprecated("Use of a bytes object as input will be removed in a future release.")
            result = self.runner.predict([{"input": test_input}])
        elif isinstance(test_input, str):
            deprecated("Use of a string as input will be removed in a future release.")
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
        """
        **DEPRECATED**

        The [chassisml.ChassisModel.test][] method now supports supplying
        batches of inputs.
        """
        deprecated("Please use the `test` method moving forward as it now supports batched inputs..")
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
        """
        **No Longer Available**

        Please use [chassis.client.OMIClient.test_container][] moving forward.
        """
        deprecated("Method no longer supported and will be removed in the next release.")
        raise NotImplementedError

    def save(self, path: Optional[str] = None,
             requirements: Optional[Union[str, List[str]]] = None,
             overwrite: bool = False, fix_env: bool = False, gpu: bool = False,
             arm64: bool = False, conda_env: Optional[dict] = None) -> BuildContext:
        """
        **DEPRECATED**

        Please use [chassisml.ChassisModel.prepare_context][] moving forward.

        ---

        Saves a copy of ChassisModel to local filepath

        Args:
            path: Filepath to save chassis model.
            requirements: Additional pip requirements needed by the model.
            conda_env: A dictionary with environment requirements.
            overwrite: No longer used.
            fix_env: No longer used.
            gpu: If True and `arm64` is True, modifies dependencies as
                needed by chassis for ARM64+GPU support
            arm64: If True and `gpu` is True, modifies dependencies as
                needed by chassis for ARM64+GPU support

        Returns:
            The `BuildContext` object that allows for further actions to be
                taken.

        Example:
        ```python
        chassis_model = ChassisModel(process_fn=process)
        context = chassis_model.save("local_model_directory")
        ```
        """
        deprecated("Please use `ChassisModel.prepare_context()` moving forward.")

        # Append any additional requirements.
        if conda_env is not None:
            self.parse_conda_env(conda_env)
        if requirements is not None:
            self.add_requirements(requirements)

        if path is not None and not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

        options = BuildOptions(base_dir=path, arch="arm64" if arm64 else "amd64",
                               cuda_version=DEFAULT_CUDA_VERSION if gpu else None)
        return self.prepare_context(options)

    def publish(self, model_name: str, model_version: str,
                registry_user: Optional[str] = None,
                registry_pass: Optional[str] = None,
                requirements: Optional[Union[str, list[str]]] = None,
                fix_env: bool = True, gpu: bool = False, arm64: bool = False,
                sample_input_path: Optional[str] = None,
                webhook: Optional[str] = None,
                conda_env: Optional[dict] = None):
        """
        **DEPRECATED**

        Please use [chassis.builder.RemoteBuilder][] moving forward.

        ---

        Builds the model locally using Docker.

        Args:
            model_name: Model name that serves as model's name and docker
                registry repository name.
            model_version: Version of model
            registry_user: Docker registry username
            registry_pass: Docker registry password
            requirements: Additional pip requirements needed by the model.
            conda_env: A dictionary with environment requirements.
            fix_env: No longer used.
            gpu: If True, builds container image that runs on GPU hardware
            arm64: If True, builds container image that runs on ARM64 architecture
            sample_input_path: No longer used.
            webhook: No longer used.

        Returns:
            Details about the result of the build.

        Example:
        ```python
        # Create Chassisml model
        chassis_model = ChassisModel(process_fn=process)

        # Build the model locally using Docker.
        response = chassis_model.publish(
            model_name="Chassisml Regression Model",
            model_version="0.0.1",
        )
        ```
        """
        deprecated("Please use `chassis.builder.RemoteBuilder` moving forward.")

        # Append any additional requirements.
        if conda_env is not None:
            self.parse_conda_env(conda_env)
        if requirements is not None:
            self.add_requirements(requirements)

        # Update the model name and version in the metadata.
        self.metadata.model_name = model_name
        self.metadata.model_version = model_version

        # Create the build options.
        options = BuildOptions(
            arch="arm64" if arm64 else "amd64",
            cuda_version=DEFAULT_CUDA_VERSION if gpu else None,
        )

        # Construct the image name from the model name.
        image_name = "-".join(model_name.translate(str.maketrans('', '', string.punctuation)).lower().split())
        # If presented with registry credentials, prefix the image name with the username of the registry user.
        # This is primarily aimed at supporting images pushed to Docker Hub.
        image_path = f"{registry_user + '/' if (registry_user and registry_pass) else ''}{image_name}"

        # Create the remote builder.
        builder = DockerBuilder(package=self, options=options)
        builder.build_image(image_path, model_version)

    def parse_conda_env(self, conda_env: Optional[dict]):
        """
        Supports legacy Chassis `conda_env` functionality by parsing pip
        dependencies and inserting into the `Buildable` object via the
        `add_requirements` function.

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
        chassis_model = ChassisModel(process_fn=predict)
        chassis_model.parse_conda_env(env)
        ```

        Args:
            conda_env: A conda environment structure.
                See above for more details.
        """
        if conda_env is not None:
            pip_dependencies = conda_env["dependencies"][1]["pip"]
            self.add_requirements(pip_dependencies)
            # TODO - add python version?
