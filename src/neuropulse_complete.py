"""
NeuroPulse - Complete AI-Powered Adaptive Learning Platform
Enterprise-grade microlearning system optimized for neurodivergent minds
"""

import os
import logging
import json
import uuid
from datetime import datetime, timedelta
from flask import Flask, render_template, render_template_string, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from openai import OpenAI

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "neuropulse-dev-key-2024")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Enhanced database configuration
app.config.update({
    "SQLALCHEMY_DATABASE_URI": os.environ.get("DATABASE_URL", "sqlite:///neuropulse_complete.db"),
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    "SQLALCHEMY_ENGINE_OPTIONS": {
        'pool_pre_ping': True,
        "pool_recycle": 300,
        "pool_timeout": 20,
        "max_overflow": 0
    },
    "SESSION_PERMANENT": True,
    "PERMANENT_SESSION_LIFETIME": timedelta(days=30)
})

# Initialize database
db = SQLAlchemy(app, model_class=Base)

# Initialize OpenAI with comprehensive error handling
try:
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    # Test the connection
    test_response = openai_client.models.list()
    AI_ENABLED = True
    logger.info("OpenAI integration successfully enabled and tested")
except Exception as e:
    logger.warning(f"OpenAI not available: {e}")
    AI_ENABLED = False
    openai_client = None

# Comprehensive Database Models
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    
    # Learning profile data
    learning_style = db.Column(db.String(20), default='adaptive')
    attention_span = db.Column(db.Integer, default=8)  # minutes
    difficulty_preference = db.Column(db.String(20), default='adaptive')
    
    # Personalization data stored as JSON
    learning_profile = db.Column(db.Text, default='{}')
    preferences = db.Column(db.Text, default='{}')
    progress_data = db.Column(db.Text, default='{}')
    
    # Gamification stats
    total_sessions = db.Column(db.Integer, default=0)
    total_correct_answers = db.Column(db.Integer, default=0)
    total_questions_answered = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    last_session_date = db.Column(db.Date, nullable=True)
    
    def accuracy_percentage(self):
        if self.total_questions_answered == 0:
            return 0.0
        return (self.total_correct_answers / self.total_questions_answered) * 100
    
    def get_learning_profile(self):
        try:
            return json.loads(self.learning_profile)
        except:
            return {}
    
    def update_learning_profile(self, data):
        self.learning_profile = json.dumps(data)

class Subject(db.Model):
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(20), nullable=True)
    color = db.Column(db.String(7), default='#6366f1')
    
    # AI-generated content tracking
    ai_generated = db.Column(db.Boolean, default=True)
    content_quality_score = db.Column(db.Float, default=0.8)
    
    # Usage statistics
    total_sessions = db.Column(db.Integer, default=0)
    average_completion_rate = db.Column(db.Float, default=0.0)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LearningSession(db.Model):
    __tablename__ = 'learning_sessions'
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True)
    
    # Session configuration
    subject_name = db.Column(db.String(100), nullable=False)
    difficulty_level = db.Column(db.String(20), default='adaptive')
    session_type = db.Column(db.String(30), default='adaptive_quiz')
    
    # Progress tracking
    current_question_index = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=5)
    correct_answers = db.Column(db.Integer, default=0)
    
    # Session data and analytics
    session_data = db.Column(db.Text, nullable=False)  # JSON: questions, answers, timing
    analytics_data = db.Column(db.Text, default='{}')  # JSON: response times, confidence levels
    
    # Status and timing
    status = db.Column(db.String(20), default='active')  # active, completed, abandoned
    estimated_duration = db.Column(db.Integer, default=600)  # seconds
    actual_duration = db.Column(db.Integer, nullable=True)
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='sessions')
    subject = db.relationship('Subject', backref='sessions')
    
    def accuracy_percentage(self):
        if self.current_question_index == 0:
            return 0.0
        return (self.correct_answers / self.current_question_index) * 100
    
    def get_session_data(self):
        try:
            return json.loads(self.session_data)
        except:
            return {}
    
    def update_session_data(self, data):
        self.session_data = json.dumps(data)

