import os
import subprocess
from mlflow.exceptions import RestException
from mlflow.tracking import MlflowClient

def download_registered_model_version(name,version,output_dir,tracking_uri=None,registry_uri=None):
    '''
    Downloads registered MLflow model

    Args:
        name (str): Registered model name
        version (str): Registered model version
        output_dir (str): Desired local output directory
        tracking_uri (str): MLflow tracking URI
        registry_uri (str): MLflow registry URI
    '''
    client = MlflowClient(tracking_uri=tracking_uri,registry_uri=registry_uri)
    run_id = client.get_model_version(name,version).run_id
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    client.download_artifacts(run_id, "model", output_dir)
    print("Model downloaded.")
    return os.path.join(output_dir,'model')

def replicate_env_from_model_dir(mlflow_model_dir,local_env_name):
    '''
    Replicates MLflow model environment, requires conda

    Args:
        mlflow_model_dir (str): Model directory
        local_env_name (str): Desired local environment name
    '''

    #TODO: warn that you need CONDA!!!

    conda_yaml_path = os.path.join(mlflow_model_dir,'conda.yaml')
    create_env_cmd = f"conda env create -f {conda_yaml_path} -n {local_env_name}"
    process = subprocess.Popen(
        create_env_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        encoding='utf-8',
        errors='replace'
    )
    while True:
        realtime_output = process.stdout.readline()

        if realtime_output == '' and process.poll() is not None:
            break

        if realtime_output:
            print(realtime_output.strip(), flush=True)
    print(f'New environment "{local_env_name}" created successfully.')

    add_env_to_ipykernel_cmd = f"""source activate {local_env_name};
    pip install ipykernel chassisml;
    python -m ipykernel install --user --name={local_env_name}
    """
    subprocess.run(add_env_to_ipykernel_cmd, capture_output=True, shell=True, executable='/bin/bash', check=True)
    print(f'New environment "{local_env_name}" added to ipykernel successfully.')
    print(f'Switch to "{local_env_name}", if you\'re using Jupyter: refresh page, click "Kernel", then "Change Kernel"')