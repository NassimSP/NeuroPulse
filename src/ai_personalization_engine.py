"""
AI-Powered Personalization Engine for NeuroPulse
Provides adaptive learning paths, personalized recommendations, and dynamic difficulty adjustment
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import statistics
from openai import OpenAI

class PersonalizationEngine:
    def __init__(self):
        self.personalization_file = 'user_personalization_data.json'
        self.learning_patterns_file = 'learning_patterns_advanced.json'
        self.recommendations_file = 'ai_recommendations_data.json'
        self.adaptive_paths_file = 'adaptive_learning_paths.json'
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        self.load_data()
    
    def load_data(self):
        """Load personalization data"""
        self.user_profiles = self._load_json_file(self.personalization_file, {})
        self.learning_patterns = self._load_json_file(self.learning_patterns_file, {})
        self.recommendations = self._load_json_file(self.recommendations_file, {})
        self.adaptive_paths = self._load_json_file(self.adaptive_paths_file, {})
    
    def _load_json_file(self, filename: str, default: dict) -> dict:
        """Load JSON file with fallback to default"""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return default
    
    def _save_json_file(self, filename: str, data: dict):
        """Save data to JSON file"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def analyze_learning_style(self, user_id: str, session_data: dict) -> dict:
        """Analyze user's learning style using AI"""
        
        # Gather user's historical data
        from analytics_dashboard import analytics_manager
        user_analytics = analytics_manager.get_user_dashboard_data(user_id)
        
        if 'error' in user_analytics:
            # New user - start with basic profile
            learning_style = {
                'visual': 0.33,
                'auditory': 0.33,
                'kinesthetic': 0.34,
                'reading_writing': 0.33,
                'confidence': 0.1
            }
        else:
            # Analyze existing patterns with AI
            learning_style = self._ai_analyze_learning_style(user_analytics, session_data)
        
        # Update user profile
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'learning_style': learning_style,
                'preferences': {},
                'optimal_conditions': {},
                'performance_patterns': {},
                'last_updated': datetime.now().isoformat()
            }
        else:
            # Update with weighted average (new data has 30% weight)
            current_style = self.user_profiles[user_id]['learning_style']
            for style_type in learning_style:
                if style_type != 'confidence':
                    current_style[style_type] = (current_style[style_type] * 0.7 + 
                                               learning_style[style_type] * 0.3)
            
            current_style['confidence'] = min(1.0, current_style.get('confidence', 0) + 0.1)
            self.user_profiles[user_id]['last_updated'] = datetime.now().isoformat()
        
        self._save_json_file(self.personalization_file, self.user_profiles)
        return self.user_profiles[user_id]['learning_style']
    
    def _ai_analyze_learning_style(self, user_analytics: dict, session_data: dict) -> dict:
        """Use AI to analyze learning style from user data"""
        
        # Prepare data summary for AI analysis
        analysis_prompt = f"""
        Analyze this learner's data to determine their learning style preferences:
        
        Performance Data:
        - Overall accuracy: {user_analytics.get('overview', {}).get('overall_accuracy', 0)}%
        - Learning velocity: {user_analytics.get('performance', {}).get('learning_velocity', 0)}%
        - Consistency score: {user_analytics.get('performance', {}).get('consistency_score', 0)}%
        - Engagement score: {user_analytics.get('performance', {}).get('engagement_score', 0)}%
        
        Learning Patterns:
        - Subject preferences: {user_analytics.get('learning_patterns', {}).get('subject_preferences', {})}
        - Session length preference: {user_analytics.get('learning_patterns', {}).get('session_length_preference', 0)} minutes
        - Optimal learning hours: {user_analytics.get('learning_patterns', {}).get('optimal_learning_hours', [])}
        
        Current Session:
        - Time spent: {session_data.get('time_spent_minutes', 0)} minutes
        - Questions answered: {session_data.get('questions_answered', 0)}
        - Accuracy: {session_data.get('accuracy_rate', 0)}%
        - Hints used: {session_data.get('hints_used', 0)}
        - Topic: {session_data.get('topic', 'Unknown')}
        
        Based on this data, determine the learner's style preferences as percentages that sum to 1.0:
        - Visual (learns through images, diagrams, charts)
        - Auditory (learns through listening, discussion)
        - Kinesthetic (learns through hands-on practice)
        - Reading/Writing (learns through text-based materials)
        
        Respond with JSON only in this format:
        {
            "visual": 0.XX,
            "auditory": 0.XX,
            "kinesthetic": 0.XX,
            "reading_writing": 0.XX,
            "confidence": 0.XX,
            "reasoning": "Brief explanation of analysis"
        }
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": "You are an expert learning psychologist specializing in learning style analysis. Provide accurate learning style assessments based on behavioral data."},
                    {"role": "user", "content": analysis_prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate and normalize the result
            total = result['visual'] + result['auditory'] + result['kinesthetic'] + result['reading_writing']
            if total > 0:
                result['visual'] /= total
                result['auditory'] /= total
                result['kinesthetic'] /= total
                result['reading_writing'] /= total
            
            return result
            
        except Exception as e:
            print(f"AI analysis failed: {e}")
            # Fallback to heuristic analysis
            return self._heuristic_learning_style_analysis(user_analytics, session_data)
    
    def _heuristic_learning_style_analysis(self, user_analytics: dict, session_data: dict) -> dict:
        """Fallback heuristic analysis if AI fails"""
        visual = 0.25
        auditory = 0.25
        kinesthetic = 0.25
        reading_writing = 0.25
        
        # Adjust based on engagement patterns
        engagement = user_analytics.get('performance', {}).get('engagement_score', 50)
        if engagement > 80:
            kinesthetic += 0.1  # High engagement suggests hands-on preference
        
        # Adjust based on session length preference
        session_length = user_analytics.get('learning_patterns', {}).get('session_length_preference', 15)
        if session_length > 20:
            reading_writing += 0.1  # Longer sessions suggest text preference
        elif session_length < 10:
            visual += 0.1  # Shorter sessions suggest visual preference
        
        # Normalize
        total = visual + auditory + kinesthetic + reading_writing
        return {
            'visual': visual / total,
            'auditory': auditory / total,
            'kinesthetic': kinesthetic / total,
            'reading_writing': reading_writing / total,
            'confidence': 0.3
        }
    
    def generate_adaptive_learning_path(self, user_id: str, subject_category: str, target_competency: str) -> dict:
        """Generate AI-powered adaptive learning path"""
        
        # Get user profile and current performance
        user_profile = self.user_profiles.get(user_id, {})
        learning_style = user_profile.get('learning_style', {})
        
        from analytics_dashboard import analytics_manager
        user_analytics = analytics_manager.get_user_dashboard_data(user_id)
        
        # Get current competency level in subject
        current_level = self._assess_current_competency(user_id, subject_category)
        
        # Generate AI-powered learning path
        learning_path = self._ai_generate_learning_path(
            user_profile, current_level, subject_category, target_competency
        )
        
        # Store the adaptive path
        path_id = str(uuid.uuid4())
        self.adaptive_paths[path_id] = {
            'user_id': user_id,
            'subject_category': subject_category,
            'target_competency': target_competency,
            'current_level': current_level,
            'learning_path': learning_path,
            'created_at': datetime.now().isoformat(),
            'progress': {
                'current_step': 0,
                'completed_steps': [],
                'estimated_completion': learning_path.get('estimated_weeks', 8)
            },
            'adaptations': []
        }
        
        self._save_json_file(self.adaptive_paths_file, self.adaptive_paths)
        return self.adaptive_paths[path_id]
    
    def _ai_generate_learning_path(self, user_profile: dict, current_level: str, 
                                  subject_category: str, target_competency: str) -> dict:
        """Use AI to generate personalized learning path"""
        
        learning_style = user_profile.get('learning_style', {})
        
        path_prompt = f"""
        Create a personalized learning path for a student with these characteristics:
        
        Learning Style:
        - Visual: {learning_style.get('visual', 0.25)*100:.1f}%
        - Auditory: {learning_style.get('auditory', 0.25)*100:.1f}%
        - Kinesthetic: {learning_style.get('kinesthetic', 0.25)*100:.1f}%
        - Reading/Writing: {learning_style.get('reading_writing', 0.25)*100:.1f}%
        
        Current Status:
        - Subject: {subject_category}
        - Current Level: {current_level}
        - Target Competency: {target_competency}
        
        Create a structured learning path with:
        1. Sequential learning modules optimized for their learning style
        2. Estimated timeframes for each module
        3. Recommended content types (visual, audio, hands-on, text)
        4. Assessment checkpoints
        5. Prerequisite skills for each module
        
        Respond with JSON only in this format:
        {{
            "estimated_weeks": 8,
            "modules": [
                {{
                    "id": "module_1",
                    "title": "Module Title",
                    "description": "Module description",
                    "estimated_hours": 10,
                    "difficulty": "foundation/intermediate/advanced",
                    "content_types": ["visual", "hands-on"],
                    "learning_objectives": ["objective1", "objective2"],
                    "prerequisites": ["skill1", "skill2"],
                    "assessment_type": "quiz/project/discussion",
                    "resources": [
                        {{
                            "type": "content_type",
                            "title": "Resource Title",
                            "description": "Resource description"
                        }}
                    ]
                }}
            ],
            "milestones": [
                {{
                    "week": 2,
                    "title": "Milestone Title",
                    "competencies": ["competency1", "competency2"]
                }}
            ]
        }}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": "You are an expert curriculum designer specializing in personalized learning paths. Create comprehensive, adaptive learning experiences."},
                    {"role": "user", "content": path_prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=2000
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"AI path generation failed: {e}")
            return self._create_default_learning_path(subject_category, current_level)
    
    def _create_default_learning_path(self, subject_category: str, current_level: str) -> dict:
        """Create default learning path if AI generation fails"""
        return {
            "estimated_weeks": 6,
            "modules": [
                {
                    "id": "module_1",
                    "title": f"Foundation in {subject_category.replace('_', ' ').title()}",
                    "description": "Build fundamental understanding",
                    "estimated_hours": 8,
                    "difficulty": "foundation",
                    "content_types": ["visual", "reading"],
                    "learning_objectives": ["Understand basic concepts", "Apply fundamental principles"],
                    "prerequisites": [],
                    "assessment_type": "quiz"
                },
                {
                    "id": "module_2",
                    "title": f"Intermediate {subject_category.replace('_', ' ').title()}",
                    "description": "Develop practical skills",
                    "estimated_hours": 12,
                    "difficulty": "intermediate",
                    "content_types": ["hands-on", "visual"],
                    "learning_objectives": ["Apply concepts to problems", "Analyze complex scenarios"],
                    "prerequisites": ["module_1"],
                    "assessment_type": "project"
                }
            ],
            "milestones": [
                {
                    "week": 3,
                    "title": "Foundation Mastery",
                    "competencies": ["Basic understanding", "Problem recognition"]
                }
            ]
        }
    
    def adapt_learning_path(self, user_id: str, path_id: str, performance_data: dict) -> dict:
        """Dynamically adapt learning path based on performance"""
        
        if path_id not in self.adaptive_paths:
            return {'error': 'Learning path not found'}
        
        path = self.adaptive_paths[path_id]
        
        # Analyze performance and determine adaptations
        adaptations = self._ai_analyze_performance_and_adapt(path, performance_data)
        
        # Apply adaptations
        if adaptations.get('difficulty_adjustment'):
            self._adjust_path_difficulty(path, adaptations['difficulty_adjustment'])
        
        if adaptations.get('content_type_adjustment'):
            self._adjust_content_types(path, adaptations['content_type_adjustment'])
        
        if adaptations.get('pacing_adjustment'):
            self._adjust_pacing(path, adaptations['pacing_adjustment'])
        
        # Record the adaptation
        path['adaptations'].append({
            'timestamp': datetime.now().isoformat(),
            'trigger': performance_data,
            'adaptations_applied': adaptations,
            'reasoning': adaptations.get('reasoning', 'Performance-based adjustment')
        })
        
        self._save_json_file(self.adaptive_paths_file, self.adaptive_paths)
        return path
    
    def _ai_analyze_performance_and_adapt(self, path: dict, performance_data: dict) -> dict:
        """Use AI to analyze performance and suggest adaptations"""
        
        adaptation_prompt = f"""
        Analyze this learner's performance and suggest learning path adaptations:
        
        Current Learning Path:
        - Subject: {path.get('subject_category', 'Unknown')}
        - Current Step: {path.get('progress', {}).get('current_step', 0)}
        - Total Modules: {len(path.get('learning_path', {}).get('modules', []))}
        
        Recent Performance:
        - Accuracy: {performance_data.get('accuracy_rate', 0)}%
        - Time Spent: {performance_data.get('time_spent_minutes', 0)} minutes
        - Questions Answered: {performance_data.get('questions_answered', 0)}
        - Completion Rate: {performance_data.get('completion_rate', 100)}%
        - Confidence Level: {performance_data.get('confidence_level', 3)}/5
        - Hints Used: {performance_data.get('hints_used', 0)}
        - Difficulty Level: {performance_data.get('difficulty_level', 'intermediate')}
        
        Suggest adaptations in these areas:
        1. Difficulty adjustment (easier/harder/maintain)
        2. Content type adjustments (more visual/auditory/kinesthetic/reading)
        3. Pacing adjustments (faster/slower/maintain)
        
        Respond with JSON only:
        {{
            "difficulty_adjustment": "easier/harder/maintain",
            "content_type_adjustment": {{
                "increase_visual": true/false,
                "increase_auditory": true/false,
                "increase_kinesthetic": true/false,
                "increase_reading": true/false
            }},
            "pacing_adjustment": "faster/slower/maintain",
            "reasoning": "Explanation of recommendations",
            "confidence": 0.XX
        }}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": "You are an adaptive learning specialist. Analyze performance data and recommend personalized learning adjustments."},
                    {"role": "user", "content": adaptation_prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=800
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"AI adaptation analysis failed: {e}")
            return self._heuristic_adaptation_analysis(performance_data)
    
    def _heuristic_adaptation_analysis(self, performance_data: dict) -> dict:
        """Fallback heuristic adaptation if AI fails"""
        accuracy = performance_data.get('accuracy_rate', 0)
        confidence = performance_data.get('confidence_level', 3)
        hints_used = performance_data.get('hints_used', 0)
        
        # Determine difficulty adjustment
        if accuracy < 60 or confidence < 2:
            difficulty_adjustment = "easier"
        elif accuracy > 90 and confidence > 4 and hints_used == 0:
            difficulty_adjustment = "harder"
        else:
            difficulty_adjustment = "maintain"
        
        # Determine content type adjustments
        content_adjustment = {
            "increase_visual": hints_used > 2,  # More visual aids if struggling
            "increase_auditory": False,
            "increase_kinesthetic": accuracy < 70,  # More hands-on if low accuracy
            "increase_reading": False
        }
        
        # Determine pacing
        completion_rate = performance_data.get('completion_rate', 100)
        if completion_rate < 80:
            pacing_adjustment = "slower"
        elif completion_rate == 100 and accuracy > 85:
            pacing_adjustment = "faster"
        else:
            pacing_adjustment = "maintain"
        
        return {
            "difficulty_adjustment": difficulty_adjustment,
            "content_type_adjustment": content_adjustment,
            "pacing_adjustment": pacing_adjustment,
            "reasoning": "Heuristic analysis based on performance metrics",
            "confidence": 0.7
        }
    
    def generate_personalized_recommendations(self, user_id: str) -> List[dict]:
        """Generate AI-powered personalized learning recommendations"""
        
        # Get comprehensive user data
        from analytics_dashboard import analytics_manager
        from social_learning import social_manager
        
        user_analytics = analytics_manager.get_user_dashboard_data(user_id)
        social_achievements = social_manager.get_collaborative_achievements(user_id)
        user_profile = self.user_profiles.get(user_id, {})
        
        # Generate recommendations using AI
        recommendations = self._ai_generate_recommendations(user_analytics, social_achievements, user_profile)
        
        # Store recommendations
        self.recommendations[user_id] = {
            'generated_at': datetime.now().isoformat(),
            'recommendations': recommendations,
            'user_profile_snapshot': user_profile
        }
        
        self._save_json_file(self.recommendations_file, self.recommendations)
        return recommendations
    
    def _ai_generate_recommendations(self, user_analytics: dict, social_achievements: dict, user_profile: dict) -> List[dict]:
        """Use AI to generate personalized recommendations"""
        
        recommendations_prompt = f"""
        Generate personalized learning recommendations for this learner:
        
        Learning Analytics:
        {json.dumps(user_analytics, indent=2)[:1500]}...
        
        Social Learning:
        {json.dumps(social_achievements, indent=2)[:500]}...
        
        Learning Style Profile:
        {json.dumps(user_profile.get('learning_style', {}), indent=2)}
        
        Generate 5-8 specific, actionable recommendations covering:
        1. Subject areas to focus on
        2. Learning methods to try
        3. Social learning opportunities
        4. Skill development priorities
        5. Optimal study strategies
        
        Respond with JSON array:
        [
            {{
                "type": "subject_focus/method/social/skill/strategy",
                "priority": "high/medium/low",
                "title": "Recommendation Title",
                "description": "Detailed description",
                "action_items": ["actionable step 1", "actionable step 2"],
                "estimated_time": "time estimate",
                "expected_outcome": "what they'll achieve"
            }}
        ]
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": "You are an expert learning advisor. Provide personalized, actionable recommendations based on comprehensive learner data."},
                    {"role": "user", "content": recommendations_prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=1500
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('recommendations', [])
            
        except Exception as e:
            print(f"AI recommendations failed: {e}")
            return self._create_default_recommendations(user_analytics)
    
    def _create_default_recommendations(self, user_analytics: dict) -> List[dict]:
        """Create default recommendations if AI generation fails"""
        return [
            {
                "type": "subject_focus",
                "priority": "high",
                "title": "Focus on Weak Areas",
                "description": "Concentrate on subjects where you score below 70%",
                "action_items": ["Review fundamentals", "Practice daily"],
                "estimated_time": "30 minutes daily",
                "expected_outcome": "Improved overall performance"
            },
            {
                "type": "strategy",
                "priority": "medium",
                "title": "Establish Consistent Study Schedule",
                "description": "Create a regular learning routine",
                "action_items": ["Set daily study time", "Track progress"],
                "estimated_time": "Planning session needed",
                "expected_outcome": "Better retention and progress"
            }
        ]
    
    def _assess_current_competency(self, user_id: str, subject_category: str) -> str:
        """Assess user's current competency level in subject"""
        from analytics_dashboard import analytics_manager
        
        user_analytics = analytics_manager.get_user_dashboard_data(user_id)
        
        if 'error' in user_analytics:
            return 'foundation'
        
        subject_data = user_analytics.get('subject_breakdown', {}).get(subject_category, {})
        if not subject_data:
            return 'foundation'
        
        avg_accuracy = subject_data.get('avg_accuracy', 0)
        
        if avg_accuracy >= 90:
            return 'expert'
        elif avg_accuracy >= 80:
            return 'advanced'
        elif avg_accuracy >= 65:
            return 'intermediate'
        else:
            return 'foundation'
    
    def _adjust_path_difficulty(self, path: dict, adjustment: str):
        """Adjust learning path difficulty"""
        modules = path['learning_path']['modules']
        
        difficulty_map = {
            'foundation': 0, 'intermediate': 1, 'advanced': 2, 'expert': 3
        }
        reverse_map = {0: 'foundation', 1: 'intermediate', 2: 'advanced', 3: 'expert'}
        
        for module in modules:
            current_level = difficulty_map.get(module['difficulty'], 1)
            
            if adjustment == 'easier' and current_level > 0:
                module['difficulty'] = reverse_map[current_level - 1]
            elif adjustment == 'harder' and current_level < 3:
                module['difficulty'] = reverse_map[current_level + 1]
    
    def _adjust_content_types(self, path: dict, adjustments: dict):
        """Adjust content types in learning path"""
        modules = path['learning_path']['modules']
        
        for module in modules:
            content_types = module.get('content_types', [])
            
            if adjustments.get('increase_visual') and 'visual' not in content_types:
                content_types.append('visual')
            
            if adjustments.get('increase_kinesthetic') and 'hands-on' not in content_types:
                content_types.append('hands-on')
            
            module['content_types'] = content_types
    
    def _adjust_pacing(self, path: dict, adjustment: str):
        """Adjust learning path pacing"""
        if adjustment == 'slower':
            path['learning_path']['estimated_weeks'] = int(path['learning_path']['estimated_weeks'] * 1.3)
        elif adjustment == 'faster':
            path['learning_path']['estimated_weeks'] = max(2, int(path['learning_path']['estimated_weeks'] * 0.8))
    
    def get_real_time_difficulty_adjustment(self, user_id: str, current_session: dict) -> dict:
        """Provide real-time difficulty adjustment during learning session"""
        
        # Analyze current session performance
        accuracy = current_session.get('accuracy_rate', 0)
        time_per_question = current_session.get('avg_time_per_question', 30)
        confidence = current_session.get('confidence_level', 3)
        
        # Get user's learning profile
        user_profile = self.user_profiles.get(user_id, {})
        
        adjustment = {
            'difficulty_change': 'maintain',
            'content_modification': [],
            'hints_available': 2,
            'reasoning': ''
        }
        
        # Real-time difficulty logic
        if accuracy < 40 and confidence < 2:
            adjustment['difficulty_change'] = 'decrease_significantly'
            adjustment['hints_available'] = 5
            adjustment['content_modification'] = ['add_visual_aids', 'simplify_language']
            adjustment['reasoning'] = 'Low accuracy and confidence indicate need for significant support'
            
        elif accuracy < 60:
            adjustment['difficulty_change'] = 'decrease_slightly'
            adjustment['hints_available'] = 3
            adjustment['content_modification'] = ['add_examples']
            adjustment['reasoning'] = 'Below target accuracy requires additional support'
            
        elif accuracy > 90 and time_per_question < 15 and confidence > 4:
            adjustment['difficulty_change'] = 'increase'
            adjustment['hints_available'] = 1
            adjustment['content_modification'] = ['add_complexity', 'reduce_scaffolding']
            adjustment['reasoning'] = 'High performance indicates readiness for increased challenge'
        
        return adjustment

# Initialize global personalization engine
personalization_engine = PersonalizationEngine()