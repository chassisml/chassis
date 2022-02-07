import os
import yaml
import json
import zipfile
import numpy as np
from chassisml import __version__
from packaging import version

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
        'timeout': {'status': '60s', 'run': '60s'},
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
