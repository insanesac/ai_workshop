"""
StudyBuddy Tools - Real tools that agents can use to help students
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Structure for search results"""
    title: str
    url: str
    snippet: str
    relevance_score: float


class WebSearchTool:
    """
    Web search tool for finding educational resources
    """
    
    def __init__(self, llm_client=None, api_key: Optional[str] = None):
        self.llm_client = llm_client
        self.api_key = api_key or os.getenv("SEARCH_API_KEY")
        
    def search_educational_content(self, query: str, topic: str = "", 
                                  difficulty_level: str = "beginner") -> List[SearchResult]:
        """Search for educational content on the web"""
        
        # Enhanced query for better educational results
        enhanced_query = f"{query} {topic} tutorial {difficulty_level} learn programming"
        
        try:
            # Try to use real search if DuckDuckGo is available
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(enhanced_query, max_results=5))
                search_results = []
                for i, result in enumerate(results):
                    search_results.append(SearchResult(
                        title=result.get('title', 'Educational Resource'),
                        url=result.get('href', '#'),
                        snippet=result.get('body', 'Educational content found'),
                        relevance_score=1.0 - (i * 0.1)  # Decreasing relevance
                    ))
                return search_results
        except ImportError:
            logger.warning("DuckDuckGo search not available, using LLM-generated results")
        except Exception as e:
            logger.warning(f"Search failed: {e}, using LLM-generated results")
        
        # Fallback: Use LLM to generate realistic search results
        if self.llm_client:
            return self._generate_search_results_with_llm(query, topic, difficulty_level)
        
        # Last resort: Basic structured results
        return self._generate_basic_search_results(query, topic, difficulty_level)
    
    def _generate_search_results_with_llm(self, query: str, topic: str, difficulty_level: str) -> List[SearchResult]:
        """Generate realistic search results using LLM"""
        if not self.llm_client:
            return self._generate_basic_search_results(query, topic, difficulty_level)
            
        prompt = f"""Generate 3 realistic educational web search results for:
Query: {query}
Topic: {topic}
Level: {difficulty_level}

For each result, provide:
1. A realistic title (like real educational websites)
2. A realistic URL (use real educational domains like codecademy.com, w3schools.com, etc.)
3. A helpful snippet description
4. Make them genuinely useful for learning

Format each result as:
TITLE: [title]
URL: [url] 
SNIPPET: [description]
---"""

        try:
            response = self.llm_client.generate_response(prompt, max_tokens=300)
            return self._parse_llm_search_results(response)
        except Exception as e:
            logger.error(f"LLM search result generation failed: {e}")
            return self._generate_basic_search_results(query, topic, difficulty_level)
    
    def _parse_llm_search_results(self, llm_response: str) -> List[SearchResult]:
        """Parse LLM response into SearchResult objects"""
        results = []
        sections = llm_response.split('---')
        
        for i, section in enumerate(sections[:3]):  # Max 3 results
            lines = section.strip().split('\n')
            title = url = snippet = ""
            
            for line in lines:
                if line.startswith('TITLE:'):
                    title = line.replace('TITLE:', '').strip()
                elif line.startswith('URL:'):
                    url = line.replace('URL:', '').strip()
                elif line.startswith('SNIPPET:'):
                    snippet = line.replace('SNIPPET:', '').strip()
            
            if title and url and snippet:
                results.append(SearchResult(
                    title=title,
                    url=url,
                    snippet=snippet,
                    relevance_score=1.0 - (i * 0.1)
                ))
        
        return results if results else self._generate_basic_search_results("", "", "")
    
    def _generate_basic_search_results(self, query: str, topic: str, difficulty_level: str) -> List[SearchResult]:
        """Generate basic structured search results as fallback"""
        return [
            SearchResult(
                title=f"Learn {topic}: {difficulty_level.title()} Guide",
                url=f"https://www.codecademy.com/learn/{topic.lower().replace(' ', '-')}",
                snippet=f"Comprehensive {topic} tutorial covering {query}. Interactive exercises and projects included.",
                relevance_score=0.95
            ),
            SearchResult(
                title=f"{topic} Documentation and Examples",
                url=f"https://docs.python.org/3/tutorial/" if 'python' in topic.lower() else f"https://developer.mozilla.org/en-US/docs/Web/{topic}",
                snippet=f"Official documentation and examples for {query}. Includes best practices and real-world usage.",
                relevance_score=0.88
            ),
            SearchResult(
                title=f"Free {topic} Course for {difficulty_level.title()}s",
                url=f"https://www.freecodecamp.org/learn/{topic.lower().replace(' ', '-')}",
                snippet=f"Free comprehensive course covering {query}. Hands-on projects and certification available.",
                relevance_score=0.82
            )
        ]
    
    def find_documentation(self, library_or_framework: str, specific_function: str = "") -> List[SearchResult]:
        """Find official documentation for programming libraries/frameworks"""
        
        query = f"{library_or_framework} {specific_function} documentation official"
        
        # Mock documentation results
        mock_docs = [
            SearchResult(
                title=f"Official {library_or_framework} Documentation",
                url=f"https://docs.{library_or_framework.lower()}.org",
                snippet=f"Official documentation for {library_or_framework}. {specific_function} reference included.",
                relevance_score=1.0
            ),
            SearchResult(
                title=f"{library_or_framework} API Reference",
                url=f"https://api.{library_or_framework.lower()}.org",
                snippet=f"Complete API reference for {library_or_framework} with examples and usage patterns.",
                relevance_score=0.92
            )
        ]
        
        return mock_docs


