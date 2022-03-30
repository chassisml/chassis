import os
import mlflow
import time
import shutil
import sys
sys.path.append('./chassisml-sdk/')
import chassisml
# from .utils.models import assemble_models_dict
import logging
logging.basicConfig(level=logging.DEBUG, format= '%(levelname)s: %(message)s')

# Test cases ordered in flow of usage (i.e., you need to create a model before testing or publishing it)

# create model tests
def test_create_model(client, logger, models, test_name="test_create_model"):
    '''
    Tests the creation of a chassis model

    NOTE: the `create_model` method works in every scenario I ran, regardless of whether or not there is a valid connection to a running chassis service,
    so the only way I could think of testing this is via the `test_env` method

    Args:

    Returns:

    '''
    print("")
    logger.info("------- Create Model Test -------")
    results = []
    for model in models:
        logger.info("Creating {} model".format(model["model_name"]))
        chassis_model = client.create_model(process_fn=model["process_fn"])
        try:
            # only way to test if `create_model` method returns valid chassis model is by testing it using this function.
            # the local test
            local_test = chassis_model.test_env(model["test_file"])
            logger.info(local_test)
            results.append(local_test)
            if list(local_test.keys())[0] in ["model_error", "env_error"]:
                logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
                logger.error(local_test[list(local_test.keys())[0]])
            else:
                logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
        except Exception as e:
            results.append({"error": e})
            logger.debug("Error with {} model: {}".format(model["model_name"], e))
            continue

    # determine number of errors produced
    num_errors = 0
    for result in results:
        if list(result.keys())[0] in ["error", "model_error", "env_error"]:
            num_errors += 1

    return num_errors

def test_create_model_with_batch(client, logger, models, test_name="test_create_model_with_batch"):
    model = models[0]
    logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
    out = 1
    return out

# test model tests
def test_local_test(client, logger, models, test_name="test_local_test"):
    '''
    Tests local `test` method

    Args:

    Returns:

    '''
    logger.info("Test Chassis Model Locally")
    results = []
    for model in models:
        logger.info("Creating {} model".format(model["model_name"]))
        chassis_model = client.create_model(process_fn=model["process_fn"])
        local_test = chassis_model.test(model["test_file"])
        if local_test == model["local_test_result"]:
            logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
        else:
            logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
            logger.error(local_test)
        results.append(local_test == model["local_test_result"])

    return results    

def test_local_batch_test(client, logger, models, test_name="test_local_batch_test"):
    '''
    Tests local `test` method with batch process function

    Args:

    Returns:

    '''
    logger.info("Test Chassis Model Locally with Batch Process")
    results = []
    for model in models:
        logger.info("Creating {} model".format(model["model_name"]))
        chassis_model = client.create_model(process_fn=model["process_fn"])
        local_test = chassis_model.test(model["test_file"])
        if local_test == model["local_test_batch_result"]:
            logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
        else:
            logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
            logger.error(local_test)
        results.append(local_test == model["local_test_batch_result"])

    return results  

def test_env_test(client, logger, models, test_name="test_env_test"):
    '''
    Tests the creation of a chassis model

    NOTE: currently the tests for `create_model` and `test_env` are exactly the same

    Args:

    Returns:

    '''
    logger.info("Test Env with Chassis Model object")
    results = []
    for model in models:
        logger.info("Creating {} model".format(model["model_name"]))
        chassis_model = client.create_model(process_fn=model["process_fn"])
        try:
            # only way to test if `create_model` method returns valid chassis model is by testing it using this function.
            # the local test
            local_test = chassis_model.test_env(model["test_file"])
            logger.info(local_test)
            results.append(local_test)
            if list(local_test.keys())[0] in ["model_error", "env_error"]:
                logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
                logger.error(local_test[list(local_test.keys())[0]])
            else:
                logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))            
        except Exception as e:
            results.append({"error": e})
            logger.debug("Error with {} model: {}".format(model["model_name"], e))
            continue

    # determine number of errors produced
    num_errors = 0
    for result in results:
        if list(result.keys())[0] in ["error", "model_error", "env_error"]:
            num_errors += 1

    return num_errors

def test_env_test_manual_env_config(client, logger, models, test_name="test_env_test_manual_env_config"):
    '''
    TODO: this would be same as test_env test at the moment. Can't get test_env to work because of local module import issues
    '''
    logger.info("Test Env with Chassis Model object and manually configure conda environment")
    results = []
    for model in models:
        logger.info("Creating {} model".format(model["model_name"]))
        chassis_model = client.create_model(process_fn=model["process_fn"])
        try:
            # only way to test if `create_model` method returns valid chassis model is by testing it using this function.
            # the local test
            local_test = chassis_model.test_env(model["test_file"], conda_env=model["conda_env"])
            logger.info(local_test)
            results.append(local_test)
            if list(local_test.keys())[0] in ["model_error", "env_error"]:
                logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
                logger.error(local_test[list(local_test.keys())[0]])
            else:
                logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))            
        except Exception as e:
            results.append({"error": e})
            logger.debug("Error with {} model: {}".format(model["model_name"], e))
            continue

    # determine number of errors produced
    num_errors = 0
    for result in results:
        if list(result.keys())[0] in ["error", "model_error", "env_error"]:
            num_errors += 1

    return num_errors    
    

