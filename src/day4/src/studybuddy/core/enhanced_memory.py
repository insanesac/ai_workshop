"""
Enhanced StudyBuddy Memory & Learning System
Provides comprehensive memory, learning analytics, and emotional intelligence
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from collections import defaultdict
import re

# Set up logging
logger = logging.getLogger(__name__)


class EmotionalIntelligence:
    """
    Analyzes student emotions and learning state from conversations
    """
    
    def __init__(self):
        # Emotion keywords mapping
        self.emotion_keywords = {
            "frustrated": ["frustrated", "stuck", "confused", "don't understand", "hate this", "annoying"],
            "confident": ["got it", "understand", "easy", "makes sense", "clear", "awesome"],
            "anxious": ["worried", "nervous", "scared", "overwhelmed", "pressure", "stressed"],
            "excited": ["excited", "love", "amazing", "awesome", "cool", "interesting"],
            "discouraged": ["give up", "too hard", "impossible", "can't do", "failing", "hopeless"],
            "motivated": ["ready", "determined", "let's do this", "motivated", "focused"]
        }
        
        # Learning indicators
        self.learning_indicators = {
            "struggling": ["don't get", "still confused", "not working", "error", "wrong"],
            "progressing": ["better now", "starting to", "almost", "getting closer"],
            "mastering": ["perfectly", "easily", "no problem", "understand completely"]
        }
    
    def analyze_emotion(self, text: str) -> Dict[str, Any]:
        """Analyze emotional state from student text"""
        text_lower = text.lower()
        
        emotions_detected = {}
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotions_detected[emotion] = score
        
        # Determine primary emotion
        primary_emotion = "neutral"
        if emotions_detected:
            primary_emotion = max(emotions_detected.keys(), key=lambda x: emotions_detected[x])
        
        # Learning state analysis
        learning_state = "unknown"
        for state, indicators in self.learning_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                learning_state = state
                break
        
        return {
            "primary_emotion": primary_emotion,
            "all_emotions": emotions_detected,
            "learning_state": learning_state,
            "needs_encouragement": primary_emotion in ["frustrated", "discouraged", "anxious"],
            "confidence_level": "high" if primary_emotion in ["confident", "excited"] else 
                              "low" if primary_emotion in ["frustrated", "discouraged"] else "medium"
        }


class LearningAnalytics:
    """
    Tracks and analyzes student learning patterns and progress
    """
    
    def __init__(self):
        self.topic_progress = defaultdict(list)
        self.session_data = []
        self.difficulty_patterns = defaultdict(int)
        
    def track_topic_interaction(self, topic: str, understanding_level: float, 
                               time_spent: int, success: bool, emotion_data: Dict):
        """Track student interaction with a specific topic"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "understanding_level": understanding_level,
            "time_spent_minutes": time_spent,
            "success": success,
            "emotion": emotion_data,
            "confidence": emotion_data.get("confidence_level", "medium")
        }
        
        self.topic_progress[topic].append(interaction)
        
        # Track difficulty patterns
        if not success or understanding_level < 5:
            self.difficulty_patterns[topic] += 1
    
    def get_learning_insights(self, topic: str = None) -> Dict[str, Any]:
        """Generate learning insights and recommendations"""
        if topic:
            topic_data = self.topic_progress.get(topic, [])
            if not topic_data:
                return {"message": f"No data available for {topic}"}
            
            # Calculate progress trends
            understanding_scores = [d["understanding_level"] for d in topic_data]
            avg_understanding = sum(understanding_scores) / len(understanding_scores)
            improvement_trend = "improving" if len(understanding_scores) > 1 and understanding_scores[-1] > understanding_scores[0] else "stable"
            
            # Emotion analysis
            recent_emotions = [d["emotion"]["primary_emotion"] for d in topic_data[-3:]]
            needs_support = any(emotion in ["frustrated", "discouraged"] for emotion in recent_emotions)
            
            return {
                "topic": topic,
                "total_sessions": len(topic_data),
                "average_understanding": round(avg_understanding, 1),
                "improvement_trend": improvement_trend,
                "recent_emotions": recent_emotions,
                "needs_emotional_support": needs_support,
                "difficulty_score": self.difficulty_patterns.get(topic, 0),
                "recommendations": self._generate_recommendations(topic, avg_understanding, recent_emotions)
            }
        else:
            # Overall learning analysis
            all_topics = list(self.topic_progress.keys())
            if not all_topics:
                return {"message": "No learning data available"}
            
            total_sessions = sum(len(sessions) for sessions in self.topic_progress.values())
            struggling_topics = [topic for topic, difficulty in self.difficulty_patterns.items() if difficulty > 2]
            
            return {
                "total_topics_studied": len(all_topics),
                "total_sessions": total_sessions,
                "struggling_topics": struggling_topics,
                "strong_topics": [topic for topic in all_topics if topic not in struggling_topics],
                "overall_trend": "progressing" if total_sessions > 5 else "starting"
            }
    
    def _generate_recommendations(self, topic: str, avg_understanding: float, recent_emotions: List[str]) -> List[str]:
        """Generate personalized learning recommendations"""
        recommendations = []
        
        if avg_understanding < 5:
            recommendations.append(f"Consider breaking down {topic} into smaller, more manageable concepts")
            recommendations.append("Try different learning resources or approaches")
        
        if "frustrated" in recent_emotions:
            recommendations.append("Take a short break and come back with fresh perspective")
            recommendations.append("Ask for help from a peer or instructor")
        
        if avg_understanding > 7:
            recommendations.append(f"Great progress on {topic}! Consider exploring advanced applications")
            recommendations.append("Help others with this topic to reinforce your understanding")
        
        return recommendations


