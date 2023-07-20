import pytest

from chassisml import ChassisModel


def test_create_model_fails_if_neither_process_nor_batch_process_given(chassis_client):
    with pytest.raises(ValueError):
        model = chassis_client.create_model()


def test_create_model_fails_if_both_process_and_batch_process_given(chassis_client, echo_predict_function):
    with pytest.raises(ValueError):
        model = chassis_client.create_model(process_fn=echo_predict_function, batch_process_fn=echo_predict_function)


def test_create_batch_model_fails_without_batch_size(chassis_client, echo_predict_function):
    with pytest.raises(ValueError):
        model = chassis_client.create_model(batch_process_fn=echo_predict_function)


def test_adding_pip_requirements_from_conda_env(echo_predict_function):
    model = ChassisModel(echo_predict_function)
    env = {
        "name": "sklearn-chassis",
        "channels": ['conda-forge'],
        "dependencies": [
            "python=3.8.5",
            {
                "pip": [
                    "scikit-learn",
                    "numpy",
                    "chassisml",
                ]
            }
        ]
    }
    model.parse_conda_env(env)
    assert len(model.requirements.symmetric_difference(["scikit-learn", "numpy", "chassisml"])) == 0

# Verify that the fields in the metadata are updated based on the values provided during `prepare_context`.
