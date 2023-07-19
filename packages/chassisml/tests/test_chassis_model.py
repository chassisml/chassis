import pytest


def test_create_model_fails_if_neither_process_nor_batch_process_given(chassis_client):
    with pytest.raises(ValueError):
        model = chassis_client.create_model()


def test_create_model_fails_if_both_process_and_batch_process_given(chassis_client, echo_predict_function):
    with pytest.raises(ValueError):
        model = chassis_client.create_model(process_fn=echo_predict_function, batch_process_fn=echo_predict_function)


def test_create_batch_model_fails_without_batch_size(chassis_client, echo_predict_function):
    with pytest.raises(ValueError):
        model = chassis_client.create_model(batch_process_fn=echo_predict_function)

# test adding requirements via conda_env (deprecated)
