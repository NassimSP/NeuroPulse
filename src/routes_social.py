"""
Social Learning Routes for NeuroPulse
Handles collaborative challenges, study groups, peer comparison, and social features
"""

from flask import render_template, request, jsonify, session, redirect, url_for
from app import app
from social_learning import social_manager
from subject_manager import subject_manager
from real_time_chat import chat_manager
from video_sessions import video_manager
from analytics_dashboard import analytics_manager
from lms_integration import lms_manager
from advanced_reporting import reporting_manager
from mobile_responsive import mobile_manager
from ai_personalization_engine import personalization_engine
from advanced_assessment_system import assessment_manager
from enterprise_integration import enterprise_manager
from ai_tutoring_system import ai_tutor
from advanced_collaboration import collaboration_manager
from gamification_system import gamification_engine
from security_compliance import security_manager
from performance_optimization import performance_manager
from immersive_technologies import immersive_manager
import uuid

@app.route('/social')
def social_dashboard():
    """Main social learning dashboard"""
    user_id = session.get('user_id')
    if not user_id:
        session['user_id'] = str(uuid.uuid4())
        user_id = session['user_id']
    
    # Get user's social achievements
    achievements = social_manager.get_collaborative_achievements(user_id)
    
    # Get active challenges
    active_challenges = social_manager.get_active_challenges()[:6]  # Show top 6
    
    # Get user's study groups
    user_groups = []
    for group_id, group in social_manager.study_groups.items():
        if user_id in group['members']:
            user_groups.append(group)
    
    return render_template('social_dashboard.html',
                         achievements=achievements,
                         active_challenges=active_challenges,
                         user_groups=user_groups,
                         user_id=user_id)

@app.route('/challenges')
def challenges_browser():
    """Browse available collaborative challenges"""
    subject_filter = request.args.get('subject')
    difficulty_filter = request.args.get('difficulty')
    
    challenges = social_manager.get_active_challenges(subject_filter)
    
    # Filter by difficulty if specified
    if difficulty_filter:
        challenges = [c for c in challenges if c['difficulty_level'] == difficulty_filter]
    
    # Get subject categories for filter
    subjects = subject_manager.get_all_subjects()
    
    return render_template('challenges_browser.html',
                         challenges=challenges,
                         subjects=subjects,
                         current_filters={'subject': subject_filter, 'difficulty': difficulty_filter})

@app.route('/challenges/create')
def create_challenge():
    """Create new collaborative challenge form"""
    subjects = subject_manager.get_all_subjects()
    return render_template('create_challenge.html', subjects=subjects)

@app.route('/api/challenges/create', methods=['POST'])
def api_create_challenge():
    """API endpoint to create new challenge"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User session required'}), 400
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['title', 'subject_category', 'topic', 'question_count']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    challenge_id = social_manager.create_challenge(user_id, data)
    
    return jsonify({
        'success': True,
        'challenge_id': challenge_id,
        'message': 'Challenge created successfully!'
    })

@app.route('/challenges/<challenge_id>')
def challenge_details(challenge_id):
    """View challenge details and leaderboard"""
    if challenge_id not in social_manager.challenges:
        return "Challenge not found", 404
    
    challenge = social_manager.challenges[challenge_id]
    user_id = session.get('user_id')
    
    # Check if user is participant
    is_participant = user_id in challenge['participants']
    user_progress = challenge['participants'].get(user_id, {}).get('progress', {}) if is_participant else None
    
    return render_template('challenge_details.html',
                         challenge=challenge,
                         is_participant=is_participant,
                         user_progress=user_progress,
                         user_id=user_id)

@app.route('/api/challenges/<challenge_id>/join', methods=['POST'])
def join_challenge(challenge_id):
    """Join a collaborative challenge"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User session required'}), 400
    
    data = request.get_json() or {}
    user_name = data.get('user_name', f"Learner_{user_id[:8]}")
    
    success = social_manager.join_challenge(challenge_id, user_id, user_name)
    
    if success:
        return jsonify({'success': True, 'message': 'Successfully joined challenge!'})
    else:
        return jsonify({'error': 'Unable to join challenge. It may be full or inactive.'}), 400

