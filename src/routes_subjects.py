"""
Subject management routes for NeuroPulse universal learning platform
"""

from flask import render_template, request, jsonify, session
from app import app
from subject_manager import subject_manager
from ai_question_generator import ai_generator
import uuid

@app.route('/subjects')
def subject_browser():
    """Browse all available subject categories"""
    subjects = subject_manager.get_all_subjects()
    return render_template('subjects.html', subjects=subjects)

@app.route('/subjects/<category>')
def subject_category(category):
    """View topics within a subject category"""
    subject_data = subject_manager.get_subject_by_category(category)
    if not subject_data:
        return "Subject category not found", 404
    
    return render_template('subject_category.html', 
                         category=category, 
                         subject_data=subject_data)

@app.route('/learn/<category>/<topic>')
@app.route('/learn/<category>/<topic>/<difficulty>')
@app.route('/learn/<category>/<topic>/<difficulty>/<int:session_length>')
def start_learning_session(category, topic, difficulty='foundation', session_length=10):
    """Start an adaptive learning session"""
    topic_details = subject_manager.get_topic_details(category, topic)
    if not topic_details:
        return "Topic not found", 404
    
    # Generate user ID if not exists
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    user_id = session['user_id']
    user_progress = subject_manager.get_user_progress(user_id, category, topic)
    
    # Initialize learning session
    session['learning_session'] = {
        'category': category,
        'topic': topic,
        'difficulty': difficulty,
        'session_length': session_length,
        'current_question': 0,
        'answers': [],
        'correct_count': 0,
        'start_time': user_progress.get('last_session'),
        'session_id': str(uuid.uuid4())
    }
    
    return render_template('learning_session.html', 
                         category=category,
                         topic=topic,
                         topic_details=topic_details,
                         difficulty=difficulty,
                         session_length=session_length,
                         user_progress=user_progress)

@app.route('/api/learning/generate-question', methods=['POST'])
def generate_adaptive_question():
    """Generate questions adaptively based on topic and difficulty"""
    data = request.get_json()
    
    if 'learning_session' not in session:
        return jsonify({'error': 'No active learning session'}), 400
    
    learning_session = session['learning_session']
    category = learning_session['category']
    topic = learning_session['topic']
    difficulty = learning_session['difficulty']
    question_num = learning_session['current_question']
    
    # Generate AI-powered questions for the specific subject and topic
    try:
        ai_questions = ai_generator.generate_questions(
            subject=f"{category}_{topic}",
            topic=topic.replace('_', ' '),
            difficulty=difficulty,
            question_count=1,
            learning_objectives=f"Understanding {topic.replace('_', ' ')} at {difficulty} level"
        )
        
        if ai_questions and len(ai_questions) > 0:
            question_data = ai_questions[0]
            question_data.update({
                'category': category,
                'topic': topic,
                'ai_generated': True
            })
        else:
            # Fallback to subject-appropriate content
            question_data = ai_generator._get_fallback_questions(f"{category}_{topic}", topic, difficulty)[0]
            question_data.update({
                'category': category,
                'topic': topic,
                'ai_generated': False
            })
            
    except Exception as e:
        # Emergency fallback
        question_data = {
            'question': f"What is a fundamental concept in {topic.replace('_', ' ')}?",
            'options': [
                'Core principles and foundations',
                'Advanced applications only', 
                'Theoretical concepts without practice',
                'Memorization of facts'
            ],
            'correct_answer': 'Core principles and foundations',
            'explanation': f"Understanding core principles is essential for building expertise in {topic.replace('_', ' ')}.",
            'aha_moment': f"Strong foundations make complex {topic.replace('_', ' ')} concepts much easier to understand.",
            'difficulty_level': difficulty,
            'category': category,
            'topic': topic,
            'ai_generated': False,
            'error_fallback': True
        }
    
    return jsonify({
        'question': question_data,
        'question_number': question_num + 1,
        'total_questions': learning_session['session_length'],
        'session_progress': (question_num / learning_session['session_length']) * 100
    })

