import os
import json
import uuid
import tempfile
import zipfile
from shutil import rmtree, copytree

from loguru import logger
from dotenv import load_dotenv
from flask import Flask, request, send_from_directory

from kubernetes import client, config
from kubernetes.client.rest import ApiException

###########################################

load_dotenv()

MOUNT_PATH_DIR = os.getenv('MOUNT_PATH_DIR')
WORKSPACE_DIR = os.getenv('WORKSPACE_DIR')
MODZY_UPLOADER_REPOSITORY = os.getenv('MODZY_UPLOADER_REPOSITORY')

DATA_DIR = f'{MOUNT_PATH_DIR}/{WORKSPACE_DIR}'

ENVIRONMENT = os.getenv('K_ENVIRONMENT')

K_DATA_VOLUME_NAME= os.getenv('K_DATA_VOLUME_NAME')
K_EMPTY_DIR_NAME = os.getenv('K_EMPTY_DIR_NAME')
K_INIT_EMPTY_DIR_PATH = os.getenv('K_INIT_EMPTY_DIR_PATH')
K_KANIKO_EMPTY_DIR_PATH = os.getenv('K_KANIKO_EMPTY_DIR_PATH')
K_SERVICE_ACCOUNT_NAME = os.getenv('K_SERVICE_ACCOUNT_NAME')
K_JOB_NAME = os.getenv('K_JOB_NAME')

###########################################

