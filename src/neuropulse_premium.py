"""
NeuroPulse Premium - Comprehensive AI Learning Platform
Enterprise-grade adaptive learning system with full feature suite
"""

import os
import json
import uuid
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum

from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Initialize OpenAI client
try:
    from openai import OpenAI
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    ai_enabled = True
    logging.info("OpenAI integration enabled")
except Exception as e:
    openai_client = None
    ai_enabled = False
    logging.warning(f"OpenAI not available: {e}")

# Import advanced learning systems
try:
    from spaced_repetition_system import spaced_repetition_engine
    from voice_navigation_system import voice_navigation_system
    from leaderboard_system import leaderboard_engine
    from analytics_dashboard import analytics_dashboard
    from adaptive_difficulty_engine import adaptive_difficulty_engine
    from learning_journey_map import learning_journey_engine
    advanced_features_enabled = True
    logging.info("Advanced learning systems enabled")
except ImportError as e:
    advanced_features_enabled = False
    logging.warning(f"Advanced features not available: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
class Base(DeclarativeBase):
    pass

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///neuropulse.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Enums for structured data
class DifficultyLevel(Enum):
    FOUNDATION = "foundation"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class LearningStyle(Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING = "reading"
    ADAPTIVE = "adaptive"

class BadgeType(Enum):
    STREAK = "streak"
    MASTERY = "mastery"
    DEDICATION = "dedication"
    EXPLORER = "explorer"
    PERFECTIONIST = "perfectionist"
    SPECIALIST = "specialist"

# Enhanced Database Models
class User(db.Model):
    __tablename__ = 'users'
    
    # Core identification
    id = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    
    # Learning preferences
    learning_style = db.Column(db.Enum(LearningStyle), default=LearningStyle.ADAPTIVE)
    attention_span = db.Column(db.Integer, default=8)  # minutes
    preferred_difficulty = db.Column(db.Enum(DifficultyLevel), default=DifficultyLevel.INTERMEDIATE)
    
    # Progress tracking
    total_sessions = db.Column(db.Integer, default=0)
    total_correct_answers = db.Column(db.Integer, default=0)
    total_questions_answered = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    total_study_time = db.Column(db.Integer, default=0)  # minutes
    
    # User data
    learning_profile = db.Column(db.Text, default='{}')
    preferences = db.Column(db.Text, default='{}')
    progress_data = db.Column(db.Text, default='{}')
    achievements = db.Column(db.Text, default='[]')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    last_session_date = db.Column(db.Date, nullable=True)
    
    # Relationships
    sessions = db.relationship('LearningSession', backref='user', lazy=True)
    subject_progress = db.relationship('SubjectProgress', backref='user', lazy=True)
    badges = db.relationship('UserBadge', backref='user', lazy=True)
    
    def accuracy_percentage(self):
        if self.total_questions_answered == 0:
            return 0.0
        return (self.total_correct_answers / self.total_questions_answered) * 100
    
    def get_learning_profile(self):
        try:
            return json.loads(self.learning_profile or '{}')
        except:
            return {}
    
    def update_learning_profile(self, data):
        """Update user's learning profile"""
        try:
            self.learning_profile = json.dumps(data)
            db.session.commit()
        except Exception as e:
            logger.error(f"Failed to update learning profile: {e}")
            db.session.rollback()
    
    def get_achievements(self):
        try:
            return json.loads(self.achievements or '[]')
        except:
            return []
    
    def add_achievement(self, achievement_data):
        """Add new achievement to user"""
        achievements = self.get_achievements()
        achievements.append({
            'id': str(uuid.uuid4()),
            'type': achievement_data['type'],
            'title': achievement_data['title'],
            'description': achievement_data['description'],
            'earned_at': datetime.now().isoformat(),
            'subject': achievement_data.get('subject'),
            'value': achievement_data.get('value')
        })
        self.achievements = json.dumps(achievements)
    
    def get_level_for_subject(self, subject):
        """Get user's current level for a specific subject"""
        progress = self.get_subject_progress(subject)
        return progress.get('level', 1)
    
    def get_subject_progress(self, subject):
        """Get detailed progress for a subject"""
        progress_data = json.loads(self.progress_data or '{}')
        return progress_data.get(subject, {
            'level': 1,
            'xp': 0,
            'sessions_completed': 0,
            'accuracy': 0.0,
            'time_spent': 0,
            'topics_mastered': [],
            'difficulty_unlocked': DifficultyLevel.FOUNDATION.value
        })

class Subject(db.Model):
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50), default='General')
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(20), default='📚')
    
    # Learning structure
    topics = db.Column(db.Text, default='[]')  # JSON list of topics
    difficulty_levels = db.Column(db.Text, default='[]')  # Available difficulty levels
    prerequisites = db.Column(db.Text, default='[]')  # Required subjects/levels
    
    # Statistics
    total_sessions = db.Column(db.Integer, default=0)
    avg_completion_rate = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sessions = db.relationship('LearningSession', backref='subject', lazy=True)
    progress_records = db.relationship('SubjectProgress', backref='subject', lazy=True)
    
    def get_topics(self):
        try:
            return json.loads(self.topics or '[]')
        except:
            return []
    
    def get_difficulty_levels(self):
        try:
            return json.loads(self.difficulty_levels or '[]')
        except:
            return [level.value for level in DifficultyLevel]

