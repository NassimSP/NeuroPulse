"""
Core Routes for NeuroPulse - Essential functionality
"""

from flask import render_template, session, request, redirect, url_for, jsonify
from app import app, db, logger
import uuid
from datetime import datetime
import json

# Session management
def get_user_id():
    if 'user_id' not in session:
        session['user_id'] = f"user_{uuid.uuid4().hex[:8]}"
    return session['user_id']

@app.route('/')
def index():
    """Main dashboard page"""
    try:
        user_id = get_user_id()
        
        # Get current quiz session if any
        current_quiz = session.get('current_quiz_id')
        current_question = session.get('current_question', 0)
        
        # Basic stats
        stats = {
            'total_sessions': session.get('total_sessions', 0),
            'correct_answers': session.get('total_correct', 0),
            'accuracy': session.get('accuracy', 0)
        }
        
        return render_template('index.html', 
                             user_id=user_id,
                             current_quiz=current_quiz,
                             current_question=current_question,
                             stats=stats)
    except Exception as e:
        logger.error(f"Index route error: {e}")
        return f"""
        <html>
        <head><title>NeuroPulse Learning Platform</title></head>
        <body style="font-family: Arial, sans-serif; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <div style="max-width: 800px; margin: 0 auto; text-align: center;">
                <h1>🧠 NeuroPulse Learning Platform</h1>
                <p>Advanced AI-powered adaptive learning system</p>
                <div style="margin: 30px 0;">
                    <a href="/quiz" style="background: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; margin: 10px;">Start Quiz</a>
                    <a href="/subjects" style="background: #2196F3; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; margin: 10px;">Browse Subjects</a>
                </div>
            </div>
        </body>
        </html>
        """

@app.route('/quiz')
def quiz_home():
    """Quiz selection page"""
    try:
        user_id = get_user_id()
        
        # Available subjects
        subjects = [
            {'id': 'math', 'name': 'Mathematics', 'icon': '🔢'},
            {'id': 'science', 'name': 'Science', 'icon': '🔬'},
            {'id': 'history', 'name': 'History', 'icon': '📚'},
            {'id': 'language', 'name': 'Language Arts', 'icon': '📝'},
            {'id': 'programming', 'name': 'Programming', 'icon': '💻'},
        ]
        
        return render_template('quiz_home.html', subjects=subjects, user_id=user_id)
    except Exception as e:
        logger.error(f"Quiz home error: {e}")
        return f"""
        <html>
        <head><title>Quiz Selection - NeuroPulse</title></head>
        <body style="font-family: Arial, sans-serif; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <div style="max-width: 800px; margin: 0 auto;">
                <h1>🎯 Select a Quiz Topic</h1>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0;">
                    <a href="/quiz/math" style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; text-decoration: none; color: white; text-align: center;">
                        <div style="font-size: 3em;">🔢</div>
                        <h3>Mathematics</h3>
                    </a>
                    <a href="/quiz/science" style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; text-decoration: none; color: white; text-align: center;">
                        <div style="font-size: 3em;">🔬</div>
                        <h3>Science</h3>
                    </a>
                    <a href="/quiz/programming" style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; text-decoration: none; color: white; text-align: center;">
                        <div style="font-size: 3em;">💻</div>
                        <h3>Programming</h3>
                    </a>
                </div>
                <p><a href="/" style="color: #FFE082;">← Back to Dashboard</a></p>
            </div>
        </body>
        </html>
        """

@app.route('/quiz/<subject>')
def start_quiz(subject):
    """Start a quiz for a specific subject"""
    try:
        user_id = get_user_id()
        quiz_id = str(uuid.uuid4())
        
        # Store quiz session
        session['current_quiz_id'] = quiz_id
        session['quiz_subject'] = subject
        session['current_question'] = 0
        session['correct_count'] = 0
        session['total_questions'] = 10
        session['quiz_start_time'] = datetime.now().isoformat()
        
        # Sample questions based on subject
        questions = get_sample_questions(subject)
        session['quiz_questions'] = questions
        
        return redirect(url_for('quiz_question', question_num=1))
        
    except Exception as e:
        logger.error(f"Start quiz error: {e}")
        return f"<h1>Error starting quiz: {e}</h1><a href='/quiz'>Try again</a>"

