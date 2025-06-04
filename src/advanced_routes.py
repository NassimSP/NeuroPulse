"""
Advanced Feature Routes for NeuroPulse
Integrates all advanced learning features into Flask routes
"""

from flask import request, jsonify, session, render_template
from app import app, db, logger
import uuid
from datetime import datetime

# Import advanced systems with error handling
try:
    from spaced_repetition_engine import spaced_repetition_engine
    from adaptive_difficulty_engine import adaptive_difficulty_engine
    from personalized_dashboard import personalized_dashboard
    from voice_navigation_system import voice_navigation_system
    from onboarding_system import onboarding_system
    ADVANCED_FEATURES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Advanced features not available: {e}")
    ADVANCED_FEATURES_AVAILABLE = False

def get_user_id():
    """Get current user ID from session"""
    return session.get('user_id', 'demo_user')

@app.route('/api/dashboard/config')
def get_dashboard_config():
    """Get personalized dashboard configuration"""
    if not ADVANCED_FEATURES_AVAILABLE:
        return jsonify({'error': 'Advanced features not available'}), 503
    
    try:
        user_id = get_user_id()
        config = personalized_dashboard.get_dashboard_config(user_id)
        return jsonify(config)
    except Exception as e:
        logger.error(f"Dashboard config error: {e}")
        return jsonify({'error': 'Failed to load dashboard'}), 500

@app.route('/api/mood/update', methods=['POST'])
def update_mood():
    """Update user's current mood and theme"""
    if not ADVANCED_FEATURES_AVAILABLE:
        return jsonify({'error': 'Advanced features not available'}), 503
    
    try:
        user_id = get_user_id()
        data = request.get_json()
        mood = data.get('mood')
        context = data.get('context', {})
        
        result = personalized_dashboard.update_mood(user_id, mood, context)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Mood update error: {e}")
        return jsonify({'error': 'Failed to update mood'}), 500

@app.route('/api/energy/update', methods=['POST'])
def update_energy():
    """Update user's learning energy level"""
    if not ADVANCED_FEATURES_AVAILABLE:
        return jsonify({'error': 'Advanced features not available'}), 503
    
    try:
        user_id = get_user_id()
        data = request.get_json()
        energy_level = data.get('energy_level')
        factors = data.get('factors', {})
        
        result = personalized_dashboard.update_learning_energy(user_id, energy_level, factors)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Energy update error: {e}")
        return jsonify({'error': 'Failed to update energy'}), 500

@app.route('/api/spaced-repetition/cards/due')
def get_due_cards():
    """Get spaced repetition cards due for review"""
    if not ADVANCED_FEATURES_AVAILABLE:
        return jsonify({'error': 'Advanced features not available'}), 503
    
    try:
        user_id = get_user_id()
        limit = request.args.get('limit', 20, type=int)
        
        due_cards = spaced_repetition_engine.get_cards_due_for_review(user_id, limit)
        return jsonify({
            'cards': due_cards,
            'count': len(due_cards)
        })
    except Exception as e:
        logger.error(f"Due cards error: {e}")
        return jsonify({'error': 'Failed to get due cards'}), 500

@app.route('/api/spaced-repetition/review', methods=['POST'])
def review_card():
    """Submit spaced repetition card review"""
    if not ADVANCED_FEATURES_AVAILABLE:
        return jsonify({'error': 'Advanced features not available'}), 503
    
    try:
        user_id = get_user_id()
        data = request.get_json()
        card_id = data.get('card_id')
        quality_response = data.get('quality_response')
        response_time = data.get('response_time')
        difficulty_felt = data.get('difficulty_felt', 3)
        
        result = spaced_repetition_engine.review_card(
            user_id, card_id, quality_response, response_time, difficulty_felt
        )
        return jsonify(result)
    except Exception as e:
        logger.error(f"Card review error: {e}")
        return jsonify({'error': 'Failed to review card'}), 500

