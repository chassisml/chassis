import math
import os

from humanfriendly import parse_timespan

from flask_psc_model import load_metadata


def _load_timeout():
    """Load the maximum timeout value from the `model.yaml` metadata file."""
    metadata = load_metadata(__file__)
    max_timeout = max(
        map(lambda timeout_: math.ceil(parse_timespan(str(timeout_))), metadata.timeout.values())
    )
    return max_timeout


# server socket
bind = ':%s' % os.environ.get('PSC_MODEL_PORT', '45000')

# timeout
timeout = _load_timeout()

# logging
logconfig_dict = dict(  # setup gunicorn and flask_psc_model logging
    version=1,
    disable_existing_loggers=False,
    root={"level": "INFO", "handlers": ["error_console"]},
    loggers={
        "gunicorn.error": {
            "level": "INFO",
            "handlers": ["error_console"],
            "propagate": False,
            "qualname": "gunicorn.error"
        },
        "gunicorn.access": {
            "level": "INFO",
            "handlers": ["error_console"],
            "propagate": False,
            "qualname": "gunicorn.access"
        },
        "flask_psc_model": {
            "level": "INFO",
            "handlers": ["error_console"],
            "propagate": False,
            "qualname": "flask_psc_model"
        },
    },
    handlers={
        "error_console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": "ext://sys.stderr"
        },
    },
    formatters={
        "generic": {
            "format": "%(asctime)s [%(process)d] [%(levelname)s] [%(name)s] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter"
        },
    }
)
