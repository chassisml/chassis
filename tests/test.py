import os
import numpy as np
import json
import pickle
import time
import sys
sys.path.append('./chassisml_sdk/')
import chassisml
from tests.test_connection import *
from tests.test_sdk import *
import logging
logging.basicConfig(level=logging.INFO, format= '%(levelname)s: %(message)s')

# model specific packages
# Scikit Leran
from sklearn.linear_model import LogisticRegression
from sklearn import datasets
# PyTorch
import cv2
import torch
import torchvision.models as models
from torchvision import transforms

# TODO: instantiate HOST_URL in __init__
HOST_URL = "http://localhost:5000"
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
UTILS_PATH = os.path.join(ROOT_DIR, "utils")


def assemble_models_dict(hello_world, sklearn, pytorch):
    models = [
        {
            "short": "hello-world",
            "model_name": "Unit Test Hello World",
            "model_version": "0.0.1",
            "process_fn": hello_world["process"],
            "batch_process_fn": hello_world["batch_process"],
            "conda_env": hello_world["env"],
            "test_file": os.path.join(UTILS_PATH, "data", "hello-world.txt"),
            "local_test_result": b'"Hello World!"',
            "local_test_batch_result": None
        },
        {
            "short": "scikit",
            "model_name": "Unit Test Scikit Learn Classifier",
            "model_version": "0.0.1",
            "process_fn": sklearn["process"],
            "batch_process_fn": sklearn["batch_process"],
            "conda_env": sklearn["env"],
            "test_file": os.path.join(UTILS_PATH, "data", "digits_sample.json"),
            "local_test_result": b'[{"data":{"result":{"classPredictions":[{"class":"5","score":"1"}]}}},{"data":{"result":{"classPredictions":[{"class":"2","score":"1"}]}}},{"data":{"result":{"classPredictions":[{"class":"8","score":"1"}]}}},{"data":{"result":{"classPredictions":[{"class":"0","score":"1"}]}}},{"data":{"result":{"classPredictions":[{"class":"1","score":"1"}]}}}]',
            "local_test_batch_result": None
        },
        {
            "short": "pytorch",
            "model_name": "Unit Test PyTorch",
            "model_version": "0.0.1",
            "process_fn": pytorch["process"],
            "batch_process_fn": pytorch["batch_process"],
            "conda_env": pytorch_env,
            "test_file": os.path.join(UTILS_PATH, "data", "airplane.jpg"),
            "local_test_result": b'[{"classPredictions":[{"class":"airliner","score":0.606},{"class":"crane","score":0.11},{"class":"wing","score":0.103},{"class":"chain saw, chainsaw","score":0.07},{"class":"aircraft carrier, carrier, flattop, attack aircraft carrier","score":0.048}]}]',
            "local_test_batch_result": [b'{"classPredictions":[{"class":"airliner","score":0.606},{"class":"crane","score":0.11},{"class":"wing","score":0.103},{"class":"chain saw, chainsaw","score":0.07},{"class":"aircraft carrier, carrier, flattop, attack aircraft carrier","score":0.048}]}', b'{"classPredictions":[{"class":"airliner","score":0.606},{"class":"crane","score":0.11},{"class":"wing","score":0.103},{"class":"chain saw, chainsaw","score":0.07},{"class":"aircraft carrier, carrier, flattop, attack aircraft carrier","score":0.048}]}', b'{"classPredictions":[{"class":"airliner","score":0.606},{"class":"crane","score":0.11},{"class":"wing","score":0.103},{"class":"chain saw, chainsaw","score":0.07},{"class":"aircraft carrier, carrier, flattop, attack aircraft carrier","score":0.048}]}', b'{"classPredictions":[{"class":"airliner","score":0.606},{"class":"crane","score":0.11},{"class":"wing","score":0.103},{"class":"chain saw, chainsaw","score":0.07},{"class":"aircraft carrier, carrier, flattop, attack aircraft carrier","score":0.048}]}']
        },        
    ]
    return models


