import logging
import os
import dotenv
import pytest
import mlflow
import time
import importlib
import shutil
import sys
sys.path.append('./chassisml-sdk/')
import chassisml
sys.path.append("./tests/")
# from utils.models import assemble_models_dict
import torch

HOST_URL = "http://localhost:5000"
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
UTILS_PATH = os.path.join(ROOT_DIR, "utils")

# placeholder local model definition for now
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

def assemble_models_dict():
    models = [
        {
            "model_name": "Hello World",
            "model_version": "0.0.1",
            "process_fn": process_hello,
            "batch_process_fn": None,
            "conda_env": hello_world_env,
            "test_file": "tests/utils/data/hello-world.txt",
            "local_test_result": b'"Hello World!"',
            "local_test_batch_result": None
        }
    ]
    return models


# PyTest fixtures used throughout all test cases
@pytest.fixture()
def client():
    return chassisml.ChassisClient(HOST_URL)

@pytest.fixture()
def logger():
    return logging.getLogger(__name__)   

@pytest.fixture()
def models():
    return assemble_models_dict()


# Test cases ordered in flow of usage (i.e., you need to create a model before testing or publishing it)

# create model tests
def test_create_model(client, logger, models):
    '''
    Tests the creation of a chassis model

    NOTE: the `create_model` method works in every scenario I ran, regardless of whether or not there is a valid connection to a running chassis service,
    so the only way I could think of testing this is via the `test_env` method

    Args:

    Returns:

    '''
    logger.info("Create Model Test")
    results = []
    for model in models:
        print(model)
        logger.info("Creating {} model".format(model["model_name"]))
        chassis_model = client.create_model(process_fn=model["process_fn"])
        try:
            # only way to test if `create_model` method returns valid chassis model is by testing it using this function.
            # the local test
            local_test = chassis_model.test_env(model["test_file"], conda_env=model["conda_env"])
            print(local_test)
            results.append(local_test)
            if list(local_test.keys())[0] == "model_error":
                logger.debug("Model Error with {} model: {}".format(model["model_name"], local_test["model_error"]))
            else:
                logger.info("{} test successful".format(model["model_name"]))
        except Exception as e:
            print(e)
            results.append({"error": e})
            logger.debug("Error with {} model: {}".format(model["model_name"], e))
            continue

    # determine number of errors produced
    num_errors = 0
    for result in results:
        if list(result.keys())[0] in ["error", "model_error"]:
            num_errors += 1

    assert num_errors == 0

# def test_create_model_with_batch(client, logger):
#     logger.debug("test model")
#     assert True

# # test model tests
# def test_local_test(client, logger, models):
#     '''
#     Tests local `test` method

#     Args:

#     Returns:

#     '''
#     logger.info("Test Chassis Model Locally")
#     results = []
#     for model in models:
#         print(model)
#         logger.info("Creating {} model".format(model["model_name"]))
#         chassis_model = client.create_model(process_fn=model["process_fn"])
#         local_test = chassis_model.test(model["test_file"])
#         if local_test == model["local_test_result"]:
#             logger.info("{}: actual output matches expected output".format(model["model_name"]))
#         else:
#             logger.debug("{}: actual output does not match expected output".format(model["model_name"]))
#         results.append(local_test == model["local_test_result"])

#     assert all(results)    

# def test_local_batch_test(client, logger, models):
#     '''
#     Tests local `test` method with batch process function

#     Args:

#     Returns:

#     '''
#     logger.info("Test Chassis Model Locally")
#     results = []
#     for model in models:
#         if model["batch_process_fn"] is not None:
#             print(model)
#             logger.info("Creating {} model".format(model["model_name"]))
#             chassis_model = client.create_model(process_fn=model["process_fn"])
#             local_test = chassis_model.test_batch(model["test_file"])
#             if local_test == model["local_test_batch_result"]:
#                 logger.info("{}: actual output matches expected output".format(model["model_name"]))
#             else:
#                 logger.debug("{}: actual output does not match expected output".format(model["model_name"]))
#             results.append(local_test == model["local_test_batch_result"])

#     assert all(results)

# def test_env_test(client, logger, models):
#     '''
#     Tests the creation of a chassis model

#     NOTE: currently the tests for `create_model` and `test_env` are exactly the same

#     Args:

