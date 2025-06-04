"""
Universal Subject Management System for NeuroPulse
Handles dynamic subject creation, progression tracking, and adaptive learning paths
"""

import json
import os
from datetime import datetime, timedelta

class SubjectManager:
    def __init__(self):
        self.subjects_file = 'subjects_data.json'
        self.user_progress_file = 'user_progress.json'
        self.load_subjects()
        self.load_user_progress()
    
    def load_subjects(self):
        """Load available subjects or create default structure"""
        try:
            with open(self.subjects_file, 'r') as f:
                self.subjects = json.load(f)
        except FileNotFoundError:
            self.subjects = self.create_default_subjects()
            self.save_subjects()
    
    def load_user_progress(self):
        """Load user progress data"""
        try:
            with open(self.user_progress_file, 'r') as f:
                self.user_progress = json.load(f)
        except FileNotFoundError:
            self.user_progress = {}
    
    def save_subjects(self):
        """Save subjects to file"""
        with open(self.subjects_file, 'w') as f:
            json.dump(self.subjects, f, indent=2)
    
    def save_user_progress(self):
        """Save user progress to file"""
        with open(self.user_progress_file, 'w') as f:
            json.dump(self.user_progress, f, indent=2)
    
    def create_default_subjects(self):
        """Create comprehensive subject categories"""
        return {
            "science": {
                "name": "Science & Technology",
                "icon": "zap",
                "color": "#3498db",
                "topics": {
                    "biology": {
                        "name": "Biology",
                        "subtopics": ["Cell Biology", "Genetics", "Ecology", "Human Anatomy", "Botany", "Zoology"],
                        "difficulty_levels": ["foundation", "intermediate", "advanced", "expert"],
                        "estimated_hours": 120
                    },
                    "chemistry": {
                        "name": "Chemistry", 
                        "subtopics": ["Organic Chemistry", "Inorganic Chemistry", "Physical Chemistry", "Biochemistry"],
                        "difficulty_levels": ["foundation", "intermediate", "advanced", "expert"],
                        "estimated_hours": 100
                    },
                    "physics": {
                        "name": "Physics",
                        "subtopics": ["Mechanics", "Thermodynamics", "Electromagnetism", "Quantum Physics"],
                        "difficulty_levels": ["foundation", "intermediate", "advanced", "expert"],
                        "estimated_hours": 150
                    },
                    "computer_science": {
                        "name": "Computer Science",
                        "subtopics": ["Programming", "Data Structures", "Algorithms", "Machine Learning", "Web Development"],
                        "difficulty_levels": ["foundation", "intermediate", "advanced", "expert"],
                        "estimated_hours": 200
                    }
                }
            },
            "mathematics": {
                "name": "Mathematics",
                "icon": "grid", 
                "color": "#e74c3c",
                "topics": {
                    "algebra": {
                        "name": "Algebra",
                        "subtopics": ["Linear Algebra", "Abstract Algebra", "Boolean Algebra"],
                        "difficulty_levels": ["foundation", "intermediate", "advanced", "expert"],
                        "estimated_hours": 80
                    },
                    "calculus": {
                        "name": "Calculus",
                        "subtopics": ["Differential Calculus", "Integral Calculus", "Multivariable Calculus"],
                        "difficulty_levels": ["foundation", "intermediate", "advanced", "expert"],
                        "estimated_hours": 120
                    },
                    "statistics": {
                        "name": "Statistics",
                        "subtopics": ["Descriptive Statistics", "Inferential Statistics", "Probability Theory"],
                        "difficulty_levels": ["foundation", "intermediate", "advanced", "expert"],
                        "estimated_hours": 90
                    }
                }
            },
            "business": {
                "name": "Business & Finance",
                "icon": "trending-up",
                "color": "#27ae60",
                "topics": {
                    "finance": {
                        "name": "Finance",
                        "subtopics": ["Personal Finance", "Corporate Finance", "Investment Analysis", "Risk Management"],
                        "difficulty_levels": ["foundation", "intermediate", "advanced", "expert"],
                        "estimated_hours": 100
                    },
                    "marketing": {
                        "name": "Marketing",
                        "subtopics": ["Digital Marketing", "Brand Management", "Market Research", "Consumer Psychology"],
                        "difficulty_levels": ["foundation", "intermediate", "advanced", "expert"],
                        "estimated_hours": 80
                    },
                    "management": {
                        "name": "Management",
                        "subtopics": ["Project Management", "Leadership", "Operations", "Strategic Planning"],
                        "difficulty_levels": ["foundation", "intermediate", "advanced", "expert"],
                        "estimated_hours": 90
                    }
                }
            },
            "engineering": {
                "name": "Engineering",
                "icon": "settings",
                "color": "#f39c12",
                "topics": {
                    "electrical": {
                        "name": "Electrical Engineering",
                        "subtopics": ["Circuit Analysis", "Power Systems", "Electronics", "Signal Processing"],
                        "difficulty_levels": ["foundation", "intermediate", "advanced", "expert"],
                        "estimated_hours": 150
                    },
                    "mechanical": {
                        "name": "Mechanical Engineering", 
                        "subtopics": ["Thermodynamics", "Fluid Mechanics", "Materials Science", "Machine Design"],
                        "difficulty_levels": ["foundation", "intermediate", "advanced", "expert"],
                        "estimated_hours": 140
                    },
                    "civil": {
                        "name": "Civil Engineering",
                        "subtopics": ["Structural Engineering", "Geotechnical Engineering", "Transportation", "Environmental"],
                        "difficulty_levels": ["foundation", "intermediate", "advanced", "expert"],
                        "estimated_hours": 130
                    }
                }
            },
            "languages": {
                "name": "Languages",
                "icon": "globe",
                "color": "#9b59b6",
                "topics": {
                    "spanish": {
                        "name": "Spanish",
                        "subtopics": ["Basic Conversation", "Grammar", "Business Spanish", "Literature"],
                        "difficulty_levels": ["beginner", "intermediate", "advanced", "fluent"],
                        "estimated_hours": 200
                    },
                    "french": {
                        "name": "French",
                        "subtopics": ["Basic Conversation", "Grammar", "Business French", "Literature"],
                        "difficulty_levels": ["beginner", "intermediate", "advanced", "fluent"],
                        "estimated_hours": 200
                    },
                    "programming_languages": {
                        "name": "Programming Languages",
                        "subtopics": ["Python", "JavaScript", "Java", "C++", "Rust"],
                        "difficulty_levels": ["beginner", "intermediate", "advanced", "expert"],
                        "estimated_hours": 300
                    }
                }
            },
            "trades": {
                "name": "Skilled Trades",
                "icon": "tool",
                "color": "#34495e",
                "topics": {
                    "electrical_trade": {
                        "name": "Electrical Work",
                        "subtopics": ["Residential Wiring", "Commercial Systems", "Safety Codes", "Motor Controls"],
                        "difficulty_levels": ["apprentice", "journeyman", "advanced", "master"],
                        "estimated_hours": 180
                    },
                    "plumbing": {
                        "name": "Plumbing",
                        "subtopics": ["Pipe Installation", "Fixture Repair", "Drainage Systems", "Gas Lines"],
                        "difficulty_levels": ["apprentice", "journeyman", "advanced", "master"],
                        "estimated_hours": 160
                    },
                    "automotive": {
                        "name": "Automotive Repair",
                        "subtopics": ["Engine Diagnostics", "Electrical Systems", "Brake Systems", "Transmission"],
                        "difficulty_levels": ["apprentice", "journeyman", "advanced", "master"],
                        "estimated_hours": 200
                    }
                }
            }
        }
    
    def get_all_subjects(self):
        """Return all available subjects"""
        return self.subjects
    
    def get_subject_by_category(self, category):
        """Get specific subject category"""
        return self.subjects.get(category, {})
    
    def get_topic_details(self, category, topic):
        """Get details for a specific topic"""
        subject = self.get_subject_by_category(category)
        return subject.get('topics', {}).get(topic, {})
    
    def add_custom_subject(self, category, topic_data):
        """Allow users to add custom subjects"""
        if category not in self.subjects:
            self.subjects[category] = {
                "name": category.title(),
                "icon": "book",
                "color": "#95a5a6",
                "topics": {}
            }
        
        self.subjects[category]['topics'].update(topic_data)
        self.save_subjects()
    
    def get_user_progress(self, user_id, category, topic):
        """Get user progress for a specific topic"""
        user_key = f"{user_id}_{category}_{topic}"
        return self.user_progress.get(user_key, {
            "level": "foundation",
            "completed_subtopics": [],
            "badges_earned": [],
            "total_questions_answered": 0,
            "correct_answers": 0,
            "learning_streak": 0,
            "last_session": None,
            "time_invested_minutes": 0
        })
    
    def update_user_progress(self, user_id, category, topic, session_data):
        """Update user progress after a learning session"""
        user_key = f"{user_id}_{category}_{topic}"
        progress = self.get_user_progress(user_id, category, topic)
        
        # Update session data
        progress['total_questions_answered'] += session_data.get('questions_answered', 0)
        progress['correct_answers'] += session_data.get('correct_answers', 0)
        progress['time_invested_minutes'] += session_data.get('session_time_minutes', 0)
        progress['last_session'] = datetime.now().isoformat()
        
        # Calculate accuracy
        accuracy = progress['correct_answers'] / max(progress['total_questions_answered'], 1)
        
        # Update learning streak
        if session_data.get('session_completed', False):
            progress['learning_streak'] += 1
        
        # Check for level progression
        progress = self.check_level_progression(progress, accuracy)
        
        # Check for new badges
        progress = self.check_badge_eligibility(progress, category, topic)
        
        self.user_progress[user_key] = progress
        self.save_user_progress()
        
        return progress
    
    def check_level_progression(self, progress, accuracy):
        """Check if user should progress to next difficulty level"""
        levels = ["foundation", "intermediate", "advanced", "expert"]
        current_level = progress['level']
        
        if current_level in levels:
            current_index = levels.index(current_level)
            
            # Progression criteria: 80%+ accuracy and 50+ questions
            if (accuracy >= 0.8 and 
                progress['total_questions_answered'] >= 50 and 
                current_index < len(levels) - 1):
                progress['level'] = levels[current_index + 1]
        
        return progress
    
    def check_badge_eligibility(self, progress, category, topic):
        """Check and award badges based on achievements"""
        new_badges = []
        
        # Accuracy badges
        accuracy = progress['correct_answers'] / max(progress['total_questions_answered'], 1)
        if accuracy >= 0.95 and 'perfectionist' not in progress['badges_earned']:
            new_badges.append('perfectionist')
        elif accuracy >= 0.85 and 'expert' not in progress['badges_earned']:
            new_badges.append('expert')
        elif accuracy >= 0.75 and 'proficient' not in progress['badges_earned']:
            new_badges.append('proficient')
        
        # Streak badges
        if progress['learning_streak'] >= 30 and 'dedicated_learner' not in progress['badges_earned']:
            new_badges.append('dedicated_learner')
        elif progress['learning_streak'] >= 7 and 'weekly_warrior' not in progress['badges_earned']:
            new_badges.append('weekly_warrior')
        
        # Time investment badges
        if progress['time_invested_minutes'] >= 1200 and 'time_master' not in progress['badges_earned']:  # 20 hours
            new_badges.append('time_master')
        elif progress['time_invested_minutes'] >= 300 and 'committed' not in progress['badges_earned']:  # 5 hours
            new_badges.append('committed')
        
        # Question volume badges
        if progress['total_questions_answered'] >= 1000 and 'quiz_master' not in progress['badges_earned']:
            new_badges.append('quiz_master')
        elif progress['total_questions_answered'] >= 500 and 'knowledge_seeker' not in progress['badges_earned']:
            new_badges.append('knowledge_seeker')
        
        progress['badges_earned'].extend(new_badges)
        return progress
    
    def get_leaderboard(self, category, topic, metric='accuracy'):
        """Generate leaderboard for a specific topic"""
        topic_users = []
        
        for user_key, progress in self.user_progress.items():
            if f"_{category}_{topic}" in user_key:
                user_id = user_key.split('_')[0]
                
                if metric == 'accuracy':
                    score = progress['correct_answers'] / max(progress['total_questions_answered'], 1)
                elif metric == 'streak':
                    score = progress['learning_streak']
                elif metric == 'time':
                    score = progress['time_invested_minutes']
                elif metric == 'questions':
                    score = progress['total_questions_answered']
                else:
                    score = 0
                
                topic_users.append({
                    'user_id': user_id,
                    'score': score,
                    'level': progress['level'],
                    'badges': len(progress['badges_earned'])
                })
        
        return sorted(topic_users, key=lambda x: x['score'], reverse=True)[:10]
    
    def generate_learning_path(self, category, topic, user_level):
        """Generate adaptive learning path based on user level"""
        topic_details = self.get_topic_details(category, topic)
        if not topic_details:
            return []
        
        subtopics = topic_details.get('subtopics', [])
        difficulty_levels = topic_details.get('difficulty_levels', ['foundation', 'intermediate', 'advanced'])
        
        # Create progressive learning path
        learning_path = []
        for i, subtopic in enumerate(subtopics):
            # Determine appropriate difficulty for this subtopic
            if user_level == 'foundation':
                difficulty = difficulty_levels[0] if difficulty_levels else 'foundation'
            elif user_level == 'intermediate':
                difficulty = difficulty_levels[min(1, len(difficulty_levels)-1)] if difficulty_levels else 'intermediate'
            else:
                difficulty = difficulty_levels[-1] if difficulty_levels else 'advanced'
            
            learning_path.append({
                'subtopic': subtopic,
                'difficulty': difficulty,
                'estimated_sessions': 3 + i,  # Progressive complexity
                'prerequisite': subtopics[i-1] if i > 0 else None
            })
        
        return learning_path

# Initialize global subject manager
subject_manager = SubjectManager()