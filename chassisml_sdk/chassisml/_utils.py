import os
import yaml
import json
import zipfile
import numpy as np
from chassisml import __version__
from packaging import version
import validators
import docker
import time
import secrets
from .grpc_model.src import model_client

DEFAULT_MODZY_YAML_DATA = {'specification': '0.4',
        'type': 'grpc',
        'source': None,
        'version': None,
        'name': None,
        'author': 'Chassis',
        'description': {'summary': 'Chassis model.',
        'details': 'Chassis model.',
        'technical': 'Chassis model.',
        'performance': None},
        'releaseNotes': None,
        'tags': [None],
        'filters': [{'type': None, 'label': None}, {'type': None, 'label': None}],
        'metrics': [{'label': None,
        'type': None,
        'value': None,
        'description': None}],
        'inputs': {'input': {'acceptedMediaTypes': ['application/json'],
        'maxSize': '5M',
        'description': 'Input file.'}},
        'outputs': {'results.json': {'mediaType': 'application/json',
        'maxSize': '1M',
        'description': 'Output file.'}},
        'requirement': {'requirementId': -3},
        'resources': {'memory': {'size': None},
        'cpu': {'count': None},
        'gpu': {'count': None}},
        'timeout': {'status': '60s', 'run': '300s'},
        'internal': {'recommended': None, 'experimental': None, 'available': None},
        'features': {'explainable': False, 'adversarialDefense': False}
    }

ARM_GPU_REMOVE = {'torch','tensorflow','mxnet','scikit-learn','onnx','pandas','scipy','numpy','scikit-learn','opencv'}

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj,np.float32) or isinstance(obj,np.float64):
            return float(obj)
        if isinstance(obj,np.int32) or isinstance(obj,np.int64):
            return int(obj)
        return json.JSONEncoder.default(self, obj)

def zipdir(model_directory,tmppath,model_zip_name):
    # Compress all files in model directory to send them as a zip.
    with zipfile.ZipFile(f'{tmppath}/{model_zip_name}', 'w', zipfile.ZIP_DEFLATED) as ziph:
        for root, dirs, files in os.walk(model_directory):
            for file in files:
                file_path = os.path.join(root, file)
                ziph.write(file_path, file_path[len(model_directory):])

def fix_dependencies(model_directory):
    conda_path = os.path.join(model_directory,"conda.yaml")
    pip_path = os.path.join(model_directory,"requirements.txt")

    with open(conda_path) as conda_r, open(pip_path) as pip_r:

        conda_lines = conda_r.readlines()
        pip_lines = pip_r.readlines()

        new_conda = ""
        new_pip = ""
        opencv_found = False
        for line in conda_lines:
            if "opencv-python" in line:
                if opencv_found:
                    continue
                else:
                    new_conda += line.replace("opencv-python=","opencv-python-headless=")
                    opencv_found = True
            else:
                    new_conda += line

        opencv_found = False
        for line in pip_lines:
            if "opencv-python" in line:
                if opencv_found:
                    continue
                else:
                    new_pip += line.replace("opencv-python=","opencv-python-headless=")
                    opencv_found = True
            else:
                    new_pip += line
        
    with open(conda_path,"w") as conda_w, open(pip_path,"w") as pip_w:
        conda_w.write(new_conda)
        pip_w.write(new_pip)

def fix_dependencies_arm_gpu(model_directory):
    conda_path = os.path.join(model_directory,"conda.yaml")
    pip_path = os.path.join(model_directory,"requirements.txt")

    if version.parse(yaml.safe_load(open(conda_path))['dependencies'][0].split('=')[1])>=version.parse('3.7'):
        print(yaml.safe_load(open(conda_path))['dependencies'][0].split('=')[1])
        raise ValueError('For GPU ARM support, Python version must be < 3.7')
    
    with open(conda_path) as conda_r, open(pip_path) as pip_r:
        conda_lines = conda_r.read().splitlines()
        pip_lines = pip_r.read().splitlines()
    
    with open(conda_path,"w") as conda_w, open(pip_path,"w") as pip_w:
        for line in conda_lines:
            if not any(package in line for package in ARM_GPU_REMOVE):
                conda_w.write(line)
                conda_w.write('\n')
        for line in pip_lines:
            if not any(package in line for package in ARM_GPU_REMOVE):
                pip_w.write(line)
                pip_w.write('\n')

def write_modzy_yaml(model_name,model_version,output_path,batch_size=None,gpu=False):
    yaml_data = DEFAULT_MODZY_YAML_DATA
    yaml_data['name'] = model_name
    yaml_data['version'] = model_version
    if batch_size:
        yaml_data['features']['maxBatchSize'] = batch_size
    if gpu:
        yaml_data['resources']['gpu']['count'] = 1
    with open(output_path,'w',encoding = "utf-8") as f:
        f.write(yaml.dump(yaml_data))

