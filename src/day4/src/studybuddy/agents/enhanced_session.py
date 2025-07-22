"""
Enhanced SessionAgent - Time management and productivity specialist with emotional intelligence
"""

import sys
import os
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class EnhancedSessionAgent:
    """
    A productivity coach that helps students manage their time and study sessions effectively
    """
    
    def __init__(self, llm_client, student_id: str = "default_student"):
        self.llm_client = llm_client
        self.student_id = student_id
        self.agent_type = "session_manager"
        
        # Session history for this student
        self.session_history = []
        self.productivity_data = {
            "total_sessions": 0,
            "total_focus_time": 0,
            "preferred_session_length": 25,  # Default Pomodoro
            "best_time_of_day": None,
            "productivity_patterns": {},
            "break_preferences": "short_active"
        }
        
        # Personality traits for session management
        self.personality_traits = {
            "organization": 0.95,  # Highly organized
            "motivation": 0.9,     # Very motivating
            "flexibility": 0.8,    # Adapts to student needs
            "accountability": 0.85, # Helps students stay accountable
            "energy": 0.8,         # Energetic and encouraging
            "empathy": 0.9         # Understanding of study struggles
        }
        
        # Emotional strategies for productivity
        self.productivity_strategies = {
            "overwhelmed": {
                "approach": "Break tasks into tiny, manageable pieces. Focus on just the next small step.",
                "session_type": "micro_sessions",
                "duration": 15,
                "break_type": "calming",
                "encouragement": "You don't have to do everything at once. Small progress is still progress!"
            },
            "tired": {
                "approach": "Use active learning techniques and take energizing breaks.",
                "session_type": "active_learning",
                "duration": 20,
                "break_type": "energizing",
                "encouragement": "Let's find ways to re-energize while we learn!"
            },
            "distracted": {
                "approach": "Remove distractions and use focused time blocks with clear goals.",
                "session_type": "deep_focus",
                "duration": 25,
                "break_type": "mindful",
                "encouragement": "Focus is a skill that improves with practice. You've got this!"
            },
            "motivated": {
                "approach": "Harness that energy with challenging tasks and achievement goals.",
                "session_type": "power_session",
                "duration": 45,
                "break_type": "short_active",
                "encouragement": "I love your energy! Let's make the most of this motivation!"
            },
            "anxious": {
                "approach": "Create structure and predictability with clear plans and achievable goals.",
                "session_type": "structured",
                "duration": 20,
                "break_type": "relaxing",
                "encouragement": "Having a clear plan can really help with anxiety. We'll take this step by step."
            }
        }
        
        # Session templates
        self.session_templates = {
            "pomodoro": {
                "work_duration": 25,
                "short_break": 5,
                "long_break": 15,
                "cycles_before_long_break": 4,
                "description": "Classic Pomodoro technique for sustained focus"
            },
            "micro_sessions": {
                "work_duration": 15,
                "break_duration": 5,
                "description": "Short sessions for when feeling overwhelmed"
            },
            "deep_focus": {
                "work_duration": 50,
                "break_duration": 10,
                "description": "Longer sessions for complex topics"
            },
            "power_session": {
                "work_duration": 45,
                "break_duration": 15,
                "description": "High-energy sessions when motivated"
            }
        }
    
    def manage_time(self, request: str, current_topic: str = "studying", 
                   available_time: int = 60) -> str:
        """
        Provide time management assistance adapted to student's current state
        """
        logger.info(f"SessionAgent managing time: {request[:50]}...")
        
        # Analyze student's current state
        state_analysis = self._analyze_student_state(request)
        
        # Select appropriate productivity strategy
        strategy = self._select_productivity_strategy(state_analysis)
        
        # Create personalized time management plan
        time_plan = self._create_time_management_plan(
            request=request,
            topic=current_topic,
            available_time=available_time,
            student_state=state_analysis,
            strategy=strategy
        )
        
        # Generate empathetic response
        response = self._generate_productivity_response(
            request=request,
            time_plan=time_plan,
            strategy=strategy,
            state_analysis=state_analysis
        )
        
        # Store session data
        self._record_session_request(request, time_plan, state_analysis)
        
        return response
    
    def _analyze_student_state(self, request: str) -> Dict[str, Any]:
        """Analyze student's current emotional and productivity state"""
        request_lower = request.lower()
        
        # Detect productivity-related emotions
        state_keywords = {
            "overwhelmed": ["overwhelmed", "too much", "stressed", "can't handle", "drowning"],
            "tired": ["tired", "exhausted", "sleepy", "worn out", "drained", "low energy"],
            "distracted": ["distracted", "can't focus", "keep getting distracted", "mind wandering"],
            "motivated": ["motivated", "ready", "energized", "excited to learn", "let's do this"],
            "anxious": ["anxious", "worried", "nervous", "stressed about", "pressure"],
            "procrastinating": ["procrastinating", "putting off", "avoiding", "don't want to start"],
            "frustrated": ["frustrated", "stuck", "not working", "annoying"]
        }
        
        detected_states = {}
        for state, keywords in state_keywords.items():
            score = sum(1 for keyword in keywords if keyword in request_lower)
            if score > 0:
                detected_states[state] = score
        
        primary_state = "neutral"
        if detected_states:
            primary_state = max(detected_states.keys(), key=lambda x: detected_states[x])
        
        # Detect time-related information
        time_pressure = any(word in request_lower for word in ["deadline", "due", "urgent", "quickly", "rush"])
        
        # Detect available time hints
        available_time_hints = self._extract_time_mentions(request)
        
        return {
            "primary_state": primary_state,
            "all_states": detected_states,
            "time_pressure": time_pressure,
            "available_time_hints": available_time_hints,
            "needs_structure": primary_state in ["overwhelmed", "anxious", "distracted"],
            "needs_energy": primary_state in ["tired", "procrastinating"],
            "confidence_level": "high" if primary_state == "motivated" else 
                               "low" if primary_state in ["overwhelmed", "frustrated"] else "medium"
        }
    
    def _extract_time_mentions(self, text: str) -> Dict[str, Any]:
        """Extract time-related information from the request"""
        import re
        
        # Look for time mentions
        time_patterns = [
            r"(\d+)\s*(hour|hr|h)\s*",
            r"(\d+)\s*(minute|min|m)\s*",
            r"(\d+)\s*(day|days)\s*"
        ]
        
        time_mentions = {}
        for pattern in time_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                amount, unit = match
                time_mentions[unit] = int(amount)
        
        return time_mentions
    
    def _select_productivity_strategy(self, state_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Select appropriate productivity strategy based on student's state"""
        primary_state = state_analysis.get("primary_state", "neutral")
        
        if primary_state in self.productivity_strategies:
            return self.productivity_strategies[primary_state]
        else:
            # Default strategy
            return {
                "approach": "Use balanced study sessions with regular breaks.",
                "session_type": "pomodoro",
                "duration": 25,
                "break_type": "short_active",
                "encouragement": "Let's create a productive study rhythm!"
            }
    
    def _create_time_management_plan(self, request: str, topic: str, available_time: int,
                                   student_state: Dict[str, Any], strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Create a detailed time management plan"""
        
        session_type = strategy.get("session_type", "pomodoro")
        recommended_duration = strategy.get("duration", 25)
        
        # Adjust for available time
        if available_time < recommended_duration:
            session_type = "micro_sessions"
            recommended_duration = min(15, available_time - 5)
        
        # Get session template
        template = self.session_templates.get(session_type, self.session_templates["pomodoro"])
        
        # Calculate number of sessions possible
        work_duration = template.get("work_duration", recommended_duration)
        break_duration = template.get("break_duration", 5)
        cycle_duration = work_duration + break_duration
        
        possible_cycles = max(1, available_time // cycle_duration)
        
        # Create detailed schedule
        schedule = []
        current_time = 0
        
        for cycle in range(possible_cycles):
            schedule.append({
                "type": "work",
                "duration": work_duration,
                "start_time": current_time,
                "activity": f"Focus on {topic}",
                "tips": self._get_focus_tips(student_state, cycle)
            })
            current_time += work_duration
            
            if cycle < possible_cycles - 1:  # Don't add break after last session
                schedule.append({
                    "type": "break",
                    "duration": break_duration,
                    "start_time": current_time,
                    "activity": self._get_break_activity(strategy.get("break_type", "short_active")),
                    "tips": ["Truly disconnect from work", "Move your body", "Hydrate"]
                })
                current_time += break_duration
        
        return {
            "session_type": session_type,
            "total_time": current_time,
            "work_sessions": possible_cycles,
            "work_duration": work_duration,
            "break_duration": break_duration,
            "schedule": schedule,
            "strategy_rationale": strategy["approach"],
            "personalization": f"Customized for {student_state['primary_state']} state"
        }
    
    def _get_focus_tips(self, student_state: Dict[str, Any], session_number: int) -> List[str]:
        """Get personalized focus tips based on student state"""
        primary_state = student_state.get("primary_state", "neutral")
        
        base_tips = [
            "Remove phone or put it in airplane mode",
            "Have water nearby",
            "Set a clear goal for this session"
        ]
        
        state_specific_tips = {
            "overwhelmed": [
                "Focus on just one small task",
                "Remind yourself: you only need to work for this short time",
                "Breathe deeply if you feel stress rising"
            ],
            "tired": [
                "Sit up straight and ensure good lighting",
                "Try reading out loud or explaining concepts aloud",
                "Take deep breaths to oxygenate your brain"
            ],
            "distracted": [
                "Close all browser tabs except what you need",
                "Put on focus music or white noise",
                "Write down distracting thoughts to deal with later"
            ],
            "motivated": [
                "Set an ambitious but achievable goal",
                "Challenge yourself with harder concepts",
                "Use this energy to tackle the most difficult parts"
            ]
        }
        
        tips = base_tips.copy()
        if primary_state in state_specific_tips:
            tips.extend(state_specific_tips[primary_state])
        
        # Add session-specific tips
        if session_number == 0:
            tips.append("Start with something you enjoy or find easy to build momentum")
        elif session_number > 2:
            tips.append("You're doing great! Stay strong through this session")
        
        return tips[:4]  # Return top 4 tips
    
    def _get_break_activity(self, break_type: str) -> str:
        """Get appropriate break activity based on type"""
        
        activities = {
            "calming": "Take slow, deep breaths or do a brief meditation",
            "energizing": "Do jumping jacks, stretch, or walk around",
            "short_active": "Stand up, stretch your arms and neck, walk to get water",
            "mindful": "Look out the window, practice deep breathing, or do a mindfulness minute",
            "relaxing": "Listen to calming music, gentle stretching, or close your eyes and rest"
        }
        
        return activities.get(break_type, "Take a short walk and hydrate")
    
    def _generate_productivity_response(self, request: str, time_plan: Dict[str, Any],
                                      strategy: Dict[str, Any], state_analysis: Dict[str, Any]) -> str:
        """Generate personalized productivity guidance using the LLM"""
        
        # Build system prompt for session management
        system_prompt = self._build_session_manager_prompt(state_analysis, strategy)
        
        # Build detailed user prompt
        user_prompt = self._build_time_management_prompt(request, time_plan, state_analysis)
        
        try:
            response = self.llm_client.generate_response(
                prompt=user_prompt,
                system_message=system_prompt,
                max_tokens=350,
                temperature=0.7
            )
            
            # Add schedule details
            enhanced_response = self._add_schedule_details(response, time_plan)
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"Error generating session response: {e}")
            return self._generate_productivity_fallback(request, time_plan, state_analysis)
    
    def _build_session_manager_prompt(self, state_analysis: Dict[str, Any], 
                                    strategy: Dict[str, Any]) -> str:
        """Build system prompt for session manager personality"""
        
        primary_state = state_analysis.get("primary_state", "neutral")
        
        return f"""You are Sam, an expert productivity coach and time management specialist. You're incredibly organized, motivating, and understand the psychology of studying and focus.

STUDENT CURRENT STATE:
- Primary state: {primary_state}
- Needs structure: {state_analysis.get('needs_structure', False)}
- Needs energy: {state_analysis.get('needs_energy', False)}
- Time pressure: {state_analysis.get('time_pressure', False)}

RECOMMENDED STRATEGY:
- Approach: {strategy['approach']}
- Session type: {strategy['session_type']}
- Encouragement: {strategy['encouragement']}

YOUR PERSONALITY:
- Highly organized and systematic
- Motivating and energetic
- Empathetic to study struggles
- Practical and solution-focused
- Encouraging but realistic
- Helps students build sustainable habits

RESPONSE GUIDELINES:
1. Acknowledge their current state with empathy
2. Explain why the recommended approach will work for them
3. Provide practical, actionable advice
4. Be encouraging but realistic about challenges
5. Help them see productivity as a skill they're building
6. Make time management feel achievable, not overwhelming

Remember: Good time management is about working WITH your brain and energy, not against it."""
        
        return system_prompt
    
    def _build_time_management_prompt(self, request: str, time_plan: Dict[str, Any],
                                    state_analysis: Dict[str, Any]) -> str:
        """Build context-rich prompt for time management advice"""
        
        prompt_parts = [
            f"Student Request: {request}",
            f"Current State: {state_analysis['primary_state']}",
            f"Recommended Session Type: {time_plan['session_type']}",
            f"Available Time: {time_plan['total_time']} minutes",
            f"Number of Work Sessions: {time_plan['work_sessions']}",
            f"Strategy Rationale: {time_plan['strategy_rationale']}"
        ]
        
        return "\n\n".join(prompt_parts)
    
    def _add_schedule_details(self, response: str, time_plan: Dict[str, Any]) -> str:
        """Add specific schedule details to the response"""
        
        schedule_text = f"\n\n📅 **Your Personalized Schedule:**\n"
        
        for i, item in enumerate(time_plan["schedule"], 1):
            if item["type"] == "work":
                schedule_text += f"\n🎯 **Session {(i+1)//2}** ({item['duration']} min): {item['activity']}\n"
                schedule_text += f"   💡 *Tips: {', '.join(item['tips'][:2])}*\n"
            else:
                schedule_text += f"\n☕ **Break** ({item['duration']} min): {item['activity']}\n"
        
        schedule_text += f"\n⏱️ **Total productive time: {time_plan['total_time']} minutes**"
        schedule_text += f"\n🎯 **{time_plan['work_sessions']} focused work sessions**"
        
        return response + schedule_text
    
    def _generate_productivity_fallback(self, request: str, time_plan: Dict[str, Any],
                                      state_analysis: Dict[str, Any]) -> str:
        """Generate fallback response for productivity guidance using LLM when available"""
        
        primary_state = state_analysis.get("primary_state", "neutral")
        
        # Try to use LLM for better fallback response
        if hasattr(self, 'llm_client') and self.llm_client:
            try:
                fallback_prompt = f"""As Sam, a productivity coach, respond to this student's time management request when having technical difficulties:

Student Request: "{request}"
Student State: {primary_state}
Recommended Plan: {time_plan['work_sessions']} sessions of {time_plan['work_duration']} minutes

Create an encouraging, practical response that:
1. Acknowledges their current state with empathy
2. Explains the time plan clearly
3. Provides actionable productivity tips
4. Maintains motivation despite technical issues
5. Keeps the tone supportive and energetic

Be conversational and supportive, not robotic."""

                response = self.llm_client.generate_response(
                    prompt=fallback_prompt,
                    max_tokens=250,
                    temperature=0.7
                )
                
                # Add the actual plan details
                return f"{response}\n\n🎯 **Your Plan Details:**\n- {time_plan['work_sessions']} sessions × {time_plan['work_duration']} minutes\n- {time_plan.get('break_duration', 5)}-minute breaks\n- Total focus time: {time_plan['total_time']} minutes"
                
            except Exception as e:
                logger.error(f"LLM fallback failed: {e}")
        
        # Basic hardcoded fallback if LLM unavailable
        encouragement = {
            "overwhelmed": "I understand you're feeling overwhelmed. Let's break this down into manageable pieces.",
            "tired": "I can hear that you're tired. Let's work with your energy level, not against it.",
            "distracted": "Distraction is totally normal! Let's create some structure to help you focus.",
            "motivated": "I love your motivation! Let's channel that energy productively."
        }.get(primary_state, "Let's create a productive study plan together!")
        
        return f"""{encouragement}

Here's what I recommend for your request: "{request}"

🎯 **Your Plan:**
- **{time_plan['work_sessions']} focused sessions** of {time_plan['work_duration']} minutes each
- **Short breaks** of {time_plan.get('break_duration', 5)} minutes between sessions
- **Total time:** {time_plan['total_time']} minutes

🔑 **Key Success Tips:**
1. **Start small** - Even 15 minutes of focused work is valuable
2. **Remove distractions** - Phone away, focus music on
3. **Celebrate progress** - Acknowledge every completed session
4. **Be kind to yourself** - Some days are harder than others

Remember: Productivity isn't about perfection, it's about showing up consistently. You've got this! 💪

Ready to start your first session? I believe in you! 🌟"""
    
    def _record_session_request(self, request: str, time_plan: Dict[str, Any], 
                              state_analysis: Dict[str, Any]):
        """Record session data for learning about student patterns"""
        
        session_record = {
            "timestamp": datetime.now().isoformat(),
            "request": request,
            "student_state": state_analysis["primary_state"],
            "recommended_duration": time_plan["work_duration"],
            "total_time": time_plan["total_time"],
            "session_type": time_plan["session_type"]
        }
        
        self.session_history.append(session_record)
        
        # Update productivity data
        self.productivity_data["total_sessions"] += 1
        
        # Learn patterns (simple implementation)
        state = state_analysis["primary_state"]
        if state in self.productivity_data["productivity_patterns"]:
            self.productivity_data["productivity_patterns"][state] += 1
        else:
            self.productivity_data["productivity_patterns"][state] = 1
    
    def get_productivity_insights(self) -> Dict[str, Any]:
        """Get insights about student's productivity patterns"""
        
        if not self.session_history:
            return {
                "message": "No session data yet. Start using time management to build insights!",
                "suggestion": "Try a few study sessions to help me learn your patterns."
            }
        
        # Analyze patterns
        states = [session["student_state"] for session in self.session_history]
        most_common_state = max(set(states), key=states.count) if states else "neutral"
        
        avg_session_length = sum(s["recommended_duration"] for s in self.session_history) / len(self.session_history)
        
        return {
            "total_sessions_planned": len(self.session_history),
            "most_common_state": most_common_state,
            "average_session_length": round(avg_session_length, 1),
            "productivity_patterns": self.productivity_data["productivity_patterns"],
            "insights": [
                f"You tend to feel {most_common_state} when planning study sessions",
                f"Your average preferred session length is {avg_session_length:.0f} minutes",
                "Keep building these productive habits!"
            ],
            "recommendations": [
                "Try to notice which times of day you feel most motivated",
                "Experiment with different session lengths to find your sweet spot",
                "Celebrate small wins to build positive study associations"
            ]
        }


# Backward compatibility
class SessionAgent(EnhancedSessionAgent):
    """Backward compatibility wrapper"""
    pass
