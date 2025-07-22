# StudyBuddy AI Learning Assistant
# Production-grade multi-agent system for personalized education

__version__ = "1.0.0"
__author__ = "AI Workshop Team"
__description__ = "Production multi-agent AI learning assistant powered by Qwen2.5-14B"

from .core.llm_client import ProductionLLMClient, QwenLangChainLLM

# Enhanced versions with full LLM integration
from .agents.enhanced_tutor import EnhancedTutorAgent
from .agents.enhanced_session import EnhancedSessionAgent
from .agents.enhanced_goal import EnhancedGoalAgent

# Tools with LLM enhancement
from .tools.learning_tools import WebSearchTool, CodeAnalysisTool, LearningResourceTool

def create_study_buddy_system(model_name: str = "Qwen/Qwen2.5-14B-Instruct", 
                             student_id: str = "default_student") -> dict:
    """
    Factory function to create a complete StudyBuddy system with all agents
    
    Args:
        model_name: The LLM model to use (default: Qwen2.5-14B)
        student_id: Unique identifier for the student
        
    Returns:
        Dictionary containing initialized LLM client and all agents
    """
    
    # Initialize LLM client
    llm_client = ProductionLLMClient(model_name=model_name)
    
    # Create enhanced agents with full LLM integration
    agents = {
        "tutor": EnhancedTutorAgent(llm_client=llm_client, student_id=student_id),
        "session_manager": EnhancedSessionAgent(llm_client=llm_client, student_id=student_id),
        "goal_coach": EnhancedGoalAgent(llm_client=llm_client, student_id=student_id)
    }
    
    # Create enhanced tools
    tools = {
        "web_search": WebSearchTool(llm_client=llm_client),
        "code_analyzer": CodeAnalysisTool(llm_client=llm_client),
        "resource_generator": LearningResourceTool(llm_client=llm_client)
    }
    
    return {
        "llm_client": llm_client,
        "agents": agents,
        "tools": tools,
        "student_id": student_id,
        "model_name": model_name
    }

def create_basic_study_buddy(student_id: str = "default_student") -> dict:
    """
    Create a StudyBuddy system with enhanced agents
    """
    return create_study_buddy_system(
        model_name="Qwen/Qwen2.5-14B-Instruct",
        student_id=student_id
    )

__all__ = [
    "ProductionLLMClient",
    "QwenLangChainLLM", 
    "EnhancedTutorAgent",
    "EnhancedSessionAgent",
    "EnhancedGoalAgent",
    "WebSearchTool",
    "CodeAnalysisTool", 
    "LearningResourceTool",
    "create_study_buddy_system",
    "create_basic_study_buddy"
]
