import itertools
import os
import signal
from threading import Lock

from flask import Blueprint, abort, current_app, jsonify, request
from werkzeug.exceptions import HTTPException, InternalServerError
from werkzeug.http import HTTP_STATUS_CODES
from werkzeug.utils import import_string

from ._interface import ModelBase
from ._util import filepaths_are_equivalent, classname, listify


api = Blueprint('model_api', __name__)


class ModelWrapper:
    """Add some utilities to the model instance."""

    def __init__(self, model):
        """Create a new `ModelWrapper` instance."""
        self._model = model
        self._run_lock = Lock()

    def __str__(self):
        return self._model.__str__()

    def get_inputs(self, input_dir):
        """Get the list of absolute input file paths expected by the model."""
        inputs = listify(self._model.input_filenames)
        inputs = [os.path.abspath(os.path.join(str(input_dir), filename)) for filename in inputs]
        return inputs

    def get_outputs(self, output_dir):
        """Get the list of absolute output file paths expected by the model."""
        outputs = listify(self._model.output_filenames)
        outputs = [os.path.abspath(os.path.join(str(output_dir), filename)) for filename in outputs]
        return outputs

    def run(self, input_dir, output_dir):
        """Proxy `model.run()`."""
        # the app shouldn't be run in a multithreaded environment but we will try to protect a
        # model instance from being run from multiple threads in the case that it is
        with self._run_lock:
            filepaths = self.get_inputs(input_dir) + self.get_outputs(output_dir)
            current_app.logger.info('Executing %s.run with filepath args: %s', classname(self._model), filepaths)
            self._model.run(*filepaths)

    @property
    def input_filenames(self):
        """Read-only proxy `model.input_filenames`."""
        return listify(self._model.input_filenames)

    @property
    def output_filenames(self):
        """Read-only proxy `model.output_filenames`."""
        return listify(self._model.output_filenames)

    @property
    def validation_exception_class(self):
        """Read-only proxy `model.validation_exception_class`."""
        return self._model.validation_exception_class

    @property
    def io_exception_class(self):
        """Read-only proxy `model.io_exception_class`."""
        return self._model.io_exception_class


class ModelCache:
    """A singleton for holding the single model instances."""
    _cache = {}
    _cache_lock = Lock()

    @classmethod
    def get_instance(cls):
        """Get the lazily loaded model instance."""
        # the app shouldn't be run in a multithreaded environment but we will try to protect against
        # multiple model instance instantiation from multiple threads in the case that it is
        with cls._cache_lock:
            factory = cls.get_factory()
            instance = cls._cache.get(factory)
            if instance is None:
                instance = cls._construct_model(factory)
                instance = ModelWrapper(instance)
                cls._cache[factory] = instance
            return instance

    @classmethod
    def get_factory(cls):
        """Get the model factory."""
        factory = current_app.config.get('PSC_MODEL_FACTORY', None)
        if factory is None:
            raise ValueError('the PSC_MODEL_FACTORY application configuration value must be set')
        if not callable(factory):
            factory = import_string(factory)
        return factory

    @classmethod
    def _construct_model(cls, factory):
        """Construct an instance of the configured model."""
        if not callable(factory):
            factory = import_string(factory)
        model = factory()
        if model is None:
            raise ValueError('model factory must return a model instance')

        current_app.logger.info('Created model instance: %s', classname(model))

        if not isinstance(model, ModelBase):
            # we will warn instead of raising an exception because the model instance can
            # theoretically still work even if not an instance of ModelBase
            current_app.logger.warn('Model classes should inherit from: %s' % classname(ModelBase))
        return model


def terminate_process_group():
    """Attempts to shutdown the entire process group for this worker process by sending
    a `SIGTERM` signal to the current process group (or `CTRL_C_EVENT` on Windows). If
    running with the Werkzeug development server, the Werkzeug shutdown function will
    be called instead.

    This is in order to handle forking webservers where exiting this process won't
    lead to the shutdown of the webserver.

    This may not work if forked webserver workers change their process group or if the
    webserver does not handle the `SIGTERM` signal by shutting down. It is known to work
    with Gunicorn. It does NOT work correctly with Waitress or Tornado.
    """
    werkzeug_shutdown = request.environ.get('werkzeug.server.shutdown')
    if werkzeug_shutdown is not None:
        werkzeug_shutdown()
    else:
        if hasattr(signal, 'CTRL_C_EVENT'):  # windows
            # CTRL_C_EVENT will raise the signal in the whole process group
            os.kill(os.getpid(), signal.CTRL_C_EVENT)
        else:  # unix
            # send signal to all processes in current process group
            os.kill(0, signal.SIGTERM)


def get_shutdown_function():
    """Get the shutdown function."""
    shutdown_function = current_app.config.get('PSC_SHUTDOWN_FUNCTION', terminate_process_group)
    if not callable(shutdown_function):
        shutdown_function = import_string(shutdown_function)
    return shutdown_function


