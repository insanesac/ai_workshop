"""
StudyBuddy FastAPI Application
Production-grade API for multi-agent AI learning assistant
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import yaml
import uvicorn

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from studybuddy.core.llm_client import ensure_production_llm, QwenLangChainLLM
from studybuddy.agents.tutor import TutorAgent
from studybuddy.agents.session import SessionAgent
from studybuddy.agents.goal import GoalAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

# Global agents (initialized on startup)
tutor_agent = None
session_agent = None
goal_agent = None
llm_client = None

# Load configuration
def load_config():
    """Load application configuration"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'app_config.yaml')
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.warning("Config file not found, using defaults")
        return {
            'api': {'host': '0.0.0.0', 'port': 8000},
            'security': {'allowed_origins': ['http://localhost:8501']}
        }

config = load_config()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources"""
    global tutor_agent, session_agent, goal_agent, llm_client
    
    logger.info("🚀 Starting StudyBuddy API...")
    
    try:
        # Initialize LLM client
        logger.info("🧠 Initializing LLM client...")
        llm_client = ensure_production_llm()
        langchain_llm = QwenLangChainLLM(llm_client)
        
        # Initialize agents
        logger.info("🤖 Initializing agents...")
        tutor_agent = TutorAgent(langchain_llm)
        session_agent = SessionAgent(langchain_llm)
        goal_agent = GoalAgent(langchain_llm)
        
        logger.info("✅ StudyBuddy API initialized successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize StudyBuddy API: {e}")
        raise
    
    yield
    
    logger.info("🔄 Shutting down StudyBuddy API...")

# Create FastAPI app
app = FastAPI(
    title=config.get('api', {}).get('title', 'StudyBuddy API'),
    description=config.get('api', {}).get('description', 'Production multi-agent AI learning assistant API'),
    version=config.get('api', {}).get('version', '1.0.0'),
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get('security', {}).get('allowed_origins', ['*']),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message to send to the agent")
    agent_type: str = Field(..., description="Type of agent: 'tutor', 'session', or 'goal'")
    context: Optional[Dict] = Field(default=None, description="Additional context for the request")

class ChatResponse(BaseModel):
    response: str = Field(..., description="Agent's response")
    agent_type: str = Field(..., description="Type of agent that responded")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict] = Field(default=None, description="Additional response metadata")

class HealthResponse(BaseModel):
    status: str = Field(..., description="API health status")
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = Field(..., description="API version")
    agents_loaded: List[str] = Field(..., description="List of loaded agents")

class SystemStatsResponse(BaseModel):
    llm_stats: Dict = Field(..., description="LLM usage statistics")
    uptime: str = Field(..., description="API uptime")
    agents_status: Dict = Field(..., description="Agent status information")

# Dependency to get the appropriate agent
def get_agent(agent_type: str):
    """Get the appropriate agent based on type"""
    if agent_type == "tutor":
        if tutor_agent is None:
            raise HTTPException(status_code=503, detail="TutorAgent not initialized")
        return tutor_agent
    elif agent_type == "session":
        if session_agent is None:
            raise HTTPException(status_code=503, detail="SessionAgent not initialized")
        return session_agent
    elif agent_type == "goal":
        if goal_agent is None:
            raise HTTPException(status_code=503, detail="GoalAgent not initialized")
        return goal_agent
    else:
        raise HTTPException(status_code=400, detail=f"Invalid agent type: {agent_type}")

# API Routes
@app.get("/", response_model=Dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "StudyBuddy AI Learning Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "chat": "/chat",
            "health": "/health", 
            "stats": "/stats"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    agents_loaded = []
    if tutor_agent is not None:
        agents_loaded.append("tutor")
    if session_agent is not None:
        agents_loaded.append("session")
    if goal_agent is not None:
        agents_loaded.append("goal")
    
    return HealthResponse(
        status="healthy" if len(agents_loaded) == 3 else "degraded",
        version="1.0.0",
        agents_loaded=agents_loaded
    )

@app.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats():
    """Get system statistics"""
    if llm_client is None:
        raise HTTPException(status_code=503, detail="LLM client not initialized")
    
    llm_stats = llm_client.get_stats()
    
    agents_status = {
        "tutor": tutor_agent is not None,
        "session": session_agent is not None,
        "goal": goal_agent is not None
    }
    
    return SystemStatsResponse(
        llm_stats=llm_stats,
        uptime="Runtime stats not implemented",  # Could add actual uptime tracking
        agents_status=agents_status
    )

@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Chat with a specific agent"""
    try:
        # Get the appropriate agent
        agent = get_agent(request.agent_type)
        
        # Call the agent's main method
        if request.agent_type == "tutor":
            response = agent.teach(request.message)
        elif request.agent_type == "session":
            response = agent.manage_time(request.message)
        elif request.agent_type == "goal":
            response = agent.coach(request.message)
        else:
            raise HTTPException(status_code=400, detail="Invalid agent type")
        
        return ChatResponse(
            response=response,
            agent_type=request.agent_type,
            metadata={"context": request.context}
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/tutor/teach")
async def tutor_teach(request: Dict):
    """Direct endpoint for tutor agent"""
    if tutor_agent is None:
        raise HTTPException(status_code=503, detail="TutorAgent not initialized")
    
    message = request.get("message", "")
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    try:
        response = tutor_agent.teach(message)
        return {"response": response, "agent": "tutor", "timestamp": datetime.now()}
    except Exception as e:
        logger.error(f"Error in tutor endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/session/manage")
async def session_manage(request: Dict):
    """Direct endpoint for session agent"""
    if session_agent is None:
        raise HTTPException(status_code=503, detail="SessionAgent not initialized")
    
    message = request.get("message", "")
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    try:
        response = session_agent.manage_time(message)
        return {"response": response, "agent": "session", "timestamp": datetime.now()}
    except Exception as e:
        logger.error(f"Error in session endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/goal/coach")
async def goal_coach(request: Dict):
    """Direct endpoint for goal agent"""
    if goal_agent is None:
        raise HTTPException(status_code=503, detail="GoalAgent not initialized")
    
    message = request.get("message", "")
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    try:
        response = goal_agent.coach(message)
        return {"response": response, "agent": "goal", "timestamp": datetime.now()}
    except Exception as e:
        logger.error(f"Error in goal endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Run the server
    host = config.get('api', {}).get('host', '0.0.0.0')
    port = config.get('api', {}).get('port', 8000)
    
    logger.info(f"🚀 Starting StudyBuddy API on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
