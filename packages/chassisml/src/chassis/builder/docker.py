import string

import docker
from docker.errors import BuildError

from .context import BuildContext


def _create_full_image_name(name: str, tag: str):
    illegal_punc = string.punctuation.translate({ord(i): None for i in '_.-'})
    # remove first character if :
    if tag is not None and len(tag) > 0:
        if tag[0] == ":":
            tag = tag[1:]
        if sum([chr in illegal_punc for chr in tag]):
            raise ValueError(f"Illegal characters in tag. Tag parameter must adhere to Docker's tagging rules: 'A tag name must be valid ASCII and may contain lowercase and uppercase letters, digits, underscores, periods and hyphens. A tag name may not start with a period or a hyphen and may contain a maximum of 128 characters'")

    container_image_name = "-".join(name.translate(str.maketrans('', '', string.punctuation)).lower().split())
    return f"{container_image_name}:{tag}"


class DockerBuilder:

    def __init__(self, context: BuildContext):
        self.client = docker.from_env()
        self.context = context

    def build_image(self, name: str, tag="latest", cache=False, show_logs=False, clean_context=True):
        try:
            image, logs = self.client.images.build(
                path=self.context.base_dir,
                tag=_create_full_image_name(name, tag),
                rm=not cache,
                forcerm=not cache,
                platform=self.context.platform,
            )
            if show_logs:
                log_output = ""
                for log_line in logs:
                    if "stream" in log_line:
                        log_output += log_line["stream"]
                print(log_output)
            print(f"Image ID: {image.id}")
            print(f"Image Tags: {image.tags}")
            if clean_context:
                print("Cleaning context")
                self.context.cleanup()
        except BuildError as e:
            log_output = ""
            print("Error in Docker build process. Full logs below:\n\n")
            for log_line in e.build_log:
                if "stream" in log_line:
                    log_output += log_line["stream"]
            print(log_output)
            raise e