@app.route('/api/learning/submit-answer', methods=['POST'])
def submit_learning_answer():
    """Submit answer in adaptive learning session"""
    data = request.get_json()
    
    if 'learning_session' not in session:
        return jsonify({'error': 'No active learning session'}), 400
    
    learning_session = session['learning_session']
    selected_answer = data.get('answer')
    confidence_level = data.get('confidence', 3)
    question_data = data.get('question_data', {})
    
    # Simulate answer checking (will be replaced with actual logic)
    is_correct = selected_answer == question_data.get('correct_answer')
    
    # Enhanced session tracking
    if is_correct:
        learning_session['correct_count'] += 1
    
    answer_record = {
        'question_num': learning_session['current_question'],
        'selected_answer': selected_answer,
        'correct_answer': question_data.get('correct_answer'),
        'is_correct': is_correct,
        'confidence': confidence_level,
        'topic': learning_session['topic'],
        'difficulty': learning_session['difficulty']
    }
    
    learning_session['answers'].append(answer_record)
    learning_session['current_question'] += 1
    
    # Check if session is complete
    is_complete = learning_session['current_question'] >= learning_session['session_length']
    
    response = {
        'is_correct': is_correct,
        'explanation': question_data.get('explanation', ''),
        'aha_moment': question_data.get('aha_moment', ''),
        'is_complete': is_complete,
        'current_score': learning_session['correct_count'],
        'session_progress': (learning_session['current_question'] / learning_session['session_length']) * 100
    }
    
    if is_complete:
        # Update user progress
        user_id = session.get('user_id')
        session_data = {
            'questions_answered': learning_session['session_length'],
            'correct_answers': learning_session['correct_count'],
            'session_completed': True,
            'session_time_minutes': 15  # Estimate for now
        }
        
        updated_progress = subject_manager.update_user_progress(
            user_id, 
            learning_session['category'], 
            learning_session['topic'], 
            session_data
        )
        
        response['session_complete'] = True
        response['updated_progress'] = updated_progress
        response['results_url'] = f"/learning-results/{learning_session['category']}/{learning_session['topic']}"
    
    session['learning_session'] = learning_session
    session.permanent = True
    
    return jsonify(response)

@app.route('/learning-results/<category>/<topic>')
def learning_results(category, topic):
    """Show results after learning session"""
    if 'learning_session' not in session:
        return "No session found", 404
    
    learning_session = session['learning_session']
    user_id = session.get('user_id')
    user_progress = subject_manager.get_user_progress(user_id, category, topic)
    
    # Generate learning path for next steps
    learning_path = subject_manager.generate_learning_path(category, topic, user_progress['level'])
    
    return render_template('learning_results.html',
                         session_data=learning_session,
                         user_progress=user_progress,
                         learning_path=learning_path,
                         category=category,
                         topic=topic)

@app.route('/profile')
def user_profile():
    """User learning profile and progress dashboard"""
    user_id = session.get('user_id')
    if not user_id:
        session['user_id'] = str(uuid.uuid4())
        user_id = session['user_id']
    
    # Get all user progress across subjects
    all_progress = {}
    for user_key, progress in subject_manager.user_progress.items():
        if user_key.startswith(user_id):
            parts = user_key.split('_')
            if len(parts) >= 3:
                category = parts[1]
                topic = parts[2]
                if category not in all_progress:
                    all_progress[category] = {}
                all_progress[category][topic] = progress
    
    return render_template('user_profile.html', 
                         user_progress=all_progress,
                         subjects=subject_manager.get_all_subjects())

@app.route('/leaderboard/<category>/<topic>')
def topic_leaderboard(category, topic):
    """Show leaderboard for specific topic"""
    accuracy_board = subject_manager.get_leaderboard(category, topic, 'accuracy')
    streak_board = subject_manager.get_leaderboard(category, topic, 'streak')
    questions_board = subject_manager.get_leaderboard(category, topic, 'questions')
    
    return render_template('leaderboard.html',
                         category=category,
                         topic=topic,
                         accuracy_board=accuracy_board,
                         streak_board=streak_board,
                         questions_board=questions_board)

@app.route('/api/subjects/add-custom', methods=['POST'])
def add_custom_subject():
    """Allow users to request custom subjects"""
    data = request.get_json()
    
    custom_request = {
        'category': data.get('category'),
        'topic_name': data.get('topic_name'),
        'subtopics': data.get('subtopics', []),
        'user_id': session.get('user_id'),
        'requested_at': 'now'
    }
    
    # For now, just acknowledge the request
    # In production, this would queue the request for content creation
    
    return jsonify({
        'success': True,
        'message': f"Custom topic '{custom_request['topic_name']}' has been requested and will be available soon!"
    })