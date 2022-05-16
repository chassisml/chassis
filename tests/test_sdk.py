import os
import mlflow
import time
import shutil
import docker
import sys
sys.path.append('./chassisml_sdk/')
import chassisml
import logging
logging.basicConfig(level=logging.INFO, format= '%(levelname)s: %(message)s')

# Test cases ordered in flow of usage (i.e., you need to create a model before testing or publishing it)

# create model tests
def test_create_model(client, logger, model, test_name="test_create_model"):
    '''
    Tests the creation of a chassis model

    NOTE: the `create_model` method works in every scenario I ran, regardless of whether or not there is a valid connection to a running chassis service,
    so the only way I could think of testing this is via the `test_env` method

    '''
    print("\n")
    logger.info("------- Create Model Test -------")
    logger.info("Creating {} model".format(model["model_name"]))
    chassis_model = client.create_model(process_fn=model["process_fn"])
    try:
        # only way to test if `create_model` method returns valid chassis model is by testing it using this function.
        # the local test
        local_test = chassis_model.test_env(model["test_file"])
        logger.info(local_test)
        result = local_test
        if list(local_test.keys())[0] in ["model_error", "env_error"]:
            logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
            logger.error(local_test[list(local_test.keys())[0]])
        else:
            logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
    except Exception as e:
        result = {"error": e}
        logger.error("Error with {} model: {}".format(model["model_name"], e))

    # determine number of errors produced
    output = 1
    if list(result.keys())[0] in ["error", "model_error", "env_error"]:
        output = 0

    return output

def test_create_model_with_batch(client, logger, model, test_name="test_create_model_with_batch"):
    print("\n")
    logger.info("------- Create Model Test (with Batch Process Function) -------")
    logger.info("Creating {} model".format(model["model_name"]))
    if model["batch_process_fn"] is None:
        logger.info("Skipping model {}, batch_process_fn not defined".format(model["model_name"]))
        logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
        result = {"skipped": model["model_name"]}
    else:
        chassis_model = client.create_model(batch_process_fn=model["batch_process_fn"], batch_size=4)
        try:
            # only way to test if `create_model` method returns valid chassis model is by testing it using this function.
            # the local test
            local_test = chassis_model.test_env(model["test_file"])
            logger.info(local_test)
            result = local_test
            if list(local_test.keys())[0] in ["model_error", "env_error"]:
                logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
                logger.error(local_test[list(local_test.keys())[0]])
            else:
                logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
        except Exception as e:
            result = {"error": e}
            logger.error("Error with {} model: {}".format(model["model_name"], e))

    # determine number of errors produced
    output = 1
    if list(result.keys())[0] in ["error", "model_error", "env_error"]:
        output = 0

    return output

# test model tests
def test_local_test(client, logger, model, test_name="test_local_test"):
    '''
    Tests local `test` method

    Args:

    Returns:

    '''
    print("\n")
    logger.info("------- Test Chassis Model Locally -------")
    logger.info("Creating {} model".format(model["model_name"]))
    chassis_model = client.create_model(process_fn=model["process_fn"])
    local_test = chassis_model.test(model["test_file"])
    if local_test == model["local_test_result"]:
        logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
    else:
        logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
        logger.error(local_test)
    result = 1 if local_test == model["local_test_result"] else 0

    return result 

def test_local_batch_test(client, logger, model, test_name="test_local_batch_test"):
    '''
    Tests local `test` method with batch process function

    Args:

    Returns:

    '''
    print("\n")
    logger.info("------- Test Chassis Model Locally with Batch Process -------")
    if model["batch_process_fn"] is None:
        logger.info("Skipping model {}, batch_process_fn not defined".format(model["model_name"]))
        logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
        result = 1
    else:        
        logger.info("Creating {} model".format(model["model_name"]))
        chassis_model = client.create_model(batch_process_fn=model["batch_process_fn"], batch_size=4)
        local_test = chassis_model.test_batch(model["test_file"])
        if local_test == model["local_test_batch_result"]:
            logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
        else:
            logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
            logger.error(local_test)
        result = 1 if local_test == model["local_test_batch_result"] else 0

    return result  

