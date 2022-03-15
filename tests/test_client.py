import chassisml

HOST_URL = "http://localhost:5000"

def test_can_construct_client():
    client = chassisml.ChassisClient(HOST_URL)
    print(client)
    assert client is not None