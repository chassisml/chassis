import os
import yaml
import shutil
import tempfile
import subprocess

def download_model_artifacts(tenant_id,service_principal_id,service_principal_password,
                    workspace_name,subscription_id,resource_group,model_name,output_dir):
    '''
    Downloads registered Azure ML model artifacts

    Args:
        tenant_id (str): Azure ML tenant id
        service_principal_id (str): Azure ML service principal id with access to workspace
        service_principal_password (str): Azure ML service principal password with access to workspace
        workspace_name (str): Azure ML workspace name
        subscription_id (str): Azure ML subscription ID
        resource_group (str): Azure ML resource group
        model_name (str): Azure ML registered model name
        output_dir (str): Desired local output directory
    '''

    from azureml.core import Workspace,Model
    from azureml.core.authentication import ServicePrincipalAuthentication

    svc_pr = ServicePrincipalAuthentication(
            tenant_id=tenant_id,
            service_principal_id=service_principal_id,
            service_principal_password=service_principal_password
        )
        
    ws = Workspace.get(name=workspace_name,
            subscription_id=subscription_id,
            resource_group=resource_group,
            auth=svc_pr)

    model = Model(ws, model_name)
    model.download(output_dir,exist_ok=True)
    print("Model downloaded.")

def replicate_remote_env(tenant_id,service_principal_id,service_principal_password,
    workspace_name,subscription_id,resource_group,remote_env_name,local_env_name=None):
    '''
    Replicates remote Azure ML environment locally, requires conda

    Args:
        tenant_id (str): Azure ML tenant id
        service_principal_id (str): Azure ML service principal id with access to workspace
        service_principal_password (str): Azure ML service principal password with access to workspace
        workspace_name (str): Azure ML workspace name
        subscription_id (str): Azure ML subscription ID
        resource_group (str): Azure ML resource group
        remote_env_name (str): Azure ML environment name
        local_env_name (str): Desired local environment name
    '''

    from azureml.core import Workspace,Model
    from azureml.core.environment import Environment
    from azureml.core.authentication import ServicePrincipalAuthentication

    #TODO: warn that you need CONDA!!!

    svc_pr = ServicePrincipalAuthentication(
            tenant_id=tenant_id,
            service_principal_id=service_principal_id,
            service_principal_password=service_principal_password
        )
        
    ws = Workspace.get(name=workspace_name,
            subscription_id=subscription_id,
            resource_group=resource_group,
            auth=svc_pr)

    myenv = Environment.get(workspace=ws, name=remote_env_name)
    yaml_data = myenv.python.conda_dependencies.as_dict()
    
    try:
        tmppath = tempfile.mkdtemp()
        conda_yaml_path = os.path.join(tmppath,'conda.yaml')
        with open(conda_yaml_path,'w',encoding = "utf-8") as f:
            f.write(yaml.dump(yaml_data))

        new_env_name = local_env_name if local_env_name else yaml_data['name']
        create_env_cmd = f"conda env create -f {conda_yaml_path} -n {new_env_name}"
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
        print(f'New environment "{new_env_name}" created successfully.')

        add_env_to_ipykernel_cmd = f"""source activate {new_env_name};
        pip install ipykernel chassisml;
        python -m ipykernel install --user --name={new_env_name}
        """
        subprocess.run(add_env_to_ipykernel_cmd, capture_output=True, shell=True, executable='/bin/bash', check=True)
        print(f'New environment "{new_env_name}" added to ipykernel successfully.')
        
        shutil.rmtree(tmppath)
    except Exception as e:
        if os.path.exists(tmppath):
            shutil.rmtree(tmppath)
        raise(e)