@app.route('/api/adaptive-difficulty/recommendation')
def get_difficulty_recommendation():
    """Get adaptive difficulty recommendation"""
    if not ADVANCED_FEATURES_AVAILABLE:
        return jsonify({'error': 'Advanced features not available'}), 503
    
    try:
        user_id = get_user_id()
        subject_category = request.args.get('subject_category', 'general')
        question_type = request.args.get('question_type')
        
        recommendation = adaptive_difficulty_engine.get_recommended_difficulty(
            user_id, subject_category, question_type
        )
        return jsonify(recommendation)
    except Exception as e:
        logger.error(f"Difficulty recommendation error: {e}")
        return jsonify({'error': 'Failed to get recommendation'}), 500

@app.route('/api/adaptive-difficulty/performance', methods=['POST'])
def record_performance():
    """Record performance data for adaptive difficulty"""
    if not ADVANCED_FEATURES_AVAILABLE:
        return jsonify({'error': 'Advanced features not available'}), 503
    
    try:
        user_id = get_user_id()
        data = request.get_json()
        subject_category = data.get('subject_category')
        performance_data = data.get('performance_data')
        
        result = adaptive_difficulty_engine.record_performance(
            user_id, subject_category, performance_data
        )
        return jsonify(result)
    except Exception as e:
        logger.error(f"Performance recording error: {e}")
        return jsonify({'error': 'Failed to record performance'}), 500

@app.route('/api/voice/command', methods=['POST'])
def process_voice_command():
    """Process voice command"""
    if not ADVANCED_FEATURES_AVAILABLE:
        return jsonify({'error': 'Advanced features not available'}), 503
    
    try:
        user_id = get_user_id()
        data = request.get_json()
        command_text = data.get('command_text')
        context = data.get('context', {})
        
        result = voice_navigation_system.process_voice_command(
            user_id, command_text, context
        )
        return jsonify(result)
    except Exception as e:
        logger.error(f"Voice command error: {e}")
        return jsonify({'error': 'Failed to process voice command'}), 500

@app.route('/api/voice/analytics')
def get_voice_analytics():
    """Get voice usage analytics"""
    if not ADVANCED_FEATURES_AVAILABLE:
        return jsonify({'error': 'Advanced features not available'}), 503
    
    try:
        user_id = get_user_id()
        analytics = voice_navigation_system.get_voice_analytics(user_id)
        return jsonify(analytics)
    except Exception as e:
        logger.error(f"Voice analytics error: {e}")
        return jsonify({'error': 'Failed to get analytics'}), 500

@app.route('/api/onboarding/status')
def get_onboarding_status():
    """Get onboarding status"""
    if not ADVANCED_FEATURES_AVAILABLE:
        return jsonify({'error': 'Advanced features not available'}), 503
    
    try:
        user_id = get_user_id()
        status = onboarding_system.get_onboarding_status(user_id)
        return jsonify(status)
    except Exception as e:
        logger.error(f"Onboarding status error: {e}")
        return jsonify({'error': 'Failed to get onboarding status'}), 500