@app.route('/quiz/question/<int:question_num>')
def quiz_question(question_num):
    """Display a quiz question"""
    try:
        if 'current_quiz_id' not in session:
            return redirect(url_for('quiz_home'))
        
        questions = session.get('quiz_questions', [])
        if question_num > len(questions):
            return redirect(url_for('quiz_results'))
        
        question = questions[question_num - 1]
        total_questions = len(questions)
        
        return f"""
        <html>
        <head><title>Question {question_num} - NeuroPulse Quiz</title></head>
        <body style="font-family: Arial, sans-serif; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <div style="max-width: 800px; margin: 0 auto;">
                <div style="margin-bottom: 20px;">
                    <span>Question {question_num} of {total_questions}</span>
                    <div style="background: rgba(255,255,255,0.2); height: 4px; border-radius: 2px; margin: 10px 0;">
                        <div style="background: #4CAF50; height: 100%; width: {(question_num/total_questions)*100}%; border-radius: 2px;"></div>
                    </div>
                </div>
                
                <h2>{question['question']}</h2>
                
                <form method="POST" action="/quiz/submit">
                    <input type="hidden" name="question_num" value="{question_num}">
                    <input type="hidden" name="correct_answer" value="{question['correct']}">
                    
                    <div style="margin: 20px 0;">
                        {generate_options_html(question['options'])}
                    </div>
                    
                    <button type="submit" style="background: #4CAF50; color: white; padding: 15px 30px; border: none; border-radius: 25px; font-size: 16px; cursor: pointer;">
                        Submit Answer
                    </button>
                </form>
                
                <p><a href="/quiz" style="color: #FFE082;">← End Quiz</a></p>
            </div>
        </body>
        </html>
        """
        
    except Exception as e:
        logger.error(f"Quiz question error: {e}")
        return f"<h1>Error loading question: {e}</h1><a href='/quiz'>Back to Quiz Home</a>"

@app.route('/quiz/submit', methods=['POST'])
def submit_answer():
    """Submit a quiz answer"""
    try:
        question_num = int(request.form['question_num'])
        user_answer = request.form['answer']
        correct_answer = request.form['correct_answer']
        
        is_correct = user_answer == correct_answer
        if is_correct:
            session['correct_count'] = session.get('correct_count', 0) + 1
        
        session['current_question'] = question_num
        
        # Check if quiz is complete
        total_questions = session.get('total_questions', 10)
        if question_num >= total_questions:
            return redirect(url_for('quiz_results'))
        else:
            return redirect(url_for('quiz_question', question_num=question_num + 1))
            
    except Exception as e:
        logger.error(f"Submit answer error: {e}")
        return f"<h1>Error submitting answer: {e}</h1><a href='/quiz'>Back to Quiz Home</a>"

@app.route('/quiz/results')
def quiz_results():
    """Show quiz results"""
    try:
        if 'current_quiz_id' not in session:
            return redirect(url_for('quiz_home'))
        
        correct_count = session.get('correct_count', 0)
        total_questions = session.get('total_questions', 10)
        accuracy = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        subject = session.get('quiz_subject', 'Unknown')
        
        # Update session stats
        session['total_sessions'] = session.get('total_sessions', 0) + 1
        session['total_correct'] = session.get('total_correct', 0) + correct_count
        session['accuracy'] = accuracy
        
        # Clear current quiz
        for key in ['current_quiz_id', 'quiz_subject', 'current_question', 'correct_count', 'quiz_questions']:
            session.pop(key, None)
        
        return f"""
        <html>
        <head><title>Quiz Results - NeuroPulse</title></head>
        <body style="font-family: Arial, sans-serif; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <div style="max-width: 800px; margin: 0 auto; text-align: center;">
                <h1>🎉 Quiz Complete!</h1>
                <div style="background: rgba(255,255,255,0.1); padding: 30px; border-radius: 20px; margin: 30px 0;">
                    <h2>Subject: {subject.title()}</h2>
                    <h3>Score: {correct_count}/{total_questions}</h3>
                    <h3>Accuracy: {accuracy:.1f}%</h3>
                    
                    <div style="margin: 20px 0;">
                        {get_performance_message(accuracy)}
                    </div>
                </div>
                
                <div style="margin: 30px 0;">
                    <a href="/quiz/{subject}" style="background: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; margin: 10px;">Try Again</a>
                    <a href="/quiz" style="background: #2196F3; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; margin: 10px;">New Subject</a>
                    <a href="/" style="background: #FF9800; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; margin: 10px;">Dashboard</a>
                </div>
            </div>
        </body>
        </html>
        """
        
    except Exception as e:
        logger.error(f"Quiz results error: {e}")
        return f"<h1>Error loading results: {e}</h1><a href='/'>Back to Home</a>"

