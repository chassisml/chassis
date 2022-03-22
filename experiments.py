import os
from dataclasses import dataclass
import importlib
from numpy import isin
import requests


def process_hello(input_bytes):
    return "Hello World!"

def assemble_models_dict():

    models = [
        {
            "model_name": "Hello World",
            "model_version": "0.0.1",
            "process_fn": process_hello,
            "test_file": "./tests/utils/data/hello-world.txt"
        }
    ]

    return models    

models = assemble_models_dict()    

HOST_URL = "http://localhost:5000"

client = chassisml.ChassisClient(HOST_URL)

chassis_model = client.create_model(process_fn=models[0]["process_fn"])
print(chassis_model)

test_out = b'"Hello World!"'

try:
    output = chassis_model.test("tests/utils/data/hello-world.txt")
    # print(output, type(output), output==test_out)
    # print(list(output.keys())[0])
except Exception as e:
    print(e)
# except requests.exceptions.ConnectionError as e:
#     raise ConnectionError("connection error")

# try to save model
chassis_model.save("../tmp-hello-world-model")

import mlflow
# checks: paths exist + model can be loaded by mlflow pyfunc method

check = {}
check["model"] = "test model"
check["saved_model_checks"] = []
TMP_SAVE_DIR = "../tmp-hello-world-model"
check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "conda.yaml")))
check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "MLmodel")))
check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "python_model.pkl")))
check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "requirements.txt")))

try:
    model = mlflow.pyfunc.load_model(TMP_SAVE_DIR)
    if isinstance(model, mlflow.pyfunc.PyFuncModel):
        check["model_load_check"] = True
    else:
        check["model_load_check"] = False
except Exception as e:
    check["model_load_check"] = False

new_list = [] + check["saved_model_checks"]
new_list.append(check["model_load_check"])
print(new_list)

# import shutil
# shutil.rmtree(TMP_SAVE_DIR)





# os.path.isfile(os.path.join("../tmp-hello-world-model", "conda.yaml"))
# os.path.isfile(os.path.join("../tmp-hello-world-model", "MLmodel"))
# os.path.isfile(os.path.join("../tmp-hello-world-model", "python_model.pkl"))
# os.path.isfile(os.path.join("../tmp-hello-world-model", "requirements.txt"))

# import subprocess

# output = subprocess.run("curl localhost:5000", shell=True, capture_output=True)

# print(output.stdout.decode() == "Alive!")


# def test_can_construct_client():
#     client = chassisml.ChassisClient(HOST_URL)
#     print(client)
#     assert client is not None
