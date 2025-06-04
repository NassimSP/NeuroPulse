"""
NeuroPulse - Universal Adaptive Learning Platform
AI-powered microlearning for any subject, optimized for ADHD minds
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
import json
import uuid
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///neuropulse.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    'pool_pre_ping': True,
    "pool_recycle": 300,
}

# Initialize database
db = SQLAlchemy(app, model_class=Base)

# Initialize OpenAI
try:
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    AI_ENABLED = True
    logger.info("OpenAI integration enabled")
except Exception as e:
    logger.warning(f"OpenAI not available: {e}")
    AI_ENABLED = False
    openai_client = None

# Database Models
class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    learning_profile = db.Column(db.Text, nullable=True)  # JSON
    preferences = db.Column(db.Text, nullable=True)  # JSON
    progress_data = db.Column(db.Text, nullable=True)  # JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)

class LearningSession(db.Model):
    __tablename__ = 'learning_sessions'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    session_data = db.Column(db.Text, nullable=False)  # JSON
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

class GeneratedContent(db.Model):
    __tablename__ = 'generated_content'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.String(36), primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    difficulty_level = db.Column(db.String(20), nullable=False)
    content_type = db.Column(db.String(30), nullable=False)
    content_data = db.Column(db.Text, nullable=False)  # JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create tables
with app.app_context():
    try:
        db.create_all()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database warning: {e}")

# Utility Functions
def get_user_id():
    """Get or create user session and database record"""
    if 'user_id' not in session:
        session['user_id'] = f"user_{uuid.uuid4().hex[:8]}"
        session['username'] = f"Learner_{session['user_id'][-4:]}"
        
        # Create user in database if doesn't exist
        user_id = session['user_id']
        username = session['username']
        
        existing_user = User.query.filter_by(id=user_id).first()
        if not existing_user:
            try:
                new_user = User()
                new_user.id = user_id
                new_user.username = username
                new_user.learning_profile = '{}'
                new_user.preferences = '{}'
                new_user.progress_data = '{}'
                
                db.session.add(new_user)
                db.session.commit()
                logger.info(f"Created new user: {user_id}")
            except Exception as e:
                logger.error(f"Error creating user: {e}")
                db.session.rollback()
    
    return session['user_id']

def generate_learning_content(subject, difficulty="intermediate", content_type="quiz"):
    """Generate dynamic learning content using AI"""
    if not AI_ENABLED:
        return get_fallback_content(subject, difficulty, content_type)
    
    try:
        # Create comprehensive prompt for AI content generation
        prompt = f"""
        Create engaging, interactive learning content for: {subject}
        Difficulty level: {difficulty}
        Content type: {content_type}
        
        Generate 5 questions with the following structure:
        1. Each question should be educational and progressive
        2. Include multiple choice options (4 choices each)
        3. Provide detailed explanations for correct answers
        4. Add confidence tracking elements
        5. Include interactive elements where applicable
        
        Return as JSON with this structure:
        {{
            "subject": "{subject}",
            "difficulty": "{difficulty}",
            "questions": [
                {{
                    "id": 1,
                    "question": "Question text",
                    "type": "multiple_choice",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "explanation": "Detailed explanation",
                    "learning_objective": "What this teaches",
                    "confidence_prompt": "How confident are you?",
                    "interactive_element": "drag_drop|diagram|timer|none"
                }}
            ],
            "learning_path": "Next suggested topics",
            "estimated_time": "5-8 minutes"
        }}
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # Latest OpenAI model
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert educational content creator specializing in neurodivergent-friendly learning experiences. Create engaging, bite-sized learning content optimized for ADHD minds."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        content = json.loads(response.choices[0].message.content)
        
        # Store generated content
        try:
            content_id = str(uuid.uuid4())
            generated_content = GeneratedContent()
            generated_content.id = content_id
            generated_content.subject = subject
            generated_content.difficulty_level = difficulty
            generated_content.content_type = content_type
            generated_content.content_data = json.dumps(content)
            
            db.session.add(generated_content)
            db.session.commit()
        except Exception as e:
            logger.warning(f"Could not store generated content: {e}")
            db.session.rollback()
        
        return content
        
    except Exception as e:
        logger.error(f"AI content generation error: {e}")
        return get_fallback_content(subject, difficulty, content_type)