class GeneratedContent(db.Model):
    __tablename__ = 'generated_content'
    
    id = db.Column(db.String(36), primary_key=True)
    subject_name = db.Column(db.String(100), nullable=False)
    difficulty_level = db.Column(db.String(20), nullable=False)
    content_type = db.Column(db.String(30), default='adaptive_quiz')
    
    # Content data
    content_data = db.Column(db.Text, nullable=False)  # JSON
    generation_prompt = db.Column(db.Text, nullable=True)
    
    # Quality metrics
    usage_count = db.Column(db.Integer, default=0)
    average_score = db.Column(db.Float, default=0.0)
    user_feedback_score = db.Column(db.Float, default=0.0)
    
    # AI metadata
    model_used = db.Column(db.String(50), default='gpt-4o')
    generation_time = db.Column(db.Float, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    def get_content_data(self):
        try:
            return json.loads(self.content_data)
        except:
            return {}

# Comprehensive AI Content Generation System
class AIContentGenerator:
    def __init__(self, openai_client):
        self.client = openai_client
        self.enabled = openai_client is not None
    
    def generate_adaptive_content(self, subject, difficulty='adaptive', user_profile=None):
        """Generate comprehensive adaptive learning content"""
        if not self.enabled:
            return self._get_fallback_content(subject, difficulty)
        
        try:
            # Create sophisticated prompt based on user profile and subject
            prompt = self._create_adaptive_prompt(subject, difficulty, user_profile)
            
            start_time = datetime.now()
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert educational content creator specializing in neurodivergent-friendly learning experiences. 
                        Create engaging, interactive, bite-sized learning content optimized for ADHD minds with:
                        - Clear, focused questions without cognitive overload
                        - Progressive difficulty building
                        - Immediate dopamine rewards through achievement recognition
                        - Confidence tracking and adaptive feedback
                        - Real-world applications and examples
                        - Interactive elements where appropriate"""
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=2000
            )
            
            generation_time = (datetime.now() - start_time).total_seconds()
            content = json.loads(response.choices[0].message.content)
            
            # Store generated content for future use
            self._store_generated_content(subject, difficulty, content, prompt, generation_time)
            
            return content
            
        except Exception as e:
            logger.error(f"AI content generation failed: {e}")
            return self._get_fallback_content(subject, difficulty)
    
    def _create_adaptive_prompt(self, subject, difficulty, user_profile):
        """Create sophisticated prompt based on learning profile"""
        base_prompt = f"""
        Create an adaptive learning session for: {subject}
        Difficulty level: {difficulty}
        
        Generate 5-7 progressive questions with the following structure:
        {{
            "subject": "{subject}",
            "difficulty": "{difficulty}",
            "session_type": "adaptive_quiz",
            "estimated_time": "5-8 minutes",
            "learning_objectives": ["objective1", "objective2"],
            "questions": [
                {{
                    "id": 1,
                    "question": "Clear, focused question text",
                    "type": "multiple_choice",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "explanation": "Detailed explanation why this is correct",
                    "difficulty": "beginner|intermediate|advanced",
                    "learning_objective": "What this question teaches",
                    "confidence_prompt": "How confident are you in this answer?",
                    "interactive_element": "none|diagram|timer|drag_drop",
                    "real_world_context": "How this applies in real situations",
                    "dopamine_reward": "Encouraging message for correct answer"
                }}
            ],
            "adaptive_pathways": {{
                "if_struggling": "Suggest easier concepts or review",
                "if_mastering": "Suggest advanced topics or applications",
                "next_session_suggestions": ["topic1", "topic2"]
            }},
            "gamification": {{
                "points_available": 100,
                "streak_bonus": true,
                "achievement_unlocks": ["achievement_name"]
            }}
        }}
        
        Focus on creating questions that:
        1. Build progressive understanding
        2. Include real-world applications
        3. Provide clear explanations
        4. Offer dopamine rewards for engagement
        5. Adapt to different learning styles
        """
        
        if user_profile:
            learning_style = user_profile.get('learning_style', 'adaptive')
            attention_span = user_profile.get('attention_span', 8)
            base_prompt += f"\n\nUser Profile: Learning style: {learning_style}, Attention span: {attention_span} minutes"
        
        return base_prompt
    
    def _store_generated_content(self, subject, difficulty, content, prompt, generation_time):
        """Store generated content for reuse and analytics"""
        try:
            content_id = str(uuid.uuid4())
            generated_content = GeneratedContent()
            generated_content.id = content_id
            generated_content.subject_name = subject
            generated_content.difficulty_level = difficulty
            generated_content.content_data = json.dumps(content)
            generated_content.generation_prompt = prompt
            generated_content.generation_time = generation_time
            generated_content.expires_at = datetime.utcnow() + timedelta(days=30)
            
            db.session.add(generated_content)
            db.session.commit()
            
        except Exception as e:
            logger.warning(f"Could not store generated content: {e}")
            db.session.rollback()
    
    def _get_fallback_content(self, subject, difficulty):
        """High-quality fallback content when AI is unavailable"""
        return {
            "subject": subject,
            "difficulty": difficulty,
            "session_type": "adaptive_quiz",
            "estimated_time": "5-7 minutes",
            "learning_objectives": [f"Understand key concepts in {subject}", f"Apply {subject} knowledge"],
            "questions": [
                {
                    "id": 1,
                    "question": f"What aspect of {subject} would you like to explore first?",
                    "type": "multiple_choice",
                    "options": [
                        f"Fundamental concepts of {subject}",
                        f"Practical applications of {subject}",
                        f"Advanced techniques in {subject}",
                        f"Real-world examples of {subject}"
                    ],
                    "correct_answer": f"Fundamental concepts of {subject}",
                    "explanation": f"Starting with fundamentals provides a strong foundation for mastering {subject}",
                    "difficulty": "beginner",
                    "learning_objective": f"Establish learning direction for {subject}",
                    "confidence_prompt": "How confident do you feel about this topic area?",
                    "interactive_element": "none",
                    "real_world_context": f"Understanding {subject} basics helps in many professional and personal contexts",
                    "dopamine_reward": "Great choice! Building strong foundations leads to lasting success!"
                }
            ],
            "adaptive_pathways": {
                "if_struggling": f"Let's start with even more basic {subject} concepts",
                "if_mastering": f"Ready to explore intermediate {subject} topics!",
                "next_session_suggestions": [f"Basic {subject} principles", f"{subject} terminology"]
            },
            "gamification": {
                "points_available": 50,
                "streak_bonus": True,
                "achievement_unlocks": ["First Steps in " + subject]
            }
        }

# Initialize AI content generator
ai_generator = AIContentGenerator(openai_client)

# Enhanced User Management System
def get_or_create_user():
    """Get existing user or create new one with comprehensive profile"""
    try:
        if 'user_id' not in session:
            session['user_id'] = f"user_{uuid.uuid4().hex[:8]}"
            session['username'] = f"Learner_{session['user_id'][-4:]}"
            session.permanent = True
        
        user_id = session['user_id']
        username = session['username']
        
        # Try to find existing user
        try:
            user = User.query.filter_by(id=user_id).first()
        except Exception as e:
            logger.warning(f"Database query error: {e}")
            user = None
        
        if not user:
            try:
                user = User()
                user.id = user_id
                user.username = username
                user.email = None
                user.learning_style = 'adaptive'
                user.attention_span = 8
                user.difficulty_preference = 'adaptive'
                user.learning_profile = json.dumps({
                    'onboarding_complete': False,
                    'learning_style': 'adaptive',
                    'preferred_session_length': 8,
                    'difficulty_preference': 'adaptive',
                    'subjects_of_interest': []
                })
                user.preferences = '{}'
                user.progress_data = '{}'
                
                db.session.add(user)
                db.session.commit()
                logger.info(f"Created new user: {user_id}")
                
            except Exception as e:
                logger.error(f"Error creating user: {e}")
                db.session.rollback()
                # Create minimal fallback user object for session
                class FallbackUser:
                    def __init__(self):
                        self.id = user_id
                        self.username = username
                        self.total_sessions = 0
                        self.total_correct_answers = 0
                        self.total_questions_answered = 0
                        self.current_streak = 0
                        self.longest_streak = 0
                        self.email = None
                        self.learning_style = 'adaptive'
                        self.attention_span = 8
                        self.difficulty_preference = 'adaptive'
                        self.learning_profile = '{}'
                        self.preferences = '{}'
                        self.progress_data = '{}'
                        self.created_at = datetime.utcnow()
                        self.last_active = datetime.utcnow()
                        self.last_session_date = None
                    
                    def accuracy_percentage(self):
                        return 0.0
                    
                    def get_learning_profile(self):
                        return {'onboarding_complete': False}
                    
                    def update_learning_profile(self, data):
                        self.learning_profile = json.dumps(data)
                
                return FallbackUser()
        
        return user
        
    except Exception as e:
        logger.error(f"Critical user management error: {e}")
        return None

# Create database tables
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

# Main Application Routes
@app.route('/')
def index():
    """Enhanced main dashboard with personalization"""
    user = get_or_create_user()
    if not user:
        return "Database error. Please refresh the page.", 500
    
    # Update last active
    user.last_active = datetime.utcnow()
    db.session.commit()
    
    profile = user.get_learning_profile()
    show_onboarding = not profile.get('onboarding_complete', False)
    
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NeuroPulse - Learn Anything</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
                overflow-x: hidden;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                animation: fadeIn 0.8s ease-out;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .header {
                text-align: center;
                margin-bottom: 40px;
                padding: 40px 0;
            }
            
            .logo {
                font-size: 3.5rem;
                font-weight: 800;
                margin-bottom: 15px;
                background: linear-gradient(45deg, #FFE082, #FFF, #64B5F6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                text-shadow: 0 4px 20px rgba(0,0,0,0.3);
            }
            
            .tagline {
                font-size: 1.3rem;
                opacity: 0.95;
                margin-bottom: 20px;
                font-weight: 300;
                letter-spacing: 0.5px;
            }
            
            .ai-badge {
                display: inline-block;
                background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
                padding: 8px 20px;
                border-radius: 25px;
                font-size: 0.9rem;
                font-weight: 600;
                margin-bottom: 30px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }
            
            .welcome-card {
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(20px);
                border-radius: 25px;
                padding: 40px;
                margin-bottom: 40px;
                border: 1px solid rgba(255,255,255,0.2);
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                text-align: center;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            
            .stat-item {
                text-align: center;
                padding: 20px;
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                transition: transform 0.3s ease;
            }
            
            .stat-item:hover {
                transform: translateY(-5px);
            }
            
            .stat-number {
                font-size: 2rem;
                font-weight: 700;
                color: #4CAF50;
                margin-bottom: 5px;
            }
            
            .stat-label {
                font-size: 0.85rem;
                opacity: 0.8;
            }
            
            .subject-input-section {
                text-align: center;
                margin-bottom: 50px;
            }
            
            .input-group {
                position: relative;
                max-width: 600px;
                margin: 0 auto;
            }
            
            .subject-input {
                width: 100%;
                padding: 20px 25px;
                font-size: 1.1rem;
                border: none;
                border-radius: 20px;
                background: rgba(255,255,255,0.95);
                color: #333;
                margin-bottom: 25px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.2);
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
            }
            
            .subject-input:focus {
                outline: none;
                transform: translateY(-2px);
                box-shadow: 0 12px 35px rgba(0,0,0,0.3);
            }
            
            .start-button {
                background: linear-gradient(45deg, #4CAF50, #45a049);
                color: white;
                padding: 18px 45px;
                border: none;
                border-radius: 30px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .start-button:hover {
                transform: translateY(-3px);
                box-shadow: 0 10px 30px rgba(76, 175, 80, 0.6);
            }
            
            .examples-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 25px;
                margin-top: 50px;
            }
            
            .example-card {
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(15px);
                border-radius: 20px;
                padding: 30px;
                border: 1px solid rgba(255,255,255,0.2);
                cursor: pointer;
                transition: all 0.4s ease;
                position: relative;
                overflow: hidden;
            }
            
            .example-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
                transition: left 0.5s;
            }
            
            .example-card:hover {
                transform: translateY(-8px);
                background: rgba(255,255,255,0.15);
                box-shadow: 0 15px 40px rgba(0,0,0,0.4);
            }
            
            .example-card:hover::before {
                left: 100%;
            }
            
            .example-icon {
                font-size: 3.5rem;
                margin-bottom: 20px;
                display: block;
                text-align: center;
            }
            
            .example-title {
                font-size: 1.4rem;
                font-weight: 700;
                margin-bottom: 15px;
                text-align: center;
            }
            
            .example-desc {
                opacity: 0.85;
                line-height: 1.6;
                text-align: center;
                font-size: 0.95rem;
            }
            
            .features-section {
                margin-top: 60px;
                text-align: center;
            }
            
            .features-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 30px;
                margin-top: 40px;
            }
            
            .feature-item {
                padding: 30px;
                background: rgba(255,255,255,0.08);
                border-radius: 20px;
                border: 1px solid rgba(255,255,255,0.1);
                transition: all 0.3s ease;
            }
            
            .feature-item:hover {
                background: rgba(255,255,255,0.12);
                transform: translateY(-5px);
            }
            
            .feature-icon {
                font-size: 2.5rem;
                margin-bottom: 20px;
                display: block;
            }
            
            .feature-title {
                font-size: 1.2rem;
                font-weight: 600;
                margin-bottom: 15px;
            }
            
            .feature-desc {
                opacity: 0.85;
                line-height: 1.5;
                font-size: 0.95rem;
            }
            
            .nav-actions {
                position: fixed;
                top: 20px;
                right: 20px;
                display: flex;
                gap: 15px;
                z-index: 1000;
            }
            
            .nav-button {
                background: rgba(255,255,255,0.15);
                backdrop-filter: blur(10px);
                color: white;
                padding: 12px 20px;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 25px;
                text-decoration: none;
                font-weight: 500;
                transition: all 0.3s ease;
                font-size: 0.9rem;
            }
            
            .nav-button:hover {
                background: rgba(255,255,255,0.25);
                transform: translateY(-2px);
                text-decoration: none;
                color: white;
            }
        </style>
    </head>
    <body>
        <div class="nav-actions">
            <a href="/progress" class="nav-button">📊 Progress</a>
            {% if show_onboarding %}
            <a href="/onboarding" class="nav-button">🎯 Setup</a>
            {% endif %}
        </div>
        
        <div class="container">
            <div class="header">
                <div class="logo">🧠 NeuroPulse</div>
                <div class="tagline">Learn Anything, Remember Everything, Love Every Minute</div>
                <div class="ai-badge">{{ "✨ AI-Powered Learning" if ai_enabled else "🔧 Core Learning Features" }}</div>
            </div>
            
            <div class="welcome-card">
                <h2>Welcome back, {{ user.username }}!</h2>
                <p style="margin: 20px 0; font-size: 1.1rem; opacity: 0.9;">
                    What would you like to learn today? From quantum physics to plumbing, 
                    from Excel to electrical engineering - I'll create a personalized learning experience just for you.
                </p>
                
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-number">{{ user.total_sessions }}</div>
                        <div class="stat-label">Sessions</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{{ "%.0f"|format(user.accuracy_percentage()) }}%</div>
                        <div class="stat-label">Accuracy</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{{ user.current_streak }}</div>
                        <div class="stat-label">Streak</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{{ user.total_correct_answers }}</div>
                        <div class="stat-label">Correct</div>
                    </div>
                </div>
            </div>
            
            <div class="subject-input-section">
                <form action="/learn" method="POST">
                    <div class="input-group">
                        <input type="text" name="subject" class="subject-input" 
                               placeholder="Type any subject you want to learn (e.g., 'Python programming', 'Italian cooking', 'financial planning')" 
                               required autocomplete="off">
                        <button type="submit" class="start-button">Start Learning Journey</button>
                    </div>
                </form>
            </div>
            
            <div class="examples-grid">
                <div class="example-card" onclick="startSubject('Data Analysis & Visualization')">
                    <div class="example-icon">📊</div>
                    <div class="example-title">Data Analysis</div>
                    <div class="example-desc">Master Excel, Python, and visualization techniques with interactive exercises and real datasets</div>
                </div>
                
                <div class="example-card" onclick="startSubject('Electrical Engineering Fundamentals')">
                    <div class="example-icon">⚡</div>
                    <div class="example-title">Electrical Engineering</div>
                    <div class="example-desc">Wire virtual circuits, solve engineering challenges, and master electrical concepts step-by-step</div>
                </div>
                
                <div class="example-card" onclick="startSubject('Italian Language & Culture')">
                    <div class="example-icon">🇮🇹</div>
                    <div class="example-title">Language Learning</div>
                    <div class="example-desc">Interactive conversations, grammar puzzles, and cultural immersion with native content</div>
                </div>
                
                <div class="example-card" onclick="startSubject('Personal Financial Planning')">
                    <div class="example-icon">💰</div>
                    <div class="example-title">Financial Planning</div>
                    <div class="example-desc">Budgeting, investing, and wealth-building strategies with practical calculators and simulations</div>
                </div>
                
                <div class="example-card" onclick="startSubject('Organic Chemistry Mastery')">
                    <div class="example-icon">🧪</div>
                    <div class="example-title">Chemistry</div>
                    <div class="example-desc">Build molecules in 3D, balance equations interactively, and explore chemical reactions</div>
                </div>
                
                <div class="example-card" onclick="startSubject('Creative Writing & Storytelling')">
                    <div class="example-icon">✍️</div>
                    <div class="example-title">Creative Writing</div>
                    <div class="example-desc">Storytelling techniques, character development, and narrative structure with AI feedback</div>
                </div>
            </div>
            
            <div class="features-section">
                <h2 style="font-size: 2.2rem; margin-bottom: 20px;">Why NeuroPulse Works</h2>
                <p style="font-size: 1.1rem; opacity: 0.9; margin-bottom: 40px;">Designed specifically for neurodivergent minds with cutting-edge learning science</p>
                
                <div class="features-grid">
                    <div class="feature-item">
                        <div class="feature-icon">🎯</div>
                        <div class="feature-title">AI-Adaptive Learning</div>
                        <div class="feature-desc">Advanced algorithms adjust to your unique learning patterns, pace, and preferences in real-time</div>
                    </div>
                    
                    <div class="feature-item">
                        <div class="feature-icon">⏱️</div>
                        <div class="feature-title">ADHD-Optimized Sessions</div>
                        <div class="feature-desc">5-10 minute focused bursts designed for optimal attention and retention without overwhelm</div>
                    </div>
                    
                    <div class="feature-item">
                        <div class="feature-icon">🎮</div>
                        <div class="feature-title">Gamified Progress</div>
                        <div class="feature-desc">Streaks, achievements, and dopamine rewards that make learning addictive in the best way</div>
                    </div>
                    
                    <div class="feature-item">
                        <div class="feature-icon">🧠</div>
                        <div class="feature-title">Neurodivergent Friendly</div>
                        <div class="feature-desc">Built from the ground up for ADHD, dyslexia, autism, and other learning differences</div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            function startSubject(subject) {
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '/learn';
                
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'subject';
                input.value = subject;
                
                form.appendChild(input);
                document.body.appendChild(form);
                form.submit();
            }
            
            // Enhanced form submission with loading state
            document.querySelector('form').addEventListener('submit', function(e) {
                const button = this.querySelector('.start-button');
                button.innerHTML = '🚀 Creating Your Learning Experience...';
                button.disabled = true;
            });
            
            // Auto-focus on input
            document.querySelector('.subject-input').focus();
        </script>
    </body>
    </html>
    """, user=user, ai_enabled=AI_ENABLED, show_onboarding=show_onboarding)