class LearningSession(db.Model):
    __tablename__ = 'learning_sessions'
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True)
    
    # Session configuration
    subject_name = db.Column(db.String(100), nullable=False)
    topic = db.Column(db.String(200), nullable=True)
    difficulty_level = db.Column(db.Enum(DifficultyLevel), default=DifficultyLevel.INTERMEDIATE)
    session_type = db.Column(db.String(50), default='practice')  # practice, assessment, review
    
    # Progress tracking
    current_question_index = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=10)
    correct_answers = db.Column(db.Integer, default=0)
    confidence_scores = db.Column(db.Text, default='[]')
    
    # Session data
    session_data = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='active')
    
    # Timing
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    time_spent = db.Column(db.Integer, default=0)  # seconds
    
    def accuracy_percentage(self):
        if self.current_question_index == 0:
            return 0.0
        return (self.correct_answers / self.current_question_index) * 100
    
    def get_session_data(self):
        try:
            return json.loads(self.session_data or '{}')
        except:
            return {}

class SubjectProgress(db.Model):
    __tablename__ = 'subject_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    
    # Progress metrics
    level = db.Column(db.Integer, default=1)
    xp = db.Column(db.Integer, default=0)
    sessions_completed = db.Column(db.Integer, default=0)
    total_time_spent = db.Column(db.Integer, default=0)  # minutes
    
    # Performance metrics
    accuracy = db.Column(db.Float, default=0.0)
    consistency_score = db.Column(db.Float, default=0.0)
    improvement_rate = db.Column(db.Float, default=0.0)
    
    # Learning data
    topics_mastered = db.Column(db.Text, default='[]')
    current_difficulty = db.Column(db.Enum(DifficultyLevel), default=DifficultyLevel.FOUNDATION)
    strengths = db.Column(db.Text, default='[]')
    areas_for_improvement = db.Column(db.Text, default='[]')
    
    # Timestamps
    first_session = db.Column(db.DateTime, default=datetime.utcnow)
    last_session = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_topics_mastered(self):
        try:
            return json.loads(self.topics_mastered or '[]')
        except:
            return []

class UserBadge(db.Model):
    __tablename__ = 'user_badges'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    
    # Badge details
    badge_type = db.Column(db.Enum(BadgeType), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(20), default='🏆')
    
    # Context
    subject_name = db.Column(db.String(100), nullable=True)
    achievement_value = db.Column(db.Integer, nullable=True)  # streak length, accuracy %, etc.
    
    # Timestamps
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

