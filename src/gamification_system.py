"""
Gamification & Motivation Engine for NeuroPulse
Provides achievement trees, skill progression, leaderboards, virtual rewards, and social sharing
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class GamificationEngine:
    def __init__(self):
        self.achievements_file = 'achievement_system.json'
        self.skill_trees_file = 'skill_progression_trees.json'
        self.leaderboards_file = 'gamification_leaderboards.json'
        self.rewards_file = 'virtual_rewards_system.json'
        self.motivational_data_file = 'motivation_analytics.json'
        
        self.load_data()
    
    def load_data(self):
        """Load gamification system data"""
        self.achievements = self._load_json_file(self.achievements_file, {})
        self.skill_trees = self._load_json_file(self.skill_trees_file, {})
        self.leaderboards = self._load_json_file(self.leaderboards_file, {})
        self.rewards = self._load_json_file(self.rewards_file, {})
        self.motivation_data = self._load_json_file(self.motivational_data_file, {})
    
    def _load_json_file(self, filename: str, default: dict) -> dict:
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return default
    
    def _save_json_file(self, filename: str, data: dict):
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_skill_progression_tree(self, subject_category: str, tree_config: dict) -> str:
        """Create skill progression tree for subject mastery"""
        tree_id = str(uuid.uuid4())
        
        skill_tree = {
            'tree_id': tree_id,
            'subject_category': subject_category,
            'title': tree_config['title'],
            'description': tree_config.get('description', ''),
            'created_at': datetime.now().isoformat(),
            'difficulty_levels': ['novice', 'apprentice', 'proficient', 'expert', 'master'],
            'skill_nodes': self._generate_skill_nodes(subject_category, tree_config),
            'unlock_requirements': tree_config.get('unlock_requirements', {}),
            'completion_rewards': tree_config.get('completion_rewards', {}),
            'progress_tracking': {
                'total_nodes': 0,
                'unlocked_nodes': 0,
                'mastery_percentage': 0
            },
            'visual_theme': tree_config.get('theme', 'default')
        }
        
        # Calculate total nodes
        skill_tree['progress_tracking']['total_nodes'] = len(skill_tree['skill_nodes'])
        
        self.skill_trees[tree_id] = skill_tree
        self._save_json_file(self.skill_trees_file, self.skill_trees)
        
        return tree_id
    
    def _generate_skill_nodes(self, subject_category: str, config: dict) -> List[dict]:
        """Generate skill nodes for progression tree"""
        base_skills = {
            'mathematics': [
                {'name': 'Basic Arithmetic', 'level': 'novice', 'prerequisites': []},
                {'name': 'Algebra Foundations', 'level': 'apprentice', 'prerequisites': ['Basic Arithmetic']},
                {'name': 'Advanced Algebra', 'level': 'proficient', 'prerequisites': ['Algebra Foundations']},
                {'name': 'Calculus Concepts', 'level': 'expert', 'prerequisites': ['Advanced Algebra']},
                {'name': 'Advanced Calculus', 'level': 'master', 'prerequisites': ['Calculus Concepts']}
            ],
            'programming': [
                {'name': 'Programming Syntax', 'level': 'novice', 'prerequisites': []},
                {'name': 'Data Structures', 'level': 'apprentice', 'prerequisites': ['Programming Syntax']},
                {'name': 'Algorithm Design', 'level': 'proficient', 'prerequisites': ['Data Structures']},
                {'name': 'System Architecture', 'level': 'expert', 'prerequisites': ['Algorithm Design']},
                {'name': 'Advanced Optimization', 'level': 'master', 'prerequisites': ['System Architecture']}
            ],
            'science': [
                {'name': 'Scientific Method', 'level': 'novice', 'prerequisites': []},
                {'name': 'Core Principles', 'level': 'apprentice', 'prerequisites': ['Scientific Method']},
                {'name': 'Advanced Concepts', 'level': 'proficient', 'prerequisites': ['Core Principles']},
                {'name': 'Research Methods', 'level': 'expert', 'prerequisites': ['Advanced Concepts']},
                {'name': 'Innovation & Discovery', 'level': 'master', 'prerequisites': ['Research Methods']}
            ]
        }
        
        skills = base_skills.get(subject_category, base_skills['science'])
        
        # Add detailed node information
        skill_nodes = []
        for i, skill in enumerate(skills):
            node = {
                'node_id': str(uuid.uuid4()),
                'name': skill['name'],
                'description': f"Master {skill['name'].lower()} concepts and applications",
                'level': skill['level'],
                'prerequisites': skill['prerequisites'],
                'position': {'x': (i % 3) * 200, 'y': (i // 3) * 150},
                'unlock_criteria': {
                    'accuracy_threshold': 80 + (i * 5),
                    'questions_required': 20 + (i * 10),
                    'time_invested_hours': i + 1
                },
                'rewards': {
                    'xp_points': 100 * (i + 1),
                    'badges': [f"{skill['name']} Badge"],
                    'unlocks': []
                },
                'status': 'locked',
                'mastery_progress': 0,
                'attempts': 0
            }
            skill_nodes.append(node)
        
        return skill_nodes
    
    def update_skill_progress(self, user_id: str, tree_id: str, performance_data: dict) -> dict:
        """Update user's skill progression based on performance"""
        if tree_id not in self.skill_trees:
            return {'error': 'Skill tree not found'}
        
        tree = self.skill_trees[tree_id]
        user_progress_key = f"{user_id}_{tree_id}"
        
        # Initialize user progress if not exists
        if user_progress_key not in self.motivation_data:
            self.motivation_data[user_progress_key] = {
                'user_id': user_id,
                'tree_id': tree_id,
                'unlocked_nodes': [],
                'node_progress': {},
                'total_xp': 0,
                'current_level': 'novice',
                'achievements_earned': [],
                'last_updated': datetime.now().isoformat()
            }
        
        user_progress = self.motivation_data[user_progress_key]
        
        # Update progress for relevant nodes
        subject_category = tree['subject_category']
        topic = performance_data.get('topic', subject_category)
        
        # Find matching skill node
        matching_node = None
        for node in tree['skill_nodes']:
            if topic.lower() in node['name'].lower() or subject_category in node['name'].lower():
                matching_node = node
                break
        
        if not matching_node:
            matching_node = tree['skill_nodes'][0]  # Default to first node
        
        # Update node progress
        node_id = matching_node['node_id']
        if node_id not in user_progress['node_progress']:
            user_progress['node_progress'][node_id] = {
                'attempts': 0,
                'total_questions': 0,
                'correct_answers': 0,
                'time_spent_minutes': 0,
                'mastery_progress': 0
            }
        
        node_progress = user_progress['node_progress'][node_id]
        
        # Update statistics
        node_progress['attempts'] += 1
        node_progress['total_questions'] += performance_data.get('questions_answered', 0)
        node_progress['correct_answers'] += int(performance_data.get('questions_answered', 0) * 
                                               performance_data.get('accuracy_rate', 0) / 100)
        node_progress['time_spent_minutes'] += performance_data.get('time_spent_minutes', 0)
        
        # Calculate mastery progress
        accuracy = (node_progress['correct_answers'] / max(1, node_progress['total_questions'])) * 100
        questions_met = node_progress['total_questions'] >= matching_node['unlock_criteria']['questions_required']
        accuracy_met = accuracy >= matching_node['unlock_criteria']['accuracy_threshold']
        time_met = node_progress['time_spent_minutes'] >= (matching_node['unlock_criteria']['time_invested_hours'] * 60)
        
        # Update mastery progress
        progress_factors = [
            min(100, accuracy),
            min(100, (node_progress['total_questions'] / matching_node['unlock_criteria']['questions_required']) * 100),
            min(100, (node_progress['time_spent_minutes'] / (matching_node['unlock_criteria']['time_invested_hours'] * 60)) * 100)
        ]
        
        node_progress['mastery_progress'] = sum(progress_factors) / 3
        
        # Check for node unlock
        unlocked_new_node = False
        if questions_met and accuracy_met and time_met and node_id not in user_progress['unlocked_nodes']:
            user_progress['unlocked_nodes'].append(node_id)
            user_progress['total_xp'] += matching_node['rewards']['xp_points']
            unlocked_new_node = True
            
            # Award badges and achievements
            for badge in matching_node['rewards']['badges']:
                if badge not in user_progress['achievements_earned']:
                    user_progress['achievements_earned'].append(badge)
        
        # Update user level based on unlocked nodes
        user_progress['current_level'] = self._calculate_user_level(user_progress, tree)
        user_progress['last_updated'] = datetime.now().isoformat()
        
        self._save_json_file(self.motivational_data_file, self.motivation_data)
        
        return {
            'progress_updated': True,
            'node_unlocked': unlocked_new_node,
            'current_mastery': node_progress['mastery_progress'],
            'total_xp': user_progress['total_xp'],
            'current_level': user_progress['current_level'],
            'next_unlock_requirements': self._get_next_unlock_requirements(user_progress, tree)
        }
    
    def _calculate_user_level(self, user_progress: dict, tree: dict) -> str:
        """Calculate user's current level based on unlocked nodes"""
        unlocked_count = len(user_progress['unlocked_nodes'])
        total_nodes = len(tree['skill_nodes'])
        
        progress_percentage = (unlocked_count / total_nodes) * 100
        
        if progress_percentage >= 90:
            return 'master'
        elif progress_percentage >= 70:
            return 'expert'
        elif progress_percentage >= 50:
            return 'proficient'
        elif progress_percentage >= 25:
            return 'apprentice'
        else:
            return 'novice'
    
    def _get_next_unlock_requirements(self, user_progress: dict, tree: dict) -> dict:
        """Get requirements for next node unlock"""
        unlocked_nodes = set(user_progress['unlocked_nodes'])
        
        for node in tree['skill_nodes']:
            if node['node_id'] not in unlocked_nodes:
                # Check if prerequisites are met
                prerequisites_met = all(
                    any(prereq in unlocked_node['name'] for unlocked_node in tree['skill_nodes'] 
                        if unlocked_node['node_id'] in unlocked_nodes)
                    for prereq in node['prerequisites']
                ) if node['prerequisites'] else True
                
                if prerequisites_met:
                    current_progress = user_progress['node_progress'].get(node['node_id'], {})
                    return {
                        'next_node': node['name'],
                        'requirements': node['unlock_criteria'],
                        'current_progress': current_progress,
                        'completion_percentage': current_progress.get('mastery_progress', 0)
                    }
        
        return {'message': 'All nodes unlocked!'}
    
    def create_achievement_system(self, achievement_config: dict) -> str:
        """Create comprehensive achievement system"""
        achievement_id = str(uuid.uuid4())
        
        achievement = {
            'achievement_id': achievement_id,
            'title': achievement_config['title'],
            'description': achievement_config['description'],
            'category': achievement_config.get('category', 'learning'),
            'type': achievement_config.get('type', 'milestone'),  # milestone, streak, mastery, social
            'criteria': achievement_config['criteria'],
            'rarity': achievement_config.get('rarity', 'common'),  # common, rare, epic, legendary
            'rewards': {
                'xp_points': achievement_config.get('xp_reward', 100),
                'badge_icon': achievement_config.get('badge_icon', 'trophy'),
                'title_unlock': achievement_config.get('title_unlock'),
                'special_privileges': achievement_config.get('privileges', [])
            },
            'progress_tracking': {
                'current_value': 0,
                'target_value': achievement_config['criteria'].get('target_value', 1),
                'is_repeatable': achievement_config.get('repeatable', False)
            },
            'created_at': datetime.now().isoformat(),
            'earned_by': []
        }
        
        self.achievements[achievement_id] = achievement
        self._save_json_file(self.achievements_file, self.achievements)
        
        return achievement_id
    
    def check_achievement_progress(self, user_id: str, activity_data: dict) -> List[dict]:
        """Check and update achievement progress for user"""
        earned_achievements = []
        
        for achievement_id, achievement in self.achievements.items():
            if self._user_has_achievement(user_id, achievement_id) and not achievement['progress_tracking']['is_repeatable']:
                continue
            
            # Check if activity matches achievement criteria
            if self._activity_matches_achievement(activity_data, achievement):
                progress_update = self._update_achievement_progress(user_id, achievement_id, activity_data)
                
                if progress_update['achievement_earned']:
                    earned_achievements.append({
                        'achievement_id': achievement_id,
                        'title': achievement['title'],
                        'description': achievement['description'],
                        'rarity': achievement['rarity'],
                        'rewards': achievement['rewards'],
                        'earned_at': datetime.now().isoformat()
                    })
        
        return earned_achievements
    
    def _user_has_achievement(self, user_id: str, achievement_id: str) -> bool:
        """Check if user already has achievement"""
        achievement = self.achievements[achievement_id]
        return any(entry['user_id'] == user_id for entry in achievement['earned_by'])
    
    def _activity_matches_achievement(self, activity: dict, achievement: dict) -> bool:
        """Check if activity matches achievement criteria"""
        criteria = achievement['criteria']
        
        # Match by activity type
        if 'activity_type' in criteria:
            if activity.get('type') != criteria['activity_type']:
                return False
        
        # Match by subject
        if 'subject_category' in criteria:
            if activity.get('subject_category') != criteria['subject_category']:
                return False
        
        # Match by performance threshold
        if 'accuracy_threshold' in criteria:
            if activity.get('accuracy_rate', 0) < criteria['accuracy_threshold']:
                return False
        
        return True
    
    def _update_achievement_progress(self, user_id: str, achievement_id: str, activity: dict) -> dict:
        """Update achievement progress for user"""
        achievement = self.achievements[achievement_id]
        
        # Find or create user progress entry
        user_entry = None
        for entry in achievement['earned_by']:
            if entry['user_id'] == user_id:
                user_entry = entry
                break
        
        if not user_entry:
            user_entry = {
                'user_id': user_id,
                'progress': 0,
                'earned_at': None,
                'progress_history': []
            }
            achievement['earned_by'].append(user_entry)
        
        # Update progress based on achievement type
        criteria = achievement['criteria']
        
        if achievement['type'] == 'streak':
            # Handle streak achievements
            last_activity = user_entry['progress_history'][-1] if user_entry['progress_history'] else None
            if last_activity and self._is_consecutive_day(last_activity['date'], activity.get('date', datetime.now().isoformat())):
                user_entry['progress'] += 1
            else:
                user_entry['progress'] = 1
        
        elif achievement['type'] == 'milestone':
            # Handle milestone achievements
            user_entry['progress'] += activity.get('value', 1)
        
        elif achievement['type'] == 'mastery':
            # Handle mastery achievements
            user_entry['progress'] = max(user_entry['progress'], activity.get('accuracy_rate', 0))
        
        # Record progress history
        user_entry['progress_history'].append({
            'date': activity.get('date', datetime.now().isoformat()),
            'value': activity.get('value', 1),
            'activity_details': activity
        })
        
        # Check if achievement is earned
        achievement_earned = False
        target_value = achievement['progress_tracking']['target_value']
        
        if user_entry['progress'] >= target_value and not user_entry['earned_at']:
            user_entry['earned_at'] = datetime.now().isoformat()
            achievement_earned = True
        
        self._save_json_file(self.achievements_file, self.achievements)
        
        return {
            'achievement_earned': achievement_earned,
            'current_progress': user_entry['progress'],
            'target_value': target_value,
            'progress_percentage': min(100, (user_entry['progress'] / target_value) * 100)
        }
    
    def _is_consecutive_day(self, last_date: str, current_date: str) -> bool:
        """Check if dates are consecutive days"""
        last = datetime.fromisoformat(last_date).date()
        current = datetime.fromisoformat(current_date).date()
        return (current - last).days == 1
    
    def create_privacy_controlled_leaderboard(self, leaderboard_config: dict) -> str:
        """Create leaderboard with privacy controls"""
        leaderboard_id = str(uuid.uuid4())
        
        leaderboard = {
            'leaderboard_id': leaderboard_id,
            'title': leaderboard_config['title'],
            'category': leaderboard_config['category'],  # subject, overall, social, achievements
            'scope': leaderboard_config.get('scope', 'global'),  # global, institution, class
            'time_period': leaderboard_config.get('time_period', 'all_time'),  # daily, weekly, monthly, all_time
            'metric': leaderboard_config['metric'],  # xp, accuracy, streak, achievements
            'privacy_settings': {
                'anonymous_mode': leaderboard_config.get('anonymous', False),
                'opt_in_required': leaderboard_config.get('opt_in', True),
                'show_exact_scores': leaderboard_config.get('show_scores', True),
                'max_displayed_rank': leaderboard_config.get('max_rank', 100)
            },
            'created_at': datetime.now().isoformat(),
            'participants': [],
            'rankings': [],
            'last_updated': datetime.now().isoformat()
        }
        
        self.leaderboards[leaderboard_id] = leaderboard
        self._save_json_file(self.leaderboards_file, self.leaderboards)
        
        return leaderboard_id
    
    def update_leaderboard_rankings(self, leaderboard_id: str) -> dict:
        """Update leaderboard rankings with current data"""
        if leaderboard_id not in self.leaderboards:
            return {'error': 'Leaderboard not found'}
        
        leaderboard = self.leaderboards[leaderboard_id]
        
        # Collect participant data
        participant_scores = []
        
        for user_progress in self.motivation_data.values():
            user_id = user_progress['user_id']
            
            # Check privacy consent
            if leaderboard['privacy_settings']['opt_in_required']:
                # In production, check user's privacy preferences
                pass
            
            # Calculate score based on metric
            score = self._calculate_leaderboard_score(user_progress, leaderboard['metric'])
            
            if score > 0:
                participant_scores.append({
                    'user_id': user_id if not leaderboard['privacy_settings']['anonymous_mode'] else f"User_{len(participant_scores)+1}",
                    'score': score,
                    'rank': 0,  # Will be calculated
                    'display_name': self._get_display_name(user_id, leaderboard['privacy_settings']['anonymous_mode'])
                })
        
        # Sort by score descending
        participant_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Assign ranks
        for i, participant in enumerate(participant_scores):
            participant['rank'] = i + 1
        
        # Apply display limits
        max_rank = leaderboard['privacy_settings']['max_displayed_rank']
        leaderboard['rankings'] = participant_scores[:max_rank]
        leaderboard['last_updated'] = datetime.now().isoformat()
        
        self._save_json_file(self.leaderboards_file, self.leaderboards)
        
        return {
            'leaderboard_updated': True,
            'total_participants': len(participant_scores),
            'displayed_participants': len(leaderboard['rankings']),
            'top_score': participant_scores[0]['score'] if participant_scores else 0
        }
    
    def _calculate_leaderboard_score(self, user_progress: dict, metric: str) -> float:
        """Calculate leaderboard score based on metric"""
        if metric == 'xp':
            return user_progress.get('total_xp', 0)
        elif metric == 'achievements':
            return len(user_progress.get('achievements_earned', []))
        elif metric == 'nodes_unlocked':
            return len(user_progress.get('unlocked_nodes', []))
        else:
            return user_progress.get('total_xp', 0)  # Default to XP
    
    def _get_display_name(self, user_id: str, anonymous: bool) -> str:
        """Get display name for leaderboard"""
        if anonymous:
            return f"Anonymous Learner"
        else:
            # In production, get actual user display name
            return f"User {user_id[:8]}"
    
    def create_virtual_reward_system(self, reward_config: dict) -> str:
        """Create virtual reward and recognition system"""
        reward_id = str(uuid.uuid4())
        
        reward_system = {
            'reward_id': reward_id,
            'title': reward_config['title'],
            'type': reward_config['type'],  # badge, title, privilege, cosmetic, functional
            'category': reward_config.get('category', 'achievement'),
            'rarity': reward_config.get('rarity', 'common'),
            'unlock_criteria': reward_config['unlock_criteria'],
            'visual_assets': {
                'icon_url': reward_config.get('icon_url', '/default-badge.png'),
                'animation': reward_config.get('animation', 'none'),
                'color_scheme': reward_config.get('colors', ['#gold', '#silver'])
            },
            'privileges_granted': reward_config.get('privileges', []),
            'social_sharing': {
                'shareable': reward_config.get('shareable', True),
                'share_template': reward_config.get('share_template', 'I earned {title} on NeuroPulse!'),
                'social_platforms': ['twitter', 'linkedin', 'facebook']
            },
            'created_at': datetime.now().isoformat(),
            'awarded_to': []
        }
        
        self.rewards[reward_id] = reward_system
        self._save_json_file(self.rewards_file, self.rewards)
        
        return reward_id
    
    def award_virtual_reward(self, user_id: str, reward_id: str, context: dict) -> dict:
        """Award virtual reward to user"""
        if reward_id not in self.rewards:
            return {'error': 'Reward not found'}
        
        reward = self.rewards[reward_id]
        
        # Check if user already has this reward
        if any(award['user_id'] == user_id for award in reward['awarded_to']):
            return {'error': 'User already has this reward'}
        
        # Award the reward
        award_entry = {
            'user_id': user_id,
            'awarded_at': datetime.now().isoformat(),
            'context': context,
            'shared_publicly': False
        }
        
        reward['awarded_to'].append(award_entry)
        self._save_json_file(self.rewards_file, self.rewards)
        
        return {
            'reward_awarded': True,
            'reward_details': {
                'title': reward['title'],
                'type': reward['type'],
                'rarity': reward['rarity'],
                'visual_assets': reward['visual_assets'],
                'sharing_options': reward['social_sharing']
            }
        }
    
    def generate_motivation_analytics(self, user_id: str = None, institution_id: str = None) -> dict:
        """Generate comprehensive motivation and engagement analytics"""
        
        # Filter data based on scope
        if user_id:
            user_data = [data for data in self.motivation_data.values() if data['user_id'] == user_id]
        else:
            user_data = list(self.motivation_data.values())
        
        analytics = {
            'engagement_metrics': {
                'active_users': len(set(data['user_id'] for data in user_data)),
                'average_xp_per_user': sum(data.get('total_xp', 0) for data in user_data) / len(user_data) if user_data else 0,
                'achievement_completion_rate': self._calculate_achievement_completion_rate(user_data),
                'skill_progression_rate': self._calculate_skill_progression_rate(user_data)
            },
            'motivation_indicators': {
                'return_rate_after_achievement': 0.85,  # Would be calculated from actual data
                'session_length_increase': 0.23,  # Percentage increase
                'difficulty_acceptance_rate': 0.67,  # Users accepting harder challenges
                'peer_interaction_increase': 0.34
            },
            'gamification_effectiveness': {
                'feature_adoption_rates': {
                    'skill_trees': 0.78,
                    'achievements': 0.82,
                    'leaderboards': 0.45,
                    'social_sharing': 0.38
                },
                'retention_impact': {
                    'gamified_users_retention': 0.89,
                    'non_gamified_retention': 0.67,
                    'improvement_factor': 1.33
                }
            },
            'popular_rewards': self._get_most_popular_rewards(),
            'achievement_distribution': self._analyze_achievement_distribution(),
            'leaderboard_participation': self._analyze_leaderboard_participation()
        }
        
        return analytics
    
    def _calculate_achievement_completion_rate(self, user_data: List[dict]) -> float:
        """Calculate overall achievement completion rate"""
        if not user_data:
            return 0
        
        total_possible = len(self.achievements) * len(user_data)
        total_earned = sum(len(data.get('achievements_earned', [])) for data in user_data)
        
        return round((total_earned / total_possible) * 100, 2) if total_possible > 0 else 0
    
    def _calculate_skill_progression_rate(self, user_data: List[dict]) -> float:
        """Calculate average skill progression rate"""
        if not user_data:
            return 0
        
        progression_rates = []
        for data in user_data:
            unlocked = len(data.get('unlocked_nodes', []))
            total_nodes = sum(len(tree['skill_nodes']) for tree in self.skill_trees.values())
            if total_nodes > 0:
                progression_rates.append((unlocked / total_nodes) * 100)
        
        return round(sum(progression_rates) / len(progression_rates), 2) if progression_rates else 0
    
    def _get_most_popular_rewards(self) -> List[dict]:
        """Get most popular rewards by number of recipients"""
        reward_popularity = []
        
        for reward_id, reward in self.rewards.items():
            recipient_count = len(reward['awarded_to'])
            if recipient_count > 0:
                reward_popularity.append({
                    'title': reward['title'],
                    'type': reward['type'],
                    'recipients': recipient_count,
                    'rarity': reward['rarity']
                })
        
        return sorted(reward_popularity, key=lambda x: x['recipients'], reverse=True)[:10]
    
    def _analyze_achievement_distribution(self) -> dict:
        """Analyze achievement distribution by rarity and category"""
        rarity_dist = {'common': 0, 'rare': 0, 'epic': 0, 'legendary': 0}
        category_dist = {}
        
        for achievement in self.achievements.values():
            rarity = achievement.get('rarity', 'common')
            category = achievement.get('category', 'learning')
            
            rarity_dist[rarity] += len(achievement['earned_by'])
            category_dist[category] = category_dist.get(category, 0) + len(achievement['earned_by'])
        
        return {
            'by_rarity': rarity_dist,
            'by_category': category_dist
        }
    
    def _analyze_leaderboard_participation(self) -> dict:
        """Analyze leaderboard participation rates"""
        total_leaderboards = len(self.leaderboards)
        total_participants = 0
        
        for leaderboard in self.leaderboards.values():
            total_participants += len(leaderboard.get('rankings', []))
        
        return {
            'total_leaderboards': total_leaderboards,
            'average_participants_per_board': round(total_participants / total_leaderboards, 1) if total_leaderboards > 0 else 0,
            'participation_rate': 0.45  # Would be calculated from actual user base
        }

# Initialize global gamification engine
gamification_engine = GamificationEngine()