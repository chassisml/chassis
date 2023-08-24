import pytest
from chassis.builder.utils import sanitize_image_name


def test_sanitize_image_name():
    tag = sanitize_image_name("image", "tag")
    assert tag == "image:tag"


def test_sanitize_image_name_with_invalid_characters():
    tag = sanitize_image_name("my!image", "tag")
    assert tag == "my-image:tag"


def test_sanitize_image_name_with_invalid_leading_characters():
    tag = sanitize_image_name("!image", "tag")
    assert tag == "image:tag"


def test_sanitize_image_name_with_invalid_trailing_characters():
    tag = sanitize_image_name("image!", "tag")
    assert tag == "image:tag"


def test_sanitize_image_name_with_multiple_consecutive_invalid_characters():
    tag = sanitize_image_name("my!!!image", "tag")
    assert tag == "my-image:tag"


def test_sanitize_image_name_with_slash():
    tag = sanitize_image_name("my/image", "tag")
    assert tag == "my/image:tag"


def test_sanitize_image_name_with_tag_longer_than_allowed():
    tag = sanitize_image_name("a" * 130, "tag")
    assert len(tag) == 128
    assert tag == f"{'a' * 124}:tag"