# save model locally tests
def test_save(client, logger, models, utils_path, test_name="test_save"):
    logger.info("Saving MLFlow model locally (default config)")
    checks = []
    agg_checks = []
    for model in models:
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
            logger.debug(e)
            check["saved_model_checks"] = False
            continue          
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
            logger.debug("Error loading pyfunc model: {}".format(e))
            check["model_load_check"] = False
            continue
        
        agg_checks += check["saved_model_checks"]
        agg_checks.append(check["model_load_check"])
        checks.append(check)

        # remove temp dir
        shutil.rmtree(TMP_SAVE_DIR)

    return agg_checks         

def test_save_manual_env_config(client, logger, models, utils_path, test_name="test_save_manual_env_config"):
    logger.info("Saving MLFlow model locally (manual config)")
    checks = []
    agg_checks = []
    for model in models:
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
            logger.debug(e)
            check["saved_model_checks"] = False
            continue          
        # load model and confirm it is the correct instance
        try:
            mlflow_model = mlflow.pyfunc.load_model(TMP_SAVE_DIR)
            if isinstance(mlflow_model, mlflow.pyfunc.PyFuncModel):
                check["model_load_check"] = True
                logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
            else:
                logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
                logger.error("Loaded model not correct instance type")
                check["model_load_check"] = False
        except Exception as e:
            logger.debug("Error loading pyfunc model: {}".format(e))
            check["model_load_check"] = False
            continue
        
        agg_checks += check["saved_model_checks"]
        agg_checks.append(check["model_load_check"])
        checks.append(check)

        # remove temp dir
        shutil.rmtree(TMP_SAVE_DIR)

    return agg_checks  

def test_save_gpu(client, logger, models, utils_path, test_name="test_save_gpu"):
    logger.info("Saving MLFlow model locally (with GPU)")
    checks = []
    agg_checks = []
    for model in models:
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
            logger.debug(e)
            check["saved_model_checks"] = False
            continue        
        # load model and confirm it is the correct instance
        try:
            mlflow_model = mlflow.pyfunc.load_model(TMP_SAVE_DIR)
            if isinstance(mlflow_model, mlflow.pyfunc.PyFuncModel):
                check["model_load_check"] = True
                logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
            else:
                logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
                logger.error("Loaded model not correct instance type")
                check["model_load_check"] = False
        except Exception as e:
            logger.debug("Error loading pyfunc model: {}".format(e))
            check["model_load_check"] = False
            continue
        
        agg_checks += check["saved_model_checks"]
        agg_checks.append(check["model_load_check"])
        checks.append(check)

        # remove temp dir
        shutil.rmtree(TMP_SAVE_DIR)

    return agg_checks 

def test_save_arm(client, logger, models, utils_path, test_name="test_save_arm"):
    logger.info("Saving MLFlow model locally (with ARM)")
    checks = []
    agg_checks = []
    for model in models:
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
            logger.debug(e)
            check["saved_model_checks"] = False
            continue        
        # load model and confirm it is the correct instance
        try:
            mlflow_model = mlflow.pyfunc.load_model(TMP_SAVE_DIR)
            if isinstance(mlflow_model, mlflow.pyfunc.PyFuncModel):
                check["model_load_check"] = True
                logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
            else:
                logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
                logger.error("Loaded model not correct instance type")
                check["model_load_check"] = False
        except Exception as e:
            logger.debug("Error loading pyfunc model: {}".format(e))
            check["model_load_check"] = False
            continue
        
        agg_checks += check["saved_model_checks"]
        agg_checks.append(check["model_load_check"])
        checks.append(check)

        # remove temp dir
        shutil.rmtree(TMP_SAVE_DIR)

    return agg_checks         

def test_save_gpu_and_arm(client, logger, models, utils_path, test_name="test_save_gpu_and_arm"):
    logger.info("Saving MLFlow model locally (with ARM and GPU)")
    checks = []
    agg_checks = []
    for model in models:
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
            logger.debug(e)
            check["saved_model_checks"] = False
            continue
        # load model and confirm it is the correct instance
        try:
            mlflow_model = mlflow.pyfunc.load_model(TMP_SAVE_DIR)
            if isinstance(mlflow_model, mlflow.pyfunc.PyFuncModel):
                check["model_load_check"] = True
                logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
            else:
                logger.info(" ******** FAILED - test:{}, model:{}".format(test_name, model["model_name"]))
                logger.error("Loaded model not correct instance type")
                check["model_load_check"] = False
        except Exception as e:
            logger.debug("Error loading pyfunc model: {}".format(e))
            check["model_load_check"] = False
            continue
        
        agg_checks += check["saved_model_checks"]
        agg_checks.append(check["model_load_check"])
        checks.append(check)

        # remove temp dir
        shutil.rmtree(TMP_SAVE_DIR)

    return agg_checks         


