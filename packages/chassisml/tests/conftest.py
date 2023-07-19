import os
from typing import Any

import pytest

from chassisml import ChassisClient


@pytest.fixture
def chassis_client():
    host = "https://chassis.app.modzy.com" if os.getenv('CHASSIS_URL') is None else os.getenv('CHASSIS_URL')
    return ChassisClient(host)


@pytest.fixture
def echo_predict_function():
    def echo_predict_function(input_bytes: bytes) -> Any:
        return {"Message": str(input_bytes)}

    return echo_predict_function


@pytest.fixture
def classic_predict_function():
    def classic_predict_function(input_bytes: bytes) -> dict[str, Any]:
        pass

    return classic_predict_function


@pytest.fixture
def predict_function():
    def predict_function(inputs: dict[str, bytes]) -> dict[str, Any]:
        return inputs

    return predict_function


@pytest.fixture
def batch_predict_function():
    def batch_predict_function(inputs: list[dict[str, bytes]]) -> list[dict[str, Any]]:
        return inputs

    return batch_predict_function