def check_modzy_url(modzy_url):
    if not validators.url(modzy_url):
        raise ValueError("Provided Modzy URL is not a valid URL")
    if not modzy_url.startswith('https://'):
        raise ValueError("Modzy URL must start with 'https://', example: 'https://my.modzy.com'")
    if not modzy_url[-1].isalpha():
        raise ValueError("Modzy URL must end with alpha char, example: 'https://my.modzy.com'")
    return True

def run_inference(input_data,container_url="localhost",host_port=45000):
    '''
    This is the method you use to submit data to a container chassis has built for inference.
    it assumes the container has been downloaded from dockerhub and is running somewhere you have access to

    Args:
        input_data (json): dictionary of the form {"input": <binary respresentaion of your data>}
        container_url (str): URL where container is running
        host_port (int): host port that forwards to container's grpc server port

    Returns:
        return_value (str): Success -> results from model processing as specified in the process function.
                            Failure -> Error codes from processing errors. All errors should container the word "Error."

    Examples:
        ```python
        # assume that the container is running locally, and that it was started with this docker command
        #  docker run -it -p 5001:45000 <docker_uname>/<container_name>:<tag_id>

        from chassisml_sdk.chassisml import chassisml

        client = chassisml.ChassisClient()

        input_data = {"input": b"[[0.0, 0.0, 0.0, 1.0, 12.0, 6.0, 0.0, 0.0, 0.0, 0.0, 0.0, 11.0, 15.0, 2.0, 0.0, 0.0, 0.0, 0.0, 8.0, 16.0, 6.0, 1.0, 2.0, 0.0, 0.0, 4.0, 16.0, 9.0, 1.0, 15.0, 9.0, 0.0, 0.0, 13.0, 15.0, 6.0, 10.0, 16.0, 6.0, 0.0, 0.0, 12.0, 16.0, 16.0, 16.0, 16.0, 1.0, 0.0, 0.0, 1.0, 7.0, 4.0, 14.0, 13.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 14.0, 9.0, 0.0, 0.0], [0.0, 0.0, 8.0, 16.0, 3.0, 0.0, 1.0, 0.0, 0.0, 0.0, 16.0, 14.0, 5.0, 14.0, 12.0, 0.0, 0.0, 0.0, 8.0, 16.0, 16.0, 9.0, 0.0, 0.0, 0.0, 0.0, 3.0, 16.0, 14.0, 1.0, 0.0, 0.0, 0.0, 0.0, 12.0, 16.0, 16.0, 2.0, 0.0, 0.0, 0.0, 0.0, 16.0, 11.0, 16.0, 4.0, 0.0, 0.0, 0.0, 3.0, 16.0, 16.0, 16.0, 6.0, 0.0, 0.0, 0.0, 0.0, 10.0, 16.0, 10.0, 1.0, 0.0, 0.0], [0.0, 0.0, 5.0, 12.0, 8.0, 0.0, 1.0, 0.0, 0.0, 0.0, 11.0, 16.0, 5.0, 13.0, 6.0, 0.0, 0.0, 0.0, 2.0, 15.0, 16.0, 12.0, 1.0, 0.0, 0.0, 0.0, 0.0, 10.0, 16.0, 6.0, 0.0, 0.0, 0.0, 0.0, 1.0, 15.0, 16.0, 7.0, 0.0, 0.0, 0.0, 0.0, 8.0, 16.0, 16.0, 11.0, 0.0, 0.0, 0.0, 0.0, 11.0, 16.0, 16.0, 9.0, 0.0, 0.0, 0.0, 0.0, 6.0, 12.0, 12.0, 3.0, 0.0, 0.0], [0.0, 0.0, 0.0, 3.0, 15.0, 4.0, 0.0, 0.0, 0.0, 0.0, 4.0, 16.0, 12.0, 0.0, 0.0, 0.0, 0.0, 0.0, 12.0, 15.0, 3.0, 4.0, 3.0, 0.0, 0.0, 7.0, 16.0, 5.0, 3.0, 15.0, 8.0, 0.0, 0.0, 13.0, 16.0, 13.0, 15.0, 16.0, 2.0, 0.0, 0.0, 12.0, 16.0, 16.0, 16.0, 13.0, 0.0, 0.0, 0.0, 0.0, 4.0, 5.0, 16.0, 8.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 16.0, 4.0, 0.0, 0.0], [0.0, 0.0, 10.0, 14.0, 8.0, 1.0, 0.0, 0.0, 0.0, 2.0, 16.0, 14.0, 6.0, 1.0, 0.0, 0.0, 0.0, 0.0, 15.0, 15.0, 8.0, 15.0, 0.0, 0.0, 0.0, 0.0, 5.0, 16.0, 16.0, 10.0, 0.0, 0.0, 0.0, 0.0, 12.0, 15.0, 15.0, 12.0, 0.0, 0.0, 0.0, 4.0, 16.0, 6.0, 4.0, 16.0, 6.0, 0.0, 0.0, 8.0, 16.0, 10.0, 8.0, 16.0, 8.0, 0.0, 0.0, 1.0, 8.0, 12.0, 14.0, 12.0, 1.0, 0.0]]"}
        input_list = [input_data for _ in range(30)]

        print("single input")
        print(client.run_inference(input_data, container_url="localhost", host_port=5001))
        print("multi inputs")
        results = client.run_inference(input_list, container_url="localhost", host_port=5001)
        for x in results:
            print(x)
    '''
    model_client.override_server_URL(container_url, host_port)
    return model_client.run(input_data)