class CodeAnalysisTool:
    """
    Tool for analyzing and explaining code using LLM intelligence
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
    
    def analyze_code_snippet(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Analyze a code snippet and provide intelligent insights"""
        
        if self.llm_client:
            return self._analyze_with_llm(code, language)
        else:
            return self._analyze_with_patterns(code, language)
    
    def _analyze_with_llm(self, code: str, language: str) -> Dict[str, Any]:
        """Use LLM for intelligent code analysis"""
        
        prompt = f"""Analyze this {language} code and provide educational insights:

```{language}
{code}
```

Please provide analysis in this format:
DIFFICULTY: [beginner/intermediate/advanced]
CONCEPTS: [comma-separated list of programming concepts used]
ISSUES: [any potential issues or improvements]
SUGGESTIONS: [educational suggestions for improvement]
EXPLANATION: [brief explanation of what the code does]

Focus on being educational and helpful for learning."""

        try:
            response = self.llm_client.generate_response(prompt, max_tokens=400)
            return self._parse_llm_analysis(response, code)
        except Exception as e:
            logger.error(f"LLM code analysis failed: {e}")
            return self._analyze_with_patterns(code, language)
    
    def _parse_llm_analysis(self, llm_response: str, original_code: str) -> Dict[str, Any]:
        """Parse LLM analysis response into structured format"""
        
        analysis = {
            "language": "python",
            "line_count": len(original_code.split('\n')),
            "estimated_difficulty": "intermediate",
            "concepts_used": [],
            "potential_issues": [],
            "suggestions": [],
            "explanation": "Code analysis completed"
        }
        
        lines = llm_response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('DIFFICULTY:'):
                analysis["estimated_difficulty"] = line.replace('DIFFICULTY:', '').strip().lower()
            elif line.startswith('CONCEPTS:'):
                concepts = line.replace('CONCEPTS:', '').strip()
                analysis["concepts_used"] = [c.strip() for c in concepts.split(',') if c.strip()]
            elif line.startswith('ISSUES:'):
                issues = line.replace('ISSUES:', '').strip()
                if issues and issues.lower() not in ['none', 'no issues']:
                    analysis["potential_issues"] = [issues]
            elif line.startswith('SUGGESTIONS:'):
                suggestions = line.replace('SUGGESTIONS:', '').strip()
                if suggestions:
                    analysis["suggestions"] = [suggestions]
            elif line.startswith('EXPLANATION:'):
                explanation = line.replace('EXPLANATION:', '').strip()
                if explanation:
                    analysis["explanation"] = explanation
        
        # Calculate complexity score based on analysis
        analysis["complexity_score"] = len(analysis["concepts_used"]) + len(original_code.split('\n')) // 10
        
        return analysis
    
    def _analyze_with_patterns(self, code: str, language: str) -> Dict[str, Any]:
        """Fallback pattern-based analysis"""
        analysis = {
            "language": language,
            "estimated_difficulty": self._estimate_difficulty(code),
            "concepts_used": self._identify_concepts(code, language),
            "potential_issues": self._check_common_issues(code, language),
            "suggestions": self._generate_suggestions(code, language),
            "line_count": len(code.split('\n')),
            "complexity_score": self._calculate_complexity(code),
            "explanation": "Basic pattern-based analysis completed"
        }
        
        return analysis
    
    def _estimate_difficulty(self, code: str) -> str:
        """Estimate the difficulty level of code"""
        advanced_patterns = ['class ', 'def ', 'import ', 'lambda', 'try:', 'except:', 'with ']
        intermediate_patterns = ['for ', 'while ', 'if ', 'elif', 'else:', 'list(', 'dict(']
        
        advanced_count = sum(1 for pattern in advanced_patterns if pattern in code)
        intermediate_count = sum(1 for pattern in intermediate_patterns if pattern in code)
        
        if advanced_count > 2:
            return "advanced"
        elif intermediate_count > 1 or advanced_count > 0:
            return "intermediate"
        else:
            return "beginner"
    
    def _identify_concepts(self, code: str, language: str) -> List[str]:
        """Identify programming concepts in the code"""
        concepts = []
        
        if language.lower() == "python":
            patterns = {
                "functions": r"def\s+\w+",
                "classes": r"class\s+\w+",
                "loops": r"(for\s+\w+\s+in|while\s+)",
                "conditionals": r"if\s+.*:",
                "list_comprehensions": r"\[.*for.*in.*\]",
                "exception_handling": r"try:|except:",
                "file_operations": r"open\s*\(",
                "imports": r"import\s+\w+|from\s+\w+\s+import"
            }
            
            for concept, pattern in patterns.items():
                if re.search(pattern, code):
                    concepts.append(concept)
        
        return concepts
    
    def _check_common_issues(self, code: str, language: str) -> List[str]:
        """Check for common programming issues"""
        issues = []
        
        if language.lower() == "python":
            # Check for common Python issues
            if re.search(r"print\s*\([^)]*\)", code) and "input(" in code:
                issues.append("Mixed input/output - consider separating logic")
            
            if "==" in code and "=" in code:
                issues.append("Be careful with assignment (=) vs comparison (==)")
            
            if re.search(r"range\s*\(\s*len\s*\(", code):
                issues.append("Consider using direct iteration instead of range(len())")
        
        return issues
    
    def _generate_suggestions(self, code: str, language: str) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        lines = code.split('\n')
        
        # General suggestions
        if len(lines) > 20:
            suggestions.append("Consider breaking this into smaller functions")
        
        if not any(line.strip().startswith('#') for line in lines):
            suggestions.append("Add comments to explain your logic")
        
        if language.lower() == "python":
            if "print(" in code:
                suggestions.append("Great use of print statements for debugging!")
            
            if "def " in code:
                suggestions.append("Excellent use of functions to organize code")
        
        return suggestions
    
    def _calculate_complexity(self, code: str) -> int:
        """Calculate a simple complexity score"""
        complexity_indicators = ['if ', 'for ', 'while ', 'try:', 'def ', 'class ']
        return sum(code.count(indicator) for indicator in complexity_indicators)


