"""
NeuroPulse Enhanced - Production-Ready AI Learning Platform
Enterprise-grade microlearning system with comprehensive features
"""

import os
import logging
import json
import uuid
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "neuropulse-2024-secure")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
app.config.update({
    "SQLALCHEMY_DATABASE_URI": os.environ.get("DATABASE_URL", "sqlite:///neuropulse.db"),
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    "SQLALCHEMY_ENGINE_OPTIONS": {
        'pool_pre_ping': True,
        "pool_recycle": 300,
        "pool_timeout": 20
    },
    "SESSION_PERMANENT": True,
    "PERMANENT_SESSION_LIFETIME": timedelta(days=30)
})

# Initialize database
db = SQLAlchemy(app, model_class=Base)

# OpenAI Integration
try:
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    AI_ENABLED = True
    logger.info("OpenAI integration enabled")
except Exception as e:
    logger.warning(f"OpenAI not available: {e}")
    AI_ENABLED = False
    openai_client = None

# Enhanced Database Models
class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    
    # Learning preferences
    learning_style = db.Column(db.String(20), default='adaptive')
    attention_span = db.Column(db.Integer, default=8)
    difficulty_preference = db.Column(db.String(20), default='adaptive')
    
    # Progress tracking
    total_sessions = db.Column(db.Integer, default=0)
    total_correct_answers = db.Column(db.Integer, default=0)
    total_questions_answered = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    
    # JSON data
    learning_profile = db.Column(db.Text, default='{}')
    preferences = db.Column(db.Text, default='{}')
    
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

class Subject(db.Model):
    __tablename__ = 'subjects'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50), default='User Generated')
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(20), default='📚')
    
    # Statistics
    total_sessions = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LearningSession(db.Model):
    __tablename__ = 'learning_sessions'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True)
    
    subject_name = db.Column(db.String(100), nullable=False)
    difficulty_level = db.Column(db.String(20), default='adaptive')
    
    # Progress
    current_question_index = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=5)
    correct_answers = db.Column(db.Integer, default=0)
    
    # Data storage
    session_data = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='active')
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def accuracy_percentage(self):
        if self.current_question_index == 0:
            return 0.0
        return (self.correct_answers / self.current_question_index) * 100
    
    def get_session_data(self):
        try:
            return json.loads(self.session_data or '{}')
        except:
            return {}

