# Chassis Testing Suite

This subdirectory contains the test suite for Chassisml, and this page provides an overview of the tests and usage instructions.

## Directory Contents

* `utils/`: Utility folder that contains sample data for each model to be tested
* `requirements.txt`: Requirements file containing all test suite dependencies
* `test_connection.py`: Tests connection to the Chassisml service based on a user-specified URL (if deployed locally, this URL will be "http://localhost:5000")
* `test_sdk.py`: Contains tests for every method available in the Chassisml SDK, which in turn covers every method and endpoint in the service.
* `test.py`: Driver script that defines model requirements and kicks off the tests (importing test methods from `test_connection.py` and `test_sdk.py`)

## Usage

**Before starting the test suite you must first define the following Environment Variables**

DOCKER_USER
DOCKER_PASS


To kickoff the test suite, you must first create a virtual environment and install the dependencies listed in `requirements.txt` within this directory.

`python -m venv test-suite`

Activate the environment and use pip to install the dependencies.

_Linux/Mac OS_
`source test-suite/bin/activate`

_Windows_
`.\test-suite\Scripts\activate`

`pip install -r requirements.txt`

Run the test script as a python module from the parent level of this repository.

```
cd ..
python -m tests.test
```