def docker_start(image_id,host_port = 5001,container_port=None,timeout=20,pull_container=False):
    '''
    Creates and starts a container for model inference.

    Args:
        image_id (string): the name of an OMI container image usually of the form <docker_uname>/<container_name>:<tag_id>
        host_port (int): host port that forwards to container's grpc server port
        container_port (str): container port the grpc server listens to
        timeout (int): number of seconds to wait for gRPC server to spin up

    Returns:
        return_value (str):    Success -> "Id" of container that was started.
                                Failure -> message if any success criteria is missing.

    '''

    return_value = "Failure: container didn't start"
    client = docker.APIClient()

    #check for image and pull if flag is set
    if pull_container and  len([x for x in client.images() if
                x["RepoTags"] != None and image_id in x["RepoTags"]]) == 0:
        try:
            print("Pulling container " + image_id + " from registry. \n This may take a few minutes depending on the size of your image")
            client.pull(image_id)
        except Exception as e:
            print("Unable to pull container. Is this the correct registry id? "+ image_id)
            raise ValueError(image_id + " failed to pull from repo. aborting processing")

    #use OMI port by default
    if not container_port:
        container_port = int(client.inspect_image(image_id)['Config']['Labels']['ml.openmodel.port'])

    try:

        #get current container list
        containers = client.containers(filters={"status": "running", "ancestor": image_id})
        container_id = None

        if len(containers) == 0:

            container = client.create_container(
            image=image_id,
            name="chassis_inference_container"+secrets.token_hex(nbytes=4),
            ports=[container_port],
            host_config=client.create_host_config(port_bindings={
                container_port: host_port
            })
            )
            container_id=container.get('Id')
            client.start(container=container_id)
        else:
            container_id = containers[0]['Id']

        grpc_started = False
        for _ in range(timeout):
            log_entry = "".join([chr(x) for x in client.logs(container=container_id)])
            if "gRPC Server running" in log_entry:
                grpc_started = True
                break
            time.sleep(1)

        if grpc_started is False:
            raise TimeoutError("server failed to start within timeout limit of " + str(timeout) + "seconds")

        return_value = container_id

    except Exception as e:

        print("Error: Container failed to start with Docker client call\n" + print(e))

    return return_value

def docker_clean_up(container_id):
    '''
    stops a container and removes it from the system.

    Args:
    container_id (str): Id of the container to stop and remove

    Returns:
    str:    Success message if the container is successfully stopped and removed.
            Failure message if any success criteria is missing.

    '''
    client = docker.APIClient()

    Err_str = "Failure: Docker clean up failed."\
                    "\n Check to make sure containers have been removed from your system." \
                    "\n If they are on your system still, they will be named chassis_inference_container." \
                    "\n Manually remove them if they still exist with 'docker rm'."
    return_value = False
    partial_success = False
    try:
        # containers only shows running containers by default so this grab the container for us to stop it.
        if len(client.containers(filters={"id":container_id})) > 0:
            client.stop(container=container_id)
        partial_success=True
    except Exception as e:
        return_value += "\n Error Message: " + str(e)
        print("Error: there was a problem stopping the chassis_inference_container. \n if you are sure it is running, you should manually stop it.\n"+ str(e) +"\n" + Err_str)

    try:
        # we stop the container regardless of its state as it is not intended for use outside the OMI check.
        client.remove_container(container=container_id, force=True)
        if partial_success:
            return_value = True
    except Exception as e:
        return_value += "\n Error Message: " + str(e)
        print("Error: problem removing the chassis_inference_container. \n if you are sure it is on the system, you should remove it manually.\n" + str(e) +"\n"+ Err_str)

    return return_value