class ConversationMemory:
    """
    Manages conversation history with semantic search and context retrieval
    """
    
    def __init__(self, student_id: str, memory_dir: str = "memory"):
        self.student_id = student_id
        self.memory_dir = memory_dir
        os.makedirs(memory_dir, exist_ok=True)
        
        # Initialize conversation storage
        self.conversation_file = os.path.join(memory_dir, f"{student_id}_conversations.json")
        self.conversations = self._load_conversations()
        
        # Initialize analytics
        self.emotion_analyzer = EmotionalIntelligence()
        self.learning_analytics = LearningAnalytics()
    
    def _load_conversations(self) -> List[Dict]:
        """Load conversation history from disk"""
        if os.path.exists(self.conversation_file):
            try:
                with open(self.conversation_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def _save_conversations(self):
        """Save conversations to disk"""
        with open(self.conversation_file, 'w') as f:
            json.dump(self.conversations, f, indent=2)
    
    def store_conversation(self, agent_type: str, user_message: str, agent_response: str,
                          topic: str = "general", emotion_data : str = "neutral", understanding_level: float = 5.0):
        """Store a conversation with emotional and learning analysis"""
        
        # Create conversation record
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "agent_type": agent_type,
            "topic": topic,
            "user_message": user_message,
            "agent_response": agent_response,
            "emotion_analysis": emotion_data,
            "understanding_level": understanding_level,
            "session_length": 1  # Will be updated for longer conversations
        }
        
        self.conversations.append(conversation)
        self._save_conversations()
        
        # Track in learning analytics
        self.learning_analytics.track_topic_interaction(
            topic=topic,
            understanding_level=understanding_level,
            time_spent=1,
            success=emotion_data["learning_state"] != "struggling",
            emotion_data=emotion_data
        )
    
    def get_conversation_context(self, current_topic: str, agent_type: str = None, limit: int = 5) -> Dict[str, Any]:
        """Get relevant conversation context for personalized responses"""
        
        # Filter conversations by relevance
        relevant_conversations = []
        
        for conv in self.conversations[-20:]:  # Look at recent conversations
            relevance_score = 0
            
            # Topic similarity
            if current_topic.lower() in conv["topic"].lower() or conv["topic"].lower() in current_topic.lower():
                relevance_score += 3
            
            # Agent type match
            if agent_type and conv["agent_type"] == agent_type:
                relevance_score += 2
            
            # Recent conversations get higher scores
            conv_time = datetime.fromisoformat(conv["timestamp"])
            hours_ago = (datetime.now() - conv_time).total_seconds() / 3600
            if hours_ago < 24:
                relevance_score += 2
            elif hours_ago < 168:  # 1 week
                relevance_score += 1
            
            if relevance_score > 0:
                relevant_conversations.append((conv, relevance_score))
        
        # Sort by relevance and take top conversations
        relevant_conversations.sort(key=lambda x: x[1], reverse=True)
        top_conversations = [conv[0] for conv in relevant_conversations[:limit]]
        
        # Analyze emotional state trends
        recent_emotions = [conv["emotion_analysis"]["primary_emotion"] 
                          for conv in self.conversations[-5:] if conv["emotion_analysis"]]
        
        # Get learning insights
        learning_insights = self.learning_analytics.get_learning_insights(current_topic)
        
        return {
            "relevant_conversations": top_conversations,
            "recent_emotional_trend": recent_emotions,
            "learning_insights": learning_insights,
            "total_conversations": len(self.conversations),
            "topics_discussed": list(set(conv["topic"] for conv in self.conversations)),
            "needs_encouragement": any(emotion in ["frustrated", "discouraged", "anxious"] 
                                     for emotion in recent_emotions[-3:])
        }
    
    def get_student_profile(self) -> Dict[str, Any]:
        """Generate comprehensive student profile"""
        if not self.conversations:
            return {
                "student_id": self.student_id,
                "status": "new_student",
                "total_conversations": 0
            }
        
        # Calculate session statistics
        total_conversations = len(self.conversations)
        unique_topics = list(set(conv["topic"] for conv in self.conversations))
        
        # Emotional analysis
        all_emotions = [conv["emotion_analysis"]["primary_emotion"] 
                       for conv in self.conversations if conv["emotion_analysis"]]
        emotion_distribution = {}
        for emotion in all_emotions:
            emotion_distribution[emotion] = emotion_distribution.get(emotion, 0) + 1
        
        # Learning patterns
        avg_understanding = sum(conv["understanding_level"] for conv in self.conversations) / total_conversations
        
        # Recent activity
        recent_activity = self.conversations[-5:] if len(self.conversations) >= 5 else self.conversations
        
        return {
            "student_id": self.student_id,
            "total_conversations": total_conversations,
            "topics_studied": unique_topics,
            "average_understanding": round(avg_understanding, 1),
            "emotion_distribution": emotion_distribution,
            "learning_insights": self.learning_analytics.get_learning_insights(),
            "recent_activity": recent_activity,
            "preferred_learning_style": self._detect_learning_style(),
            "study_patterns": self._analyze_study_patterns()
        }
    
    def _detect_learning_style(self) -> str:
        """Detect student's preferred learning style from conversation patterns"""
        if len(self.conversations) < 3:
            return "unknown"
        
        # Analyze conversation content for learning style indicators
        text_requests = sum(1 for conv in self.conversations if "explain" in conv["user_message"].lower())
        example_requests = sum(1 for conv in self.conversations if "example" in conv["user_message"].lower())
        practice_requests = sum(1 for conv in self.conversations if "practice" in conv["user_message"].lower())
        
        if example_requests > text_requests and example_requests > practice_requests:
            return "visual_learner"
        elif practice_requests > text_requests:
            return "kinesthetic_learner"
        else:
            return "auditory_learner"
    
    def _analyze_study_patterns(self) -> Dict[str, Any]:
        """Analyze student's study patterns and habits"""
        if len(self.conversations) < 5:
            return {"pattern": "insufficient_data"}
        
        # Analyze timing patterns
        conversation_times = [datetime.fromisoformat(conv["timestamp"]) for conv in self.conversations]
        hours = [t.hour for t in conversation_times]
        
        # Find peak study hours
        hour_counts = {}
        for hour in hours:
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        peak_hour = max(hour_counts.keys(), key=lambda x: hour_counts[x]) if hour_counts else 12
        
        # Analyze session frequency
        if len(conversation_times) > 1:
            time_diffs = [(conversation_times[i] - conversation_times[i-1]).total_seconds() / 3600 
                         for i in range(1, len(conversation_times))]
            avg_gap_hours = sum(time_diffs) / len(time_diffs)
        else:
            avg_gap_hours = 0
        
        return {
            "preferred_study_time": f"{peak_hour}:00",
            "average_session_gap_hours": round(avg_gap_hours, 1),
            "study_frequency": "high" if avg_gap_hours < 24 else "medium" if avg_gap_hours < 72 else "low",
            "total_study_days": len(set(t.date() for t in conversation_times))
        }