def get_sample_questions(subject):
    """Get sample questions for a subject"""
    questions_db = {
        'math': [
            {'question': 'What is 15 + 27?', 'options': ['42', '41', '43', '40'], 'correct': '42'},
            {'question': 'What is 8 × 7?', 'options': ['54', '56', '58', '52'], 'correct': '56'},
            {'question': 'What is 144 ÷ 12?', 'options': ['11', '12', '13', '14'], 'correct': '12'},
            {'question': 'What is the square root of 64?', 'options': ['6', '7', '8', '9'], 'correct': '8'},
            {'question': 'What is 25% of 80?', 'options': ['15', '20', '25', '30'], 'correct': '20'},
        ],
        'science': [
            {'question': 'What is the chemical symbol for water?', 'options': ['H2O', 'CO2', 'O2', 'NaCl'], 'correct': 'H2O'},
            {'question': 'How many planets are in our solar system?', 'options': ['7', '8', '9', '10'], 'correct': '8'},
            {'question': 'What gas do plants absorb from the atmosphere?', 'options': ['Oxygen', 'Nitrogen', 'Carbon Dioxide', 'Hydrogen'], 'correct': 'Carbon Dioxide'},
            {'question': 'What is the fastest land animal?', 'options': ['Lion', 'Cheetah', 'Leopard', 'Tiger'], 'correct': 'Cheetah'},
            {'question': 'What is the hardest natural substance?', 'options': ['Gold', 'Iron', 'Diamond', 'Silver'], 'correct': 'Diamond'},
        ],
        'programming': [
            {'question': 'Which language is known as the "language of the web"?', 'options': ['Python', 'JavaScript', 'Java', 'C++'], 'correct': 'JavaScript'},
            {'question': 'What does HTML stand for?', 'options': ['Hypertext Markup Language', 'High-Tech Modern Language', 'Home Tool Markup Language', 'Hyperlink and Text Markup Language'], 'correct': 'Hypertext Markup Language'},
            {'question': 'Which symbol is used for comments in Python?', 'options': ['//', '#', '/*', '--'], 'correct': '#'},
            {'question': 'What is a function in programming?', 'options': ['A variable', 'A reusable block of code', 'A type of loop', 'A data structure'], 'correct': 'A reusable block of code'},
            {'question': 'Which of these is NOT a programming language?', 'options': ['Python', 'JavaScript', 'Photoshop', 'Java'], 'correct': 'Photoshop'},
        ]
    }
    
    return questions_db.get(subject, questions_db['math'])[:10]

def generate_options_html(options):
    """Generate HTML for multiple choice options"""
    html = ""
    for i, option in enumerate(options):
        html += f"""
        <div style="margin: 10px 0;">
            <label style="display: block; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px; cursor: pointer;">
                <input type="radio" name="answer" value="{option}" required style="margin-right: 10px;">
                {option}
            </label>
        </div>
        """
    return html

def get_performance_message(accuracy):
    """Get performance message based on accuracy"""
    if accuracy >= 90:
        return "🌟 Excellent! You're a star!"
    elif accuracy >= 80:
        return "👍 Great job! Keep it up!"
    elif accuracy >= 70:
        return "😊 Good work! You're improving!"
    elif accuracy >= 60:
        return "📚 Not bad! Keep studying!"
    else:
        return "💪 Keep practicing! You'll get better!"

@app.route('/subjects')
def subjects():
    """Show available subjects"""
    return f"""
    <html>
    <head><title>Subjects - NeuroPulse</title></head>
    <body style="font-family: Arial, sans-serif; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
        <div style="max-width: 800px; margin: 0 auto;">
            <h1>📚 Available Subjects</h1>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0;">
                <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px;">
                    <h3>🔢 Mathematics</h3>
                    <p>Arithmetic, algebra, geometry, and more</p>
                    <a href="/quiz/math" style="color: #4CAF50;">Start Quiz →</a>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px;">
                    <h3>🔬 Science</h3>
                    <p>Biology, chemistry, physics, and earth science</p>
                    <a href="/quiz/science" style="color: #4CAF50;">Start Quiz →</a>
                </div>
                <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px;">
                    <h3>💻 Programming</h3>
                    <p>Coding concepts, languages, and best practices</p>
                    <a href="/quiz/programming" style="color: #4CAF50;">Start Quiz →</a>
                </div>
            </div>
            <p><a href="/" style="color: #FFE082;">← Back to Dashboard</a></p>
        </div>
    </body>
    </html>
    """

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'status': 'online',
        'version': '1.0.0',
        'features': {
            'quizzes': True,
            'subjects': True,
            'analytics': True
        },
        'timestamp': datetime.now().isoformat()
    })

logger.info("Core routes initialized successfully")