if __name__ == "__main__":
    
    # fixtures used throughout all test cases
    logger = logging.getLogger(__name__)
     
    client = chassisml.ChassisClient(HOST_URL)
    docker_creds = {
        "user": os.getenv("DOCKER_USER"),
        "pass": os.getenv("DOCKER_PASS")
    }

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
                    "chassisml",
                ] 
            }
        ]
    }

    '''
    Scikit-Learn Model
    '''

    # Import and normalize data
    X_digits, y_digits = datasets.load_digits(return_X_y=True)
    X_digits = X_digits / X_digits.max()

    n_samples = len(X_digits)

    # Split data into training and test sets
    X_train = X_digits[: int(0.9 * n_samples)]
    y_train = y_digits[: int(0.9 * n_samples)]
    X_test = X_digits[int(0.9 * n_samples) :]
    y_test = y_digits[int(0.9 * n_samples) :]

    # Train Model
    logistic = LogisticRegression(max_iter=1000)
    print(
        "LogisticRegression mean accuracy score: %f"
        % logistic.fit(X_train, y_train).score(X_test, y_test)
    )    

    def process_sklearn(input_bytes):
        inputs = np.array(json.loads(input_bytes))
        inference_results = logistic.predict(inputs)
        structured_results = []
        for inference_result in inference_results:
            structured_output = {
                "data": {
                    "result": {"classPredictions": [{"class": str(inference_result), "score": str(1)}]}
                }
            }
            structured_results.append(structured_output)
        return structured_results    

    sklearn_env = {
        "name": "sklearn-chassis",
        "channels": ['conda-forge'],
        "dependencies": [
            "python=3.8.5",
            {
                "pip": [
                    "scikit-learn",
                    "numpy",
                    "chassisml"
                ] 
            }
        ]
    }

    '''
    PyTorch Model
    '''

    model_pytorch = models.resnet50(pretrained=True)
    model_pytorch.eval()

    labels = pickle.load(open('./chassisml-sdk/examples/pytorch/data/imagenet_labels.pkl','rb'))

    transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])        

    device = 'cuda'
    model_pytorch.to(device)

    def process_pytorch(input_bytes):
        
        # preprocess list of inputs
        decoded = cv2.imdecode(np.frombuffer(input_bytes, np.uint8), -1)
        resized = cv2.resize(decoded, (224, 224)).reshape((1,224,224,3))
        images = [resized]
        images_arr = np.concatenate(images)
        batch_t = torch.stack(tuple(transform(i) for i in images_arr), dim=0).to(device)

        # run batch inference and softmax
        output = model_pytorch(batch_t)
        probs = torch.nn.functional.softmax(output, dim=1)
        softmax_preds = probs.detach().cpu().numpy()
        
        # postprocess
        all_formatted_results = []
        for preds in softmax_preds: 
            indices = np.argsort(preds)[::-1]
            classes = [labels[idx] for idx in indices[:5]]
            scores = [float(preds[idx]) for idx in indices[:5]]
            preds = [{"class": "{}".format(label), "score": round(float(score),3)} for label, score in zip(classes, scores)]
            preds.sort(key = lambda x: x["score"],reverse=True)
            results = {"classPredictions": preds}
            all_formatted_results.append(results)
        
        # output list of formatted results
        return all_formatted_results    

    def batch_process_pytorch(inputs_list):
        
        # preprocess list of inputs
        images = []
        for input in inputs_list:
            decoded = cv2.imdecode(np.frombuffer(input, np.uint8), -1)
            resized = cv2.resize(decoded, (224, 224)).reshape((1,224,224,3))
            images.append(resized)
        images_arr = np.concatenate(images)
        batch_t = torch.stack(tuple(transform(i) for i in images_arr), dim=0).to(device)

        # run batch inference and softmax
        output = model_pytorch(batch_t)
        probs = torch.nn.functional.softmax(output, dim=1)
        softmax_preds = probs.detach().cpu().numpy()
        
        # postprocess
        all_formatted_results = []
        for preds in softmax_preds: 
            indices = np.argsort(preds)[::-1]
            classes = [labels[idx] for idx in indices[:5]]
            scores = [float(preds[idx]) for idx in indices[:5]]
            preds = [{"class": "{}".format(label), "score": round(float(score),3)} for label, score in zip(classes, scores)]
            preds.sort(key = lambda x: x["score"],reverse=True)
            results = {"classPredictions": preds}
            all_formatted_results.append(results)
        
        # output list of formatted results
        return all_formatted_results    

    pytorch_env = {
        "name": "pytorch-chassis",
        "channels": ['conda-forge'],
        "dependencies": [
            "python=3.8.5",
            {
                "pip": [
                    "torch",
                    "torchvision",
                    "opencv-python"
                    "numpy",
                    "chassisml"
                ] 
            }
        ]        
    }
    
    hello_world_dict = {
        "env": hello_world_env,
        "process": process_hello,
        "batch_process": None
    }
    sklearn_dict = {
        "env": sklearn_env,
        "process": process_sklearn,
        "batch_process": None
    }
    pytorch_dict = {
        "env": pytorch_env,
        "process": process_pytorch,
        "batch_process": batch_process_pytorch
    }
    models = assemble_models_dict(hello_world_dict, sklearn_dict, pytorch_dict)
    
    ALL_TEST_RESULTS = {}
    # test connection
    out = test_can_connect_to_service(HOST_URL, logger, "test_can_connect_to_service")
    
    # test sdk for each model 
    for model in models:
        TEST_RESULTS = []
        modzy_creds = {
            "sample_filepath": model["test_file"],
            "modzy_api_key": os.getenv("MODZY_API_KEY"),
            "modzy_url": os.getenv("MODZY_BASE_URL")
        }        
        out = test_create_model(client, logger, model)
        TEST_RESULTS.append(out)
        out = test_create_model_with_batch(client, logger, model)    
        TEST_RESULTS.append(out)
        out = test_local_test(client, logger, model)
        TEST_RESULTS.append(out)
        out = test_local_batch_test(client, logger, model)
        TEST_RESULTS.append(out)
        out = test_env_test(client, logger, model)
        TEST_RESULTS.append(out)
        out = test_env_test_manual_env_config(client, logger, model)
        TEST_RESULTS.append(out)
        out = test_save(client, logger, model, UTILS_PATH)               
        TEST_RESULTS.append(out)
        out = test_save_manual_env_config(client, logger, model, UTILS_PATH)               
        TEST_RESULTS.append(out)
        out = test_save_gpu(client, logger, model, UTILS_PATH)               
        TEST_RESULTS.append(out)
        out = test_save_arm(client, logger, model, UTILS_PATH)                 
        TEST_RESULTS.append(out)
        out = test_save_gpu_and_arm(client, logger, model, UTILS_PATH) 
        TEST_RESULTS.append(out)
        # regular publish
        out, job = test_publish(client, logger, model, docker_creds)
        TEST_RESULTS.append(out)
        out = test_get_job_status(client, logger, job)
        TEST_RESULTS.append(out)
        out = test_block_until_complete(client, logger, job)
        TEST_RESULTS.append(out)
        out, path = test_download_tar(client, logger, job, UTILS_PATH)
        TEST_RESULTS.append(out)
        out = test_omi_compliance(client, logger, path)
        TEST_RESULTS.append(out)
        # publish with deployment to Modzy
        out, job = test_publish_modzy_deploy(client, logger, model, docker_creds, modzy_creds)
        TEST_RESULTS.append(out)
        out = test_get_job_status(client, logger, job)
        TEST_RESULTS.append(out)
        out = test_block_until_complete(client, logger, job)
        TEST_RESULTS.append(out)
        out, path = test_download_tar(client, logger, job, UTILS_PATH)
        TEST_RESULTS.append(out)
        out = test_omi_compliance(client, logger, path)
        TEST_RESULTS.append(out)
        # publish with manual env config
        out, job = test_publish_manual_env_config(client, logger, model, docker_creds)
        TEST_RESULTS.append(out)
        out = test_get_job_status(client, logger, job)
        TEST_RESULTS.append(out)
        out = test_block_until_complete(client, logger, job)
        TEST_RESULTS.append(out)
        out, path = test_download_tar(client, logger, job, UTILS_PATH)
        TEST_RESULTS.append(out)
        out = test_omi_compliance(client, logger, path)
        TEST_RESULTS.append(out)   
        # publish with GPU
        out, job = test_publish_gpu(client, logger, model, docker_creds)
        TEST_RESULTS.append(out)
        out = test_get_job_status(client, logger, job)
        TEST_RESULTS.append(out)
        out = test_block_until_complete(client, logger, job)
        TEST_RESULTS.append(out)
        out, path = test_download_tar(client, logger, job, UTILS_PATH)
        TEST_RESULTS.append(out)
        out = test_omi_compliance(client, logger, path)
        TEST_RESULTS.append(out)  
        # publish with arm
        out, job = test_publish_arm(client, logger, model, docker_creds)
        TEST_RESULTS.append(out)
        out = test_get_job_status(client, logger, job)
        TEST_RESULTS.append(out)
        out = test_block_until_complete(client, logger, job)
        TEST_RESULTS.append(out)
        out, path = test_download_tar(client, logger, job, UTILS_PATH)
        TEST_RESULTS.append(out)
        out = test_omi_compliance(client, logger, path)
        TEST_RESULTS.append(out) 
        # publish with arm and GPU
        out, job = test_publish_gpu_and_arm(client, logger, model, docker_creds)
        TEST_RESULTS.append(out)
        out = test_get_job_status(client, logger, job)
        TEST_RESULTS.append(out)
        out = test_block_until_complete(client, logger, job)
        TEST_RESULTS.append(out)
        out, path = test_download_tar(client, logger, job, UTILS_PATH)
        TEST_RESULTS.append(out)
        out = test_omi_compliance(client, logger, path)
        TEST_RESULTS.append(out)                                                       

        logger.info("--------------------- SUMMARY for Model {} ---------------------".format(model["model_name"]))
        logger.info("{} PASSED, {} FAILED".format(sum(TEST_RESULTS), len(TEST_RESULTS) - sum(TEST_RESULTS)))   
        ALL_TEST_RESULTS[model["short"]] = {
            "passed": sum(TEST_RESULTS),
            "failed": len(TEST_RESULTS) - sum(TEST_RESULTS)
        }


    print("\n")
    logger.info("--------------------- SUMMARY for All Models ---------------------")
    for result in ALL_TEST_RESULTS:
        logger.info("{} ---- {} PASSED, {} FAILED".format(result, ALL_TEST_RESULTS[result]["passed"], ALL_TEST_RESULTS[result]["failed"]))                
    

    
