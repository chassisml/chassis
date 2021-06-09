#!/usr/bin/env python
# -*- coding utf-8 -*-

import os
import time
import json
import requests
import urllib.parse
from loguru import logger
from shutil import copyfile, rmtree
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from kubernetes import client, config, watch

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--tar_path', type=str, required=True)
parser.add_argument('--model_dir', type=str, required=True)
parser.add_argument('--input_filename', type=str, required=True)
parser.add_argument('--metadata', type=str, required=True)
parser.add_argument('--deploy', type=bool, required=True)
args = parser.parse_args()

JOB_NAME = os.getenv('JOB_NAME')
ENVIRONMENT = os.getenv('ENVIRONMENT')
MODZY_BASE_URL = 'https://master.dev.modzy.engineering'

headers = {'Authorization': os.getenv('API_KEY')}

routes = {
    'details': '/api/accounting/access-keys/{}',
    'create_model': '/api/models',
    'add_image': '/api/models/{}/versions/{}/container-image',
    'add_data': '/api/models/{}',
    'add_metadata': '/api/models/{}/versions/{}',
    'load_model': '/api/models/{}/versions/{}/load-process',
    'upload_input_example': '/api/models/{}/versions/{}/testInput',
    'run_model': '/api/models/{}/versions/{}/run-process',
    'deploy_model': '/api/models/{}/versions/{}',
    'model_draft': '/launchpad/hardware-requirements/{}/{}',
    'model_url': '/models/{}/{}',
}

default_values = {
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


def format_url(route, *args):
    return urllib.parse.urljoin(MODZY_BASE_URL, route).format(*args)

def create_model(metadata):
    start = time.time()

    route = format_url(routes['create_model'])

    name, version = metadata.get('name'), metadata.get('version')
    data = {'name': name, 'version': version}

    res = requests.post(route, json=data, headers=headers)
    res.raise_for_status()

    logger.info(f'create_model returned took [{1000*(time.time()-start)} ms]')

    return res.json()

def add_container_image(identifier, version, data, tar_path):
    start = time.time()

    route = format_url(routes['add_image'], identifier, version)

    # Timeout to None since the remote testing server is very slow.
    res = requests.post(route, files=[('file', open(tar_path, 'rb'))], headers=headers, timeout=None)
    res.raise_for_status()

    # XXX
    #  os.remove(tar_path)

    logger.info(f'add_container_image took [{1000*(time.time()-start)} ms]')

def add_tags_and_description(identifier, body, data):
    start = time.time()

    tags_and_description = {'tags': body.get('tags'), 'description': body.get('description')}

    identifier = data.get('identifier')
    route = format_url(routes['add_data'], identifier)

    res = requests.patch(route, json=tags_and_description, headers=headers)
    res.raise_for_status()

    logger.info(f'add_tags_and_description took [{1000*(time.time()-start)} ms]')

def add_metadata(identifier, version, body, data):
    start = time.time()

    route = format_url(routes['add_metadata'], identifier, version)

    res = requests.patch(route, json=body, headers=headers)
    res.raise_for_status()

    logger.info(f'add_metadata took [{1000*(time.time()-start)} ms]')

    return res.json()

def load_model(identifier, version, data):
    start = time.time()

    route = format_url(routes['load_model'], identifier, version)

    retry_strategy = Retry(
        total=10,
        backoff_factor=10,
        status_forcelist=[400],
        allowed_methods=frozenset(['POST']),
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount('https://', adapter)

    res = http.post(route, headers=headers)

    logger.info(f'load_model took [{1000*(time.time()-start)} ms]')

def upload_input_example(identifier, version, data, input_filename, input_file_path):
    start = time.time()

    files = {'file': (input_filename, open(input_file_path, 'rb'))}
    params = {'name': data['inputs'][0]['name']}
    route = format_url(routes['upload_input_example'], identifier, version)

    res = requests.post(route, params=params, files=files, headers=headers)
    res.raise_for_status()

    logger.info(f'upload_input_example took [{1000*(time.time()-start)} ms]')

def run_model(identifier, version, data):
    start = time.time()

    route = format_url(routes['run_model'], identifier, version)

    res = requests.post(route, headers=headers)
    res.raise_for_status()

    logger.info(f'run_model took [{1000*(time.time()-start)} ms]')

def deploy_model(identifier, version, data):
    start = time.time()

    route = format_url(routes['deploy_model'], identifier, version)

    status = {'status': 'active'}

    res = requests.patch(route, json=status, headers=headers)
    res.raise_for_status()

    logger.info(f'deploy_model took [{1000*(time.time()-start)} ms]')

def upload_model():
    metadata = json.loads(args.metadata)
    tar_path = args.tar_path
    deploy = args.deploy
    #  input_file = request.files.get('input_file')
    input_filename = args.input_filename
    model_dir = args.model_dir
    input_file_path = f'{model_dir}/{input_filename}'

    # Override default values with values sent in the request.
    metadata = {**default_values, **metadata}

    model_data = create_model(metadata)

    identifier, version = model_data.get('identifier'), metadata.get('version')

    add_container_image(identifier, version, model_data, tar_path)

    if not deploy:
        rmtree(model_dir)

        container_data = {
            'container_url': format_url(routes['model_draft'], identifier, version)
        }

        return container_data

    add_tags_and_description(identifier, metadata, model_data)

    model_data_metadata = add_metadata(identifier, version, metadata, model_data)

    model_data = {**model_data, **model_data_metadata}

    load_model(identifier, version, model_data)

    upload_input_example(identifier, version, model_data, input_filename, input_file_path)

    rmtree(model_dir)

    run_model(identifier, version, model_data)

    deploy_model(identifier, version, model_data)

    permalink = model_data.get('permalink')
    container_data = {
        **model_data,
        'container_url': format_url(routes['model_url'], permalink, version)
    }

    return container_data

def update_job_with_result(api_instance, result):
    job = api_instance.read_namespaced_job(JOB_NAME, ENVIRONMENT)
    job.metadata.annotations = { 'result': json.dumps(result) }

    api_instance.patch_namespaced_job(JOB_NAME, ENVIRONMENT, job)

def main():
    config.load_incluster_config()
    batch_v1 = client.BatchV1Api()

    result = upload_model()

    update_job_with_result(batch_v1, result)

if __name__ == '__main__':
    main()