@app.route('/challenges/<challenge_id>/compete')
def challenge_compete(challenge_id):
    """Start competing in a challenge"""
    user_id = session.get('user_id')
    if not user_id or challenge_id not in social_manager.challenges:
        return redirect(url_for('challenges_browser'))
    
    challenge = social_manager.challenges[challenge_id]
    
    # Check if user is participant
    if user_id not in challenge['participants']:
        return redirect(url_for('challenge_details', challenge_id=challenge_id))
    
    # Set up challenge session
    session['challenge_session'] = {
        'challenge_id': challenge_id,
        'current_question': 0,
        'answers': [],
        'start_time': 'now',
        'session_type': 'challenge'
    }
    
    return render_template('challenge_session.html',
                         challenge=challenge,
                         user_id=user_id)

@app.route('/study-groups')
def study_groups_browser():
    """Browse available study groups"""
    subject_filter = request.args.get('subject')
    
    # Get all public study groups
    public_groups = []
    for group_id, group in social_manager.study_groups.items():
        if group['privacy'] == 'public':
            if not subject_filter or group['subject_focus'] == subject_filter:
                group_info = group.copy()
                group_info['member_count'] = len(group['members'])
                group_info['spots_available'] = group['max_members'] - len(group['members'])
                public_groups.append(group_info)
    
    subjects = subject_manager.get_all_subjects()
    
    return render_template('study_groups_browser.html',
                         study_groups=public_groups,
                         subjects=subjects,
                         current_filter=subject_filter)

@app.route('/study-groups/create')
def create_study_group():
    """Create new study group form"""
    subjects = subject_manager.get_all_subjects()
    return render_template('create_study_group.html', subjects=subjects)

@app.route('/api/study-groups/create', methods=['POST'])
def api_create_study_group():
    """API endpoint to create new study group"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User session required'}), 400
    
    data = request.get_json()
    
    # Validate required fields
    if not data.get('name') or not data.get('subject_focus'):
        return jsonify({'error': 'Group name and subject focus are required'}), 400
    
    group_id = social_manager.create_study_group(user_id, data)
    
    return jsonify({
        'success': True,
        'group_id': group_id,
        'message': 'Study group created successfully!'
    })

@app.route('/study-groups/<group_id>')
def study_group_details(group_id):
    """View study group details"""
    if group_id not in social_manager.study_groups:
        return "Study group not found", 404
    
    group = social_manager.study_groups[group_id]
    user_id = session.get('user_id')
    
    is_member = user_id in group['members']
    user_role = group['members'].get(user_id, {}).get('role') if is_member else None
    
    return render_template('study_group_details.html',
                         group=group,
                         is_member=is_member,
                         user_role=user_role,
                         user_id=user_id)

@app.route('/api/study-groups/<group_id>/join', methods=['POST'])
def join_study_group(group_id):
    """Join a study group"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User session required'}), 400
    
    data = request.get_json() or {}
    user_name = data.get('user_name', f"Learner_{user_id[:8]}")
    
    success = social_manager.join_study_group(group_id, user_id, user_name)
    
    if success:
        return jsonify({'success': True, 'message': 'Successfully joined study group!'})
    else:
        return jsonify({'error': 'Unable to join study group. It may be full or you may already be a member.'}), 400

@app.route('/peer-comparison/<category>/<topic>')
def peer_comparison(category, topic):
    """View peer comparison for specific topic"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('subject_browser'))
    
    comparison_data = social_manager.get_peer_comparison(user_id, category, topic)
    topic_details = subject_manager.get_topic_details(category, topic)
    
    return render_template('peer_comparison.html',
                         comparison_data=comparison_data,
                         topic_details=topic_details,
                         category=category,
                         topic=topic)

@app.route('/find-study-partners/<category>/<topic>')
def find_study_partners(category, topic):
    """Find study partners for specific topic"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('subject_browser'))
    
    partners = social_manager.suggest_study_partners(user_id, category, topic)
    topic_details = subject_manager.get_topic_details(category, topic)
    
    return render_template('study_partners.html',
                         partners=partners,
                         topic_details=topic_details,
                         category=category,
                         topic=topic)

