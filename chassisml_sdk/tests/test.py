"Code for testing the Chassis SDK"

#setup the relative imports
import os
import sys
# from chassis.tests.test_sdk import test_block_until_complete
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(THIS_DIR[:-6])
import chassisml

import docker
docker_client = docker.from_env()
with open(os.path.join(THIS_DIR, "output-sample.tar"), "rb") as f:
    image_repo_tag = docker_client.images.load(f)[0].attrs["RepoTags"][0]

# add command line argument parser for user to pass image id as parameter through CLI
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("image_id", default=None, help="Local docker image ID to test in the format dockerusername/repositoryname:tag")

args = parser.parse_args()

#instantiate a client
client = chassisml.ChassisClient()

# test compliance
test_output = client.test_OMI_compliance(image_id=image_repo_tag)
print(test_output, type(test_output), test_output[0], type(test_output[1]))

