import requests

def create_version(modzy_client,modzy_model_id,requested_version):
    model = modzy_client.models.get(modzy_model_id)
    if requested_version in model.versions:
        raise ValueError("Requested model version already exists.")
    create_version_url = modzy_client.base_url + f'models/{modzy_model_id}/versions'
    data = {"version": requested_version}
    res = requests.post(create_version_url, json=data, headers={'Authorization': f'ApiKey {modzy_client.api_key}'})
    if not res.ok and not "already exists" in res.text:
        res.raise_for_status()