def test_env_test(client, logger, model, test_name="test_env_test"):
    '''
    Tests the creation of a chassis model

    NOTE: currently the tests for `create_model` and `test_env` are exactly the same

    Args:

    Returns:

    '''
    print("\n")
    logger.info("------- Test Env with Chassis Model object -------")
    logger.info("Creating {} model".format(model["model_name"]))
    chassis_model = client.create_model(process_fn=model["process_fn"])
    try:
        # only way to test if `create_model` method returns valid chassis model is by testing it using this function.
        # the local test
        local_test = chassis_model.test_env(model["test_file"])
        logger.info(local_test)
        result = local_test
        if list(local_test.keys())[0] in ["model_error", "env_error"]:
            logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
            logger.error(local_test[list(local_test.keys())[0]])
        else:
            logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))            
    except Exception as e:
        result = {"error": e}
        logger.error("Error with {} model: {}".format(model["model_name"], e))

    # determine number of errors produced
    output = 1
    if list(result.keys())[0] in ["error", "model_error", "env_error"]:
        output = 0    

    return output

def test_env_test_manual_env_config(client, logger, model, test_name="test_env_test_manual_env_config"):
    '''
    TODO: this would be same as test_env test at the moment. Can't get test_env to work because of local module import issues
    '''
    print("\n")
    logger.info("------- Test Env with Chassis Model object and manually configure conda environment -------")
    logger.info("Creating {} model".format(model["model_name"]))
    chassis_model = client.create_model(process_fn=model["process_fn"])
    try:
        # only way to test if `create_model` method returns valid chassis model is by testing it using this function.
        # the local test
        local_test = chassis_model.test_env(model["test_file"], conda_env=model["conda_env"])
        logger.info(local_test)
        result = local_test
        if list(local_test.keys())[0] in ["model_error", "env_error"]:
            logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
            logger.error(local_test[list(local_test.keys())[0]])
        else:
            logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))            
    except Exception as e:
        result = {"error": e}
        logger.error("Error with {} model: {}".format(model["model_name"], e))

    # determine number of errors produced
    output = 1
    if list(result.keys())[0] in ["error", "model_error", "env_error"]:
        output = 0    

    return output 
    