@app.route('/api/social/update-challenge-progress', methods=['POST'])
def update_challenge_progress():
    """Update progress in active challenge"""
    user_id = session.get('user_id')
    challenge_session = session.get('challenge_session')
    
    if not user_id or not challenge_session:
        return jsonify({'error': 'No active challenge session'}), 400
    
    data = request.get_json()
    challenge_id = challenge_session['challenge_id']
    
    success = social_manager.update_challenge_progress(challenge_id, user_id, data)
    
    if success:
        # Get updated leaderboard position
        challenge = social_manager.challenges[challenge_id]
        user_position = None
        for i, entry in enumerate(challenge['leaderboard']):
            if entry['user_id'] == user_id:
                user_position = i + 1
                break
        
        return jsonify({
            'success': True,
            'leaderboard_position': user_position,
            'total_participants': len(challenge['participants'])
        })
    else:
        return jsonify({'error': 'Failed to update progress'}), 400

@app.route('/social-achievements')
def social_achievements():
    """View user's social learning achievements"""
    user_id = session.get('user_id')
    if not user_id:
        session['user_id'] = str(uuid.uuid4())
        user_id = session['user_id']
    
    achievements = social_manager.get_collaborative_achievements(user_id)
    
    return render_template('social_achievements.html',
                         achievements=achievements,
                         user_id=user_id)

@app.route('/api/social/start-team-challenge', methods=['POST'])
def start_team_challenge():
    """Create a team-based challenge"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User session required'}), 400
    
    data = request.get_json()
    team_size = data.get('team_size', 4)
    
    challenge_id = social_manager.create_team_challenge(user_id, team_size, data)
    
    return jsonify({
        'success': True,
        'challenge_id': challenge_id,
        'message': 'Team challenge created successfully!'
    })

@app.route('/leaderboards')
def global_leaderboards():
    """View global leaderboards across all subjects"""
    # Get top performers across all subjects
    all_leaderboards = {}
    subjects = subject_manager.get_all_subjects()
    
    for category_key, category_data in subjects.items():
        category_boards = {}
        for topic_key, topic_data in category_data['topics'].items():
            accuracy_board = subject_manager.get_leaderboard(category_key, topic_key, 'accuracy')
            if accuracy_board:
                category_boards[topic_key] = {
                    'name': topic_data['name'],
                    'top_performers': accuracy_board[:3]
                }
        if category_boards:
            all_leaderboards[category_key] = {
                'name': category_data['name'],
                'topics': category_boards
            }
    
    return render_template('global_leaderboards.html',
                         leaderboards=all_leaderboards)

# Chat System Routes
@app.route('/chat')
def chat_dashboard():
    """Main chat dashboard showing all user's chat rooms"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('social_dashboard'))
    
    user_chat_rooms = chat_manager.get_user_chat_rooms(user_id)
    
    return render_template('chat_dashboard.html',
                         chat_rooms=user_chat_rooms,
                         user_id=user_id)

@app.route('/chat/<chat_room_id>')
def chat_room(chat_room_id):
    """View specific chat room"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('social_dashboard'))
    
    if chat_room_id not in chat_manager.chat_rooms:
        return "Chat room not found", 404
    
    chat_room_data = chat_manager.chat_rooms[chat_room_id]
    
    # Check if user is participant
    if user_id not in chat_room_data['participants']:
        return "Access denied", 403
    
    # Get chat history
    messages = chat_manager.get_chat_history(chat_room_id, limit=50)
    
    return render_template('chat_room.html',
                         chat_room=chat_room_data,
                         messages=messages,
                         user_id=user_id)

@app.route('/api/chat/send', methods=['POST'])
def send_chat_message():
    """Send a message to a chat room"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User session required'}), 400
    
    data = request.get_json()
    chat_room_id = data.get('chat_room_id')
    content = data.get('content', '').strip()
    message_type = data.get('type', 'text')
    
    if not chat_room_id or not content:
        return jsonify({'error': 'Chat room ID and content required'}), 400
    
    message = chat_manager.send_message(chat_room_id, user_id, content, message_type)
    
    if 'error' in message:
        return jsonify(message), 400
    
    return jsonify({'success': True, 'message': message})