#     Returns:

#     '''
#     logger.info("Test Env with Chassis Model object")
#     results = []
#     for model in models:
#         print(model)
#         logger.info("Creating {} model".format(model["model_name"]))
#         chassis_model = client.create_model(process_fn=model["process_fn"])
#         try:
#             # only way to test if `create_model` method returns valid chassis model is by testing it using this function.
#             # the local test
#             local_test = chassis_model.test_env(model["test_file"], conda_env=model["conda_env"])
#             print(local_test)
#             results.append(local_test)
#             if list(local_test.keys())[0] == "model_error":
#                 logger.debug("Model Error with {} model: {}".format(model["model_name"], local_test["model_error"]))
#             else:
#                 logger.info("{} test successful".format(model["model_name"]))
#         except Exception as e:
#             print(e)
#             results.append({"error": e})
#             logger.debug("Error with {} model: {}".format(model["model_name"], e))
#             continue

#     # determine number of errors produced
#     num_errors = 0
#     for result in results:
#         if list(result.keys())[0] in ["error", "model_error"]:
#             num_errors += 1

#     assert num_errors == 0

#     assert True

# def test_env_test_manual_env_config():
#     '''
#     TODO: this would be same as test_env test at the moment. Can't get test_env to work because of local module import issues
#     '''
#     # logger.info("Test Env with Chassis Model object and manually configure conda environment")
#     # results = []
#     # for model in models:
#     #     print(model)
#     #     logger.info("Creating {} model".format(model["model_name"]))
#     #     chassis_model = client.create_model(process_fn=model["process_fn"])
#     #     try:
#     #         # only way to test if `create_model` method returns valid chassis model is by testing it using this function.
#     #         # the local test
#     #         local_test = chassis_model.test_env(model["test_file"], conda_env=model["conda_env"])
#     #         print(local_test)
#     #         results.append(local_test)
#     #         if list(local_test.keys())[0] == "model_error":
#     #             logger.debug("Model Error with {} model: {}".format(model["model_name"], local_test["model_error"]))
#     #         else:
#     #             logger.info("{} test successful".format(model["model_name"]))
#     #     except Exception as e:
#     #         print(e)
#     #         results.append({"error": e})
#     #         logger.debug("Error with {} model: {}".format(model["model_name"], e))
#     #         continue

#     # # determine number of errors produced
#     # num_errors = 0
#     # for result in results:
#     #     if list(result.keys())[0] in ["error", "model_error"]:
#     #         num_errors += 1

#     # assert num_errors == 0    
    
#     assert True 

# # save model locally tests
# def test_save(client, logger, models):
#     logger.info("Saving MLFlow model locally (default config)")
#     checks = []
#     agg_checks = []
#     for model in models:
#         check = {}
#         check["model"] = model["model_name"]
#         check["saved_model_checks"] = []
#         print(model)
#         logger.info("Creating {} model".format(model["model_name"]))
#         # build model
#         chassis_model = client.create_model(process_fn=model["process_fn"])    
#         # create temp dir
#         TMP_SAVE_DIR = os.path.join(UTILS_PATH, "tmp-model")
#         # save chassis model
#         if os.path.isdir(TMP_SAVE_DIR):
#             shutil.rmtree(TMP_SAVE_DIR)
#         chassis_model.save(TMP_SAVE_DIR, conda_env=model["conda_env"], overwrite=False, fix_env=True, gpu=False, arm64=False)
#         # check expected files exist + model can be loaded using mlflow pyfunc load_model method
#         check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "conda.yaml")))
#         check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "MLmodel")))
#         check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "python_model.pkl")))
#         check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "requirements.txt")))
#         # load model and confirm it is the correct instance
#         try:
#             model = mlflow.pyfunc.load_model(TMP_SAVE_DIR)
#             if isinstance(model, mlflow.pyfunc.PyFuncModel):
#                 check["model_load_check"] = True
#             else:
#                 logger.debug("Loaded model not correct instance type")
#                 check["model_load_check"] = False
#         except Exception as e:
#             logger.debug("Error loading pyfunc model: {}".format(e))
#             check["model_load_check"] = False
#             continue
        
#         agg_checks += check["saved_model_checks"]
#         agg_checks.append(check["model_load_check"])
#         checks.append(check)