# Enhanced AI Content Generator
class PremiumContentGenerator:
    def __init__(self, openai_client=None):
        self.client = openai_client
        self.enabled = openai_client is not None
        
    def generate_adaptive_questions(self, subject: str, topic: str = None, 
                                  difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE,
                                  question_count: int = 10, user_level: int = 1) -> Dict[str, Any]:
        """Generate adaptive questions tailored to user level and subject"""
        
        if not self.enabled:
            return self._generate_fallback_questions(subject, difficulty, question_count)
        
        try:
            # Enhanced prompt for comprehensive learning
            system_prompt = f"""You are an expert educator creating adaptive learning content for neurodivergent learners.

Subject: {subject}
Topic: {topic or 'General concepts'}
Difficulty: {difficulty.value}
User Level: {user_level}
Question Count: {question_count}

Create {question_count} questions that:
1. Build progressively in complexity
2. Include real-world applications
3. Use clear, ADHD-friendly language
4. Provide detailed explanations
5. Include confidence-boosting elements

For each question, provide:
- Multiple choice options (4 choices)
- Detailed explanation of the correct answer
- Why wrong answers are incorrect
- Real-world application or example
- Difficulty rating (1-5)
- Learning objective addressed

Return as JSON with this structure:
{{
    "subject": "{subject}",
    "difficulty": "{difficulty.value}",
    "estimated_time": "8-12 minutes",
    "learning_objectives": ["objective1", "objective2"],
    "questions": [
        {{
            "id": 1,
            "question": "Clear, engaging question text",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "explanation": "Detailed explanation why A is correct",
            "wrong_explanations": {{"B": "Why B is wrong", "C": "Why C is wrong", "D": "Why D is wrong"}},
            "real_world_example": "Practical application",
            "difficulty_rating": 3,
            "learning_objective": "What this question teaches"
        }}
    ]
}}"""

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Generate adaptive learning content for {subject}"}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            content = json.loads(response.choices[0].message.content)
            
            # Add metadata
            content['generated_at'] = datetime.now().isoformat()
            content['ai_generated'] = True
            content['user_level'] = user_level
            
            return content
            
        except Exception as e:
            logger.error(f"AI content generation failed: {e}")
            return self._generate_fallback_questions(subject, difficulty, question_count)
    
    def _generate_fallback_questions(self, subject: str, difficulty: DifficultyLevel, count: int) -> Dict[str, Any]:
        """High-quality fallback questions when AI is unavailable"""
        
        base_questions = {
            "electrical engineering": [
                {
                    "question": "What is Ohm's Law?",
                    "options": ["V = I × R", "P = V × I", "Q = C × V", "F = m × a"],
                    "correct_answer": "V = I × R",
                    "explanation": "Ohm's Law states that voltage equals current times resistance (V = I × R). This fundamental relationship helps calculate electrical values in circuits.",
                    "real_world_example": "Used to calculate voltage drop across resistors in LED circuits",
                    "difficulty_rating": 2
                },
                {
                    "question": "What safety measure is most important when working with electrical circuits?",
                    "options": ["Turn off power at breaker", "Wear gloves", "Use insulated tools", "All of the above"],
                    "correct_answer": "All of the above",
                    "explanation": "Electrical safety requires multiple precautions: turning off power, using proper PPE, and using insulated tools.",
                    "real_world_example": "Professional electricians follow all these safety protocols",
                    "difficulty_rating": 1
                }
            ],
            "python programming": [
                {
                    "question": "Which Python data type is ordered and changeable?",
                    "options": ["List", "Set", "Dictionary", "Tuple"],
                    "correct_answer": "List",
                    "explanation": "Lists in Python are ordered (maintain insertion order) and mutable (changeable after creation).",
                    "real_world_example": "Shopping lists, to-do items, user records",
                    "difficulty_rating": 2
                },
                {
                    "question": "What does the 'len()' function return?",
                    "options": ["Length of object", "Last element", "Type of object", "Memory size"],
                    "correct_answer": "Length of object",
                    "explanation": "The len() function returns the number of items in an object like a string, list, or dictionary.",
                    "real_world_example": "Counting characters in user input validation",
                    "difficulty_rating": 1
                }
            ]
        }
        
        # Get subject-specific questions or create generic ones
        subject_lower = subject.lower()
        questions = []
        
        if any(key in subject_lower for key in base_questions.keys()):
            for key in base_questions.keys():
                if key in subject_lower:
                    questions = base_questions[key][:count]
                    break
        else:
            # Generate generic questions for any subject
            questions = [
                {
                    "question": f"What is a fundamental concept in {subject}?",
                    "options": ["Foundation principle", "Advanced technique", "Specialized tool", "Recent innovation"],
                    "correct_answer": "Foundation principle",
                    "explanation": f"Understanding fundamental concepts is crucial for building knowledge in {subject}.",
                    "real_world_example": f"Foundation concepts in {subject} apply to many practical situations",
                    "difficulty_rating": 2
                }
            ]
        
        return {
            "subject": subject,
            "difficulty": difficulty.value,
            "estimated_time": f"{count * 1.2:.0f} minutes",
            "learning_objectives": [f"Understand core concepts in {subject}"],
            "questions": questions,
            "generated_at": datetime.now().isoformat(),
            "ai_generated": False
        }

# Gamification and Achievement System
class AchievementEngine:
    """Handles badges, streaks, and gamification elements"""
    
    @staticmethod
    def check_and_award_badges(user: User, session_data: Dict) -> List[Dict]:
        """Check for new badge achievements and award them"""
        new_badges = []
        
        # Streak badges
        if user.current_streak == 7:
            badge = {
                'type': BadgeType.STREAK.value,
                'title': 'Week Warrior',
                'description': 'Completed 7 days in a row',
                'icon': '🔥'
            }
            user.add_achievement(badge)
            new_badges.append(badge)
        
        elif user.current_streak == 30:
            badge = {
                'type': BadgeType.STREAK.value,
                'title': 'Monthly Master',
                'description': 'Completed 30 days in a row',
                'icon': '🏆'
            }
            user.add_achievement(badge)
            new_badges.append(badge)
        
        # Accuracy badges
        session_accuracy = session_data.get('accuracy', 0)
        if session_accuracy >= 95:
            badge = {
                'type': BadgeType.PERFECTIONIST.value,
                'title': 'Perfectionist',
                'description': 'Achieved 95%+ accuracy in a session',
                'icon': '💎',
                'subject': session_data.get('subject')
            }
            user.add_achievement(badge)
            new_badges.append(badge)
        
        # Session count badges
        if user.total_sessions == 10:
            badge = {
                'type': BadgeType.DEDICATION.value,
                'title': 'Getting Started',
                'description': 'Completed 10 learning sessions',
                'icon': '🌱'
            }
            user.add_achievement(badge)
            new_badges.append(badge)
        
        elif user.total_sessions == 100:
            badge = {
                'type': BadgeType.DEDICATION.value,
                'title': 'Centurion',
                'description': 'Completed 100 learning sessions',
                'icon': '👑'
            }
            user.add_achievement(badge)
            new_badges.append(badge)
        
        return new_badges

