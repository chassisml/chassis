import unittest

from model_lib.model import FactorizationMachines
from flask_psc_model import ModelBase


class TestModel(unittest.TestCase):

    def setUp(self):
        self.model = FactorizationMachines()

    def test_model_is_model_base_instance(self):
        self.assertIsInstance(self.model, ModelBase)

    def test_prediction(self):
        pass

if __name__ == '__main__':
    unittest.main()
