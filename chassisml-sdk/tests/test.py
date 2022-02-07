"Code for testing the Chassis SDK"

#setup the relative imports
import os
import sys
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(THIS_DIR[:-6])
import chassisml

#instantiate a client
client = chassisml.ChassisClient()

# test compliance
print(client.test_OMI_compliance(image_id='claytondavisms/sklearn-digits:0.0.1'))