# Enhanced User Management
def get_or_create_user():
    """Enhanced user management with comprehensive fallback"""
    try:
        user_id = session.get('user_id')
        username = session.get('username', 'Learner')
        
        if not user_id:
            user_id = f"user_{uuid.uuid4().hex[:8]}"
            username = f"Learner {user_id[-4:]}"
            session['user_id'] = user_id
            session['username'] = username
        
        # Session-based user class for fallback
        class SessionUser:
            def __init__(self):
                self.id = user_id
                self.username = username
                self.email = None
                self.learning_style = LearningStyle.ADAPTIVE
                self.attention_span = 8
                self.preferred_difficulty = DifficultyLevel.INTERMEDIATE
                self.learning_profile = '{}'
                self.preferences = '{}'
                self.progress_data = '{}'
                self.achievements = '[]'
                self.created_at = datetime.utcnow()
                self.last_active = datetime.utcnow()
                self.last_session_date = None
                
                # Load from session
                self.total_sessions = session.get('total_sessions', 0)
                self.total_correct_answers = session.get('total_correct_answers', 0)
                self.total_questions_answered = session.get('total_questions_answered', 0)
                self.current_streak = session.get('current_streak', 0)
                self.longest_streak = session.get('longest_streak', 0)
                self.total_study_time = session.get('total_study_time', 0)
            
            def accuracy_percentage(self):
                if self.total_questions_answered == 0:
                    return 0.0
                return (self.total_correct_answers / self.total_questions_answered) * 100
            
            def get_learning_profile(self):
                return session.get('learning_profile', {'onboarding_complete': False})
            
            def update_learning_profile(self, data):
                session['learning_profile'] = data
                self.learning_profile = json.dumps(data)
            
            def get_achievements(self):
                return session.get('achievements', [])
            
            def add_achievement(self, achievement_data):
                achievements = self.get_achievements()
                achievements.append(achievement_data)
                session['achievements'] = achievements
            
            def get_subject_progress(self, subject):
                progress_data = session.get('progress_data', {})
                return progress_data.get(subject, {
                    'level': 1,
                    'xp': 0,
                    'sessions_completed': 0,
                    'accuracy': 0.0,
                    'time_spent': 0,
                    'topics_mastered': [],
                    'difficulty_unlocked': DifficultyLevel.FOUNDATION.value
                })
        
        # Try database first
        try:
            user = User.query.filter_by(id=user_id).first()
            if user:
                user.last_active = datetime.utcnow()
                db.session.commit()
                return user
        except Exception as e:
            logger.warning(f"Database query failed: {e}")
        
        # Try to create database user
        try:
            user = User()
            user.id = user_id
            user.username = username
            user.learning_profile = json.dumps({
                'onboarding_complete': False,
                'learning_style': LearningStyle.ADAPTIVE.value,
                'preferred_session_length': 8
            })
            
            db.session.add(user)
            db.session.commit()
            logger.info(f"Created database user: {user_id}")
            return user
            
        except Exception as e:
            logger.warning(f"Database user creation failed: {e}")
            db.session.rollback()
        
        # Return session-based user
        return SessionUser()
        
    except Exception as e:
        logger.error(f"User management error: {e}")
        # Emergency fallback
        class EmergencyUser:
            def __init__(self):
                self.id = f"emergency_{uuid.uuid4().hex[:8]}"
                self.username = "Guest Learner"
                self.total_sessions = 0
                self.total_correct_answers = 0
                self.total_questions_answered = 0
                self.current_streak = 0
                self.longest_streak = 0
                self.total_study_time = 0
                
            def accuracy_percentage(self):
                return 0.0
                
            def get_learning_profile(self):
                return {'onboarding_complete': False}
                
            def update_learning_profile(self, data):
                pass
                
            def get_achievements(self):
                return []
                
            def add_achievement(self, achievement_data):
                pass
                
            def get_subject_progress(self, subject):
                return {
                    'level': 1,
                    'xp': 0,
                    'sessions_completed': 0,
                    'accuracy': 0.0,
                    'time_spent': 0,
                    'topics_mastered': [],
                    'difficulty_unlocked': DifficultyLevel.FOUNDATION.value
                }
        
        return EmergencyUser()

# Initialize systems
content_generator = PremiumContentGenerator(openai_client)

# Initialize database
with app.app_context():
    try:
        db.create_all()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization warning: {e}")

