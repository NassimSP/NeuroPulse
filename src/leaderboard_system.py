"""
Leaderboard and Social Learning System for NeuroPulse
Implements per-topic and global rankings with ADHD-friendly gamification
"""

import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class LeaderboardType(Enum):
    GLOBAL = "global"
    SUBJECT = "subject"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    STREAK = "streak"
    ACCURACY = "accuracy"

class LeaderboardEngine:
    """Advanced leaderboard system with social learning features"""
    
    def __init__(self):
        self.leaderboards = {}
        self.user_stats = {}
        self.achievements = {}
        self.social_interactions = {}
        self.load_data()
    
    def load_data(self):
        """Load leaderboard and social data"""
        try:
            with open('data/leaderboard_data.json', 'r') as f:
                data = json.load(f)
                self.leaderboards = data.get('leaderboards', {})
                self.user_stats = data.get('user_stats', {})
                self.achievements = data.get('achievements', {})
                self.social_interactions = data.get('social_interactions', {})
        except FileNotFoundError:
            self.leaderboards = {}
            self.user_stats = {}
            self.achievements = {}
            self.social_interactions = {}
            self._initialize_default_leaderboards()
    
    def save_data(self):
        """Save leaderboard and social data"""
        import os
        os.makedirs('data', exist_ok=True)
        
        data = {
            'leaderboards': self.leaderboards,
            'user_stats': self.user_stats,
            'achievements': self.achievements,
            'social_interactions': self.social_interactions,
            'last_updated': datetime.now().isoformat()
        }
        
        with open('data/leaderboard_data.json', 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _initialize_default_leaderboards(self):
        """Initialize default leaderboard categories"""
        categories = [
            'global', 'Python Programming', 'Electrical Engineering',
            'Financial Planning', 'Data Analysis', 'Botany', 'Chemistry',
            'Physics', 'Mathematics'
        ]
        
        for category in categories:
            self.leaderboards[category] = {
                'daily': [],
                'weekly': [],
                'monthly': [],
                'all_time': [],
                'streak': [],
                'accuracy': []
            }
    
    def update_user_performance(self, user_id: str, username: str, subject: str, 
                              session_data: Dict) -> Dict:
        """Update user performance and recalculate leaderboards"""
        
        # Initialize user stats if needed
        if user_id not in self.user_stats:
            self.user_stats[user_id] = {
                'username': username,
                'total_sessions': 0,
                'total_questions': 0,
                'total_correct': 0,
                'current_streak': 0,
                'longest_streak': 0,
                'subjects': {},
                'last_active': datetime.now().isoformat(),
                'join_date': datetime.now().isoformat(),
                'achievements': [],
                'points': 0,
                'level': 1
            }
        
        user_stats = self.user_stats[user_id]
        
        # Update username in case it changed
        user_stats['username'] = username
        
        # Initialize subject stats if needed
        if subject not in user_stats['subjects']:
            user_stats['subjects'][subject] = {
                'sessions': 0,
                'questions': 0,
                'correct': 0,
                'streak': 0,
                'level': 1,
                'xp': 0,
                'best_accuracy': 0,
                'total_time': 0
            }
        
        subject_stats = user_stats['subjects'][subject]
        
        # Extract session performance
        questions_answered = len(session_data.get('questions', []))
        correct_answers = session_data.get('correct_answers', 0)
        session_accuracy = (correct_answers / questions_answered * 100) if questions_answered > 0 else 0
        confidence_ratings = session_data.get('confidence_ratings', [])
        avg_confidence = sum(r.get('confidence', 3) for r in confidence_ratings) / len(confidence_ratings) if confidence_ratings else 3
        
        # Update global stats
        user_stats['total_sessions'] += 1
        user_stats['total_questions'] += questions_answered
        user_stats['total_correct'] += correct_answers
        user_stats['last_active'] = datetime.now().isoformat()
        
        # Update streak
        if session_accuracy >= 70:  # 70% threshold for streak continuation
            user_stats['current_streak'] += 1
            subject_stats['streak'] += 1
            if user_stats['current_streak'] > user_stats['longest_streak']:
                user_stats['longest_streak'] = user_stats['current_streak']
        else:
            user_stats['current_streak'] = 0
            subject_stats['streak'] = 0
        
        # Update subject stats
        subject_stats['sessions'] += 1
        subject_stats['questions'] += questions_answered
        subject_stats['correct'] += correct_answers
        if session_accuracy > subject_stats['best_accuracy']:
            subject_stats['best_accuracy'] = session_accuracy
        
        # Calculate XP and points
        xp_earned = self._calculate_xp(session_data, session_accuracy, avg_confidence)
        subject_stats['xp'] += xp_earned
        user_stats['points'] += xp_earned
        
        # Update level based on XP
        subject_stats['level'] = self._calculate_level(subject_stats['xp'])
        user_stats['level'] = self._calculate_level(user_stats['points'])
        
        # Update leaderboards
        self._update_leaderboard_rankings(user_id, subject, session_data, session_accuracy)
        
        # Check for new achievements
        new_achievements = self._check_achievements(user_id, subject, session_data, session_accuracy)
        
        self.save_data()
        
        return {
            'xp_earned': xp_earned,
            'new_level': user_stats['level'],
            'subject_level': subject_stats['level'],
            'new_achievements': new_achievements,
            'current_streak': user_stats['current_streak'],
            'leaderboard_position': self._get_user_position(user_id, subject)
        }
    
    def _calculate_xp(self, session_data: Dict, accuracy: float, avg_confidence: float) -> int:
        """Calculate XP earned from session with ADHD-friendly bonuses"""
        base_xp = len(session_data.get('questions', [])) * 10  # 10 XP per question
        
        # Accuracy bonus
        accuracy_bonus = int(base_xp * (accuracy / 100) * 0.5)  # Up to 50% bonus for perfect accuracy
        
        # Confidence bonus (rewards honest self-assessment)
        confidence_bonus = int(base_xp * 0.1) if 2 <= avg_confidence <= 4 else 0  # Bonus for realistic confidence
        
        # Streak bonus
        streak_bonus = min(int(base_xp * 0.2), 50)  # Up to 20% bonus for streaks, capped at 50 XP
        
        # Completion bonus
        completion_bonus = int(base_xp * 0.3)  # 30% bonus for completing session
        
        # Difficulty bonus
        difficulty_map = {'foundation': 1.0, 'beginner': 1.1, 'intermediate': 1.2, 'advanced': 1.4, 'expert': 1.6}
        difficulty_multiplier = difficulty_map.get(session_data.get('difficulty', 'intermediate'), 1.2)
        
        total_xp = int((base_xp + accuracy_bonus + confidence_bonus + streak_bonus + completion_bonus) * difficulty_multiplier)
        
        return max(total_xp, base_xp)  # Ensure minimum base XP
    
    def _calculate_level(self, total_xp: int) -> int:
        """Calculate level based on total XP with ADHD-friendly progression"""
        # More frequent level-ups for dopamine hits
        if total_xp < 100:
            return 1
        return min(int(math.sqrt(total_xp / 100)) + 1, 100)  # Cap at level 100
    
    def _update_leaderboard_rankings(self, user_id: str, subject: str, session_data: Dict, accuracy: float):
        """Update all relevant leaderboard rankings"""
        user_stats = self.user_stats[user_id]
        
        # Prepare user entry
        user_entry = {
            'user_id': user_id,
            'username': user_stats['username'],
            'points': user_stats['points'],
            'level': user_stats['level'],
            'accuracy': (user_stats['total_correct'] / user_stats['total_questions'] * 100) if user_stats['total_questions'] > 0 else 0,
            'streak': user_stats['current_streak'],
            'sessions': user_stats['total_sessions'],
            'last_updated': datetime.now().isoformat()
        }
        
        # Update global leaderboards
        self._update_leaderboard_category('global', user_entry)
        
        # Update subject-specific leaderboards
        if subject in user_stats['subjects']:
            subject_stats = user_stats['subjects'][subject]
            subject_entry = {
                'user_id': user_id,
                'username': user_stats['username'],
                'subject_xp': subject_stats['xp'],
                'subject_level': subject_stats['level'],
                'subject_accuracy': (subject_stats['correct'] / subject_stats['questions'] * 100) if subject_stats['questions'] > 0 else 0,
                'subject_streak': subject_stats['streak'],
                'subject_sessions': subject_stats['sessions'],
                'last_updated': datetime.now().isoformat()
            }
            self._update_leaderboard_category(subject, subject_entry)
    
    def _update_leaderboard_category(self, category: str, user_entry: Dict):
        """Update a specific leaderboard category"""
        if category not in self.leaderboards:
            self.leaderboards[category] = {
                'daily': [], 'weekly': [], 'monthly': [], 'all_time': [], 'streak': [], 'accuracy': []
            }
        
        leaderboard = self.leaderboards[category]
        
        # Update all-time leaderboard
        self._update_ranking_list(leaderboard['all_time'], user_entry, 'points', 100)
        
        # Update streak leaderboard
        self._update_ranking_list(leaderboard['streak'], user_entry, 'streak', 50)
        
        # Update accuracy leaderboard
        self._update_ranking_list(leaderboard['accuracy'], user_entry, 'accuracy', 50)
        
        # Update time-based leaderboards (daily, weekly, monthly)
        self._update_time_based_leaderboards(category, user_entry)
    
    def _update_ranking_list(self, ranking_list: List[Dict], user_entry: Dict, sort_key: str, max_size: int):
        """Update a ranking list with proper sorting"""
        # Remove existing entry for this user
        ranking_list[:] = [entry for entry in ranking_list if entry['user_id'] != user_entry['user_id']]
        
        # Add new entry
        ranking_list.append(user_entry)
        
        # Sort by the specified key (descending)
        ranking_list.sort(key=lambda x: x.get(sort_key, 0), reverse=True)
        
        # Trim to max size
        ranking_list[:] = ranking_list[:max_size]
    
    def _update_time_based_leaderboards(self, category: str, user_entry: Dict):
        """Update time-based leaderboards (daily, weekly, monthly)"""
        now = datetime.now()
        
        # Daily leaderboard (resets daily)
        daily_key = now.strftime('%Y-%m-%d')
        if not hasattr(self, '_daily_reset') or self._daily_reset != daily_key:
            self.leaderboards[category]['daily'] = []
            self._daily_reset = daily_key
        
        self._update_ranking_list(self.leaderboards[category]['daily'], user_entry, 'points', 50)
        
        # Weekly leaderboard (resets weekly)
        week_start = now - timedelta(days=now.weekday())
        weekly_key = week_start.strftime('%Y-%W')
        if not hasattr(self, '_weekly_reset') or self._weekly_reset != weekly_key:
            self.leaderboards[category]['weekly'] = []
            self._weekly_reset = weekly_key
        
        self._update_ranking_list(self.leaderboards[category]['weekly'], user_entry, 'points', 50)
        
        # Monthly leaderboard (resets monthly)
        monthly_key = now.strftime('%Y-%m')
        if not hasattr(self, '_monthly_reset') or self._monthly_reset != monthly_key:
            self.leaderboards[category]['monthly'] = []
            self._monthly_reset = monthly_key
        
        self._update_ranking_list(self.leaderboards[category]['monthly'], user_entry, 'points', 50)
    
    def _check_achievements(self, user_id: str, subject: str, session_data: Dict, accuracy: float) -> List[Dict]:
        """Check and award new achievements"""
        new_achievements = []
        user_stats = self.user_stats[user_id]
        
        # Achievement definitions
        achievement_checks = [
            # Session-based achievements
            {'id': 'perfect_session', 'condition': accuracy == 100, 'title': 'Perfect Score!', 'description': 'Achieved 100% accuracy in a session', 'points': 50},
            {'id': 'high_accuracy', 'condition': accuracy >= 90, 'title': 'Excellence', 'description': 'Achieved 90%+ accuracy', 'points': 25},
            {'id': 'completed_session', 'condition': True, 'title': 'Session Complete', 'description': 'Completed a learning session', 'points': 10},
            
            # Streak achievements
            {'id': 'streak_3', 'condition': user_stats['current_streak'] == 3, 'title': 'Getting Consistent', 'description': '3-day learning streak', 'points': 30},
            {'id': 'streak_7', 'condition': user_stats['current_streak'] == 7, 'title': 'Week Warrior', 'description': '7-day learning streak', 'points': 75},
            {'id': 'streak_30', 'condition': user_stats['current_streak'] == 30, 'title': 'Month Master', 'description': '30-day learning streak', 'points': 200},
            
            # Session count achievements
            {'id': 'sessions_10', 'condition': user_stats['total_sessions'] == 10, 'title': 'Getting Started', 'description': 'Completed 10 sessions', 'points': 50},
            {'id': 'sessions_50', 'condition': user_stats['total_sessions'] == 50, 'title': 'Dedicated Learner', 'description': 'Completed 50 sessions', 'points': 150},
            {'id': 'sessions_100', 'condition': user_stats['total_sessions'] == 100, 'title': 'Centurion', 'description': 'Completed 100 sessions', 'points': 300},
            
            # Level achievements
            {'id': 'level_5', 'condition': user_stats['level'] == 5, 'title': 'Rising Star', 'description': 'Reached level 5', 'points': 40},
            {'id': 'level_10', 'condition': user_stats['level'] == 10, 'title': 'Expert Learner', 'description': 'Reached level 10', 'points': 100},
            {'id': 'level_25', 'condition': user_stats['level'] == 25, 'title': 'Learning Master', 'description': 'Reached level 25', 'points': 250},
            
            # Subject diversity achievements
            {'id': 'subjects_3', 'condition': len(user_stats['subjects']) == 3, 'title': 'Explorer', 'description': 'Learned 3 different subjects', 'points': 60},
            {'id': 'subjects_5', 'condition': len(user_stats['subjects']) == 5, 'title': 'Renaissance Mind', 'description': 'Learned 5 different subjects', 'points': 120},
            {'id': 'subjects_10', 'condition': len(user_stats['subjects']) == 10, 'title': 'Polymath', 'description': 'Learned 10 different subjects', 'points': 300},
        ]
        
        # Check each achievement
        for achievement in achievement_checks:
            achievement_id = f"{achievement['id']}_{user_id}"
            
            # Skip if already earned
            if achievement_id in user_stats.get('achievements', []):
                continue
            
            # Check condition
            if achievement['condition']:
                new_achievements.append({
                    'id': achievement['id'],
                    'title': achievement['title'],
                    'description': achievement['description'],
                    'points': achievement['points'],
                    'earned_at': datetime.now().isoformat(),
                    'subject': subject
                })
                
                # Add to user's achievements
                if 'achievements' not in user_stats:
                    user_stats['achievements'] = []
                user_stats['achievements'].append(achievement_id)
                
                # Award points
                user_stats['points'] += achievement['points']
        
        return new_achievements
    
    def get_leaderboard(self, category: str = 'global', timeframe: str = 'all_time', limit: int = 50) -> Dict:
        """Get leaderboard data for display"""
        if category not in self.leaderboards:
            return {'rankings': [], 'total_users': 0, 'category': category, 'timeframe': timeframe}
        
        if timeframe not in self.leaderboards[category]:
            timeframe = 'all_time'
        
        rankings = self.leaderboards[category][timeframe][:limit]
        
        # Add rank numbers
        for i, entry in enumerate(rankings):
            entry['rank'] = i + 1
        
        return {
            'rankings': rankings,
            'total_users': len(self.user_stats),
            'category': category,
            'timeframe': timeframe,
            'last_updated': datetime.now().isoformat()
        }
    
    def _get_user_position(self, user_id: str, subject: str = 'global') -> Dict:
        """Get user's position in various leaderboards"""
        positions = {}
        
        if subject in self.leaderboards:
            for timeframe, rankings in self.leaderboards[subject].items():
                for i, entry in enumerate(rankings):
                    if entry['user_id'] == user_id:
                        positions[timeframe] = i + 1
                        break
                else:
                    positions[timeframe] = None
        
        return positions
    
    def get_user_analytics(self, user_id: str) -> Dict:
        """Get comprehensive analytics for a user"""
        if user_id not in self.user_stats:
            return {'error': 'User not found'}
        
        user_stats = self.user_stats[user_id]
        
        # Calculate overall accuracy
        overall_accuracy = (user_stats['total_correct'] / user_stats['total_questions'] * 100) if user_stats['total_questions'] > 0 else 0
        
        # Get positions in leaderboards
        global_positions = self._get_user_position(user_id, 'global')
        
        # Subject performance
        subject_performance = []
        for subject, stats in user_stats['subjects'].items():
            subject_accuracy = (stats['correct'] / stats['questions'] * 100) if stats['questions'] > 0 else 0
            subject_positions = self._get_user_position(user_id, subject)
            
            subject_performance.append({
                'subject': subject,
                'level': stats['level'],
                'xp': stats['xp'],
                'accuracy': round(subject_accuracy, 1),
                'sessions': stats['sessions'],
                'streak': stats['streak'],
                'positions': subject_positions
            })
        
        # Recent achievements
        recent_achievements = user_stats.get('achievements', [])[-5:]
        
        return {
            'user_id': user_id,
            'username': user_stats['username'],
            'level': user_stats['level'],
            'points': user_stats['points'],
            'overall_accuracy': round(overall_accuracy, 1),
            'current_streak': user_stats['current_streak'],
            'longest_streak': user_stats['longest_streak'],
            'total_sessions': user_stats['total_sessions'],
            'subjects_learned': len(user_stats['subjects']),
            'global_positions': global_positions,
            'subject_performance': subject_performance,
            'recent_achievements': recent_achievements,
            'join_date': user_stats['join_date'],
            'last_active': user_stats['last_active']
        }
    
    def get_social_features(self, user_id: str) -> Dict:
        """Get social learning features and recommendations"""
        user_stats = self.user_stats.get(user_id, {})
        
        # Find peers with similar interests
        similar_users = self._find_similar_users(user_id)
        
        # Get trending subjects
        trending_subjects = self._get_trending_subjects()
        
        # Get study group recommendations
        study_groups = self._get_study_group_recommendations(user_id)
        
        return {
            'similar_users': similar_users,
            'trending_subjects': trending_subjects,
            'study_group_recommendations': study_groups,
            'challenges': self._get_active_challenges(user_id)
        }
    
    def _find_similar_users(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Find users with similar learning patterns"""
        if user_id not in self.user_stats:
            return []
        
        user_subjects = set(self.user_stats[user_id].get('subjects', {}).keys())
        similar_users = []
        
        for other_id, other_stats in self.user_stats.items():
            if other_id == user_id:
                continue
            
            other_subjects = set(other_stats.get('subjects', {}).keys())
            
            # Calculate similarity based on shared subjects
            if user_subjects and other_subjects:
                similarity = len(user_subjects.intersection(other_subjects)) / len(user_subjects.union(other_subjects))
                
                if similarity > 0.3:  # At least 30% similarity
                    similar_users.append({
                        'user_id': other_id,
                        'username': other_stats['username'],
                        'level': other_stats['level'],
                        'shared_subjects': list(user_subjects.intersection(other_subjects)),
                        'similarity': round(similarity, 2)
                    })
        
        # Sort by similarity
        similar_users.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_users[:limit]
    
    def _get_trending_subjects(self, limit: int = 5) -> List[Dict]:
        """Get currently trending subjects"""
        subject_activity = {}
        
        # Count recent activity per subject
        for user_stats in self.user_stats.values():
            for subject, stats in user_stats.get('subjects', {}).items():
                if subject not in subject_activity:
                    subject_activity[subject] = {'sessions': 0, 'users': 0}
                
                subject_activity[subject]['sessions'] += stats['sessions']
                subject_activity[subject]['users'] += 1
        
        # Calculate trending score
        trending = []
        for subject, activity in subject_activity.items():
            trending_score = activity['sessions'] * math.log(activity['users'] + 1)
            trending.append({
                'subject': subject,
                'activity_score': trending_score,
                'total_sessions': activity['sessions'],
                'active_users': activity['users']
            })
        
        trending.sort(key=lambda x: x['activity_score'], reverse=True)
        return trending[:limit]
    
    def _get_study_group_recommendations(self, user_id: str) -> List[Dict]:
        """Get study group recommendations"""
        # This would integrate with the collaborative learning system
        return [
            {
                'group_id': 'python_beginners',
                'name': 'Python Beginners Study Group',
                'subject': 'Python Programming',
                'members': 12,
                'activity_level': 'high'
            },
            {
                'group_id': 'electrical_pros',
                'name': 'Electrical Engineering Professionals',
                'subject': 'Electrical Engineering',
                'members': 8,
                'activity_level': 'medium'
            }
        ]
    
    def _get_active_challenges(self, user_id: str) -> List[Dict]:
        """Get active learning challenges"""
        return [
            {
                'challenge_id': 'weekly_streak',
                'name': 'Weekly Learning Streak',
                'description': 'Learn for 7 consecutive days',
                'progress': self.user_stats.get(user_id, {}).get('current_streak', 0),
                'target': 7,
                'reward': 'Week Warrior Badge + 75 XP'
            },
            {
                'challenge_id': 'subject_explorer',
                'name': 'Subject Explorer',
                'description': 'Try 3 different subjects this month',
                'progress': len(self.user_stats.get(user_id, {}).get('subjects', {})),
                'target': 3,
                'reward': 'Explorer Badge + 60 XP'
            }
        ]

# Global instance
leaderboard_engine = LeaderboardEngine()