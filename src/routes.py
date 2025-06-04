from flask import render_template, request, jsonify, session, redirect, url_for
from app import app, db
from models import User, QuizSession, Question, Subject, LearningProgress
from quiz_data import get_quiz_data, get_quiz_by_id
from quiz_data_backup import get_questions_by_difficulty, get_adaptive_question_set
# Import advanced learning systems with error handling
try:
    from spaced_repetition_engine import spaced_repetition_engine
    from adaptive_difficulty_engine import adaptive_difficulty_engine
    from personalized_dashboard import personalized_dashboard
    from voice_navigation_system import voice_navigation_system
    from onboarding_system import onboarding_system
    ADVANCED_FEATURES = True
except ImportError:
    ADVANCED_FEATURES = False
import random
import logging
import uuid
from datetime import datetime

@app.route('/')
def index():
    """Enhanced main dashboard with all integrated features"""
    try:
        # Get user session data (for demo purposes, using session-based user)
        user_id = session.get('user_id', 'demo_user')
        
        # Initialize user systems if needed
        dashboard_config = personalized_dashboard.initialize_user_dashboard(user_id)
        onboarding_status = onboarding_system.initialize_user_onboarding(user_id)
        voice_system = voice_navigation_system.initialize_voice_system(user_id)
        
        # Get learning analytics and progress
        learning_insights = {
            'spaced_repetition_due': len(spaced_repetition_engine.get_cards_due_for_review(user_id)),
            'energy_level': dashboard_config['energy']['current_level'],
            'current_mood': dashboard_config['mood']['current'],
            'theme': dashboard_config['theme']
        }
        
        # Check if onboarding needed
        if not onboarding_status.get('onboarding_complete', False):
            return render_template('onboarding.html', 
                                 onboarding_status=onboarding_status,
                                 dashboard_config=dashboard_config)
        
        return render_template('index.html', 
                             dashboard_config=dashboard_config,
                             learning_insights=learning_insights,
                             voice_enabled=voice_system.get('voice_enabled', True))
    
    except Exception as e:
        logging.error(f"Dashboard error: {e}")
        return redirect(url_for('subject_browser'))

@app.route('/legacy-quizzes')
def legacy_quizzes():
    """Legacy quiz interface for backward compatibility"""
    quizzes = get_quiz_data()
    return render_template('index.html', quizzes=quizzes)

@app.route('/quiz/<int:quiz_id>')
@app.route('/quiz/<int:quiz_id>/<difficulty>')
def quiz(quiz_id, difficulty='beginner'):
    """Start or continue a quiz session with adaptive difficulty"""
    quiz_data = get_quiz_by_id(quiz_id)
    if not quiz_data:
        return "Quiz not found", 404
    
    # Initialize session data for this quiz
    session['current_quiz_id'] = quiz_id
    session['current_question'] = 0
    session['answers'] = []
    session['correct_count'] = 0
    session['difficulty_level'] = difficulty
    session['streak_count'] = 0
    session['total_confidence'] = 0
    
    return render_template('quiz.html', quiz=quiz_data, difficulty=difficulty)

@app.route('/api/quiz/<int:quiz_id>/question/<int:question_num>')
def get_question(quiz_id, question_num):
    """Get a specific question from a quiz with adaptive difficulty"""
    difficulty = session.get('difficulty_level', 'beginner')
    
    # Try to get enhanced questions from backup data
    try:
        enhanced_questions = get_questions_by_difficulty(quiz_id, difficulty)
        if enhanced_questions and question_num < len(enhanced_questions):
            question = enhanced_questions[question_num]
            return jsonify({
                'question': question,
                'question_number': question_num + 1,
                'total_questions': len(enhanced_questions),
                'quiz_title': f"Enhanced Quiz (Level: {difficulty.title()})",
                'difficulty': difficulty,
                'has_aha_moment': 'aha_moment' in question
            })
    except:
        pass
    
    # Fallback to original questions
    quiz_data = get_quiz_by_id(quiz_id)
    if not quiz_data or question_num >= len(quiz_data['questions']):
        return jsonify({'error': 'Question not found'}), 404
    
    question = quiz_data['questions'][question_num]
    return jsonify({
        'question': question,
        'question_number': question_num + 1,
        'total_questions': len(quiz_data['questions']),
        'quiz_title': quiz_data['title'],
        'difficulty': difficulty,
        'has_aha_moment': False
    })