#         # remove temp dir
#         shutil.rmtree(TMP_SAVE_DIR)
#     print(agg_checks)

#     assert all(agg_checks)         

# def test_save_manual_env_config(client, logger, models):
#     logger.info("Saving MLFlow model locally (default config)")
#     checks = []
#     agg_checks = []
#     for model in models:
#         check = {}
#         check["model"] = model["model_name"]
#         check["saved_model_checks"] = []
#         print(model)
#         logger.info("Creating {} model".format(model["model_name"]))
#         # build model
#         chassis_model = client.create_model(process_fn=model["process_fn"])    
#         # create temp dir
#         TMP_SAVE_DIR = os.path.join(UTILS_PATH, "tmp-model")
#         # save chassis model
#         if os.path.isdir(TMP_SAVE_DIR):
#             shutil.rmtree(TMP_SAVE_DIR)        
#         chassis_model.save(TMP_SAVE_DIR, conda_env=model["conda_env"], overwrite=False, fix_env=True, gpu=False, arm64=False)
#         # check expected files exist + model can be loaded using mlflow pyfunc load_model method
#         check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "conda.yaml")))
#         check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "MLmodel")))
#         check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "python_model.pkl")))
#         check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "requirements.txt")))
#         # load model and confirm it is the correct instance
#         try:
#             model = mlflow.pyfunc.load_model(TMP_SAVE_DIR)
#             if isinstance(model, mlflow.pyfunc.PyFuncModel):
#                 check["model_load_check"] = True
#             else:
#                 logger.debug("Loaded model not correct instance type")
#                 check["model_load_check"] = False
#         except Exception as e:
#             logger.debug("Error loading pyfunc model: {}".format(e))
#             check["model_load_check"] = False
#             continue
        
#         agg_checks += check["saved_model_checks"]
#         agg_checks.append(check["model_load_check"])
#         checks.append(check)

#         # remove temp dir
#         shutil.rmtree(TMP_SAVE_DIR)
#     print(agg_checks)

#     assert all(agg_checks)  

# def test_save_gpu(client, logger, models):
#     logger.info("Saving MLFlow model locally (default config)")
#     checks = []
#     agg_checks = []
#     for model in models:
#         check = {}
#         check["model"] = model["model_name"]
#         check["saved_model_checks"] = []
#         print(model)
#         logger.info("Creating {} model".format(model["model_name"]))
#         # build model
#         chassis_model = client.create_model(process_fn=model["process_fn"])    
#         # create temp dir
#         TMP_SAVE_DIR = os.path.join(UTILS_PATH, "tmp-model")
#         # save chassis model
#         if os.path.isdir(TMP_SAVE_DIR):
#             shutil.rmtree(TMP_SAVE_DIR)        
#         chassis_model.save(TMP_SAVE_DIR, conda_env=None, overwrite=False, fix_env=True, gpu=True, arm64=False)
#         # check expected files exist + model can be loaded using mlflow pyfunc load_model method
#         check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "conda.yaml")))
#         check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "MLmodel")))
#         check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "python_model.pkl")))
#         check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "requirements.txt")))
#         # load model and confirm it is the correct instance
#         try:
#             model = mlflow.pyfunc.load_model(TMP_SAVE_DIR)
#             if isinstance(model, mlflow.pyfunc.PyFuncModel):
#                 check["model_load_check"] = True
#             else:
#                 logger.debug("Loaded model not correct instance type")
#                 check["model_load_check"] = False
#         except Exception as e:
#             logger.debug("Error loading pyfunc model: {}".format(e))
#             check["model_load_check"] = False
#             continue
        
#         agg_checks += check["saved_model_checks"]
#         agg_checks.append(check["model_load_check"])
#         checks.append(check)

#         # remove temp dir
#         shutil.rmtree(TMP_SAVE_DIR)
#     print(agg_checks)

#     assert all(agg_checks)

