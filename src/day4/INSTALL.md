# 🚀 StudyBuddy Installation Guide

## Quick Setup for Development

### Option 1: Development Mode (Recommended for Workshop)

```bash
# Navigate to the day4 directory
cd ai-workshop/src/day4

# Install in development mode (allows editing)
pip install -e .

# Install with all extras for full functionality
pip install -e ".[dev,notebook,gpu]"

# Verify installation
python -c "import studybuddy; print('✅ StudyBuddy installed successfully!')"
```

### Option 2: Direct Installation

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Add src to Python path (for notebook compatibility)
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

## Running the Applications

### 1. FastAPI Backend

```bash
# Start the API server
cd fastapi_app
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Access API docs: http://localhost:8000/docs
```

### 2. Streamlit Frontend

```bash
# Start the web interface
cd streamlit_app
streamlit run app.py

# Access web app: http://localhost:8501
```

### 3. Jupyter Notebooks

```bash
# Start Jupyter Lab
jupyter lab notebooks/

# Run notebooks in sequence:
# 1. 02_production_setup.ipynb
# 2. 03_individual_agents.ipynb
# 3. 04_multi_agent_system.ipynb
```

### 4. Docker Deployment

```bash
# Build and run all services
docker-compose up --build

# Access applications:
# - Web UI: http://localhost:8501
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

## Package Structure After Installation

```
studybuddy/
├── core/              # LLM client and base functionality
├── agents/            # Specialized AI agents
├── tools/             # Agent tools and utilities
└── utils/             # Common utilities
```

## Import Examples

```python
# Import individual agents
from studybuddy.agents.tutor import TutorAgent
from studybuddy.agents.session import SessionAgent
from studybuddy.agents.goal import GoalAgent

# Import LLM client
from studybuddy.core.llm_client import ensure_production_llm, QwenLangChainLLM

# Import everything
import studybuddy
```

## Troubleshooting

### Common Issues:

1. **Import Error**: Make sure you've installed the package or added src to PYTHONPATH
2. **GPU Issues**: Install CUDA-compatible PyTorch if using GPU
3. **Port Conflicts**: Change ports in config/app_config.yaml if needed
4. **Memory Issues**: Reduce model batch size or use CPU mode

### Getting Help:

- Check the README.md for detailed documentation
- Review notebook comments for explanations
- Check FastAPI docs at http://localhost:8000/docs when running
