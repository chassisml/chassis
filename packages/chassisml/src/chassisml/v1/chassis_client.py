import time
import urllib.parse
import warnings
from typing import Union

import requests
from packaging import version

from chassis.typing import LegacyBatchPredictFunction, LegacyNormalPredictFunction
from chassis.builder import BuildResponse
from .chassis_model import ChassisModel
from .helpers import deprecated

routes = {
    'build': '/build',
    'job': '/jobs',
    'test': '/test'
}


class ChassisClient:
    """
    The Chassis Client object.

    This class is used to interact with the Kaniko service.

    Attributes:
        base_url (str): The base url for the API.
        auth_header (str): Optional authorization header to be included with all requests.
        ssl_verification (Union[str, bool]): Can be path to certificate to use during requests to service, True (use verification), or False (don't use verification).
    """

    def __init__(self, base_url='http://localhost:5000', auth_header=None, ssl_verification=True):
        self.base_url = base_url
        self.auth_header = auth_header
        self.ssl_verification = ssl_verification

        if base_url == "http://chassis-test-mode:9999":
            # Don't try to reach out to a real server during tests.
            return

        version_route = base_url + "/version"
        if self.auth_header:
            res = requests.get(version_route, headers={'Authorization': self.auth_header}, verify=self.ssl_verification)
        else:
            res = requests.get(version_route, verify=self.ssl_verification)

        parsed_version = version.parse(res.text)
        if parsed_version < version.Version('1.5.0'):
            warnings.warn("Chassis service version should be >=1.5.0 for compatibility with this SDK version, things may not work as expected. Please update the service.")

    def get_job_status(self, job_id: str) -> BuildResponse:
        """
        Checks the status of a chassis job

        Args:
            job_id (str): Chassis job identifier generated from `ChassisModel.publish` method

        Returns:
            Dict: JSON Chassis job status

        Examples:
        ```python
        # Create Chassisml model
        chassis_model = chassis_client.create_model(process_fn=process)

        # Define Dockerhub credentials
        dockerhub_user = "user"
        dockerhub_pass = "password"

        # Publish model to Docker registry
        response = chassis_model.publish(
            model_name="Chassisml Regression Model",
            model_version="0.0.1",
            registry_user=dockerhub_user,
            registry_pass=dockerhub_pass,
        )

        job_id = response.get('job_id')
        job_status = chassis_client.get_job_status(job_id)
        ```

        """
        route = f'{urllib.parse.urljoin(self.base_url, routes["job"])}/{job_id}'
        if self.auth_header:
            res = requests.get(route, headers={'Authorization': self.auth_header}, verify=self.ssl_verification)
        else:
            res = requests.get(route, verify=self.ssl_verification)

        data = res.json()
        return BuildResponse(**data)

    def get_job_logs(self, job_id):
        """
        Checks the status of a chassis job
        Args:
            job_id (str): Chassis job identifier generated from `ChassisModel.publish` method

        Returns:
            Dict: JSON Chassis job status
        Examples:
        ```python
        # Create Chassisml model
        chassis_model = chassis_client.create_model(process_fn=process)
        # Define Dockerhub credentials
        dockerhub_user = "user"
        dockerhub_pass = "password"
        # Publish model to Docker registry
        response = chassis_model.publish(
            model_name="Chassisml Regression Model",
            model_version="0.0.1",
            registry_user=dockerhub_user,
            registry_pass=dockerhub_pass,
        )
        job_id = response.get('job_id')
        job_status = chassis_client.get_job_logs(job_id)
        ```
        """
        route = f'{urllib.parse.urljoin(self.base_url, routes["job"])}/{job_id}/logs'
        if self.auth_header:
            res = requests.get(route, headers={'Authorization': self.auth_header}, verify=self.ssl_verification)
        else:
            res = requests.get(route, verify=self.ssl_verification)
        res.raise_for_status()
        return res.text

    def block_until_complete(self, job_id: str, timeout=None, poll_interval=5) -> BuildResponse:
        """
        Blocks until Chassis job is complete or timeout is reached. Polls Chassis job API until a result is marked finished.

        Args:
            job_id (str): Chassis job identifier generated from `ChassisModel.publish` method
            timeout (int): Timeout threshold in seconds
            poll_interval (int): Amount of time to wait in between API polls to check status of job

        Returns:
            Dict: final job status returned by `ChassisClient.block_until_complete` method

        Examples:
        ```python
        # Create Chassisml model
        chassis_model = chassis_client.create_model(process_fn=process)

        # Define Dockerhub credentials
        dockerhub_user = "user"
        dockerhub_pass = "password"

        # Publish model to Docker registry
        response = chassis_model.publish(
            model_name="Chassisml Regression Model",
            model_version="0.0.1",
            registry_user=dockerhub_user,
            registry_pass=dockerhub_pass,
        )

        job_id = response.get('job_id')
        final_status = chassis_client.block_until_complete(job_id)
        ```
        """
        endby = time.time() + timeout if (timeout is not None) else None
        while True:
            status = self.get_job_status(job_id)
            if status.completed:
                return status
            if (endby is not None) and (time.time() > endby - poll_interval):
                print('Timed out before completion.')
                return BuildResponse(image_tag=None, logs=None, success=False, completed=False, error_message="Timed out before completion.", remote_build_id=job_id)
            time.sleep(poll_interval)

    def download_tar(self, job_id, output_filename):
        """
        Downloads container image as tar archive

        **NOTE**: This method is not available in the publicly-hosted service.

        Args:
            job_id (str): Chassis job identifier generated from `ChassisModel.publish` method
            output_filename (str): Local output filepath to save container image

        Returns:
            None: This method does not return an object

        Examples:
        ```python
        # Publish model to Docker registry
        response = chassis_model.publish(
            model_name="Chassisml Regression Model",
            model_version="0.0.1",
            registry_user=dockerhub_user,
            registry_pass=dockerhub_pass,
        )

        job_id = response.get('job_id)
        chassis_client.download_tar(job_id, "./chassis-model.tar")
        ```
        """
        deprecated()
        url = f'{urllib.parse.urljoin(self.base_url, routes["job"])}/{job_id}/download-tar'

        if self.auth_header:
            r = requests.get(url, headers={'Authorization': self.auth_header}, verify=self.ssl_verification)
        else:
            r = requests.get(url, verify=self.ssl_verification)

        if r.status_code == 200:
            with open(output_filename, 'wb') as f:
                f.write(r.content)
        else:
            print(f'Error download tar: {r.text}')

    def create_model(self, process_fn: LegacyNormalPredictFunction = None, batch_process_fn: LegacyBatchPredictFunction = None, batch_size=None):
        """
        DEPRECATED

        Builds chassis model locally

        Args:
            process_fn (function): Python function that must accept a single piece of input data in raw bytes form. This method is responsible for handling all data preprocessing, executing inference, and returning the processed predictions. Defining additional functions is acceptable as long as they are called within the `process` method
            batch_process_fn (function): Python function that must accept a batch of input data in raw bytes form. This method is responsible for handling all data preprocessing, executing inference, and returning the processed predictions. Defining additional functions is acceptable as long as they are called within the `process` method
            batch_size (int): Maximum batch size if `batch_process_fn` is defined

        Returns:
            ChassisModel: Chassis Model object that can be tested locally and published to a Docker Registry

        Examples:
        The following snippet was taken from this [example](https://docs.modzy.com/docs/chassis-ml).
        ```python
        # Import and normalize data
        X_digits, y_digits = datasets.load_digits(return_X_y=True)
        X_digits = X_digits / X_digits.max()

        n_samples = len(X_digits)

        # Split data into training and test sets
        X_train = X_digits[: int(0.9 * n_samples)]
        y_train = y_digits[: int(0.9 * n_samples)]
        X_test = X_digits[int(0.9 * n_samples) :]
        y_test = y_digits[int(0.9 * n_samples) :]

        # Train Model
        logistic = LogisticRegression(max_iter=1000)
        print(
            "LogisticRegression mean accuracy score: %f"
            % logistic.fit(X_train, y_train).score(X_test, y_test)
        )

        # Save small sample input to use for testing later
        sample = X_test[:5].tolist()
        with open("digits_sample.json", 'w') as out:
            json.dump(sample, out)

        # Define Process function
        def process(input_bytes):
            inputs = np.array(json.loads(input_bytes))
            inference_results = logistic.predict(inputs)
            structured_results = []
            for inference_result in inference_results:
                structured_output = {
                    "data": {
                        "result": {"classPredictions": [{"class": str(inference_result), "score": str(1)}]}
                    }
                }
                structured_results.append(structured_output)
            return structured_results

        # create Chassis model
        chassis_model = chassis_client.create_model(process_fn=process)
        ```

        """
        deprecated()
        if process_fn and batch_process_fn:
            raise ValueError("Please supply either a process_fn or batch_process_fn but not both")
        elif process_fn:
            return ChassisModel(process_fn, chassis_client=self, legacy_predict_fn=True)
        elif batch_process_fn:
            if not batch_size:
                raise ValueError("Both batch_process_fn and batch_size must be provided for batch support")
            return ChassisModel(batch_process_fn, batch_size=batch_size, legacy_predict_fn=True, chassis_client=self)
        else:
            raise ValueError("At least one of process_fn or batch_process_fn must be provided.")

    # TODO - move out of this class
    def run_inference(self, input_data, container_url="localhost", host_port=45000):
        """
        This is the method you use to submit data to a container chassis has built for inference. It assumes the container has been downloaded from dockerhub and is running somewhere you have access to.

        Args:
            input_data (json): dictionary of the form {"input": <binary respresentaion of your data>}
            container_url (str): URL where container is running
            host_port (int): host port that forwards to container's grpc server port

        Returns:
            return_value (str): Success -> results from model processing as specified in the process function.
                                Failure -> Error codes from processing errors. All errors should container the word "Error."

        Examples:
        ```python
        # assume that the container is running locally, and that it was started with this docker command
        #  docker run -it -p 5001:45000 <docker_uname>/<container_name>:<tag_id>

        from chassisml_sdk.chassisml import chassisml

        client = chassisml.ChassisClient("https://chassis.app.modzy.com/")

        input_data = {"input": b"[[0.0, 0.0, 0.0, 1.0, 12.0, 6.0, 0.0, 0.0, 0.0, 0.0, 0.0, 11.0, 15.0, 2.0, 0.0, 0.0, 0.0, 0.0, 8.0, 16.0, 6.0, 1.0, 2.0, 0.0, 0.0, 4.0, 16.0, 9.0, 1.0, 15.0, 9.0, 0.0, 0.0, 13.0, 15.0, 6.0, 10.0, 16.0, 6.0, 0.0, 0.0, 12.0, 16.0, 16.0, 16.0, 16.0, 1.0, 0.0, 0.0, 1.0, 7.0, 4.0, 14.0, 13.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 14.0, 9.0, 0.0, 0.0], [0.0, 0.0, 8.0, 16.0, 3.0, 0.0, 1.0, 0.0, 0.0, 0.0, 16.0, 14.0, 5.0, 14.0, 12.0, 0.0, 0.0, 0.0, 8.0, 16.0, 16.0, 9.0, 0.0, 0.0, 0.0, 0.0, 3.0, 16.0, 14.0, 1.0, 0.0, 0.0, 0.0, 0.0, 12.0, 16.0, 16.0, 2.0, 0.0, 0.0, 0.0, 0.0, 16.0, 11.0, 16.0, 4.0, 0.0, 0.0, 0.0, 3.0, 16.0, 16.0, 16.0, 6.0, 0.0, 0.0, 0.0, 0.0, 10.0, 16.0, 10.0, 1.0, 0.0, 0.0], [0.0, 0.0, 5.0, 12.0, 8.0, 0.0, 1.0, 0.0, 0.0, 0.0, 11.0, 16.0, 5.0, 13.0, 6.0, 0.0, 0.0, 0.0, 2.0, 15.0, 16.0, 12.0, 1.0, 0.0, 0.0, 0.0, 0.0, 10.0, 16.0, 6.0, 0.0, 0.0, 0.0, 0.0, 1.0, 15.0, 16.0, 7.0, 0.0, 0.0, 0.0, 0.0, 8.0, 16.0, 16.0, 11.0, 0.0, 0.0, 0.0, 0.0, 11.0, 16.0, 16.0, 9.0, 0.0, 0.0, 0.0, 0.0, 6.0, 12.0, 12.0, 3.0, 0.0, 0.0], [0.0, 0.0, 0.0, 3.0, 15.0, 4.0, 0.0, 0.0, 0.0, 0.0, 4.0, 16.0, 12.0, 0.0, 0.0, 0.0, 0.0, 0.0, 12.0, 15.0, 3.0, 4.0, 3.0, 0.0, 0.0, 7.0, 16.0, 5.0, 3.0, 15.0, 8.0, 0.0, 0.0, 13.0, 16.0, 13.0, 15.0, 16.0, 2.0, 0.0, 0.0, 12.0, 16.0, 16.0, 16.0, 13.0, 0.0, 0.0, 0.0, 0.0, 4.0, 5.0, 16.0, 8.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 16.0, 4.0, 0.0, 0.0], [0.0, 0.0, 10.0, 14.0, 8.0, 1.0, 0.0, 0.0, 0.0, 2.0, 16.0, 14.0, 6.0, 1.0, 0.0, 0.0, 0.0, 0.0, 15.0, 15.0, 8.0, 15.0, 0.0, 0.0, 0.0, 0.0, 5.0, 16.0, 16.0, 10.0, 0.0, 0.0, 0.0, 0.0, 12.0, 15.0, 15.0, 12.0, 0.0, 0.0, 0.0, 4.0, 16.0, 6.0, 4.0, 16.0, 6.0, 0.0, 0.0, 8.0, 16.0, 10.0, 8.0, 16.0, 8.0, 0.0, 0.0, 1.0, 8.0, 12.0, 14.0, 12.0, 1.0, 0.0]]"}
        input_list = [input_data for _ in range(30)]

        print("single input")
        print(client.run_inference(input_data, container_url="localhost", host_port=5001))
        print("multi inputs")
        results = client.run_inference(input_list, container_url="localhost", host_port=5001)
        for x in results:
            print(x)
        ```
        """
        model_client.override_server_URL(container_url, host_port)
        return model_client.run(input_data)

    # TODO - move out of this class
    def docker_infer(self, image_id, input_data, container_url="localhost", host_port=5001, container_port=None, timeout=20, clean_up=True, pull_container=False):
        """
        Runs inference on an OMI compliant container. This method checks to see if a container is running and if not starts it. The method then runs inference against the input_data with the model in the container, and optionally shuts down the container.

        Args:
            image_id (string): the name of an OMI container image usually of the form <docker_uname>/<container_name>:<tag_id>
            input_data (json): dictionary of the form {"input": <binary respresentaion of your data>}
            container_url (str): URL where container is running
            host_port (int): host port that forwards to container's grpc server port
            container_port (str): container port the grpc server listens to
            timeout (int): number of seconds to wait for gRPC server to spin up
            clean_up (bool): whether or not to stop and remove the container after inference
            pull_container (bool): if True pulls missing container from repo

        Returns:
            return_value (str):    Success -> model output as defined in the process function
                                    Failure -> Error message if any success criteria is missing.
        Example:
        ```python
        host_port = 5002
        client = chassisml.ChassisClient()


        input_data = {"input": b"[[0.0, 0.0, 0.0, 1.0, 12.0, 6.0, 0.0, 0.0, 0.0, 0.0, 0.0, 11.0, 15.0, 2.0, 0.0, 0.0, 0.0, 0.0, 8.0, 16.0, 6.0, 1.0, 2.0, 0.0, 0.0, 4.0, 16.0, 9.0, 1.0, 15.0, 9.0, 0.0, 0.0, 13.0, 15.0, 6.0, 10.0, 16.0, 6.0, 0.0, 0.0, 12.0, 16.0, 16.0, 16.0, 16.0, 1.0, 0.0, 0.0, 1.0, 7.0, 4.0, 14.0, 13.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 14.0, 9.0, 0.0, 0.0], [0.0, 0.0, 8.0, 16.0, 3.0, 0.0, 1.0, 0.0, 0.0, 0.0, 16.0, 14.0, 5.0, 14.0, 12.0, 0.0, 0.0, 0.0, 8.0, 16.0, 16.0, 9.0, 0.0, 0.0, 0.0, 0.0, 3.0, 16.0, 14.0, 1.0, 0.0, 0.0, 0.0, 0.0, 12.0, 16.0, 16.0, 2.0, 0.0, 0.0, 0.0, 0.0, 16.0, 11.0, 16.0, 4.0, 0.0, 0.0, 0.0, 3.0, 16.0, 16.0, 16.0, 6.0, 0.0, 0.0, 0.0, 0.0, 10.0, 16.0, 10.0, 1.0, 0.0, 0.0], [0.0, 0.0, 5.0, 12.0, 8.0, 0.0, 1.0, 0.0, 0.0, 0.0, 11.0, 16.0, 5.0, 13.0, 6.0, 0.0, 0.0, 0.0, 2.0, 15.0, 16.0, 12.0, 1.0, 0.0, 0.0, 0.0, 0.0, 10.0, 16.0, 6.0, 0.0, 0.0, 0.0, 0.0, 1.0, 15.0, 16.0, 7.0, 0.0, 0.0, 0.0, 0.0, 8.0, 16.0, 16.0, 11.0, 0.0, 0.0, 0.0, 0.0, 11.0, 16.0, 16.0, 9.0, 0.0, 0.0, 0.0, 0.0, 6.0, 12.0, 12.0, 3.0, 0.0, 0.0], [0.0, 0.0, 0.0, 3.0, 15.0, 4.0, 0.0, 0.0, 0.0, 0.0, 4.0, 16.0, 12.0, 0.0, 0.0, 0.0, 0.0, 0.0, 12.0, 15.0, 3.0, 4.0, 3.0, 0.0, 0.0, 7.0, 16.0, 5.0, 3.0, 15.0, 8.0, 0.0, 0.0, 13.0, 16.0, 13.0, 15.0, 16.0, 2.0, 0.0, 0.0, 12.0, 16.0, 16.0, 16.0, 13.0, 0.0, 0.0, 0.0, 0.0, 4.0, 5.0, 16.0, 8.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 16.0, 4.0, 0.0, 0.0], [0.0, 0.0, 10.0, 14.0, 8.0, 1.0, 0.0, 0.0, 0.0, 2.0, 16.0, 14.0, 6.0, 1.0, 0.0, 0.0, 0.0, 0.0, 15.0, 15.0, 8.0, 15.0, 0.0, 0.0, 0.0, 0.0, 5.0, 16.0, 16.0, 10.0, 0.0, 0.0, 0.0, 0.0, 12.0, 15.0, 15.0, 12.0, 0.0, 0.0, 0.0, 4.0, 16.0, 6.0, 4.0, 16.0, 6.0, 0.0, 0.0, 8.0, 16.0, 10.0, 8.0, 16.0, 8.0, 0.0, 0.0, 1.0, 8.0, 12.0, 14.0, 12.0, 1.0, 0.0]]"}
        input_list = [input_data for _ in range(30)]
        print("single input")
        print(client.docker_infer(image_id="claytondavisms/sklearn-digits-docker-test:0.0.7", input_data=input_data, container_url="localhost", host_port=host_port, clean_up=False, pull_container=True))

        print("multi inputs")
        results = client.run_inference(input_list, container_url="localhost", host_port=host_port)
        results = client.docker_infer(image_id="claytondavisms/sklearn-digits-docker-test:0.0.7", input_data=input_list, container_url="localhost", host_port=host_port)
        for x in results:
            print(x)
        ```
        """
        try:
            container_id = docker_start(image_id, host_port=host_port, container_port=container_port, timeout=timeout, pull_container=pull_container)
            if "Error" in container_id:
                raise ValueError("container_id wrong")
            return_value = self.run_inference(input_data, container_url=container_url, host_port=host_port)
            if clean_up:
                docker_clean_up(container_id)
        except Exception as e:
            return_value = {"results": ["Error " + str(e)]}

        return return_value
