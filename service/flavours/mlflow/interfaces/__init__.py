import os
import sys
from loguru import logger

INTERFACE = os.getenv('INTERFACE')

def start_interface_server():
    if INTERFACE == 'kfserving':
        from .kfserving import start_server
        start_server()
    else:
        logger.critical('No valid INTERFACE environment variable defined.')
        sys.exit(1)
