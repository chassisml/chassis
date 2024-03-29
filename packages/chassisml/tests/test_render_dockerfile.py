import sys
import re

import pytest

from chassisml import ChassisModel
from chassis.builder import BuildOptions


def test_render_cpu_dockerfile(echo_predict_function):
    model = ChassisModel(echo_predict_function)
    options = BuildOptions()
    rendered_dockerfile = model.render_dockerfile(options)
    assert f"FROM python:{sys.version_info.major}.{sys.version_info.minor}-slim-bullseye" in rendered_dockerfile.splitlines()


def test_render_gpu_dockerfile(echo_predict_function):
    model = ChassisModel(echo_predict_function)
    options = BuildOptions(cuda_version="12.2.0")
    rendered_dockerfile = model.render_dockerfile(options)
    assert "FROM nvidia/cuda:12.2.0-runtime-ubuntu20.04" in rendered_dockerfile.splitlines()


def test_render_cpu_dockerfile_with_nondefault_python_version(echo_predict_function):
    model = ChassisModel(echo_predict_function)
    options = BuildOptions(python_version="4.0")
    rendered_dockerfile = model.render_dockerfile(options)
    assert "FROM python:4.0-slim-bullseye" in rendered_dockerfile.splitlines()


def test_render_dockerfile_with_no_apt_packages(echo_predict_function):
    model = ChassisModel(echo_predict_function)
    options = BuildOptions()
    rendered_dockerfile = model.render_dockerfile(options)
    assert re.search("apt-get install -y\\s+&&", rendered_dockerfile) is None


def test_render_dockerfile_with_apt_packages(echo_predict_function):
    model = ChassisModel(echo_predict_function)
    model.add_apt_packages(["libgmp", "opencv-headless"])
    options = BuildOptions()
    rendered_dockerfile = model.render_dockerfile(options)
    assert re.search("apt-get install -y (?:libgmp |opencv-headless ){2}", rendered_dockerfile) is not None
