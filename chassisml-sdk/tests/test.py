"Code for testing the Chassis SDK"

#setup the relative imports
import os
import sys
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(THIS_DIR[:-6])
import chassisml

# add command line argument parser for user to pass image id as parameter through CLI
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("image_id", default=None, help="Local docker image ID to test in the format dockerusername/repositoryname:tag")

args = parser.parse_args()

#instantiate a client
client = chassisml.ChassisClient()

# test compliance
print(client.test_OMI_compliance(image_id=args.image_id))