# publish model tests
def test_publish(client, logger, models, credentials, test_name="test_publish"):
    print("")
    logger.info("------- Publish Model Test -------")
    results = []
    for model in models:
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
                results.append({"error": response})
            else:
                logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
                job_id["model"] = model["model_name"]
                job_id["job_id"] = response.get("job_id")
                results.append(job_id)                
        except Exception as e:
            results.append({"error": e})
            logger.debug("Error with {} model: {}".format(model["model_name"], e))
            continue

    # determine number of errors produced
    num_errors = 0
    for result in results:
        if list(result.keys())[0] == "error":
            num_errors += 1

    return num_errors, results

def test_publish_modzy_deploy(client, logger, models, credentials, modzy_info, test_name="test_publish_modzy_deploy"):
    print("")
    logger.info("------- Publish Model Test Deploy to Modzy -------")
    results = []
    for model in models:
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
                results.append({"error": response})
            else:
                logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
                job_id["model"] = model["model_name"]
                job_id["job_id"] = response.get("job_id")
                results.append(job_id)                
        except Exception as e:
            results.append({"error": e})
            logger.debug("Error with {} model: {}".format(model["model_name"], e))
            continue

    # determine number of errors produced
    num_errors = 0
    for result in results:
        if list(result.keys())[0] == "error":
            num_errors += 1

    return num_errors, results 

def test_publish_manual_env_config(client, logger, models, credentials, test_name="test_publish_manual_env_config"):
    print("")
    logger.info("------- Publish Model Test Manual Env Config -------")
    results = []
    for model in models:
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
                results.append({"error": response})
            else:
                logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
                job_id["model"] = model["model_name"]
                job_id["job_id"] = response.get("job_id")
                results.append(job_id)                
        except Exception as e:
            results.append({"error": e})
            logger.debug("Error with {} model: {}".format(model["model_name"], e))
            continue

    # determine number of errors produced
    num_errors = 0
    for result in results:
        if list(result.keys())[0] == "error":
            num_errors += 1

    return num_errors, results   

def test_publish_gpu(client, logger, models, credentials, test_name="test_publish_gpu"):
    print("")
    logger.info("------- Publish Model Test GPU -------")
    results = []
    for model in models:
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
                results.append({"error": response})
            else:
                logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
                job_id["model"] = model["model_name"]
                job_id["job_id"] = response.get("job_id")
                results.append(job_id)                
        except Exception as e:
            results.append({"error": e})
            logger.debug("Error with {} model: {}".format(model["model_name"], e))
            continue

    # determine number of errors produced
    num_errors = 0
    for result in results:
        if list(result.keys())[0] == "error":
            num_errors += 1

    return num_errors, results    

def test_publish_arm(client, logger, models, credentials, test_name="test_publish_arm"):
    print("")
    logger.info("------- Publish Model Test ARM -------")
    results = []
    for model in models:
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
                results.append({"error": response})
            else:
                logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
                job_id["model"] = model["model_name"]
                job_id["job_id"] = response.get("job_id")
                results.append(job_id)                
        except Exception as e:
            results.append({"error": e})
            logger.debug("Error with {} model: {}".format(model["model_name"], e))
            continue

    # determine number of errors produced
    num_errors = 0
    for result in results:
        if list(result.keys())[0] == "error":
            num_errors += 1

    return num_errors, results

def test_publish_gpu_and_arm(client, logger, models, credentials, test_name="test_publish_gpu_and_arm"):
    print("")
    logger.info("------- Publish Model Test GPU/ARM -------")
    results = []
    for model in models:
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
                results.append({"error": response})
            else:
                logger.info(" ******** PASSED - test:{}, model:{}".format(test_name, model["model_name"]))
                job_id["model"] = model["model_name"]
                job_id["job_id"] = response.get("job_id")
                results.append(job_id)                
        except Exception as e:
            results.append({"error": e})
            logger.debug("Error with {} model: {}".format(model["model_name"], e))
            continue

    # determine number of errors produced
    num_errors = 0
    for result in results:
        if list(result.keys())[0] == "error":
            num_errors += 1

    return num_errors, results




def test_get_job_status(client, logger, job_ids):
    
    logger.debug("test status")
    assert True

def test_block_until_complete():
    assert True

def test_omi_compliance():
    assert True

def test_download_tar():
    assert True



# run test cases
if __name__ == "__main__":
    
    # fixtures used throughout all test cases
    logger = logging.getLogger(__name__)
     
    client = chassisml.ChassisClient(HOST_URL)
    models = assemble_models_dict()

    # run tests for each model in the models dictionary   
