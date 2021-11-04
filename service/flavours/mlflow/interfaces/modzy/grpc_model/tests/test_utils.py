import pytest

from grpc_model import TEST_RESOURCES
from grpc_model.src.utils import parse_complete_model_yaml


@pytest.mark.parametrize("model_file_i", [1, 2])
def test_parse_complete_model_yaml(model_file_i):
    model_yaml_contents = parse_complete_model_yaml(
        TEST_RESOURCES / "model_yaml_examples" / f"model{model_file_i}.yaml"
    )
    print(model_yaml_contents)
