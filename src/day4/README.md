# 🎓 StudyBuddy - AI Learning Assistant

## Production Multi-Agent System powered by Qwen2.5-14B

StudyBuddy is a production-grade AI learning assistant that uses multiple specialized agents to provide personalized educational support, time management, and progress tracking.

---

## 🚀 **System Architecture**

```
StudyBuddy System
├── 📚 TutorAgent - Educational Specialist
├── ⏰ SessionAgent - Time Management Expert  
├── 🎯 GoalAgent - Progress & Motivation Coach
└── 🤝 CoordinatorAgent - Multi-Agent Orchestrator
```

### **Core Technologies:**
- **LLM**: Qwen2.5-14B-Instruct (4-bit quantized)
- **Framework**: LangChain + CrewAI
- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Deployment**: Docker + Docker Compose

---

## 📁 **Project Structure**

```
day4/
├── � notebooks/                    # Jupyter development notebooks
│   ├── 01_studybuddy_introduction.ipynb
│   ├── 02_production_setup.ipynb
│   ├── 03_individual_agents.ipynb
│   ├── 04_multi_agent_system.ipynb
│   └── 05_production_demo.ipynb
├── 🐍 src/studybuddy/              # Core Python package
│   ├── core/                       # Core LLM functionality
│   │   ├── llm_client.py           # Production LLM client
│   │   └── __init__.py
│   ├── agents/                     # Specialized AI agents
│   │   ├── tutor.py                # Educational specialist
│   │   ├── session.py              # Time management
│   │   ├── goal.py                 # Progress tracking
│   │   └── __init__.py
│   ├── tools/                      # Agent tools and utilities
│   └── utils/                      # Shared utilities
├── ⚙️  config/                      # Configuration files
│   ├── model_config.yaml           # LLM settings
│   ├── agent_config.yaml           # Agent personalities
│   └── app_config.yaml             # Application settings
├── 📊 data/                        # Data storage
│   ├── sessions/                   # Study sessions
│   ├── goals/                      # Learning goals
│   └── notes/                      # Study materials
├── 🚀 fastapi_app/                 # REST API backend
│   └── main.py                     # FastAPI application
├── � streamlit_app/               # Web interface
│   └── app.py                      # Streamlit application
├── 🐳 Dockerfile                   # Container definition
├── 🐳 docker-compose.yml           # Multi-service orchestration
├── 📦 requirements.txt             # Python dependencies
└── 📦 setup.py                     # Package installation
```

## � **Quick Start**

### **Option 1: Development Setup**

```bash
# Clone the repository
cd ai-workshop/src/day4

# Install dependencies
pip install -r requirements.txt

# Run FastAPI backend
cd fastapi_app
python main.py

# In another terminal, run Streamlit frontend
cd streamlit_app
streamlit run app.py
```

### **Option 2: Docker Deployment**

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access the applications:
# - Streamlit Web UI: http://localhost:8501
# - FastAPI Docs: http://localhost:8000/docs
# - API Health: http://localhost:8000/health
```

**Built with ❤️ for AI education by the AI Workshop Team**
