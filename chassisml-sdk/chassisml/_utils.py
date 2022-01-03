import os
import yaml
import json
import zipfile
import numpy as np

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
        conda = conda_r.read().replace("opencv-python=","opencv-python-headless=")
        pip = pip_r.read().replace("opencv-python=","opencv-python-headless=")
    
    with open(conda_path,"w") as conda_w, open(pip_path,"w") as pip_w:
        conda_w.write(conda)
        pip_w.write(pip)

def write_modzy_yaml(model_name,model_version,output_path):
    yaml_data = DEFAULT_MODZY_YAML_DATA
    yaml_data['name'] = model_name
    yaml_data['version'] = model_version
    with open(output_path,'w',encoding = "utf-8") as f:
        f.write(yaml.dump(yaml_data))