"""
Database Models for NeuroPulse Learning Platform
Comprehensive model definitions for all platform features
"""

from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint, Index, String, Integer, Float, Boolean, Text, DateTime, Time
import json

# Import db from app after it's created
def get_db():
    from app import db
    return db

db = get_db()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.String(50), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    profile_image_url = db.Column(db.String(255), nullable=True)
    
    # Learning preferences
    learning_style = db.Column(db.String(20), default='visual')
    preferred_difficulty = db.Column(db.String(20), default='intermediate')
    study_schedule = db.Column(db.Text, nullable=True)  # JSON string
    accessibility_settings = db.Column(db.Text, nullable=True)  # JSON string
    
    # Platform settings
    current_theme = db.Column(db.String(20), default='focused')
    voice_enabled = db.Column(db.Boolean, default=True)
    notifications_enabled = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    quiz_sessions = db.relationship('QuizSession', backref='user', lazy=True, cascade='all, delete-orphan')
    learning_progress = db.relationship('LearningProgress', backref='user', lazy=True, cascade='all, delete-orphan')
    spaced_repetition_cards = db.relationship('SpacedRepetitionCard', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Subject(db.Model):
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    difficulty_levels = db.Column(db.Text, nullable=True)  # JSON string
    
    # Metadata
    icon = db.Column(db.String(50), nullable=True)
    color = db.Column(db.String(7), nullable=True)  # Hex color
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    questions = db.relationship('Question', backref='subject', lazy=True, cascade='all, delete-orphan')
    quiz_sessions = db.relationship('QuizSession', backref='subject', lazy=True)
    
    def __repr__(self):
        return f'<Subject {self.name}>'

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    
    # Question content
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), default='multiple_choice')
    difficulty_level = db.Column(db.String(20), nullable=False)
    topic = db.Column(db.String(100), nullable=True)
    
    # Answer data
    correct_answer = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=True)  # JSON string for multiple choice
    explanation = db.Column(db.Text, nullable=True)
    hints = db.Column(db.Text, nullable=True)  # JSON string
    
    # Metadata
    estimated_time = db.Column(db.Integer, default=60)  # seconds
    tags = db.Column(db.Text, nullable=True)  # JSON string
    is_active = db.Column(db.Boolean, default=True)
    
    # AI generation data
    ai_generated = db.Column(db.Boolean, default=False)
    generation_prompt = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    quiz_attempts = db.relationship('QuizAttempt', backref='question', lazy=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_subject_difficulty', 'subject_id', 'difficulty_level'),
        Index('idx_question_topic', 'topic'),
    )
    
    def __repr__(self):
        return f'<Question {self.id}: {self.question_text[:50]}...>'

class QuizSession(db.Model):
    __tablename__ = 'quiz_sessions'
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    
    # Session configuration
    session_type = db.Column(db.String(20), default='practice')  # practice, assessment, spaced_repetition
    difficulty_level = db.Column(db.String(20), nullable=False)
    target_questions = db.Column(db.Integer, default=10)
    time_limit = db.Column(db.Integer, nullable=True)  # seconds
    
    # Session progress
    current_question_index = db.Column(db.Integer, default=0)
    questions_answered = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    
    # Session state
    status = db.Column(db.String(20), default='active')  # active, completed, paused, abandoned
    adaptive_difficulty = db.Column(db.Boolean, default=True)
    
    # Performance metrics
    total_time_spent = db.Column(db.Integer, default=0)  # seconds
    average_response_time = db.Column(db.Float, default=0.0)
    confidence_scores = db.Column(db.Text, nullable=True)  # JSON string
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    attempts = db.relationship('QuizAttempt', backref='session', lazy=True, cascade='all, delete-orphan')
    
    @property
    def accuracy_percentage(self):
        if self.questions_answered == 0:
            return 0.0
        return (self.correct_answers / self.questions_answered) * 100
    
    def __repr__(self):
        return f'<QuizSession {self.id}: {self.user_id}>'

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('quiz_sessions.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    
    # Attempt details
    user_answer = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    response_time = db.Column(db.Float, nullable=False)  # seconds
    attempt_number = db.Column(db.Integer, default=1)
    
    # User interaction data
    confidence_level = db.Column(db.Integer, nullable=True)  # 1-5 scale
    hints_used = db.Column(db.Integer, default=0)
    difficulty_felt = db.Column(db.Integer, nullable=True)  # 1-5 scale
    
    # Timestamps
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_session_question', 'session_id', 'question_id'),
        Index('idx_attempt_time', 'answered_at'),
    )
    
    def __repr__(self):
        return f'<QuizAttempt {self.id}: {self.is_correct}>'

