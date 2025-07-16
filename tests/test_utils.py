# test_utils.py

import unittest
from src.shared.utils.data_loader import load_data
from src.shared.utils.model_utils import save_model, load_model
from src.shared.utils.visualization import plot_results

class TestUtils(unittest.TestCase):

    def test_load_data(self):
        # Test loading a valid dataset
        data = load_data('src/day2/data/campus_faq.jsonl')
        self.assertIsNotNone(data)
        self.assertGreater(len(data), 0)

    def test_save_load_model(self):
        # Test saving and loading a model
        model_path = 'test_model.pth'
        dummy_model = {'param1': 1, 'param2': 2}
        save_model(dummy_model, model_path)
        
        loaded_model = load_model(model_path)
        self.assertEqual(dummy_model, loaded_model)

    def test_plot_results(self):
        # Test plotting results
        results = [0.1, 0.2, 0.3, 0.4]
        try:
            plot_results(results)
        except Exception as e:
            self.fail(f"plot_results raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()