import os
import yaml
import shutil
import tempfile
import subprocess

def download_model_artifacts(workspace_name,subscription_id,resource_group,model_name,output_dir):

    from azureml.core import Workspace,Model

    ws = Workspace.get(name=workspace_name,
               subscription_id=subscription_id,
               resource_group=resource_group)

    model = Model(ws, model_name)
    model.download(output_dir)
    print("Model downloaded.")

def replicate_remote_env(workspace_name,subscription_id,resource_group,remote_env_name,local_env_name=None):

    from azureml.core import Workspace,Model
    from azureml.core.environment import Environment

    #TODO: warn that you need CONDA!!!

    ws = Workspace.get(name=workspace_name,
               subscription_id=subscription_id,
               resource_group=resource_group)

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