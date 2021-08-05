#!/usr/bin/env python
# -*- coding utf-8 -*-

import os
import time
import json
import yaml
import requests
import urllib.parse
from loguru import logger
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from kubernetes import client, config

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--api_key', type=str, required=False)
parser.add_argument('--deploy', type=bool, required=False)
parser.add_argument('--image_tag', type=str, required=False)
parser.add_argument('--sample_input_path', type=str, required=False)
parser.add_argument('--metadata_path', type=str, required=False)
args = parser.parse_args()

JOB_NAME = os.getenv('JOB_NAME')
ENVIRONMENT = os.getenv('ENVIRONMENT')
MODZY_BASE_URL = 'https://integration.modzy.engineering'

r_session = requests.Session()

routes = {
    'create_model': '/api/models',
    'add_image': '/api/models/{}/versions/{}/container-image',
    'add_data': '/api/models/{}',
    'add_metadata': '/api/models/{}/versions/{}',
    'load_model': '/api/models/{}/versions/{}/load-process',
    'upload_input_example': '/api/models/{}/versions/{}/testInput',
    'run_model': '/api/models/{}/versions/{}/run-process',
    'deploy_model': '/api/models/{}/versions/{}',
    'model_url': '/models/{}/{}',
}

def format_url(route, *args):
    return urllib.parse.urljoin(MODZY_BASE_URL, route).format(*args)

def create_model(metadata):
    '''https://v2ui.dev.modzy.engineering/docs/deployment/models/create-model'''

    start = time.time()

    route = format_url(routes['create_model'])

    name, version = metadata.get('name'), metadata.get('version')
    data = {'name': name, 'version': version}

    res = r_session.post(route, json=data)
    res.raise_for_status()

    logger.info(f'create_model returned took [{1000*(time.time()-start)} ms]')

    return res.json()

def add_tags_and_description(identifier, metadata):
    '''https://v2ui.dev.modzy.engineering/docs/deployment/models/update-model'''

    start = time.time()

    route = format_url(routes['add_data'], identifier)

    tags_and_description = {
        'description': metadata.get('description').get('summary') or ''
    }

    # By default tags is empty so only use it in case some are defined.
    tags = metadata.get('tags')
    if tags[0] is not None:
        tags_and_description['tags'] = tags

    res = r_session.patch(route, json=tags_and_description)
    res.raise_for_status()

    logger.info(f'add_tags_and_description took [{1000*(time.time()-start)} ms]')

def add_container_image(identifier, version, image_tag):
    '''https://v2ui.dev.modzy.engineering/docs/deployment/container-image/add-container-image'''

    start = time.time()

    route = format_url(routes['add_image'], identifier, version)

    username, image_name = image_tag.split('/')
    image_name, manifest = f'{image_name}{":latest" if ":" not in image_name else ""}'.split(':')

    # Assuming it's uploaded to Docker hub.
    url = f'https://registry.hub.docker.com/v2/{username}/{image_name}/manifests/{manifest}'
    registry = {'registry': {'url': url}}

    # Timeout to None since the remote testing server is very slow.
    res = r_session.post(route, json=registry, timeout=None)
    res.raise_for_status()

    logger.info(f'add_container_image took [{1000*(time.time()-start)} ms]')

def _format_metadata(metadata):
    body = {}

    for key in 'inputValidationSchema timeout requirement statistics processing versionHistory'.split():
        if key in metadata:
            body[key] = metadata[key]

    long_description = metadata.get('description').get('details')
    if long_description:
        body['longDescription'] = long_description
    technical_details = metadata.get('description').get('technical')
    if technical_details:
        body['technicalDetails'] = technical_details
    performance_summary = metadata.get('description').get('performance')
    if performance_summary:
        body['performanceSummary'] = performance_summary
    inputs = metadata.get('inputs')
    if inputs:
        inputs_array = []
        for input_key in inputs.keys():
            inputs_array.append({
                'name': input_key,
                'acceptedMediaTypes': ','.join(inputs[input_key].get('acceptedMediaTypes')),
                'maximumSize': inputs[input_key].get('maxSize'),
                'description': inputs[input_key].get('description'),
            })
        body['inputs'] = inputs_array
    outputs = metadata.get('outputs')
    if outputs:
        outputs_array = []
        for output_key in outputs.keys():
            outputs_array.append({
                'name': output_key,
                'mediaType': outputs[output_key].get('mediaType'),
                'maximumSize': outputs[output_key].get('maxSize'),
                'description': outputs[output_key].get('description'),
            })
        body['outputs'] = outputs_array

    return body