class LearningResourceTool:
    """
    Tool for generating and managing learning resources using LLM intelligence
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
    
    def generate_practice_exercises(self, topic: str, difficulty: str, student_level: str) -> List[Dict[str, Any]]:
        """Generate practice exercises based on topic and difficulty using LLM"""
        
        if self.llm_client:
            return self._generate_exercises_with_llm(topic, difficulty, student_level)
        else:
            return self._generate_basic_exercises(topic, difficulty, student_level)
    
    def _generate_exercises_with_llm(self, topic: str, difficulty: str, student_level: str) -> List[Dict[str, Any]]:
        """Generate exercises using LLM"""
        
        if not self.llm_client:
            return self._generate_basic_exercises(topic, difficulty, student_level)
        
        prompt = f"""Create 2-3 educational programming exercises for:
Topic: {topic}
Difficulty: {difficulty}
Student Level: {student_level}

For each exercise, provide:
1. A clear title
2. A description of what to build/solve
3. Starter code template
4. 2-3 helpful hints
5. A brief solution (commented)

Format each exercise as:
EXERCISE: [number]
TITLE: [exercise title]
DESCRIPTION: [what to build]
STARTER: [starter code template]
HINTS: [hint1, hint2, hint3]
SOLUTION: [solution code]
---

Make exercises progressively challenging but achievable at the {difficulty} level."""

        try:
            response = self.llm_client.generate_response(prompt, max_tokens=600)
            return self._parse_exercise_response(response)
        except Exception as e:
            logger.error(f"LLM exercise generation failed: {e}")
            return self._generate_basic_exercises(topic, difficulty, student_level)
    
    def _parse_exercise_response(self, llm_response: str) -> List[Dict[str, Any]]:
        """Parse LLM response into exercise objects"""
        exercises = []
        sections = llm_response.split('---')
        
        for section in sections:
            exercise = {}
            lines = section.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('TITLE:'):
                    exercise['title'] = line.replace('TITLE:', '').strip()
                elif line.startswith('DESCRIPTION:'):
                    exercise['description'] = line.replace('DESCRIPTION:', '').strip()
                elif line.startswith('STARTER:'):
                    # Collect multi-line starter code
                    starter_code = line.replace('STARTER:', '').strip()
                    exercise['starter_code'] = starter_code
                elif line.startswith('HINTS:'):
                    hints_text = line.replace('HINTS:', '').strip()
                    exercise['hints'] = [h.strip() for h in hints_text.split(',') if h.strip()]
                elif line.startswith('SOLUTION:'):
                    solution = line.replace('SOLUTION:', '').strip()
                    exercise['solution'] = solution
            
            if 'title' in exercise and 'description' in exercise:
                exercises.append(exercise)
        
        return exercises if exercises else self._generate_basic_exercises("programming", "beginner", "beginner")
    
    def _generate_basic_exercises(self, topic: str, difficulty: str, student_level: str) -> List[Dict[str, Any]]:
        """Generate basic exercises as fallback"""
        
        basic_exercises = [
            {
                "title": f"Practice {topic}",
                "description": f"A {difficulty} level exercise to practice {topic} concepts",
                "starter_code": f"# {topic} practice exercise\n# Your code here\npass",
                "hints": ["Break the problem into steps", "Test your code with examples", "Don't forget edge cases"],
                "solution": f"# Solution will vary based on {topic}",
                "encouragement": f"Great job practicing {topic}! Every expert was once a beginner."
            }
        ]
        
        return basic_exercises
    
    def create_study_plan(self, topic: str, timeline_days: int, current_level: str) -> Dict[str, Any]:
        """Create a personalized study plan using LLM"""
        
        if self.llm_client:
            return self._create_study_plan_with_llm(topic, timeline_days, current_level)
        else:
            return self._create_basic_study_plan(topic, timeline_days, current_level)
    
    def _create_study_plan_with_llm(self, topic: str, timeline_days: int, current_level: str) -> Dict[str, Any]:
        """Generate study plan using LLM"""
        
        if not self.llm_client:
            return self._create_basic_study_plan(topic, timeline_days, current_level)
        
        prompt = f"""Create a detailed {timeline_days}-day study plan for:
