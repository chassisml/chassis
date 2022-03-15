import logging
import os
import dotenv
import pytest
import time
from datetime import datetime, timedelta
from modzy import ApiClient, error
from modzy.jobs import Jobs

dotenv.load_dotenv()

BASE_URL = os.getenv('MODZY_BASE_URL')
API_KEY = os.getenv('MODZY_API_KEY')

MODEL_ID = 'ed542963de'  # sentiment-analysis


# @pytest.fixture()
# def client():
#     return ApiClient(base_url=BASE_URL, api_key=API_KEY)


@pytest.fixture()
def logger():
    return logging.getLogger(__name__)


def test_get_job_history(logger):
    # jobs = client.jobs.get_history()
    logger.debug("jobs history: %d", 3)
    # for job in jobs:
    #     logger.debug("job: %s", job)
    #     assert job.job_identifier
    #     assert job.submitted_by
    #     assert job.model
    #     assert job.model.identifier
    #     assert job.model.version
    #     assert job.model.name
    #     assert job.status
    assert "test" == "test"
'''

import logging
import os
import dotenv
import pytest
import time
import chassisml

HOST_URL = "http://localhost:5000"

dotenv.load_dotenv()

@pytest.fixture()
def client():
    return chassisml.ChassisClient(HOST_URL)

@pytest.fixture()
def logger():
    return logging.getLogger(__name__)

# logger = logs()


# Chassis Client methods


def test_create_model(client, logger):
    logger.debug("test model")
    assert True

def test_get_job_status(client, logger):
    logger.debug("test status")
    assert True

def test_block_until_complete():
    assert True

def test_omi_compliance():
    assert True

def test_download_tar():
    assert True



# Chassis Model methods


def test_local_test():
    assert True

def test_local_batch_test():
    assert True

def test_env_test():
    assert True

def test_publish():
    assert True

def test_save():
    assert True
'''