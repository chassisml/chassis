import os
import shutil
import unittest
import itertools
from contextlib import ExitStack
from tempfile import TemporaryDirectory
from unittest import mock

from werkzeug.http import HTTP_STATUS_CODES

from ._api import ModelCache
from ._interface import ModelBase
from ._util import listify, stripext, classname


class AppTestCase(unittest.TestCase):
    """Utility base class for writing application tests.

    The `AutoAppTestCase` can be used instead in most cases.

    Inspired in part by: https://github.com/jarus/flask-testing
    """

    def create_app(self):
        """Create and configure the Flask app.

        Subclasses must implement this function and return a Flask instance.

        The `app.logger` will be disabled by default. If you need to test logging
        you may set `self.app.logger.enabled = True` in your unit test function.
        """
        raise NotImplementedError

    def run(self, *args, **kwargs):
        """Do any setup. Doing it here means users don't have to remember to call
        super().setUp() in subclasses.
        """
        try:
            self._pre_set_up()
            super().run(*args, **kwargs)
        finally:
            self._post_set_up()

    def _pre_set_up(self):
        self.app = self.create_app()
        self.client = self.app.test_client()

    def _post_set_up(self):
        if getattr(self, 'app', None) is not None:
            del self.app
        if getattr(self, 'client', None) is not None:
            del self.client

    def run_test_job(self, inputs, string_encoding='utf-8'):
        """Run a job against the application and collect any results using a temporary directory.

        The `inputs` should be a `dict` mapping filename to the input data for that file. The data can
        be a `bytes`, `str`, or file-like object. The `string_encoding` parameter will be used to encode
        `str` data when writing to file.

        The function will return a tuple of `(response, results)`. The `response` will be a Flask `Response`
        object and the results will be a `dict` of mapping output filename to `bytes` objects containing
        the raw bytes of any files output to the output directory.

        For example, a subclass might use this utility to implement an application specific function to run
        a test job with two inputs that decodes an output as json as follows:
        ```
        def run_test_job(self, input_data1, input_data2):
            # This model expects two input files named 'input1' and 'input2' and writes out an
            # output files named 'output.json'.
            # The raw `bytes` from the 'output.json' file will be decoded using `json.loads`.
            import json
            response, results = super().run_test_job(
                {'input1': input_data1, 'input2': input_data2}
            )
            result = results.get('output.json')
            if result is not None:
                result = json.loads(result)
            return response, result
        ```
        """
        response = self.client.get('/status')
        self.assertEqual(response.status_code, 200, 'GET /status failed')

        with TemporaryDirectory() as input_tempdir, TemporaryDirectory() as output_tempdir:
            for filename, datum in inputs.items():
                if datum is None:
                    continue

                input_path = os.path.join(input_tempdir, filename)

                if isinstance(datum, str):
                    datum = datum.encode(string_encoding)

                with open(input_path, mode='wb') as input_file:
                    try:
                        input_file.write(datum)
                    except TypeError:
                        shutil.copyfileobj(datum, input_file)

            body = {
                'type': 'file',
                'input': input_tempdir,
                'output': output_tempdir,
            }
            response = self.client.post('/run', json=body)

            results = {}
            for filename in os.listdir(output_tempdir):
                output_path = os.path.join(output_tempdir, filename)
                self.assertTrue(os.path.isfile(output_path), 'output must be file not directory')

                with open(output_path, mode='rb') as output_file:
                    result = output_file.read()

                results[filename] = result

        return response, results

    def assertResponse(self, response, status_code, status=None, message=None):
        """Assert that a response has a given `status_code`.

        You may specify a specific `status` and `message` to check for, or a callable
        that returns None or a truthy value to indicate success. Otherwise by default
        `status` is checked against the standard HTTP status text, and a `message` is
        simply checked to exist.
        """
        self.assertEqual(response.status_code, status_code, 'response status does not match')
        self.assertEqual(response.content_type, 'application/json', 'response content type must be json')

        body = response.get_json()
        self.assertEqual(body['statusCode'], status_code, 'response body "statusCode" does not match')

        if status is None:
            status = HTTP_STATUS_CODES.get(status_code, None)
        if status is None:
            # some status... any status ...
            self.assertTrue(isinstance(body['status'], str) and body['status'],
                            'response body "status" must be a non-empty string')
        elif callable(status):
            test = status(body['status'])
            if test is not None:
                self.assertTrue(test, 'response body "status" does not match')
        else:
            self.assertEqual(body['status'], status, 'response body "status" does not match')

        if message is None:
            # some message... any message ...
            self.assertTrue(isinstance(body['message'], str) and body['message'],
                            'response body "message" must be a non-empty string')
        elif callable(message):
            test = message(body['message'])
            if test is not None:
                self.assertTrue(message(body['message']), 'response body "message" does not match')
        else:
            self.assertEqual(body['message'], message, 'response body "message" does not match')

    def assertSuccessResponse(self, response):
        """Assert that a response represents a successful run.
        This corresponds to a 200 HTTP status.
        """
        self.assertResponse(response, 200)

    def assertAcceptedResponse(self, response):
        """Assert that a response represents that a request has been received.
        This corresponds to a 202 HTTP status.

        Generally this should not be needed outside of the tests already provided
        by the `sanity_check` function.
        """
        self.assertResponse(response, 202)

    def assertClientErrorResponse(self, response, message=None):
        """Assert that a response represents a client error (i.e. an invalid
        job configuration). This corresponds to a 400 HTTP status.

        You may specify a specific error `message` to check for, or provide a
        callable that returns `bool` indicating a match. Otherwise by default
        it is simply checked that an error message exists.

        Generally this should not be needed outside of the tests already provided
        by the `sanity_check` function.
        """
        self.assertResponse(response, 400, message=message)

    def assertMediaTypeErrorResponse(self, response, message=None):
        """Assert that a response represents a client error. This corresponds to
        a 415 HTTP status.

        You may specify a specific error `message` to check for, or provide a
        callable that returns `bool` indicating a match. Otherwise by default
        it is simply checked that an error message exists.

        Generally this should not be needed outside of the tests provided by
        the `sanity_check` function.
        """
        self.assertResponse(response, 415, message=message)

    def assertValidationErrorResponse(self, response, message=None):
        """Assert that a response represents a model validation error against
        the supplied input files.

        You may specify a specific error `message` to check for, or provide a
        callable that returns `bool` indicating a match. Otherwise by default
        it is simply checked that an error message exists.
        """
        self.assertResponse(response, 422, message=message)

    def check_sanity(self):
        """Run some basic sanity checks on the app.

        This includes checking that `/status` returns a success response and that basic validation
        is performed by the `/run` route on invalid job configurations.

        It is suggested that subclasses use this as part of a sanity test:
        ```
        def test_sanity(self):
            self.check_sanity()
        ```
        """
        self._check_sanity_status()
        self._check_sanity_shutdown()
        self._check_sanity_run()

    def _check_sanity_status(self):
        """Run some basic sanity checks on the `/status` route."""
        response = self.client.get('/status')
        self.assertSuccessResponse(response)

    def _check_sanity_shutdown(self):
        """Run some basic sanity checks on the `/shutdown` route."""
        # mock the shutdown function so we don't self terminate during unit tests
        mock_shutdown_function = mock.Mock()
        with mock.patch('flask_psc_model._api.get_shutdown_function', return_value=mock_shutdown_function):
            response = self.client.post('/shutdown')
            self.assertAcceptedResponse(response)

            # TODO: how to test `/shutdown` route actually results in a termination with exit code 0?
            self.assertTrue(mock_shutdown_function.called, 'shutdown function was not called')

    def _check_sanity_run(self):
        """Run some basic sanity checks on the `/run` route."""
        response = self.client.post('/run', data=None, mimetype='application/json')
        self.assertClientErrorResponse(response)

        response = self.client.post('/run', json={"cat": "dog"})
        self.assertClientErrorResponse(response)

        response = self.client.post('/run', data='cats and dogs', mimetype='application/json')
        self.assertClientErrorResponse(response)

        response = self.client.post('/run', data='cats and dogs', mimetype='text/plain')
        self.assertMediaTypeErrorResponse(response)

        response = self.client.post('/run', json={'type': 'file', 'input': os.devnull,
                                                  'output': os.devnull}, content_type='text/plain')
        self.assertClientErrorResponse(response)

    # TODO: more comprehensive test suite


