"""
Comprehensive Onboarding Experience System for NeuroPulse
Provides interactive tours, personalized setup, and guided feature discovery
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import random

class OnboardingSystem:
    def __init__(self):
        self.onboarding_progress_file = 'onboarding_progress.json'
        self.tour_data_file = 'interactive_tours.json'
        self.personalization_data_file = 'onboarding_personalization.json'
        self.feature_discovery_file = 'feature_discovery.json'
        
        self.load_data()
        
        # Onboarding stages and their requirements
        self.onboarding_stages = {
            'welcome': {
                'name': 'Welcome to NeuroPulse',
                'description': 'Introduction and initial setup',
                'steps': ['welcome_message', 'learning_goals', 'preferences'],
                'estimated_time': 3,
                'required': True
            },
            'profile_setup': {
                'name': 'Create Your Learning Profile',
                'description': 'Personalize your learning experience',
                'steps': ['learning_style', 'subject_interests', 'study_schedule', 'accessibility_needs'],
                'estimated_time': 5,
                'required': True
            },
            'feature_discovery': {
                'name': 'Discover NeuroPulse Features',
                'description': 'Learn about key platform capabilities',
                'steps': ['ai_tutor_intro', 'quiz_system', 'progress_tracking', 'social_features'],
                'estimated_time': 8,
                'required': False
            },
            'interactive_tour': {
                'name': 'Interactive Platform Tour',
                'description': 'Hands-on exploration of the interface',
                'steps': ['navigation_tour', 'dashboard_tour', 'quiz_demo', 'ai_tutor_demo'],
                'estimated_time': 10,
                'required': False
            },
            'first_learning_session': {
                'name': 'Your First Learning Session',
                'description': 'Complete your first quiz to calibrate the system',
                'steps': ['subject_selection', 'difficulty_calibration', 'first_quiz', 'feedback_collection'],
                'estimated_time': 15,
                'required': True
            },
            'advanced_features': {
                'name': 'Advanced Features & Customization',
                'description': 'Explore advanced functionality',
                'steps': ['spaced_repetition', 'mood_themes', 'voice_navigation', 'collaboration_tools'],
                'estimated_time': 12,
                'required': False
            }
        }
        
        # Interactive tour definitions
        self.tour_definitions = {
            'navigation_tour': {
                'title': 'Platform Navigation',
                'steps': [
                    {
                        'target': '.navbar-custom',
                        'title': 'Main Navigation',
                        'content': 'This is your main navigation bar. Access all major features from here.',
                        'position': 'bottom',
                        'spotlight': True
                    },
                    {
                        'target': '.brand-link',
                        'title': 'NeuroPulse Logo',
                        'content': 'Click here anytime to return to your dashboard.',
                        'position': 'bottom',
                        'spotlight': True
                    },
                    {
                        'target': '.btn-ai-tutor',
                        'title': 'AI Tutor Access',
                        'content': 'Your AI tutor is always available. Click here or press Ctrl+K for instant help.',
                        'position': 'bottom',
                        'spotlight': True,
                        'interactive': True,
                        'action': 'demo_ai_tutor'
                    },
                    {
                        'target': '.user-menu',
                        'title': 'User Menu',
                        'content': 'Access your profile, settings, and account options here.',
                        'position': 'bottom-left',
                        'spotlight': True
                    }
                ]
            },
            'dashboard_tour': {
                'title': 'Your Learning Dashboard',
                'steps': [
                    {
                        'target': '.energy-visualization',
                        'title': 'Learning Energy Tracker',
                        'content': 'Monitor your learning energy and optimize study sessions based on your natural rhythms.',
                        'position': 'top',
                        'spotlight': True
                    },
                    {
                        'target': '.mood-selector',
                        'title': 'Mood-Based Themes',
                        'content': 'Select your current mood to automatically adjust the interface theme and recommendations.',
                        'position': 'top',
                        'spotlight': True,
                        'interactive': True,
                        'action': 'demo_mood_change'
                    },
                    {
                        'target': '.progress-overview',
                        'title': 'Progress Overview',
                        'content': 'Track your learning progress across all subjects with detailed analytics.',
                        'position': 'top',
                        'spotlight': True
                    },
                    {
                        'target': '.spaced-repetition-cards',
                        'title': 'Spaced Repetition System',
                        'content': 'Review cards are automatically scheduled for optimal retention using advanced algorithms.',
                        'position': 'top',
                        'spotlight': True
                    }
                ]
            },
            'quiz_demo': {
                'title': 'Adaptive Quiz System',
                'steps': [
                    {
                        'target': '.quiz-interface',
                        'title': 'Smart Quiz Interface',
                        'content': 'Our adaptive system adjusts difficulty in real-time based on your performance.',
                        'position': 'top',
                        'spotlight': True
                    },
                    {
                        'target': '.hint-system',
                        'title': 'Intelligent Hints',
                        'content': 'Get contextual hints that guide you to the answer without giving it away.',
                        'position': 'right',
                        'spotlight': True,
                        'interactive': True,
                        'action': 'demo_hint_system'
                    },
                    {
                        'target': '.answer-feedback',
                        'title': 'Detailed Feedback',
                        'content': 'Receive comprehensive explanations for both correct and incorrect answers.',
                        'position': 'top',
                        'spotlight': True
                    }
                ]
            }
        }
        
        # Personalization questionnaire
        self.personalization_questions = {
            'learning_style': {
                'question': 'How do you learn best?',
                'type': 'multiple_choice',
                'options': [
                    {'value': 'visual', 'label': 'Visual (diagrams, images, videos)', 'description': 'I understand better with visual aids'},
                    {'value': 'auditory', 'label': 'Auditory (listening, discussion)', 'description': 'I learn by hearing and talking'},
                    {'value': 'kinesthetic', 'label': 'Hands-on (practice, experimentation)', 'description': 'I need to do things to understand'},
                    {'value': 'reading', 'label': 'Reading/Writing (text, notes)', 'description': 'I prefer text-based learning'}
                ]
            },
            'study_pace': {
                'question': 'What\'s your preferred learning pace?',
                'type': 'multiple_choice',
                'options': [
                    {'value': 'fast', 'label': 'Fast-paced', 'description': 'I like to move quickly through material'},
                    {'value': 'moderate', 'label': 'Moderate pace', 'description': 'I prefer a balanced approach'},
                    {'value': 'slow', 'label': 'Thorough and deliberate', 'description': 'I like to take time to fully understand'}
                ]
            },
            'challenge_preference': {
                'question': 'How do you feel about challenging content?',
                'type': 'scale',
                'scale': {
                    'min': 1,
                    'max': 5,
                    'labels': {
                        1: 'Prefer easier content',
                        3: 'Balanced difficulty',
                        5: 'Love challenging content'
                    }
                }
            },
            'study_time_preference': {
                'question': 'When do you typically study best?',
                'type': 'multiple_select',
                'options': [
                    {'value': 'early_morning', 'label': 'Early morning (6-9 AM)'},
                    {'value': 'morning', 'label': 'Morning (9-12 PM)'},
                    {'value': 'afternoon', 'label': 'Afternoon (12-5 PM)'},
                    {'value': 'evening', 'label': 'Evening (5-9 PM)'},
                    {'value': 'night', 'label': 'Night (9 PM+)'}
                ]
            },
            'attention_span': {
                'question': 'How long can you typically focus in one session?',
                'type': 'multiple_choice',
                'options': [
                    {'value': 'short', 'label': '15-25 minutes', 'description': 'I prefer short, focused sessions'},
                    {'value': 'medium', 'label': '25-45 minutes', 'description': 'I can focus for moderate periods'},
                    {'value': 'long', 'label': '45+ minutes', 'description': 'I can maintain focus for extended periods'}
                ]
            },
            'motivation_style': {
                'question': 'What motivates you most in learning?',
                'type': 'multiple_select',
                'options': [
                    {'value': 'progress_tracking', 'label': 'Seeing my progress'},
                    {'value': 'achievements', 'label': 'Earning achievements and badges'},
                    {'value': 'competition', 'label': 'Competing with others'},
                    {'value': 'collaboration', 'label': 'Learning with others'},
                    {'value': 'mastery', 'label': 'Mastering difficult concepts'},
                    {'value': 'practical_application', 'label': 'Applying knowledge practically'}
                ]
            }
        }
        
        # Feature highlights for discovery
        self.feature_highlights = {
            'ai_tutor': {
                'title': 'AI Learning Assistant',
                'description': 'Get instant help, explanations, and personalized guidance',
                'benefits': ['24/7 availability', 'Contextual explanations', 'Adaptive responses'],
                'demo_action': 'show_ai_tutor_demo'
            },
            'spaced_repetition': {
                'title': 'Spaced Repetition System',
                'description': 'Optimize long-term retention with scientifically-proven algorithms',
                'benefits': ['Improved retention', 'Optimal review timing', 'Personalized scheduling'],
                'demo_action': 'show_spaced_repetition_demo'
            },
            'adaptive_difficulty': {
                'title': 'Adaptive Difficulty',
                'description': 'Content automatically adjusts to your performance in real-time',
                'benefits': ['Perfect challenge level', 'Prevents frustration', 'Accelerates learning'],
                'demo_action': 'show_adaptive_demo'
            },
            'mood_themes': {
                'title': 'Mood-Based Personalization',
                'description': 'Interface adapts to your emotional state for optimal learning',
                'benefits': ['Emotional awareness', 'Optimized environment', 'Better engagement'],
                'demo_action': 'show_mood_demo'
            },
            'voice_navigation': {
                'title': 'Voice Commands',
                'description': 'Navigate and control the platform using voice commands',
                'benefits': ['Hands-free operation', 'Accessibility support', 'Efficient navigation'],
                'demo_action': 'show_voice_demo'
            },
            'collaboration': {
                'title': 'Social Learning',
                'description': 'Learn with others through study groups and peer challenges',
                'benefits': ['Peer support', 'Collaborative learning', 'Motivation boost'],
                'demo_action': 'show_collaboration_demo'
            }
        }
    
    def load_data(self):
        """Load onboarding system data"""
        self.onboarding_progress = self._load_json_file(self.onboarding_progress_file, {})
        self.tour_data = self._load_json_file(self.tour_data_file, {})
        self.personalization_data = self._load_json_file(self.personalization_data_file, {})
        self.feature_discovery = self._load_json_file(self.feature_discovery_file, {})
    
    def _load_json_file(self, filename: str, default: dict) -> dict:
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return default
    
    def _save_json_file(self, filename: str, data: dict):
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def initialize_user_onboarding(self, user_id: str, user_data: dict = None) -> dict:
        """Initialize onboarding process for new user"""
        if user_id not in self.onboarding_progress:
            self.onboarding_progress[user_id] = {
                'user_id': user_id,
                'current_stage': 'welcome',
                'completed_stages': [],
                'current_step': 0,
                'total_progress': 0.0,
                'started_at': datetime.now().isoformat(),
                'estimated_completion_time': None,
                'personalization_complete': False,
                'tour_preferences': {
                    'show_tooltips': True,
                    'auto_advance': False,
                    'skip_animations': False
                },
                'feature_discovery_progress': {},
                'onboarding_complete': False
            }
            
            # Initialize personalization data
            if user_id not in self.personalization_data:
                self.personalization_data[user_id] = {
                    'responses': {},
                    'learning_profile': {},
                    'recommendations': [],
                    'setup_complete': False
                }
            
            # Apply any provided user data
            if user_data:
                self.onboarding_progress[user_id].update(user_data)
        
        self._save_all_files()
        
        return self.get_onboarding_status(user_id)
    
    def _save_all_files(self):
        """Save all onboarding data files"""
        self._save_json_file(self.onboarding_progress_file, self.onboarding_progress)
        self._save_json_file(self.tour_data_file, self.tour_data)
        self._save_json_file(self.personalization_data_file, self.personalization_data)
        self._save_json_file(self.feature_discovery_file, self.feature_discovery)
    
    def get_onboarding_status(self, user_id: str) -> dict:
        """Get comprehensive onboarding status for user"""
        if user_id not in self.onboarding_progress:
            return {'onboarding_needed': True}
        
        progress = self.onboarding_progress[user_id]
        current_stage = progress['current_stage']
        
        if progress['onboarding_complete']:
            return {
                'onboarding_complete': True,
                'completed_at': progress.get('completed_at'),
                'personalization_profile': self.personalization_data.get(user_id, {})
            }
        
        stage_info = self.onboarding_stages.get(current_stage, {})
        
        return {
            'onboarding_active': True,
            'current_stage': current_stage,
            'stage_info': stage_info,
            'current_step': progress['current_step'],
            'total_progress': progress['total_progress'],
            'next_step': self._get_next_step(user_id),
            'estimated_time_remaining': self._calculate_remaining_time(user_id),
            'can_skip_stage': not stage_info.get('required', False),
            'personalization_status': self._get_personalization_status(user_id)
        }
    
    def _get_next_step(self, user_id: str) -> Optional[dict]:
        """Get information about the next onboarding step"""
        progress = self.onboarding_progress[user_id]
        current_stage = progress['current_stage']
        current_step = progress['current_step']
        
        stage = self.onboarding_stages.get(current_stage)
        if not stage:
            return None
        
        steps = stage['steps']
        if current_step < len(steps):
            step_name = steps[current_step]
            return self._get_step_details(step_name, current_stage)
        
        return None
    
    def _get_step_details(self, step_name: str, stage_name: str) -> dict:
        """Get detailed information about a specific onboarding step"""
        step_definitions = {
            'welcome_message': {
                'title': 'Welcome to NeuroPulse',
                'type': 'presentation',
                'content': 'Welcome to your personalized learning journey!',
                'action': 'show_welcome_message'
            },
            'learning_goals': {
                'title': 'Set Your Learning Goals',
                'type': 'form',
                'content': 'What would you like to achieve with NeuroPulse?',
                'action': 'collect_learning_goals'
            },
            'learning_style': {
                'title': 'Discover Your Learning Style',
                'type': 'questionnaire',
                'content': 'Help us understand how you learn best',
                'action': 'show_learning_style_quiz'
            },
            'ai_tutor_intro': {
                'title': 'Meet Your AI Tutor',
                'type': 'interactive_demo',
                'content': 'Experience the power of AI-assisted learning',
                'action': 'demo_ai_tutor'
            },
            'navigation_tour': {
                'title': 'Platform Navigation Tour',
                'type': 'guided_tour',
                'content': 'Learn to navigate NeuroPulse efficiently',
                'action': 'start_navigation_tour'
            },
            'first_quiz': {
                'title': 'Your First Adaptive Quiz',
                'type': 'interactive_activity',
                'content': 'Experience our adaptive difficulty system',
                'action': 'start_calibration_quiz'
            },
            'spaced_repetition': {
                'title': 'Spaced Repetition System',
                'type': 'feature_demo',
                'content': 'Optimize your long-term retention',
                'action': 'demo_spaced_repetition'
            },
            'mood_themes': {
                'title': 'Mood-Based Personalization',
                'type': 'feature_demo',
                'content': 'Adapt the interface to your emotional state',
                'action': 'demo_mood_themes'
            },
            'voice_navigation': {
                'title': 'Voice Commands',
                'type': 'feature_demo',
                'content': 'Control NeuroPulse with your voice',
                'action': 'demo_voice_navigation'
            }
        }
        
        return step_definitions.get(step_name, {
            'title': step_name.replace('_', ' ').title(),
            'type': 'generic',
            'content': f'Complete {step_name} step',
            'action': f'handle_{step_name}'
        })
    
    def advance_onboarding_step(self, user_id: str, step_data: dict = None) -> dict:
        """Advance user to next onboarding step"""
        progress = self.onboarding_progress[user_id]
        current_stage = progress['current_stage']
        current_step = progress['current_step']
        
        stage = self.onboarding_stages[current_stage]
        steps = stage['steps']
        
        # Process current step data if provided
        if step_data:
            self._process_step_data(user_id, steps[current_step], step_data)
        
        # Advance to next step
        next_step = current_step + 1
        
        if next_step >= len(steps):
            # Stage complete, move to next stage
            progress['completed_stages'].append(current_stage)
            next_stage = self._get_next_stage(current_stage)
            
            if next_stage:
                progress['current_stage'] = next_stage
                progress['current_step'] = 0
            else:
                # Onboarding complete
                progress['onboarding_complete'] = True
                progress['completed_at'] = datetime.now().isoformat()
                self._finalize_onboarding(user_id)
        else:
            progress['current_step'] = next_step
        
        # Update progress percentage
        progress['total_progress'] = self._calculate_total_progress(user_id)
        
        self._save_all_files()
        
        return self.get_onboarding_status(user_id)
    
    def _process_step_data(self, user_id: str, step_name: str, step_data: dict):
        """Process data collected from onboarding step"""
        if step_name in self.personalization_questions:
            # Store personalization response
            self.personalization_data[user_id]['responses'][step_name] = step_data
            
        elif step_name == 'learning_goals':
            # Store learning goals
            self.personalization_data[user_id]['learning_goals'] = step_data.get('goals', [])
            
        elif step_name == 'preferences':
            # Store general preferences
            self.personalization_data[user_id]['preferences'] = step_data
            
        # Update learning profile based on collected data
        self._update_learning_profile(user_id)
    
    def _update_learning_profile(self, user_id: str):
        """Update user's learning profile based on collected data"""
        responses = self.personalization_data[user_id]['responses']
        profile = {}
        
        # Analyze learning style preferences
        if 'learning_style' in responses:
            profile['learning_style'] = responses['learning_style']['value']
        
        if 'study_pace' in responses:
            profile['preferred_pace'] = responses['study_pace']['value']
        
        if 'challenge_preference' in responses:
            profile['challenge_tolerance'] = responses['challenge_preference']['value']
        
        if 'attention_span' in responses:
            profile['session_length'] = responses['attention_span']['value']
        
        if 'study_time_preference' in responses:
            profile['optimal_study_times'] = responses['study_time_preference']['values']
        
        if 'motivation_style' in responses:
            profile['motivation_factors'] = responses['motivation_style']['values']
        
        # Generate personalized recommendations
        recommendations = self._generate_personalized_recommendations(profile)
        
        self.personalization_data[user_id]['learning_profile'] = profile
        self.personalization_data[user_id]['recommendations'] = recommendations
        self.personalization_data[user_id]['setup_complete'] = True
    
    def _generate_personalized_recommendations(self, profile: dict) -> List[dict]:
        """Generate personalized recommendations based on learning profile"""
        recommendations = []
        
        # Learning style recommendations
        learning_style = profile.get('learning_style')
        if learning_style == 'visual':
            recommendations.append({
                'type': 'interface',
                'title': 'Visual Learning Optimization',
                'description': 'Enable enhanced visual elements and diagrams',
                'action': 'enable_visual_mode'
            })
        elif learning_style == 'auditory':
            recommendations.append({
                'type': 'feature',
                'title': 'Audio Features',
                'description': 'Enable text-to-speech and audio explanations',
                'action': 'enable_audio_features'
            })
        
        # Session length recommendations
        attention_span = profile.get('session_length')
        if attention_span == 'short':
            recommendations.append({
                'type': 'study_schedule',
                'title': 'Short Session Mode',
                'description': 'Optimize for 15-25 minute focused sessions',
                'action': 'enable_short_sessions'
            })
        elif attention_span == 'long':
            recommendations.append({
                'type': 'study_schedule',
                'title': 'Extended Learning Sessions',
                'description': 'Enable longer form content and deep dives',
                'action': 'enable_extended_sessions'
            })
        
        # Challenge level recommendations
        challenge_tolerance = profile.get('challenge_tolerance', 3)
        if challenge_tolerance >= 4:
            recommendations.append({
                'type': 'difficulty',
                'title': 'Challenge Mode',
                'description': 'Start with more challenging content',
                'action': 'increase_initial_difficulty'
            })
        elif challenge_tolerance <= 2:
            recommendations.append({
                'type': 'difficulty',
                'title': 'Gentle Learning Curve',
                'description': 'Begin with easier content and build confidence',
                'action': 'gentle_difficulty_curve'
            })
        
        # Motivation-based recommendations
        motivation_factors = profile.get('motivation_factors', [])
        if 'achievements' in motivation_factors:
            recommendations.append({
                'type': 'gamification',
                'title': 'Achievement System',
                'description': 'Enable badges and achievement tracking',
                'action': 'enable_achievements'
            })
        if 'competition' in motivation_factors:
            recommendations.append({
                'type': 'social',
                'title': 'Competitive Features',
                'description': 'Join leaderboards and challenges',
                'action': 'enable_competitions'
            })
        
        return recommendations
    
    def _get_next_stage(self, current_stage: str) -> Optional[str]:
        """Get the next onboarding stage"""
        stage_order = list(self.onboarding_stages.keys())
        current_index = stage_order.index(current_stage)
        
        if current_index + 1 < len(stage_order):
            return stage_order[current_index + 1]
        
        return None
    
    def _calculate_total_progress(self, user_id: str) -> float:
        """Calculate overall onboarding progress percentage"""
        progress = self.onboarding_progress[user_id]
        
        total_steps = sum(len(stage['steps']) for stage in self.onboarding_stages.values())
        completed_steps = 0
        
        # Count completed stages
        for stage_name in progress['completed_stages']:
            completed_steps += len(self.onboarding_stages[stage_name]['steps'])
        
        # Add current stage progress
        completed_steps += progress['current_step']
        
        return (completed_steps / total_steps) * 100
    
    def _calculate_remaining_time(self, user_id: str) -> int:
        """Calculate estimated remaining onboarding time in minutes"""
        progress = self.onboarding_progress[user_id]
        current_stage = progress['current_stage']
        
        remaining_time = 0
        stage_started = False
        
        for stage_name, stage in self.onboarding_stages.items():
            if stage_name == current_stage:
                stage_started = True
                # Add remaining time for current stage
                current_step = progress['current_step']
                total_steps = len(stage['steps'])
                remaining_steps = total_steps - current_step
                stage_time = stage['estimated_time']
                remaining_time += (remaining_steps / total_steps) * stage_time
            elif stage_started:
                # Add time for upcoming stages
                remaining_time += stage['estimated_time']
        
        return int(remaining_time)
    
    def _get_personalization_status(self, user_id: str) -> dict:
        """Get current personalization setup status"""
        data = self.personalization_data.get(user_id, {})
        responses = data.get('responses', {})
        
        total_questions = len(self.personalization_questions)
        answered_questions = len(responses)
        
        return {
            'questions_answered': answered_questions,
            'total_questions': total_questions,
            'completion_percentage': (answered_questions / total_questions) * 100,
            'profile_complete': data.get('setup_complete', False),
            'recommendations_generated': len(data.get('recommendations', []))
        }
    
    def skip_onboarding_stage(self, user_id: str, stage_name: str = None) -> dict:
        """Skip current or specified onboarding stage"""
        progress = self.onboarding_progress[user_id]
        stage_to_skip = stage_name or progress['current_stage']
        
        # Check if stage can be skipped
        stage = self.onboarding_stages.get(stage_to_skip)
        if stage and stage.get('required', False):
            return {
                'success': False,
                'error': 'Cannot skip required onboarding stage',
                'stage': stage_to_skip
            }
        
        # Mark stage as completed
        if stage_to_skip not in progress['completed_stages']:
            progress['completed_stages'].append(stage_to_skip)
        
        # Move to next stage
        next_stage = self._get_next_stage(stage_to_skip)
        if next_stage:
            progress['current_stage'] = next_stage
            progress['current_step'] = 0
        else:
            progress['onboarding_complete'] = True
            progress['completed_at'] = datetime.now().isoformat()
        
        progress['total_progress'] = self._calculate_total_progress(user_id)
        
        self._save_all_files()
        
        return {
            'success': True,
            'skipped_stage': stage_to_skip,
            'new_status': self.get_onboarding_status(user_id)
        }
    
    def get_interactive_tour(self, user_id: str, tour_name: str) -> dict:
        """Get interactive tour configuration"""
        if tour_name not in self.tour_definitions:
            return {'error': 'Tour not found'}
        
        tour = self.tour_definitions[tour_name].copy()
        
        # Add user preferences
        progress = self.onboarding_progress.get(user_id, {})
        tour_prefs = progress.get('tour_preferences', {})
        
        tour['user_preferences'] = tour_prefs
        tour['tour_id'] = str(uuid.uuid4())
        
        # Track tour start
        if user_id not in self.tour_data:
            self.tour_data[user_id] = {}
        
        self.tour_data[user_id][tour['tour_id']] = {
            'tour_name': tour_name,
            'started_at': datetime.now().isoformat(),
            'current_step': 0,
            'completed': False
        }
        
        self._save_all_files()
        
        return tour
    
    def update_tour_progress(self, user_id: str, tour_id: str, step_index: int, action_data: dict = None) -> dict:
        """Update progress for interactive tour"""
        if user_id not in self.tour_data or tour_id not in self.tour_data[user_id]:
            return {'error': 'Tour session not found'}
        
        tour_session = self.tour_data[user_id][tour_id]
        tour_session['current_step'] = step_index
        tour_session['last_updated'] = datetime.now().isoformat()
        
        if action_data:
            if 'actions' not in tour_session:
                tour_session['actions'] = []
            tour_session['actions'].append({
                'step': step_index,
                'action': action_data,
                'timestamp': datetime.now().isoformat()
            })
        
        self._save_all_files()
        
        return {
            'success': True,
            'current_step': step_index,
            'tour_progress': tour_session
        }
    
    def complete_tour(self, user_id: str, tour_id: str) -> dict:
        """Mark tour as completed"""
        if user_id not in self.tour_data or tour_id not in self.tour_data[user_id]:
            return {'error': 'Tour session not found'}
        
        tour_session = self.tour_data[user_id][tour_id]
        tour_session['completed'] = True
        tour_session['completed_at'] = datetime.now().isoformat()
        
        # Update onboarding progress if this was part of onboarding
        self._check_onboarding_tour_completion(user_id, tour_session['tour_name'])
        
        self._save_all_files()
        
        return {
            'success': True,
            'tour_completed': True,
            'completion_time': tour_session['completed_at']
        }
    
    def _check_onboarding_tour_completion(self, user_id: str, tour_name: str):
        """Check if completed tour advances onboarding progress"""
        if user_id not in self.onboarding_progress:
            return
        
        progress = self.onboarding_progress[user_id]
        current_stage = progress['current_stage']
        current_step = progress['current_step']
        
        stage = self.onboarding_stages.get(current_stage, {})
        steps = stage.get('steps', [])
        
        if current_step < len(steps) and tour_name in steps[current_step]:
            # This tour completion advances onboarding
            self.advance_onboarding_step(user_id)
    
    def _finalize_onboarding(self, user_id: str):
        """Finalize onboarding process and set up user account"""
        # Apply personalized recommendations
        personalization = self.personalization_data.get(user_id, {})
        recommendations = personalization.get('recommendations', [])
        
        for rec in recommendations:
            if rec['action'] == 'enable_visual_mode':
                # Apply visual learning optimizations
                pass
            elif rec['action'] == 'enable_audio_features':
                # Enable audio features
                pass
            # Apply other recommendations...
        
        # Initialize feature discovery tracking
        if user_id not in self.feature_discovery:
            self.feature_discovery[user_id] = {
                'discovered_features': [],
                'feature_usage': {},
                'discovery_progress': 0.0
            }
    
    def get_feature_discovery_status(self, user_id: str) -> dict:
        """Get feature discovery progress and suggestions"""
        if user_id not in self.feature_discovery:
            return {'no_data': True}
        
        discovery = self.feature_discovery[user_id]
        total_features = len(self.feature_highlights)
        discovered_count = len(discovery['discovered_features'])
        
        # Suggest next feature to discover
        undiscovered_features = [
            name for name in self.feature_highlights.keys()
            if name not in discovery['discovered_features']
        ]
        
        next_suggestion = None
        if undiscovered_features:
            # Prioritize based on user profile
            personalization = self.personalization_data.get(user_id, {})
            profile = personalization.get('learning_profile', {})
            
            next_suggestion = self._suggest_next_feature(undiscovered_features, profile)
        
        return {
            'discovered_features': discovered_count,
            'total_features': total_features,
            'discovery_progress': (discovered_count / total_features) * 100,
            'next_suggestion': next_suggestion,
            'available_features': {
                name: info for name, info in self.feature_highlights.items()
                if name not in discovery['discovered_features']
            }
        }
    
    def _suggest_next_feature(self, available_features: List[str], profile: dict) -> Optional[dict]:
        """Suggest next feature based on user profile"""
        # Priority mapping based on user characteristics
        feature_priorities = {
            'ai_tutor': ['help_seeking', 'explanation_oriented'],
            'spaced_repetition': ['retention_focused', 'systematic_learner'],
            'adaptive_difficulty': ['challenge_seeking', 'performance_oriented'],
            'mood_themes': ['aesthetic_sensitive', 'emotional_awareness'],
            'voice_navigation': ['accessibility_needs', 'efficiency_focused'],
            'collaboration': ['social_learner', 'team_oriented']
        }
        
        # Score features based on profile match
        feature_scores = {}
        for feature in available_features:
            score = 0
            feature_chars = feature_priorities.get(feature, [])
            
            # Simple scoring based on profile characteristics
            if 'learning_style' in profile:
                if profile['learning_style'] == 'auditory' and feature == 'voice_navigation':
                    score += 3
                elif profile['learning_style'] == 'visual' and feature == 'mood_themes':
                    score += 2
            
            if 'motivation_factors' in profile:
                motivation = profile['motivation_factors']
                if 'collaboration' in motivation and feature == 'collaboration':
                    score += 3
                elif 'progress_tracking' in motivation and feature == 'spaced_repetition':
                    score += 2
            
            feature_scores[feature] = score
        
        if feature_scores:
            best_feature = max(feature_scores.items(), key=lambda x: x[1])[0]
            return {
                'feature_name': best_feature,
                'feature_info': self.feature_highlights[best_feature],
                'match_score': feature_scores[best_feature]
            }
        
        return None

# Initialize global onboarding system
onboarding_system = OnboardingSystem()