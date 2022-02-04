
import docker
import time
from grpc_requests import Client



class OMI_check():
    """
    The OMI_check class provides Chassisml capabilities to validate that images are meeting the OMI specification.

    """
    version = "0.0.1"
    omi_required_annotations = ["ml.openmodel.interfaces",
                                "ml.openmodel.protocols",
                                "ml.openmodel.port",
                                "ml.openml.model_name"]
    omi_required_gRPC_methods = ["Run", "Status", "Shutdown"]

    # Image ID for the image we will evaluate for OMI compliance
    image_id = None
    container = None
    container_port = None   # must be numeric
    host_port = None        # must be numeric
    url = None
    def __init__(self, base_url='npipe:////./pipe/docker_engine',
                 image_id=None,
                 container_port=45000,
                 host_port=5001,
                 url="localhost"):
        try:
            self.client = docker.APIClient(base_url=base_url)
            self.image_id = image_id
            self.container_port = container_port
            self.host_port = host_port
            self.url = url
        except Exception as e:
            self.client = None

            print("Error: no Docker client available at the base url")

    def start_container(self, timeout=20):
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
            return_value = "Success: Image contains all OMI required OCI annotations"

        except Exception as e:
            return_value += "\n Error Message: " + str(e)
            print("Error message:", e)

        return return_value

    def validate_gRPC(self):
        return_value = "Failure: OMI required gRPC routes not present."

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
