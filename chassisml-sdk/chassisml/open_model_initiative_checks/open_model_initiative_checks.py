
import docker
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

    def __init__(self, base_url='npipe:////./pipe/docker_engine'):
        try:
            #self.client = docker.APIClient(base_url='npipe:////./pipe/docker_engine')
            self.client = docker.APIClient(base_url=base_url)
        except Exception as e:
            self.client = None
            print("Error: no Docker client available at the base url")

    def validate_image(self, image_id):
        try:
            # verify image exists and retrieve its information
            img_meta = self.client.inspect_image(image_id)
            labels = img_meta['Config']['Labels']
            if labels is None:
                raise TypeError("No Labels are associated with image " + image_id)

            for label in self.omi_required_annotations:
                if label not in labels:
                    raise ValueError("Image " + image_id + " missing required annotation" + label)

        except Exception as e:
            print("Error message:", e)

    def validate_gRPC(self, url="localhost", port="5001"):
        try:
            endpoint = url+":"+port
            client = Client.get_by_endpoint(endpoint)
            print(client.service_names)

            if "ModzyModel" in client.service_names:
                model_service = client.service("ModzyModel")
                for method in self.omi_required_gRPC_methods:
                    if method not in model_service.method_names:
                        raise ValueError("gRPC server missing the following method: " + method)
                #if ("Run" not in model_service.method_names) | ("Statuss" not in model_service.method_names) | ("Shutdown" not in model_service.method_names):
                #   raise ValueError("gRPC server missing one of the following methods: Run, Status, Shutdown")

            
        except Exception as e:
            print("Error message:", e)





if __name__ == '__main__':
    check = OMI_check()
    check.validate_image('claytondavisms/sklearn-digits:0.0.1')
    check.validate_gRPC()

