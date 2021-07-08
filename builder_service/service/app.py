import os
import json
import uuid
import tempfile
import zipfile
import urllib.parse
from shutil import rmtree, copytree
import requests
from loguru import logger
from flask import Flask, request, send_from_directory
from kubernetes import client, config

MOUNT_PATH_DIR = '/data'
WORKSPACE_DIR = f'{MOUNT_PATH_DIR}/workspace'
#  WORKSPACE_DIR = f'{MOUNT_PATH_DIR}'
KFSERVING_PORT = os.getenv('KFSERVING_PORT')
PROXY_PORT = os.getenv('PROXY_PORT')
ENVIRONMENT = os.getenv('ENVIRONMENT')

MODZY_BASE_URL = 'https://master.dev.modzy.engineering'
JOB_NAME = 'chassis-builder-job'

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

###########################################
def create_job_object(
    image_name,
    module_name,
    module_version,
    model_name,
    path_to_tar_file,
    random_name,
    deploy,
    registry_auth,
):
    job_name = f'{JOB_NAME}-{random_name}'

    # Configureate Pod template container
    volume_mount = client.V1VolumeMount(
        mount_path=MOUNT_PATH_DIR,
        name='kaniko-data'
    )
    volume_mount_empty_dir_init_container = client.V1VolumeMount(
        mount_path='/tmp/credentials',
        name='registry-credentials'
    )
    volume_mount_empty_dir_container = client.V1VolumeMount(
        mount_path='/kaniko/.docker',
        name='registry-credentials'
    )

    registry_credentials = f'{{\"auths\":{{\"https://index.docker.io/v1/\":{{\"auth\":\"{registry_auth}\"}}}}}}'

    init_container = client.V1Container(
        name='credentials',
        image='busybox',
        volume_mounts=[
            volume_mount_empty_dir_init_container
        ],
        # XXX: only compatible with Docker Hub at the moment.
        command=[
            '/bin/sh',
            '-c',
            f'echo "{registry_credentials}" > /tmp/credentials/config.json'
        ]
    )
    container = client.V1Container(
        name='kaniko',
        image='gcr.io/kaniko-project/executor:latest',
        volume_mounts=[
            volume_mount,
            volume_mount_empty_dir_container
        ],
        args=[
            f'--dockerfile={WORKSPACE_DIR}/flavours/{module_name}/Dockerfile',
            '' if deploy else '--no-push',
            #  '--insecure',
            #  '--skip-tls-verify',
            ##############################
            f'--tarPath={path_to_tar_file}',
            f'--destination={image_name}{"" if ":" in image_name else ":latest"}',
            f'--context={WORKSPACE_DIR}',
            f'--build-arg=MODEL_DIR=model-{random_name}',
            f'--build-arg=MODEL_NAME={model_name}',
            f'--build-arg=MODEL_CLASS={module_name}',
            f'--build-arg=KFSERVING_PORT={KFSERVING_PORT}',
            f'--build-arg=PROXY_PORT={PROXY_PORT}',
            f'--build-arg=MODULE_VERSION={module_version}',
        ]
    )
    pv_claim = client.V1PersistentVolumeClaimVolumeSource(
        claim_name='kaniko-data'
    )
    empty_dir_volume_source = client.V1EmptyDirVolumeSource()
    volume = client.V1Volume(
        name='kaniko-data',
        persistent_volume_claim=pv_claim
    )
    volume_empty_dir = client.V1Volume(
        name='registry-credentials',
        empty_dir=empty_dir_volume_source
    )
    pod_spec = client.V1PodSpec(
        service_account_name='job-builder',
        restart_policy='Never',
        init_containers=[init_container],
        containers=[container],
        volumes=[volume, volume_empty_dir]
    )
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(name=job_name),
        spec=pod_spec
    )
    spec = client.V1JobSpec(
        backoff_limit=0,
        template=template
    )
    job = client.V1Job(
        api_version='batch/v1',
        kind='Job',
        metadata=client.V1ObjectMeta(
            name=job_name,
        ),
        spec=spec
    )

    return job