# def test_save_arm(client, logger, models):
#     logger.info("Saving MLFlow model locally (default config)")
#     checks = []
#     agg_checks = []
#     for model in models:
#         check = {}
#         check["model"] = model["model_name"]
#         check["saved_model_checks"] = []
#         print(model)
#         logger.info("Creating {} model".format(model["model_name"]))
#         # build model
#         chassis_model = client.create_model(process_fn=model["process_fn"])    
#         # create temp dir
#         TMP_SAVE_DIR = os.path.join(UTILS_PATH, "tmp-model")
#         # save chassis model
#         if os.path.isdir(TMP_SAVE_DIR):
#             shutil.rmtree(TMP_SAVE_DIR)        
#         chassis_model.save(TMP_SAVE_DIR, conda_env=None, overwrite=False, fix_env=True, gpu=False, arm64=True)
#         # check expected files exist + model can be loaded using mlflow pyfunc load_model method
#         check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "conda.yaml")))
#         check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "MLmodel")))
#         check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "python_model.pkl")))
#         check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "requirements.txt")))
#         # load model and confirm it is the correct instance
#         try:
#             model = mlflow.pyfunc.load_model(TMP_SAVE_DIR)
#             if isinstance(model, mlflow.pyfunc.PyFuncModel):
#                 check["model_load_check"] = True
#             else:
#                 logger.debug("Loaded model not correct instance type")
#                 check["model_load_check"] = False
#         except Exception as e:
#             logger.debug("Error loading pyfunc model: {}".format(e))
#             check["model_load_check"] = False
#             continue
        
#         agg_checks += check["saved_model_checks"]
#         agg_checks.append(check["model_load_check"])
#         checks.append(check)

#         # remove temp dir
#         shutil.rmtree(TMP_SAVE_DIR)
#     print(agg_checks)

#     assert all(agg_checks)

# def test_save_gpu_and_arm(client, logger, models):
#     # logger.info("Saving MLFlow model locally (default config)")
#     # checks = []
#     # agg_checks = []
#     # for model in models:
#     #     check = {}
#     #     check["model"] = model["model_name"]
#     #     check["saved_model_checks"] = []
#     #     print(model)
#     #     logger.info("Creating {} model".format(model["model_name"]))
#     #     # build model
#     #     chassis_model = client.create_model(process_fn=model["process_fn"])    
#     #     # create temp dir
#     #     TMP_SAVE_DIR = os.path.join(UTILS_PATH, "tmp-model")
#     #     # save chassis model
#     #     
#         # if os.path.isdir(TMP_SAVE_DIR):
#         #     shutil.rmtree(TMP_SAVE_DIR)    
#     #     chassis_model.save(TMP_SAVE_DIR, conda_env=None, overwrite=False, fix_env=True, gpu=True, arm64=True)
#     #     # check expected files exist + model can be loaded using mlflow pyfunc load_model method
#     #     check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "conda.yaml")))
#     #     check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "MLmodel")))
#     #     check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "python_model.pkl")))
#     #     check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "requirements.txt")))
#     #     # load model and confirm it is the correct instance
#     #     try:
#     #         model = mlflow.pyfunc.load_model(TMP_SAVE_DIR)
#     #         if isinstance(model, mlflow.pyfunc.PyFuncModel):
#     #             check["model_load_check"] = True
#     #         else:
#     #             logger.debug("Loaded model not correct instance type")
#     #             check["model_load_check"] = False
#     #     except Exception as e:
#     #         logger.debug("Error loading pyfunc model: {}".format(e))
#     #         check["model_load_check"] = False
#     #         continue
        
#     #     agg_checks += check["saved_model_checks"]
#     #     agg_checks.append(check["model_load_check"])
#     #     checks.append(check)

#     #     # remove temp dir
#     #     shutil.rmtree(TMP_SAVE_DIR)
#     # print(agg_checks)

#     # assert all(agg_checks) 
#     assert True

# # publish model tests
# def test_publish():
#     logger.info("Create Model Test")
#     results = []
#     for model in models:
#         print(model)
#         logger.info("Creating {} model".format(model["model_name"]))
#         chassis_model = client.create_model(process_fn=model["process_fn"])

#     assert True

# def test_publish_modzy_deploy():
#     assert True    

# def test_publish_manual_env_config():
#     assert True    

# def test_publish_gpu():
#     assert True    

# def test_publish_arm():
#     assert True    

# def test_publish_gpu_and_arm():
#     assert True    




# def test_get_job_status(client, logger):
#     logger.debug("test status")
#     assert True

# def test_block_until_complete():
#     assert True

# def test_omi_compliance():
#     assert True

# def test_download_tar():
#     assert True



# # Chassis Model methods test cases
   
