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

CHASSIS_DEV = True
WINDOWS = True if os.name == 'nt' else False

if CHASSIS_DEV:
    # if you are doing development
    # we need to setup the repo for 3rd party uploads
    MODZY_UPLOADER_REPOSITORY = 'ghcr.io/modzy/chassis-modzy-uploader'
    # TODO: determine if we need to update these paths on windows or Mac
    MOUNT_PATH_DIR = os.getenv('MOUNT_PATH_DIR')
    WORKSPACE_DIR = os.getenv('WORKSPACE_DIR')
    # TODO: check for development volumes
else:
    MODZY_UPLOADER_REPOSITORY = os.getenv('MODZY_UPLOADER_REPOSITORY')

DATA_DIR = f'{MOUNT_PATH_DIR}/{WORKSPACE_DIR}'

ENVIRONMENT = os.getenv('K_ENVIRONMENT')

K_DATA_VOLUME_NAME = os.getenv('K_DATA_VOLUME_NAME')
K_EMPTY_DIR_NAME = os.getenv('K_EMPTY_DIR_NAME')
K_INIT_EMPTY_DIR_PATH = os.getenv('K_INIT_EMPTY_DIR_PATH')
K_KANIKO_EMPTY_DIR_PATH = os.getenv('K_KANIKO_EMPTY_DIR_PATH')
K_SERVICE_ACCOUNT_NAME = os.getenv('K_SERVICE_ACCOUNT_NAME')
K_JOB_NAME = os.getenv('K_JOB_NAME')


