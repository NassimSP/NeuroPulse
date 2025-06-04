"""
Interactive Learning Journey Map for NeuroPulse
Visual progress tracking with milestone-based learning paths
"""

import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class MilestoneType(Enum):
    FOUNDATION = "foundation"
    SKILL_UNLOCK = "skill_unlock"
    MASTERY = "mastery"
    BREAKTHROUGH = "breakthrough"
    EXPERTISE = "expertise"

class LearningPath(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTERY = "mastery"

class LearningJourneyEngine:
    """Advanced learning journey mapping with visual progress tracking"""
    
    def __init__(self):
        self.journey_maps = {}
        self.milestones = {}
        self.learning_paths = {}
        self.progress_tracking = {}
        self.subject_hierarchies = {}
        self.load_data()
        self.initialize_subject_hierarchies()
    
    def load_data(self):
        """Load learning journey data from storage"""
        try:
            with open('data/learning_journey_data.json', 'r') as f:
                data = json.load(f)
                self.journey_maps = data.get('journey_maps', {})
                self.milestones = data.get('milestones', {})
                self.learning_paths = data.get('learning_paths', {})
                self.progress_tracking = data.get('progress_tracking', {})
                self.subject_hierarchies = data.get('subject_hierarchies', {})
        except FileNotFoundError:
            self.journey_maps = {}
            self.milestones = {}
            self.learning_paths = {}
            self.progress_tracking = {}
            self.subject_hierarchies = {}
    
    def save_data(self):
        """Save learning journey data to storage"""
        import os
        os.makedirs('data', exist_ok=True)
        
        data = {
            'journey_maps': self.journey_maps,
            'milestones': self.milestones,
            'learning_paths': self.learning_paths,
            'progress_tracking': self.progress_tracking,
            'subject_hierarchies': self.subject_hierarchies,
            'last_updated': datetime.now().isoformat()
        }
        
        with open('data/learning_journey_data.json', 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def initialize_subject_hierarchies(self):
        """Initialize comprehensive subject learning hierarchies"""
        
        self.subject_hierarchies = {
            'Python Programming': {
                'levels': [
                    {
                        'name': 'Foundation',
                        'description': 'Basic syntax and concepts',
                        'milestones': [
                            {'name': 'Variables & Data Types', 'xp_required': 0, 'concepts': ['variables', 'strings', 'numbers', 'booleans']},
                            {'name': 'Control Structures', 'xp_required': 100, 'concepts': ['if/else', 'loops', 'conditions']},
                            {'name': 'Functions Basics', 'xp_required': 200, 'concepts': ['function definition', 'parameters', 'return values']}
                        ]
                    },
                    {
                        'name': 'Intermediate',
                        'description': 'Data structures and OOP',
                        'milestones': [
                            {'name': 'Data Structures', 'xp_required': 350, 'concepts': ['lists', 'dictionaries', 'sets', 'tuples']},
                            {'name': 'Object-Oriented Programming', 'xp_required': 500, 'concepts': ['classes', 'objects', 'inheritance', 'polymorphism']},
                            {'name': 'File Handling & Exceptions', 'xp_required': 650, 'concepts': ['file I/O', 'error handling', 'try/except']}
                        ]
                    },
                    {
                        'name': 'Advanced',
                        'description': 'Advanced concepts and libraries',
                        'milestones': [
                            {'name': 'Advanced Functions', 'xp_required': 800, 'concepts': ['decorators', 'generators', 'lambda functions']},
                            {'name': 'Libraries & Modules', 'xp_required': 1000, 'concepts': ['numpy', 'pandas', 'requests', 'json']},
                            {'name': 'Web Development', 'xp_required': 1200, 'concepts': ['Flask', 'APIs', 'databases']}
                        ]
                    },
                    {
                        'name': 'Expert',
                        'description': 'Professional development skills',
                        'milestones': [
                            {'name': 'Testing & Debugging', 'xp_required': 1500, 'concepts': ['unit testing', 'debugging', 'profiling']},
                            {'name': 'Advanced Patterns', 'xp_required': 1800, 'concepts': ['design patterns', 'architecture', 'best practices']},
                            {'name': 'Performance Optimization', 'xp_required': 2100, 'concepts': ['optimization', 'concurrency', 'memory management']}
                        ]
                    }
                ]
            },
            
            'Electrical Engineering': {
                'levels': [
                    {
                        'name': 'Foundation',
                        'description': 'Basic electrical concepts',
                        'milestones': [
                            {'name': 'Basic Circuit Theory', 'xp_required': 0, 'concepts': ['voltage', 'current', 'resistance', 'power']},
                            {'name': 'Ohms Law & Kirchhoff', 'xp_required': 120, 'concepts': ['ohms law', 'KVL', 'KCL', 'circuit analysis']},
                            {'name': 'AC/DC Fundamentals', 'xp_required': 250, 'concepts': ['AC circuits', 'DC circuits', 'waveforms', 'frequency']}
                        ]
                    },
                    {
                        'name': 'Intermediate',
                        'description': 'Circuit analysis and components',
                        'milestones': [
                            {'name': 'Complex Circuits', 'xp_required': 400, 'concepts': ['impedance', 'reactance', 'phasors', 'complex analysis']},
                            {'name': 'Electronic Components', 'xp_required': 600, 'concepts': ['diodes', 'transistors', 'capacitors', 'inductors']},
                            {'name': 'Amplifiers & Filters', 'xp_required': 800, 'concepts': ['op-amps', 'filters', 'amplification', 'feedback']}
                        ]
                    },
                    {
                        'name': 'Advanced',
                        'description': 'System design and analysis',
                        'milestones': [
                            {'name': 'Digital Electronics', 'xp_required': 1000, 'concepts': ['logic gates', 'flip-flops', 'counters', 'memory']},
                            {'name': 'Microcontrollers', 'xp_required': 1300, 'concepts': ['microcontrollers', 'programming', 'interfaces', 'sensors']},
                            {'name': 'Power Systems', 'xp_required': 1600, 'concepts': ['power electronics', 'transformers', 'motors', 'generators']}
                        ]
                    }
                ]
            },
            
            'Data Analysis': {
                'levels': [
                    {
                        'name': 'Foundation',
                        'description': 'Data fundamentals',
                        'milestones': [
                            {'name': 'Data Types & Structures', 'xp_required': 0, 'concepts': ['data types', 'datasets', 'variables', 'observations']},
                            {'name': 'Descriptive Statistics', 'xp_required': 100, 'concepts': ['mean', 'median', 'mode', 'standard deviation']},
                            {'name': 'Data Visualization Basics', 'xp_required': 200, 'concepts': ['charts', 'graphs', 'plots', 'visualization principles']}
                        ]
                    },
                    {
                        'name': 'Intermediate',
                        'description': 'Statistical analysis',
                        'milestones': [
                            {'name': 'Probability & Distributions', 'xp_required': 350, 'concepts': ['probability', 'distributions', 'sampling', 'hypothesis testing']},
                            {'name': 'Correlation & Regression', 'xp_required': 500, 'concepts': ['correlation', 'linear regression', 'multivariate analysis']},
                            {'name': 'Data Cleaning & Preprocessing', 'xp_required': 650, 'concepts': ['data cleaning', 'missing values', 'outliers', 'normalization']}
                        ]
                    }
                ]
            },
            
            'Mathematics': {
                'levels': [
                    {
                        'name': 'Foundation',
                        'description': 'Basic mathematical concepts',
                        'milestones': [
                            {'name': 'Arithmetic Operations', 'xp_required': 0, 'concepts': ['addition', 'subtraction', 'multiplication', 'division']},
                            {'name': 'Fractions & Decimals', 'xp_required': 80, 'concepts': ['fractions', 'decimals', 'percentages', 'ratios']},
                            {'name': 'Basic Algebra', 'xp_required': 160, 'concepts': ['variables', 'equations', 'inequalities', 'expressions']}
                        ]
                    },
                    {
                        'name': 'Intermediate',
                        'description': 'Advanced algebra and geometry',
                        'milestones': [
                            {'name': 'Quadratic Equations', 'xp_required': 280, 'concepts': ['quadratics', 'factoring', 'completing the square']},
                            {'name': 'Geometry Fundamentals', 'xp_required': 400, 'concepts': ['shapes', 'area', 'volume', 'angles']},
                            {'name': 'Trigonometry Basics', 'xp_required': 550, 'concepts': ['sine', 'cosine', 'tangent', 'triangles']}
                        ]
                    }
                ]
            }
        }
        
        self.save_data()
    
    def initialize_user_journey(self, user_id: str, subject: str) -> Dict:
        """Initialize learning journey for a user in a specific subject"""
        
        if user_id not in self.journey_maps:
            self.journey_maps[user_id] = {}
        
        if subject not in self.journey_maps[user_id]:
            self.journey_maps[user_id][subject] = {
                'current_level': 0,
                'current_milestone': 0,
                'total_xp': 0,
                'completed_milestones': [],
                'unlocked_concepts': [],
                'journey_start_date': datetime.now().isoformat(),
                'last_activity': datetime.now().isoformat(),
                'learning_path': LearningPath.BEGINNER.value,
                'achievements': [],
                'streak_data': {
                    'current_streak': 0,
                    'longest_streak': 0,
                    'last_activity_date': None
                }
            }
        
        self.save_data()
        return self.journey_maps[user_id][subject]
    
    def update_progress(self, user_id: str, subject: str, session_data: Dict) -> Dict:
        """Update user's learning journey progress based on session data"""
        
        # Initialize journey if needed
        self.initialize_user_journey(user_id, subject)
        
        journey = self.journey_maps[user_id][subject]
        
        # Calculate XP earned from session
        xp_earned = self._calculate_session_xp(session_data)
        journey['total_xp'] += xp_earned
        journey['last_activity'] = datetime.now().isoformat()
        
        # Update streak
        self._update_streak(journey)
        
        # Check for milestone completions
        new_milestones = self._check_milestone_completions(user_id, subject, journey)
        
        # Check for level advancement
        level_advancement = self._check_level_advancement(subject, journey)
        
        # Update learning path if needed
        self._update_learning_path(journey)
        
        # Generate progress insights
        progress_insights = self._generate_progress_insights(journey, session_data)
        
        self.save_data()
        
        return {
            'xp_earned': xp_earned,
            'total_xp': journey['total_xp'],
            'current_level': journey['current_level'],
            'current_milestone': journey['current_milestone'],
            'new_milestones': new_milestones,
            'level_advancement': level_advancement,
            'progress_insights': progress_insights,
            'next_milestone': self._get_next_milestone(subject, journey),
            'completion_percentage': self._calculate_completion_percentage(subject, journey)
        }
    
    def _calculate_session_xp(self, session_data: Dict) -> int:
        """Calculate XP earned from a learning session"""
        base_xp = len(session_data.get('questions', [])) * 10
        accuracy = session_data.get('accuracy', 0)
        confidence = session_data.get('avg_confidence', 3)
        
        # Accuracy bonus
        accuracy_bonus = int(base_xp * (accuracy / 100) * 0.5)
        
        # Confidence bonus (realistic self-assessment)
        confidence_bonus = int(base_xp * 0.1) if 2 <= confidence <= 4 else 0
        
        # Difficulty multiplier
        difficulty_map = {'foundation': 1.0, 'beginner': 1.1, 'intermediate': 1.2, 'advanced': 1.4, 'expert': 1.6}
        difficulty_multiplier = difficulty_map.get(session_data.get('difficulty', 'intermediate'), 1.2)
        
        total_xp = int((base_xp + accuracy_bonus + confidence_bonus) * difficulty_multiplier)
        return max(total_xp, base_xp // 2)  # Minimum 50% of base XP
    
    def _update_streak(self, journey: Dict):
        """Update learning streak data"""
        today = datetime.now().date()
        last_activity = journey['streak_data'].get('last_activity_date')
        
        if last_activity:
            last_date = datetime.fromisoformat(last_activity).date()
            days_diff = (today - last_date).days
            
            if days_diff == 0:
                # Same day, no change to streak
                pass
            elif days_diff == 1:
                # Consecutive day, increment streak
                journey['streak_data']['current_streak'] += 1
                if journey['streak_data']['current_streak'] > journey['streak_data']['longest_streak']:
                    journey['streak_data']['longest_streak'] = journey['streak_data']['current_streak']
            else:
                # Streak broken
                journey['streak_data']['current_streak'] = 1
        else:
            # First activity
            journey['streak_data']['current_streak'] = 1
        
        journey['streak_data']['last_activity_date'] = today.isoformat()
    
    def _check_milestone_completions(self, user_id: str, subject: str, journey: Dict) -> List[Dict]:
        """Check for new milestone completions"""
        new_milestones = []
        
        if subject not in self.subject_hierarchies:
            return new_milestones
        
        hierarchy = self.subject_hierarchies[subject]
        current_level_idx = journey['current_level']
        
        if current_level_idx >= len(hierarchy['levels']):
            return new_milestones
        
        current_level = hierarchy['levels'][current_level_idx]
        milestones = current_level['milestones']
        
        for i, milestone in enumerate(milestones):
            milestone_id = f"{subject}_{current_level_idx}_{i}"
            
            if milestone_id not in journey['completed_milestones'] and journey['total_xp'] >= milestone['xp_required']:
                # Milestone completed!
                journey['completed_milestones'].append(milestone_id)
                journey['current_milestone'] = max(journey['current_milestone'], i + 1)
                
                # Unlock concepts
                for concept in milestone['concepts']:
                    if concept not in journey['unlocked_concepts']:
                        journey['unlocked_concepts'].append(concept)
                
                new_milestone = {
                    'id': milestone_id,
                    'name': milestone['name'],
                    'level': current_level['name'],
                    'concepts_unlocked': milestone['concepts'],
                    'completion_date': datetime.now().isoformat(),
                    'type': self._determine_milestone_type(milestone, current_level_idx, i)
                }
                
                new_milestones.append(new_milestone)
                
                # Add to achievements
                journey['achievements'].append({
                    'type': 'milestone_completion',
                    'milestone': new_milestone,
                    'date': datetime.now().isoformat()
                })
        
        return new_milestones
    
    def _check_level_advancement(self, subject: str, journey: Dict) -> Optional[Dict]:
        """Check if user should advance to next level"""
        
        if subject not in self.subject_hierarchies:
            return None
        
        hierarchy = self.subject_hierarchies[subject]
        current_level_idx = journey['current_level']
        
        if current_level_idx >= len(hierarchy['levels']) - 1:
            return None  # Already at max level
        
        current_level = hierarchy['levels'][current_level_idx]
        milestones = current_level['milestones']
        
        # Check if all milestones in current level are completed
        completed_in_level = 0
        for i, milestone in enumerate(milestones):
            milestone_id = f"{subject}_{current_level_idx}_{i}"
            if milestone_id in journey['completed_milestones']:
                completed_in_level += 1
        
        if completed_in_level >= len(milestones):
            # Advance to next level
            journey['current_level'] += 1
            journey['current_milestone'] = 0
            
            next_level = hierarchy['levels'][journey['current_level']]
            
            advancement = {
                'previous_level': current_level['name'],
                'new_level': next_level['name'],
                'advancement_date': datetime.now().isoformat(),
                'total_xp_at_advancement': journey['total_xp'],
                'milestones_completed': completed_in_level
            }
            
            # Add to achievements
            journey['achievements'].append({
                'type': 'level_advancement',
                'advancement': advancement,
                'date': datetime.now().isoformat()
            })
            
            return advancement
        
        return None
    
    def _determine_milestone_type(self, milestone: Dict, level_idx: int, milestone_idx: int) -> str:
        """Determine the type of milestone based on position and content"""
        if level_idx == 0 and milestone_idx == 0:
            return MilestoneType.FOUNDATION.value
        elif 'mastery' in milestone['name'].lower() or 'expert' in milestone['name'].lower():
            return MilestoneType.MASTERY.value
        elif 'advanced' in milestone['name'].lower() or 'optimization' in milestone['name'].lower():
            return MilestoneType.EXPERTISE.value
        elif milestone_idx == 0:  # First milestone in a level
            return MilestoneType.SKILL_UNLOCK.value
        else:
            return MilestoneType.BREAKTHROUGH.value
    
    def _update_learning_path(self, journey: Dict):
        """Update learning path based on progress and performance"""
        total_xp = journey['total_xp']
        
        if total_xp >= 2000:
            journey['learning_path'] = LearningPath.MASTERY.value
        elif total_xp >= 1500:
            journey['learning_path'] = LearningPath.EXPERT.value
        elif total_xp >= 800:
            journey['learning_path'] = LearningPath.ADVANCED.value
        elif total_xp >= 300:
            journey['learning_path'] = LearningPath.INTERMEDIATE.value
        else:
            journey['learning_path'] = LearningPath.BEGINNER.value
    
    def _generate_progress_insights(self, journey: Dict, session_data: Dict) -> List[str]:
        """Generate insights about learning progress"""
        insights = []
        
        # XP insights
        total_xp = journey['total_xp']
        if total_xp >= 1000:
            insights.append(f"Impressive! You've earned {total_xp} XP and are becoming an expert!")
        elif total_xp >= 500:
            insights.append(f"Great progress! {total_xp} XP earned - you're building solid expertise.")
        elif total_xp >= 100:
            insights.append(f"Good momentum! {total_xp} XP earned - keep up the consistent learning.")
        
        # Streak insights
        current_streak = journey['streak_data']['current_streak']
        if current_streak >= 7:
            insights.append(f"Amazing {current_streak}-day streak! Consistency is building mastery.")
        elif current_streak >= 3:
            insights.append(f"{current_streak}-day learning streak active - great habit forming!")
        
        # Concept insights
        concepts_unlocked = len(journey['unlocked_concepts'])
        if concepts_unlocked >= 20:
            insights.append(f"Mastery developing! {concepts_unlocked} concepts unlocked across multiple areas.")
        elif concepts_unlocked >= 10:
            insights.append(f"Knowledge expanding! {concepts_unlocked} concepts mastered so far.")
        
        # Recent performance insights
        accuracy = session_data.get('accuracy', 0)
        if accuracy >= 90:
            insights.append("Excellent accuracy! Your understanding is deepening significantly.")
        elif accuracy >= 75:
            insights.append("Strong performance! You're grasping concepts well.")
        
        return insights[:3]  # Limit to top 3 insights
    
    def _get_next_milestone(self, subject: str, journey: Dict) -> Optional[Dict]:
        """Get information about the next milestone to achieve"""
        
        if subject not in self.subject_hierarchies:
            return None
        
        hierarchy = self.subject_hierarchies[subject]
        current_level_idx = journey['current_level']
        
        if current_level_idx >= len(hierarchy['levels']):
            return None
        
        current_level = hierarchy['levels'][current_level_idx]
        milestones = current_level['milestones']
        
        # Find next uncompleted milestone
        for i, milestone in enumerate(milestones):
            milestone_id = f"{subject}_{current_level_idx}_{i}"
            if milestone_id not in journey['completed_milestones']:
                xp_needed = max(0, milestone['xp_required'] - journey['total_xp'])
                progress_percentage = min(100, (journey['total_xp'] / milestone['xp_required']) * 100) if milestone['xp_required'] > 0 else 100
                
                return {
                    'name': milestone['name'],
                    'level': current_level['name'],
                    'xp_required': milestone['xp_required'],
                    'xp_needed': xp_needed,
                    'progress_percentage': round(progress_percentage, 1),
                    'concepts': milestone['concepts'],
                    'estimated_sessions': max(1, xp_needed // 50)  # Rough estimate
                }
        
        # All milestones in current level completed, check next level
        if current_level_idx + 1 < len(hierarchy['levels']):
            next_level = hierarchy['levels'][current_level_idx + 1]
            first_milestone = next_level['milestones'][0]
            xp_needed = max(0, first_milestone['xp_required'] - journey['total_xp'])
            
            return {
                'name': first_milestone['name'],
                'level': next_level['name'],
                'xp_required': first_milestone['xp_required'],
                'xp_needed': xp_needed,
                'progress_percentage': min(100, (journey['total_xp'] / first_milestone['xp_required']) * 100) if first_milestone['xp_required'] > 0 else 100,
                'concepts': first_milestone['concepts'],
                'estimated_sessions': max(1, xp_needed // 50),
                'level_transition': True
            }
        
        return None
    
    def _calculate_completion_percentage(self, subject: str, journey: Dict) -> float:
        """Calculate overall completion percentage for the subject"""
        
        if subject not in self.subject_hierarchies:
            return 0.0
        
        hierarchy = self.subject_hierarchies[subject]
        total_milestones = sum(len(level['milestones']) for level in hierarchy['levels'])
        completed_milestones = len(journey['completed_milestones'])
        
        return round((completed_milestones / total_milestones) * 100, 1) if total_milestones > 0 else 0.0
    
    def get_visual_journey_map(self, user_id: str, subject: str) -> Dict:
        """Generate comprehensive visual journey map data"""
        
        if user_id not in self.journey_maps or subject not in self.journey_maps[user_id]:
            self.initialize_user_journey(user_id, subject)
        
        journey = self.journey_maps[user_id][subject]
        
        if subject not in self.subject_hierarchies:
            return {'error': f'Subject {subject} not available'}
        
        hierarchy = self.subject_hierarchies[subject]
        
        # Build visual map structure
        visual_map = {
            'subject': subject,
            'user_progress': {
                'total_xp': journey['total_xp'],
                'current_level': journey['current_level'],
                'current_milestone': journey['current_milestone'],
                'learning_path': journey['learning_path'],
                'completion_percentage': self._calculate_completion_percentage(subject, journey),
                'concepts_unlocked': len(journey['unlocked_concepts']),
                'streak': journey['streak_data']['current_streak'],
                'journey_duration': self._calculate_journey_duration(journey)
            },
            'levels': [],
            'achievements': journey['achievements'][-10:],  # Last 10 achievements
            'next_milestone': self._get_next_milestone(subject, journey),
            'progress_insights': self._generate_progress_insights(journey, {}),
            'learning_recommendations': self._generate_learning_recommendations(journey, subject)
        }
        
        # Build level and milestone data
        for level_idx, level in enumerate(hierarchy['levels']):
            level_data = {
                'name': level['name'],
                'description': level['description'],
                'index': level_idx,
                'is_current': level_idx == journey['current_level'],
                'is_completed': level_idx < journey['current_level'],
                'is_locked': level_idx > journey['current_level'],
                'milestones': []
            }
            
            for milestone_idx, milestone in enumerate(level['milestones']):
                milestone_id = f"{subject}_{level_idx}_{milestone_idx}"
                is_completed = milestone_id in journey['completed_milestones']
                is_current = (level_idx == journey['current_level'] and 
                            milestone_idx == journey['current_milestone'] and 
                            not is_completed)
                
                progress_percentage = 0
                if is_completed:
                    progress_percentage = 100
                elif milestone['xp_required'] <= journey['total_xp']:
                    progress_percentage = 100
                elif milestone['xp_required'] > 0:
                    progress_percentage = min(100, (journey['total_xp'] / milestone['xp_required']) * 100)
                
                milestone_data = {
                    'name': milestone['name'],
                    'index': milestone_idx,
                    'xp_required': milestone['xp_required'],
                    'concepts': milestone['concepts'],
                    'is_completed': is_completed,
                    'is_current': is_current,
                    'is_accessible': journey['total_xp'] >= milestone['xp_required'] * 0.8,  # 80% threshold for accessibility
                    'progress_percentage': round(progress_percentage, 1),
                    'type': self._determine_milestone_type(milestone, level_idx, milestone_idx)
                }
                
                level_data['milestones'].append(milestone_data)
            
            visual_map['levels'].append(level_data)
        
        return visual_map
    
    def _calculate_journey_duration(self, journey: Dict) -> Dict:
        """Calculate learning journey duration statistics"""
        start_date = datetime.fromisoformat(journey['journey_start_date'])
        now = datetime.now()
        duration = now - start_date
        
        return {
            'days': duration.days,
            'weeks': duration.days // 7,
            'months': duration.days // 30,
            'start_date': journey['journey_start_date'],
            'last_activity': journey['last_activity']
        }
    
    def _generate_learning_recommendations(self, journey: Dict, subject: str) -> List[str]:
        """Generate personalized learning recommendations"""
        recommendations = []
        
        # Based on progress
        completion = self._calculate_completion_percentage(subject, journey)
        if completion < 20:
            recommendations.append("Focus on foundational concepts to build a strong learning base")
        elif completion < 50:
            recommendations.append("You're making good progress! Continue with regular practice sessions")
        elif completion < 80:
            recommendations.append("Advanced concepts await! Challenge yourself with harder problems")
        else:
            recommendations.append("Near mastery! Consider exploring related subjects or advanced applications")
        
        # Based on streak
        streak = journey['streak_data']['current_streak']
        if streak < 3:
            recommendations.append("Build a learning routine - aim for 3+ consecutive days")
        elif streak >= 7:
            recommendations.append("Excellent consistency! Your streak is building lasting knowledge")
        
        # Based on learning path
        path = journey['learning_path']
        if path == LearningPath.BEGINNER.value:
            recommendations.append("Take time to understand each concept before moving forward")
        elif path == LearningPath.EXPERT.value:
            recommendations.append("Consider mentoring others or contributing to projects in this area")
        
        return recommendations[:3]  # Limit to top 3 recommendations
    
    def get_subject_overview(self, subject: str) -> Dict:
        """Get comprehensive overview of a subject's learning structure"""
        
        if subject not in self.subject_hierarchies:
            return {'error': f'Subject {subject} not available'}
        
        hierarchy = self.subject_hierarchies[subject]
        
        overview = {
            'subject': subject,
            'total_levels': len(hierarchy['levels']),
            'total_milestones': sum(len(level['milestones']) for level in hierarchy['levels']),
            'total_concepts': sum(len(concept) for level in hierarchy['levels'] 
                                for milestone in level['milestones'] 
                                for concept in milestone['concepts']),
            'estimated_completion_time': self._estimate_completion_time(hierarchy),
            'difficulty_progression': [level['name'] for level in hierarchy['levels']],
            'level_details': []
        }
        
        for level in hierarchy['levels']:
            level_detail = {
                'name': level['name'],
                'description': level['description'],
                'milestone_count': len(level['milestones']),
                'concept_count': sum(len(milestone['concepts']) for milestone in level['milestones']),
                'xp_range': {
                    'min': min(milestone['xp_required'] for milestone in level['milestones']),
                    'max': max(milestone['xp_required'] for milestone in level['milestones'])
                } if level['milestones'] else {'min': 0, 'max': 0}
            }
            overview['level_details'].append(level_detail)
        
        return overview
    
    def _estimate_completion_time(self, hierarchy: Dict) -> Dict:
        """Estimate time required to complete the subject"""
        total_milestones = sum(len(level['milestones']) for level in hierarchy['levels'])
        max_xp = max(milestone['xp_required'] for level in hierarchy['levels'] 
                    for milestone in level['milestones']) if hierarchy['levels'] else 0
        
        # Rough estimates based on average learning pace
        estimated_sessions = max_xp // 40  # Assuming ~40 XP per session
        estimated_hours = estimated_sessions * 0.5  # ~30 minutes per session
        estimated_weeks = estimated_sessions // 5  # 5 sessions per week
        
        return {
            'estimated_sessions': estimated_sessions,
            'estimated_hours': round(estimated_hours, 1),
            'estimated_weeks': estimated_weeks,
            'note': 'Estimates based on average learning pace and may vary by individual'
        }

# Global instance
learning_journey_engine = LearningJourneyEngine()