# save model locally tests
def test_save(client, logger, model, utils_path, test_name="test_save"):
    print("\n")
    logger.info("------- Saving MLFlow model locally (default config) -------")
    agg_checks = []
    check = {}
    check["model"] = model["model_name"]
    check["saved_model_checks"] = []
    logger.info("Creating {} model".format(model["model_name"]))
    # build model
    chassis_model = client.create_model(process_fn=model["process_fn"])    
    # create temp dir
    TMP_SAVE_DIR = os.path.join(utils_path, "tmp-model")
    # save chassis model
    if os.path.isdir(TMP_SAVE_DIR):
        shutil.rmtree(TMP_SAVE_DIR)
    try:
        chassis_model.save(TMP_SAVE_DIR, overwrite=False, fix_env=True, gpu=False, arm64=False)
        # check expected files exist + model can be loaded using mlflow pyfunc load_model method
        check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "conda.yaml")))
        check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "MLmodel")))
        check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "python_model.pkl")))
        check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "requirements.txt")))
    except Exception as e:
        logger.error(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
        logger.error(e)
        check["saved_model_checks"] = [False]
    # load model and confirm it is the correct instance
    try:
        logger.info(TMP_SAVE_DIR)
        mlflow_model = mlflow.pyfunc.load_model(TMP_SAVE_DIR)
        if isinstance(mlflow_model, mlflow.pyfunc.PyFuncModel):
            check["model_load_check"] = True
            logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
        else:
            logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
            logger.error("Loaded model not correct instance type")
            check["model_load_check"] = False
    except Exception as e:
        logger.error("Error loading pyfunc model: {}".format(e))
        check["model_load_check"] = False
    
    agg_checks += check["saved_model_checks"]
    agg_checks.append(check["model_load_check"])

    # remove temp dir
    shutil.rmtree(TMP_SAVE_DIR)

    output = 0
    if all(agg_checks):
        output = 1

    return output         

def test_save_manual_env_config(client, logger, model, utils_path, test_name="test_save_manual_env_config"):
    print("\n")
    logger.info("------- Saving MLFlow model locally (manual config) -------")
    agg_checks = []
    check = {}
    check["model"] = model["model_name"]
    check["saved_model_checks"] = []
    logger.info("Creating {} model".format(model["model_name"]))
    # build model
    chassis_model = client.create_model(process_fn=model["process_fn"])    
    # create temp dir
    TMP_SAVE_DIR = os.path.join(utils_path, "tmp-model")
    # save chassis model
    if os.path.isdir(TMP_SAVE_DIR):
        shutil.rmtree(TMP_SAVE_DIR)
    try:
        chassis_model.save(TMP_SAVE_DIR, conda_env=model["conda_env"], overwrite=False, fix_env=True, gpu=False, arm64=False)
        # check expected files exist + model can be loaded using mlflow pyfunc load_model method
        check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "conda.yaml")))
        check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "MLmodel")))
        check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "python_model.pkl")))
        check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "requirements.txt")))
    except Exception as e:
        logger.error(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
        logger.error(e)
        check["saved_model_checks"] = [False]
    # load model and confirm it is the correct instance
    try:
        logger.info(TMP_SAVE_DIR)
        mlflow_model = mlflow.pyfunc.load_model(TMP_SAVE_DIR)
        if isinstance(mlflow_model, mlflow.pyfunc.PyFuncModel):
            check["model_load_check"] = True
            logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
        else:
            logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
            logger.error("Loaded model not correct instance type")
            check["model_load_check"] = False
    except Exception as e:
        logger.error("Error loading pyfunc model: {}".format(e))
        check["model_load_check"] = False
    
    agg_checks += check["saved_model_checks"]
    agg_checks.append(check["model_load_check"])

    # remove temp dir
    shutil.rmtree(TMP_SAVE_DIR)

    output = 0
    if all(agg_checks):
        output = 1

    return output      

def test_save_gpu(client, logger, model, utils_path, test_name="test_save_gpu"):
    print("\n")
    logger.info("------- Saving MLFlow model locally (with GPU) -------")
    agg_checks = []
    check = {}
    check["model"] = model["model_name"]
    check["saved_model_checks"] = []
    logger.info("Creating {} model".format(model["model_name"]))
    # build model
    chassis_model = client.create_model(process_fn=model["process_fn"])    
    # create temp dir
    TMP_SAVE_DIR = os.path.join(utils_path, "tmp-model")
    # save chassis model
    if os.path.isdir(TMP_SAVE_DIR):
        shutil.rmtree(TMP_SAVE_DIR)
    try:
        chassis_model.save(TMP_SAVE_DIR, overwrite=False, fix_env=True, gpu=True, arm64=False)
        # check expected files exist + model can be loaded using mlflow pyfunc load_model method
        check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "conda.yaml")))
        check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "MLmodel")))
        check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "python_model.pkl")))
        check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "requirements.txt")))
    except Exception as e:
        logger.error(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
        logger.error(e)
        check["saved_model_checks"] = [False]
    # load model and confirm it is the correct instance
    try:
        logger.info(TMP_SAVE_DIR)
        mlflow_model = mlflow.pyfunc.load_model(TMP_SAVE_DIR)
        if isinstance(mlflow_model, mlflow.pyfunc.PyFuncModel):
            check["model_load_check"] = True
            logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
        else:
            logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
            logger.error("Loaded model not correct instance type")
            check["model_load_check"] = False
    except Exception as e:
        logger.error("Error loading pyfunc model: {}".format(e))
        check["model_load_check"] = False
    
    agg_checks += check["saved_model_checks"]
    agg_checks.append(check["model_load_check"])

    # remove temp dir
    shutil.rmtree(TMP_SAVE_DIR)

    output = 0
    if all(agg_checks):
        output = 1

    return output

def test_save_arm(client, logger, model, utils_path, test_name="test_save_arm"):
    print("\n")
    logger.info("------- Saving MLFlow model locally (with ARM) -------")
    agg_checks = []
    check = {}
    check["model"] = model["model_name"]
    check["saved_model_checks"] = []
    logger.info("Creating {} model".format(model["model_name"]))
    # build model
    chassis_model = client.create_model(process_fn=model["process_fn"])    
    # create temp dir
    TMP_SAVE_DIR = os.path.join(utils_path, "tmp-model")
    # save chassis model
    if os.path.isdir(TMP_SAVE_DIR):
        shutil.rmtree(TMP_SAVE_DIR)
    try:
        chassis_model.save(TMP_SAVE_DIR, overwrite=False, fix_env=True, gpu=False, arm64=True)
        # check expected files exist + model can be loaded using mlflow pyfunc load_model method
        check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "conda.yaml")))
        check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "MLmodel")))
        check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "python_model.pkl")))
        check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "requirements.txt")))
    except Exception as e:
        logger.error(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
        logger.error(e)
        check["saved_model_checks"] = [False]
    # load model and confirm it is the correct instance
    try:
        logger.info(TMP_SAVE_DIR)
        mlflow_model = mlflow.pyfunc.load_model(TMP_SAVE_DIR)
        if isinstance(mlflow_model, mlflow.pyfunc.PyFuncModel):
            check["model_load_check"] = True
            logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
        else:
            logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
            logger.error("Loaded model not correct instance type")
            check["model_load_check"] = False
    except Exception as e:
        logger.error("Error loading pyfunc model: {}".format(e))
        check["model_load_check"] = False
    
    agg_checks += check["saved_model_checks"]
    agg_checks.append(check["model_load_check"])

    # remove temp dir
    shutil.rmtree(TMP_SAVE_DIR)

    output = 0
    if all(agg_checks):
        output = 1

    return output    

def test_save_gpu_and_arm(client, logger, model, utils_path, test_name="test_save_gpu_and_arm"):
    print("\n")
    logger.info("------- Saving MLFlow model locally (with ARM and GPU) -------")
    agg_checks = []
    check = {}
    check["model"] = model["model_name"]
    check["saved_model_checks"] = []
    logger.info("Creating {} model".format(model["model_name"]))
    # build model
    chassis_model = client.create_model(process_fn=model["process_fn"])    
    # create temp dir
    TMP_SAVE_DIR = os.path.join(utils_path, "tmp-model")
    # save chassis model
    if os.path.isdir(TMP_SAVE_DIR):
        shutil.rmtree(TMP_SAVE_DIR)
    try:
        chassis_model.save(TMP_SAVE_DIR, overwrite=False, fix_env=True, gpu=True, arm64=True)
        # check expected files exist + model can be loaded using mlflow pyfunc load_model method
        check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "conda.yaml")))
        check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "MLmodel")))
        check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "python_model.pkl")))
        check["saved_model_checks"].append(os.path.isfile(os.path.join(TMP_SAVE_DIR, "requirements.txt")))
    except Exception as e:
        logger.error(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
        logger.error(e)
        check["saved_model_checks"] = [False]
    # load model and confirm it is the correct instance
    try:
        logger.info(TMP_SAVE_DIR)
        mlflow_model = mlflow.pyfunc.load_model(TMP_SAVE_DIR)
        if isinstance(mlflow_model, mlflow.pyfunc.PyFuncModel):
            check["model_load_check"] = True
            logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
        else:
            logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
            logger.error("Loaded model not correct instance type")
            check["model_load_check"] = False
    except Exception as e:
        logger.error("Error loading pyfunc model: {}".format(e))
        check["model_load_check"] = False
    
    agg_checks += check["saved_model_checks"]
    agg_checks.append(check["model_load_check"])

    # remove temp dir
    shutil.rmtree(TMP_SAVE_DIR)

    output = 0
    if all(agg_checks):
        output = 1

    return output      


# publish model tests
def test_publish(client, logger, model, credentials, test_name="test_publish"):
    print("\n")
    logger.info("------- Publish Model Test -------")
    job_id = {}
    logger.info("Creating {} model".format(model["model_name"]))
    chassis_model = client.create_model(process_fn=model["process_fn"])
    try:
        response = chassis_model.publish(
            model_name=model["model_name"],
            model_version=model["model_version"],
            registry_user=credentials["user"],
            registry_pass=credentials["pass"]                
        )
        logger.info(response)
        if response["error"]:
            logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
            logger.error(response)
            result = {"error": response, "model": model["model_name"]}
        else:
            logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
            job_id["model"] = model["model_name"]
            job_id["job_id"] = response.get("job_id")
            result = job_id                
    except Exception as e:
        result = {"error": e, "model": model["model_name"]}
        logger.error("Error with {} model: {}".format(model["model_name"], e))

    # determine number of errors produced
    output = 1
    if list(result.keys())[0] == "error":
        output = 0

    return output, result

def test_publish_modzy_deploy(client, logger, model, credentials, modzy_info, test_name="test_publish_modzy_deploy"):
    print("\n")
    logger.info("------- Publish Model Test Deploy to Modzy -------")
    job_id = {}
    logger.info("Creating {} model".format(model["model_name"]))
    chassis_model = client.create_model(process_fn=model["process_fn"])
    try:
        response = chassis_model.publish(
            model_name=model["model_name"],
            model_version=model["model_version"],
            registry_user=credentials["user"],
            registry_pass=credentials["pass"],
            modzy_sample_input_path=modzy_info["sample_filepath"],
            modzy_api_key=modzy_info["modzy_api_key"],
            modzy_url=modzy_info["modzy_url"]                                
        )
        logger.info(response)
        if response["error"]:
            logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
            logger.error(response)
            result = {"error": response, "model": model["model_name"]}
        else:
            logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
            job_id["model"] = model["model_name"]
            job_id["job_id"] = response.get("job_id")
            result = job_id                
    except Exception as e:
        result = {"error": e, "model": model["model_name"]}
        logger.error("Error with {} model: {}".format(model["model_name"], e))

    # determine number of errors produced
    output = 1
    if list(result.keys())[0] == "error":
        output = 0

    return output, result    

def test_publish_manual_env_config(client, logger, model, credentials, test_name="test_publish_manual_env_config"):
    print("\n")
    logger.info("------- Publish Model Test Manual Env Config -------")
    job_id = {}
    logger.info("Creating {} model".format(model["model_name"]))
    chassis_model = client.create_model(process_fn=model["process_fn"])
    try:
        response = chassis_model.publish(
            model_name=model["model_name"],
            model_version=model["model_version"],
            registry_user=credentials["user"],
            registry_pass=credentials["pass"],
            conda_env=model["conda_env"]                
        )
        logger.info(response)
        if response["error"]:
            logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
            logger.error(response)
            result = {"error": response, "model": model["model_name"]}
        else:
            logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
            job_id["model"] = model["model_name"]
            job_id["job_id"] = response.get("job_id")
            result = job_id                
    except Exception as e:
        result = {"error": e, "model": model["model_name"]}
        logger.error("Error with {} model: {}".format(model["model_name"], e))

    # determine number of errors produced
    output = 1
    if list(result.keys())[0] == "error":
        output = 0

    return output, result    

def test_publish_gpu(client, logger, model, credentials, test_name="test_publish_gpu"):
    print("\n")
    logger.info("------- Publish Model Test GPU -------")
    job_id = {}
    logger.info("Creating {} model".format(model["model_name"]))
    chassis_model = client.create_model(process_fn=model["process_fn"])
    try:
        response = chassis_model.publish(
            model_name=model["model_name"],
            model_version=model["model_version"],
            registry_user=credentials["user"],
            registry_pass=credentials["pass"],
            gpu=True                
        )
        logger.info(response)
        if response["error"]:
            logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
            logger.error(response)
            result = {"error": response, "model": model["model_name"]}
        else:
            logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
            job_id["model"] = model["model_name"]
            job_id["job_id"] = response.get("job_id")
            result = job_id                
    except Exception as e:
        result = {"error": e, "model": model["model_name"]}
        logger.error("Error with {} model: {}".format(model["model_name"], e))

    # determine number of errors produced
    output = 1
    if list(result.keys())[0] == "error":
        output = 0

    return output, result    
    
def test_publish_arm(client, logger, model, credentials, test_name="test_publish_arm"):
    print("\n")
    logger.info("------- Publish Model Test ARM -------")
    job_id = {}
    logger.info("Creating {} model".format(model["model_name"]))
    chassis_model = client.create_model(process_fn=model["process_fn"])
    try:
        response = chassis_model.publish(
            model_name=model["model_name"],
            model_version=model["model_version"],
            registry_user=credentials["user"],
            registry_pass=credentials["pass"],
            arm64=True               
        )
        logger.info(response)
        if response["error"]:
            logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
            logger.error(response)
            result = {"error": response, "model": model["model_name"]}
        else:
            logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
            job_id["model"] = model["model_name"]
            job_id["job_id"] = response.get("job_id")
            result = job_id                
    except Exception as e:
        result = {"error": e, "model": model["model_name"]}
        logger.error("Error with {} model: {}".format(model["model_name"], e))

    # determine number of errors produced
    output = 1
    if list(result.keys())[0] == "error":
        output = 0

    return output, result    

def test_publish_gpu_and_arm(client, logger, model, credentials, test_name="test_publish_gpu_and_arm"):
    print("\n")
    logger.info("------- Publish Model Test GPU/ARM -------")
    job_id = {}
    logger.info("Creating {} model".format(model["model_name"]))
    chassis_model = client.create_model(process_fn=model["process_fn"])
    try:
        response = chassis_model.publish(
            model_name=model["model_name"],
            model_version=model["model_version"],
            registry_user=credentials["user"],
            registry_pass=credentials["pass"],
            gpu=True,
            arm64=True               
        )
        logger.info(response)
        if response["error"]:
            logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
            logger.error(response)
            result = {"error": response, "model": model["model_name"]}
        else:
            logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
            job_id["model"] = model["model_name"]
            job_id["job_id"] = response.get("job_id")
            result = job_id                
    except Exception as e:
        result = {"error": e, "model": model["model_name"]}
        logger.error("Error with {} model: {}".format(model["model_name"], e))

    # determine number of errors produced
    output = 1
    if list(result.keys())[0] == "error":
        output = 0

    return output, result    


# chassis client tests
def test_get_job_status(client, logger, job, test_name="test_get_job_status"):
    print("\n")
    try:  
        logger.info("------- Job Status Test -------")
        logger.info("Checking Status of job {} for model {}".format(job["job_id"], job["model"]))
        status = client.get_job_status(job["job_id"])
        if status["status"]["active"] == 1:
            logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, job["model"]))
            result = 1
        else:
            logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, job["model"]))
            logger.error(status)
            result = 0                                
    except Exception as e:
        logger.error("Error with {} model: {}".format(job["model"], e))
        result = 0

    return result           