# Routes
@app.route('/')
def index():
    """Premium learning dashboard"""
    user = get_or_create_user()
    
    # Check if user needs onboarding
    profile = user.get_learning_profile()
    if not profile.get('onboarding_complete', False):
        return redirect(url_for('onboarding'))
    
    # Get user statistics and recent achievements
    recent_achievements = user.get_achievements()[-3:] if hasattr(user, 'get_achievements') else []
    
    return render_template('premium_dashboard.html', 
                         user=user, 
                         recent_achievements=recent_achievements,
                         ai_enabled=ai_enabled)

@app.route('/onboarding')
def onboarding():
    """Comprehensive onboarding experience"""
    user = get_or_create_user()
    return render_template('premium_onboarding.html', user=user)

@app.route('/complete-onboarding', methods=['POST'])
def complete_onboarding():
    """Process onboarding completion"""
    user = get_or_create_user()
    
    learning_style = request.form.get('learning_style', LearningStyle.ADAPTIVE.value)
    session_length = int(request.form.get('session_length', 8))
    interests = request.form.getlist('interests')
    goals = request.form.get('goals', '')
    
    profile = {
        'onboarding_complete': True,
        'learning_style': learning_style,
        'preferred_session_length': session_length,
        'interests': interests,
        'goals': goals,
        'completed_at': datetime.now().isoformat()
    }
    
    user.update_learning_profile(profile)
    flash('Welcome to NeuroPulse! Your learning journey begins now.', 'success')
    return redirect(url_for('index'))

@app.route('/explore')
def explore_subjects():
    """Subject exploration and discovery"""
    user = get_or_create_user()
    
    # Popular subjects with progress tracking
    popular_subjects = [
        {
            'name': 'Python Programming',
            'category': 'Technology',
            'icon': '🐍',
            'description': 'Master programming fundamentals with hands-on projects',
            'difficulty_levels': ['Foundation', 'Beginner', 'Intermediate', 'Advanced'],
            'estimated_time': '2-6 weeks',
            'user_progress': user.get_subject_progress('Python Programming') if hasattr(user, 'get_subject_progress') else {}
        },
        {
            'name': 'Electrical Engineering',
            'category': 'Engineering',
            'icon': '⚡',
            'description': 'From basic circuits to advanced electrical systems',
            'difficulty_levels': ['Foundation', 'Beginner', 'Intermediate', 'Advanced'],
            'estimated_time': '3-8 weeks',
            'user_progress': user.get_subject_progress('Electrical Engineering') if hasattr(user, 'get_subject_progress') else {}
        },
        {
            'name': 'Financial Planning',
            'category': 'Finance',
            'icon': '💰',
            'description': 'Personal finance, budgeting, and investment strategies',
            'difficulty_levels': ['Foundation', 'Beginner', 'Intermediate'],
            'estimated_time': '2-4 weeks',
            'user_progress': user.get_subject_progress('Financial Planning') if hasattr(user, 'get_subject_progress') else {}
        },
        {
            'name': 'Botany',
            'category': 'Science',
            'icon': '🌱',
            'description': 'Plant biology, ecology, and botanical sciences',
            'difficulty_levels': ['Foundation', 'Beginner', 'Intermediate', 'Advanced'],
            'estimated_time': '4-10 weeks',
            'user_progress': user.get_subject_progress('Botany') if hasattr(user, 'get_subject_progress') else {}
        },
        {
            'name': 'Data Analysis',
            'category': 'Technology',
            'icon': '📊',
            'description': 'Excel, statistics, and data visualization techniques',
            'difficulty_levels': ['Foundation', 'Beginner', 'Intermediate', 'Advanced'],
            'estimated_time': '3-7 weeks',
            'user_progress': user.get_subject_progress('Data Analysis') if hasattr(user, 'get_subject_progress') else {}
        },
        {
            'name': 'Digital Marketing',
            'category': 'Business',
            'icon': '📱',
            'description': 'SEO, social media, and online marketing strategies',
            'difficulty_levels': ['Foundation', 'Beginner', 'Intermediate'],
            'estimated_time': '2-5 weeks',
            'user_progress': user.get_subject_progress('Digital Marketing') if hasattr(user, 'get_subject_progress') else {}
        }
    ]
    
    return render_template('subject_explorer.html', 
                         user=user, 
                         subjects=popular_subjects)