@app.route('/api/quiz/submit-answer', methods=['POST'])
def submit_answer():
    """Submit an answer and get feedback"""
    data = request.get_json()
    
    if 'current_quiz_id' not in session:
        return jsonify({'error': 'No active quiz session'}), 400
    
    quiz_id = session['current_quiz_id']
    question_num = session.get('current_question', 0)
    
    quiz_data = get_quiz_by_id(quiz_id)
    if not quiz_data or question_num >= len(quiz_data['questions']):
        return jsonify({'error': 'Invalid question'}), 400
    
    question = quiz_data['questions'][question_num]
    selected_answer = data.get('answer')
    confidence_level = data.get('confidence', 3)
    
    # Check if answer is correct
    is_correct = selected_answer == question['correct_answer']
    
    # Enhanced gamification tracking
    if is_correct:
        session['correct_count'] = session.get('correct_count', 0) + 1
        session['streak_count'] = session.get('streak_count', 0) + 1
        # Bonus points for high confidence + correct answers
        confidence_bonus = confidence_level if confidence_level >= 4 else 0
    else:
        session['streak_count'] = 0
        confidence_bonus = 0
    
    session['total_confidence'] = session.get('total_confidence', 0) + confidence_level
    
    # Store enhanced answer data
    answer_data = {
        'question_num': question_num,
        'selected_answer': selected_answer,
        'correct_answer': question['correct_answer'],
        'is_correct': is_correct,
        'confidence': confidence_level,
        'confidence_bonus': confidence_bonus,
        'streak_at_time': session.get('streak_count', 0)
    }
    
    if 'answers' not in session:
        session['answers'] = []
    session['answers'].append(answer_data)
    
    # Move to next question
    session['current_question'] = question_num + 1
    
    # Determine if quiz is complete
    is_complete = session['current_question'] >= len(quiz_data['questions'])
    
    response = {
        'is_correct': is_correct,
        'correct_answer': question['correct_answer'],
        'explanation': question.get('explanation', ''),
        'aha_moment': question.get('aha_moment', ''),
        'is_complete': is_complete,
        'next_question': session['current_question'] + 1 if not is_complete else None,
        'current_score': session.get('correct_count', 0),
        'streak_count': session.get('streak_count', 0),
        'confidence_bonus': confidence_bonus,
        'avg_confidence': round(session.get('total_confidence', 0) / len(session.get('answers', [1])), 1)
    }
    
    # Add celebration triggers based on testing feedback
    if is_correct and session.get('streak_count', 0) >= 3:
        response['celebration'] = 'streak'
        response['celebration_message'] = f"Amazing! {session.get('streak_count')} in a row!"
    elif is_correct and confidence_level >= 4:
        response['celebration'] = 'confident'
        response['celebration_message'] = "Confident and correct - excellent!"
    
    if is_complete:
        response['results_url'] = f'/results/{quiz_id}'
    
    session.permanent = True
    return jsonify(response)

@app.route('/results/<int:quiz_id>')
def results(quiz_id):
    """Show quiz results"""
    if 'current_quiz_id' not in session or session['current_quiz_id'] != quiz_id:
        return "No quiz session found", 404
    
    quiz_data = get_quiz_by_id(quiz_id)
    if not quiz_data:
        return "Quiz not found", 404
    
    answers = session.get('answers', [])
    correct_count = session.get('correct_count', 0)
    total_questions = len(quiz_data['questions'])
    
    # Calculate performance metrics
    score_percentage = (correct_count / total_questions) * 100 if total_questions > 0 else 0
    
    # Calculate confidence accuracy
    high_confidence_correct = sum(1 for ans in answers if ans['confidence'] >= 4 and ans['is_correct'])
    high_confidence_total = sum(1 for ans in answers if ans['confidence'] >= 4)
    confidence_accuracy = (high_confidence_correct / high_confidence_total) * 100 if high_confidence_total > 0 else 0
    
    results_data = {
        'quiz': quiz_data,
        'answers': answers,
        'correct_count': correct_count,
        'total_questions': total_questions,
        'score_percentage': round(score_percentage, 1),
        'confidence_accuracy': round(confidence_accuracy, 1)
    }
    
    return render_template('results.html', **results_data)

@app.route('/api/quiz/reset')
def reset_quiz():
    """Reset current quiz session"""
    session.pop('current_quiz_id', None)
    session.pop('current_question', None)
    session.pop('answers', None)
    session.pop('correct_count', None)
    return jsonify({'success': True})
