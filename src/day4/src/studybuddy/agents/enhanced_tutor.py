"""
Enhanced TutorAgent - Educational specialist with empathy and comprehensive tools
"""

import sys
import os
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class EnhancedTutorAgent:
    """
    An empathetic, intelligent tutor that adapts to student needs and emotions
    """
    
    def __init__(self, llm_client, student_id: str = "default_student"):
        self.llm_client = llm_client
        self.student_id = student_id
        self.agent_type = "tutor"
        
        # Initialize tools with LLM client
        try:
            from ..tools.learning_tools import WebSearchTool, CodeAnalysisTool, LearningResourceTool
            from ..core.enhanced_memory import ConversationMemory, EmotionalIntelligence
            
            self.web_search = WebSearchTool(llm_client=llm_client)
            self.code_analyzer = CodeAnalysisTool(llm_client=llm_client)
            self.resource_tool = LearningResourceTool(llm_client=llm_client)
            self.memory = ConversationMemory(student_id)
            self.emotion_analyzer = EmotionalIntelligence()
        except ImportError as e:
            # Fallback for when tools are not available
            self.web_search = None
            self.code_analyzer = None
            self.resource_tool = None
            self.memory = None
            self.emotion_analyzer = None
            logger.warning(f"Enhanced tools not available ({e}), using basic functionality")
        
        # Mock conversation history for basic functionality
        self.conversation_history = []
        
        # Tutor personality traits
        self.personality_traits = {
            "patience": 0.9,
            "enthusiasm": 0.8,
            "empathy": 0.95,
            "encouragement": 0.9,
            "humor": 0.6,
            "adaptability": 0.85
        }
        
        # Teaching strategies based on emotional states
        self.emotional_strategies = {
            "frustrated": {
                "approach": "Break down concepts into smaller steps, use analogies, provide encouragement",
                "tone": "calm, patient, reassuring",
                "techniques": ["step-by-step breakdown", "real-world analogies", "confidence building"]
            },
            "confident": {
                "approach": "Challenge with slightly advanced concepts, provide interesting applications",
                "tone": "enthusiastic, engaging",
                "techniques": ["advanced examples", "practical applications", "exploration encouragement"]
            },
            "anxious": {
                "approach": "Provide structure, clear expectations, and lots of positive reinforcement",
                "tone": "calm, supportive, structured",
                "techniques": ["clear roadmaps", "small wins", "stress reduction"]
            },
            "excited": {
                "approach": "Channel enthusiasm into productive learning, provide engaging content",
                "tone": "energetic, passionate",
                "techniques": ["exciting projects", "cool applications", "discovery learning"]
            },
            "discouraged": {
                "approach": "Focus on strengths, celebrate small wins, rebuild confidence",
                "tone": "warm, encouraging, supportive",
                "techniques": ["strength identification", "achievement highlighting", "motivation rebuilding"]
            }
        }
    
    def teach(self, student_question: str, topic: str = "programming", 
              understanding_level: float = 5.0) -> str:
        """
        Provide educational response adapted to student's emotional state and learning history
        """
        logger.info(f"TutorAgent teaching: {student_question[:50]}...")
        
        # Analyze emotional state from question
        emotion_data = self._analyze_emotion(student_question)
        
        # Select appropriate teaching strategy
        strategy = self._select_teaching_strategy(emotion_data)
        
        # Generate empathetic response
        response = self._generate_empathetic_response(
            question=student_question,
            topic=topic,
            emotion_data=emotion_data,
            strategy=strategy,
            understanding_level=understanding_level
        )
        
        # Store conversation
        self.conversation_history.append({
            "question": student_question,
            "response": response,
            "emotion": emotion_data["primary_emotion"],
            "topic": topic,
            "understanding_level": understanding_level
        })
        
        return response
    
    def _analyze_emotion(self, text: str) -> Dict[str, Any]:
        """Simple emotion analysis from student text"""
        text_lower = text.lower()
        
        emotion_keywords = {
            "frustrated": ["frustrated", "stuck", "confused", "don't understand", "hate this", "annoying"],
            "confident": ["got it", "understand", "easy", "makes sense", "clear", "awesome"],
            "anxious": ["worried", "nervous", "scared", "overwhelmed", "pressure", "stressed"],
            "excited": ["excited", "love", "amazing", "awesome", "cool", "interesting"],
            "discouraged": ["give up", "too hard", "impossible", "can't do", "failing", "hopeless"],
            "motivated": ["ready", "determined", "let's do this", "motivated", "focused"]
        }
        
        emotions_detected = {}
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotions_detected[emotion] = score
        
        primary_emotion = "neutral"
        if emotions_detected:
            primary_emotion = max(emotions_detected.keys(), key=lambda x: emotions_detected[x])
        
        return {
            "primary_emotion": primary_emotion,
            "all_emotions": emotions_detected,
            "needs_encouragement": primary_emotion in ["frustrated", "discouraged", "anxious"],
            "confidence_level": "high" if primary_emotion in ["confident", "excited"] else 
                              "low" if primary_emotion in ["frustrated", "discouraged"] else "medium"
        }
    
    def _select_teaching_strategy(self, emotion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Select appropriate teaching strategy based on student's emotional state"""
        primary_emotion = emotion_data.get("primary_emotion", "neutral")
        
        if primary_emotion in self.emotional_strategies:
            return self.emotional_strategies[primary_emotion]
        else:
            return {
                "approach": "Clear explanation with examples and practice opportunities",
                "tone": "friendly, helpful, clear",
                "techniques": ["clear explanations", "practical examples", "guided practice"]
            }
    
    def _generate_empathetic_response(self, question: str, topic: str, emotion_data: Dict[str, Any],
                                     strategy: Dict[str, Any], understanding_level: float) -> str:
        """Generate a personalized, empathetic response using the LLM"""
        
        # Build comprehensive system prompt
        system_prompt = self._build_tutor_system_prompt(emotion_data, strategy, understanding_level)
        
        # Build context-rich user prompt
        user_prompt = self._build_contextual_prompt(question, topic, emotion_data)
        
        try:
            # Generate response using the LLM
            response = self.llm_client.generate_response(
                prompt=user_prompt,
                system_message=system_prompt,
                max_tokens=400,
                temperature=0.7
            )
            
            # Add personality touches
            enhanced_response = self._enhance_response_with_personality(response, emotion_data)
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"Error generating tutor response: {e}")
            return self._generate_fallback_response(question, emotion_data)
    
    def _build_tutor_system_prompt(self, emotion_data: Dict[str, Any], 
                                  strategy: Dict[str, Any], understanding_level: float) -> str:
        """Build a comprehensive system prompt for the tutor personality"""
        
        primary_emotion = emotion_data.get("primary_emotion", "neutral")
        
        system_prompt = f"""You are Alex, an expert programming tutor with a warm, empathetic personality. You genuinely care about your students' success and adapt your teaching style to their emotional needs.

STUDENT CONTEXT:
- Current emotional state: {primary_emotion}
- Understanding level: {understanding_level}/10
- Needs encouragement: {emotion_data.get('needs_encouragement', False)}

TEACHING STRATEGY FOR THIS INTERACTION:
- Approach: {strategy['approach']}
- Tone: {strategy['tone']}
- Techniques: {', '.join(strategy['techniques'])}

YOUR PERSONALITY TRAITS:
- Extremely patient and understanding
- Enthusiastic about programming and teaching
- Uses analogies and real-world examples
- Celebrates student progress, no matter how small
- Adapts explanations to student's emotional state
- Encourages experimentation and learning from mistakes

RESPONSE GUIDELINES:
1. Acknowledge the student's emotional state if appropriate
2. Use the recommended tone and approach
3. Provide clear, step-by-step explanations
4. Include practical examples and analogies
5. Offer encouragement and positive reinforcement
6. Suggest next steps or practice opportunities
7. Be conversational and supportive, not robotic

Remember: You're not just teaching code, you're building confidence and fostering a love for programming."""
        
        return system_prompt
    
    def _build_contextual_prompt(self, question: str, topic: str, emotion_data: Dict[str, Any]) -> str:
        """Build a context-rich prompt for the LLM"""
        
        prompt_parts = [f"Student Question: {question}"]
        prompt_parts.append(f"Topic: {topic}")
        
        # Add emotional context
        if emotion_data["primary_emotion"] != "neutral":
            prompt_parts.append(f"Student seems {emotion_data['primary_emotion']} - please respond accordingly")
        
        # Add conversation history context
        if len(self.conversation_history) > 0:
            recent_topics = [conv["topic"] for conv in self.conversation_history[-2:]]
            if recent_topics:
                prompt_parts.append(f"Recent topics discussed: {', '.join(recent_topics)}")
        
        return "\n\n".join(prompt_parts)
    
    def _enhance_response_with_personality(self, response: str, emotion_data: Dict[str, Any]) -> str:
        """Add personality touches to the LLM response"""
        
        primary_emotion = emotion_data.get("primary_emotion", "neutral")
        
        # Add emotional support if needed
        if primary_emotion == "frustrated":
            if not any(phrase in response.lower() for phrase in ["i understand", "frustrating", "no worries"]):
                response = "I totally understand that this can be frustrating! " + response
        
        elif primary_emotion == "excited":
            if not any(phrase in response.lower() for phrase in ["awesome", "exciting", "love your enthusiasm"]):
                response = "I love your enthusiasm! " + response
        
        elif primary_emotion == "discouraged":
            if not any(phrase in response.lower() for phrase in ["you've got this", "believe", "capable"]):
                response += "\n\nRemember, every programmer has been where you are now. You've got this! 💪"
        
        # Add encouragement for progress
        if len(self.conversation_history) > 3:
            response += "\n\nBy the way, I'm really proud of how much you've been learning! Keep up the great work! 🌟"
        
        return response
    
    def _generate_fallback_response(self, question: str, emotion_data: Dict[str, Any]) -> str:
        """Generate a fallback response when LLM fails"""
        
        primary_emotion = emotion_data.get("primary_emotion", "neutral")
        
        if primary_emotion == "frustrated":
            return f"""I can see you're working through something challenging, and that's completely normal in programming! 
            
Let me help you with "{question}". While I'm having a technical moment, here's what I suggest:

1. Break the problem into smaller pieces
2. Try writing out what you want to happen in plain English first
3. Look for similar examples online or in documentation
4. Don't hesitate to ask for help - every programmer does this!

What specific part is giving you the most trouble? I'm here to help you figure it out step by step. 🤗"""

        else:
            return f"""Thanks for your question about "{question}"! I'm having a small technical hiccup, but I'm still here to help you learn.

Here's my suggestion: Try breaking down your question into smaller parts, and let's tackle them one by one. Programming is all about problem-solving, and sometimes the best way to learn is by working through challenges together.

What's the specific concept or part you'd like to focus on first? I'm excited to help you understand it! 🚀"""
    
    def create_practice_exercises(self, topic: str, difficulty: str = "beginner") -> List[Dict[str, Any]]:
        """Create personalized practice exercises"""
        
        # Mock exercise generation based on topic
        if topic.lower() == "python functions":
            if difficulty == "beginner":
                return [
                    {
                        "title": "Create a Greeting Function",
                        "description": "Write a function that takes a name as input and returns a greeting message",
                        "starter_code": "def greet(name):\n    # Your code here\n    pass",
                        "expected_output": "Hello, [name]!",
                        "hints": ["Use the return statement", "Use string concatenation or f-strings"],
                        "solution": "def greet(name):\n    return f'Hello, {name}!'",
                        "encouragement": "You've got this! This is a great way to practice functions."
                    },
                    {
                        "title": "Calculator Function",
                        "description": "Create a function that adds two numbers",
                        "starter_code": "def add_numbers(a, b):\n    # Your code here\n    pass",
                        "expected_output": "Sum of the two numbers",
                        "hints": ["Use the + operator", "Don't forget to return the result"],
                        "solution": "def add_numbers(a, b):\n    return a + b",
                        "encouragement": "Take your time with this - there's no rush to perfection!"
                    }
                ]
        
        return [
            {
                "title": f"Practice {topic}",
                "description": f"A {difficulty} level exercise for {topic}",
                "starter_code": "# Your code here",
                "hints": ["Break it down step by step", "Think about what you want to achieve"],
                "encouragement": f"Remember, every expert was once a beginner. {topic} will help you grow!"
            }
        ]
    
    def explain_concept(self, concept: str, level: str = "beginner") -> str:
        """Explain a programming concept at the appropriate level"""
        prompt = f"Please explain the programming concept '{concept}' for a {level} level student."
        return self.teach(prompt, topic=concept)
    
    def review_code(self, code: str, language: str = "python") -> str:
        """Review and provide feedback on student code"""
        prompt = f"""Please review this {language} code and provide educational feedback:

```{language}
{code}
```

Focus on:
1. Code correctness
2. Best practices
3. Learning opportunities
4. Suggestions for improvement"""
        
        return self.teach(prompt, topic=f"{language} code review")


# Backward compatibility
class TutorAgent(EnhancedTutorAgent):
    """Backward compatibility wrapper"""
    pass
