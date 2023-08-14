import re


def sanitize_image_name(image_name: str, tag: str = "latest") -> str:
    """
    Sanitizes the image name according to the Docker spec.

        The tag must be valid ASCII and can contain lowercase and uppercase
        letters, digits, underscores, periods, and hyphens. It cannot start
        with a period or hyphen and must be no longer than 128 characters.

    Args:
        image_name: The name of the image to sanitize, _without_ the tag component.
        tag: The tag of the image.

    Returns:
        The full sanitized image tag suitable for use with `docker tag`, etc.
    """
    name = _sanitize_string(image_name)
    tag = _sanitize_string(tag)
    # Combine the image and tag and limit the result to no more than 128 characters.
    tag_length = len(tag) + 1
    if tag_length >= 128:
        raise ValueError("tag is too long, no room for the image name in the 128 character limit")
    last_name_index = 128 - tag_length
    name = name[:last_name_index]
    return f"{name}:{tag}"


def _sanitize_string(s: str) -> str:
    # First, replace all invalid characters with a dash.
    s = re.sub("[^a-zA-Z0-9_.-/]", "-", s)
    # Next strip any leading or trailing periods or hyphens.
    s = re.sub("^[.-]+", "", s)
    s = re.sub("[.-]+$", "", s)
    # Collapse multiple consecutive hyphens into a single one.
    s = re.sub("-+", "-", s)
    return s