class LearningProgress(db.Model):
    __tablename__ = 'learning_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    
    # Progress metrics
    total_questions_attempted = db.Column(db.Integer, default=0)
    total_correct_answers = db.Column(db.Integer, default=0)
    current_difficulty_level = db.Column(db.String(20), default='beginner')
    mastery_level = db.Column(db.Float, default=0.0)  # 0-100 percentage
    
    # Performance tracking
    average_response_time = db.Column(db.Float, default=0.0)
    consistency_score = db.Column(db.Float, default=0.0)
    retention_strength = db.Column(db.Float, default=0.0)
    
    # Study patterns
    total_study_time = db.Column(db.Integer, default=0)  # seconds
    study_sessions_count = db.Column(db.Integer, default=0)
    last_study_date = db.Column(db.DateTime, nullable=True)
    study_streak = db.Column(db.Integer, default=0)
    
    # Adaptive learning data
    learning_velocity = db.Column(db.Float, default=0.5)
    challenge_tolerance = db.Column(db.Float, default=0.5)
    optimal_session_length = db.Column(db.Integer, default=1800)  # seconds
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('user_id', 'subject_id', name='unique_user_subject_progress'),
        Index('idx_user_progress', 'user_id'),
        Index('idx_mastery_level', 'mastery_level'),
    )
    
    @property
    def accuracy_percentage(self):
        if self.total_questions_attempted == 0:
            return 0.0
        return (self.total_correct_answers / self.total_questions_attempted) * 100
    
    def __repr__(self):
        return f'<LearningProgress {self.user_id}: {self.subject_id}>'

class SpacedRepetitionCard(db.Model):
    __tablename__ = 'spaced_repetition_cards'
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    
    # Card content
    front_content = db.Column(db.Text, nullable=False)
    back_content = db.Column(db.Text, nullable=False)
    subject_category = db.Column(db.String(50), nullable=False)
    topic = db.Column(db.String(100), nullable=True)
    difficulty_level = db.Column(db.String(20), default='intermediate')
    
    # Spaced repetition algorithm data
    ease_factor = db.Column(db.Float, default=2.5)
    interval_days = db.Column(db.Integer, default=1)
    repetitions = db.Column(db.Integer, default=0)
    quality_responses = db.Column(db.Text, nullable=True)  # JSON array
    
    # Review scheduling
    next_review_date = db.Column(db.DateTime, nullable=False)
    last_reviewed_date = db.Column(db.DateTime, nullable=True)
    graduation_stage = db.Column(db.String(20), default='learning')  # learning, review, mature
    
    # Performance metrics
    total_reviews = db.Column(db.Integer, default=0)
    correct_responses = db.Column(db.Integer, default=0)
    average_response_time = db.Column(db.Float, default=0.0)
    retention_strength = db.Column(db.Float, default=0.0)
    
    # Card metadata
    tags = db.Column(db.Text, nullable=True)  # JSON array
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_user_next_review', 'user_id', 'next_review_date'),
        Index('idx_subject_category', 'subject_category'),
        Index('idx_graduation_stage', 'graduation_stage'),
    )
    
    def __repr__(self):
        return f'<SpacedRepetitionCard {self.id}: {self.front_content[:30]}...>'