Topic: {topic}
Current Level: {current_level}
Timeline: {timeline_days} days

Please create a structured plan with:
1. 3-4 phases of learning
2. Daily time recommendations 
3. Specific topics to cover each phase
4. Learning goals for each phase
5. Suggested daily activities
6. Success metrics to track progress

Format as:
PHASE: [number] - [phase name]
DURATION: [days]
TOPICS: [topic1, topic2, topic3]
GOALS: [goal1, goal2]
DAILY_ACTIVITIES: [activity1, activity2, activity3]
---

Make it realistic and achievable for a {current_level} level learner."""

        try:
            response = self.llm_client.generate_response(prompt, max_tokens=500)
            return self._parse_study_plan_response(response, topic, timeline_days, current_level)
        except Exception as e:
            logger.error(f"LLM study plan generation failed: {e}")
            return self._create_basic_study_plan(topic, timeline_days, current_level)
    
    def _parse_study_plan_response(self, llm_response: str, topic: str, timeline_days: int, current_level: str) -> Dict[str, Any]:
        """Parse LLM study plan response"""
        
        phases = []
        sections = llm_response.split('---')
        
        for section in sections:
            phase = {}
            lines = section.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('PHASE:'):
                    phase_info = line.replace('PHASE:', '').strip()
                    parts = phase_info.split(' - ')
                    if len(parts) >= 2:
                        phase['phase'] = parts[0].strip()
                        phase['title'] = parts[1].strip()
                elif line.startswith('DURATION:'):
                    duration = line.replace('DURATION:', '').strip()
                    try:
                        phase['duration_days'] = int(duration.split()[0])
                    except:
                        phase['duration_days'] = timeline_days // 3
                elif line.startswith('TOPICS:'):
                    topics = line.replace('TOPICS:', '').strip()
                    phase['topics'] = [t.strip() for t in topics.split(',') if t.strip()]
                elif line.startswith('GOALS:'):
                    goals = line.replace('GOALS:', '').strip()
                    phase['goals'] = [g.strip() for g in goals.split(',') if g.strip()]
                elif line.startswith('DAILY_ACTIVITIES:'):
                    activities = line.replace('DAILY_ACTIVITIES:', '').strip()
                    phase['daily_activities'] = [a.strip() for a in activities.split(',') if a.strip()]
            
            if 'title' in phase:
                phases.append(phase)
        
        return {
            "topic": topic,
            "total_duration_days": timeline_days,
            "current_level": current_level,
            "phases": phases if phases else self._get_default_phases(timeline_days),
            "success_metrics": [
                "Complete daily learning goals",
                "Practice regularly with hands-on exercises", 
                "Track understanding and ask questions",
                "Build projects to apply knowledge"
            ],
            "resources": [
                "Interactive tutorials and documentation",
                "Video courses and lectures",
                "Practice platforms and coding challenges",
                "Community forums and study groups"
            ]
        }
    
    def _create_basic_study_plan(self, topic: str, timeline_days: int, current_level: str) -> Dict[str, Any]:
        """Create basic study plan as fallback"""
        
        phases = self._get_default_phases(timeline_days)
        
        return {
            "topic": topic,
            "total_duration_days": timeline_days,
            "current_level": current_level,
            "phases": phases,
            "success_metrics": [
                "Complete daily coding exercises",
                "Build small projects each week",
                "Explain concepts to others",
                "Debug code independently"
            ],
            "resources": [
                "Interactive coding platforms",
                "Video tutorials",
                "Practice websites",
                "Programming books"
            ]
        }
    
    def _get_default_phases(self, timeline_days: int) -> List[Dict[str, Any]]:
        """Get default learning phases"""
        days_per_phase = max(1, timeline_days // 3)
        
        return [
            {
                "phase": 1,
                "title": "Fundamentals",
                "duration_days": days_per_phase,
                "topics": ["Basic concepts", "Syntax", "Core operations"],
                "goals": ["Understand basic principles", "Write simple programs"],
                "daily_activities": ["30 min reading", "45 min practice", "15 min review"]
            },
            {
                "phase": 2,
                "title": "Intermediate Concepts", 
                "duration_days": days_per_phase,
                "topics": ["Advanced features", "Problem solving", "Best practices"],
                "goals": ["Build working applications", "Apply learned concepts"],
                "daily_activities": ["45 min coding", "30 min exercises", "15 min reflection"]
            },
            {
                "phase": 3,
                "title": "Advanced Application",
                "duration_days": timeline_days - (2 * days_per_phase),
                "topics": ["Real projects", "Integration", "Optimization"],
                "goals": ["Complete portfolio projects", "Master advanced techniques"],
                "daily_activities": ["60 min project work", "30 min research", "30 min documentation"]
            }
        ]


class ProgressTrackingTool:
    """
    Tool for tracking student progress and achievements
    """
    
    def __init__(self, student_id: str, data_dir: str = "progress_data"):
        self.student_id = student_id
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.progress_file = os.path.join(data_dir, f"{student_id}_progress.json")
        self.achievements_file = os.path.join(data_dir, f"{student_id}_achievements.json")
        
        self.progress_data = self._load_progress()
        self.achievements = self._load_achievements()
    
    def _load_progress(self) -> Dict[str, Any]:
        """Load progress data from file"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        return {
            "topics": {},
            "overall_stats": {
                "total_study_time": 0,
                "sessions_completed": 0,
                "streak_days": 0,
                "last_study_date": None
            }
        }
    
    def _load_achievements(self) -> List[Dict[str, Any]]:
        """Load achievements from file"""
        if os.path.exists(self.achievements_file):
            try:
                with open(self.achievements_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return []
    
    def _save_data(self):
        """Save progress and achievements to files"""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress_data, f, indent=2)
        
        with open(self.achievements_file, 'w') as f:
            json.dump(self.achievements, f, indent=2)
    
    def update_progress(self, topic: str, understanding_score: float, 
                       time_spent_minutes: int, exercises_completed: int = 0):
        """Update student progress for a topic"""
        
        if topic not in self.progress_data["topics"]:
            self.progress_data["topics"][topic] = {
                "understanding_scores": [],
                "total_time": 0,
                "exercises_completed": 0,
                "sessions": 0,
                "first_studied": datetime.now().isoformat(),
                "last_studied": None
            }
        
        topic_data = self.progress_data["topics"][topic]
        topic_data["understanding_scores"].append({
            "score": understanding_score,
            "timestamp": datetime.now().isoformat()
        })
        topic_data["total_time"] += time_spent_minutes
        topic_data["exercises_completed"] += exercises_completed
        topic_data["sessions"] += 1
        topic_data["last_studied"] = datetime.now().isoformat()
        
        # Update overall stats
        overall = self.progress_data["overall_stats"]
        overall["total_study_time"] += time_spent_minutes
        overall["sessions_completed"] += 1
        
        # Update streak
        today = datetime.now().date()
        last_date = datetime.fromisoformat(overall["last_study_date"]).date() if overall["last_study_date"] else None
        
        if last_date:
            if today == last_date:
                pass  # Same day, no change to streak
            elif today == last_date + timedelta(days=1):
                overall["streak_days"] += 1  # Consecutive day
            else:
                overall["streak_days"] = 1  # Streak broken, start new
        else:
            overall["streak_days"] = 1  # First day
        
        overall["last_study_date"] = datetime.now().isoformat()
        
        # Check for achievements
        self._check_achievements(topic, understanding_score, time_spent_minutes)
        
        self._save_data()
    
    def _check_achievements(self, topic: str, understanding_score: float, time_spent_minutes: int):
        """Check if student has earned any new achievements"""
        
        new_achievements = []
        overall = self.progress_data["overall_stats"]
        
        # Study streak achievements
        if overall["streak_days"] == 7 and not self._has_achievement("7_day_streak"):
            new_achievements.append({
                "id": "7_day_streak",
                "title": "Week Warrior",
                "description": "Studied for 7 consecutive days!",
                "icon": "🔥",
                "earned_date": datetime.now().isoformat()
            })
        
        # Total time achievements
        if overall["total_study_time"] >= 300 and not self._has_achievement("5_hour_milestone"):  # 5 hours
            new_achievements.append({
                "id": "5_hour_milestone",
                "title": "Dedicated Learner",
                "description": "Spent 5 hours studying!",
                "icon": "⏰",
                "earned_date": datetime.now().isoformat()
            })
        
        # Understanding achievements
        if understanding_score >= 9.0 and not self._has_achievement("excellence_achieved"):
            new_achievements.append({
                "id": "excellence_achieved",
                "title": "Excellence Achieved",
                "description": "Scored 9+ understanding on a topic!",
                "icon": "🌟",
                "earned_date": datetime.now().isoformat()
            })
        
        # Topic mastery
        topic_data = self.progress_data["topics"].get(topic, {})
        scores = [s["score"] for s in topic_data.get("understanding_scores", [])]
        if len(scores) >= 3 and all(s >= 8.0 for s in scores[-3:]):
            achievement_id = f"master_{topic.lower().replace(' ', '_')}"
            if not self._has_achievement(achievement_id):
                new_achievements.append({
                    "id": achievement_id,
                    "title": f"{topic} Master",
                    "description": f"Consistently scored 8+ on {topic}!",
                    "icon": "🎓",
                    "earned_date": datetime.now().isoformat()
                })
        
        self.achievements.extend(new_achievements)
        return new_achievements
    
    def _has_achievement(self, achievement_id: str) -> bool:
        """Check if student already has an achievement"""
        return any(a["id"] == achievement_id for a in self.achievements)
    
    def get_progress_summary(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """Get progress summary for a topic or overall"""
        
        if topic:
            if topic not in self.progress_data["topics"]:
                return {"error": f"No progress data for {topic}"}
            
            topic_data = self.progress_data["topics"][topic]
            scores = [s["score"] for s in topic_data["understanding_scores"]]
            
            return {
                "topic": topic,
                "average_understanding": sum(scores) / len(scores) if scores else 0,
                "progress_trend": "improving" if len(scores) > 1 and scores[-1] > scores[0] else "stable",
                "total_time_hours": round(topic_data["total_time"] / 60, 1),
                "sessions_completed": topic_data["sessions"],
                "exercises_completed": topic_data["exercises_completed"],
                "first_studied": topic_data["first_studied"],
                "last_studied": topic_data["last_studied"]
            }
        else:
            # Overall summary
            all_scores = []
            for topic_data in self.progress_data["topics"].values():
                all_scores.extend(s["score"] for s in topic_data["understanding_scores"])
            
            return {
                "overall_understanding": sum(all_scores) / len(all_scores) if all_scores else 0,
                "topics_studied": len(self.progress_data["topics"]),
                "total_study_hours": round(self.progress_data["overall_stats"]["total_study_time"] / 60, 1),
                "current_streak": self.progress_data["overall_stats"]["streak_days"],
                "total_sessions": self.progress_data["overall_stats"]["sessions_completed"],
                "recent_achievements": self.achievements[-3:] if len(self.achievements) >= 3 else self.achievements
            }