@app.route('/start-learning', methods=['POST'])
def start_learning():
    """Begin adaptive learning session"""
    user = get_or_create_user()
    
    # Get learning parameters
    subject = request.form.get('subject', '').strip()
    topic = request.form.get('topic', '').strip()
    difficulty = request.form.get('difficulty', DifficultyLevel.INTERMEDIATE.value)
    question_count = int(request.form.get('question_count', 10))
    
    if not subject:
        return jsonify({'error': 'Please specify a subject to learn'}), 400
    
    # Get user's level for this subject
    user_level = 1
    if hasattr(user, 'get_subject_progress'):
        progress = user.get_subject_progress(subject)
        user_level = progress.get('level', 1)
    
    # Generate adaptive content
    try:
        difficulty_enum = DifficultyLevel(difficulty)
    except ValueError:
        difficulty_enum = DifficultyLevel.INTERMEDIATE
    
    content = content_generator.generate_adaptive_questions(
        subject=subject,
        topic=topic,
        difficulty=difficulty_enum,
        question_count=question_count,
        user_level=user_level
    )
    
    # Create learning session
    session_id = str(uuid.uuid4())
    session_data = {
        'session_id': session_id,
        'user_id': user.id,
        'subject': subject,
        'topic': topic,
        'difficulty': difficulty,
        'questions': content.get('questions', []),
        'current_question': 0,
        'correct_answers': 0,
        'confidence_ratings': [],
        'started_at': datetime.now().isoformat(),
        'learning_objectives': content.get('learning_objectives', []),
        'estimated_time': content.get('estimated_time', '10 minutes')
    }
    
    # Store session
    session['current_learning_session'] = session_data
    
    return redirect(url_for('learning_session'))

@app.route('/learn')
def learning_session():
    """Interactive learning session with premium features"""
    user = get_or_create_user()
    learning_session = session.get('current_learning_session')
    
    if not learning_session:
        return redirect(url_for('explore_subjects'))
    
    # Calculate progress
    current_q = learning_session['current_question']
    total_q = len(learning_session['questions'])
    progress_percent = (current_q / total_q * 100) if total_q > 0 else 0
    
    return render_template('premium_learning.html',
                         user=user,
                         session_data=learning_session,
                         progress_percent=progress_percent)

@app.route('/submit-answer', methods=['POST'])
def submit_answer():
    """Process answer with comprehensive tracking"""
    user = get_or_create_user()
    learning_session = session.get('current_learning_session')
    
    if not learning_session:
        return jsonify({'error': 'No active session'}), 400
    
    # Get answer data
    data = request.get_json()
    answer = data.get('answer')
    confidence = data.get('confidence', 3)
    time_taken = data.get('time_taken', 0)
    
    question_index = learning_session['current_question']
    
    if question_index >= len(learning_session['questions']):
        return jsonify({'error': 'Session already complete'}), 400
    
    # Get current question
    current_q = learning_session['questions'][question_index]
    is_correct = answer == current_q['correct_answer']
    
    # Update session data
    if is_correct:
        learning_session['correct_answers'] += 1
    
    learning_session['confidence_ratings'].append({
        'question': question_index,
        'confidence': confidence,
        'correct': is_correct,
        'time_taken': time_taken
    })
    
    learning_session['current_question'] += 1
    
    # Update session
    session['current_learning_session'] = learning_session
    
    # Check if session complete
    is_complete = learning_session['current_question'] >= len(learning_session['questions'])
    
    response = {
        'is_correct': is_correct,
        'correct_answer': current_q['correct_answer'],
        'explanation': current_q.get('explanation', ''),
        'wrong_explanations': current_q.get('wrong_explanations', {}),
        'real_world_example': current_q.get('real_world_example', ''),
        'is_complete': is_complete,
        'score': learning_session['correct_answers'],
        'total': len(learning_session['questions']),
        'progress_percent': (learning_session['current_question'] / len(learning_session['questions']) * 100)
    }
    
    if is_complete:
        # Calculate final statistics
        accuracy = (learning_session['correct_answers'] / len(learning_session['questions'])) * 100
        avg_confidence = sum(r['confidence'] for r in learning_session['confidence_ratings']) / len(learning_session['confidence_ratings'])
        
        # Update user statistics
        user.total_sessions += 1
        user.total_correct_answers += learning_session['correct_answers']
        user.total_questions_answered += len(learning_session['questions'])
        
        # Update session storage
        if hasattr(session, 'get'):
            session['total_sessions'] = user.total_sessions
            session['total_correct_answers'] = user.total_correct_answers
            session['total_questions_answered'] = user.total_questions_answered
        
        # Check for achievements
        session_summary = {
            'subject': learning_session['subject'],
            'accuracy': accuracy,
            'questions_answered': len(learning_session['questions']),
            'avg_confidence': avg_confidence
        }
        
        new_badges = AchievementEngine.check_and_award_badges(user, session_summary)
        
        response.update({
            'final_accuracy': accuracy,
            'avg_confidence': avg_confidence,
            'new_badges': new_badges,
            'performance_message': 'Outstanding work!' if accuracy >= 90 else 'Great effort!' if accuracy >= 70 else 'Keep practicing!',
            'next_recommendation': f"Ready for {learning_session['subject']} at a higher level?" if accuracy >= 80 else f"Review {learning_session['subject']} fundamentals"
        })
        
        # Clear current session
        session.pop('current_learning_session', None)
    
    return jsonify(response)