class AutoAppTestCase(AppTestCase):
    """Utility class for writing application tests that can automatically be run against a
    collection of file based test cases.
    """

    #: encoding to use when interacting with text files (text inputs, json, error messages, etc)
    text_encoding = 'utf-8'

    #: the filename that will contain expected error messages
    error_message_filename = 'message.txt'

    #: a list of input filenames; if `None` they will be read from the model factory class if possible
    input_filenames = None

    #: a list of output filenames; if `None` they will be read from the model factory class if possible
    output_filenames = None

    def _pre_set_up(self):
        super()._pre_set_up()

        # TODO: should we attempt to read expected filenames (and more?) from the `model.yaml` file instead?
        #       instantiating a model instance here outside of the `/status` lifecycle is a bad idea since the
        #       model instances cannot be relied on to clean themselves up properly; however, attempting
        #       to read from the model factory itself like below can be problematic if the factory is not a class
        #       or the properties are not defined at the class level... or if they are defined at the class
        #       level but then altered during instance constructions we will have read the wrong values
        if self.input_filenames is None or self.output_filenames is None:
            # attempt to lookup the input/output filenames from the configured model
            with self.app.app_context():
                factory = ModelCache.get_factory()
            try:
                is_modelbase = issubclass(factory, ModelBase)
            except Exception:
                is_modelbase = False
            if not is_modelbase:
                raise ValueError('model factory `%s` is not a subclass of `%s`; unable to determine '
                                 '"input_filenames" and "output_filenames", they must be set manually '
                                 'as attributes of `%s`'
                                 % (classname(factory), classname(ModelBase), classname(self)))
            if self.input_filenames is None:
                input_filenames = listify(factory.input_filenames)
                try:
                    if not isinstance(next(iter(input_filenames)), str):
                        raise ValueError('unable to determine "input_filenames" from the model factory '
                                         '`%s`, it must be set manually as an attribute of `%s`'
                                         % (classname(factory), classname(self)))
                except StopIteration:
                    pass
                self.input_filenames = input_filenames
            if self.output_filenames is None:
                output_filenames = listify(factory.output_filenames)
                try:
                    if not isinstance(next(iter(output_filenames)), str):
                        raise ValueError('unable to determine "output_filenames" from the model factory '
                                         '`%s`, it must be set manually as an attribute of `%s`'
                                         % (classname(factory), classname(self)))
                except StopIteration:
                    pass
                self.output_filenames = output_filenames

        self.input_filenames = listify(self.input_filenames)
        if len(self.input_filenames) < 1:
            raise ValueError('there must be at least one input filename')
        self.output_filenames = listify(self.output_filenames)
        if len(self.output_filenames) < 1:
            raise ValueError('there must be at least one output filename')

        self._check_confusable_filenames(self.error_message_filename,
                                         *itertools.chain(self.input_filenames, self.output_filenames))

    def _check_confusable_filenames(self, *filenames):
        # we need filenames to not be confusable (i.e. not only differ in file extension) in order to
        # walk the test file directories but it is also likely useful to our end users that this is true
        def _err(filename):
            error = ('the filename "%s" is confusable with other input or output filenames; '
                     'use a unique filename that does not differ only by file extension' % (filename,))
            if filename == self.error_message_filename:
                error += ('\nto use a different filename for expected error message text, set '
                          '`%s.error_message_filename` to the preferred value' % classname(self))
            raise ValueError(error)

        filename_set = set()
        for filename in filenames:
            if filename in filename_set:
                _err(filename)
            filename_noext = stripext(filename)
            if filename_noext in filename_set:
                _err(filename)
            filename_set.add(filename)
            filename_set.add(filename_noext)

    def run_test_job(self, *inputs):
        """Run a job against the application and collect any results using a temporary directory.

        The `inputs` should be a the input data in the order specified by the model's `input_filenames`.
        The data can be `bytes`, `str`, or file-like objects. The `text_encoding` parameter of this class
        will be used to encode `str` data when writing to file.

        The function will return a tuple of `(response, result1, result2, ...)`. The `response` will be a
        Flask `Response` the results will be `bytes` objects containing the raw bytes of the results files
        in the order specified by the model's `output_filenames`.

        For example:
        ```
        # if our model class is defined as:
        class MyModel(ModelBase):
            input_filenames = ['a.txt', 'b.txt']
            output_filenames = ['y.json', 'z.json']
            ...

        # then we can use this function as:
        response, result_y, result_z = self.run_test_job(input_a, input_b)
        ```
        """
        if len(inputs) != len(self.input_filenames):
            raise ValueError('the number of inputs must match the number of model input filenames')
        input_map = {filename: data for filename, data in zip(self.input_filenames, inputs)}
        response, results = super().run_test_job(input_map, string_encoding=self.text_encoding)
        flat_results = (results.get(filename) for filename in self.output_filenames)
        return tuple(itertools.chain((response,), flat_results))

    def check_example_cases(self, data_dir):
        """Checks that valid model inputs return the expected results.

        The subdirectories of the provided `data_dir` will be used as example test cases. Each subdirectory
        should contain a set of valid input files and the expected result files.

        The expected filenames are determined by the model's `input_filenames` and `output_filenames` values.
        To provide some flexibility, this function will look in the test case directory for a file with the given
        filename (with or without any file extensions), or for a directory with a matching filename (with or
        without any file extensions) containing a single file. For example, an "input.txt" input file may be
        located at any of the following locations relative to the test case subdirectory:
            - input.txt
            - input
            - input.txt/any-filename
            - input/any-filename

        Any set of model `input_filenames` and `output_filenames` that contains filenames that are exact matches
        or differ only by file extension will be rejected as they cannot be distinguished. These confusable
        filenames may also confuse users of your model, not just this test function :)

        For each test case, the input files found in the subdirectory will be run through the application and
        the actual results from the model run will be compared against the results files found in the same
        subdirectory. The `check_results` function will be used to check that each individual test case results
        match expected results.
        """
        case_count = 0
        for casename, filepath_map in walk_test_data_dir(data_dir, strip_ext=True):
            case_count += 1
            with self.subTest(casename):
                with ExitStack() as stack:
                    inputs = []
                    for filename in self.input_filenames:
                        filepath = filepath_map.get(filename, filepath_map.get(stripext(filename)))
                        if not filepath:
                            raise ValueError('data directory "%s" missing input file "%s"' % (casename, filename))
                        file = open(filepath, 'rb')
                        stack.enter_context(file)
                        inputs.append(file)
                    response, *results = self.run_test_job(*inputs)
                self.assertSuccessResponse(response)

                expected_results = []
                for filename in self.output_filenames:
                    filepath = filepath_map.get(filename, filepath_map.get(stripext(filename)))
                    if not filepath:
                        raise ValueError('data directory "%s" missing results file "%s"' % (casename, filename))
                    with open(filepath, 'rb') as file:
                        result = file.read()
                    expected_results.append(result)
                self.check_results(*itertools.chain(results, expected_results))

        self.assertGreater(case_count, 0, 'no test cases were found in: %s' % (data_dir,))

    def check_results(self, *results):
        """Asserts that a single set of actual results matches the corresponding expected results. This function
        is used by `check_example_cases` to check that a single test cases passes.

        All actual results will be passed to the function in the order specified by the model's `output_filenames`
        followed by all expected file results in the order specified by the model's `output_filenames`. These values
        will be `bytes` objects.

        For example:
        ```
        # if our model class is defined as:
        class MyModel(ModelBase):
            output_filenames = ['y.json', 'z.json']
            ...

        # then this function will be called with parameters like:
        self.check_results(actual_y, actual_z, expected_y, expected_z)
        ```

        By default the check passes if all actual results are equal to expected (as determined by the `==` operator).

        Override this function to use custom criteria. This is likely needed if you do not want to use binary equality
        as the test criteria.
        """
        actual_results = results[len(results)//2:]
        expected_results = results[:len(results)//2]
        for actual_result, expected_result in zip(actual_results, expected_results):
            self.assertEqual(actual_result, expected_result, 'actual result does not match expected result')

    def check_validation_error_cases(self, data_dir):
        """Checks that invalid inputs return the expected error messages.

        The subdirectories of the provided `data_dir` will be used as example test cases. Each subdirectory
        should contain a set of invalid input files (i.e. inputs that you do not expect the model to be able run
        successfully) and the expected error messages. By default the error message text file should be named
        "message.txt"; this filename may be changed by setting this class's `error_message_filename` attribute.

        The expected filenames are determined by the model's `input_filenames` and this class's
        `error_message_filename` attribute ("message.txt" by default). To provide some flexibility, this function
        will look in the test case directory for a file with the given filename (with or without any file extensions),
        or for a directory with a matching filename (with or without any file extensions) containing a single file.
        For example, an "message.txt" input file may be located at any of the following locations relative to the test
        case subdirectory:
            - message.txt
            - message
            - message.txt/any-filename
            - message/any-filename

        Any set of model `input_filenames`, `output_filenames`, and this class's `error_message_filename` that
        contains filenames that are exact matches or differ only by file extension will be rejected as they cannot be
        distinguished. These confusable filenames may also confuse users of your model, not just this test function :)

        For each test case, the input files found in the subdirectory will be run through the application and
        the error message returned by the model run will be compared against the error message file found in the same
        subdirectory. The `check_validation_error_message` function will be used to check that each individual test
        case message matches the expected message.
        """
        case_count = 0
        for casename, filepath_map in walk_test_data_dir(data_dir, strip_ext=True):
            case_count += 1
            with self.subTest(casename):
                with ExitStack() as stack:
                    inputs = []
                    for filename in self.input_filenames:
                        filepath = filepath_map.get(filename, filepath_map.get(stripext(filename)))
                        if not filepath:
                            raise ValueError('data directory "%s" missing input file "%s"' % (casename, filename))
                        file = open(filepath, 'rb')
                        stack.enter_context(file)
                        inputs.append(file)
                    response, *_ = self.run_test_job(*inputs)

                message_path = filepath_map.get(self.error_message_filename,
                                                filepath_map.get(stripext(self.error_message_filename)))
                if not message_path:
                    raise ValueError('data directory "%s" missing expected message file "%s"'
                                     % (casename, self.error_message_filename))
                with open(message_path, 'r', encoding=self.text_encoding) as file:
                    expected_error_message = file.read()

                def _check_message(message):
                    self.check_validation_error_message(message, expected_error_message)

                self.assertValidationErrorResponse(response, message=_check_message)

        self.assertGreater(case_count, 0, 'no test cases were found in: %s' % (data_dir,))

    def check_validation_error_message(self, actual_message, expected_message):
        """Asserts that a single actual validation error message matches the corresponding
        expected message text. This function is used by `check_validation_error_cases` to check
        that a single test cases passes.

        By default the check passes if the expected message is case-insensitively contained within
        the actual message. This means that the full error message does not need to be specified,
        only a snippet of important text.

        Override this function to use custom criteria.
        """
        self.assertIn(expected_message.strip().lower(), actual_message.strip().lower(),
                      'response body "message" does not match')


def walk_test_data_dir(path, strip_ext=False):
    """Walks a test data directory tree and yields tuples containing (casename, filepath_map).

    The first level of the directory tree identifies the name of a given test case and will be
    returned as `casename`.

    Every regular file found within the `casename` directory will be added to the `filepath_map`
    with the filename used as key and the value set to the full path to the file.
    Every directory found within the `casename` directory must contain exactly one file, and the
    directory name will be used as key and the value set to the full path to that nested file.

    Any filename extension will be removed from the key names in the `filepath_map` if `strip_ext`
    is set to True. This would allow e.g. both "image.png" and "image.jpg" to be used for the
    "image" file without requiring them to be nested inside a directory.

    For example, if the directory is laid out as follows:
    ```
    path
    ├── test-case-name-1
    │   ├── input.txt
    │   └── output.json
    ├── test-case-name-2
    │   ├── input.txt
    │   │   └── test-2.txt
    │   └── output.json
    │       └── test-2-results.json
    ```

    This function will yield:
    ```
    (
        ("test-case-name-1", {
            "input": "path/test-case-name-2/input.txt",
            "output": "path/test-case-name-2/output.json",
        }),
        ("test-case-name-2", {
            "input": "path/test-case-name-1/input.txt/test-2.txt",
            "output": "path/test-case-name-1/output.json/test-2-results.json",
        })
    )
    ```
    """
    for casename in os.listdir(path):
        casepath = os.path.join(path, casename)
        if not os.path.isdir(casepath):
            continue
        filepath_map = {}
        for dataname in os.listdir(casepath):
            datapath = os.path.join(casepath, dataname)
            if os.path.isdir(datapath):  # directory
                filenames = os.listdir(datapath)
                if len(filenames) != 1:
                    raise ValueError("test case file directory must contain exactly one file: %s" % (datapath,))
                filepath = os.path.join(datapath, filenames[0])
            else:  # file
                filepath = datapath

            key = dataname if not strip_ext else os.path.splitext(dataname)[0]
            filepath_map[key] = filepath

        yield (casename, filepath_map)
