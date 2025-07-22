"""
Enhanced GoalAgent - Progress tracking and motivational coach with emotional intelligence
"""

import sys
import os
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class EnhancedGoalAgent:
    """
    A motivational coach that helps students set, track, and achieve their learning goals
    """
    
    def __init__(self, llm_client, student_id: str = "default_student"):
        self.llm_client = llm_client
        self.student_id = student_id
        self.agent_type = "goal_coach"
        
        # Student goals and achievements
        self.student_goals = []
        self.achievements = []
        self.progress_history = []
        
        # Motivational personality traits
        self.personality_traits = {
            "motivation": 0.95,    # Highly motivating
            "optimism": 0.9,       # Very optimistic
            "empathy": 0.85,       # Understanding of struggles
            "accountability": 0.9,  # Helps maintain accountability
            "celebration": 0.95,   # Great at celebrating wins
            "resilience": 0.88     # Helps build resilience
        }
        
        # Motivational strategies based on emotional states
        self.motivational_strategies = {
            "discouraged": {
                "approach": "Focus on progress made, reframe setbacks as learning, celebrate small wins",
                "tone": "warm, encouraging, hopeful",
                "techniques": ["progress highlighting", "reframing", "small goal setting"],
                "affirmations": "You've already come so far. Every small step counts."
            },
            "overwhelmed": {
                "approach": "Break goals into micro-steps, focus on just the next action",
                "tone": "calm, reassuring, organized",
                "techniques": ["goal decomposition", "next-action focusing", "stress relief"],
                "affirmations": "You don't have to do everything at once. One step at a time."
            },
            "stuck": {
                "approach": "Explore different approaches, adjust strategies, find accountability",
                "tone": "collaborative, problem-solving",
                "techniques": ["strategy adjustment", "alternative paths", "support building"],
                "affirmations": "Being stuck is temporary. Let's find a new way forward."
            },
            "motivated": {
                "approach": "Harness momentum, set ambitious milestones, create action plans",
                "tone": "energetic, enthusiastic, challenging",
                "techniques": ["momentum building", "stretch goals", "action planning"],
                "affirmations": "Your motivation is powerful! Let's make the most of this energy."
            },
            "anxious": {
                "approach": "Create clear plans, reduce uncertainty, build confidence gradually",
                "tone": "calm, structured, supportive",
                "techniques": ["planning", "uncertainty reduction", "gradual confidence building"],
                "affirmations": "Having a clear plan helps. You're more capable than you realize."
            },
            "celebrating": {
                "approach": "Acknowledge achievement, reinforce positive behaviors, set next milestone",
                "tone": "joyful, proud, forward-looking",
                "techniques": ["achievement recognition", "behavior reinforcement", "next level planning"],
                "affirmations": "You did it! This success shows what you're capable of."
            }
        }
        
        # Goal templates and frameworks
        self.goal_frameworks = {
            "SMART": {
                "description": "Specific, Measurable, Achievable, Relevant, Time-bound",
                "questions": [
                    "What exactly do you want to accomplish?",
                    "How will you measure success?",
                    "Is this realistically achievable?",
                    "Why is this important to you?",
                    "When do you want to complete this?"
                ]
            },
            "OKR": {
                "description": "Objectives and Key Results",
                "questions": [
                    "What is your inspiring objective?",
                    "What are 2-3 measurable key results?",
                    "How will you track progress?",
                    "What's your timeline?"
                ]
            },
            "Habit_Building": {
                "description": "Building sustainable learning habits",
                "questions": [
                    "What habit do you want to build?",
                    "When will you do this each day?",
                    "How will you track it?",
                    "What's your reward system?"
                ]
            }
        }
        
        # Achievement levels and rewards
        self.achievement_levels = {
            "First Step": {"points": 10, "icon": "🌱", "description": "Taking the first action"},
            "Momentum Builder": {"points": 25, "icon": "🚀", "description": "Consistent progress for 3 days"},
            "Week Warrior": {"points": 50, "icon": "⚡", "description": "One week of consistent effort"},
            "Goal Crusher": {"points": 100, "icon": "🏆", "description": "Completing a major goal"},
            "Resilient Learner": {"points": 75, "icon": "💪", "description": "Bouncing back from setbacks"},
            "Habit Master": {"points": 150, "icon": "🎯", "description": "30 days of consistent habits"}
        }
    
    def coach(self, request: str, current_goal: Optional[str] = None, progress_update: Optional[float] = None) -> str:
        """
        Provide motivational coaching and goal guidance
        """
        logger.info(f"GoalAgent coaching: {request[:50]}...")
        
        # Analyze student's motivational state
        motivation_analysis = self._analyze_motivational_state(request)
        
        # Determine coaching approach
        strategy = self._select_motivational_strategy(motivation_analysis)
        
        # Check for goal-related actions (setting, updating, completing)
        goal_action = self._detect_goal_action(request)
        
        # Generate coaching response
        response = self._generate_coaching_response(
            request=request,
            current_goal=current_goal,
            progress_update=progress_update,
            motivation_analysis=motivation_analysis,
            strategy=strategy,
            goal_action=goal_action
        )
        
        # Handle any goal management tasks
        self._handle_goal_management(goal_action, request, current_goal, progress_update)
        
        return response
    
    def _analyze_motivational_state(self, request: str) -> Dict[str, Any]:
        """Analyze student's current motivational and emotional state"""
        request_lower = request.lower()
        
        # Detect motivational states
        state_keywords = {
            "discouraged": ["discouraged", "giving up", "can't do", "too hard", "failing", "hopeless"],
            "overwhelmed": ["overwhelmed", "too much", "stressed", "pressure", "can't handle"],
            "stuck": ["stuck", "not progressing", "plateau", "same place", "not moving forward"],
            "motivated": ["motivated", "excited", "ready", "determined", "energized", "pumped"],
            "anxious": ["anxious", "worried", "nervous", "scared", "uncertain", "doubt"],
            "celebrating": ["achieved", "completed", "finished", "success", "did it", "accomplished"],
            "procrastinating": ["procrastinating", "avoiding", "putting off", "don't want to"],
            "confused": ["confused", "don't understand", "unclear", "lost", "don't know how"]
        }
        
        detected_states = {}
        for state, keywords in state_keywords.items():
            score = sum(1 for keyword in keywords if keyword in request_lower)
            if score > 0:
                detected_states[state] = score
        
        primary_state = "neutral"
        if detected_states:
            primary_state = max(detected_states.keys(), key=lambda x: detected_states[x])
        
        # Detect progress indicators
        progress_indicators = {
            "making_progress": ["making progress", "getting better", "improving", "learning"],
            "struggling": ["struggling", "difficult", "hard time", "challenges"],
            "breakthrough": ["breakthrough", "finally got it", "clicked", "understand now"]
        }
        
        progress_state = "unknown"
        for state, indicators in progress_indicators.items():
            if any(indicator in request_lower for indicator in indicators):
                progress_state = state
                break
        
        return {
            "primary_state": primary_state,
            "all_states": detected_states,
            "progress_state": progress_state,
            "needs_encouragement": primary_state in ["discouraged", "stuck", "overwhelmed"],
            "needs_planning": primary_state in ["overwhelmed", "confused", "stuck"],
            "needs_celebration": primary_state in ["celebrating", "breakthrough"],
            "motivation_level": "high" if primary_state in ["motivated", "celebrating"] else
                               "low" if primary_state in ["discouraged", "procrastinating"] else "medium"
        }
    
    def _select_motivational_strategy(self, motivation_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Select appropriate motivational strategy"""
        primary_state = motivation_analysis.get("primary_state", "neutral")
        
        if primary_state in self.motivational_strategies:
            return self.motivational_strategies[primary_state]
        else:
            # Default motivational strategy
            return {
                "approach": "Provide encouragement and help clarify next steps",
                "tone": "supportive, clear, encouraging",
                "techniques": ["goal clarification", "next steps", "encouragement"],
                "affirmations": "You're on a learning journey, and every step matters."
            }
    
    def _detect_goal_action(self, request: str) -> Dict[str, Any]:
        """Detect if student wants to set, update, or complete goals"""
        request_lower = request.lower()
        
        actions = {
            "set_goal": ["set a goal", "want to achieve", "goal is", "want to learn", "my goal"],
            "update_progress": ["made progress", "completed", "finished", "done with", "update"],
            "complete_goal": ["achieved", "finished my goal", "completed my goal", "goal accomplished"],
            "need_help": ["stuck on", "struggling with", "need help", "don't know how"],
            "change_goal": ["change my goal", "different goal", "new goal", "modify goal"]
        }
        
        detected_actions = []
        for action, keywords in actions.items():
            if any(keyword in request_lower for keyword in keywords):
                detected_actions.append(action)
        
        primary_action = detected_actions[0] if detected_actions else None
        
        return {
            "primary_action": primary_action,
            "all_actions": detected_actions,
            "goal_related": len(detected_actions) > 0
        }
    
    def _generate_coaching_response(self, request: str, current_goal: Optional[str], progress_update: Optional[float],
                                  motivation_analysis: Dict[str, Any], strategy: Dict[str, Any],
                                  goal_action: Dict[str, Any]) -> str:
        """Generate personalized coaching response"""
        
        # Build coaching system prompt
        system_prompt = self._build_coaching_system_prompt(motivation_analysis, strategy)
        
        # Build contextual prompt
        user_prompt = self._build_coaching_prompt(request, current_goal, progress_update, 
                                                motivation_analysis, goal_action)
        
        try:
            response = self.llm_client.generate_response(
                prompt=user_prompt,
                system_message=system_prompt,
                max_tokens=400,
                temperature=0.8  # Slightly more creative for motivational content
            )
            
            # Add personalized motivational elements
            enhanced_response = self._enhance_with_motivation(response, motivation_analysis, strategy)
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"Error generating goal coaching response: {e}")
            return self._generate_coaching_fallback(request, motivation_analysis, strategy)
    
    def _build_coaching_system_prompt(self, motivation_analysis: Dict[str, Any], 
                                    strategy: Dict[str, Any]) -> str:
        """Build system prompt for goal coaching personality"""
        
        primary_state = motivation_analysis.get("primary_state", "neutral")
        
        return f"""You are Jordan, an expert goal-setting coach and motivational specialist. You have years of experience helping students achieve their learning goals and building their confidence.

STUDENT CURRENT STATE:
- Motivational state: {primary_state}
- Motivation level: {motivation_analysis.get('motivation_level', 'medium')}
- Needs encouragement: {motivation_analysis.get('needs_encouragement', False)}
- Needs planning: {motivation_analysis.get('needs_planning', False)}
- Progress state: {motivation_analysis.get('progress_state', 'unknown')}

COACHING STRATEGY:
- Approach: {strategy['approach']}
- Tone: {strategy['tone']}
- Techniques: {', '.join(strategy['techniques'])}
- Core message: {strategy['affirmations']}

YOUR PERSONALITY:
- Incredibly motivating and inspiring
- Believes deeply in every student's potential
- Uses specific, actionable advice
- Celebrates all progress, no matter how small
- Helps reframe setbacks as learning opportunities
- Creates clear, achievable next steps
- Balances optimism with realistic planning

RESPONSE GUIDELINES:
1. Acknowledge their current emotional state with genuine empathy
2. Use the recommended tone and approach
3. Provide specific, actionable advice
4. Include motivational affirmations naturally
5. Help them see progress they might be missing
6. Create clear next steps
7. Be inspiring but realistic
8. Use their name or "you" to make it personal

Remember: Your role is to help them believe in themselves while providing practical guidance to achieve their goals."""
        
        return system_prompt
    
    def _build_coaching_prompt(self, request: str, current_goal: Optional[str], progress_update: Optional[float],
                             motivation_analysis: Dict[str, Any], goal_action: Dict[str, Any]) -> str:
        """Build context-rich prompt for coaching"""
        
        prompt_parts = [f"Student Request: {request}"]
        
        if current_goal:
            prompt_parts.append(f"Current Goal: {current_goal}")
        
        if progress_update is not None:
            prompt_parts.append(f"Progress Update: {progress_update}/10")
        
        prompt_parts.append(f"Motivational State: {motivation_analysis['primary_state']}")
        
        if goal_action["goal_related"]:
            prompt_parts.append(f"Goal Action Detected: {goal_action['primary_action']}")
        
        # Add context about previous goals if available
        if self.student_goals:
            recent_goals = [goal["title"] for goal in self.student_goals[-2:]]
            prompt_parts.append(f"Recent Goals: {', '.join(recent_goals)}")
        
        # Add achievements context
        if self.achievements:
            recent_achievements = [ach["title"] for ach in self.achievements[-2:]]
            prompt_parts.append(f"Recent Achievements: {', '.join(recent_achievements)}")
        
        return "\n\n".join(prompt_parts)
    
    def _enhance_with_motivation(self, response: str, motivation_analysis: Dict[str, Any], 
                               strategy: Dict[str, Any]) -> str:
        """Add motivational elements and achievements to the response"""
        
        primary_state = motivation_analysis.get("primary_state", "neutral")
        
        # Add achievement recognition if appropriate
        if motivation_analysis.get("needs_celebration", False):
            if "congratulations" not in response.lower():
                response = "🎉 Congratulations! " + response
        
        # Add affirmation if not already present
        affirmation = strategy.get("affirmations", "")
        if affirmation and affirmation.lower() not in response.lower():
            response += f"\n\n💫 *Remember: {affirmation}*"
        
        # Add motivational emoji and formatting
        if primary_state == "discouraged":
            response += "\n\n🌟 You've got this! Every expert was once a beginner."
        elif primary_state == "motivated":
            response += "\n\n🚀 I love your energy! Let's channel it into action!"
        elif primary_state == "overwhelmed":
            response += "\n\n🧘‍♀️ Take it one step at a time. You don't have to do everything at once."
        
        # Add progress insights if available
        if len(self.progress_history) > 2:
            response += f"\n\n📈 **Progress Insight:** You've been consistently working on your goals - that's the key to success!"
        
        return response
    
    def _generate_coaching_fallback(self, request: str, motivation_analysis: Dict[str, Any],
                                  strategy: Dict[str, Any]) -> str:
        """Generate fallback coaching response, enhanced with LLM when available"""
        
        primary_state = motivation_analysis.get("primary_state", "neutral")
        affirmation = strategy.get("affirmations", "You're capable of more than you realize.")
        
        # Try to use LLM for better fallback response
        if hasattr(self, 'llm_client') and self.llm_client:
            try:
                fallback_prompt = f"""As Jordan, a motivational goal coach, respond to this student when experiencing technical difficulties:

Student Request: "{request}"
Student State: {primary_state}
Strategy Affirmation: {affirmation}
Approach: {strategy.get('approach', 'encouraging support')}

Create a motivational response that:
1. Acknowledges their {primary_state} state with genuine empathy
2. Provides the affirmation naturally in the response
3. Offers 3 specific, actionable steps they can take
4. Maintains an inspiring but realistic tone
5. Ends with a question to engage them

Be encouraging, specific, and genuinely helpful even during technical issues."""

                response = self.llm_client.generate_response(
                    prompt=fallback_prompt,
                    max_tokens=300,
                    temperature=0.8
                )
                
                return response
                
            except Exception as e:
                logger.error(f"LLM coaching fallback failed: {e}")
        
        # Hardcoded fallback when LLM is unavailable
        state_responses = {
            "discouraged": f"""I hear that you're feeling discouraged, and that's completely understandable. Learning can be challenging, and it's normal to have moments of doubt.

Here's what I want you to remember: **{affirmation}**

🎯 **Let's refocus:**
1. **Acknowledge your progress** - What have you learned recently, even if it seems small?
2. **Adjust your approach** - Maybe try a different learning method or break things into smaller steps
3. **Celebrate small wins** - Every bit of progress counts and builds momentum

What's one small thing you can do today to move forward? I believe in you! 💪""",

            "motivated": f"""I love your motivation and energy! This is the perfect time to harness that drive and create real momentum.

**{affirmation}**

🚀 **Let's make the most of this energy:**
1. **Set a clear goal** - What specifically do you want to accomplish?
2. **Create action steps** - Break it down into daily actions
3. **Track your progress** - Celebrate each milestone along the way

Your motivation is powerful - let's turn it into lasting progress! What's your most important goal right now? 🌟""",

            "overwhelmed": f"""I can hear that you're feeling overwhelmed, and that's okay. When we have big goals, it's easy to feel like there's too much to do.

**{affirmation}**

🧘‍♀️ **Let's simplify:**
1. **Pick ONE thing** - What's the most important thing to focus on today?
2. **Make it smaller** - Break that one thing into tiny, manageable steps
3. **Just start** - Even 10 minutes of progress is valuable

You don't have to do everything at once. What's one small step you can take right now? 🌱"""
        }
        
        if primary_state in state_responses:
            return state_responses[primary_state]
        else:
            return f"""Thanks for sharing with me! I'm here to help you achieve your learning goals.

**{affirmation}**

🎯 **Here's how I can help:**
- **Goal Setting** - Let's create clear, achievable goals together
- **Progress Tracking** - I'll help you see and celebrate your progress
- **Motivation** - When things get tough, I'll help you stay on track
- **Planning** - We'll break big goals into manageable steps

What would you like to work on? I'm excited to support your learning journey! 🚀"""
    
    def _handle_goal_management(self, goal_action: Dict[str, Any], request: str, 
                              current_goal: Optional[str], progress_update: Optional[float]):
        """Handle goal-related actions like setting, updating, or completing goals"""
        
        if not goal_action["goal_related"]:
            return
        
        action = goal_action["primary_action"]
        
        if action == "set_goal":
            self._create_goal_from_request(request)
        elif action == "update_progress" and current_goal and progress_update is not None:
            self._update_goal_progress(current_goal, progress_update)
        elif action == "complete_goal" and current_goal:
            self._complete_goal(current_goal)
        
        # Record progress history
        self.progress_history.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "request": request,
            "goal": current_goal,
            "progress": progress_update
        })
    
    def _create_goal_from_request(self, request: str):
        """Extract and create a goal from student request"""
        
        # Simple goal extraction (could be enhanced with NLP)
        goal_title = request[:100] if len(request) <= 100 else request[:97] + "..."
        
        new_goal = {
            "id": len(self.student_goals) + 1,
            "title": goal_title,
            "description": request,
            "created_date": datetime.now().isoformat(),
            "target_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "progress": 0.0,
            "status": "active",
            "category": "learning"
        }
        
        self.student_goals.append(new_goal)
    
    def _update_goal_progress(self, goal_title: str, progress: float):
        """Update progress for a specific goal"""
        
        for goal in self.student_goals:
            if goal_title.lower() in goal["title"].lower():
                old_progress = goal["progress"]
                goal["progress"] = progress
                goal["last_updated"] = datetime.now().isoformat()
                
                # Check for achievement unlock
                if progress >= 10.0 and old_progress < 10.0:
                    self._unlock_achievement("Goal Crusher", f"Completed goal: {goal['title']}")
                elif progress > old_progress + 2.0:
                    self._unlock_achievement("Momentum Builder", "Making consistent progress")
                
                break
    
    def _complete_goal(self, goal_title: str):
        """Mark a goal as completed"""
        
        for goal in self.student_goals:
            if goal_title.lower() in goal["title"].lower():
                goal["status"] = "completed"
                goal["completed_date"] = datetime.now().isoformat()
                goal["progress"] = 10.0
                
                self._unlock_achievement("Goal Crusher", f"Completed: {goal['title']}")
                break
    
    def _unlock_achievement(self, achievement_name: str, description: str):
        """Unlock an achievement for the student"""
        
        if achievement_name in self.achievement_levels:
            achievement_data = self.achievement_levels[achievement_name]
            
            new_achievement = {
                "title": achievement_name,
                "description": description,
                "icon": achievement_data["icon"],
                "points": achievement_data["points"],
                "unlocked_date": datetime.now().isoformat()
            }
            
            self.achievements.append(new_achievement)
    
    def set_smart_goal(self, goal_description: str, timeline_days: int = 30) -> Dict[str, Any]:
        """Help create a SMART goal"""
        
        smart_goal = {
            "original_description": goal_description,
            "specific": f"Learn {goal_description}",
            "measurable": "Complete exercises and demonstrate understanding",
            "achievable": "Break into daily study sessions",
            "relevant": "Supports programming skill development",
            "time_bound": f"Complete within {timeline_days} days",
            "action_steps": [
                "Identify specific topics to learn",
                "Find learning resources",
                "Create daily study schedule",
                "Practice with exercises",
                "Track progress weekly"
            ],
            "success_metrics": [
                "Complete daily study sessions",
                "Finish practice exercises",
                "Explain concepts to others",
                "Build a small project"
            ]
        }
        
        return smart_goal
    
    def get_progress_report(self) -> Dict[str, Any]:
        """Generate a comprehensive progress report"""
        
        active_goals = [g for g in self.student_goals if g["status"] == "active"]
        completed_goals = [g for g in self.student_goals if g["status"] == "completed"]
        
        total_points = sum(ach["points"] for ach in self.achievements)
        
        return {
            "summary": {
                "total_goals": len(self.student_goals),
                "active_goals": len(active_goals),
                "completed_goals": len(completed_goals),
                "total_achievement_points": total_points,
                "achievements_unlocked": len(self.achievements)
            },
            "active_goals": active_goals,
            "recent_achievements": self.achievements[-3:] if len(self.achievements) >= 3 else self.achievements,
            "motivation_insights": self._generate_motivation_insights(),
            "next_steps": self._suggest_next_steps()
        }
    
    def _generate_motivation_insights(self) -> List[str]:
        """Generate insights about student's motivation patterns"""
        
        if not self.progress_history:
            return ["Start setting goals to build motivation insights!"]
        
        insights = []
        
        # Analyze recent progress
        recent_updates = [p for p in self.progress_history[-10:] if p["action"] == "update_progress"]
        if recent_updates:
            insights.append("You're actively tracking your progress - great habit!")
        
        # Check goal completion rate
        if len(self.student_goals) > 0:
            completion_rate = len([g for g in self.student_goals if g["status"] == "completed"]) / len(self.student_goals)
            if completion_rate > 0.7:
                insights.append("You have an excellent goal completion rate!")
            elif completion_rate > 0.3:
                insights.append("You're making good progress on your goals.")
            else:
                insights.append("Consider breaking goals into smaller, more achievable steps.")
        
        return insights
    
    def _suggest_next_steps(self) -> List[str]:
        """Suggest next steps based on current progress"""
        
        suggestions = []
        
        active_goals = [g for g in self.student_goals if g["status"] == "active"]
        
        if not active_goals:
            suggestions.append("Set a new learning goal to get started!")
        else:
            # Find goals that haven't been updated recently
            for goal in active_goals:
                if goal.get("last_updated"):
                    last_update = datetime.fromisoformat(goal["last_updated"])
                    if (datetime.now() - last_update).days > 7:
                        suggestions.append(f"Update progress on: {goal['title']}")
                else:
                    suggestions.append(f"Track progress on: {goal['title']}")
        
        if len(self.achievements) == 0:
            suggestions.append("Complete your first study session to unlock achievements!")
        
        return suggestions[:3]  # Return top 3 suggestions


# Backward compatibility
class GoalAgent(EnhancedGoalAgent):
    """Backward compatibility wrapper"""
    pass