@app.route('/dashboard')
def dashboard():
    """Comprehensive learning dashboard"""
    user = get_or_create_user()
    
    # Get recent achievements
    achievements = user.get_achievements() if hasattr(user, 'get_achievements') else []
    recent_achievements = achievements[-5:] if achievements else []
    
    # Calculate learning statistics
    total_time_hours = user.total_study_time // 60 if hasattr(user, 'total_study_time') else 0
    avg_session_accuracy = user.accuracy_percentage()
    
    return render_template('learning_dashboard.html',
                         user=user,
                         recent_achievements=recent_achievements,
                         total_time_hours=total_time_hours,
                         avg_session_accuracy=avg_session_accuracy)

@app.route('/profile')
def profile():
    """User profile and progress management"""
    user = get_or_create_user()
    
    # Get comprehensive user statistics
    profile_data = {
        'user': user,
        'learning_profile': user.get_learning_profile(),
        'achievements': user.get_achievements() if hasattr(user, 'get_achievements') else [],
        'total_badges': len(user.get_achievements()) if hasattr(user, 'get_achievements') else 0,
        'join_date': user.created_at if hasattr(user, 'created_at') else datetime.now(),
        'accuracy_trend': [user.accuracy_percentage()],  # Would be expanded with historical data
        'favorite_subjects': []  # Would be calculated from session history
    }
    
    return render_template('user_profile.html', **profile_data)