def create_job_object(
    image_name,
    module_name,
    model_name,
    path_to_tar_file,
    random_name,
    modzy_data,
    publish,
    registry_auth,
):
    job_name = f'{K_JOB_NAME}-{random_name}'

    # XXX: Only for Docker Hub.
    registry_credentials = f'{{"auths":{{"https://index.docker.io/v1/":{{"auth":"{registry_auth}"}}}}}}'

    data_volume_mount = client.V1VolumeMount(
        mount_path=MOUNT_PATH_DIR,
        name=K_DATA_VOLUME_NAME
    )
    # This volume will be used by init container to populare registry credentials.
    init_empty_dir_volume_mount = client.V1VolumeMount(
        mount_path=K_INIT_EMPTY_DIR_PATH,
        name=K_EMPTY_DIR_NAME
    )
    # This volume will be used by kaniko container to get registry credentials.
    kaniko_empty_dir_volume_mount = client.V1VolumeMount(
        mount_path=K_KANIKO_EMPTY_DIR_PATH,
        name=K_EMPTY_DIR_NAME
    )

    # This container is used to populate registry credentials.
    init_container = client.V1Container(
        name='credentials',
        image='busybox',
        volume_mounts=[init_empty_dir_volume_mount],
        # XXX: Only compatible with Docker Hub at the moment.
        command=[
            '/bin/sh',
            '-c',
            f'echo \'{registry_credentials}\' > {K_INIT_EMPTY_DIR_PATH}/config.json'
        ]
    )
    # This container is used to build the final image.
    init_container_kaniko = client.V1Container(
        name='kaniko',
        image='gcr.io/kaniko-project/executor:latest',
        volume_mounts=[
            data_volume_mount,
            kaniko_empty_dir_volume_mount
        ],
        args=[
            f'--dockerfile={DATA_DIR}/flavours/{module_name}/Dockerfile',
            '' if publish else '--no-push',
            f'--tarPath={path_to_tar_file}',
            f'--destination={image_name}{"" if ":" in image_name else ":latest"}',
            f'--context={DATA_DIR}',
            f'--build-arg=MODEL_DIR=model-{random_name}',
            f'--build-arg=MODZY_METADATA_PATH={modzy_data.get("modzy_metadata_path")}',
            f'--build-arg=MODEL_NAME={model_name}',
            f'--build-arg=MODEL_CLASS={module_name}',
            # Modzy is the default interface.
            '--build-arg=INTERFACE=modzy',
        ]
    )
    modzy_uploader_container = client.V1Container(
        name='modzy-uploader',
        image=MODZY_UPLOADER_REPOSITORY,
        volume_mounts=[data_volume_mount],
        env=[
            client.V1EnvVar(name='JOB_NAME', value=job_name),
            client.V1EnvVar(name='ENVIRONMENT', value=ENVIRONMENT)
        ],
        args=[
            f'--api_key={modzy_data.get("api_key")}',
            f'--deploy={True if modzy_data.get("deploy") else ""}',
            f'--sample_input_path={modzy_data.get("modzy_sample_input_path")}',
            f'--metadata_path={DATA_DIR}/{modzy_data.get("modzy_metadata_path")}',
            f'--image_tag={image_name}{"" if ":" in image_name else ":latest"}',
        ]
    )

    data_pv_claim = client.V1PersistentVolumeClaimVolumeSource(
        claim_name=K_DATA_VOLUME_NAME
    )
    data_volume = client.V1Volume(
        name=K_DATA_VOLUME_NAME,
        persistent_volume_claim=data_pv_claim
    )
    empty_dir_volume = client.V1Volume(
        name=K_EMPTY_DIR_NAME,
        empty_dir=client.V1EmptyDirVolumeSource()
    )
    pod_spec = client.V1PodSpec(
        service_account_name=K_SERVICE_ACCOUNT_NAME,
        restart_policy='Never',
        init_containers=[init_container, init_container_kaniko],
        containers=[modzy_uploader_container],
        volumes=[
            data_volume,
            empty_dir_volume
        ]
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

def run_kaniko(
    image_name,
    module_name,
    model_name,
    path_to_tar_file,
    random_name,
    modzy_data,
    publish,
    registry_auth,
):
    config.load_incluster_config()
    batch_v1 = client.BatchV1Api()

    try:
        job = create_job_object(
            image_name,
            module_name,
            model_name,
            path_to_tar_file,
            random_name,
            modzy_data,
            publish,
            registry_auth,
        )
        create_job(batch_v1, job)
    except Exception as err:
        return str(err)

    return False

def unzip_model(model, module_name, random_name):
    tmp_dir = tempfile.mkdtemp()
    path_to_zip_file = f'{tmp_dir}/{model.filename}'
    zip_content_dst = f'{DATA_DIR}/flavours/{module_name}/model-{random_name}'

    model.save(path_to_zip_file)

    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extractall(zip_content_dst)

    rmtree(tmp_dir)

    return zip_content_dst

def extract_modzy_metadata(modzy_metadata_data, module_name, random_name):
    if modzy_metadata_data:
        metadata_path = f'flavours/{module_name}/model-{random_name}.yaml'
        modzy_metadata_data.save(f'{DATA_DIR}/{metadata_path}')
    else:
        # Use the default one if user has not sent its own metadata file.
        # This way, mlflow/Dockerfile will not throw an error because it
        # will copy a file that does exist.
        metadata_path = f'flavours/{module_name}/interfaces/modzy/asset_bundle/0.1.0/model.yaml'

    return metadata_path

def extract_modzy_sample_input(modzy_sample_input_data, module_name, random_name):
    if not modzy_sample_input_data:
        return

    sample_input_path = f'{DATA_DIR}/flavours/{module_name}/{random_name}-{modzy_sample_input_data.filename}'
    modzy_sample_input_data.save(sample_input_path)

    return sample_input_path

def get_job_status(job_id):
    config.load_incluster_config()
    batch_v1 = client.BatchV1Api()

    try:
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
    except ApiException as e:
        logger.error(f'Exception when getting job status: {e}')
        return e.body

def download_tar(job_id):
    uid = job_id.split(f'{K_JOB_NAME}-')[1]

    return send_from_directory(DATA_DIR, path=f'kaniko_image-{uid}.tar', as_attachment=False)

def build_image():
    if not ('image_data' in request.files and 'model' in request.files):
        return 'Both model and image_data are required', 500

    image_data = json.load(request.files.get('image_data'))
    model = request.files.get('model')
    modzy_metadata_data = request.files.get('modzy_metadata_data')
    modzy_sample_input_data = request.files.get('modzy_sample_input_data')
    modzy_data = json.load(request.files.get('modzy_data') or {})

    image_name = image_data.get('name')
    # XXX: this is hardcoded here because before we were using
    # other frameworks until we decided to fix it to mlflow.
    module_name = 'mlflow'
    model_name = image_data.get('model_name')
    # It should match the version that
    # has been used to generate the model.
    publish = image_data.get('publish', False)
    publish = True if publish else ''
    registry_auth = image_data.get('registry_auth')

    random_name = str(uuid.uuid4())
    model_unzipped_dir = unzip_model(model, module_name, random_name)

    # User can build the image but not deploy it to Modzy. So no input_sample is mandatory.
    # On the other hand, the model.yaml is needed to build the image so proceed with it.
    if modzy_data:
        modzy_sample_input_path = extract_modzy_sample_input(modzy_sample_input_data, module_name, random_name)
        modzy_data['modzy_sample_input_path'] = modzy_sample_input_path

    modzy_metadata_path = extract_modzy_metadata(modzy_metadata_data, module_name, random_name)
    modzy_data['modzy_metadata_path'] = modzy_metadata_path

    path_to_tar_file = f'{DATA_DIR}/kaniko_image-{random_name}.tar'

    logger.debug(f'Request data: {image_name}, {module_name}, {model_name}, {path_to_tar_file}')

    error = run_kaniko(
        image_name,
        module_name,
        model_name,
        path_to_tar_file,
        random_name,
        modzy_data,
        publish,
        registry_auth,
    )

    if error:
        return {'error': error, 'job_id': None}

    return {'error': False, 'job_id': f'{K_JOB_NAME}-{random_name}'}

def copy_required_files_for_kaniko():
    try:
        # These directories will be copied to a shared volume
        # with Kaniko so that it will be able to access them.
        for dir_to_copy in 'flavours'.split():
            dst = f'{DATA_DIR}/{dir_to_copy}'

            if os.path.exists(dst):
                rmtree(dst)

            copytree(f'./{dir_to_copy}', dst)
    except OSError as e:
        print(f'Directory not copied. Error: {e}')

def create_app():
    flask_app = Flask(__name__)

    @flask_app.route('/health')
    def hello2():
        return 'Chassis Server Up and Running!'

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

###########################################

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    copy_required_files_for_kaniko()

    app = create_app()
    app.run(debug=False, host='0.0.0.0', port=port)