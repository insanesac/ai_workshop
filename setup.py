from setuptools import setup, find_packages

setup(
    name='ai-workshop',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A comprehensive AI workshop covering LLMs, CV, and practical applications.',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'torch',
        'transformers',
        'opencv-python',
        'numpy',
        'pandas',
        'matplotlib',
        'gradio',
        'sentence-transformers',
        'faiss-cpu',  # or 'faiss-gpu' if using GPU
        'scikit-learn',
    ],
    extras_require={
        'gpu': [
            'torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu113',
        ],
    },
    python_requires='>=3.10',
)