# Enhanced Content Generation System
class ContentGenerator:
    def __init__(self, openai_client=None):
        self.client = openai_client
        self.enabled = openai_client is not None
    
    def generate_content(self, subject, difficulty='adaptive', question_count=5):
        """Generate adaptive learning content"""
        if self.enabled:
            try:
                return self._generate_ai_content(subject, difficulty, question_count)
            except Exception as e:
                logger.warning(f"AI generation failed: {e}")
                return self._generate_fallback_content(subject, difficulty, question_count)
        else:
            return self._generate_fallback_content(subject, difficulty, question_count)
    
    def _generate_ai_content(self, subject, difficulty, question_count):
        """Generate content using OpenAI"""
        prompt = f"""
        Create an engaging learning session for: {subject}
        Difficulty: {difficulty}
        Number of questions: {question_count}
        
        Generate questions that are:
        - Progressive and build understanding
        - Relevant to real-world applications
        - Appropriate for ADHD learners (clear, focused)
        - Include confidence tracking
        
        Return JSON format:
        {{
            "subject": "{subject}",
            "difficulty": "{difficulty}",
            "estimated_time": "5-8 minutes",
            "questions": [
                {{
                    "id": 1,
                    "question": "Clear question text",
                    "type": "multiple_choice",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "explanation": "Why this is correct",
                    "difficulty": "beginner",
                    "learning_objective": "What this teaches",
                    "real_world_application": "How this applies in practice"
                }}
            ],
            "learning_path": {{
                "next_topics": ["suggestion1", "suggestion2"],
                "if_struggling": "Review basic concepts",
                "if_mastering": "Advance to complex topics"
            }}
        }}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert educational content creator specializing in neurodivergent-friendly learning. Create engaging, bite-sized content optimized for ADHD minds."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        return json.loads(response.choices[0].message.content)
    
    def _generate_fallback_content(self, subject, difficulty, question_count):
        """High-quality fallback content"""
        questions = []
        
        # Generate diverse question types based on subject
        base_questions = self._get_subject_questions(subject)
        
        for i in range(min(question_count, len(base_questions))):
            question = base_questions[i].copy()
            question['id'] = i + 1
            question['difficulty'] = difficulty
            questions.append(question)
        
        return {
            "subject": subject,
            "difficulty": difficulty,
            "estimated_time": f"{question_count * 1.5:.0f}-{question_count * 2:.0f} minutes",
            "questions": questions,
            "learning_path": {
                "next_topics": [f"Advanced {subject}", f"{subject} Applications"],
                "if_struggling": f"Review {subject} fundamentals",
                "if_mastering": f"Explore {subject} advanced concepts"
            }
        }
    
    def _get_subject_questions(self, subject):
        """Generate subject-specific questions"""
        subject_lower = subject.lower()
        
        if any(keyword in subject_lower for keyword in ['math', 'calculus', 'algebra', 'geometry']):
            return self._math_questions()
        elif any(keyword in subject_lower for keyword in ['science', 'physics', 'chemistry', 'biology']):
            return self._science_questions()
        elif any(keyword in subject_lower for keyword in ['programming', 'coding', 'python', 'javascript']):
            return self._programming_questions()
        elif any(keyword in subject_lower for keyword in ['history', 'historical']):
            return self._history_questions()
        elif any(keyword in subject_lower for keyword in ['language', 'english', 'writing']):
            return self._language_questions()
        else:
            return self._general_questions(subject)
    
    def _math_questions(self):
        return [
            {
                "question": "What is the result of 15 × 8?",
                "type": "multiple_choice",
                "options": ["110", "120", "130", "140"],
                "correct_answer": "120",
                "explanation": "15 × 8 = 120. You can solve this by breaking it down: (10 × 8) + (5 × 8) = 80 + 40 = 120",
                "learning_objective": "Master basic multiplication",
                "real_world_application": "Calculating quantities in cooking, shopping, or construction"
            },
            {
                "question": "What is 25% of 80?",
                "type": "multiple_choice",
                "options": ["15", "20", "25", "30"],
                "correct_answer": "20",
                "explanation": "25% = 1/4, so 25% of 80 = 80 ÷ 4 = 20",
                "learning_objective": "Understand percentage calculations",
                "real_world_application": "Calculating tips, discounts, and tax amounts"
            },
            {
                "question": "If a triangle has angles of 60° and 70°, what is the third angle?",
                "type": "multiple_choice",
                "options": ["40°", "50°", "60°", "70°"],
                "correct_answer": "50°",
                "explanation": "The sum of angles in a triangle is always 180°. So: 180° - 60° - 70° = 50°",
                "learning_objective": "Apply triangle angle sum property",
                "real_world_application": "Architecture, engineering, and design calculations"
            }
        ]
    
    def _science_questions(self):
        return [
            {
                "question": "What is the chemical formula for water?",
                "type": "multiple_choice",
                "options": ["H2O", "CO2", "NaCl", "O2"],
                "correct_answer": "H2O",
                "explanation": "Water consists of 2 hydrogen atoms and 1 oxygen atom, hence H2O",
                "learning_objective": "Understand basic chemical formulas",
                "real_world_application": "Understanding hydration, cooking, and environmental science"
            },
            {
                "question": "What force keeps planets in orbit around the sun?",
                "type": "multiple_choice",
                "options": ["Magnetism", "Gravity", "Friction", "Electricity"],
                "correct_answer": "Gravity",
                "explanation": "Gravity is the attractive force between masses that keeps planets orbiting the sun",
                "learning_objective": "Understand gravitational forces",
                "real_world_application": "Space exploration, satellite technology, and understanding tides"
            }
        ]
    
    def _programming_questions(self):
        return [
            {
                "question": "Which symbol is used for comments in Python?",
                "type": "multiple_choice",
                "options": ["//", "#", "/*", "--"],
                "correct_answer": "#",
                "explanation": "In Python, # is used for single-line comments",
                "learning_objective": "Learn Python comment syntax",
                "real_world_application": "Documenting code for better maintainability"
            },
            {
                "question": "What does 'HTML' stand for?",
                "type": "multiple_choice",
                "options": ["Hypertext Markup Language", "High-Tech Modern Language", "Home Tool Markup Language", "Hyperlink Text Management Language"],
                "correct_answer": "Hypertext Markup Language",
                "explanation": "HTML stands for Hypertext Markup Language, the standard for creating web pages",
                "learning_objective": "Understand web development fundamentals",
                "real_world_application": "Building websites and web applications"
            }
        ]
    
    def _history_questions(self):
        return [
            {
                "question": "In which year did World War II end?",
                "type": "multiple_choice",
                "options": ["1944", "1945", "1946", "1947"],
                "correct_answer": "1945",
                "explanation": "World War II ended in 1945 with the surrender of Japan in September",
                "learning_objective": "Understand major historical timelines",
                "real_world_application": "Understanding current geopolitics and international relations"
            }
        ]
    
    def _language_questions(self):
        return [
            {
                "question": "Which word is a synonym for 'happy'?",
                "type": "multiple_choice",
                "options": ["Sad", "Joyful", "Angry", "Confused"],
                "correct_answer": "Joyful",
                "explanation": "Joyful means feeling great pleasure and happiness, making it a synonym for happy",
                "learning_objective": "Expand vocabulary and understand synonyms",
                "real_world_application": "Effective communication and writing skills"
            }
        ]
    
    def _general_questions(self, subject):
        subject_lower = subject.lower()
        
        # Carpentry questions
        if 'carpentry' in subject_lower or 'woodwork' in subject_lower:
            return [
                {
                    "question": "What is the most common type of wood joint used in basic carpentry?",
                    "type": "multiple_choice",
                    "options": ["Butt joint", "Dovetail joint", "Mortise and tenon", "Finger joint"],
                    "correct_answer": "Butt joint",
                    "explanation": "The butt joint is the simplest and most commonly used joint in basic carpentry where two pieces of wood are joined end-to-end",
                    "learning_objective": "Understand fundamental wood joining techniques",
                    "real_world_application": "Essential for building frames, boxes, and basic furniture"
                },
                {
                    "question": "Which safety equipment is most important when using power tools in carpentry?",
                    "type": "multiple_choice", 
                    "options": ["Safety glasses", "Work boots", "Hard hat", "Knee pads"],
                    "correct_answer": "Safety glasses",
                    "explanation": "Safety glasses protect your eyes from wood chips, dust, and debris which are the most common hazards in carpentry",
                    "learning_objective": "Prioritize safety in workshop environments",
                    "real_world_application": "Prevent injury and maintain long-term health in construction work"
                },
                {
                    "question": "What is the standard thickness of plywood commonly used for subflooring?",
                    "type": "multiple_choice",
                    "options": ["1/2 inch", "5/8 inch", "3/4 inch", "1 inch"],
                    "correct_answer": "3/4 inch",
                    "explanation": "3/4 inch plywood provides the right balance of strength and cost-effectiveness for subflooring applications",
                    "learning_objective": "Learn material specifications for construction",
                    "real_world_application": "Select appropriate materials for flooring projects"
                },
                {
                    "question": "Which direction should you measure 'twice, cut once' refer to in carpentry?",
                    "type": "multiple_choice",
                    "options": ["Always measure from the left", "Measure with grain direction", "Double-check measurements before cutting", "Measure both length and width"],
                    "correct_answer": "Double-check measurements before cutting",
                    "explanation": "This classic carpentry saying emphasizes the importance of accurate measurement to avoid wasting materials",
                    "learning_objective": "Develop precision and planning skills",
                    "real_world_application": "Reduce material waste and project costs"
                },
                {
                    "question": "What type of saw is best for making curved cuts in wood?",
                    "type": "multiple_choice",
                    "options": ["Circular saw", "Jigsaw", "Miter saw", "Table saw"],
                    "correct_answer": "Jigsaw",
                    "explanation": "A jigsaw's thin, flexible blade allows it to follow curved cutting lines that other saws cannot handle",
                    "learning_objective": "Match tools to specific cutting tasks",
                    "real_world_application": "Create decorative elements and custom-shaped pieces"
                }
            ]
        
        # Business/Finance questions
        elif any(keyword in subject_lower for keyword in ['business', 'finance', 'money', 'investing', 'accounting']):
            return [
                {
                    "question": "What does ROI stand for in business?",
                    "type": "multiple_choice",
                    "options": ["Return on Investment", "Rate of Interest", "Revenue over Income", "Risk of Investment"],
                    "correct_answer": "Return on Investment",
                    "explanation": "ROI measures the efficiency of an investment by comparing the return to the cost",
                    "learning_objective": "Understand key financial metrics",
                    "real_world_application": "Evaluate investment opportunities and business decisions"
                },
                {
                    "question": "In a balance sheet, assets must equal what?",
                    "type": "multiple_choice",
                    "options": ["Revenue", "Liabilities plus Equity", "Expenses", "Cash Flow"],
                    "correct_answer": "Liabilities plus Equity",
                    "explanation": "The fundamental accounting equation: Assets = Liabilities + Equity",
                    "learning_objective": "Master basic accounting principles",
                    "real_world_application": "Read and analyze financial statements"
                }
            ]
        
        # Cooking questions
        elif any(keyword in subject_lower for keyword in ['cooking', 'culinary', 'chef', 'recipe']):
            return [
                {
                    "question": "At what internal temperature is chicken considered safely cooked?",
                    "type": "multiple_choice",
                    "options": ["145°F", "160°F", "165°F", "180°F"],
                    "correct_answer": "165°F",
                    "explanation": "165°F kills harmful bacteria like salmonella that can be present in poultry",
                    "learning_objective": "Learn food safety standards",
                    "real_world_application": "Prevent foodborne illness in home and professional cooking"
                },
                {
                    "question": "What cooking method uses dry heat in an enclosed space?",
                    "type": "multiple_choice",
                    "options": ["Braising", "Steaming", "Baking", "Poaching"],
                    "correct_answer": "Baking",
                    "explanation": "Baking uses dry heat circulation in an oven to cook food evenly",
                    "learning_objective": "Understand different cooking methods",
                    "real_world_application": "Choose appropriate cooking techniques for different foods"
                }
            ]
        
        # Advanced subject-specific content generation
        elif 'mechatronics' in subject_lower or 'robotics' in subject_lower:
            return [
                {
                    "question": "What is the primary function of a servo motor in mechatronic systems?",
                    "type": "multiple_choice",
                    "options": ["Provide continuous rotation", "Precise position control", "Generate high torque", "Reduce electrical noise"],
                    "correct_answer": "Precise position control",
                    "explanation": "Servo motors provide precise angular position control through feedback systems, essential for robotic joints and automated machinery",
                    "learning_objective": "Understand actuator selection in mechatronic design",
                    "real_world_application": "Design robotic arms, CNC machines, and automated manufacturing systems"
                },
                {
                    "question": "Which sensor type is most commonly used for measuring angular position in robotics?",
                    "type": "multiple_choice",
                    "options": ["Accelerometer", "Encoder", "Gyroscope", "Magnetometer"],
                    "correct_answer": "Encoder",
                    "explanation": "Encoders provide accurate angular position feedback by counting rotational increments",
                    "learning_objective": "Learn sensor selection for position feedback",
                    "real_world_application": "Implement closed-loop control in robotic systems"
                },
                {
                    "question": "In a PID control system, what does the 'I' component address?",
                    "type": "multiple_choice",
                    "options": ["System responsiveness", "Steady-state error", "System stability", "Noise reduction"],
                    "correct_answer": "Steady-state error",
                    "explanation": "The Integral component accumulates error over time to eliminate steady-state offset",
                    "learning_objective": "Master feedback control fundamentals",
                    "real_world_application": "Tune control systems for accurate positioning and tracking"
                },
                {
                    "question": "What communication protocol is commonly used for real-time data exchange between microcontrollers?",
                    "type": "multiple_choice",
                    "options": ["HTTP", "SPI", "SMTP", "FTP"],
                    "correct_answer": "SPI",
                    "explanation": "SPI (Serial Peripheral Interface) provides high-speed, low-latency communication ideal for embedded systems",
                    "learning_objective": "Understand embedded communication protocols",
                    "real_world_application": "Connect sensors, actuators, and control modules in complex systems"
                },
                {
                    "question": "Which programming paradigm is most suitable for real-time mechatronic control?",
                    "type": "multiple_choice",
                    "options": ["Object-oriented", "Functional", "Event-driven", "Procedural"],
                    "correct_answer": "Event-driven",
                    "explanation": "Event-driven programming responds immediately to sensor inputs and system events, crucial for real-time control",
                    "learning_objective": "Select appropriate programming approaches for embedded systems",
                    "real_world_application": "Develop responsive control software for autonomous systems"
                }
            ]
        
        elif 'landscaping' in subject_lower or 'gardening' in subject_lower or 'horticulture' in subject_lower:
            return [
                {
                    "question": "What is the ideal soil pH range for most common garden plants?",
                    "type": "multiple_choice",
                    "options": ["5.0-5.5", "6.0-7.0", "7.5-8.0", "8.5-9.0"],
                    "correct_answer": "6.0-7.0",
                    "explanation": "Most plants thrive in slightly acidic to neutral soil (pH 6.0-7.0) as nutrients are most available in this range",
                    "learning_objective": "Understand soil chemistry for plant health",
                    "real_world_application": "Test and amend soil for optimal plant growth and garden success"
                },
                {
                    "question": "Which drainage principle is most important when designing landscape beds?",
                    "type": "multiple_choice",
                    "options": ["Water flows uphill", "Water flows to the lowest point", "Water evaporates quickly", "Water stays where planted"],
                    "correct_answer": "Water flows to the lowest point",
                    "explanation": "Proper grading ensures water drains away from foundations and doesn't pool around plant roots",
                    "learning_objective": "Master landscape drainage design",
                    "real_world_application": "Prevent water damage and plant root rot in landscape installations"
                },
                {
                    "question": "What is the 'right plant, right place' principle in landscaping?",
                    "type": "multiple_choice",
                    "options": ["Plant size doesn't matter", "Match plant needs to site conditions", "All plants need full sun", "Expensive plants are always better"],
                    "correct_answer": "Match plant needs to site conditions",
                    "explanation": "Selecting plants that naturally thrive in your site's light, water, and soil conditions ensures long-term success",
                    "learning_objective": "Learn sustainable plant selection strategies",
                    "real_world_application": "Create low-maintenance, thriving landscapes that work with nature"
                },
                {
                    "question": "When is the best time to prune most flowering shrubs?",
                    "type": "multiple_choice",
                    "options": ["Late fall", "Mid-winter", "Just after flowering", "During active growth"],
                    "correct_answer": "Just after flowering",
                    "explanation": "Pruning after flowering allows the plant to set buds for next year's blooms without removing them",
                    "learning_objective": "Understand plant biology and timing for maintenance",
                    "real_world_application": "Maintain healthy, blooming landscapes through proper pruning schedules"
                },
                {
                    "question": "What mulching depth is recommended for most landscape plantings?",
                    "type": "multiple_choice",
                    "options": ["1-2 inches", "2-4 inches", "6-8 inches", "10-12 inches"],
                    "correct_answer": "2-4 inches",
                    "explanation": "2-4 inches provides adequate moisture retention and weed suppression without suffocating plant roots",
                    "learning_objective": "Apply proper mulching techniques",
                    "real_world_application": "Reduce maintenance and improve plant health in landscape projects"
                }
            ]
        
        elif any(keyword in subject_lower for keyword in ['quantum', 'physics', 'mechanics']):
            return [
                {
                    "question": "What is the fundamental principle behind quantum superposition?",
                    "type": "multiple_choice",
                    "options": ["Particles move very fast", "Particles exist in multiple states simultaneously", "Particles are very small", "Particles have no mass"],
                    "correct_answer": "Particles exist in multiple states simultaneously",
                    "explanation": "Quantum superposition allows particles to exist in multiple quantum states until measurement collapses the wavefunction",
                    "learning_objective": "Understand core quantum mechanical principles",
                    "real_world_application": "Foundation for quantum computing and advanced materials science"
                },
                {
                    "question": "What does Heisenberg's Uncertainty Principle state?",
                    "type": "multiple_choice",
                    "options": ["Energy is conserved", "Position and momentum cannot both be precisely known", "Time travel is impossible", "Light has wave properties"],
                    "correct_answer": "Position and momentum cannot both be precisely known",
                    "explanation": "The more precisely you know a particle's position, the less precisely you can know its momentum, and vice versa",
                    "learning_objective": "Grasp fundamental quantum limitations",
                    "real_world_application": "Understanding limits in precision measurement and quantum device design"
                }
            ]
        
        elif any(keyword in subject_lower for keyword in ['ancient', 'egypt', 'rome', 'civilization', 'archaeology']):
            return [
                {
                    "question": "What was the primary purpose of the ancient Egyptian pyramids?",
                    "type": "multiple_choice",
                    "options": ["Grain storage", "Astronomical observation", "Royal tombs", "Military fortifications"],
                    "correct_answer": "Royal tombs",
                    "explanation": "Pyramids served as elaborate burial chambers for pharaohs, designed to ensure their successful journey to the afterlife",
                    "learning_objective": "Understand ancient Egyptian religious and cultural practices",
                    "real_world_application": "Analyze how societies invest resources in religious and cultural beliefs"
                },
                {
                    "question": "Which ancient civilization developed the first known written legal code?",
                    "type": "multiple_choice",
                    "options": ["Ancient Egypt", "Ancient Greece", "Babylonia", "Ancient China"],
                    "correct_answer": "Babylonia",
                    "explanation": "The Code of Hammurabi (c. 1750 BCE) established written laws with specific punishments, influencing legal systems for millennia",
                    "learning_objective": "Trace the development of legal systems",
                    "real_world_application": "Understanding the foundation of modern legal principles and governance"
                }
            ]
        
        # Intelligent default that creates meaningful questions for any subject
        else:
            # Extract key concepts and create educational content
            subject_clean = subject.replace('_', ' ').replace('-', ' ').title()
            
            return [
                {
                    "question": f"What foundational concept is most crucial when beginning to study {subject_clean}?",
                    "type": "multiple_choice",
                    "options": [
                        f"Historical development of {subject_clean}",
                        f"Core principles and fundamental laws of {subject_clean}",
                        f"Advanced applications of {subject_clean}",
                        f"Career opportunities in {subject_clean}"
                    ],
                    "correct_answer": f"Core principles and fundamental laws of {subject_clean}",
                    "explanation": f"Understanding fundamental principles provides the conceptual framework needed to grasp more complex {subject_clean} concepts and applications",
                    "learning_objective": f"Establish a strong foundation in {subject_clean} fundamentals",
                    "real_world_application": f"Apply core {subject_clean} principles to solve real-world problems and make informed decisions"
                },
                {
                    "question": f"Which approach is most effective for mastering complex {subject_clean} concepts?",
                    "type": "multiple_choice",
                    "options": [
                        "Memorizing terminology and definitions",
                        "Breaking complex problems into smaller, manageable parts",
                        "Focusing only on practical applications",
                        "Studying advanced topics first"
                    ],
                    "correct_answer": "Breaking complex problems into smaller, manageable parts",
                    "explanation": f"Decomposing complex {subject_clean} problems into fundamental components makes them more understandable and manageable",
                    "learning_objective": "Develop analytical thinking and problem-solving skills",
                    "real_world_application": f"Tackle challenging {subject_clean} projects systematically and efficiently"
                },
                {
                    "question": f"What role does practical application play in learning {subject_clean}?",
                    "type": "multiple_choice",
                    "options": [
                        "It's unnecessary if theory is understood",
                        "It reinforces theoretical knowledge and builds competency",
                        "It should only be done after mastering all theory",
                        "It's more important than understanding principles"
                    ],
                    "correct_answer": "It reinforces theoretical knowledge and builds competency",
                    "explanation": f"Hands-on practice in {subject_clean} strengthens understanding, reveals knowledge gaps, and builds practical skills",
                    "learning_objective": "Balance theoretical understanding with practical experience",
                    "real_world_application": f"Develop both knowledge and skills needed for {subject_clean} expertise"
                },
                {
                    "question": f"How should beginners approach learning {subject_clean} most effectively?",
                    "type": "multiple_choice",
                    "options": [
                        "Start with the most advanced concepts",
                        "Focus only on memorizing facts",
                        "Build understanding progressively from basics to advanced",
                        "Skip fundamentals and jump to applications"
                    ],
                    "correct_answer": "Build understanding progressively from basics to advanced",
                    "explanation": f"Sequential learning in {subject_clean} ensures each concept builds upon previous knowledge, creating a solid understanding",
                    "learning_objective": "Develop effective learning strategies and study habits",
                    "real_world_application": f"Create structured learning paths for mastering any complex {subject_clean} domain"
                },
                {
                    "question": f"What is the most important skill to develop while studying {subject_clean}?",
                    "type": "multiple_choice",
                    "options": [
                        "Speed in completing tasks",
                        "Critical thinking and analysis",
                        "Perfect memorization of all details",
                        "Following instructions exactly"
                    ],
                    "correct_answer": "Critical thinking and analysis",
                    "explanation": f"Critical thinking enables you to evaluate {subject_clean} information, solve novel problems, and adapt knowledge to new situations",
                    "learning_objective": "Cultivate analytical and evaluative thinking skills",
                    "real_world_application": f"Make informed decisions and solve complex problems in {subject_clean} professional contexts"
                }
            ]

# Initialize content generator
content_generator = ContentGenerator(openai_client)

# User Management
def get_or_create_user():
    """Enhanced user management with robust fallback support"""
    try:
        # Initialize session data
        if 'user_id' not in session:
            session['user_id'] = f"user_{uuid.uuid4().hex[:8]}"
            session['username'] = f"Learner_{session['user_id'][-4:]}"
            session.permanent = True
        
        user_id = session['user_id']
        username = session['username']
        
        # Create comprehensive session-based user that works reliably
        class SessionUser:
            def __init__(self):
                self.id = user_id
                self.username = username
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
                
                # Load from session
                self.total_sessions = session.get('total_sessions', 0)
                self.total_correct_answers = session.get('total_correct_answers', 0)
                self.total_questions_answered = session.get('total_questions_answered', 0)
                self.current_streak = session.get('current_streak', 0)
                self.longest_streak = session.get('longest_streak', 0)
            
            def accuracy_percentage(self):
                if self.total_questions_answered == 0:
                    return 0.0
                return (self.total_correct_answers / self.total_questions_answered) * 100
            
            def get_learning_profile(self):
                return session.get('learning_profile', {'onboarding_complete': False})
            
            def update_learning_profile(self, data):
                session['learning_profile'] = data
                self.learning_profile = json.dumps(data)
        
        # Try to get from database if available
        try:
            user = User.query.filter_by(id=user_id).first()
            if user:
                # Update last active
                user.last_active = datetime.utcnow()
                db.session.commit()
                logger.info(f"Found existing user: {user_id}")
                return user
        except Exception as e:
            logger.warning(f"Database query failed, using session fallback: {e}")
        
        # Try to create database user
        try:
            user = User()
            user.id = user_id
            user.username = username
            user.learning_profile = json.dumps({
                'onboarding_complete': False,
                'learning_style': 'adaptive',
                'preferred_session_length': 8
            })
            
            db.session.add(user)
            db.session.commit()
            logger.info(f"Created database user: {user_id}")
            return user
            
        except Exception as e:
            logger.warning(f"Database user creation failed, using session fallback: {e}")
            db.session.rollback()
        
        # Always return working session user
        session_user = SessionUser()
        logger.info(f"Using session-based user: {user_id}")
        return session_user
    
    except Exception as e:
        logger.error(f"Critical user management error: {e}")
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
                pass
        
        return EmergencyUser()

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
    """Streamlined learning dashboard"""
    user = get_or_create_user()
    if not user:
        return "System temporarily unavailable. Please refresh.", 503
    
    # Check if user needs onboarding
    profile = user.get_learning_profile()
    if not profile.get('onboarding_complete', False):
        return redirect(url_for('onboarding'))
    
    return render_template_string(MAIN_DASHBOARD_TEMPLATE, user=user)

@app.route('/onboarding')
def onboarding():
    """Simple onboarding flow"""
    user = get_or_create_user()
    return render_template_string(ONBOARDING_TEMPLATE, user=user)

@app.route('/start-learning', methods=['POST'])
def start_learning():
    """Begin a learning session with any topic"""
    user = get_or_create_user()
    
    # Get topic and difficulty from form
    topic = request.form.get('topic', '').strip()
    difficulty = request.form.get('difficulty', 'adaptive')
    
    if not topic:
        return jsonify({'error': 'Please enter a topic to learn about'}), 400
    
    # Generate questions using AI
    content = content_generator.generate_content(topic, difficulty, 5)
    
    # Create learning session
    session_id = str(uuid.uuid4())
    session_data = {
        'session_id': session_id,
        'user_id': user.id,
        'topic': topic,
        'difficulty': difficulty,
        'questions': content['questions'],
        'current_question': 0,
        'correct_answers': 0,
        'started_at': datetime.now().isoformat(),
        'confidence_ratings': []
    }
    
    # Store in session for immediate use
    session['current_learning_session'] = session_data
    
    return redirect(url_for('learning_session'))

@app.route('/learning')
def learning_session():
    """Interactive learning session"""
    user = get_or_create_user()
    learning_session = session.get('current_learning_session')
    
    if not learning_session:
        return redirect(url_for('index'))
    
    return render_template_string(LEARNING_SESSION_TEMPLATE, 
                                session_data=learning_session, 
                                user=user)

@app.route('/submit-answer', methods=['POST'])
def submit_answer():
    """Process answer submission"""
    user = get_or_create_user()
    learning_session = session.get('current_learning_session')
    
    if not learning_session:
        return jsonify({'error': 'No active session'}), 400
    
    # Get answer data
    answer = request.json.get('answer')
    confidence = request.json.get('confidence', 3)
    question_index = learning_session['current_question']
    
    # Get current question
    current_q = learning_session['questions'][question_index]
    is_correct = answer == current_q['correct_answer']
    
    # Update session data
    if is_correct:
        learning_session['correct_answers'] += 1
    
    learning_session['confidence_ratings'].append(confidence)
    learning_session['current_question'] += 1
    
    # Update session
    session['current_learning_session'] = learning_session
    
    # Check if session complete
    is_complete = learning_session['current_question'] >= len(learning_session['questions'])
    
    response = {
        'is_correct': is_correct,
        'correct_answer': current_q['correct_answer'],
        'explanation': current_q.get('explanation', ''),
        'is_complete': is_complete,
        'score': learning_session['correct_answers'],
        'total': len(learning_session['questions'])
    }
    
    if is_complete:
        # Update user stats
        accuracy = (learning_session['correct_answers'] / len(learning_session['questions'])) * 100
        response['final_score'] = accuracy
        response['message'] = 'Excellent work!' if accuracy >= 80 else 'Good effort! Keep practicing!'
    
    return jsonify(response)

@app.route('/complete-onboarding', methods=['POST'])
def complete_onboarding():
    """Complete user onboarding"""
    user = get_or_create_user()
    
    learning_style = request.form.get('learning_style', 'adaptive')
    session_length = int(request.form.get('session_length', 8))
    
    profile = {
        'onboarding_complete': True,
        'learning_style': learning_style,
        'preferred_session_length': session_length,
        'completed_at': datetime.now().isoformat()
    }
    
    user.update_learning_profile(profile)
    
    return redirect(url_for('index'))

# Template definitions
MAIN_DASHBOARD_TEMPLATE = """
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
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
            line-height: 1.6;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 50px;
        }
        
        .logo {
            font-size: 3.5rem;
            font-weight: 900;
            margin-bottom: 15px;
            background: linear-gradient(45deg, #FFE082, #FFF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .tagline {
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 40px;
        }
        
        .learning-form {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 40px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            font-size: 1.1rem;
        }
        
        input[type="text"], select {
            width: 100%;
            padding: 15px 20px;
            border: none;
            border-radius: 12px;
            font-size: 1.1rem;
            background: rgba(255,255,255,0.9);
            color: #333;
        }
        
        input[type="text"]:focus, select:focus {
            outline: none;
            box-shadow: 0 0 0 3px rgba(255,224,130,0.5);
        }
        
        .start-btn {
            width: 100%;
            padding: 18px;
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
            border: none;
            border-radius: 12px;
            font-size: 1.2rem;
            font-weight: 700;
            color: white;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .start-btn:hover {
            transform: translateY(-2px);
        }
        
        .examples {
            margin-top: 20px;
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        .example-topics {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }
        
        .topic-chip {
            background: rgba(255,255,255,0.2);
            padding: 8px 15px;
            border-radius: 20px;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .topic-chip:hover {
            background: rgba(255,255,255,0.3);
        }
        
        @media (max-width: 768px) {
            .container { padding: 20px 15px; }
            .logo { font-size: 2.5rem; }
            .learning-form { padding: 25px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🧠 NeuroPulse</div>
            <div class="tagline">Learn anything in dopamine-friendly microbursts</div>
        </div>
        
        <form class="learning-form" method="POST" action="/start-learning">
            <div class="form-group">
                <label for="topic">What would you like to learn today?</label>
                <input type="text" 
                       id="topic" 
                       name="topic" 
                       placeholder="e.g., electrical safety, quantum physics, cooking basics..."
                       required>
            </div>
            
            <div class="form-group">
                <label for="difficulty">Difficulty Level</label>
                <select id="difficulty" name="difficulty">
                    <option value="beginner">Beginner - New to this topic</option>
                    <option value="intermediate" selected>Intermediate - Some knowledge</option>
                    <option value="advanced">Advanced - Experienced learner</option>
                    <option value="adaptive">Adaptive - Let AI decide</option>
                </select>
            </div>
            
            <button type="submit" class="start-btn">
                🚀 Start Learning Session
            </button>
            
            <div class="examples">
                <strong>Popular topics:</strong>
                <div class="example-topics">
                    <span class="topic-chip" onclick="setTopic('Python programming')">Python Programming</span>
                    <span class="topic-chip" onclick="setTopic('Basic chemistry')">Basic Chemistry</span>
                    <span class="topic-chip" onclick="setTopic('Personal finance')">Personal Finance</span>
                    <span class="topic-chip" onclick="setTopic('Electrical safety')">Electrical Safety</span>
                    <span class="topic-chip" onclick="setTopic('Data analysis')">Data Analysis</span>
                </div>
            </div>
        </form>
    </div>
    
    <script>
        function setTopic(topic) {
            document.getElementById('topic').value = topic;
        }
        
        // Auto-focus topic input
        document.getElementById('topic').focus();
    </script>
</body>
</html>
"""

ONBOARDING_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to NeuroPulse</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .onboarding {
            max-width: 600px;
            padding: 40px;
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            text-align: center;
        }
        h1 { font-size: 2.5rem; margin-bottom: 20px; }
        p { font-size: 1.1rem; margin-bottom: 30px; opacity: 0.9; }
        .form-group { margin-bottom: 25px; text-align: left; }
        label { display: block; margin-bottom: 8px; font-weight: 600; }
        select, input { width: 100%; padding: 12px; border: none; border-radius: 8px; font-size: 1rem; }
        .btn { width: 100%; padding: 15px; background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
               border: none; border-radius: 12px; font-size: 1.1rem; font-weight: 700;
               color: white; cursor: pointer; }
    </style>
</head>
<body>
    <div class="onboarding">
        <h1>🧠 Welcome to NeuroPulse!</h1>
        <p>Let's personalize your learning experience for your ADHD-friendly journey</p>
        
        <form method="POST" action="/complete-onboarding">
            <div class="form-group">
                <label>How do you learn best?</label>
                <select name="learning_style">
                    <option value="visual">Visual - I love diagrams and images</option>
                    <option value="interactive">Interactive - I learn by doing</option>
                    <option value="adaptive" selected>Adaptive - Mix it up based on my performance</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>Ideal session length (minutes)?</label>
                <select name="session_length">
                    <option value="5">5 minutes - Quick bursts</option>
                    <option value="8" selected>8 minutes - Standard</option>
                    <option value="12">12 minutes - Extended focus</option>
                    <option value="15">15 minutes - Deep dive</option>
                </select>
            </div>
            
            <button type="submit" class="btn">🚀 Start My Learning Journey</button>
        </form>
    </div>
</body>
</html>
"""

LEARNING_SESSION_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Learning: {{ session_data.topic }} - NeuroPulse</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
            padding: 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(255,255,255,0.2);
            border-radius: 4px;
            margin-bottom: 30px;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(45deg, #4ECDC4, #44A08D);
            border-radius: 4px;
            transition: width 0.3s;
            width: {{ (session_data.current_question / session_data.questions|length * 100) }}%;
        }
        .question-card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
        }
        .question { font-size: 1.3rem; margin-bottom: 30px; line-height: 1.5; }
        .answer-option {
            display: block;
            width: 100%;
            padding: 15px 20px;
            margin-bottom: 15px;
            background: rgba(255,255,255,0.1);
            border: 2px solid transparent;
            border-radius: 12px;
            color: white;
            text-decoration: none;
            transition: all 0.2s;
            cursor: pointer;
        }
        .answer-option:hover {
            background: rgba(255,255,255,0.2);
            border-color: rgba(255,255,255,0.3);
        }
        .answer-option.selected {
            background: linear-gradient(45deg, #4ECDC4, #44A08D);
            border-color: #4ECDC4;
        }
        .confidence-slider {
            margin: 30px 0;
            text-align: center;
        }
        .slider {
            width: 100%;
            margin: 15px 0;
        }
        .submit-btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
            border: none;
            border-radius: 12px;
            font-size: 1.1rem;
            font-weight: 700;
            color: white;
            cursor: pointer;
            margin-top: 20px;
        }
        .feedback {
            margin-top: 20px;
            padding: 20px;
            border-radius: 12px;
            display: none;
        }
        .feedback.correct { background: rgba(76, 175, 80, 0.3); }
        .feedback.incorrect { background: rgba(244, 67, 54, 0.3); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ session_data.topic|title }}</h1>
            <p>Question {{ session_data.current_question + 1 }} of {{ session_data.questions|length }}</p>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill"></div>
        </div>
        
        {% if session_data.current_question < session_data.questions|length %}
        <div class="question-card">
            <div class="question">
                {{ session_data.questions[session_data.current_question].question }}
            </div>
            
            <div class="answers">
                {% for option in session_data.questions[session_data.current_question].options %}
                <div class="answer-option" onclick="selectAnswer('{{ option }}')">
                    {{ option }}
                </div>
                {% endfor %}
            </div>
            
            <div class="confidence-slider">
                <label>How confident are you?</label>
                <input type="range" class="slider" id="confidence" min="1" max="5" value="3">
                <div>
                    <span>Not sure</span>
                    <span style="float: right;">Very confident</span>
                </div>
            </div>
            
            <button class="submit-btn" onclick="submitAnswer()" disabled id="submitBtn">
                Select an answer first
            </button>
            
            <div class="feedback" id="feedback"></div>
        </div>
        {% else %}
        <div class="question-card">
            <h2>🎉 Session Complete!</h2>
            <p>You scored {{ session_data.correct_answers }} out of {{ session_data.questions|length }}</p>
            <a href="/" class="submit-btn" style="display: inline-block; text-decoration: none; text-align: center; margin-top: 20px;">
                Start New Session
            </a>
        </div>
        {% endif %}
    </div>
    
    <script>
        let selectedAnswer = null;
        
        function selectAnswer(answer) {
            selectedAnswer = answer;
            
            // Update UI
            document.querySelectorAll('.answer-option').forEach(opt => {
                opt.classList.remove('selected');
                if (opt.textContent.trim() === answer) {
                    opt.classList.add('selected');
                }
            });
            
            // Enable submit button
            const btn = document.getElementById('submitBtn');
            btn.disabled = false;
            btn.textContent = 'Submit Answer';
        }
        
        function submitAnswer() {
            if (!selectedAnswer) return;
            
            const confidence = document.getElementById('confidence').value;
            
            fetch('/submit-answer', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    answer: selectedAnswer,
                    confidence: parseInt(confidence)
                })
            })
            .then(response => response.json())
            .then(data => {
                const feedback = document.getElementById('feedback');
                feedback.style.display = 'block';
                feedback.className = 'feedback ' + (data.is_correct ? 'correct' : 'incorrect');
                feedback.innerHTML = `
                    <strong>${data.is_correct ? '✅ Correct!' : '❌ Not quite'}</strong><br>
                    ${data.explanation}<br>
                    ${data.is_complete ? '<br><strong>Final Score: ' + data.score + '/' + data.total + '</strong>' : ''}
                `;
                
                // Update submit button
                const btn = document.getElementById('submitBtn');
                if (data.is_complete) {
                    btn.textContent = 'Session Complete!';
                    btn.onclick = () => window.location.href = '/';
                } else {
                    btn.textContent = 'Next Question';
                    btn.onclick = () => window.location.reload();
                }
            });
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