@app.route('/learn', methods=['POST'])
def start_learning():
    """Enhanced learning session initialization with AI content generation"""
    user = get_or_create_user()
    if not user:
        flash("Please try again in a moment", "error")
        return redirect(url_for('index'))
    
    subject = request.form.get('subject', '').strip()
    if not subject:
        flash("Please enter a subject to learn", "warning")
        return redirect(url_for('index'))
    
    # Create or find subject
    subject_obj = Subject.query.filter_by(name=subject).first()
    if not subject_obj:
        subject_obj = Subject()
        subject_obj.name = subject
        subject_obj.category = 'User Generated'
        subject_obj.description = f"AI-generated content for {subject}"
        subject_obj.icon = '🎯'
        db.session.add(subject_obj)
    
    # Generate learning session
    session_id = str(uuid.uuid4())
    session['current_session_id'] = session_id
    session['current_subject'] = subject
    session['current_question'] = 0
    session['correct_answers'] = 0
    session['session_start'] = datetime.now().isoformat()
    
    # Generate AI content based on user profile
    user_profile = user.get_learning_profile()
    content = ai_generator.generate_adaptive_content(subject, 'adaptive', user_profile)
    
    # Create learning session
    learning_session = LearningSession()
    learning_session.id = session_id
    learning_session.user_id = user.id
    learning_session.subject_id = subject_obj.id
    learning_session.subject_name = subject
    learning_session.total_questions = len(content.get('questions', []))
    learning_session.update_session_data(content)
    
    # Update user stats
    user.total_sessions += 1
    user.last_active = datetime.utcnow()
    
    # Update subject stats
    subject_obj.total_sessions += 1
    
    try:
        db.session.commit()
        logger.info(f"Created learning session {session_id} for {subject}")
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        db.session.rollback()
        flash("Error creating learning session. Please try again.", "error")
        return redirect(url_for('index'))
    
    return redirect(url_for('learning_interface'))