def create_job(api_instance, job):
    api_response = api_instance.create_namespaced_job(
        body=job,
        namespace=ENVIRONMENT)
    logger.info(f'Pod created. Status={str(api_response.status)}')
###########################################

def format_url(route, *args):
    return urllib.parse.urljoin(MODZY_BASE_URL, route).format(*args)

def run_kaniko(
    image_name,
    module_name,
    module_version,
    model_name,
    path_to_tar_file,
    random_name,
    deploy,
    registry_auth,
):
    config.load_incluster_config()
    batch_v1 = client.BatchV1Api()

    try:
        job = create_job_object(
            image_name,
            module_name,
            module_version,
            model_name,
            path_to_tar_file,
            random_name,
            deploy,
            registry_auth,
        )
        create_job(batch_v1, job)
    except Exception as err:
        return str(err)

    return False

def unzip_model(model, module_name, random_name):
    tmp_dir = tempfile.mkdtemp()
    path_to_zip_file = f'{tmp_dir}/{model.filename}'
    zip_content_dst = f'{WORKSPACE_DIR}/flavours/{module_name}/model-{random_name}'

    model.save(path_to_zip_file)

    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extractall(zip_content_dst)

    rmtree(tmp_dir)

    return zip_content_dst

def get_job_status(job_id):
    config.load_incluster_config()
    batch_v1 = client.BatchV1Api()

    job = batch_v1.read_namespaced_job(job_id, ENVIRONMENT)

    annotations = job.metadata.annotations or {}
    result = annotations.get('result')
    result = json.loads(result) if result else None
    status = job.status

    job_data = {
        'result': result,
        'status': status.to_dict()
    }

    return job_data

def download_tar(job_id):
    uid = job_id.split(f'{JOB_NAME}-')[1]

    return send_from_directory(WORKSPACE_DIR, path=f'kaniko_image-{uid}.tar', as_attachment=False)

def build_image():
    image_data = json.load(request.files.get('image_data'))
    model = request.files.get('model')
    input_file = request.files.get('input_file')

    if not (image_data and model):
        return 'Both model and image_data are required', 500

    image_name = image_data.get('name')
    module_name = image_data.get('module_name')
    # XXX
    module_name = 'mlflow'
    model_name = image_data.get('model_name')
    # It should match the version that
    # has been used to generate the model.
    module_version = image_data.get('module_version')
    deploy = image_data.get('deploy', False)
    deploy = True if deploy else ''
    registry_auth = image_data.get('registry_auth')

    random_name = str(uuid.uuid4())
    model_unzipped_dir = unzip_model(model, module_name, random_name)

    path_to_tar_file = f'{WORKSPACE_DIR}/kaniko_image-{random_name}.tar'

    error = run_kaniko(
        image_name,
        module_name,
        module_version,
        model_name,
        path_to_tar_file,
        random_name,
        deploy,
        registry_auth,
    )

    if error:
        return {'error': error, 'job_id': None}

    return {'error': False, 'job_id': f'{JOB_NAME}-{random_name}'}

def copy_required_files_for_kaniko():
    try:
        for dir_to_copy in 'proxy flavours'.split():
            dst = f'{WORKSPACE_DIR}/{dir_to_copy}'

            if os.path.exists(dst):
                rmtree(dst)

            copytree(f'./volume/{dir_to_copy}', dst)
    except OSError as e:
        print(f'Directory not copied. Error: {e}')

def create_app(test_config=None):
    flask_app = Flask(__name__)

    if test_config is None:
        # Load the instance config, if it exists, when not testing.
        flask_app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in.
        flask_app.config.update(test_config)

    @flask_app.route('/')
    def hello():
        return 'Alive!'

    @flask_app.route('/build', methods=['POST'])
    def build_image_api():
        return build_image()

    @flask_app.route('/job/<job_id>', methods=['GET'])
    def get_job_status_api(job_id):
        return get_job_status(job_id)

    @flask_app.route('/job/<job_id>/download-tar')
    def download_job_tar_api(job_id):
        return download_tar(job_id)

    return flask_app


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    copy_required_files_for_kaniko()

    app = create_app()
    app.run(debug=False, host='0.0.0.0', port=port)