def test_block_until_complete(client, logger, job, test_name="test_block_until_complete"):
    print("\n")
    try:
        logger.info("------- Block Until Complete Test -------")
        logger.info("Checking Status of job {} for model {}".format(job["job_id"], job["model"]))        
        status = client.block_until_complete(job["job_id"])
        if status["status"]["failed"] is None and status["status"]["conditions"][0]["type"] == "Complete":
            logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, job["model"]))
            result = 1
        else:
            logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, job["model"]))
            logger.error(status)
            result = 0                                
    except Exception as e:
        logger.error("Error with {} model: {}".format(job["model"], e))
        result = 0

    return result    
    
def test_download_tar(client, logger, job, out_path, test_name="test_download_tar"):
    print("\n")
    logger.info("------- Download Tar File Test -------")  
    out_path = ""
    model_name_edited = job["model"].lower().replace(" ", "-")
    TMP_DOWNLOAD_DIR = os.path.join(out_path, model_name_edited + ".tar")
    if os.path.isdir(TMP_DOWNLOAD_DIR):
        shutil.rmtree(TMP_DOWNLOAD_DIR)          
    try:
        logger.info("Download tar for model {}".format(job["model"]))
        client.download_tar(job["job_id"], TMP_DOWNLOAD_DIR)
        if os.path.isfile(TMP_DOWNLOAD_DIR):
            logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, job["model"]))
            out_path = TMP_DOWNLOAD_DIR
            result = 1
        else:
            logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, job["model"]))
            result = 0                                
    except Exception as e:
        logger.error("Error with {} model: {}".format(job["model"], e))
        result = 0   
    
    return result, out_path

def test_omi_compliance(client, logger, path, test_name="test_omi_compliance"):
    print("\n")
    logger.info("------- OMI Compliance Test -------")
    docker_client = docker.from_env()
    try:
        with open(os.path.join(path), "rb") as f:
            image_repo_tag = docker_client.images.load(f)[0].attrs["RepoTags"][0]
        compliance = client.test_OMI_compliance(image_repo_tag)
        if compliance[0]:
            logger.info(" ******** PASSED - test:{}, tar:{}".format(test_name, path))
            result = 1
        else:
            logger.info(" ******** FAILED - test:{}, tar:{}".format(test_name, path))
            result = 0                 
    except Exception as e:
        logger.error("Error with path {}".format(path, e))
        result = 0

    # remove temp dir
    if os.path.isfile(path):
        os.remove(path)    

    return result              

