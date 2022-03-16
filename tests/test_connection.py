import subprocess

# TODO: instantiate HOST_URL in __init__

HOST_URL = "http://localhost:5000"

def test_can_connect_to_service():
    output = subprocess.run("curl {}".format(HOST_URL), shell=True, capture_output=True)
    assert output.stdout.decode() == "Alive!"