class UserMoodData(db.Model):
    __tablename__ = 'user_mood_data'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    
    # Mood information
    mood_state = db.Column(db.String(20), nullable=False)
    confidence_level = db.Column(db.Integer, nullable=True)  # 1-5 scale
    energy_level = db.Column(db.Integer, nullable=True)  # 1-100 scale
    
    # Context data
    context_factors = db.Column(db.Text, nullable=True)  # JSON string
    study_session_id = db.Column(db.String(36), nullable=True)
    
    # Timestamps
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_user_mood_time', 'user_id', 'recorded_at'),
    )
    
    def __repr__(self):
        return f'<UserMoodData {self.user_id}: {self.mood_state}>'

class LearningEnergyData(db.Model):
    __tablename__ = 'learning_energy_data'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    
    # Energy metrics
    energy_level = db.Column(db.Integer, nullable=False)  # 0-100
    energy_state = db.Column(db.String(20), nullable=False)  # peak, high, medium, low, depleted
    
    # Contributing factors
    factors_data = db.Column(db.Text, nullable=True)  # JSON string
    session_context = db.Column(db.Text, nullable=True)  # JSON string
    
    # Predictions and patterns
    predicted_peak_time = db.Column(db.Time, nullable=True)
    pattern_analysis = db.Column(db.Text, nullable=True)  # JSON string
    
    # Timestamps
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_user_energy_time', 'user_id', 'recorded_at'),
        Index('idx_energy_level', 'energy_level'),
    )
    
    def __repr__(self):
        return f'<LearningEnergyData {self.user_id}: {self.energy_level}>'

class OnboardingProgress(db.Model):
    __tablename__ = 'onboarding_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Progress tracking
    current_stage = db.Column(db.String(30), default='welcome')
    current_step = db.Column(db.Integer, default=0)
    completed_stages = db.Column(db.Text, nullable=True)  # JSON array
    total_progress = db.Column(db.Float, default=0.0)
    
    # Personalization data
    learning_profile = db.Column(db.Text, nullable=True)  # JSON string
    preferences_data = db.Column(db.Text, nullable=True)  # JSON string
    feature_discovery_progress = db.Column(db.Text, nullable=True)  # JSON string
    
    # Completion status
    onboarding_complete = db.Column(db.Boolean, default=False)
    personalization_complete = db.Column(db.Boolean, default=False)
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<OnboardingProgress {self.user_id}: {self.current_stage}>'

class VoiceCommandHistory(db.Model):
    __tablename__ = 'voice_command_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    
    # Command details
    original_command = db.Column(db.Text, nullable=False)
    normalized_command = db.Column(db.Text, nullable=False)
    recognized_action = db.Column(db.String(50), nullable=True)
    success = db.Column(db.Boolean, nullable=False)
    
    # Performance metrics
    confidence_score = db.Column(db.Float, nullable=True)
    processing_time = db.Column(db.Float, nullable=True)
    
    # Context
    session_context = db.Column(db.Text, nullable=True)  # JSON string
    
    # Timestamps
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_user_voice_time', 'user_id', 'executed_at'),
        Index('idx_voice_success', 'success'),
    )
    
    def __repr__(self):
        return f'<VoiceCommandHistory {self.user_id}: {self.original_command[:30]}...>'

class SystemAnalytics(db.Model):
    __tablename__ = 'system_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Metric information
    metric_name = db.Column(db.String(100), nullable=False)
    metric_value = db.Column(db.Float, nullable=False)
    metric_unit = db.Column(db.String(20), nullable=True)
    
    # Categorization
    category = db.Column(db.String(50), nullable=False)
    subcategory = db.Column(db.String(50), nullable=True)
    
    # Context data
    metadata = db.Column(db.Text, nullable=True)  # JSON string
    aggregation_period = db.Column(db.String(20), nullable=True)  # hourly, daily, weekly
    
    # Timestamps
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    period_start = db.Column(db.DateTime, nullable=True)
    period_end = db.Column(db.DateTime, nullable=True)
    
    # Indexes for analytics queries
    __table_args__ = (
        Index('idx_metric_name_time', 'metric_name', 'recorded_at'),
        Index('idx_category_time', 'category', 'recorded_at'),
    )
    
    def __repr__(self):
        return f'<SystemAnalytics {self.metric_name}: {self.metric_value}>'

# Create all tables
def init_db():
    """Initialize database tables"""
    try:
        db.create_all()
        return True
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False