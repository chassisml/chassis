import os
from .common import MLFlowFlavour

# XXX
INTERFACE = os.getenv('INTERFACE') or 'kfserving'

def get_blueprint():
    if INTERFACE == 'kfserving':
        from .kfserving import kfserving_blueprint
        return kfserving_blueprint