# Advanced Learning System API Endpoints
@app.route('/api/voice/command', methods=['POST'])
def process_voice_command():
    """Process voice navigation command"""
    if not advanced_features_enabled:
        return jsonify({'error': 'Advanced features not available'}), 503
    
    try:
        data = request.get_json()
        user_id = session.get('user_id', str(uuid.uuid4()))
        voice_input = data.get('voice_input', '')
        context = data.get('context', {})
        
        response = voice_navigation_system.process_voice_command(user_id, voice_input, context)
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Voice command error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/dashboard')
def get_analytics_dashboard():
    """Get comprehensive analytics dashboard"""
    if not advanced_features_enabled:
        return jsonify({'error': 'Advanced features not available'}), 503
    
    try:
        user_id = session.get('user_id', str(uuid.uuid4()))
        dashboard = analytics_dashboard.generate_user_dashboard(user_id)
        return jsonify(dashboard)
        
    except Exception as e:
        logger.error(f"Analytics dashboard error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/leaderboard')
def get_leaderboard():
    """Get leaderboard rankings"""
    if not advanced_features_enabled:
        return jsonify({'error': 'Advanced features not available'}), 503
    
    try:
        category = request.args.get('category', 'global')
        timeframe = request.args.get('timeframe', 'all_time')
        limit = int(request.args.get('limit', 50))
        
        leaderboard = leaderboard_engine.get_leaderboard(category, timeframe, limit)
        return jsonify(leaderboard)
        
    except Exception as e:
        logger.error(f"Leaderboard error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/spaced-repetition/cards')
def get_spaced_repetition_cards():
    """Get cards due for spaced repetition review"""
    if not advanced_features_enabled:
        return jsonify({'error': 'Advanced features not available'}), 503
    
    try:
        user_id = session.get('user_id', str(uuid.uuid4()))
        limit = int(request.args.get('limit', 20))
        
        cards = spaced_repetition_engine.get_cards_due_for_review(user_id, limit)
        return jsonify({'cards': cards})
        
    except Exception as e:
        logger.error(f"Spaced repetition error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/spaced-repetition/review', methods=['POST'])
def process_spaced_repetition_review():
    """Process spaced repetition card review"""
    if not advanced_features_enabled:
        return jsonify({'error': 'Advanced features not available'}), 503
    
    try:
        data = request.get_json()
        user_id = session.get('user_id', str(uuid.uuid4()))
        card_id = data.get('card_id')
        difficulty = data.get('difficulty', 3)  # 0-5 scale
        energy_level = data.get('energy_level', 5)
        
        from spaced_repetition_system import ReviewDifficulty
        review_difficulty = ReviewDifficulty(difficulty)
        
        result = spaced_repetition_engine.process_review(
            user_id, card_id, review_difficulty, energy_level
        )
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Spaced repetition review error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/adaptive-difficulty/recommendation')
def get_difficulty_recommendation():
    """Get adaptive difficulty recommendation"""
    if not advanced_features_enabled:
        return jsonify({'error': 'Advanced features not available'}), 503
    
    try:
        user_id = session.get('user_id', str(uuid.uuid4()))
        subject = request.args.get('subject', 'General')
        
        recommendation = adaptive_difficulty_engine.get_recommended_difficulty(
            user_id, subject
        )
        return jsonify(recommendation)
        
    except Exception as e:
        logger.error(f"Adaptive difficulty error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/analytics')
def get_user_analytics():
    """Get comprehensive user analytics"""
    if not advanced_features_enabled:
        return jsonify({'error': 'Advanced features not available'}), 503
    
    try:
        user_id = session.get('user_id', str(uuid.uuid4()))
        
        # Combine analytics from multiple systems
        analytics = {
            'dashboard': analytics_dashboard.generate_user_dashboard(user_id),
            'leaderboard': leaderboard_engine.get_user_analytics(user_id),
            'voice_usage': voice_navigation_system.get_voice_analytics(user_id),
            'spaced_repetition': spaced_repetition_engine.get_retention_insights(user_id)
        }
        
        return jsonify(analytics)
        
    except Exception as e:
        logger.error(f"User analytics error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/institutional/report')
def get_institutional_report():
    """Get institutional analytics report"""
    if not advanced_features_enabled:
        return jsonify({'error': 'Advanced features not available'}), 503
    
    try:
        institution_id = request.args.get('institution_id', 'default')
        report = analytics_dashboard.generate_institutional_report(institution_id)
        return jsonify(report)
        
    except Exception as e:
        logger.error(f"Institutional report error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/voice/commands')
def get_voice_commands():
    """Get available voice commands"""
    if not advanced_features_enabled:
        return jsonify({'error': 'Advanced features not available'}), 503
    
    try:
        user_id = session.get('user_id', str(uuid.uuid4()))
        commands = voice_navigation_system._get_user_relevant_commands(user_id)
        return jsonify({'commands': commands})
        
    except Exception as e:
        logger.error(f"Voice commands error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/social/features')
def get_social_features():
    """Get social learning features and recommendations"""
    if not advanced_features_enabled:
        return jsonify({'error': 'Advanced features not available'}), 503
    
    try:
        user_id = session.get('user_id', str(uuid.uuid4()))
        social_features = leaderboard_engine.get_social_features(user_id)
        return jsonify(social_features)
        
    except Exception as e:
        logger.error(f"Social features error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/learning-journey/map')
def get_learning_journey_map():
    """Get interactive learning journey map with visual progress tracking"""
    if not advanced_features_enabled:
        return jsonify({'error': 'Advanced features not available'}), 503
    
    try:
        user_id = session.get('user_id', str(uuid.uuid4()))
        subject = request.args.get('subject', 'Python Programming')
        
        visual_map = learning_journey_engine.get_visual_journey_map(user_id, subject)
        return jsonify(visual_map)
        
    except Exception as e:
        logger.error(f"Learning journey map error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/learning-journey/update', methods=['POST'])
def update_learning_journey():
    """Update learning journey progress"""
    if not advanced_features_enabled:
        return jsonify({'error': 'Advanced features not available'}), 503
    
    try:
        data = request.get_json()
        user_id = session.get('user_id', str(uuid.uuid4()))
        subject = data.get('subject', 'Python Programming')
        session_data = data.get('session_data', {})
        
        progress_update = learning_journey_engine.update_progress(user_id, subject, session_data)
        return jsonify(progress_update)
        
    except Exception as e:
        logger.error(f"Learning journey update error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/learning-journey/subjects')
def get_available_subjects():
    """Get available subjects with learning journey structures"""
    if not advanced_features_enabled:
        return jsonify({'error': 'Advanced features not available'}), 503
    
    try:
        subjects = []
        for subject in learning_journey_engine.subject_hierarchies.keys():
            overview = learning_journey_engine.get_subject_overview(subject)
            subjects.append(overview)
        
        return jsonify({'subjects': subjects})
        
    except Exception as e:
        logger.error(f"Available subjects error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/learning-journey')
def learning_journey_page():
    """Interactive learning journey map page"""
    user_id = session.get('user_id')
    if not user_id:
        user_id = str(uuid.uuid4())
        session['user_id'] = user_id
    
    # Get user data
    user = None
    try:
        user = db.session.execute(
            db.select(User).where(User.id == user_id)
        ).scalar_one_or_none()
        
        if not user:
            # Create temporary user object for journey map access
            user = type('TempUser', (), {
                'username': "Journey Explorer",
                'total_sessions': 0,
                'total_correct_answers': 0,
                'total_questions_answered': 0
            })()
    except Exception as e:
        logger.warning(f"User lookup error: {e}")
        user = type('TempUser', (), {
            'username': "Journey Explorer",
            'total_sessions': 0,
            'total_correct_answers': 0,
            'total_questions_answered': 0
        })()
    
    # Get available subjects
    available_subjects = []
    if advanced_features_enabled:
        try:
            for subject in learning_journey_engine.subject_hierarchies.keys():
                overview = learning_journey_engine.get_subject_overview(subject)
                available_subjects.append(overview)
        except Exception as e:
            logger.warning(f"Could not load subjects: {e}")
    
    return render_template('learning_journey.html', 
                         user=user,
                         available_subjects=available_subjects,
                         advanced_features=advanced_features_enabled)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)