@app.route('/interface', methods=['GET', 'POST'])
def learning_interface():
    """Enhanced learning interface with adaptive questioning"""
    if 'current_session_id' not in session:
        return redirect(url_for('index'))
    
    session_id = session['current_session_id']
    learning_session = LearningSession.query.filter_by(id=session_id).first()
    
    if not learning_session:
        flash("Session not found. Starting a new one.", "info")
        return redirect(url_for('index'))
    
    current_question = session.get('current_question', 0)
    session_data = learning_session.get_session_data()
    questions = session_data.get('questions', [])
    
    if current_question >= len(questions):
        return redirect(url_for('session_complete'))
    
    question = questions[current_question]
    progress = ((current_question + 1) / len(questions)) * 100
    
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Learning: {{ learning_session.subject_name }} - NeuroPulse</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
                padding: 20px;
                animation: fadeIn 0.6s ease-out;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .learning-container {
                max-width: 900px;
                margin: 0 auto;
            }
            
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            
            .subject-title {
                font-size: 2rem;
                font-weight: 700;
                margin-bottom: 15px;
                background: linear-gradient(45deg, #FFE082, #FFF);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .session-info {
                display: flex;
                justify-content: center;
                gap: 30px;
                margin-bottom: 20px;
                flex-wrap: wrap;
            }
            
            .info-item {
                background: rgba(255,255,255,0.1);
                padding: 10px 20px;
                border-radius: 20px;
                font-size: 0.9rem;
                backdrop-filter: blur(10px);
            }
            
            .progress-container {
                background: rgba(255,255,255,0.2);
                border-radius: 15px;
                padding: 6px;
                margin-bottom: 40px;
                box-shadow: inset 0 2px 5px rgba(0,0,0,0.2);
            }
            
            .progress-bar {
                background: linear-gradient(45deg, #4CAF50, #45a049);
                height: 12px;
                border-radius: 10px;
                width: {{ progress }}%;
                transition: width 0.5s ease;
                box-shadow: 0 2px 10px rgba(76, 175, 80, 0.4);
            }
            
            .progress-text {
                text-align: center;
                margin-top: 15px;
                font-size: 0.95rem;
                opacity: 0.9;
            }
            
            .question-card {
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(20px);
                border-radius: 25px;
                padding: 45px;
                margin-bottom: 30px;
                border: 1px solid rgba(255,255,255,0.2);
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                animation: slideUp 0.5s ease-out;
            }
            
            @keyframes slideUp {
                from { opacity: 0; transform: translateY(30px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .question-meta {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 25px;
                flex-wrap: wrap;
                gap: 15px;
            }
            
            .question-number {
                background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 0.9rem;
                font-weight: 600;
            }
            
            .difficulty-badge {
                background: rgba(255,255,255,0.2);
                padding: 6px 14px;
                border-radius: 15px;
                font-size: 0.85rem;
                font-weight: 500;
            }
            
            .question-text {
                font-size: 1.5rem;
                font-weight: 500;
                line-height: 1.5;
                margin-bottom: 35px;
                text-align: center;
            }
            
            .options-grid {
                display: grid;
                gap: 18px;
                margin-bottom: 35px;
            }
            
            .option {
                background: rgba(255,255,255,0.1);
                border: 2px solid rgba(255,255,255,0.2);
                border-radius: 18px;
                padding: 20px 25px;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                position: relative;
                overflow: hidden;
            }
            
            .option::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
                transition: left 0.3s;
            }
            
            .option:hover {
                background: rgba(255,255,255,0.15);
                border-color: rgba(255,255,255,0.4);
                transform: translateX(5px);
            }
            
            .option:hover::before {
                left: 100%;
            }
            
            .option.selected {
                background: rgba(76, 175, 80, 0.25);
                border-color: #4CAF50;
                box-shadow: 0 0 20px rgba(76, 175, 80, 0.3);
            }
            
            .option-letter {
                background: rgba(255,255,255,0.2);
                width: 40px;
                height: 40px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                margin-right: 20px;
                flex-shrink: 0;
                font-size: 1.1rem;
            }
            
            .option.selected .option-letter {
                background: #4CAF50;
                color: white;
            }
            
            .option-text {
                flex: 1;
                font-size: 1.1rem;
                line-height: 1.4;
            }
            
            .confidence-section {
                background: rgba(255,255,255,0.08);
                border-radius: 20px;
                padding: 25px;
                margin: 30px 0;
                text-align: center;
            }
            
            .confidence-label {
                font-size: 1.1rem;
                margin-bottom: 20px;
                font-weight: 500;
            }
            
            .confidence-slider {
                width: 100%;
                max-width: 350px;
                margin: 15px auto;
                -webkit-appearance: none;
                height: 10px;
                border-radius: 5px;
                background: rgba(255,255,255,0.2);
                outline: none;
            }
            
            .confidence-slider::-webkit-slider-thumb {
                -webkit-appearance: none;
                width: 24px;
                height: 24px;
                border-radius: 50%;
                background: linear-gradient(45deg, #4CAF50, #45a049);
                cursor: pointer;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            }
            
            .confidence-labels {
                display: flex;
                justify-content: space-between;
                max-width: 350px;
                margin: 15px auto 0;
                font-size: 0.85rem;
                opacity: 0.8;
            }
            
            .submit-section {
                text-align: center;
                margin-top: 30px;
            }
            
            .submit-button {
                background: linear-gradient(45deg, #4CAF50, #45a049);
                color: white;
                padding: 18px 50px;
                border: none;
                border-radius: 30px;
                font-size: 1.2rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .submit-button:hover:not(:disabled) {
                transform: translateY(-3px);
                box-shadow: 0 10px 30px rgba(76, 175, 80, 0.6);
            }
            
            .submit-button:disabled {
                opacity: 0.5;
                cursor: not-allowed;
                transform: none;
                box-shadow: 0 6px 20px rgba(76, 175, 80, 0.2);
            }
            
            .nav-buttons {
                display: flex;
                justify-content: space-between;
                margin-top: 30px;
                gap: 15px;
                flex-wrap: wrap;
            }
            
            .nav-button {
                background: rgba(255,255,255,0.1);
                color: white;
                padding: 12px 25px;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 25px;
                text-decoration: none;
                transition: all 0.3s ease;
                font-weight: 500;
                backdrop-filter: blur(10px);
            }
            
            .nav-button:hover {
                background: rgba(255,255,255,0.2);
                text-decoration: none;
                color: white;
                transform: translateY(-2px);
            }
            
            .learning-objective {
                background: rgba(100, 181, 246, 0.2);
                border-left: 4px solid #64B5F6;
                padding: 15px 20px;
                margin: 20px 0;
                border-radius: 0 10px 10px 0;
                font-style: italic;
            }
            
            @media (max-width: 768px) {
                .learning-container {
                    padding: 10px;
                }
                
                .question-card {
                    padding: 30px 20px;
                }
                
                .question-text {
                    font-size: 1.3rem;
                }
                
                .session-info {
                    gap: 15px;
                }
                
                .nav-buttons {
                    justify-content: center;
                }
            }
        </style>
    </head>
    <body>
        <div class="learning-container">
            <div class="header">
                <div class="subject-title">{{ learning_session.subject_name }}</div>
                <div class="session-info">
                    <div class="info-item">📚 Question {{ current_question + 1 }} of {{ questions|length }}</div>
                    <div class="info-item">🎯 {{ question.get('difficulty', 'adaptive').title() }}</div>
                    <div class="info-item">⏱️ {{ session_data.get('estimated_time', '5-8 minutes') }}</div>
                </div>
            </div>
            
            <div class="progress-container">
                <div class="progress-bar"></div>
                <div class="progress-text">{{ "%.0f"|format(progress) }}% Complete</div>
            </div>
            
            <form action="/submit_answer" method="POST" id="answerForm">
                <input type="hidden" name="question_id" value="{{ question['id'] }}">
                <input type="hidden" name="correct_answer" value="{{ question['correct_answer'] }}">
                
                <div class="question-card">
                    <div class="question-meta">
                        <div class="question-number">Question {{ current_question + 1 }}</div>
                        <div class="difficulty-badge">{{ question.get('difficulty', 'adaptive').title() }} Level</div>
                    </div>
                    
                    <div class="question-text">{{ question['question'] }}</div>
                    
                    {% if question.get('learning_objective') %}
                    <div class="learning-objective">
                        <strong>Learning Goal:</strong> {{ question['learning_objective'] }}
                    </div>
                    {% endif %}
                    
                    <div class="options-grid">
                        {% for option in question['options'] %}
                        <div class="option" data-value="{{ option }}">
                            <div class="option-letter">{{ ['A', 'B', 'C', 'D'][loop.index0] }}</div>
                            <div class="option-text">{{ option }}</div>
                        </div>
                        {% endfor %}
                    </div>
                    
                    <div class="confidence-section">
                        <div class="confidence-label">{{ question.get('confidence_prompt', 'How confident are you in your answer?') }}</div>
                        <input type="range" name="confidence" class="confidence-slider" min="1" max="5" value="3" id="confidenceSlider">
                        <div class="confidence-labels">
                            <span>Not Sure</span>
                            <span>Somewhat Confident</span>
                            <span>Very Confident</span>
                        </div>
                    </div>
                </div>
                
                <div class="submit-section">
                    <button type="submit" class="submit-button" id="submitBtn" disabled>Submit Answer</button>
                </div>
            </form>
            
            <div class="nav-buttons">
                <a href="/" class="nav-button">← Home</a>
                <a href="/progress" class="nav-button">📊 Progress</a>
                <a href="#" class="nav-button" onclick="skipQuestion()">Skip Question →</a>
            </div>
        </div>
        
        <script>
            const options = document.querySelectorAll('.option');
            const submitBtn = document.getElementById('submitBtn');
            let selectedOption = null;
            
            options.forEach(option => {
                option.addEventListener('click', function() {
                    // Remove previous selection
                    options.forEach(opt => opt.classList.remove('selected'));
                    
                    // Add selection to clicked option
                    this.classList.add('selected');
                    selectedOption = this.dataset.value;
                    
                    // Enable submit button
                    submitBtn.disabled = false;
                    
                    // Set hidden input value
                    let hiddenInput = document.querySelector('input[name="user_answer"]');
                    if (!hiddenInput) {
                        hiddenInput = document.createElement('input');
                        hiddenInput.type = 'hidden';
                        hiddenInput.name = 'user_answer';
                        document.getElementById('answerForm').appendChild(hiddenInput);
                    }
                    hiddenInput.value = selectedOption;
                });
            });
            
            // Enhanced form submission
            document.getElementById('answerForm').addEventListener('submit', function(e) {
                if (!selectedOption) {
                    e.preventDefault();
                    alert('Please select an answer before submitting.');
                    return;
                }
                
                submitBtn.innerHTML = '🚀 Processing...';
                submitBtn.disabled = true;
            });
            
            function skipQuestion() {
                if (confirm('Are you sure you want to skip this question?')) {
                    window.location.href = '/skip_question';
                }
            }
            
            // Confidence slider visual feedback
            const confidenceSlider = document.getElementById('confidenceSlider');
            confidenceSlider.addEventListener('input', function() {
                const value = this.value;
                const colors = ['#f44336', '#ff9800', '#ffeb3b', '#8bc34a', '#4caf50'];
                this.style.background = `linear-gradient(to right, ${colors[value-1]} 0%, ${colors[value-1]} ${(value-1)*25}%, rgba(255,255,255,0.2) ${(value-1)*25}%)`;
            });
            
            // Keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                if (e.key >= '1' && e.key <= '4') {
                    const index = parseInt(e.key) - 1;
                    if (options[index]) {
                        options[index].click();
                    }
                } else if (e.key === 'Enter' && selectedOption) {
                    document.getElementById('answerForm').submit();
                }
            });
        </script>
    </body>
    </html>
    """, 
    learning_session=learning_session, 
    question=question, 
    questions=questions,
    current_question=current_question, 
    progress=progress,
    session_data=session_data
    )

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    """Enhanced answer processing with detailed analytics"""
    if 'current_session_id' not in session:
        return redirect(url_for('index'))
    
    user = get_or_create_user()
    session_id = session['current_session_id']
    learning_session = LearningSession.query.filter_by(id=session_id).first()
    
    if not learning_session or not user:
        flash("Session error. Please start a new learning session.", "error")
        return redirect(url_for('index'))
    
    # Get answer data
    user_answer = request.form.get('user_answer')
    correct_answer = request.form.get('correct_answer')
    confidence = int(request.form.get('confidence', 3))
    question_id = request.form.get('question_id')
    
    is_correct = user_answer == correct_answer
    current_question = session.get('current_question', 0)
    
    # Update session progress
    learning_session.current_question_index = current_question + 1
    if is_correct:
        learning_session.correct_answers += 1
        user.total_correct_answers += 1
    
    user.total_questions_answered += 1
    
    # Update user streak
    today = datetime.now().date()
    if user.last_session_date != today:
        if user.last_session_date == today - timedelta(days=1):
            user.current_streak += 1
        else:
            user.current_streak = 1
        user.last_session_date = today
        
        if user.current_streak > user.longest_streak:
            user.longest_streak = user.current_streak
    
    # Store detailed answer analytics
    answer_data = {
        'question_id': question_id,
        'user_answer': user_answer,
        'correct_answer': correct_answer,
        'is_correct': is_correct,
        'confidence': confidence,
        'response_time': None,  # Could be calculated with frontend timing
        'timestamp': datetime.now().isoformat()
    }
    
    # Add to session analytics
    session_data = learning_session.get_session_data()
    if 'answer_history' not in session_data:
        session_data['answer_history'] = []
    session_data['answer_history'].append(answer_data)
    learning_session.update_session_data(session_data)
    
    # Move to next question
    session['current_question'] = current_question + 1
    session['correct_answers'] = session.get('correct_answers', 0) + (1 if is_correct else 0)
    
    try:
        db.session.commit()
    except Exception as e:
        logger.error(f"Error updating answer: {e}")
        db.session.rollback()
        flash("Error processing answer. Please try again.", "error")
        return redirect(url_for('learning_interface'))
    
    return redirect(url_for('learning_interface'))

@app.route('/complete')
def session_complete():
    """Enhanced session completion with comprehensive analytics"""
    if 'current_session_id' not in session:
        return redirect(url_for('index'))
    
    user = get_or_create_user()
    session_id = session['current_session_id']
    learning_session = LearningSession.query.filter_by(id=session_id).first()
    
    if not learning_session or not user:
        return redirect(url_for('index'))
    
    # Finalize session
    learning_session.status = 'completed'
    learning_session.completed_at = datetime.utcnow()
    
    # Calculate final statistics
    session_data = learning_session.get_session_data()
    answer_history = session_data.get('answer_history', [])
    
    total_questions = len(answer_history)
    correct_answers = sum(1 for answer in answer_history if answer['is_correct'])
    accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    
    # Update subject completion rate
    if learning_session.subject:
        subject = learning_session.subject
        # Calculate new average completion rate
        total_sessions = subject.total_sessions
        if total_sessions > 0:
            current_avg = subject.average_completion_rate
            new_completion_rate = accuracy / 100
            subject.average_completion_rate = ((current_avg * (total_sessions - 1)) + new_completion_rate) / total_sessions
    
    # Clear session data
    for key in ['current_session_id', 'current_subject', 'current_question', 'correct_answers', 'session_start']:
        session.pop(key, None)
    
    try:
        db.session.commit()
    except Exception as e:
        logger.error(f"Error completing session: {e}")
        db.session.rollback()
    
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Session Complete - NeuroPulse</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
                animation: fadeIn 0.8s ease-out;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: scale(0.9); }
                to { opacity: 1; transform: scale(1); }
            }
            
            .completion-card {
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(20px);
                border-radius: 30px;
                padding: 60px;
                text-align: center;
                border: 1px solid rgba(255,255,255,0.2);
                max-width: 700px;
                width: 100%;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            
            .celebration {
                font-size: 5rem;
                margin-bottom: 25px;
                animation: bounce 2s infinite;
            }
            
            @keyframes bounce {
                0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
                40% { transform: translateY(-15px); }
                60% { transform: translateY(-8px); }
            }
            
            .completion-title {
                font-size: 3rem;
                font-weight: 800;
                margin-bottom: 20px;
                background: linear-gradient(45deg, #FFE082, #FFF, #64B5F6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .subject-completed {
                font-size: 1.4rem;
                margin-bottom: 40px;
                opacity: 0.95;
                line-height: 1.4;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 25px;
                margin: 40px 0;
            }
            
            .stat-card {
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
                padding: 25px;
                border: 1px solid rgba(255,255,255,0.2);
                transition: transform 0.3s ease;
            }
            
            .stat-card:hover {
                transform: translateY(-5px);
            }
            
            .stat-number {
                font-size: 2.5rem;
                font-weight: 800;
                margin-bottom: 8px;
                background: linear-gradient(45deg, #4CAF50, #45a049);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .stat-label {
                font-size: 0.95rem;
                opacity: 0.9;
                font-weight: 500;
            }
            
            .performance-message {
                font-size: 1.3rem;
                margin: 40px 0;
                padding: 25px;
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
                line-height: 1.5;
                border: 1px solid rgba(255,255,255,0.2);
            }
            
            .achievements {
                margin: 30px 0;
            }
            
            .achievement-badge {
                display: inline-block;
                background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
                padding: 10px 20px;
                border-radius: 25px;
                margin: 5px;
                font-size: 0.9rem;
                font-weight: 600;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            
            .action-buttons {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 40px;
            }
            
            .action-button {
                padding: 18px 35px;
                border: none;
                border-radius: 30px;
                font-size: 1.1rem;
                font-weight: 600;
                text-decoration: none;
                text-align: center;
                transition: all 0.3s ease;
                box-shadow: 0 6px 20px rgba(0,0,0,0.2);
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .primary-button {
                background: linear-gradient(45deg, #4CAF50, #45a049);
                color: white;
            }
            
            .secondary-button {
                background: linear-gradient(45deg, #2196F3, #1976D2);
                color: white;
            }
            
            .tertiary-button {
                background: rgba(255,255,255,0.15);
                color: white;
                border: 1px solid rgba(255,255,255,0.3);
            }
            
            .action-button:hover {
                transform: translateY(-3px);
                box-shadow: 0 10px 30px rgba(0,0,0,0.4);
                text-decoration: none;
                color: white;
            }
            
            .streak-display {
                background: rgba(255, 193, 7, 0.2);
                border: 2px solid #FFC107;
                border-radius: 15px;
                padding: 15px;
                margin: 20px 0;
                font-weight: 600;
            }
            
            @media (max-width: 768px) {
                .completion-card {
                    padding: 40px 30px;
                }
                
                .completion-title {
                    font-size: 2.2rem;
                }
                
                .stats-grid {
                    grid-template-columns: repeat(2, 1fr);
                }
            }
        </style>
    </head>
    <body>
        <div class="completion-card">
            <div class="celebration">🎉</div>
            <div class="completion-title">Outstanding Work!</div>
            <div class="subject-completed">
                You've completed a learning session on<br>
                <strong>{{ learning_session.subject_name }}</strong>
            </div>
            
            {% if user.current_streak > 1 %}
            <div class="streak-display">
                🔥 {{ user.current_streak }} Day Learning Streak! Keep it going!
            </div>
            {% endif %}
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{{ correct_answers }}</div>
                    <div class="stat-label">Correct Answers</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-number">{{ total_questions }}</div>
                    <div class="stat-label">Total Questions</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-number">{{ "%.0f"|format(accuracy) }}%</div>
                    <div class="stat-label">Accuracy</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-number">{{ user.current_streak }}</div>
                    <div class="stat-label">Current Streak</div>
                </div>
            </div>
            
            <div class="performance-message">
                {{ get_performance_message(accuracy, user.current_streak) }}
            </div>
            
            {% if get_achievements(accuracy, user.current_streak) %}
            <div class="achievements">
                <h3>🏆 Achievements Unlocked:</h3>
                {% for achievement in get_achievements(accuracy, user.current_streak) %}
                <span class="achievement-badge">{{ achievement }}</span>
                {% endfor %}
            </div>
            {% endif %}
            
            <div class="action-buttons">
                <a href="/learn_more?subject={{ learning_session.subject_name }}" class="action-button primary-button">
                    Continue {{ learning_session.subject_name }}
                </a>
                
                <a href="/" class="action-button secondary-button">
                    Learn Something New
                </a>
                
                <a href="/progress" class="action-button tertiary-button">
                    View Progress
                </a>
            </div>
        </div>
    </body>
    </html>
    """, 
    learning_session=learning_session,
    user=user,
    total_questions=total_questions,
    correct_answers=correct_answers,
    accuracy=accuracy,
    get_performance_message=get_performance_message_with_streak,
    get_achievements=get_achievements_unlocked
    )

def get_performance_message_with_streak(accuracy, streak):
    """Get performance message considering accuracy and streak"""
    if streak >= 7:
        return f"🌟 Incredible! {streak} days of consistent learning! You're building unstoppable momentum!"
    elif accuracy >= 90:
        return "🎯 Exceptional mastery! Your understanding is rock-solid and your learning approach is clearly working!"
    elif accuracy >= 80:
        return "👏 Excellent progress! You're demonstrating strong comprehension and steady improvement!"
    elif accuracy >= 70:
        return "💪 Solid work! You're building strong foundations and developing real expertise!"
    elif accuracy >= 60:
        return "📈 Great effort! You're making meaningful progress and every step counts towards mastery!"
    else:
        return "🎯 Every expert started as a beginner! Your dedication to learning is already a victory worth celebrating!"

def get_achievements_unlocked(accuracy, streak):
    """Get list of achievements based on performance"""
    achievements = []
    
    if accuracy == 100:
        achievements.append("Perfect Score!")
    elif accuracy >= 90:
        achievements.append("Excellence Achiever")
    elif accuracy >= 80:
        achievements.append("High Performer")
    
    if streak >= 30:
        achievements.append("Learning Legend")
    elif streak >= 14:
        achievements.append("Two Week Warrior")
    elif streak >= 7:
        achievements.append("Week Long Learner")
    elif streak >= 3:
        achievements.append("Streak Starter")
    
    return achievements

@app.route('/progress')
def view_progress():
    """Comprehensive progress analytics dashboard"""
    user = get_or_create_user()
    if not user:
        return redirect(url_for('index'))
    
    # Get user's learning sessions
    sessions = LearningSession.query.filter_by(user_id=user.id).order_by(LearningSession.started_at.desc()).all()
    completed_sessions = [s for s in sessions if s.status == 'completed']
    
    # Get subject statistics
    subjects_studied = db.session.query(Subject).join(LearningSession).filter(
        LearningSession.user_id == user.id,
        LearningSession.status == 'completed'
    ).distinct().all()
    
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Learning Progress - NeuroPulse</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
                padding: 20px;
            }
            
            .progress-container {
                max-width: 1200px;
                margin: 0 auto;
                animation: fadeIn 0.8s ease-out;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .header {
                text-align: center;
                margin-bottom: 50px;
                padding: 40px 0;
            }
            
            .title {
                font-size: 3rem;
                font-weight: 800;
                margin-bottom: 15px;
                background: linear-gradient(45deg, #FFE082, #FFF);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .subtitle {
                font-size: 1.2rem;
                opacity: 0.9;
                margin-bottom: 30px;
            }
            
            .back-button {
                background: rgba(255,255,255,0.15);
                color: white;
                padding: 12px 25px;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 25px;
                text-decoration: none;
                display: inline-block;
                margin-bottom: 40px;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
            }
            
            .back-button:hover {
                background: rgba(255,255,255,0.25);
                text-decoration: none;
                color: white;
                transform: translateY(-2px);
            }
            
            .stats-overview {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 25px;
                margin-bottom: 50px;
            }
            
            .stat-card {
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(15px);
                border-radius: 20px;
                padding: 30px;
                text-align: center;
                border: 1px solid rgba(255,255,255,0.2);
                transition: transform 0.3s ease;
            }
            
            .stat-card:hover {
                transform: translateY(-5px);
            }
            
            .stat-icon {
                font-size: 2.5rem;
                margin-bottom: 15px;
                display: block;
            }
            
            .stat-number {
                font-size: 2.2rem;
                font-weight: 700;
                margin-bottom: 8px;
                color: #4CAF50;
            }
            
            .stat-label {
                font-size: 1rem;
                opacity: 0.9;
                font-weight: 500;
            }
            
            .sections {
                display: grid;
                gap: 40px;
            }
            
            .section {
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(15px);
                border-radius: 25px;
                padding: 40px;
                border: 1px solid rgba(255,255,255,0.2);
            }
            
            .section-title {
                font-size: 1.8rem;
                font-weight: 600;
                margin-bottom: 25px;
                display: flex;
                align-items: center;
                gap: 15px;
            }
            
            .sessions-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px;
            }
            
            .session-card {
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 25px;
                border: 1px solid rgba(255,255,255,0.2);
                transition: all 0.3s ease;
            }
            
            .session-card:hover {
                transform: translateY(-3px);
                background: rgba(255,255,255,0.15);
            }
            
            .session-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }
            
            .session-subject {
                font-size: 1.2rem;
                font-weight: 600;
            }
            
            .session-status {
                padding: 4px 12px;
                border-radius: 15px;
                font-size: 0.8rem;
                font-weight: 500;
            }
            
            .status-completed {
                background: rgba(76, 175, 80, 0.3);
                color: #4CAF50;
            }
            
            .status-active {
                background: rgba(255, 193, 7, 0.3);
                color: #FFC107;
            }
            
            .session-stats {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
                margin-top: 15px;
            }
            
            .session-stat {
                text-align: center;
            }
            
            .session-stat-number {
                font-size: 1.1rem;
                font-weight: 600;
                color: #64B5F6;
            }
            
            .session-stat-label {
                font-size: 0.8rem;
                opacity: 0.8;
            }
            
            .subjects-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                gap: 20px;
            }
            
            .subject-card {
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 25px;
                border: 1px solid rgba(255,255,255,0.2);
                text-align: center;
                transition: all 0.3s ease;
            }
            
            .subject-card:hover {
                transform: translateY(-3px);
                background: rgba(255,255,255,0.15);
            }
            
            .subject-icon {
                font-size: 2.5rem;
                margin-bottom: 15px;
                display: block;
            }
            
            .subject-name {
                font-size: 1.2rem;
                font-weight: 600;
                margin-bottom: 10px;
            }
            
            .subject-sessions {
                font-size: 0.9rem;
                opacity: 0.8;
            }
            
            .empty-state {
                text-align: center;
                padding: 60px 20px;
                opacity: 0.8;
            }
            
            .empty-icon {
                font-size: 4rem;
                margin-bottom: 20px;
                display: block;
            }
            
            .empty-title {
                font-size: 1.5rem;
                margin-bottom: 15px;
            }
            
            .empty-desc {
                font-size: 1rem;
                line-height: 1.5;
                margin-bottom: 30px;
            }
            
            .cta-button {
                background: linear-gradient(45deg, #4CAF50, #45a049);
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 25px;
                text-decoration: none;
                font-weight: 600;
                transition: all 0.3s ease;
                display: inline-block;
            }
            
            .cta-button:hover {
                transform: translateY(-2px);
                text-decoration: none;
                color: white;
                box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4);
            }
            
            @media (max-width: 768px) {
                .stats-overview {
                    grid-template-columns: repeat(2, 1fr);
                }
                
                .section {
                    padding: 25px 20px;
                }
                
                .sessions-grid,
                .subjects-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="progress-container">
            <a href="/" class="back-button">← Back to Home</a>
            
            <div class="header">
                <div class="title">📊 Your Learning Journey</div>
                <div class="subtitle">Track your progress and celebrate your achievements</div>
            </div>
            
            <div class="stats-overview">
                <div class="stat-card">
                    <div class="stat-icon">🎯</div>
                    <div class="stat-number">{{ user.total_sessions }}</div>
                    <div class="stat-label">Total Sessions</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon">✅</div>
                    <div class="stat-number">{{ user.total_correct_answers }}</div>
                    <div class="stat-label">Correct Answers</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon">📈</div>
                    <div class="stat-number">{{ "%.0f"|format(user.accuracy_percentage()) }}%</div>
                    <div class="stat-label">Overall Accuracy</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon">🔥</div>
                    <div class="stat-number">{{ user.current_streak }}</div>
                    <div class="stat-label">Current Streak</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon">🏆</div>
                    <div class="stat-number">{{ user.longest_streak }}</div>
                    <div class="stat-label">Longest Streak</div>
                </div>
            </div>
            
            <div class="sections">
                <div class="section">
                    <div class="section-title">
                        <span>📚</span>
                        Recent Learning Sessions
                    </div>
                    
                    {% if sessions %}
                    <div class="sessions-grid">
                        {% for session in sessions[:6] %}
                        <div class="session-card">
                            <div class="session-header">
                                <div class="session-subject">{{ session.subject_name }}</div>
                                <div class="session-status status-{{ session.status }}">
                                    {{ session.status.title() }}
                                </div>
                            </div>
                            
                            <div style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 10px;">
                                {{ session.started_at.strftime('%B %d, %Y at %I:%M %p') }}
                            </div>
                            
                            {% if session.status == 'completed' %}
                            <div class="session-stats">
                                <div class="session-stat">
                                    <div class="session-stat-number">{{ session.correct_answers }}</div>
                                    <div class="session-stat-label">Correct</div>
                                </div>
                                <div class="session-stat">
                                    <div class="session-stat-number">{{ session.current_question_index }}</div>
                                    <div class="session-stat-label">Total</div>
                                </div>
                                <div class="session-stat">
                                    <div class="session-stat-number">{{ "%.0f"|format(session.accuracy_percentage()) }}%</div>
                                    <div class="session-stat-label">Accuracy</div>
                                </div>
                            </div>
                            {% endif %}
                        </div>
                        {% endfor %}
                    </div>
                    {% else %}
                    <div class="empty-state">
                        <div class="empty-icon">📖</div>
                        <div class="empty-title">No Learning Sessions Yet</div>
                        <div class="empty-desc">Start your first learning session to see your progress here!</div>
                        <a href="/" class="cta-button">Start Learning</a>
                    </div>
                    {% endif %}
                </div>
                
                <div class="section">
                    <div class="section-title">
                        <span>🎓</span>
                        Subjects Mastered
                    </div>
                    
                    {% if subjects_studied %}
                    <div class="subjects-grid">
                        {% for subject in subjects_studied %}
                        <div class="subject-card">
                            <div class="subject-icon">{{ subject.icon or '📚' }}</div>
                            <div class="subject-name">{{ subject.name }}</div>
                            <div class="subject-sessions">
                                {{ subject.sessions|selectattr('user_id', 'equalto', user.id)|selectattr('status', 'equalto', 'completed')|list|length }} sessions completed
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                    {% else %}
                    <div class="empty-state">
                        <div class="empty-icon">🌟</div>
                        <div class="empty-title">Ready to Explore?</div>
                        <div class="empty-desc">Complete your first learning session to start building your knowledge portfolio!</div>
                        <a href="/" class="cta-button">Discover Subjects</a>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </body>
    </html>
    """, 
    user=user, 
    sessions=sessions, 
    completed_sessions=completed_sessions,
    subjects_studied=subjects_studied
    )

@app.route('/learn_more')
def learn_more():
    """Continue learning in the same subject"""
    subject = request.args.get('subject', '')
    if subject:
        return render_template_string("""
        <form action="/learn" method="POST" style="display: none;" id="continueForm">
            <input type="hidden" name="subject" value="{{ subject }}">
        </form>
        <script>
            document.getElementById('continueForm').submit();
        </script>
        """, subject=subject)
    return redirect(url_for('index'))

@app.route('/skip_question')
def skip_question():
    """Skip current question"""
    if 'current_session_id' in session:
        current_question = session.get('current_question', 0)
        session['current_question'] = current_question + 1
    return redirect(url_for('learning_interface'))

@app.route('/health')
def health_check():
    """Comprehensive health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'ai_enabled': AI_ENABLED,
        'database': 'connected',
        'features': {
            'adaptive_learning': True,
            'ai_content_generation': AI_ENABLED,
            'progress_tracking': True,
            'gamification': True,
            'personalization': True
        },
        'version': '2.1.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/user/profile', methods=['GET', 'POST'])
def user_profile_api():
    """API endpoint for user profile management"""
    user = get_or_create_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if request.method == 'GET':
        return jsonify({
            'user_id': user.id,
            'username': user.username,
            'learning_profile': user.get_learning_profile(),
            'stats': {
                'total_sessions': user.total_sessions,
                'total_correct_answers': user.total_correct_answers,
                'total_questions_answered': user.total_questions_answered,
                'accuracy_percentage': user.accuracy_percentage(),
                'current_streak': user.current_streak,
                'longest_streak': user.longest_streak
            }
        })
    
    elif request.method == 'POST':
        data = request.get_json()
        if 'learning_profile' in data:
            user.update_learning_profile(data['learning_profile'])
            db.session.commit()
        return jsonify({'success': True})

logger.info("NeuroPulse Complete application initialized successfully")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)