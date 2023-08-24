import json
import os

import pytest

from chassisml import ChassisClient


@pytest.fixture
def chassis_client():
    host = "http://chassis-test-mode:9999" if os.getenv('CHASSIS_URL') is None else os.getenv('CHASSIS_URL')
    return ChassisClient(host)


@pytest.fixture
def echo_predict_function():
    def echo_predict_function(input_bytes: bytes) -> bytes:
        return json.dumps({"Message": str(input_bytes)}).encode()

    return echo_predict_function


@pytest.fixture
def classic_predict_function():
    def classic_predict_function(input_bytes: bytes) -> dict[str, bytes]:
        pass

    return classic_predict_function


@pytest.fixture
def predict_function():
    def predict_function(inputs: dict[str, bytes]) -> dict[str, bytes]:
        return inputs

    return predict_function


@pytest.fixture
def batch_predict_function():
    def batch_predict_function(inputs: list[dict[str, bytes]]) -> list[dict[str, bytes]]:
        return inputs

    return batch_predict_function
