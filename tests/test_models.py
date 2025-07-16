# test_models.py

import unittest
from src.shared.utils.model_utils import load_model, predict

class TestModelUtils(unittest.TestCase):

    def setUp(self):
        self.model_name = 'distilgpt2'
        self.model = load_model(self.model_name)

    def test_load_model(self):
        self.assertIsNotNone(self.model, "Model should be loaded successfully.")

    def test_predict(self):
        input_text = "In the future, AI will"
        output = predict(self.model, input_text)
        self.assertIsInstance(output, str, "Output should be a string.")
        self.assertGreater(len(output), 0, "Output should not be empty.")

if __name__ == '__main__':
    unittest.main()