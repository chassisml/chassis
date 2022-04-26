
import docker
import time
from grpc_requests import Client



class OMI_check():
    """This Class checks an image to see if it is compliant with the OMI Spec www.openmodel.ml/spec
        It is assumed that
         1. the image is locally resident on the user's host machine
         2. Docker is locally installed on the user's host machine
         3. the account running the methods in this class has docker access permissions.

    Attributes:
        version (str): the version of this class
        omi_required_annotations (list[str]): a list of the OMI required strings.
        omi_required_gRPC_methods (list[str]): a list of the OMI required gRPC methods.
        image_id(str): the id of the image to be tested for OMI compliance. e.g. dockerusername/modelname:tag
        container(docker container): Docker container created from image_id with the Docker API
        container_port(int): port on the container that the model listens on. defaults to 45000, but overridden by  ml.openmodel.port annotation
        host_port(int): port on docker running host that will be forwarded to the container_port. defaults to 5001, but can be overridden in constructer.
        url(str): url of running class container. defaults to localhost.
    """

    version = "0.0.1"
    omi_required_annotations = ["ml.openmodel.interfaces",
                                "ml.openmodel.protocols",
                                "ml.openmodel.port",
                                "ml.openml.model_name"]
    omi_required_gRPC_methods = ["Run", "Status", "Shutdown"]
    image_id = None
    container = None
    container_port = None   # must be numeric
    host_port = None        # must be numeric
    url = None

    # The base_url variable to the init constructor is used to initialize the 
    # Docker API client. For windows, this url is 'npipe:////./pipe/docker_engine'
    # But by default, Docker will set the url to the DOCKER_HOST environment variable,
    # which automatically detects where the Docker server is hosted based on operating system 
    def __init__(self, base_url=None, 
                 image_id=None,
                 container_port=45000,
                 host_port=5001,
                 url="localhost"):

        try:
            print(base_url)
            self.client = docker.APIClient()
            self.image_id = image_id
            self.container_port = container_port
            self.host_port = host_port
            self.url = url
        except Exception as e:
            self.client = None

            print("Error: no Docker client available at the base url")

    def start_container(self, timeout=20):
        '''
                Creates and starts a container for gRPC server testing.

                Args:
                    timeout (int): number of seconds to wait for gRPC server to spin up

                Returns:
                    str:    Success message if the container is successfully created and started AND the gRPC server spins up within timeout seconds.
                            Failure message if any success criteria is missing.

                '''

        return_value = "Failure: container didn't start"

        try:
            self.container = self.client.create_container(
                image=self.image_id,
                name="OMI_Compliance_Check_Container",
                ports=[self.container_port],
                host_config=self.client.create_host_config(port_bindings={
                    self.container_port: self.host_port
                })
            )
            self.client.start(container=self.container.get('Id'))

            grpc_started = False
            for t in range(timeout):
                log_entry = "".join([chr(x) for x in self.client.logs(container=self.container.get('Id'))])
                if "gRPC Server running" in log_entry:
                    grpc_started = True
                    break
                time.sleep(1)

            if grpc_started is False:
                raise TimeoutError("server failed to start within timeout limit of "+str(timeout)+"seconds")

            return_value = "Success: Container Start Successful"

        except Exception as e:
            return_value += "\n Error Message: " + str(e)
            print("Error: Container failed to start with Docker client call\n" + print(e))

        return return_value

    def clean_up(self):
        '''
            Creates and starts a container for gRPC server testing.

            Args:
            None: N/A

            Returns:
            str:    Success message if the container is successfully stopped and removed.
                    Failure message if any success criteria is missing.

            '''

        return_value = "Failure: OMI clean up failed."\
                       "\n Check to make sure containers have been removed from your system." \
                       "\n If they are on your system still, they will be named OMI_Compliance_Check_Container." \
                       "\n Manually remove them if they still exist with 'docker rm'."
        partial_success = False
        try:
            # containers only shows running containers by default so this grab the container for us to stop it.
            if len(self.client.containers(filters={"id":self.container.get('Id')})) > 0:
                self.client.stop(container=self.container.get('Id'))
            partial_success=True
        except Exception as e:
            return_value += "\n Error Message: " + str(e)
            print("Error: there was a problem stopping the OMI Compliance check container. \n if you are sure it is running, you should manually stop it.")

        try:
            # we stop the container regardless of its state as it is not intended for use outside the OMI check.
            self.client.remove_container(container=self.container.get('Id'), force=True)
            if partial_success:
                return_value = "Success: The OMI_Compliance_Check_Container has been stopped and removed from the host."
        except Exception as e:
            return_value += "\n Error Message: " + str(e)
            print("Error: problem removing the OMI Compliance check container. \n if you are sure it is on the system, you should remove it manually")

        return return_value

    def validate_image(self):
        '''
             Validates that an image has the OMI required OCI annotations. Also assigns container port from annotation.

        Args:
            None: N/A

        Returns:
            str:    Success message if the container has all OMI required annotations.
                    Failure message if any success criteria is missing.

        '''
        return_value = "Failure: Image lacks OMI required OCI annotations"

        try:
            # verify image exists and retrieve its information
            img_meta = self.client.inspect_image(self.image_id)
            labels = img_meta['Config']['Labels']
            if labels is None:
                raise TypeError("No Labels are associated with image " + self.image_id)

            for label in self.omi_required_annotations:
                if label not in labels:
                    raise ValueError("Image " + self.image_id + " missing required annotation" + label)

            self.container_port = int(labels["ml.openmodel.port"])

            return_value = "Success: Image contains all OMI required OCI annotations"

        except Exception as e:
            return_value += "\n Error Message: " + str(e)
            print("Error message:", e)

        return return_value

    def validate_gRPC(self):
        '''
        Validates that an image has the required gRPC methods through reflection.

        Args:
            None: N/A

        Returns:
            str:    Success message if the container has all OMI required gRPC calls AND they are available through reflection.
                    Failure message if any success criteria is missing.

                '''
        return_value = "Failure: OMI required gRPC methods not present."

        try:
            endpoint = self.url+":"+str(self.host_port)
            client = Client.get_by_endpoint(endpoint)

            if "ModzyModel" in client.service_names:
                model_service = client.service("ModzyModel")
                for method in self.omi_required_gRPC_methods:
                    if method not in model_service.method_names:
                        raise ValueError("gRPC server missing the following method: " + method)

            return_value = "Success: All OMI required gRPC routes available."

        except Exception as e:
            return_value += "\n Error Message: " + str(e)
            print("Error message:", e)

        return return_value



if __name__ == '__main__':
    print("Running OMI Compliance Check")
    check = OMI_check(image_id='claytondavisms/sklearn-digits:0.0.1')
    print(check.validate_image())
    print(check.start_container())
    print(check.validate_gRPC())
    print(check.clean_up())