def get_fallback_content(subject, difficulty, content_type):
    """Fallback content when AI is not available"""
    return {
        "subject": subject,
        "difficulty": difficulty,
        "questions": [
            {
                "id": 1,
                "question": f"What would you like to learn about {subject}?",
                "type": "multiple_choice",
                "options": [
                    f"Basic concepts of {subject}",
                    f"Advanced topics in {subject}",
                    f"Practical applications of {subject}",
                    f"Real-world examples of {subject}"
                ],
                "correct_answer": "Basic concepts",
                "explanation": f"Starting with fundamentals is key to mastering {subject}",
                "learning_objective": f"Introduction to {subject} concepts",
                "confidence_prompt": "How confident do you feel about this topic?",
                "interactive_element": "none"
            }
        ],
        "learning_path": f"Continue exploring {subject}",
        "estimated_time": "5 minutes"
    }

# Routes
@app.route('/')
def index():
    """Main dashboard - Subject selection and personalization"""
    user_id = get_user_id()
    username = session.get('username', 'Learner')
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NeuroPulse - Learn Anything</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 40px;
                padding: 40px 0;
            }}
            
            .logo {{
                font-size: 3rem;
                font-weight: 700;
                margin-bottom: 10px;
                background: linear-gradient(45deg, #FFE082, #FFF);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .tagline {{
                font-size: 1.2rem;
                opacity: 0.9;
                margin-bottom: 20px;
            }}
            
            .welcome {{
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 40px;
                border: 1px solid rgba(255,255,255,0.2);
            }}
            
            .subject-input {{
                text-align: center;
                margin-bottom: 40px;
            }}
            
            .subject-input input {{
                width: 100%;
                max-width: 500px;
                padding: 20px;
                font-size: 1.1rem;
                border: none;
                border-radius: 15px;
                background: rgba(255,255,255,0.9);
                color: #333;
                margin-bottom: 20px;
            }}
            
            .start-button {{
                background: linear-gradient(45deg, #4CAF50, #45a049);
                color: white;
                padding: 15px 40px;
                border: none;
                border-radius: 25px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }}
            
            .start-button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.3);
            }}
            
            .examples {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 40px;
            }}
            
            .example-card {{
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 25px;
                border: 1px solid rgba(255,255,255,0.2);
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            
            .example-card:hover {{
                transform: translateY(-5px);
                background: rgba(255,255,255,0.15);
            }}
            
            .example-icon {{
                font-size: 3rem;
                margin-bottom: 15px;
            }}
            
            .example-title {{
                font-size: 1.3rem;
                font-weight: 600;
                margin-bottom: 10px;
            }}
            
            .example-desc {{
                opacity: 0.8;
                line-height: 1.5;
            }}
            
            .features {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 40px;
            }}
            
            .feature {{
                text-align: center;
                padding: 20px;
            }}
            
            .feature-icon {{
                font-size: 2rem;
                margin-bottom: 10px;
            }}
            
            .ai-badge {{
                display: inline-block;
                background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.9rem;
                font-weight: 600;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">🧠 NeuroPulse</div>
                <div class="tagline">Learn Anything, Remember Everything, Love Every Minute</div>
                <div class="ai-badge">{"✨ AI-Powered" if AI_ENABLED else "🔧 Core Features"}</div>
            </div>
            
            <div class="welcome">
                <h2>Welcome back, {username}!</h2>
                <p>What would you like to learn today? From quantum physics to plumbing, from Excel to electrical engineering - I'll create a personalized learning experience just for you.</p>
            </div>
            
            <div class="subject-input">
                <form action="/learn" method="POST">
                    <input type="text" name="subject" placeholder="Type any subject you want to learn (e.g., 'Python programming', 'Italian cooking', 'financial planning')" required>
                    <br>
                    <button type="submit" class="start-button">Start Learning Journey</button>
                </form>
            </div>
            
            <div class="examples">
                <div class="example-card" onclick="startSubject('Data Analysis')">
                    <div class="example-icon">📊</div>
                    <div class="example-title">Data Analysis</div>
                    <div class="example-desc">Master Excel, Python, and visualization techniques with interactive exercises</div>
                </div>
                
                <div class="example-card" onclick="startSubject('Electrical Engineering')">
                    <div class="example-icon">⚡</div>
                    <div class="example-title">Electrical Engineering</div>
                    <div class="example-desc">Wire virtual circuits, solve challenges, and master electrical concepts</div>
                </div>
                
                <div class="example-card" onclick="startSubject('Italian Language')">
                    <div class="example-icon">🇮🇹</div>
                    <div class="example-title">Language Learning</div>
                    <div class="example-desc">Interactive conversations, grammar puzzles, and cultural immersion</div>
                </div>
                
                <div class="example-card" onclick="startSubject('Financial Planning')">
                    <div class="example-icon">💰</div>
                    <div class="example-title">Financial Planning</div>
                    <div class="example-desc">Budgeting, investing, and wealth-building strategies made simple</div>
                </div>
                
                <div class="example-card" onclick="startSubject('Chemistry')">
                    <div class="example-icon">🧪</div>
                    <div class="example-title">Chemistry</div>
                    <div class="example-desc">Build molecules, balance equations, and explore chemical reactions</div>
                </div>
                
                <div class="example-card" onclick="startSubject('Creative Writing')">
                    <div class="example-icon">✍️</div>
                    <div class="example-title">Creative Writing</div>
                    <div class="example-desc">Storytelling techniques, character development, and narrative structure</div>
                </div>
            </div>
            
            <div class="features">
                <div class="feature">
                    <div class="feature-icon">🎯</div>
                    <h3>Adaptive Learning</h3>
                    <p>AI adjusts to your pace and learning style</p>
                </div>
                
                <div class="feature">
                    <div class="feature-icon">⏱️</div>
                    <h3>5-10 Minute Sessions</h3>
                    <p>Perfect for ADHD minds and busy schedules</p>
                </div>
                
                <div class="feature">
                    <div class="feature-icon">🎮</div>
                    <h3>Gamified Experience</h3>
                    <p>Streaks, achievements, and dopamine rewards</p>
                </div>
                
                <div class="feature">
                    <div class="feature-icon">🧠</div>
                    <h3>Neurodivergent Friendly</h3>
                    <p>Designed for ADHD, dyslexia, and learning differences</p>
                </div>
            </div>
        </div>
        
        <script>
            function startSubject(subject) {{
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
            }}
        </script>
    </body>
    </html>
    """

@app.route('/learn', methods=['POST'])
def start_learning():
    """Initialize learning session for chosen subject"""
    user_id = get_user_id()
    subject = request.form.get('subject', '').strip()
    
    if not subject:
        return redirect(url_for('index'))
    
    # Create new learning session
    session_id = str(uuid.uuid4())
    session['current_session_id'] = session_id
    session['current_subject'] = subject
    session['current_question'] = 0
    session['correct_answers'] = 0
    session['session_start'] = datetime.now().isoformat()
    
    # Generate initial content
    content = generate_learning_content(subject, "beginner", "quiz")
    
    # Store session in database
    learning_session = LearningSession()
    learning_session.id = session_id
    learning_session.user_id = user_id
    learning_session.subject = subject
    learning_session.session_data = json.dumps({
        'content': content,
        'progress': {'current_question': 0, 'total_questions': len(content['questions'])}
    })
    
    db.session.add(learning_session)
    db.session.commit()
    
    return redirect(url_for('learning_interface'))

@app.route('/interface', methods=['GET', 'POST'])
def learning_interface():
    """Main learning interface"""
    if 'current_session_id' not in session:
        return redirect(url_for('index'))
    
    session_id = session['current_session_id']
    subject = session['current_subject']
    current_question = session.get('current_question', 0)
    
    # Get session data
    learning_session = LearningSession.query.filter_by(id=session_id).first()
    if not learning_session:
        return redirect(url_for('index'))
    
    session_data = json.loads(learning_session.session_data)
    content = session_data['content']
    questions = content['questions']
    
    if current_question >= len(questions):
        return redirect(url_for('session_complete'))
    
    question = questions[current_question]
    progress = ((current_question + 1) / len(questions)) * 100
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Learning: {subject} - NeuroPulse</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
                padding: 20px;
            }}
            
            .learning-container {{
                max-width: 800px;
                margin: 0 auto;
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            
            .subject-title {{
                font-size: 1.8rem;
                font-weight: 600;
                margin-bottom: 10px;
                background: linear-gradient(45deg, #FFE082, #FFF);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .progress-container {{
                background: rgba(255,255,255,0.2);
                border-radius: 10px;
                padding: 4px;
                margin-bottom: 30px;
            }}
            
            .progress-bar {{
                background: linear-gradient(45deg, #4CAF50, #45a049);
                height: 8px;
                border-radius: 6px;
                width: {progress}%;
                transition: width 0.3s ease;
            }}
            
            .progress-text {{
                text-align: center;
                margin-top: 10px;
                font-size: 0.9rem;
                opacity: 0.8;
            }}
            
            .question-card {{
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                margin-bottom: 30px;
                border: 1px solid rgba(255,255,255,0.2);
            }}
            
            .question-number {{
                font-size: 0.9rem;
                opacity: 0.7;
                margin-bottom: 15px;
            }}
            
            .question-text {{
                font-size: 1.4rem;
                font-weight: 500;
                line-height: 1.4;
                margin-bottom: 30px;
            }}
            
            .options {{
                display: grid;
                gap: 15px;
            }}
            
            .option {{
                background: rgba(255,255,255,0.1);
                border: 2px solid rgba(255,255,255,0.2);
                border-radius: 15px;
                padding: 20px;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
            }}
            
            .option:hover {{
                background: rgba(255,255,255,0.2);
                border-color: rgba(255,255,255,0.4);
                transform: translateY(-2px);
            }}
            
            .option.selected {{
                background: rgba(76, 175, 80, 0.3);
                border-color: #4CAF50;
            }}
            
            .option-letter {{
                background: rgba(255,255,255,0.2);
                width: 35px;
                height: 35px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 600;
                margin-right: 15px;
                flex-shrink: 0;
            }}
            
            .option-text {{
                flex: 1;
                font-size: 1.1rem;
            }}
            
            .confidence-section {{
                margin-top: 30px;
                text-align: center;
            }}
            
            .confidence-label {{
                font-size: 1rem;
                margin-bottom: 15px;
                opacity: 0.9;
            }}
            
            .confidence-slider {{
                width: 100%;
                max-width: 300px;
                margin: 0 auto 20px;
                -webkit-appearance: none;
                height: 8px;
                border-radius: 5px;
                background: rgba(255,255,255,0.2);
                outline: none;
            }}
            
            .confidence-slider::-webkit-slider-thumb {{
                -webkit-appearance: none;
                width: 20px;
                height: 20px;
                border-radius: 50%;
                background: #4CAF50;
                cursor: pointer;
            }}
            
            .submit-button {{
                background: linear-gradient(45deg, #4CAF50, #45a049);
                color: white;
                padding: 15px 40px;
                border: none;
                border-radius: 25px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                margin-top: 20px;
            }}
            
            .submit-button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.3);
            }}
            
            .submit-button:disabled {{
                opacity: 0.5;
                cursor: not-allowed;
                transform: none;
            }}
            
            .nav-buttons {{
                display: flex;
                justify-content: space-between;
                margin-top: 20px;
            }}
            
            .nav-button {{
                background: rgba(255,255,255,0.1);
                color: white;
                padding: 10px 20px;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 20px;
                text-decoration: none;
                transition: all 0.3s ease;
            }}
            
            .nav-button:hover {{
                background: rgba(255,255,255,0.2);
                text-decoration: none;
                color: white;
            }}
        </style>
    </head>
    <body>
        <div class="learning-container">
            <div class="header">
                <div class="subject-title">{subject}</div>
            </div>
            
            <div class="progress-container">
                <div class="progress-bar"></div>
                <div class="progress-text">Question {current_question + 1} of {len(questions)}</div>
            </div>
            
            <form action="/submit_answer" method="POST">
                <input type="hidden" name="question_id" value="{question['id']}">
                <input type="hidden" name="correct_answer" value="{question['correct_answer']}">
                
                <div class="question-card">
                    <div class="question-number">Question {current_question + 1}</div>
                    <div class="question-text">{question['question']}</div>
                    
                    <div class="options">
                        {generate_option_html(question['options'])}
                    </div>
                    
                    <div class="confidence-section">
                        <div class="confidence-label">{question.get('confidence_prompt', 'How confident are you in your answer?')}</div>
                        <input type="range" name="confidence" class="confidence-slider" min="1" max="5" value="3">
                        <div style="display: flex; justify-content: space-between; max-width: 300px; margin: 0 auto; font-size: 0.8rem; opacity: 0.7;">
                            <span>Not Sure</span>
                            <span>Very Confident</span>
                        </div>
                    </div>
                </div>
                
                <div style="text-align: center;">
                    <button type="submit" class="submit-button" id="submitBtn" disabled>Submit Answer</button>
                </div>
            </form>
            
            <div class="nav-buttons">
                <a href="/" class="nav-button">← Home</a>
                <a href="/skip_question" class="nav-button">Skip Question →</a>
            </div>
        </div>
        
        <script>
            const options = document.querySelectorAll('.option');
            const submitBtn = document.getElementById('submitBtn');
            let selectedOption = null;
            
            options.forEach(option => {{
                option.addEventListener('click', function() {{
                    // Remove previous selection
                    options.forEach(opt => opt.classList.remove('selected'));
                    
                    // Add selection to clicked option
                    this.classList.add('selected');
                    selectedOption = this.dataset.value;
                    
                    // Enable submit button
                    submitBtn.disabled = false;
                    
                    // Set hidden input value
                    const hiddenInput = document.querySelector('input[name="user_answer"]') || 
                                       document.createElement('input');
                    hiddenInput.type = 'hidden';
                    hiddenInput.name = 'user_answer';
                    hiddenInput.value = selectedOption;
                    document.querySelector('form').appendChild(hiddenInput);
                }});
            }});
        </script>
    </body>
    </html>
    """

def generate_option_html(options):
    """Generate HTML for answer options"""
    letters = ['A', 'B', 'C', 'D']
    html = ""
    for i, option in enumerate(options):
        letter = letters[i] if i < len(letters) else str(i+1)
        html += f"""
        <div class="option" data-value="{option}">
            <div class="option-letter">{letter}</div>
            <div class="option-text">{option}</div>
        </div>
        """
    return html

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    """Process submitted answer"""
    if 'current_session_id' not in session:
        return redirect(url_for('index'))
    
    user_answer = request.form.get('user_answer')
    correct_answer = request.form.get('correct_answer')
    confidence = int(request.form.get('confidence', 3))
    
    is_correct = user_answer == correct_answer
    
    if is_correct:
        session['correct_answers'] = session.get('correct_answers', 0) + 1
    
    # Move to next question
    session['current_question'] = session.get('current_question', 0) + 1
    
    # Store answer data
    answer_data = {
        'user_answer': user_answer,
        'correct_answer': correct_answer,
        'is_correct': is_correct,
        'confidence': confidence,
        'timestamp': datetime.now().isoformat()
    }
    
    # Add to session history
    if 'answer_history' not in session:
        session['answer_history'] = []
    session['answer_history'].append(answer_data)
    
    return redirect(url_for('learning_interface'))

@app.route('/complete')
def session_complete():
    """Show session completion and results"""
    if 'current_session_id' not in session:
        return redirect(url_for('index'))
    
    subject = session.get('current_subject', 'Unknown')
    correct_answers = session.get('correct_answers', 0)
    answer_history = session.get('answer_history', [])
    total_questions = len(answer_history)
    accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    
    # Update session status
    session_id = session['current_session_id']
    learning_session = LearningSession.query.filter_by(id=session_id).first()
    if learning_session:
        learning_session.status = 'completed'
        learning_session.completed_at = datetime.utcnow()
        db.session.commit()
    
    # Clear session data
    for key in ['current_session_id', 'current_subject', 'current_question', 'correct_answers', 'answer_history']:
        session.pop(key, None)
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Session Complete - NeuroPulse</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }}
            
            .completion-card {{
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                border-radius: 30px;
                padding: 50px;
                text-align: center;
                border: 1px solid rgba(255,255,255,0.2);
                max-width: 600px;
                width: 100%;
            }}
            
            .celebration {{
                font-size: 4rem;
                margin-bottom: 20px;
                animation: bounce 2s infinite;
            }}
            
            @keyframes bounce {{
                0%, 20%, 50%, 80%, 100% {{ transform: translateY(0); }}
                40% {{ transform: translateY(-10px); }}
                60% {{ transform: translateY(-5px); }}
            }}
            
            .completion-title {{
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 20px;
                background: linear-gradient(45deg, #FFE082, #FFF);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .subject-completed {{
                font-size: 1.4rem;
                margin-bottom: 30px;
                opacity: 0.9;
            }}
            
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }}
            
            .stat {{
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 20px;
            }}
            
            .stat-number {{
                font-size: 2rem;
                font-weight: 700;
                color: #4CAF50;
                margin-bottom: 5px;
            }}
            
            .stat-label {{
                font-size: 0.9rem;
                opacity: 0.8;
            }}
            
            .performance-message {{
                font-size: 1.2rem;
                margin: 30px 0;
                padding: 20px;
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
            }}
            
            .action-buttons {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 30px;
            }}
            
            .action-button {{
                padding: 15px 30px;
                border: none;
                border-radius: 25px;
                font-size: 1.1rem;
                font-weight: 600;
                text-decoration: none;
                text-align: center;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }}
            
            .primary-button {{
                background: linear-gradient(45deg, #4CAF50, #45a049);
                color: white;
            }}
            
            .secondary-button {{
                background: linear-gradient(45deg, #2196F3, #1976D2);
                color: white;
            }}
            
            .tertiary-button {{
                background: rgba(255,255,255,0.1);
                color: white;
                border: 1px solid rgba(255,255,255,0.2);
            }}
            
            .action-button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.3);
                text-decoration: none;
                color: white;
            }}
        </style>
    </head>
    <body>
        <div class="completion-card">
            <div class="celebration">🎉</div>
            <div class="completion-title">Great Job!</div>
            <div class="subject-completed">You completed a learning session on<br><strong>{subject}</strong></div>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">{correct_answers}</div>
                    <div class="stat-label">Correct Answers</div>
                </div>
                
                <div class="stat">
                    <div class="stat-number">{total_questions}</div>
                    <div class="stat-label">Total Questions</div>
                </div>
                
                <div class="stat">
                    <div class="stat-number">{accuracy:.0f}%</div>
                    <div class="stat-label">Accuracy</div>
                </div>
            </div>
            
            <div class="performance-message">
                {get_performance_message(accuracy)}
            </div>
            
            <div class="action-buttons">
                <a href="/continue_learning?subject={subject}" class="action-button primary-button">
                    Continue {subject}
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
    """

def get_performance_message(accuracy):
    """Get encouraging performance message"""
    if accuracy >= 90:
        return "🌟 Outstanding! You're mastering this subject with incredible precision!"
    elif accuracy >= 80:
        return "👏 Excellent work! You're showing strong understanding and retention!"
    elif accuracy >= 70:
        return "💪 Great progress! You're building solid knowledge foundations!"
    elif accuracy >= 60:
        return "📈 Good effort! Keep practicing and you'll see continued improvement!"
    else:
        return "🎯 Every expert was once a beginner! Your learning journey is just getting started!"

@app.route('/continue_learning')
def continue_learning():
    """Continue learning the same subject with advanced content"""
    subject = request.args.get('subject', '')
    if subject:
        # Redirect to start a new session with intermediate difficulty
        session['continue_subject'] = subject
        return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.route('/progress')
def view_progress():
    """View learning progress and analytics"""
    user_id = get_user_id()
    sessions = LearningSession.query.filter_by(user_id=user_id).all()
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Your Progress - NeuroPulse</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
                padding: 20px;
            }}
            
            .progress-container {{
                max-width: 1000px;
                margin: 0 auto;
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 40px;
            }}
            
            .title {{
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 10px;
            }}
            
            .sessions-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }}
            
            .session-card {{
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 25px;
                border: 1px solid rgba(255,255,255,0.2);
            }}
            
            .back-button {{
                background: rgba(255,255,255,0.1);
                color: white;
                padding: 10px 20px;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 20px;
                text-decoration: none;
                display: inline-block;
                margin-bottom: 30px;
            }}
        </style>
    </head>
    <body>
        <div class="progress-container">
            <a href="/" class="back-button">← Back to Home</a>
            
            <div class="header">
                <div class="title">📊 Your Learning Journey</div>
                <p>Track your progress across all subjects</p>
            </div>
            
            {f'<p style="text-align: center; font-size: 1.2rem;">You have completed {len([s for s in sessions if s.status == "completed"])} learning sessions!</p>' if sessions else '<p style="text-align: center; font-size: 1.2rem;">Start your first learning session to see progress here!</p>'}
            
            <div class="sessions-grid">
                {generate_session_cards(sessions)}
            </div>
        </div>
    </body>
    </html>
    """

