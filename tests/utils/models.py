# TODO: build this out to include different model types/frameworks

import os

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")

'''
Hello World Model
'''

def process_hello(input_bytes):
    return "Hello World!"

hello_world_env = {
    "name": "hello-world",
    "channels": ['conda-forge'],
    "dependencies": [
        "python=3.9.6",
        {
            "pip": [
                "chassisml"
            ] 
        }
    ]
}    

hello_world_local_test_output = b'"Hello World!"'

'''
Scikit-Learn Model
'''

'''
PyTorch Model
'''

'''
LightGBM Model
'''

'''
ONNX Model
'''

def assemble_models_dict():

    models = [
        {
            "model_name": "Hello World",
            "model_version": "0.0.1",
            "process_fn": process_hello,
            "batch_process_fn": None,
            "conda_env": hello_world_env,
            "test_file": os.path.join(DATA_DIR, "hello-world.txt"),
            "local_test_result": hello_world_local_test_output,
            "local_test_batch_result": None
        }    
    ]

    return models
