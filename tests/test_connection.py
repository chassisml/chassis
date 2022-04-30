import subprocess
import logging

logging.basicConfig(level=logging.INFO, format= '%(levelname)s: %(message)s')

def test_can_connect_to_service(host_url, logger, test_name):
    output = subprocess.run("curl {}".format(host_url), shell=True, capture_output=True)
    out = 0
    if output.stdout.decode() == "Alive!":
        logger.info(" ******** PASSED - test:{}".format(test_name))
        out = 1
    else:
        logger.info(" ******** FAILED - test:{}".format(test_name))
        logger.error(output.stdout.decode())
    return out

if __name__ == "__main__":
    out = test_can_connect_to_service()