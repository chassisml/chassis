import os
import mlflow
import time
import shutil
import sys
sys.path.append('./chassisml-sdk/')
import chassisml
# from tests.utils.models import assemble_models_dict
from tests.test_connection import *
from tests.test_sdk import *
from tests.test_service import *
import logging
logging.basicConfig(level=logging.INFO, format= '%(levelname)s: %(message)s')

# TODO: instantiate HOST_URL in __init__
HOST_URL = "http://localhost:5000"
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
UTILS_PATH = os.path.join(ROOT_DIR, "utils")

def process_hello(input_bytes):
    return "Hello World!"

hello_world_env = {
    "name": "hello-world",
    "channels": ['conda-forge'],
    "dependencies": [
        "python=3.9.6",
        {
            "pip": [
                "chassisml",
            ] 
        }
    ]
}

def assemble_models_dict():
    models = [
        {
            "model_name": "Hello World",
            "model_version": "0.0.1",
            "process_fn": process_hello,
            "batch_process_fn": None,
            "conda_env": hello_world_env,
            "test_file": os.path.join(UTILS_PATH, "data", "hello-world.txt"),
            "local_test_result": b'"Hello World!"',
            "local_test_batch_result": None
        }
    ]
    return models


if __name__ == "__main__":
    
    # fixtures used throughout all test cases
    logger = logging.getLogger(__name__)
     
    client = chassisml.ChassisClient(HOST_URL)
    models = assemble_models_dict()

    docker_creds = {
        "user": "bmunday131",
        "pass": "b-rad22323"
    }

    TOTAL_PASSED = 0
    TOTAL_FAILED = 0

    # test connection
    out = test_can_connect_to_service(HOST_URL, logger, "test_can_connect_to_service")
    if out:
        TOTAL_PASSED += 1
    else:
        TOTAL_FAILED += 1
    
    # test sdk
    # out = test_create_model(client, logger, models)
    # if out == 0:
    #     TOTAL_PASSED += 1
    # else:
    #     TOTAL_FAILED += out

    # out = test_create_model_with_batch(client, logger, models)    
    # if out:
    #     TOTAL_PASSED += 1
    # else:
    #     TOTAL_FAILED += 1

    out = test_local_test(client, logger, models)
    if all(out):
        TOTAL_PASSED += 1
    else:
        TOTAL_FAILED += 1 

    out = test_local_batch_test(client, logger, models)
    if all(out):
        TOTAL_PASSED += 1
    else:
        TOTAL_FAILED += 1    

    # out = test_env_test(client, logger, models)
    # if out == 0:
    #     TOTAL_PASSED += 1
    # else:
    #     TOTAL_FAILED += out 

    # out = test_env_test_manual_env_config(client, logger, models)
    # if out == 0:
    #     TOTAL_PASSED += 1
    # else:
    #     TOTAL_FAILED += out

    out = test_save(client, logger, models, UTILS_PATH)               
    if all(out):
        TOTAL_PASSED += 1
    else:
        TOTAL_FAILED += 1

    out = test_save_manual_env_config(client, logger, models, UTILS_PATH)               
    if all(out):
        TOTAL_PASSED += 1
    else:
        TOTAL_FAILED += 1

    out = test_save_gpu(client, logger, models, UTILS_PATH)               
    if all(out):
        TOTAL_PASSED += 1
    else:
        TOTAL_FAILED += 1  

    out = test_save_arm(client, logger, models, UTILS_PATH)               
    if all(out):
        TOTAL_PASSED += 1
    else:
        TOTAL_FAILED += 1    

    out = test_save_gpu_and_arm(client, logger, models, UTILS_PATH)               
    if all(out):
        TOTAL_PASSED += 1
    else:
        TOTAL_FAILED += 1  

    # regular publish
    out, job_ids = test_publish(client, logger, models, docker_creds)
    if out == 0:
        TOTAL_PASSED += 1
    else:
        TOTAL_FAILED += out                                

    logger.info("--------------------- SUMMARY ---------------------")
    logger.info("{} PASSED, {} FAILED".format(TOTAL_PASSED, TOTAL_FAILED))        
    

    # test service
    
