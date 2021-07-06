#!/usr/bin/env python
# -*- coding utf-8 -*-

import os
import json
import requests
import urllib.parse
import zipfile
import tempfile
import shutil
from enum import Enum
from packaging import version

MODEL_ZIP_NAME = 'model.zip'

routes = {
    'build': '/build',
    'job': '/job',
}

requests_session = requests.Session()


class Constants(Enum):
    IMAGE_GREY = 'grey'
    IMAGE_COLOR = 'color'


class ChassisML:
    """The ChassisML object.

    This class is used to interact with the Kaniko service.

    Attributes:
        base_url (str): The base url for the API.
        tar_path (str): The path to the generated tar in the Kaniko service.
        model_data (json): Object that contains all the container data.
    """

    def __init__(self):
        self.base_url = 'http://localhost:5000'
        self.headers = None
        self.deploy = False

    def _zipdir(self, model_directory):
        tmppath = tempfile.mkdtemp()

        # Compress all files in model directory to send them as a zip.
        with zipfile.ZipFile(f'{tmppath}/{MODEL_ZIP_NAME}', 'w', zipfile.ZIP_DEFLATED) as ziph:
            for root, dirs, files in os.walk(model_directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    ziph.write(file_path, file_path[len(model_directory):])

        return tmppath

    def get_module_data(self, module):
        # The value of each element points out the minimum required version.
        module_name = None
        module_version = None

        try:
            module_name = module.__name__
            module_version = module.__version__
        except AttributeError:
            pass

        return {'module_name': module_name, 'module_version': module_version}

    def publish(self, api_key, module, image_data, deploy, input_example_path, metadata, image_type, base_url):
        self.base_url = base_url if base_url else self.base_url
        self.deploy = deploy

        module_data = self.get_module_data(module)

        image_data = {**image_data, **module_data}
        image_data['deploy'] = deploy
        image_data['image_type'] = image_type.value if image_type else ''

        tmp_zip_dir = self._zipdir(image_data.get('model_path'))

        files = [
            ('image_data', json.dumps(image_data)),
            ('model', open(f'{tmp_zip_dir}/{MODEL_ZIP_NAME}', 'rb')),
        ]

        # XXX
        #  if deploy:
        #      files.append(('input_file', open(input_example_path, 'rb')))
        #      files.append(('metadata', json.dumps(metadata)))

        self.headers = {'Authorization': f'ApiKey {api_key}'}
        route = urllib.parse.urljoin(self.base_url, routes['build'])

        print('Publishing container... ', end='', flush=True)
        res = requests.post(route, files=files, headers=self.headers)
        res.raise_for_status()
        print('Ok!')

        # Remove the zip so it's no longer needed.
        shutil.rmtree(tmp_zip_dir)

        return res.json()

    def get_job_status(self, job_id, api_key):
        route = f'{urllib.parse.urljoin(self.base_url, routes["job"])}/{job_id}'

        if api_key:
            self.headers = {'Authorization': f'ApiKey {api_key}'}

        res = requests.get(route, headers=self.headers)
        res.raise_for_status()

        data = res.json()

        if not data['status']['succeeded']:
            print('Not finished yet. Try again later')
            return

        result = data.get('result') or {}
        container_url = result.get('container_url')

        #  if not self.deploy:
        #      print(f'Draft model: {container_url}')
        #      inputs_outputs_help = '\nPlease, go to the Draft model url and fill in the missing values through the UI.\n' \
        #      + '\nFor every input there must be one output of type json. The "Output Name" of every output must be ' \
        #      + 'the same as the "Model Input Filename" of the referenced input but the extension ".json" must be added (even if it\'s already a json).\n' \
        #      + 'E.g.: if the "Model Input Filename" of one input is "digit.jpg", ' \
        #      + 'the "Output Name" of its corresponding output should be "digit.jpg.json".\n' \
        #      + 'Job input names must match model input filenames.'
        #      print(inputs_outputs_help)
        #  else:
        #      print(f'Deployed model: {container_url}')

        return data or {}

    def download_tar(self, job_id, output_filename, api_key):
        url = f'{urllib.parse.urljoin(self.base_url, routes["job"])}/{job_id}/download-tar'
        r = requests.get(url)

        if r.status_code == 200:
            with open(output_filename, 'wb') as f:
                f.write(r.content)
        else:
            print(f'Error download tar: {r.text}')


# ChassisML instance that is used in the SDK.
_defaultChassisML = ChassisML()

def publish(api_key, module, image_data, deploy=False, input_example_path=None, metadata=None, image_type=None, base_url=None):
    """Uploads the tarball to ChassisML API to create a model.

    If `deploy` is False it just prints the draft Url once the tarball has been uploaded.
    Example of image_data:
    ```
    {
        'name': 'test-sklearn',
        'version': '0.0.1',
        'model_name': 'digits',
        'model_path': '../../builder_service/test/sklearn/example_model',
    }
    ```
    Example of metadata when `deploy` is True:
    ```
    {
        'inputs': [{'name': 'digit.jpg', 'description': 'description input', 'acceptedMediaTypes': 'image/jpeg', 'maximumSize': int(1.024e6)}],
        'outputs': [{'name': 'digit.jpg.json', 'description': 'description output', 'mediaType': 'application/json', 'maximumSize': int(1.024e6)}],
    }
    ```
    Example of complete values when `deploy` is True:
    ```
    {
        'inputs': [{'name': 'digit.jpg', 'description': 'description input', 'acceptedMediaTypes': 'image/jpeg', 'maximumSize': int(1.024e6)}],
        'outputs': [{'name': 'digit.jpg.json', 'description': 'description output', 'mediaType': 'application/json', 'maximumSize': int(1.024e6)}],
        'description': 'Example of short description.',
        'longDescription': 'Example of long description.',
        'performanceSummary': 'Example of performance summary.',
        'requirement': {
          'cpuAmount': '1000m',
          'gpuUnits': 0,
          'memoryAmount': '512Mi'
        },
        'technicalDetails': 'Example of technical details.',
        'timeout': {
          'run': 30000,
          'status': 30000
        },
        'tags': [{'name': 'Label or Classify'}, {'name': 'Language and Text'}, {'name': 'Image'}],
        'versionHistory': 'Example of version history.'
    }
    ```

    Args:
        module (object): Module used to build the model.
        image_data (json): Required data to build and deploy the model.
        deploy (bool): Whether the model should be deployed or fixed as draft.
        input_example_path (str): Path to the input file that will be used as example during deployment. Only required if deploy==True.
        metadata (json): Required data when deploying the model. Only required if deploy==True.
        image_type (str): It defines the type of image (in case of using images). It can be chassisML.Constants.{IMAGE_GREY ,IMAGE_COLOR}
        base_url (str): Default base_url is localhost:5000.
    """
    return _defaultChassisML.publish(api_key, module, image_data, deploy, input_example_path, metadata, image_type, base_url)

def get_job_status(job_id, api_key=None):
    """Returns the data once the model has been deployed.
    """
    return _defaultChassisML.get_job_status(job_id, api_key)

def download_tar(job_id, output_filename, api_key=None):
    """Returns the data once the model has been deployed.
    """
    return _defaultChassisML.download_tar(job_id, output_filename, api_key)