def generate_session_cards(sessions):
    """Generate HTML for session cards"""
    if not sessions:
        return '<div style="text-align: center; grid-column: 1 / -1;"><p>No learning sessions yet. <a href="/" style="color: #4CAF50;">Start learning!</a></p></div>'
    
    html = ""
    for session in sessions:
        created_date = session.created_at.strftime("%B %d, %Y")
        status_icon = "✅" if session.status == "completed" else "🔄"
        html += f"""
        <div class="session-card">
            <h3>{status_icon} {session.subject}</h3>
            <p><strong>Started:</strong> {created_date}</p>
            <p><strong>Status:</strong> {session.status.title()}</p>
        </div>
        """
    return html

@app.route('/api/generate_content', methods=['POST'])
def api_generate_content():
    """API endpoint for generating new content"""
    data = request.get_json()
    subject = data.get('subject')
    difficulty = data.get('difficulty', 'intermediate')
    content_type = data.get('content_type', 'quiz')
    
    if not subject:
        return jsonify({'error': 'Subject is required'}), 400
    
    try:
        content = generate_learning_content(subject, difficulty, content_type)
        return jsonify(content)
    except Exception as e:
        logger.error(f"Content generation API error: {e}")
        return jsonify({'error': 'Failed to generate content'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'ai_enabled': AI_ENABLED,
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })

logger.info("NeuroPulse application initialized successfully")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)