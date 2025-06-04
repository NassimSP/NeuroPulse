"""
Social Learning Features for NeuroPulse
Handles peer comparison, collaborative challenges, study groups, and community features
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class SocialLearningManager:
    def __init__(self):
        self.challenges_file = 'challenges_data.json'
        self.study_groups_file = 'study_groups_data.json'
        self.social_progress_file = 'social_progress_data.json'
        self.achievements_file = 'social_achievements_data.json'
        
        self.load_data()
    
    def load_data(self):
        """Load all social learning data"""
        self.challenges = self._load_json_file(self.challenges_file, {})
        self.study_groups = self._load_json_file(self.study_groups_file, {})
        self.social_progress = self._load_json_file(self.social_progress_file, {})
        self.achievements = self._load_json_file(self.achievements_file, {})
    
    def _load_json_file(self, filename: str, default: dict) -> dict:
        """Load JSON file with fallback to default"""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return default
    
    def _save_json_file(self, filename: str, data: dict):
        """Save data to JSON file"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_challenge(self, creator_id: str, challenge_data: dict) -> str:
        """Create a new collaborative challenge"""
        challenge_id = str(uuid.uuid4())
        
        challenge = {
            'id': challenge_id,
            'creator_id': creator_id,
            'title': challenge_data.get('title'),
            'description': challenge_data.get('description'),
            'subject_category': challenge_data.get('subject_category'),
            'topic': challenge_data.get('topic'),
            'difficulty_level': challenge_data.get('difficulty_level', 'intermediate'),
            'question_count': challenge_data.get('question_count', 10),
            'time_limit_hours': challenge_data.get('time_limit_hours', 24),
            'max_participants': challenge_data.get('max_participants', 50),
            'reward_badges': challenge_data.get('reward_badges', []),
            'created_at': datetime.now().isoformat(),
            'start_time': challenge_data.get('start_time'),
            'end_time': challenge_data.get('end_time'),
            'status': 'active',
            'participants': {},
            'leaderboard': [],
            'collaboration_type': challenge_data.get('collaboration_type', 'competitive'), # competitive, collaborative, team-based
            'rules': challenge_data.get('rules', []),
            'discussion_enabled': challenge_data.get('discussion_enabled', True)
        }
        
        self.challenges[challenge_id] = challenge
        self._save_json_file(self.challenges_file, self.challenges)
        
        return challenge_id
    
    def join_challenge(self, challenge_id: str, user_id: str, user_name: str = None) -> bool:
        """Join an existing challenge"""
        if challenge_id not in self.challenges:
            return False
        
        challenge = self.challenges[challenge_id]
        
        # Check if challenge is still active and has space
        if (challenge['status'] != 'active' or 
            len(challenge['participants']) >= challenge['max_participants']):
            return False
        
        # Add participant
        challenge['participants'][user_id] = {
            'user_id': user_id,
            'user_name': user_name or f"User_{user_id[:8]}",
            'joined_at': datetime.now().isoformat(),
            'progress': {
                'questions_answered': 0,
                'correct_answers': 0,
                'completion_time': None,
                'accuracy_rate': 0.0,
                'streak_count': 0
            },
            'status': 'active'
        }
        
        self._save_json_file(self.challenges_file, self.challenges)
        return True
    
    def update_challenge_progress(self, challenge_id: str, user_id: str, session_data: dict):
        """Update user progress in a challenge"""
        if challenge_id not in self.challenges:
            return False
        
        challenge = self.challenges[challenge_id]
        if user_id not in challenge['participants']:
            return False
        
        participant = challenge['participants'][user_id]
        progress = participant['progress']
        
        # Update progress
        progress['questions_answered'] += session_data.get('questions_answered', 0)
        progress['correct_answers'] += session_data.get('correct_answers', 0)
        progress['accuracy_rate'] = progress['correct_answers'] / max(progress['questions_answered'], 1)
        progress['streak_count'] = max(progress['streak_count'], session_data.get('streak_count', 0))
        
        # Check if challenge is completed
        if progress['questions_answered'] >= challenge['question_count']:
            progress['completion_time'] = datetime.now().isoformat()
            participant['status'] = 'completed'
        
        # Update leaderboard
        self._update_challenge_leaderboard(challenge_id)
        
        self._save_json_file(self.challenges_file, self.challenges)
        return True
    
    def _update_challenge_leaderboard(self, challenge_id: str):
        """Update challenge leaderboard based on current progress"""
        challenge = self.challenges[challenge_id]
        
        # Create leaderboard entries
        leaderboard = []
        for user_id, participant in challenge['participants'].items():
            progress = participant['progress']
            
            # Calculate score based on accuracy, speed, and completion
            score = 0
            if progress['questions_answered'] > 0:
                accuracy_score = progress['accuracy_rate'] * 100
                speed_bonus = 10 if participant['status'] == 'completed' else 0
                streak_bonus = min(progress['streak_count'] * 2, 20)
                
                score = accuracy_score + speed_bonus + streak_bonus
            
            leaderboard.append({
                'user_id': user_id,
                'user_name': participant['user_name'],
                'score': round(score, 2),
                'accuracy': round(progress['accuracy_rate'] * 100, 1),
                'questions_answered': progress['questions_answered'],
                'status': participant['status'],
                'completion_time': progress.get('completion_time')
            })
        
        # Sort by score descending
        leaderboard.sort(key=lambda x: x['score'], reverse=True)
        challenge['leaderboard'] = leaderboard
    
    def get_active_challenges(self, subject_category: str = None) -> List[dict]:
        """Get list of active challenges, optionally filtered by subject"""
        active_challenges = []
        
        for challenge_id, challenge in self.challenges.items():
            if challenge['status'] == 'active':
                if subject_category is None or challenge['subject_category'] == subject_category:
                    # Add participant count and spots remaining
                    challenge_info = challenge.copy()
                    challenge_info['participant_count'] = len(challenge['participants'])
                    challenge_info['spots_remaining'] = challenge['max_participants'] - len(challenge['participants'])
                    active_challenges.append(challenge_info)
        
        return sorted(active_challenges, key=lambda x: x['created_at'], reverse=True)
    
    def create_study_group(self, creator_id: str, group_data: dict) -> str:
        """Create a new study group"""
        group_id = str(uuid.uuid4())
        
        study_group = {
            'id': group_id,
            'creator_id': creator_id,
            'name': group_data.get('name'),
            'description': group_data.get('description'),
            'subject_focus': group_data.get('subject_focus'),
            'difficulty_level': group_data.get('difficulty_level', 'mixed'),
            'max_members': group_data.get('max_members', 20),
            'privacy': group_data.get('privacy', 'public'), # public, private, invite-only
            'meeting_schedule': group_data.get('meeting_schedule'),
            'learning_goals': group_data.get('learning_goals', []),
            'created_at': datetime.now().isoformat(),
            'members': {
                creator_id: {
                    'user_id': creator_id,
                    'role': 'admin',
                    'joined_at': datetime.now().isoformat(),
                    'contribution_score': 0,
                    'sessions_attended': 0
                }
            },
            'group_challenges': [],
            'shared_resources': [],
            'discussion_threads': [],
            'group_statistics': {
                'total_sessions': 0,
                'average_accuracy': 0.0,
                'combined_learning_hours': 0,
                'achievements_unlocked': []
            }
        }
        
        self.study_groups[group_id] = study_group
        self._save_json_file(self.study_groups_file, self.study_groups)
        
        return group_id
    
    def join_study_group(self, group_id: str, user_id: str, user_name: str = None) -> bool:
        """Join a study group"""
        if group_id not in self.study_groups:
            return False
        
        group = self.study_groups[group_id]
        
        # Check if group has space and user isn't already a member
        if (len(group['members']) >= group['max_members'] or 
            user_id in group['members']):
            return False
        
        # Add member
        group['members'][user_id] = {
            'user_id': user_id,
            'user_name': user_name or f"User_{user_id[:8]}",
            'role': 'member',
            'joined_at': datetime.now().isoformat(),
            'contribution_score': 0,
            'sessions_attended': 0
        }
        
        self._save_json_file(self.study_groups_file, self.study_groups)
        return True
    
    def get_peer_comparison(self, user_id: str, subject_category: str, topic: str) -> dict:
        """Get peer comparison data for a user in a specific topic"""
        from subject_manager import subject_manager
        
        # Get user's progress
        user_progress = subject_manager.get_user_progress(user_id, subject_category, topic)
        
        # Get all users' progress for this topic
        all_progress = []
        for user_key, progress in subject_manager.user_progress.items():
            if f"_{subject_category}_{topic}" in user_key and not user_key.startswith(user_id):
                other_user_id = user_key.split('_')[0]
                all_progress.append({
                    'user_id': other_user_id,
                    'accuracy': progress['correct_answers'] / max(progress['total_questions_answered'], 1),
                    'total_questions': progress['total_questions_answered'],
                    'learning_streak': progress['learning_streak'],
                    'level': progress['level'],
                    'badges_count': len(progress['badges_earned']),
                    'time_invested': progress['time_invested_minutes']
                })
        
        if not all_progress:
            return {'message': 'No peer data available yet'}
        
        # Calculate percentiles
        user_accuracy = user_progress['correct_answers'] / max(user_progress['total_questions_answered'], 1)
        accuracies = [p['accuracy'] for p in all_progress]
        
        # User's percentile ranking
        better_count = sum(1 for acc in accuracies if user_accuracy > acc)
        percentile = (better_count / len(accuracies)) * 100 if accuracies else 50
        
        # Find similar level peers
        similar_peers = [p for p in all_progress if p['level'] == user_progress['level']]
        
        return {
            'user_stats': {
                'accuracy': round(user_accuracy * 100, 1),
                'total_questions': user_progress['total_questions_answered'],
                'level': user_progress['level'],
                'badges': len(user_progress['badges_earned']),
                'streak': user_progress['learning_streak']
            },
            'peer_ranking': {
                'percentile': round(percentile, 1),
                'rank': better_count + 1,
                'total_users': len(all_progress) + 1
            },
            'similar_level_comparison': {
                'avg_accuracy': round(sum(p['accuracy'] for p in similar_peers) / len(similar_peers) * 100, 1) if similar_peers else 0,
                'avg_questions': round(sum(p['total_questions'] for p in similar_peers) / len(similar_peers), 1) if similar_peers else 0,
                'user_vs_avg': 'above' if user_accuracy > (sum(p['accuracy'] for p in similar_peers) / len(similar_peers) if similar_peers else 0) else 'below'
            },
            'top_performers': sorted(all_progress, key=lambda x: x['accuracy'], reverse=True)[:5],
            'learning_insights': self._generate_learning_insights(user_progress, all_progress)
        }
    
    def _generate_learning_insights(self, user_progress: dict, peer_data: List[dict]) -> List[str]:
        """Generate personalized learning insights based on peer comparison"""
        insights = []
        
        user_accuracy = user_progress['correct_answers'] / max(user_progress['total_questions_answered'], 1)
        avg_peer_accuracy = sum(p['accuracy'] for p in peer_data) / len(peer_data) if peer_data else 0
        
        if user_accuracy > avg_peer_accuracy * 1.1:
            insights.append("You're performing above average! Consider challenging yourself with harder difficulty levels.")
        elif user_accuracy < avg_peer_accuracy * 0.9:
            insights.append("Focus on understanding concepts deeply rather than speed. Quality over quantity!")
        
        avg_questions = sum(p['total_questions'] for p in peer_data) / len(peer_data) if peer_data else 0
        if user_progress['total_questions_answered'] < avg_questions * 0.7:
            insights.append("More practice could help! Peers at your level typically answer more questions.")
        
        high_streak_peers = [p for p in peer_data if p['learning_streak'] > user_progress['learning_streak'] * 1.5]
        if high_streak_peers:
            insights.append("Building a consistent daily practice routine could boost your progress significantly.")
        
        return insights
    
    def get_collaborative_achievements(self, user_id: str) -> dict:
        """Get user's social learning achievements"""
        user_achievements = self.achievements.get(user_id, {
            'challenges_won': 0,
            'challenges_participated': 0,
            'study_groups_joined': 0,
            'peer_help_given': 0,
            'collaboration_badges': [],
            'social_learning_streak': 0
        })
        
        # Calculate achievement levels
        achievement_levels = {
            'challenger': min(user_achievements['challenges_participated'] // 5, 5),
            'winner': min(user_achievements['challenges_won'] // 3, 5),
            'collaborator': min(user_achievements['study_groups_joined'] // 2, 5),
            'mentor': min(user_achievements['peer_help_given'] // 10, 5)
        }
        
        return {
            'stats': user_achievements,
            'levels': achievement_levels,
            'next_milestones': self._calculate_next_milestones(user_achievements),
            'recommended_activities': self._get_recommended_social_activities(user_achievements)
        }
    
    def _calculate_next_milestones(self, achievements: dict) -> dict:
        """Calculate next milestone for each achievement category"""
        return {
            'next_challenge': max(5 - (achievements['challenges_participated'] % 5), 1),
            'next_win': max(3 - (achievements['challenges_won'] % 3), 1),
            'next_group': max(2 - (achievements['study_groups_joined'] % 2), 1),
            'next_mentor_level': max(10 - (achievements['peer_help_given'] % 10), 1)
        }
    
    def _get_recommended_social_activities(self, achievements: dict) -> List[str]:
        """Get personalized recommendations for social learning activities"""
        recommendations = []
        
        if achievements['challenges_participated'] < 3:
            recommendations.append("Join a collaborative challenge to test your skills against peers")
        
        if achievements['study_groups_joined'] == 0:
            recommendations.append("Join a study group in your area of interest for collaborative learning")
        
        if achievements['peer_help_given'] < 5:
            recommendations.append("Help other learners in discussion forums to earn mentor badges")
        
        if achievements['challenges_won'] == 0 and achievements['challenges_participated'] >= 2:
            recommendations.append("Focus on accuracy in your next challenge - you're close to your first win!")
        
        return recommendations
    
    def create_team_challenge(self, creator_id: str, team_size: int, challenge_data: dict) -> str:
        """Create a team-based collaborative challenge"""
        challenge_data.update({
            'collaboration_type': 'team-based',
            'team_size': team_size,
            'teams': {},
            'team_formation': 'auto'  # auto, manual, skill-based
        })
        
        return self.create_challenge(creator_id, challenge_data)
    
    def suggest_study_partners(self, user_id: str, subject_category: str, topic: str) -> List[dict]:
        """Suggest potential study partners based on similar progress and goals"""
        from subject_manager import subject_manager
        
        user_progress = subject_manager.get_user_progress(user_id, subject_category, topic)
        potential_partners = []
        
        # Find users with similar level and recent activity
        for user_key, progress in subject_manager.user_progress.items():
            if (f"_{subject_category}_{topic}" in user_key and 
                not user_key.startswith(user_id) and
                progress['level'] == user_progress['level']):
                
                other_user_id = user_key.split('_')[0]
                
                # Calculate compatibility score
                accuracy_diff = abs(progress['correct_answers'] / max(progress['total_questions_answered'], 1) - 
                                  user_progress['correct_answers'] / max(user_progress['total_questions_answered'], 1))
                
                compatibility_score = max(0, 100 - (accuracy_diff * 100))
                
                if compatibility_score > 60:  # Only suggest compatible partners
                    potential_partners.append({
                        'user_id': other_user_id,
                        'compatibility_score': round(compatibility_score, 1),
                        'level': progress['level'],
                        'shared_interests': [topic],  # Could be expanded
                        'activity_level': 'active' if progress.get('last_session') else 'moderate'
                    })
        
        return sorted(potential_partners, key=lambda x: x['compatibility_score'], reverse=True)[:10]

# Initialize global social learning manager
social_manager = SocialLearningManager()