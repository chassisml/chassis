import os
import sys
from loguru import logger

INTERFACE = os.getenv('INTERFACE')


def start_interface_server():
    if INTERFACE == 'kserve':
        from .kserve import start_server
        start_server()
    elif INTERFACE == 'modzy':
        from .modzy.grpc_model.src.model_server import serve
        serve()
    else:
        logger.critical('No valid INTERFACE environment variable defined.')
        sys.exit(1)
