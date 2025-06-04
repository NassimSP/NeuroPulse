"""
Adaptive Difficulty Engine for NeuroPulse
Dynamically adjusts content difficulty based on performance patterns and learning analytics
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import math
import statistics

class AdaptiveDifficultyEngine:
    def __init__(self):
        self.user_performance_file = 'user_performance_profiles.json'
        self.difficulty_settings_file = 'adaptive_difficulty_settings.json'
        self.learning_analytics_file = 'learning_analytics.json'
        
        self.load_data()
        
        # Difficulty levels and thresholds
        self.difficulty_levels = ['beginner', 'intermediate', 'advanced', 'expert', 'mastery']
        self.performance_windows = {
            'immediate': 5,    # Last 5 questions
            'recent': 15,      # Last 15 questions
            'session': 30,     # Current session
            'historical': 100  # Long-term performance
        }
        
        # Adaptation parameters
        self.confidence_threshold = 0.75
        self.struggle_threshold = 0.45
        self.mastery_threshold = 0.90
        self.volatility_threshold = 0.3
    
    def load_data(self):
        """Load adaptive difficulty data"""
        self.user_profiles = self._load_json_file(self.user_performance_file, {})
        self.difficulty_settings = self._load_json_file(self.difficulty_settings_file, {})
        self.learning_analytics = self._load_json_file(self.learning_analytics_file, {})
    
    def _load_json_file(self, filename: str, default: dict) -> dict:
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return default
    
    def _save_json_file(self, filename: str, data: dict):
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def initialize_user_profile(self, user_id: str, subject_category: str) -> dict:
        """Initialize performance profile for new user/subject combination"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {}
        
        if subject_category not in self.user_profiles[user_id]:
            self.user_profiles[user_id][subject_category] = {
                'current_difficulty': 'intermediate',
                'performance_history': [],
                'adaptation_events': [],
                'learning_patterns': {
                    'optimal_difficulty': 'intermediate',
                    'learning_velocity': 0.5,
                    'retention_strength': 0.5,
                    'challenge_tolerance': 0.5,
                    'consistency_score': 0.5
                },
                'session_analytics': {
                    'current_session_id': None,
                    'session_start_time': None,
                    'questions_in_session': 0,
                    'session_performance': []
                },
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
        
        self._save_json_file(self.user_performance_file, self.user_profiles)
        return self.user_profiles[user_id][subject_category]
    
    def record_performance(self, user_id: str, subject_category: str, performance_data: dict) -> dict:
        """Record performance data and trigger adaptation analysis"""
        profile = self.initialize_user_profile(user_id, subject_category)
        
        # Create performance record
        performance_record = {
            'timestamp': datetime.now().isoformat(),
            'question_id': performance_data.get('question_id'),
            'difficulty_level': performance_data.get('difficulty_level', profile['current_difficulty']),
            'response_time': performance_data.get('response_time', 0),
            'accuracy': performance_data.get('accuracy', 0),
            'confidence_level': performance_data.get('confidence_level', 3),  # 1-5 scale
            'hint_usage': performance_data.get('hint_usage', 0),
            'attempt_count': performance_data.get('attempt_count', 1),
            'topic': performance_data.get('topic', ''),
            'question_type': performance_data.get('question_type', 'multiple_choice')
        }
        
        # Add to performance history
        profile['performance_history'].append(performance_record)
        
        # Update session analytics
        self._update_session_analytics(profile, performance_record)
        
        # Analyze performance patterns and adapt difficulty
        adaptation_result = self._analyze_and_adapt(user_id, subject_category, profile)
        
        # Update learning patterns
        self._update_learning_patterns(profile)
        
        profile['updated_at'] = datetime.now().isoformat()
        self._save_json_file(self.user_performance_file, self.user_profiles)
        
        return {
            'performance_recorded': True,
            'current_difficulty': profile['current_difficulty'],
            'adaptation_triggered': adaptation_result['adapted'],
            'adaptation_reason': adaptation_result.get('reason', ''),
            'next_difficulty': adaptation_result.get('new_difficulty', profile['current_difficulty']),
            'learning_insights': self._generate_learning_insights(profile),
            'recommended_actions': self._generate_recommendations(profile)
        }
    
    def _update_session_analytics(self, profile: dict, performance_record: dict):
        """Update current session analytics"""
        session = profile['session_analytics']
        
        # Initialize new session if needed
        if (session['current_session_id'] is None or 
            session['session_start_time'] is None or
            self._is_new_session(session['session_start_time'])):
            
            session['current_session_id'] = str(uuid.uuid4())
            session['session_start_time'] = datetime.now().isoformat()
            session['questions_in_session'] = 0
            session['session_performance'] = []
        
        # Add performance to current session
        session['questions_in_session'] += 1
        session['session_performance'].append({
            'accuracy': performance_record['accuracy'],
            'response_time': performance_record['response_time'],
            'difficulty': performance_record['difficulty_level'],
            'confidence': performance_record['confidence_level']
        })
    
    def _is_new_session(self, last_session_start: str) -> bool:
        """Determine if enough time has passed to start a new session"""
        if not last_session_start:
            return True
        
        last_start = datetime.fromisoformat(last_session_start)
        time_since_last = (datetime.now() - last_start).total_seconds() / 3600  # hours
        
        return time_since_last > 2  # New session after 2 hours
    
    def _analyze_and_adapt(self, user_id: str, subject_category: str, profile: dict) -> dict:
        """Analyze performance patterns and adapt difficulty if necessary"""
        performance_history = profile['performance_history']
        current_difficulty = profile['current_difficulty']
        
        if len(performance_history) < 3:
            return {'adapted': False, 'reason': 'insufficient_data'}
        
        # Calculate performance metrics for different time windows
        metrics = self._calculate_performance_metrics(performance_history)
        
        # Determine if adaptation is needed
        adaptation_decision = self._make_adaptation_decision(metrics, current_difficulty)
        
        if adaptation_decision['should_adapt']:
            # Record adaptation event
            adaptation_event = {
                'timestamp': datetime.now().isoformat(),
                'from_difficulty': current_difficulty,
                'to_difficulty': adaptation_decision['new_difficulty'],
                'reason': adaptation_decision['reason'],
                'trigger_metrics': adaptation_decision['trigger_metrics'],
                'confidence_score': adaptation_decision['confidence_score']
            }
            
            profile['adaptation_events'].append(adaptation_event)
            profile['current_difficulty'] = adaptation_decision['new_difficulty']
            
            return {
                'adapted': True,
                'new_difficulty': adaptation_decision['new_difficulty'],
                'reason': adaptation_decision['reason'],
                'confidence_score': adaptation_decision['confidence_score']
            }
        
        return {'adapted': False, 'reason': 'no_adaptation_needed'}
    
    def _calculate_performance_metrics(self, performance_history: List[dict]) -> dict:
        """Calculate comprehensive performance metrics across different time windows"""
        metrics = {}
        
        for window_name, window_size in self.performance_windows.items():
            recent_performance = performance_history[-window_size:] if len(performance_history) >= window_size else performance_history
            
            if not recent_performance:
                continue
            
            # Basic metrics
            accuracies = [p['accuracy'] for p in recent_performance]
            response_times = [p['response_time'] for p in recent_performance if p['response_time'] > 0]
            confidences = [p['confidence_level'] for p in recent_performance]
            
            metrics[window_name] = {
                'avg_accuracy': statistics.mean(accuracies) if accuracies else 0,
                'accuracy_trend': self._calculate_trend(accuracies),
                'avg_response_time': statistics.mean(response_times) if response_times else 0,
                'response_time_trend': self._calculate_trend(response_times),
                'avg_confidence': statistics.mean(confidences) if confidences else 3,
                'performance_volatility': statistics.stdev(accuracies) if len(accuracies) > 1 else 0,
                'consistent_performance': self._calculate_consistency(accuracies),
                'struggle_indicators': self._detect_struggle_indicators(recent_performance),
                'mastery_indicators': self._detect_mastery_indicators(recent_performance)
            }
        
        return metrics
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend using simple linear regression slope"""
        if len(values) < 2:
            return 0
        
        n = len(values)
        x = list(range(n))
        
        # Calculate slope using least squares
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        return numerator / denominator if denominator != 0 else 0
    
    def _calculate_consistency(self, accuracies: List[float]) -> float:
        """Calculate performance consistency (inverse of coefficient of variation)"""
        if len(accuracies) < 2:
            return 1.0
        
        mean_acc = statistics.mean(accuracies)
        if mean_acc == 0:
            return 0
        
        std_acc = statistics.stdev(accuracies)
        cv = std_acc / mean_acc  # Coefficient of variation
        
        return max(0, 1 - cv)  # Higher values indicate more consistency
    
    def _detect_struggle_indicators(self, performance: List[dict]) -> dict:
        """Detect indicators that user is struggling with current difficulty"""
        if not performance:
            return {'struggling': False, 'indicators': []}
        
        indicators = []
        
        # Low accuracy
        recent_accuracy = statistics.mean([p['accuracy'] for p in performance[-5:]])
        if recent_accuracy < self.struggle_threshold:
            indicators.append('low_accuracy')
        
        # Increasing response times
        response_times = [p['response_time'] for p in performance if p['response_time'] > 0]
        if len(response_times) >= 3:
            trend = self._calculate_trend(response_times[-5:])
            if trend > 0.5:  # Increasing response times
                indicators.append('increasing_response_time')
        
        # Low confidence levels
        recent_confidence = statistics.mean([p['confidence_level'] for p in performance[-5:]])
        if recent_confidence < 2.5:
            indicators.append('low_confidence')
        
        # High hint usage
        hint_usage = [p['hint_usage'] for p in performance[-5:]]
        if statistics.mean(hint_usage) > 0.5:
            indicators.append('high_hint_usage')
        
        # Multiple attempts
        attempt_counts = [p['attempt_count'] for p in performance[-5:]]
        if statistics.mean(attempt_counts) > 1.5:
            indicators.append('multiple_attempts')
        
        return {
            'struggling': len(indicators) >= 2,
            'indicators': indicators,
            'struggle_score': len(indicators) / 5.0
        }
    
    def _detect_mastery_indicators(self, performance: List[dict]) -> dict:
        """Detect indicators that user has mastered current difficulty"""
        if not performance:
            return {'mastery': False, 'indicators': []}
        
        indicators = []
        
        # High accuracy
        recent_accuracy = statistics.mean([p['accuracy'] for p in performance[-10:]])
        if recent_accuracy >= self.mastery_threshold:
            indicators.append('high_accuracy')
        
        # Decreasing response times
        response_times = [p['response_time'] for p in performance if p['response_time'] > 0]
        if len(response_times) >= 5:
            trend = self._calculate_trend(response_times[-10:])
            if trend < -0.3:  # Decreasing response times
                indicators.append('decreasing_response_time')
        
        # High confidence
        recent_confidence = statistics.mean([p['confidence_level'] for p in performance[-10:]])
        if recent_confidence >= 4.0:
            indicators.append('high_confidence')
        
        # Minimal hint usage
        hint_usage = [p['hint_usage'] for p in performance[-10:]]
        if statistics.mean(hint_usage) < 0.1:
            indicators.append('minimal_hints')
        
        # Single attempts
        attempt_counts = [p['attempt_count'] for p in performance[-10:]]
        if statistics.mean(attempt_counts) <= 1.1:
            indicators.append('single_attempts')
        
        # Consistent performance
        accuracies = [p['accuracy'] for p in performance[-10:]]
        if self._calculate_consistency(accuracies) > 0.8:
            indicators.append('consistent_performance')
        
        return {
            'mastery': len(indicators) >= 3,
            'indicators': indicators,
            'mastery_score': len(indicators) / 6.0
        }
    
    def _make_adaptation_decision(self, metrics: dict, current_difficulty: str) -> dict:
        """Make intelligent decision about difficulty adaptation"""
        current_level_index = self.difficulty_levels.index(current_difficulty)
        
        # Get most relevant metrics (prioritize recent over historical)
        primary_metrics = metrics.get('recent', metrics.get('immediate', {}))
        immediate_metrics = metrics.get('immediate', {})
        
        if not primary_metrics:
            return {'should_adapt': False, 'reason': 'insufficient_metrics'}
        
        # Check for struggle indicators (decrease difficulty)
        struggle_info = primary_metrics.get('struggle_indicators', {})
        if struggle_info.get('struggling', False) and current_level_index > 0:
            return {
                'should_adapt': True,
                'new_difficulty': self.difficulty_levels[current_level_index - 1],
                'reason': f"Struggling detected: {', '.join(struggle_info['indicators'])}",
                'trigger_metrics': struggle_info,
                'confidence_score': struggle_info.get('struggle_score', 0)
            }
        
        # Check for mastery indicators (increase difficulty)
        mastery_info = primary_metrics.get('mastery_indicators', {})
        if mastery_info.get('mastery', False) and current_level_index < len(self.difficulty_levels) - 1:
            # Additional check: ensure consistent mastery across recent performance
            if primary_metrics.get('avg_accuracy', 0) >= self.mastery_threshold:
                return {
                    'should_adapt': True,
                    'new_difficulty': self.difficulty_levels[current_level_index + 1],
                    'reason': f"Mastery achieved: {', '.join(mastery_info['indicators'])}",
                    'trigger_metrics': mastery_info,
                    'confidence_score': mastery_info.get('mastery_score', 0)
                }
        
        # Check for performance volatility (may need difficulty stabilization)
        volatility = primary_metrics.get('performance_volatility', 0)
        if volatility > self.volatility_threshold:
            # High volatility - stay at current level to stabilize
            return {
                'should_adapt': False,
                'reason': f'High performance volatility ({volatility:.2f}) - maintaining current level for stabilization'
            }
        
        return {'should_adapt': False, 'reason': 'performance_within_optimal_range'}
    
    def _update_learning_patterns(self, profile: dict):
        """Update learning patterns based on recent performance and adaptations"""
        patterns = profile['learning_patterns']
        performance_history = profile['performance_history']
        
        if len(performance_history) < 10:
            return
        
        recent_performance = performance_history[-20:]
        
        # Calculate learning velocity (improvement rate)
        accuracies = [p['accuracy'] for p in recent_performance]
        velocity_trend = self._calculate_trend(accuracies)
        patterns['learning_velocity'] = max(0, min(1, 0.5 + velocity_trend))
        
        # Calculate retention strength
        retention_strength = statistics.mean(accuracies[-10:]) if len(accuracies) >= 10 else 0.5
        patterns['retention_strength'] = retention_strength
        
        # Calculate challenge tolerance
        struggle_count = sum(1 for p in recent_performance 
                           if p['accuracy'] < self.struggle_threshold)
        challenge_tolerance = 1 - (struggle_count / len(recent_performance))
        patterns['challenge_tolerance'] = challenge_tolerance
        
        # Calculate consistency score
        patterns['consistency_score'] = self._calculate_consistency(accuracies)
        
        # Determine optimal difficulty based on patterns
        patterns['optimal_difficulty'] = self._determine_optimal_difficulty(patterns)
    
    def _determine_optimal_difficulty(self, patterns: dict) -> str:
        """Determine optimal difficulty level based on learning patterns"""
        # Weighted score calculation
        velocity_weight = 0.3
        retention_weight = 0.4
        tolerance_weight = 0.2
        consistency_weight = 0.1
        
        composite_score = (
            patterns['learning_velocity'] * velocity_weight +
            patterns['retention_strength'] * retention_weight +
            patterns['challenge_tolerance'] * tolerance_weight +
            patterns['consistency_score'] * consistency_weight
        )
        
        # Map composite score to difficulty levels
        if composite_score >= 0.8:
            return 'expert'
        elif composite_score >= 0.7:
            return 'advanced'
        elif composite_score >= 0.5:
            return 'intermediate'
        elif composite_score >= 0.3:
            return 'beginner'
        else:
            return 'beginner'
    
    def get_recommended_difficulty(self, user_id: str, subject_category: str, 
                                 question_type: str = None) -> dict:
        """Get recommended difficulty for next question"""
        if user_id not in self.user_profiles:
            return {
                'recommended_difficulty': 'intermediate',
                'confidence': 0.5,
                'reasoning': 'No performance history available'
            }
        
        profile = self.user_profiles[user_id].get(subject_category)
        if not profile:
            return {
                'recommended_difficulty': 'intermediate',
                'confidence': 0.5,
                'reasoning': 'No subject-specific performance history'
            }
        
        current_difficulty = profile['current_difficulty']
        patterns = profile['learning_patterns']
        
        # Analyze recent session performance for micro-adjustments
        session_performance = profile['session_analytics']['session_performance']
        session_adjustment = self._calculate_session_adjustment(session_performance)
        
        # Determine final recommendation
        base_difficulty_index = self.difficulty_levels.index(current_difficulty)
        adjusted_index = max(0, min(len(self.difficulty_levels) - 1, 
                                  base_difficulty_index + session_adjustment))
        
        recommended_difficulty = self.difficulty_levels[adjusted_index]
        
        # Calculate confidence in recommendation
        confidence = self._calculate_recommendation_confidence(profile)
        
        return {
            'recommended_difficulty': recommended_difficulty,
            'confidence': confidence,
            'reasoning': self._generate_recommendation_reasoning(profile, session_adjustment),
            'learning_patterns': patterns,
            'session_insights': self._analyze_session_insights(session_performance)
        }
    
    def _calculate_session_adjustment(self, session_performance: List[dict]) -> int:
        """Calculate micro-adjustment based on current session performance"""
        if not session_performance or len(session_performance) < 3:
            return 0
        
        recent_accuracies = [p['accuracy'] for p in session_performance[-5:]]
        avg_accuracy = statistics.mean(recent_accuracies)
        
        # Micro-adjustments within session
        if avg_accuracy >= 0.9 and len(session_performance) >= 5:
            return 1  # Increase difficulty
        elif avg_accuracy <= 0.4:
            return -1  # Decrease difficulty
        else:
            return 0  # Maintain current level
    
    def _calculate_recommendation_confidence(self, profile: dict) -> float:
        """Calculate confidence in difficulty recommendation"""
        performance_history = profile['performance_history']
        adaptation_events = profile['adaptation_events']
        
        # Base confidence on amount of data
        data_confidence = min(1.0, len(performance_history) / 50)
        
        # Stability confidence based on recent adaptations
        recent_adaptations = [a for a in adaptation_events 
                            if (datetime.now() - datetime.fromisoformat(a['timestamp'])).days <= 7]
        stability_confidence = max(0.3, 1 - len(recent_adaptations) * 0.2)
        
        # Performance consistency confidence
        if len(performance_history) >= 10:
            recent_accuracies = [p['accuracy'] for p in performance_history[-10:]]
            consistency_confidence = self._calculate_consistency(recent_accuracies)
        else:
            consistency_confidence = 0.5
        
        # Weighted average
        return (data_confidence * 0.4 + stability_confidence * 0.3 + consistency_confidence * 0.3)
    
    def _generate_recommendation_reasoning(self, profile: dict, session_adjustment: int) -> str:
        """Generate human-readable reasoning for difficulty recommendation"""
        performance_history = profile['performance_history']
        patterns = profile['learning_patterns']
        
        if len(performance_history) < 5:
            return "Insufficient performance data - using default intermediate level"
        
        recent_accuracy = statistics.mean([p['accuracy'] for p in performance_history[-10:]])
        
        reasons = []
        
        if session_adjustment > 0:
            reasons.append("excellent session performance suggests readiness for increased challenge")
        elif session_adjustment < 0:
            reasons.append("session struggles indicate need for easier content")
        
        if patterns['retention_strength'] > 0.8:
            reasons.append("strong retention patterns")
        elif patterns['retention_strength'] < 0.4:
            reasons.append("retention needs improvement")
        
        if patterns['learning_velocity'] > 0.7:
            reasons.append("rapid learning progress")
        elif patterns['learning_velocity'] < 0.3:
            reasons.append("steady learning pace")
        
        if not reasons:
            reasons.append("performance within optimal range")
        
        return "Recommendation based on: " + ", ".join(reasons)
    
    def _analyze_session_insights(self, session_performance: List[dict]) -> dict:
        """Analyze current session for insights"""
        if not session_performance:
            return {'no_data': True}
        
        accuracies = [p['accuracy'] for p in session_performance]
        response_times = [p['response_time'] for p in session_performance if p['response_time'] > 0]
        
        return {
            'questions_answered': len(session_performance),
            'session_accuracy': statistics.mean(accuracies),
            'accuracy_trend': self._calculate_trend(accuracies),
            'avg_response_time': statistics.mean(response_times) if response_times else 0,
            'performance_stability': self._calculate_consistency(accuracies),
            'session_quality': self._assess_session_quality(session_performance)
        }
    
    def _assess_session_quality(self, session_performance: List[dict]) -> str:
        """Assess overall quality of current session"""
        if len(session_performance) < 3:
            return 'insufficient_data'
        
        accuracies = [p['accuracy'] for p in session_performance]
        avg_accuracy = statistics.mean(accuracies)
        consistency = self._calculate_consistency(accuracies)
        
        if avg_accuracy >= 0.8 and consistency >= 0.7:
            return 'excellent'
        elif avg_accuracy >= 0.6 and consistency >= 0.5:
            return 'good'
        elif avg_accuracy >= 0.4:
            return 'fair'
        else:
            return 'needs_improvement'
    
    def _generate_learning_insights(self, profile: dict) -> dict:
        """Generate insights about user's learning progress"""
        performance_history = profile['performance_history']
        patterns = profile['learning_patterns']
        
        if len(performance_history) < 10:
            return {'insight': 'Building learning profile - more data needed for detailed insights'}
        
        insights = []
        
        # Learning velocity insights
        if patterns['learning_velocity'] > 0.7:
            insights.append("You're learning rapidly and ready for challenges")
        elif patterns['learning_velocity'] < 0.3:
            insights.append("You're taking time to master concepts thoroughly")
        
        # Retention insights
        if patterns['retention_strength'] > 0.8:
            insights.append("Excellent knowledge retention")
        elif patterns['retention_strength'] < 0.4:
            insights.append("Consider reviewing concepts more frequently")
        
        # Consistency insights
        if patterns['consistency_score'] > 0.8:
            insights.append("Very consistent performance")
        elif patterns['consistency_score'] < 0.4:
            insights.append("Performance varies - identify optimal study conditions")
        
        return {
            'insights': insights,
            'learning_strengths': self._identify_learning_strengths(patterns),
            'improvement_areas': self._identify_improvement_areas(patterns)
        }
    
    def _identify_learning_strengths(self, patterns: dict) -> List[str]:
        """Identify user's learning strengths"""
        strengths = []
        
        if patterns['retention_strength'] > 0.7:
            strengths.append("Strong knowledge retention")
        if patterns['learning_velocity'] > 0.6:
            strengths.append("Quick concept acquisition")
        if patterns['challenge_tolerance'] > 0.7:
            strengths.append("Handles challenging content well")
        if patterns['consistency_score'] > 0.7:
            strengths.append("Consistent performance")
        
        return strengths
    
    def _identify_improvement_areas(self, patterns: dict) -> List[str]:
        """Identify areas for improvement"""
        areas = []
        
        if patterns['retention_strength'] < 0.4:
            areas.append("Knowledge retention")
        if patterns['learning_velocity'] < 0.3:
            areas.append("Learning pace")
        if patterns['challenge_tolerance'] < 0.4:
            areas.append("Handling difficult concepts")
        if patterns['consistency_score'] < 0.4:
            areas.append("Performance consistency")
        
        return areas
    
    def _generate_recommendations(self, profile: dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        patterns = profile['learning_patterns']
        performance_history = profile['performance_history']
        
        # Recent performance analysis
        if len(performance_history) >= 10:
            recent_accuracies = [p['accuracy'] for p in performance_history[-10:]]
            avg_recent = statistics.mean(recent_accuracies)
            
            if avg_recent < 0.5:
                recommendations.append("Consider reviewing fundamental concepts before proceeding")
            elif avg_recent > 0.85:
                recommendations.append("You're ready for more challenging content")
        
        # Pattern-based recommendations
        if patterns['consistency_score'] < 0.5:
            recommendations.append("Try to maintain consistent study sessions for better results")
        
        if patterns['retention_strength'] < 0.5:
            recommendations.append("Implement spaced repetition to improve retention")
        
        if patterns['challenge_tolerance'] < 0.4:
            recommendations.append("Gradually increase difficulty to build confidence")
        
        return recommendations[:3]  # Limit to top 3 recommendations

# Initialize global adaptive difficulty engine
adaptive_difficulty_engine = AdaptiveDifficultyEngine()