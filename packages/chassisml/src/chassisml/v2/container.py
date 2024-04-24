import os

from chassis.builder import Buildable, BuildOptions, DefaultBuildOptions, BuildContext
from openmodel.v2.container_pb2 import OpenModelContainerInfo
from chassis.runtime import ModelBase, PYTHON_MODEL_KEY


class OpenModelContainer(Buildable):
    info: OpenModelContainerInfo
    model: ModelBase

    def __init__(self, info: OpenModelContainerInfo, model: ModelBase):
        super().__init__()
        self.api_compatibility: set[str] = {"v1", "v2"}
        self.info = info
        self.model = model
        self.python_modules[PYTHON_MODEL_KEY] = self.model
        self._update_legacy_metadata()

    def prepare_context(self, options: BuildOptions = DefaultBuildOptions) -> BuildContext:
        context = super().prepare_context(options)
        # Save the container info
        container_info = self.info.SerializeToString()
        with open(os.path.join(context.data_dir, "container_info"), "wb") as f:
            f.write(container_info)
        return context

    def _update_legacy_metadata(self):
        self.metadata.model_name = self.info.name
        self.metadata.model_version = self.info.version
        self.metadata.model_author = f"{self.info.author.name} <{self.info.author.email}>"
        # TODO - finish rest of fields.