@app.route('/api/onboarding/advance', methods=['POST'])
def advance_onboarding():
    """Advance onboarding step"""
    if not ADVANCED_FEATURES_AVAILABLE:
        return jsonify({'error': 'Advanced features not available'}), 503
    
    try:
        user_id = get_user_id()
        data = request.get_json()
        step_data = data.get('step_data')
        
        result = onboarding_system.advance_onboarding_step(user_id, step_data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Onboarding advance error: {e}")
        return jsonify({'error': 'Failed to advance onboarding'}), 500

@app.route('/api/onboarding/tour/<tour_name>')
def get_interactive_tour(tour_name):
    """Get interactive tour configuration"""
    if not ADVANCED_FEATURES_AVAILABLE:
        return jsonify({'error': 'Advanced features not available'}), 503
    
    try:
        user_id = get_user_id()
        tour = onboarding_system.get_interactive_tour(user_id, tour_name)
        return jsonify(tour)
    except Exception as e:
        logger.error(f"Interactive tour error: {e}")
        return jsonify({'error': 'Failed to get tour'}), 500

@app.route('/api/analytics/learning-insights')
def get_learning_insights():
    """Get comprehensive learning insights"""
    try:
        user_id = get_user_id()
        insights = {}
        
        if ADVANCED_FEATURES_AVAILABLE:
            try:
                # Get spaced repetition insights
                sr_insights = spaced_repetition_engine.get_retention_insights(user_id)
                insights['spaced_repetition'] = sr_insights
                
                # Get dashboard analytics
                dashboard_config = personalized_dashboard.get_dashboard_config(user_id)
                insights['dashboard'] = dashboard_config
                
                # Get voice analytics
                voice_analytics = voice_navigation_system.get_voice_analytics(user_id)
                insights['voice_usage'] = voice_analytics
                
            except Exception as e:
                logger.warning(f"Advanced insights error: {e}")
                insights['advanced_features'] = 'unavailable'
        
        # Add basic learning progress
        insights['session_data'] = {
            'current_quiz_id': session.get('current_quiz_id'),
            'current_question': session.get('current_question', 0),
            'correct_count': session.get('correct_count', 0),
            'difficulty_level': session.get('difficulty_level', 'intermediate')
        }
        
        return jsonify(insights)
    except Exception as e:
        logger.error(f"Learning insights error: {e}")
        return jsonify({'error': 'Failed to get insights'}), 500

@app.route('/api/features/status')
def get_features_status():
    """Get status of all advanced features"""
    return jsonify({
        'advanced_features_available': ADVANCED_FEATURES_AVAILABLE,
        'features': {
            'spaced_repetition': ADVANCED_FEATURES_AVAILABLE,
            'adaptive_difficulty': ADVANCED_FEATURES_AVAILABLE,
            'mood_themes': ADVANCED_FEATURES_AVAILABLE,
            'voice_navigation': ADVANCED_FEATURES_AVAILABLE,
            'onboarding_system': ADVANCED_FEATURES_AVAILABLE,
            'learning_energy': ADVANCED_FEATURES_AVAILABLE
        },
        'timestamp': datetime.now().isoformat()
    })

# Advanced dashboard routes
@app.route('/dashboard')
def dashboard():
    """Advanced dashboard with all features"""
    try:
        user_id = get_user_id()
        
        # Get dashboard data
        if ADVANCED_FEATURES_AVAILABLE:
            dashboard_config = personalized_dashboard.get_dashboard_config(user_id)
            onboarding_status = onboarding_system.get_onboarding_status(user_id)
            
            return render_template('dashboard.html',
                                 dashboard_config=dashboard_config,
                                 onboarding_status=onboarding_status,
                                 features_available=True)
        else:
            return render_template('dashboard.html',
                                 features_available=False,
                                 message='Advanced features are loading...')
    
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return render_template('dashboard.html',
                             features_available=False,
                             error='Dashboard temporarily unavailable')

@app.route('/onboarding')
def onboarding():
    """Onboarding flow"""
    try:
        user_id = get_user_id()
        
        if ADVANCED_FEATURES_AVAILABLE:
            status = onboarding_system.get_onboarding_status(user_id)
            return render_template('onboarding.html', onboarding_status=status)
        else:
            return render_template('onboarding.html', features_available=False)
    
    except Exception as e:
        logger.error(f"Onboarding error: {e}")
        return render_template('onboarding.html', error='Onboarding temporarily unavailable')

@app.route('/spaced-repetition')
def spaced_repetition():
    """Spaced repetition interface"""
    try:
        user_id = get_user_id()
        
        if ADVANCED_FEATURES_AVAILABLE:
            due_cards = spaced_repetition_engine.get_cards_due_for_review(user_id, 10)
            insights = spaced_repetition_engine.get_retention_insights(user_id)
            
            return render_template('spaced_repetition.html',
                                 due_cards=due_cards,
                                 insights=insights)
        else:
            return render_template('spaced_repetition.html', features_available=False)
    
    except Exception as e:
        logger.error(f"Spaced repetition error: {e}")
        return render_template('spaced_repetition.html', error='Feature temporarily unavailable')

# Error handlers for advanced features
@app.errorhandler(503)
def service_unavailable(error):
    """Handle service unavailable errors"""
    return jsonify({
        'error': 'Service temporarily unavailable',
        'message': 'Advanced features are being loaded',
        'retry_after': 30
    }), 503

logger.info("Advanced routes initialized successfully")