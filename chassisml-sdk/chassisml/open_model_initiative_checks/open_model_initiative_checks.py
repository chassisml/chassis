
import docker

class OMI_check():
    """
    The OMI_check class provides Chassisml capabilities to validate that images are meeting the OMI specification.

    """
    version = "0.0.1"
    omi_required_annotations = ["ml.openmodel.interfaces",
                                "ml.openmodel.protocols",
                                "ml.openmodel.port",
                                "ml.openml.model_name"]

    def __init__(self):
        self.client = docker.APIClient(base_url='npipe:////./pipe/docker_engine')

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




if __name__ == '__main__':
    check = OMI_check()
    check.validate_image('busybox')
    check.validate_image('8697544121c7')
