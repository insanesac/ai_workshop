# test_environment.py

import os
import subprocess
import sys
import unittest

class TestEnvironmentSetup(unittest.TestCase):

    def test_python_version(self):
        """Test if Python version is 3.10 or higher."""
        version = sys.version_info
        self.assertGreaterEqual(version.major, 3)
        self.assertGreaterEqual(version.minor, 10, "Python version must be 3.10 or higher.")

    def test_required_packages_installed(self):
        """Test if required packages are installed."""
        required_packages = [
            'torch',
            'transformers',
            'opencv-python',
            'numpy',
            'pandas',
            'matplotlib',
            'gradio'
        ]
        for package in required_packages:
            with self.subTest(package=package):
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'show', package],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.assertEqual(result.returncode, 0, f"{package} is not installed.")

    def test_jupyter_notebook_installed(self):
        """Test if Jupyter Notebook is installed."""
        result = subprocess.run(
            [sys.executable, '-m', 'jupyter', '--version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.assertEqual(result.returncode, 0, "Jupyter Notebook is not installed.")

if __name__ == '__main__':
    unittest.main()