def add_metadata(identifier, version, metadata):
    '''https://v2ui.dev.modzy.engineering/docs/deployment/metadata/metadata'''

    start = time.time()

    route = format_url(routes['add_metadata'], identifier, version)

    body = _format_metadata(metadata)

    res = r_session.patch(route, json=body)
    res.raise_for_status()

    logger.info(f'add_metadata took [{1000*(time.time()-start)} ms]')

    return res.json()

def load_model(identifier, version):
    '''https://v2ui.dev.modzy.engineering/docs/deployment/tests/load-model'''

    start = time.time()

    route = format_url(routes['add_image'], identifier, version)

    # Before loading the model we need to ensure that it has been pulled.
    percentage = -1
    while percentage < 100:
        res = r_session.get(route)

        res_data = res.json()
        new_percentage = res_data.get('percentage')

        if new_percentage != percentage:
            logger.debug(f'Loading model at {new_percentage}%')
            percentage = new_percentage

        time.sleep(1)

    route = format_url(routes['load_model'], identifier, version)

    retry_strategy = Retry(
        total=10,
        backoff_factor=0.3,
        status_forcelist=[400],
        allowed_methods=frozenset(['POST']),
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = r_session
    http.mount('https://', adapter)

    res = http.post(route)

    logger.info(f'load_model took [{1000*(time.time()-start)} ms]')

def upload_input_example(identifier, version, model_data_metadata, input_sample_path):
    '''https://v2ui.dev.modzy.engineering/docs/deployment/inputs-test-file/add-test-input'''
    start = time.time()

    route = format_url(routes['upload_input_example'], identifier, version)

    input_filename = model_data_metadata['inputs'][0]['name']
    files = {'file': open(input_sample_path, 'rb')}
    params = {'name': input_filename}

    res = r_session.post(route, params=params, files=files)
    res.raise_for_status()

    logger.info(f'upload_input_example took [{1000*(time.time()-start)} ms]')

def run_model(identifier, version):
    '''https://v2ui.dev.modzy.engineering/docs/deployment/tests/run-model'''

    start = time.time()

    route = format_url(routes['run_model'], identifier, version)

    res = r_session.post(route)
    res.raise_for_status()

    logger.info(f'run_model took [{1000*(time.time()-start)} ms]')

def deploy_model(identifier, version):
    '''https://v2ui.dev.modzy.engineering/docs/deployment/models/deploy-model-version'''

    start = time.time()

    route = format_url(routes['deploy_model'], identifier, version)

    status = {'status': 'active'}

    res = r_session.patch(route, json=status)
    res.raise_for_status()

    logger.info(f'deploy_model took [{1000*(time.time()-start)} ms]')

def upload_model():
    input_sample_path = args.sample_input_path

    with open(args.metadata_path, 'r') as f:
        metadata = yaml.safe_load(f)

    model_data = create_model(metadata)

    identifier, version = model_data.get('identifier'), metadata.get('version')

    logger.debug(f'Identifier: {identifier}, Version: {version}')

    add_tags_and_description(identifier, metadata)

    add_container_image(identifier, version, args.image_tag)

    model_data = add_metadata(identifier, version, metadata)

    logger.debug(f'Model metadata: {model_data}')

    load_model(identifier, version)

    upload_input_example(identifier, version, model_data, input_sample_path)

    run_model(identifier, version)

    deploy_model(identifier, version)

    container_data = {
        **model_data,
        'container_url': format_url(routes['model_url'], identifier, version)
    }

    return container_data

def update_headers():
    api_key = args.api_key
    r_session.headers.update({'Authorization': f'ApiKey {api_key}'})

def update_job_with_result(api_instance, result):
    job = api_instance.read_namespaced_job(JOB_NAME, ENVIRONMENT)
    job.metadata.annotations = {'result': json.dumps(result)}

    api_instance.patch_namespaced_job(JOB_NAME, ENVIRONMENT, job)

def main():
    # Only deploy to Modzy if user wants to.
    if not args.deploy:
        return

    config.load_incluster_config()
    batch_v1 = client.BatchV1Api()

    update_headers()

    try:
        result = upload_model()
    except Exception as e:
        logger.error(f'Error: {str(e)}')
        result = {'error': str(e)}

    update_job_with_result(batch_v1, result)


if __name__ == '__main__':
    main()