def abort_if_input_output_filename(ex, inputs, outputs):
    """Abort appropriately if exception filename references an input or output."""
    filename = getattr(ex, 'filename', None)
    if not filename:
        current_app.logger.error('Model raised %s IO exception', classname(ex), exc_info=True)
        abort(400, str(filename))

    # TODO: is this attempt to introspect `filename` a terrible idea?
    #       this attempts to allow unrelated IOError exceptions to abort with 500 error
    for input_path in itertools.chain(inputs, outputs):
        if filepaths_are_equivalent(input_path, filename):
            current_app.logger.error('Model raised %s IO exception for file: %s',
                                     classname(ex), input_path, exc_info=True)
            abort(400, str(ex))


def make_json_response(message, status_code=200, status=None):
    """Convenience function to create standard JSON response."""
    if status is None:
        status = HTTP_STATUS_CODES.get(status_code, '')
    response = jsonify(message=message, statusCode=status_code, status=status)
    response.status_code = status_code
    return response


@api.route('/status', methods=['GET'])
def status():
    """Get the model status.

    The `/status` route should do any model initialization (if needed) and return 200 success
    if the model has been loaded successfully and is ready to be run, otherwise error.
    """
    current_app.logger.info('Route `%s` getting model instance', request.path)
    ModelCache.get_instance()
    return make_json_response(message='ready')


@api.route('/run', methods=['POST'])
def run():
    """Run the model inference.

    The `/run` route should accept the json job configuration payload, read the model inputs from
    the specified filesystem directory and write the resulting outputs to the specified filesystem
    directory. It should return 200 success if the model run completed successfully, otherwise error.

    {
        "type": "file",
        "input": "/path/to/input/directory",
        "output": "/path/to/output/directory"
    }

    The individual filenames used by the model as inputs and outputs within the directories should be
    specified in the `model.yaml` metadata file.
    """
    job = request.get_json(force=True, silent=True)

    current_app.logger.info('Route `%s` received job: %s', request.url_rule, job)

    if not isinstance(job, dict):
        if request.mimetype != 'application/json':
            abort(415, 'expected "application/json" encoded data')
        abort(400, 'invalid "application/json" encoded data')

    job_type = job.get('type')
    if job_type != 'file':
        abort(400, 'this model job configuration only supports the "file" type')

    job_input_dir = job.get('input')
    if not isinstance(job_input_dir, str):  # covers None
        abort(400, 'this model job configuration expects an input filepath')

    job_output_dir = job.get('output')
    if not isinstance(job_output_dir, str):  # covers None
        abort(400, 'this model job configuration expects an output filepath')
    try:
        os.makedirs(job_output_dir, exist_ok=True)
    except IOError:
        abort(400, 'unable to create output directory: "%s"' % (job_output_dir,))

    model = ModelCache.get_instance()

    job_input_files = model.get_inputs(job_input_dir)
    for input in job_input_files:
        if not os.path.exists(input):
            abort(400, 'expected input file does not exist: "%s"' % (input,))

    job_output_files = model.get_outputs(job_output_dir)

    try:
        model.run(job_input_dir, job_output_dir)
    except model.validation_exception_class as ex:
        current_app.logger.warning('Model raised %s validation exception', classname(ex), exc_info=True)
        abort(422, str(ex))
    except model.io_exception_class as ex:
        abort_if_input_output_filename(ex, job_input_files, job_output_files)
        raise

    for output in job_output_files:
        if not os.path.exists(output):
            abort(500, 'expected model output was not written: "%s"' % (output,))

    return make_json_response(message='success')


@api.route('/shutdown', methods=['POST'])
def shutdown():
    """Shutdown the webserver and exit.

    This should result in the container process exiting with exit code 0.

    This route may or may not return a response before the process terminates,
    resulting in a dropped connection.
    """
    current_app.logger.info('Route `%s` received shutdown request', request.path)

    shutdown_function = get_shutdown_function()
    current_app.logger.info('Calling shutdown function: %s', classname(shutdown_function))
    shutdown_function()

    return make_json_response(message='exiting', status_code=202)


@api.app_errorhandler(Exception)
def errorhandler(exception):
    """Converts any errors to json response."""
    try:
        code = int(exception.code)
        name = getattr(exception, 'name', None)
        description = str(exception.description)
    except (AttributeError, ValueError):
        code = 500
        name = None
        description = str(exception) or 'server error'

    if isinstance(exception, InternalServerError) or not isinstance(exception, HTTPException):
        current_app.logger.error('Unexpected exception', exc_info=True)
    else:
        current_app.logger.warning('Exception handled: %s', exception)

    return make_json_response(message=description, status_code=code, status=name)


@api.after_request
def after_request(response):
    """Log every successful response."""
    current_app.logger.info('Route `%s` response: %s', request.path, response.json)
    return response
