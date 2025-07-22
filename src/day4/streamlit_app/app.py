"""
StudyBuddy Streamlit Application
Production-grade web interface for multi-agent AI learning assistant
"""

import os
import sys
import logging
import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, Optional
import yaml

# Configure page
st.set_page_config(
    page_title="StudyBuddy - AI Learning Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
@st.cache_data
def load_config():
    """Load application configuration"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'app_config.yaml')
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        st.warning("Config file not found, using defaults")
        return {
            'api': {'host': 'localhost', 'port': 8000},
            'streamlit': {'title': 'StudyBuddy - AI Learning Assistant'}
        }

config = load_config()

# API Configuration
API_BASE_URL = f"http://{config.get('api', {}).get('host', 'localhost')}:{config.get('api', {}).get('port', 8000)}"

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'selected_agent' not in st.session_state:
    st.session_state.selected_agent = 'tutor'
if 'api_available' not in st.session_state:
    st.session_state.api_available = None

def check_api_health():
    """Check if the API is available"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def call_agent_api(agent_type: str, message: str) -> Optional[str]:
    """Call the agent API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "message": message,
                "agent_type": agent_type
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "No response received")
        else:
            return f"API Error: {response.status_code} - {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to StudyBuddy API. Please ensure the FastAPI server is running."
    except requests.exceptions.Timeout:
        return "⏱️ Request timed out. The AI agent might be processing a complex request."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def get_api_stats():
    """Get API statistics"""
    try:
        response = requests.get(f"{API_BASE_URL}/stats", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# Main app layout
def main():
    # Header
    st.title("🎓 StudyBuddy - AI Learning Assistant")
    st.markdown("**Production multi-agent system powered by Qwen2.5-14B**")
    
    # Check API status
    if st.session_state.api_available is None:
        with st.spinner("Checking API connection..."):
            st.session_state.api_available = check_api_health()
    
    if not st.session_state.api_available:
        st.error("""
        🚨 **StudyBuddy API is not available**
        
        Please ensure the FastAPI server is running:
        ```bash
        cd fastapi_app
        python main.py
        ```
        
        Or using uvicorn:
        ```bash
        uvicorn main:app --host 0.0.0.0 --port 8000 --reload
        ```
        """)
        
        if st.button("🔄 Retry Connection"):
            st.session_state.api_available = None
            st.rerun()
        
        return
    
    # Sidebar
    with st.sidebar:
        st.header("🤖 Agent Selection")
        
        # Agent selection
        agent_options = {
            'tutor': '📚 TutorAgent - Educational Specialist',
            'session': '⏰ SessionAgent - Time Management Expert', 
            'goal': '🎯 GoalAgent - Progress & Motivation Coach'
        }
        
        selected_agent = st.radio(
            "Choose your AI assistant:",
            options=list(agent_options.keys()),
            format_func=lambda x: agent_options[x],
            key='agent_selection'
        )
        
        st.session_state.selected_agent = selected_agent
        
        # Agent info
        st.subheader("ℹ️ Agent Info")
        
        agent_descriptions = {
            'tutor': """
            **📚 TutorAgent**
            - Educational content specialist
            - Provides clear explanations and examples
            - Helps with programming concepts
            - Creates study materials
            - Patient and adaptive teaching style
            """,
            'session': """
            **⏰ SessionAgent**
            - Time management expert
            - Creates optimized study schedules
            - Pomodoro timer integration
            - Productivity analysis and tips
            - Organized and motivating approach
            """,
            'goal': """
            **🎯 GoalAgent**
            - Progress tracking specialist
            - SMART goal setting
            - Achievement celebration
            - Motivational coaching
            - Data-driven insights
            """
        }
        
        st.markdown(agent_descriptions[selected_agent])
        
        # System status
        st.subheader("📊 System Status")
        
        # API health indicator
        st.success("✅ API Connected")
        
        # Get and display stats
        stats = get_api_stats()
        if stats:
            st.metric("LLM Requests", stats.get('llm_stats', {}).get('requests_processed', 0))
            st.metric("Tokens Generated", stats.get('llm_stats', {}).get('total_tokens_generated', 0))
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Main chat interface
    st.header(f"💬 Chat with {agent_options[selected_agent]}")
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for i, chat in enumerate(st.session_state.chat_history):
            # User message
            with st.chat_message("user"):
                st.write(chat['user_message'])
            
            # Agent response
            with st.chat_message("assistant", avatar={"tutor": "📚", "session": "⏰", "goal": "🎯"}[chat['agent_type']]):
                st.write(chat['agent_response'])
                st.caption(f"*{chat['timestamp']} - {agent_options[chat['agent_type']]}*")
    
    # Chat input
    user_input = st.chat_input("Ask your StudyBuddy assistant anything...")
    
    if user_input:
        # Add user message to history
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Display user message immediately
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get agent response
        with st.chat_message("assistant", avatar={"tutor": "📚", "session": "⏰", "goal": "🎯"}[selected_agent]):
            with st.spinner(f"🤔 {agent_options[selected_agent].split(' - ')[0]} is thinking..."):
                response = call_agent_api(selected_agent, user_input)
            
            st.write(response)
            st.caption(f"*{timestamp} - {agent_options[selected_agent]}*")
        
        # Add to chat history
        st.session_state.chat_history.append({
            'user_message': user_input,
            'agent_response': response,
            'agent_type': selected_agent,
            'timestamp': timestamp
        })
        
        # Rerun to update the display
        st.rerun()
    
    # Quick action buttons
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📚 Get Study Help"):
            st.session_state.selected_agent = 'tutor'
            # Auto-fill input (would need session state for chat input)
            st.info("Selected TutorAgent! Ask about any topic you're learning.")
    
    with col2:
        if st.button("⏰ Plan Study Session"):
            st.session_state.selected_agent = 'session'
            st.info("Selected SessionAgent! Ask about scheduling and time management.")
    
    with col3:
        if st.button("🎯 Set Learning Goals"):
            st.session_state.selected_agent = 'goal'
            st.info("Selected GoalAgent! Ask about setting and tracking learning goals.")
    
    # Example questions
    with st.expander("💡 Example Questions"):
        st.markdown("""
        **📚 For TutorAgent:**
        - "Explain Python functions with examples"
        - "Help me understand machine learning concepts"
        - "Create a study guide for data structures"
        
        **⏰ For SessionAgent:**
        - "Create a study schedule for learning Python"
        - "Start a 25-minute Pomodoro session"
        - "How can I improve my study productivity?"
        
        **🎯 For GoalAgent:**
        - "I want to learn machine learning in 3 months"
        - "Track my progress on Python learning"
        - "I need motivation to keep studying"
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**StudyBuddy v1.0.0** | Production multi-agent AI learning assistant | "
        "Powered by Qwen2.5-14B + LangChain + CrewAI"
    )

if __name__ == "__main__":
    main()
