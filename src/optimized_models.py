"""
Optimized Database Models for NeuroPulse Learning Platform
Streamlined model definitions with proper database integration
"""

from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, Index, UniqueConstraint
import json

def create_models(db):
    """Create all database models with proper db instance"""
    
    class User(UserMixin, db.Model):
        __tablename__ = 'users'
        __table_args__ = {'extend_existing': True}
        
        id = Column(String(50), primary_key=True)
        email = Column(String(120), unique=True, nullable=True)
        username = Column(String(80), unique=True, nullable=False)
        first_name = Column(String(50), nullable=True)
        last_name = Column(String(50), nullable=True)
        
        # Learning preferences stored as JSON
        learning_preferences = Column(Text, nullable=True)
        accessibility_settings = Column(Text, nullable=True)
        dashboard_config = Column(Text, nullable=True)
        
        # Timestamps
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        last_active = Column(DateTime, default=datetime.utcnow)
        
        def get_learning_preferences(self):
            """Get learning preferences as dict"""
            if self.learning_preferences:
                try:
                    return json.loads(self.learning_preferences)
                except:
                    return {}
            return {}
        
        def set_learning_preferences(self, prefs):
            """Set learning preferences from dict"""
            self.learning_preferences = json.dumps(prefs)
        
        def __repr__(self):
            return f'<User {self.username}>'
    
    class Subject(db.Model):
        __tablename__ = 'subjects'
        __table_args__ = {'extend_existing': True}
        
        id = Column(Integer, primary_key=True)
        name = Column(String(100), nullable=False, unique=True)
        category = Column(String(50), nullable=False)
        description = Column(Text, nullable=True)
        
        # Configuration stored as JSON
        config_data = Column(Text, nullable=True)
        
        # Status
        is_active = Column(Boolean, default=True)
        
        # Timestamps
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        def __repr__(self):
            return f'<Subject {self.name}>'
    
    class Question(db.Model):
        __tablename__ = 'questions'
        __table_args__ = (
            {'extend_existing': True},
            Index('idx_subject_difficulty', 'subject_id', 'difficulty_level'),
        )
        
        id = Column(Integer, primary_key=True)
        subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
        
        # Question content
        question_text = Column(Text, nullable=False)
        question_type = Column(String(20), default='multiple_choice')
        difficulty_level = Column(String(20), nullable=False)
        topic = Column(String(100), nullable=True)
        
        # Answer data stored as JSON
        answer_data = Column(Text, nullable=False)
        metadata = Column(Text, nullable=True)
        
        # Status
        is_active = Column(Boolean, default=True)
        
        # Timestamps
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        def get_answer_data(self):
            """Get answer data as dict"""
            try:
                return json.loads(self.answer_data)
            except:
                return {}
        
        def set_answer_data(self, data):
            """Set answer data from dict"""
            self.answer_data = json.dumps(data)
        
        def __repr__(self):
            return f'<Question {self.id}: {self.question_text[:50]}...>'
    
    class QuizSession(db.Model):
        __tablename__ = 'quiz_sessions'
        __table_args__ = {'extend_existing': True}
        
        id = Column(String(36), primary_key=True)
        user_id = Column(String(50), ForeignKey('users.id'), nullable=False)
        subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
        
        # Session configuration
        session_type = Column(String(20), default='practice')
        difficulty_level = Column(String(20), nullable=False)
        
        # Progress tracking
        current_question_index = Column(Integer, default=0)
        questions_answered = Column(Integer, default=0)
        correct_answers = Column(Integer, default=0)
        
        # Session data stored as JSON
        session_data = Column(Text, nullable=True)
        
        # Status
        status = Column(String(20), default='active')
        
        # Timestamps
        started_at = Column(DateTime, default=datetime.utcnow)
        completed_at = Column(DateTime, nullable=True)
        
        @property
        def accuracy_percentage(self):
            if self.questions_answered == 0:
                return 0.0
            return (self.correct_answers / self.questions_answered) * 100
        
        def __repr__(self):
            return f'<QuizSession {self.id}>'
    
    class LearningProgress(db.Model):
        __tablename__ = 'learning_progress'
        __table_args__ = (
            {'extend_existing': True},
            UniqueConstraint('user_id', 'subject_id', name='unique_user_subject_progress'),
        )
        
        id = Column(Integer, primary_key=True)
        user_id = Column(String(50), ForeignKey('users.id'), nullable=False)
        subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
        
        # Progress metrics
        total_questions_attempted = Column(Integer, default=0)
        total_correct_answers = Column(Integer, default=0)
        current_difficulty_level = Column(String(20), default='beginner')
        mastery_level = Column(Float, default=0.0)
        
        # Additional data stored as JSON
        progress_data = Column(Text, nullable=True)
        
        # Timestamps
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        @property
        def accuracy_percentage(self):
            if self.total_questions_attempted == 0:
                return 0.0
            return (self.total_correct_answers / self.total_questions_attempted) * 100
        
        def __repr__(self):
            return f'<LearningProgress {self.user_id}:{self.subject_id}>'
    
    class UserAnalytics(db.Model):
        __tablename__ = 'user_analytics'
        __table_args__ = (
            {'extend_existing': True},
            Index('idx_user_analytics_time', 'user_id', 'recorded_at'),
        )
        
        id = Column(Integer, primary_key=True)
        user_id = Column(String(50), ForeignKey('users.id'), nullable=False)
        
        # Analytics type
        analytics_type = Column(String(50), nullable=False)
        
        # Data stored as JSON
        analytics_data = Column(Text, nullable=False)
        
        # Timestamps
        recorded_at = Column(DateTime, default=datetime.utcnow)
        
        def get_analytics_data(self):
            """Get analytics data as dict"""
            try:
                return json.loads(self.analytics_data)
            except:
                return {}
        
        def set_analytics_data(self, data):
            """Set analytics data from dict"""
            self.analytics_data = json.dumps(data)
        
        def __repr__(self):
            return f'<UserAnalytics {self.user_id}:{self.analytics_type}>'
    
    # Return all model classes
    return {
        'User': User,
        'Subject': Subject,
        'Question': Question,
        'QuizSession': QuizSession,
        'LearningProgress': LearningProgress,
        'UserAnalytics': UserAnalytics
    }