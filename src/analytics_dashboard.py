"""
Advanced Analytics Dashboard for NeuroPulse
Provides comprehensive learning insights, predictive modeling, and executive reporting
"""

import json
import math
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict, Counter
import logging

logger = logging.getLogger(__name__)

class AnalyticsDashboard:
    """Advanced analytics engine with predictive learning modeling"""
    
    def __init__(self):
        self.analytics_data = {}
        self.user_metrics = {}
        self.institutional_data = {}
        self.predictive_models = {}
        self.load_data()
    
    def load_data(self):
        """Load analytics data from storage"""
        try:
            with open('data/analytics_data.json', 'r') as f:
                data = json.load(f)
                self.analytics_data = data.get('analytics', {})
                self.user_metrics = data.get('user_metrics', {})
                self.institutional_data = data.get('institutional', {})
                self.predictive_models = data.get('models', {})
        except FileNotFoundError:
            self.analytics_data = {}
            self.user_metrics = {}
            self.institutional_data = {}
            self.predictive_models = {}
    
    def save_data(self):
        """Save analytics data to storage"""
        import os
        os.makedirs('data', exist_ok=True)
        
        data = {
            'analytics': self.analytics_data,
            'user_metrics': self.user_metrics,
            'institutional': self.institutional_data,
            'models': self.predictive_models,
            'last_updated': datetime.now().isoformat()
        }
        
        with open('data/analytics_data.json', 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def record_learning_event(self, user_id: str, event_type: str, event_data: Dict):
        """Record a learning event for analytics"""
        if user_id not in self.analytics_data:
            self.analytics_data[user_id] = {
                'events': [],
                'session_history': [],
                'performance_trends': [],
                'engagement_metrics': {}
            }
        
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'data': event_data,
            'session_id': event_data.get('session_id'),
            'subject': event_data.get('subject')
        }
        
        self.analytics_data[user_id]['events'].append(event)
        
        # Update session history if it's a session completion
        if event_type == 'session_completed':
            self._update_session_history(user_id, event_data)
        
        # Update real-time metrics
        self._update_user_metrics(user_id, event_type, event_data)
        
        self.save_data()
    
    def _update_session_history(self, user_id: str, session_data: Dict):
        """Update user's session history for trend analysis"""
        session_record = {
            'date': datetime.now().isoformat(),
            'subject': session_data.get('subject'),
            'difficulty': session_data.get('difficulty'),
            'questions_answered': session_data.get('questions_answered', 0),
            'correct_answers': session_data.get('correct_answers', 0),
            'accuracy': session_data.get('accuracy', 0),
            'time_spent': session_data.get('time_spent', 0),
            'confidence_ratings': session_data.get('confidence_ratings', []),
            'energy_level': session_data.get('energy_level', 5),
            'completion_rate': session_data.get('completion_rate', 100)
        }
        
        self.analytics_data[user_id]['session_history'].append(session_record)
        
        # Keep only last 100 sessions for performance
        if len(self.analytics_data[user_id]['session_history']) > 100:
            self.analytics_data[user_id]['session_history'] = self.analytics_data[user_id]['session_history'][-100:]
    
    def _update_user_metrics(self, user_id: str, event_type: str, event_data: Dict):
        """Update real-time user metrics"""
        if user_id not in self.user_metrics:
            self.user_metrics[user_id] = {
                'total_sessions': 0,
                'total_time': 0,
                'avg_accuracy': 0,
                'engagement_score': 0,
                'learning_velocity': 0,
                'retention_rate': 0,
                'consistency_score': 0,
                'risk_factors': [],
                'strengths': [],
                'last_updated': datetime.now().isoformat()
            }
        
        metrics = self.user_metrics[user_id]
        
        if event_type == 'session_completed':
            metrics['total_sessions'] += 1
            metrics['total_time'] += event_data.get('time_spent', 0)
            
            # Update running averages
            current_accuracy = event_data.get('accuracy', 0)
            metrics['avg_accuracy'] = self._update_running_average(
                metrics['avg_accuracy'], current_accuracy, metrics['total_sessions']
            )
        
        metrics['last_updated'] = datetime.now().isoformat()
    
    def _update_running_average(self, current_avg: float, new_value: float, count: int) -> float:
        """Update running average efficiently"""
        return ((current_avg * (count - 1)) + new_value) / count
    
    def generate_user_dashboard(self, user_id: str) -> Dict:
        """Generate comprehensive user analytics dashboard"""
        if user_id not in self.analytics_data:
            return self._generate_empty_dashboard(user_id)
        
        user_data = self.analytics_data[user_id]
        session_history = user_data.get('session_history', [])
        
        if not session_history:
            return self._generate_empty_dashboard(user_id)
        
        # Performance trends
        performance_trends = self._calculate_performance_trends(session_history)
        
        # Learning insights
        learning_insights = self._generate_learning_insights(user_id, session_history)
        
        # Predictive analytics
        predictions = self._generate_predictions(user_id, session_history)
        
        # Engagement analysis
        engagement_analysis = self._analyze_engagement_patterns(user_id, session_history)
        
        # Subject performance breakdown
        subject_performance = self._analyze_subject_performance(session_history)
        
        # Weekly activity summary
        weekly_summary = self._generate_weekly_summary(session_history)
        
        dashboard = {
            'user_id': user_id,
            'generated_at': datetime.now().isoformat(),
            'overview': {
                'total_sessions': len(session_history),
                'total_time_minutes': sum(s.get('time_spent', 0) for s in session_history),
                'avg_accuracy': round(statistics.mean([s.get('accuracy', 0) for s in session_history]), 1),
                'current_streak': self._calculate_current_streak(session_history),
                'subjects_studied': len(set(s.get('subject') for s in session_history)),
                'last_session': session_history[-1]['date'] if session_history else None
            },
            'performance_trends': performance_trends,
            'learning_insights': learning_insights,
            'predictions': predictions,
            'engagement_analysis': engagement_analysis,
            'subject_performance': subject_performance,
            'weekly_summary': weekly_summary,
            'recommendations': self._generate_recommendations(user_id, session_history, predictions)
        }
        
        return dashboard
    
    def _generate_empty_dashboard(self, user_id: str) -> Dict:
        """Generate dashboard for users with no data"""
        return {
            'user_id': user_id,
            'generated_at': datetime.now().isoformat(),
            'overview': {
                'total_sessions': 0,
                'total_time_minutes': 0,
                'avg_accuracy': 0,
                'current_streak': 0,
                'subjects_studied': 0,
                'last_session': None
            },
            'insights': ['Start learning to see personalized analytics!'],
            'recommendations': [
                'Take the onboarding quiz to personalize your experience',
                'Try a quick 5-question session to get started',
                'Explore different subjects to find your interests'
            ]
        }
    
    def _calculate_performance_trends(self, session_history: List[Dict]) -> Dict:
        """Calculate performance trends over time"""
        if len(session_history) < 2:
            return {'trend': 'insufficient_data', 'change': 0, 'analysis': 'Need more sessions for trend analysis'}
        
        # Get recent vs older performance
        recent_sessions = session_history[-10:] if len(session_history) >= 10 else session_history[-len(session_history)//2:]
        older_sessions = session_history[:-len(recent_sessions)]
        
        if not older_sessions:
            return {'trend': 'insufficient_data', 'change': 0, 'analysis': 'Need more sessions for comparison'}
        
        recent_avg = statistics.mean([s.get('accuracy', 0) for s in recent_sessions])
        older_avg = statistics.mean([s.get('accuracy', 0) for s in older_sessions])
        
        change = recent_avg - older_avg
        
        if change > 5:
            trend = 'improving'
            analysis = f'Performance improving by {change:.1f}% - excellent progress!'
        elif change < -5:
            trend = 'declining'
            analysis = f'Performance declining by {abs(change):.1f}% - consider reviewing study methods'
        else:
            trend = 'stable'
            analysis = 'Performance is stable - maintaining consistent learning'
        
        # Calculate additional trend metrics
        accuracy_timeline = [s.get('accuracy', 0) for s in session_history[-20:]]
        consistency = 100 - (statistics.stdev(accuracy_timeline) if len(accuracy_timeline) > 1 else 0)
        
        return {
            'trend': trend,
            'change': round(change, 1),
            'analysis': analysis,
            'consistency_score': round(max(0, consistency), 1),
            'recent_average': round(recent_avg, 1),
            'historical_average': round(older_avg, 1)
        }
    
    def _generate_learning_insights(self, user_id: str, session_history: List[Dict]) -> List[str]:
        """Generate personalized learning insights"""
        insights = []
        
        if not session_history:
            return ['Complete your first session to see insights!']
        
        # Accuracy insights
        avg_accuracy = statistics.mean([s.get('accuracy', 0) for s in session_history])
        if avg_accuracy >= 85:
            insights.append('Excellent accuracy! You have strong knowledge retention.')
        elif avg_accuracy >= 70:
            insights.append('Good accuracy overall. Focus on challenging topics for improvement.')
        else:
            insights.append('Consider reviewing concepts more thoroughly before answering questions.')
        
        # Time analysis
        session_times = [s.get('time_spent', 0) for s in session_history if s.get('time_spent', 0) > 0]
        if session_times:
            avg_time = statistics.mean(session_times)
            if avg_time < 5:
                insights.append('You complete sessions quickly - consider taking more time to reflect.')
            elif avg_time > 20:
                insights.append('You take time to think through problems - great for deep learning!')
        
        # Confidence analysis
        confidence_data = []
        for session in session_history:
            confidence_ratings = session.get('confidence_ratings', [])
            if confidence_ratings:
                avg_confidence = statistics.mean([r.get('confidence', 3) for r in confidence_ratings])
                accuracy = session.get('accuracy', 0)
                confidence_data.append({'confidence': avg_confidence, 'accuracy': accuracy})
        
        if len(confidence_data) >= 5:
            overconfident = sum(1 for d in confidence_data if d['confidence'] > 4 and d['accuracy'] < 70)
            if overconfident > len(confidence_data) * 0.3:
                insights.append('Sometimes confidence is higher than accuracy - double-check your understanding.')
        
        # Subject diversity
        subjects = set(s.get('subject') for s in session_history)
        if len(subjects) >= 3:
            insights.append(f'Great subject diversity! Studying {len(subjects)} different topics builds cognitive flexibility.')
        elif len(subjects) == 1:
            insights.append('Consider exploring other subjects to broaden your knowledge base.')
        
        # Streak analysis
        streak = self._calculate_current_streak(session_history)
        if streak >= 7:
            insights.append(f'Amazing {streak}-day streak! Consistency is key to long-term retention.')
        elif streak >= 3:
            insights.append(f'{streak}-day streak building! Keep the momentum going.')
        
        return insights[:5]  # Limit to top 5 insights
    
    def _generate_predictions(self, user_id: str, session_history: List[Dict]) -> Dict:
        """Generate predictive analytics"""
        if len(session_history) < 5:
            return {
                'retention_forecast': 'insufficient_data',
                'mastery_timeline': 'Need more sessions for predictions',
                'risk_assessment': 'low'
            }
        
        # Simple trend-based predictions
        recent_accuracy = [s.get('accuracy', 0) for s in session_history[-10:]]
        trend_slope = self._calculate_trend_slope(recent_accuracy)
        
        # Retention forecast
        current_accuracy = statistics.mean(recent_accuracy)
        predicted_accuracy = max(0, min(100, current_accuracy + (trend_slope * 5)))  # Project 5 sessions ahead
        
        if predicted_accuracy >= 80:
            retention_forecast = 'excellent'
        elif predicted_accuracy >= 60:
            retention_forecast = 'good'
        else:
            retention_forecast = 'needs_attention'
        
        # Risk assessment for dropping out
        session_gaps = self._calculate_session_gaps(session_history)
        recent_engagement = len([s for s in session_history[-7:] if s])  # Sessions in last week
        
        risk_factors = []
        if session_gaps > 3:
            risk_factors.append('irregular_learning_pattern')
        if current_accuracy < 50:
            risk_factors.append('low_performance')
        if recent_engagement < 2:
            risk_factors.append('low_recent_activity')
        
        risk_level = 'high' if len(risk_factors) >= 2 else 'medium' if risk_factors else 'low'
        
        return {
            'retention_forecast': retention_forecast,
            'predicted_accuracy': round(predicted_accuracy, 1),
            'trend_direction': 'improving' if trend_slope > 0 else 'declining' if trend_slope < 0 else 'stable',
            'risk_assessment': risk_level,
            'risk_factors': risk_factors,
            'recommended_interventions': self._get_intervention_recommendations(risk_factors)
        }
    
    def _calculate_trend_slope(self, values: List[float]) -> float:
        """Calculate trend slope using simple linear regression"""
        if len(values) < 2:
            return 0
        
        n = len(values)
        x_values = list(range(n))
        
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(values)
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        return numerator / denominator if denominator != 0 else 0
    
    def _calculate_session_gaps(self, session_history: List[Dict]) -> float:
        """Calculate average gap between sessions in days"""
        if len(session_history) < 2:
            return 0
        
        dates = [datetime.fromisoformat(s['date'].replace('Z', '+00:00')) for s in session_history[-10:]]
        gaps = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
        
        return statistics.mean(gaps) if gaps else 0
    
    def _get_intervention_recommendations(self, risk_factors: List[str]) -> List[str]:
        """Get intervention recommendations based on risk factors"""
        interventions = []
        
        if 'irregular_learning_pattern' in risk_factors:
            interventions.append('Set up a consistent daily learning schedule')
        if 'low_performance' in risk_factors:
            interventions.append('Review fundamental concepts before advancing')
        if 'low_recent_activity' in risk_factors:
            interventions.append('Start with shorter 5-minute sessions to rebuild momentum')
        
        return interventions
    
    def _analyze_engagement_patterns(self, user_id: str, session_history: List[Dict]) -> Dict:
        """Analyze user engagement patterns"""
        if not session_history:
            return {'engagement_score': 0, 'patterns': []}
        
        # Calculate engagement metrics
        completion_rates = [s.get('completion_rate', 100) for s in session_history]
        avg_completion = statistics.mean(completion_rates)
        
        session_lengths = [s.get('time_spent', 0) for s in session_history if s.get('time_spent', 0) > 0]
        avg_session_length = statistics.mean(session_lengths) if session_lengths else 0
        
        # Engagement score (0-100)
        engagement_score = (avg_completion * 0.4) + (min(avg_session_length / 15, 1) * 30) + (min(len(session_history) / 20, 1) * 30)
        
        # Identify patterns
        patterns = []
        if avg_completion > 90:
            patterns.append('High completion rate - excellent focus')
        if avg_session_length > 10:
            patterns.append('Extended session times - deep engagement')
        if len(session_history) > 10:
            patterns.append('Consistent learning habit established')
        
        return {
            'engagement_score': round(engagement_score, 1),
            'avg_completion_rate': round(avg_completion, 1),
            'avg_session_length': round(avg_session_length, 1),
            'patterns': patterns
        }
    
    def _analyze_subject_performance(self, session_history: List[Dict]) -> List[Dict]:
        """Analyze performance by subject"""
        subject_data = defaultdict(list)
        
        for session in session_history:
            subject = session.get('subject')
            if subject:
                subject_data[subject].append(session)
        
        subject_analysis = []
        for subject, sessions in subject_data.items():
            accuracies = [s.get('accuracy', 0) for s in sessions]
            avg_accuracy = statistics.mean(accuracies)
            
            subject_analysis.append({
                'subject': subject,
                'sessions': len(sessions),
                'avg_accuracy': round(avg_accuracy, 1),
                'total_time': sum(s.get('time_spent', 0) for s in sessions),
                'trend': self._calculate_subject_trend(accuracies),
                'mastery_level': self._calculate_mastery_level(avg_accuracy, len(sessions))
            })
        
        # Sort by number of sessions
        subject_analysis.sort(key=lambda x: x['sessions'], reverse=True)
        return subject_analysis
    
    def _calculate_subject_trend(self, accuracies: List[float]) -> str:
        """Calculate trend for a specific subject"""
        if len(accuracies) < 3:
            return 'insufficient_data'
        
        recent = statistics.mean(accuracies[-3:])
        earlier = statistics.mean(accuracies[:-3])
        
        if recent > earlier + 5:
            return 'improving'
        elif recent < earlier - 5:
            return 'declining'
        else:
            return 'stable'
    
    def _calculate_mastery_level(self, avg_accuracy: float, session_count: int) -> str:
        """Calculate mastery level for a subject"""
        if session_count < 3:
            return 'novice'
        elif avg_accuracy >= 85 and session_count >= 10:
            return 'expert'
        elif avg_accuracy >= 75 and session_count >= 5:
            return 'proficient'
        elif avg_accuracy >= 60:
            return 'developing'
        else:
            return 'beginner'
    
    def _generate_weekly_summary(self, session_history: List[Dict]) -> Dict:
        """Generate weekly activity summary"""
        now = datetime.now()
        week_start = now - timedelta(days=7)
        
        recent_sessions = [
            s for s in session_history 
            if datetime.fromisoformat(s['date'].replace('Z', '+00:00')) >= week_start
        ]
        
        if not recent_sessions:
            return {
                'sessions_this_week': 0,
                'time_this_week': 0,
                'avg_accuracy_this_week': 0,
                'subjects_this_week': 0,
                'daily_breakdown': []
            }
        
        # Daily breakdown
        daily_data = defaultdict(list)
        for session in recent_sessions:
            session_date = datetime.fromisoformat(session['date'].replace('Z', '+00:00')).date()
            daily_data[session_date].append(session)
        
        daily_breakdown = []
        for i in range(7):
            day = (now - timedelta(days=6-i)).date()
            day_sessions = daily_data.get(day, [])
            daily_breakdown.append({
                'date': day.isoformat(),
                'sessions': len(day_sessions),
                'accuracy': round(statistics.mean([s.get('accuracy', 0) for s in day_sessions]), 1) if day_sessions else 0,
                'time_spent': sum(s.get('time_spent', 0) for s in day_sessions)
            })
        
        return {
            'sessions_this_week': len(recent_sessions),
            'time_this_week': sum(s.get('time_spent', 0) for s in recent_sessions),
            'avg_accuracy_this_week': round(statistics.mean([s.get('accuracy', 0) for s in recent_sessions]), 1),
            'subjects_this_week': len(set(s.get('subject') for s in recent_sessions)),
            'daily_breakdown': daily_breakdown
        }
    
    def _calculate_current_streak(self, session_history: List[Dict]) -> int:
        """Calculate current consecutive day streak"""
        if not session_history:
            return 0
        
        # Get unique session dates
        session_dates = list(set(
            datetime.fromisoformat(s['date'].replace('Z', '+00:00')).date() 
            for s in session_history
        ))
        session_dates.sort(reverse=True)
        
        if not session_dates:
            return 0
        
        # Check if today or yesterday has a session
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        if session_dates[0] not in [today, yesterday]:
            return 0  # Streak broken
        
        # Count consecutive days
        streak = 0
        current_date = session_dates[0]
        
        for session_date in session_dates:
            if session_date == current_date:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        return streak
    
    def _generate_recommendations(self, user_id: str, session_history: List[Dict], predictions: Dict) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if not session_history:
            return [
                'Start with a quick 5-question session to establish your baseline',
                'Try different subjects to discover your interests',
                'Set up a daily learning reminder'
            ]
        
        # Based on performance trends
        if predictions.get('retention_forecast') == 'needs_attention':
            recommendations.append('Focus on reviewing concepts you find challenging')
            recommendations.append('Consider shorter, more frequent sessions')
        
        # Based on engagement
        avg_accuracy = statistics.mean([s.get('accuracy', 0) for s in session_history])
        if avg_accuracy < 60:
            recommendations.append('Try easier difficulty levels to build confidence')
            recommendations.append('Review explanations carefully after each question')
        elif avg_accuracy > 85:
            recommendations.append('Challenge yourself with advanced difficulty levels')
            recommendations.append('Explore new subjects to expand your knowledge')
        
        # Based on activity patterns
        recent_sessions = len([s for s in session_history[-7:] if s])
        if recent_sessions < 3:
            recommendations.append('Aim for at least 3 sessions per week for optimal retention')
        
        # Subject-specific recommendations
        subjects = set(s.get('subject') for s in session_history)
        if len(subjects) == 1:
            recommendations.append('Try learning complementary subjects to broaden your skills')
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def generate_institutional_report(self, institution_id: str = None) -> Dict:
        """Generate comprehensive institutional analytics report"""
        all_users = list(self.user_metrics.keys())
        
        if not all_users:
            return {'error': 'No user data available'}
        
        # Aggregate metrics
        total_sessions = sum(metrics.get('total_sessions', 0) for metrics in self.user_metrics.values())
        total_users = len(all_users)
        active_users = sum(1 for metrics in self.user_metrics.values() 
                          if (datetime.now() - datetime.fromisoformat(metrics.get('last_updated', datetime.now().isoformat()))).days <= 7)
        
        avg_accuracy = statistics.mean([metrics.get('avg_accuracy', 0) for metrics in self.user_metrics.values() if metrics.get('avg_accuracy', 0) > 0])
        
        # Risk analysis
        at_risk_users = sum(1 for user_id in all_users if self._assess_user_risk(user_id) == 'high')
        
        return {
            'institution_id': institution_id or 'default',
            'generated_at': datetime.now().isoformat(),
            'overview': {
                'total_users': total_users,
                'active_users': active_users,
                'total_sessions': total_sessions,
                'avg_accuracy': round(avg_accuracy, 1) if avg_accuracy else 0,
                'at_risk_users': at_risk_users
            },
            'engagement_metrics': self._calculate_institutional_engagement(),
            'performance_distribution': self._calculate_performance_distribution(),
            'subject_popularity': self._calculate_subject_popularity(),
            'recommendations': self._generate_institutional_recommendations()
        }
    
    def _assess_user_risk(self, user_id: str) -> str:
        """Assess if user is at risk of dropping out"""
        if user_id not in self.analytics_data:
            return 'unknown'
        
        session_history = self.analytics_data[user_id].get('session_history', [])
        if not session_history:
            return 'high'
        
        # Check recent activity
        last_session = datetime.fromisoformat(session_history[-1]['date'].replace('Z', '+00:00'))
        days_inactive = (datetime.now() - last_session).days
        
        if days_inactive > 14:
            return 'high'
        elif days_inactive > 7:
            return 'medium'
        
        # Check performance trend
        if len(session_history) >= 5:
            recent_accuracy = statistics.mean([s.get('accuracy', 0) for s in session_history[-5:]])
            if recent_accuracy < 40:
                return 'high'
            elif recent_accuracy < 60:
                return 'medium'
        
        return 'low'
    
    def _calculate_institutional_engagement(self) -> Dict:
        """Calculate institutional engagement metrics"""
        engagement_scores = []
        for user_id, metrics in self.user_metrics.items():
            if user_id in self.analytics_data:
                session_history = self.analytics_data[user_id].get('session_history', [])
                engagement = self._analyze_engagement_patterns(user_id, session_history)
                engagement_scores.append(engagement.get('engagement_score', 0))
        
        if not engagement_scores:
            return {'avg_engagement': 0, 'distribution': {}}
        
        avg_engagement = statistics.mean(engagement_scores)
        
        # Distribution
        high_engagement = sum(1 for score in engagement_scores if score >= 70)
        medium_engagement = sum(1 for score in engagement_scores if 40 <= score < 70)
        low_engagement = sum(1 for score in engagement_scores if score < 40)
        
        return {
            'avg_engagement': round(avg_engagement, 1),
            'distribution': {
                'high': high_engagement,
                'medium': medium_engagement,
                'low': low_engagement
            }
        }
    
    def _calculate_performance_distribution(self) -> Dict:
        """Calculate performance distribution across users"""
        accuracies = [metrics.get('avg_accuracy', 0) for metrics in self.user_metrics.values() if metrics.get('avg_accuracy', 0) > 0]
        
        if not accuracies:
            return {'distribution': {}, 'percentiles': {}}
        
        # Performance bands
        excellent = sum(1 for acc in accuracies if acc >= 85)
        good = sum(1 for acc in accuracies if 70 <= acc < 85)
        fair = sum(1 for acc in accuracies if 55 <= acc < 70)
        needs_improvement = sum(1 for acc in accuracies if acc < 55)
        
        # Percentiles
        percentiles = {
            '25th': round(statistics.quantiles(accuracies, n=4)[0], 1),
            '50th': round(statistics.median(accuracies), 1),
            '75th': round(statistics.quantiles(accuracies, n=4)[2], 1),
            '90th': round(statistics.quantiles(accuracies, n=10)[8], 1)
        }
        
        return {
            'distribution': {
                'excellent': excellent,
                'good': good,
                'fair': fair,
                'needs_improvement': needs_improvement
            },
            'percentiles': percentiles
        }
    
    def _calculate_subject_popularity(self) -> List[Dict]:
        """Calculate subject popularity across institution"""
        subject_stats = defaultdict(lambda: {'users': 0, 'sessions': 0, 'avg_accuracy': []})
        
        for user_id, analytics in self.analytics_data.items():
            session_history = analytics.get('session_history', [])
            user_subjects = set()
            
            for session in session_history:
                subject = session.get('subject')
                if subject:
                    subject_stats[subject]['sessions'] += 1
                    subject_stats[subject]['avg_accuracy'].append(session.get('accuracy', 0))
                    user_subjects.add(subject)
            
            for subject in user_subjects:
                subject_stats[subject]['users'] += 1
        
        popularity_list = []
        for subject, stats in subject_stats.items():
            avg_accuracy = statistics.mean(stats['avg_accuracy']) if stats['avg_accuracy'] else 0
            popularity_list.append({
                'subject': subject,
                'users': stats['users'],
                'sessions': stats['sessions'],
                'avg_accuracy': round(avg_accuracy, 1)
            })
        
        popularity_list.sort(key=lambda x: x['sessions'], reverse=True)
        return popularity_list[:10]  # Top 10 subjects
    
    def _generate_institutional_recommendations(self) -> List[str]:
        """Generate recommendations for institutional improvement"""
        recommendations = []
        
        # Analyze overall metrics
        total_users = len(self.user_metrics)
        if total_users == 0:
            return ['No users to analyze']
        
        active_rate = sum(1 for metrics in self.user_metrics.values() 
                         if (datetime.now() - datetime.fromisoformat(metrics.get('last_updated', datetime.now().isoformat()))).days <= 7) / total_users
        
        if active_rate < 0.3:
            recommendations.append('Low user engagement - consider implementing retention strategies')
        
        at_risk_count = sum(1 for user_id in self.user_metrics.keys() if self._assess_user_risk(user_id) == 'high')
        if at_risk_count > total_users * 0.2:
            recommendations.append('High number of at-risk users - implement early intervention programs')
        
        avg_accuracy = statistics.mean([metrics.get('avg_accuracy', 0) for metrics in self.user_metrics.values() if metrics.get('avg_accuracy', 0) > 0])
        if avg_accuracy < 60:
            recommendations.append('Consider providing additional learning support and resources')
        
        return recommendations

# Global instance
analytics_dashboard = AnalyticsDashboard()