@app.route('/api/chat/history/<chat_room_id>')
def get_chat_history(chat_room_id):
    """Get chat history for a room"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User session required'}), 400
    
    if chat_room_id not in chat_manager.chat_rooms:
        return jsonify({'error': 'Chat room not found'}), 404
    
    chat_room = chat_manager.chat_rooms[chat_room_id]
    if user_id not in chat_room['participants']:
        return jsonify({'error': 'Access denied'}), 403
    
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    messages = chat_manager.get_chat_history(chat_room_id, limit, offset)
    
    return jsonify({'messages': messages})

@app.route('/api/chat/react', methods=['POST'])
def react_to_message():
    """Add reaction to a message"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User session required'}), 400
    
    data = request.get_json()
    chat_room_id = data.get('chat_room_id')
    message_id = data.get('message_id')
    reaction = data.get('reaction')
    
    if not all([chat_room_id, message_id, reaction]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    success = chat_manager.add_reaction(chat_room_id, message_id, user_id, reaction)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to add reaction'}), 400

@app.route('/api/chat/create-dm', methods=['POST'])
def create_direct_message():
    """Create direct message room between two users"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User session required'}), 400
    
    data = request.get_json()
    other_user_id = data.get('other_user_id')
    
    if not other_user_id:
        return jsonify({'error': 'Other user ID required'}), 400
    
    dm_room_id = chat_manager.create_direct_message_room(user_id, other_user_id)
    
    return jsonify({
        'success': True,
        'chat_room_id': dm_room_id,
        'redirect_url': f'/chat/{dm_room_id}'
    })

@app.route('/api/chat/search/<chat_room_id>')
def search_chat_messages():
    """Search messages in a chat room"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User session required'}), 400
    
    query = request.args.get('q', '').strip()
    limit = request.args.get('limit', 20, type=int)
    
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    
    if chat_room_id not in chat_manager.chat_rooms:
        return jsonify({'error': 'Chat room not found'}), 404
    
    chat_room = chat_manager.chat_rooms[chat_room_id]
    if user_id not in chat_room['participants']:
        return jsonify({'error': 'Access denied'}), 403
    
    results = chat_manager.search_messages(chat_room_id, query, limit)
    
    return jsonify({'results': results})

# Auto-create chat rooms for study groups and challenges
@app.route('/api/social/auto-create-chat', methods=['POST'])
def auto_create_chat_room():
    """Automatically create chat room for study group or challenge"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User session required'}), 400
    
    data = request.get_json()
    room_type = data.get('type')  # 'study_group' or 'challenge'
    room_id = data.get('room_id')
    room_name = data.get('name')
    participants = data.get('participants', [])
    
    if not all([room_type, room_id, room_name]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    chat_room_id = chat_manager.create_chat_room(room_type, room_id, room_name, participants)
    
    return jsonify({
        'success': True,
        'chat_room_id': chat_room_id
    })

# Video Study Session Routes
@app.route('/video-sessions')
def video_sessions_dashboard():
    """Video study sessions dashboard"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('social_dashboard'))
    
    upcoming_sessions = video_manager.get_upcoming_sessions(user_id)
    session_history = video_manager.get_session_history(user_id, limit=10)
    
    return render_template('video_sessions_dashboard.html',
                         upcoming_sessions=upcoming_sessions,
                         session_history=session_history,
                         user_id=user_id)

@app.route('/video-sessions/create')
def create_video_session():
    """Create new video study session form"""
    subjects = subject_manager.get_all_subjects()
    return render_template('create_video_session.html', subjects=subjects)

@app.route('/api/video-sessions/create', methods=['POST'])
def api_create_video_session():
    """API endpoint to create new video session"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User session required'}), 400
    
    data = request.get_json()
    
    required_fields = ['title', 'subject_category', 'topic', 'scheduled_start']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    session_id = video_manager.create_study_session(user_id, data)
    
    # Auto-create chat room for the session
    chat_room_id = chat_manager.create_chat_room(
        'video_session', 
        session_id, 
        f"Chat: {data['title']}", 
        [user_id]
    )
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'chat_room_id': chat_room_id,
        'message': 'Video session created successfully!'
    })

@app.route('/video-sessions/<session_id>')
def video_session_details(session_id):
    """View video session details"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('social_dashboard'))
    
    if session_id not in video_manager.sessions:
        return "Session not found", 404
    
    session_data = video_manager.sessions[session_id]
    
    return render_template('video_session_details.html',
                         session=session_data,
                         user_id=user_id)

@app.route('/api/video-sessions/<session_id>/join', methods=['POST'])
def join_video_session(session_id):
    """Join a video study session"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User session required'}), 400
    
    data = request.get_json() or {}
    user_name = data.get('user_name', f"Learner_{user_id[:8]}")
    
    result = video_manager.join_session(session_id, user_id, user_name)
    
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result)

@app.route('/api/video-sessions/<session_id>/start', methods=['POST'])
def start_video_session(session_id):
    """Start a video session (host only)"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User session required'}), 400
    
    success = video_manager.start_session(session_id, user_id)
    
    if success:
        return jsonify({'success': True, 'message': 'Session started successfully!'})
    else:
        return jsonify({'error': 'Unable to start session'}), 400

@app.route('/api/video-sessions/<session_id>/end', methods=['POST'])
def end_video_session(session_id):
    """End a video session (host only)"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User session required'}), 400
    
    result = video_manager.end_session(session_id, user_id)
    
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result)

# Advanced Analytics Dashboard Routes
@app.route('/analytics')
def analytics_dashboard():
    """Advanced analytics dashboard"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('social_dashboard'))
    
    dashboard_data = analytics_manager.get_user_dashboard_data(user_id)
    
    if 'error' in dashboard_data:
        return render_template('analytics_no_data.html', user_id=user_id)
    
    return render_template('analytics_dashboard.html',
                         data=dashboard_data,
                         user_id=user_id)

@app.route('/api/analytics/track-session', methods=['POST'])
def track_analytics_session():
    """Track learning session for analytics"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User session required'}), 400
    
    data = request.get_json()
    
    required_fields = ['subject_category', 'topic', 'difficulty_level', 'questions_answered', 'correct_answers']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required session data'}), 400
    
    analytics_manager.track_learning_session(user_id, data)
    
    return jsonify({'success': True, 'message': 'Session tracked successfully'})

@app.route('/api/analytics/performance-trends')
def get_performance_trends():
    """Get performance trends data"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User session required'}), 400
    
    days = request.args.get('days', 30, type=int)
    trend_data = analytics_manager._calculate_recent_trend(user_id, days)
    
    return jsonify(trend_data)

@app.route('/analytics/subject/<category>')
def subject_analytics(category):
    """Detailed analytics for specific subject"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('analytics_dashboard'))
    
    dashboard_data = analytics_manager.get_user_dashboard_data(user_id)
    
    if 'error' in dashboard_data or category not in dashboard_data['subject_breakdown']:
        return "Subject data not found", 404
    
    subject_data = dashboard_data['subject_breakdown'][category]
    
    return render_template('subject_analytics.html',
                         subject_data=subject_data,
                         category=category,
                         user_id=user_id)

@app.route('/analytics/compare')
def comparative_analytics():
    """Comparative analytics page"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('analytics_dashboard'))
    
    dashboard_data = analytics_manager.get_user_dashboard_data(user_id)
    
    if 'error' in dashboard_data:
        return redirect(url_for('analytics_dashboard'))
    
    return render_template('comparative_analytics.html',
                         data=dashboard_data,
                         user_id=user_id)

# Learning Management System Routes
@app.route('/lms')
def lms_dashboard():
    """LMS dashboard for institutions"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('social_dashboard'))
    
    user_role = request.args.get('role', 'student')  # student, instructor, admin
    institution_id = request.args.get('institution_id')
    
    if user_role == 'student':
        dashboard_data = lms_manager.get_student_dashboard(user_id, institution_id)
    elif user_role == 'instructor':
        dashboard_data = lms_manager.get_instructor_dashboard(user_id, institution_id)
    else:
        dashboard_data = {'message': 'Admin dashboard coming soon'}
    
    return render_template('lms_dashboard.html',
                         data=dashboard_data,
                         user_role=user_role,
                         user_id=user_id)

@app.route('/lms/courses/create')
def create_lms_course():
    """Create new LMS course form"""
    subjects = subject_manager.get_all_subjects()
    return render_template('create_lms_course.html', subjects=subjects)

@app.route('/api/lms/courses/create', methods=['POST'])
def api_create_lms_course():
    """API endpoint to create new course"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User session required'}), 400
    
    data = request.get_json()
    
    required_fields = ['title', 'subject_category']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    course_id = lms_manager.create_course(user_id, data)
    
    return jsonify({
        'success': True,
        'course_id': course_id,
        'message': 'Course created successfully!'
    })

@app.route('/api/lms/courses/<course_id>/enroll', methods=['POST'])
def enroll_in_course(course_id):
    """Enroll student in course"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User session required'}), 400
    
    success = lms_manager.enroll_student(course_id, user_id)
    
    if success:
        return jsonify({'success': True, 'message': 'Successfully enrolled in course!'})
    else:
        return jsonify({'error': 'Unable to enroll in course'}), 400

@app.route('/api/lms/assignments/<assignment_id>/submit', methods=['POST'])
def submit_lms_assignment(assignment_id):
    """Submit assignment solution"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User session required'}), 400
    
    data = request.get_json()
    
    submission_id = lms_manager.submit_assignment(assignment_id, user_id, data)
    
    if submission_id:
        return jsonify({'success': True, 'submission_id': submission_id})
    else:
        return jsonify({'error': 'Failed to submit assignment'}), 400

@app.route('/api/lms/institutions/create', methods=['POST'])
def create_institution():
    """Create new educational institution"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User session required'}), 400
    
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'error': 'Institution name is required'}), 400
    
    institution_id = lms_manager.create_institution(user_id, data)
    
    return jsonify({
        'success': True,
        'institution_id': institution_id,
        'message': 'Institution created successfully!'
    })

# Advanced Reporting Routes
@app.route('/reports')
def reports_dashboard():
    """Advanced reporting dashboard"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('social_dashboard'))
    
    institution_id = request.args.get('institution_id')
    time_period = request.args.get('period', '30d')
    
    if institution_id:
        executive_report = reporting_manager.generate_executive_dashboard(institution_id, time_period)
        return render_template('executive_dashboard.html',
                             report=executive_report,
                             user_id=user_id)
    else:
        return render_template('reports_selector.html', user_id=user_id)

@app.route('/api/reports/executive/<institution_id>')
def generate_executive_report(institution_id):
    """Generate executive dashboard report"""
    time_period = request.args.get('period', '30d')
    
    report = reporting_manager.generate_executive_dashboard(institution_id, time_period)
    
    return jsonify(report)

@app.route('/api/reports/custom', methods=['POST'])
def generate_custom_report():
    """Generate custom report"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User session required'}), 400
    
    data = request.get_json()
    institution_id = data.get('institution_id')
    
    if not institution_id:
        return jsonify({'error': 'Institution ID required'}), 400
    
    report = reporting_manager.generate_custom_report(institution_id, data)
    
    return jsonify(report)

# Mobile Optimization Routes
@app.route('/api/mobile/track-usage', methods=['POST'])
def track_mobile_usage():
    """Track mobile device usage"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User session required'}), 400
    
    data = request.get_json()
    device_info = data.get('device_info', {})
    session_data = data.get('session_data', {})
    
    mobile_manager.track_device_usage(user_id, device_info, session_data)
    
    return jsonify({'success': True})

@app.route('/api/mobile/responsive-css')
def get_responsive_css():
    """Get mobile-responsive CSS"""
    device_type = request.args.get('device_type')
    css_content = mobile_manager.get_responsive_css(device_type)
    
    return css_content, 200, {'Content-Type': 'text/css'}

@app.route('/api/mobile/analytics/<institution_id>')
def get_mobile_analytics(institution_id):
    """Get mobile analytics report"""
    report = mobile_manager.get_device_analytics_report(institution_id)
    
    return jsonify(report)

@app.route('/mobile-js')
def get_mobile_javascript():
    """Get mobile optimization JavaScript"""
    js_content = mobile_manager.get_mobile_javascript()
    
    return js_content, 200, {'Content-Type': 'application/javascript'}

# Integrated Analytics Route
@app.route('/api/analytics/comprehensive/<institution_id>')
def get_comprehensive_analytics(institution_id):
    """Get comprehensive analytics combining all systems"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User session required'}), 400
    
    # Combine analytics from all systems
    comprehensive_data = {
        'learning_analytics': analytics_manager.get_user_dashboard_data(user_id),
        'lms_analytics': lms_manager.get_student_dashboard(user_id, institution_id),
        'social_analytics': {
            'achievements': social_manager.get_collaborative_achievements(user_id),
            'challenges_participated': len([c for c in social_manager.challenges.values() 
                                           if user_id in c['participants']]),
            'study_groups_joined': len([g for g in social_manager.study_groups.values() 
                                      if user_id in g['members']])
        },
        'mobile_analytics': mobile_manager.get_device_analytics_report(institution_id),
        'executive_summary': reporting_manager.generate_executive_dashboard(institution_id, '30d')
    }
    
    return jsonify(comprehensive_data)