import json
import logging
import os
import unittest

from app import app
from flask_psc_model.testing import AutoAppTestCase

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
EXAMPLE_DATA_DIR = os.path.join(THIS_DIR, 'data', 'example')
VALIDATION_ERROR_DATA_DIR = os.path.join(THIS_DIR, 'data', 'validation-error')


class TestApp(AutoAppTestCase):
    #: the filename that will contain expected error messages
    error_message_filename = 'message.txt'

    def create_app(self):
        """Configure the app for testing"""
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.logger.setLevel(logging.DEBUG)
        return app

    def test_sanity(self):
        """Test that basic things are working in the app"""
        self.check_sanity()

    def test_example_cases(self):
        """Tests that valid model inputs return the expected results.

        See `check_example_cases` for more details.

        Test cases in your example data directory should at minimum include:
            - a representative set of possible input files
            - edge cases (e.g. empty text, emoji text, 1 pixel images, images with alpha channel, etc -- if these
              are not considered errors)
            - tests of the "largest" inputs the model is prepared to handle (e.g. longest text, max image size, etc)
        """
        self.check_example_cases(EXAMPLE_DATA_DIR)

    def check_results(self, actual, expected):
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

        Instead we override this function with our own custom logic to parse the JSON and compare the results.
        """
        actual = json.loads(actual.decode('utf-8'))  # in Python<3.6 `json.loads` does not handle `bytes`
        expected = json.loads(expected.decode('utf-8'))
        self.assertEqual(actual, expected, 'actual JSON does not match expected JSON')

    def test_validation_error_cases(self):
        """Tests that invalid inputs return the expected error messages.

        See `check_validation_error_cases` for more details.

        Test cases in your validation error data directory should at minimum include:
        - input files of an incorrect type (e.g. invalid utf-8 text when the model requires utf-8 text, a text file
          when the model requires an image file, etc)
        - input files of the correct type but with invalid values (e.g. a JSON file that is valid JSON but does not
          contain the required keys and values, etc)
        - inputs that are too "large" or too "small" (e.g. text that is too long, empty text when some text is
          required, an image file with overly large dimensions, etc)
        """
        self.check_validation_error_cases(VALIDATION_ERROR_DATA_DIR)

    def check_validation_error_message(self, actual, expected):
        """Asserts that a single actual validation error message matches the corresponding
        expected message text. This function is used by `check_validation_error_cases` to check
        that a single test cases passes.

        By default the check passes if the expected message is case-insensitively contained within
        the actual message. This means that the full error message does not need to be specified,
        only a snippet of important text.

        Replace the call to the default super function with your own custom logic if needed.
        """
        super().check_validation_error_message(actual, expected)


if __name__ == '__main__':
    unittest.main()