###########################################
def create_dev_environment():
    # get the kubeconfig file for local cluster
    kubefile = os.getenv("CHASSIS_KUBECONFIG")
    config.load_kube_config(kubefile)

    # check to see if the development cluster has the development volume and claim installed
    base_api = client.CoreV1Api()
    try:
        # check to see if the volume exists
        # volume and claim based off of https://github.com/docker/for-win/issues/5325#issuecomment-632309842 Gsyltc comment
        api_response = base_api.list_persistent_volume(pretty='pretty', watch=False)
        print(api_response)
        filtered_pv = [pv for pv in api_response.items if pv.metadata.name == "local-volume-chassis"]
        if len(filtered_pv) == 0:
            # if the volume doesn't exist, create it. note these paths are specific for Docker Desktop On Windows
            # TODO: document a Linux or Mac version

            local_path = f'/run/desktop/mnt/host/c/{MOUNT_PATH_DIR}'

            local_node_selector_terms = client.V1NodeSelectorTerm(
                match_expressions=[client.V1NodeSelectorRequirement(
                    key="kubernetes.io/hostname",
                    operator="In",
                    values=["docker-desktop"])]
            )

            local_volume_spec = client.V1PersistentVolumeSpec(capacity={"storage": "10Gi"},
                                                              volume_mode="Filesystem",
                                                              access_modes=["ReadWriteOnce"],
                                                              persistent_volume_reclaim_policy="Delete",
                                                              storage_class_name="local-storage",
                                                              local=client.V1LocalVolumeSource(path=local_path),
                                                              node_affinity=client.V1VolumeNodeAffinity(
                                                                  required=client.V1NodeSelector(
                                                                      node_selector_terms=[local_node_selector_terms])
                                                              )
                                                              )
            local_volume_meta = client.V1ObjectMeta(name="local-volume-chassis")

            local_pvolume = client.V1PersistentVolume(api_version="v1",
                                                      kind="PersistentVolume",
                                                      metadata=local_volume_meta,
                                                      spec=local_volume_spec)

            api_response = base_api.create_persistent_volume(body=local_pvolume)
            print(api_response)
    except Exception as err:
        print(err)

    try:
        # check to see if the volume claim exists
        api_response = base_api.list_persistent_volume_claim_for_all_namespaces(pretty='pretty', watch=False)
        print(api_response)
        filtered_pvc = [pvc for pvc in api_response.items if pvc.metadata.name == "dir-claim-chassis"]
        if len(filtered_pvc) == 0:
            # if the volume doesn't exist, create it.

            local_volume_claim_spec = client.V1PersistentVolumeClaimSpec(storage_class_name="local-storage",
                                                                         access_modes=["ReadWriteOnce"],
                                                                         resources=client.V1ResourceRequirements(
                                                                             requests={"storage": "1Gi"}
                                                                         )
                                                                         )

            local_pvolume_claim = client.V1PersistentVolumeClaim(api_version="v1",
                                                                 kind="PersistentVolumeClaim",
                                                                 metadata=client.V1ObjectMeta(name="dir-claim-chassis"),
                                                                 spec=local_volume_claim_spec)

            api_response = base_api.create_namespaced_persistent_volume_claim(body=local_pvolume_claim,
                                                                              namespace="default")
            print(api_response)
    except Exception as err:
        print(err)

    # The dev volume and claim are now accessible in the local Kubernetes cluster.
    # testing has only been done against Windows 10 running the kubernetes cluster in docker desktop
    return


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
    # This sets up all the objects needed to create a model image

    job_name = f'{K_JOB_NAME}-{random_name}'

    # credential setup for Docker Hub.
    # json for holding registry credentials that will access docker hub.
    # reference: https://github.com/GoogleContainerTools/kaniko#pushing-to-docker-hub 
    registry_credentials = f'{{"auths":{{"https://index.docker.io/v1/":{{"auth":"{registry_auth}"}}}}}}'

    # mount path leads to /data
    # this is a mount point. NOT the volume itself.
    # name aligns with a volume defined below.
    data_volume_mount = client.V1VolumeMount(
        mount_path=MOUNT_PATH_DIR,
        name="local-volume-code"
    ) if CHASSIS_DEV else client.V1VolumeMount(
        mount_path=MOUNT_PATH_DIR,
        name=K_DATA_VOLUME_NAME
    )

    # This volume will be used by init container to populate registry credentials.
    # mount leads to /tmp/credentials
    # this is a mount point. NOT the volume itself.
    # name aligns with a volume defined below.
    init_empty_dir_volume_mount = client.V1VolumeMount(
        mount_path=K_INIT_EMPTY_DIR_PATH,
        name=K_EMPTY_DIR_NAME
    )

    # This volume will be used by kaniko container to get registry credentials.
    # mount path leads to /kaniko/.docker per kaniko reference documentation
    # this is a mount point. NOT the volume itself.
    # name aligns with a volume defined below.
    kaniko_empty_dir_volume_mount = client.V1VolumeMount(
        mount_path=K_KANIKO_EMPTY_DIR_PATH,
        name=K_EMPTY_DIR_NAME
    )

    # This container is used to populate registry credentials.
    # it only runs the single command in shell to echo our credentials into their proper file
    # per the reference documentation for Docker Hub
    # TODO: add credentials for Cloud Providers
    init_container = client.V1Container(
        name='credentials',
        image='busybox',
        volume_mounts=[init_empty_dir_volume_mount],
        command=[
            '/bin/sh',
            '-c',
            f'echo \'{registry_credentials}\' > {K_INIT_EMPTY_DIR_PATH}/config.json'
        ]
    )

    # This is the kaniko container used to build the final image.
    # the arguments are different depending on whether you are doing local dev or running in production
    # the dockerfile is in a subdirectory of the service so we use the current working directory to access it.
    # service_dir = ("/" + os.getcwd().replace("\\", "/").replace(":", "")).lower()
    service_dir = DATA_DIR
    comment = """[
            f'--dockerfile={service_dir}/flavours/{module_name}/Dockerfile',
            '' if publish else '--no-push',
            f'--tarPath={path_to_tar_file}',
            f'--destination={image_name}{"" if ":" in image_name else ":latest"}',
            f'--context={service_dir}',
            f'--build-arg=MODEL_DIR=model-{random_name}',
            f'--build-arg=MODZY_METADATA_PATH={modzy_data.get("modzy_metadata_path")}',
            f'--build-arg=MODEL_NAME={model_name}',
            f'--build-arg=MODEL_CLASS={module_name}',
            # Modzy is the default interface.
            '--build-arg=INTERFACE=modzy',
        ] if CHASSIS_DEV else """

    kaniko_args = [
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

    init_container_kaniko = client.V1Container(
        name='kaniko',
        image='gcr.io/kaniko-project/executor:latest',
        volume_mounts=[
            data_volume_mount,
            kaniko_empty_dir_volume_mount
        ],
        args=kaniko_args
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

    # volume claim
    data_pv_claim = client.V1PersistentVolumeClaimVolumeSource(
        claim_name="dir-claim-chassis"
    ) if CHASSIS_DEV else client.V1PersistentVolumeClaimVolumeSource(
        claim_name=K_DATA_VOLUME_NAME
    )

    # volume holding data

    data_volume = client.V1Volume(
        name="local-volume-code",
        persistent_volume_claim=data_pv_claim
    ) if CHASSIS_DEV else client.V1Volume(
        name=K_DATA_VOLUME_NAME,
        persistent_volume_claim=data_pv_claim
    )

    # volume holding credentials 
    empty_dir_volume = client.V1Volume(
        name=K_EMPTY_DIR_NAME,
        empty_dir=client.V1EmptyDirVolumeSource()
    )

    # Pod spec for the image build process 
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

    # setup and initiate model image build
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
    # this method kicks off the kaniko build job to create the new model image.
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
    # This method creates and launches a job object that uses Kaniko to 
    # create the desired image.
    if CHASSIS_DEV:
        # if you are doing local dev you need to point at the local kubernetes cluster with your config file
        kubefile = os.getenv("CHASSIS_KUBECONFIG")
        config.load_kube_config(kubefile)
    else:
        # if the service is running inside a cluster during production then the config can be inherited
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

    # if running on windows, zip dst has to be modified for local kubernetes processing
    # if WINDOWS:
    # zip_content_dst =

    model.save(path_to_zip_file)

    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extractall(zip_content_dst)

    rmtree(tmp_dir)


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
    # This method gets the status of the Kaniko job and the results if the job has completed.
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
    # This method gets to image kaniko built during the job named "jobid"
    uid = job_id.split(f'{K_JOB_NAME}-')[1]

    return send_from_directory(DATA_DIR, path=f'kaniko_image-{uid}.tar', as_attachment=False)


def build_image():
    # this method is run by the /build route. It generates a model image based upon a POST request
    # request.files structure can be seen in chassisml-sdk
    if not ('image_data' in request.files and 'model' in request.files):
        return 'Both model and image_data are required', 500

    # retrieve image_data and populate variables accordingly
    image_data = json.load(request.files.get('image_data'))
    model_name = image_data.get('model_name')
    image_name = image_data.get('name')
    publish = image_data.get('publish', False)
    publish = True if publish else ''
    registry_auth = image_data.get('registry_auth')

    # retrieve binary representations for all three variables 
    model = request.files.get('model')
    modzy_metadata_data = request.files.get('modzy_metadata_data')
    modzy_sample_input_data = request.files.get('modzy_sample_input_data')

    # json string loaded into variable
    modzy_data = json.load(request.files.get('modzy_data') or {})

    # This is a future proofing variable in case we encounter a model that cannot be converted into mlflow.
    # It will remain hardcoded for now. 
    module_name = 'mlflow'

    # This name is a random id used to ensure that all jobs are uniquely named and traceable.
    random_name = str(uuid.uuid4())

    # Unzip model archive
    unzip_model(model, module_name, random_name)

    # User can build the image but not deploy it to Modzy. So no input_sample is mandatory.
    # On the other hand, the model.yaml is needed to build the image so proceed with it.

    # save the sample input to the modzy_sample_input_path directory
    if modzy_data:
        modzy_sample_input_path = extract_modzy_sample_input(modzy_sample_input_data, module_name, random_name)
        modzy_data['modzy_sample_input_path'] = modzy_sample_input_path

    # TODO: this probably should only be done if modzy_data is true.
    modzy_metadata_path = extract_modzy_metadata(modzy_metadata_data, module_name, random_name)
    modzy_data['modzy_metadata_path'] = modzy_metadata_path

    # this path is the local location that kaniko will store the image it creates
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
    # if using a special debug docker file this is where it goes
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
    create_dev_environment()

    app = create_app()
    app.run(debug=False, host='0.0.0.0', port=port)
