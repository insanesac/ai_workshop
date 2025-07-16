# Setup Instructions for AI Workshop

Welcome to the AI Workshop! This document provides step-by-step instructions to set up your environment and get started with the workshop materials.

## Prerequisites

Before you begin, ensure you have the following installed on your machine:

- **Python 3.10 or higher**
- **Jupyter Notebook** or **VS Code** (with Jupyter extension)
- **Git** (for version control)

## Environment Setup

### 1. Clone the Repository

Start by cloning the workshop repository to your local machine. Open your terminal and run:

```bash
git clone https://github.com/yourusername/ai-workshop.git
cd ai-workshop
```

### 2. Create a Virtual Environment

It's recommended to create a virtual environment to manage dependencies. You can use `venv` or `conda`. Here’s how to do it with `venv`:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install Required Packages

Navigate to the `src/shared/requirements` directory and install the required packages using `pip`:

```bash
pip install -r requirements.txt
```

If you have a GPU and want to utilize it, install the GPU-specific requirements:

```bash
pip install -r requirements_gpu.txt
```

Alternatively, if you prefer using `conda`, you can create an environment using the provided YAML file:

```bash
conda env create -f src/shared/requirements/conda_environment.yml
conda activate ai-workshop
```

### 4. Verify Installation

To ensure everything is set up correctly, run the following commands in a Python shell:

```python
import torch
import transformers
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import gradio as gr

print("All packages imported successfully!")
```

### 5. Launch Jupyter Notebook

If you are using Jupyter Notebook, you can start it by running:

```bash
jupyter notebook
```

Navigate to the `src/day1/notebooks` directory to access the workshop notebooks.

### 6. Explore Workshop Materials

The workshop is structured into five days, each focusing on different aspects of AI and ML. Here’s a brief overview:

- **Day 1**: Foundations & Environment Setup
- **Day 2**: LLM Fine-Tuning & Application
- **Day 3**: Computer Vision Deep Dive
- **Day 4**: Capstone Hackathon
- **Day 5**: Showcase & Next Steps

You can find the notebooks and scripts in the respective directories under `src/day1`, `src/day2`, `src/day3`, `src/day4`, and `src/day5`.

## Troubleshooting

If you encounter any issues during setup, refer to the [Troubleshooting Guide](troubleshooting.md) for common problems and solutions.

## Additional Resources

For further learning, check out the [Additional Resources](additional_resources.md) document.

## Ethics Guidelines

Please review the [Ethics Guidelines](ethics_guidelines.md) to understand the ethical considerations in AI development.

---

With these instructions, you should be well on your way to successfully setting up your environment for the AI Workshop. Enjoy your learning experience!