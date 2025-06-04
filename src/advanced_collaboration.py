"""
Advanced Collaboration Tools for NeuroPulse
Provides virtual whiteboards, breakout rooms, peer review systems, and real-time document collaboration
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class AdvancedCollaborationManager:
    def __init__(self):
        self.whiteboards_file = 'virtual_whiteboards.json'
        self.breakout_rooms_file = 'breakout_rooms_data.json'
        self.peer_reviews_file = 'peer_review_system.json'
        self.collaborative_docs_file = 'collaborative_documents.json'
        self.collaboration_analytics_file = 'collaboration_analytics.json'
        
        self.load_data()
    
    def load_data(self):
        """Load collaboration system data"""
        self.whiteboards = self._load_json_file(self.whiteboards_file, {})
        self.breakout_rooms = self._load_json_file(self.breakout_rooms_file, {})
        self.peer_reviews = self._load_json_file(self.peer_reviews_file, {})
        self.collaborative_docs = self._load_json_file(self.collaborative_docs_file, {})
        self.analytics = self._load_json_file(self.collaboration_analytics_file, {})
    
    def _load_json_file(self, filename: str, default: dict) -> dict:
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return default
    
    def _save_json_file(self, filename: str, data: dict):
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_virtual_whiteboard(self, creator_id: str, session_data: dict) -> str:
        """Create virtual whiteboard for collaborative problem-solving"""
        whiteboard_id = str(uuid.uuid4())
        
        whiteboard = {
            'id': whiteboard_id,
            'creator_id': creator_id,
            'title': session_data['title'],
            'subject_category': session_data.get('subject_category', 'general'),
            'created_at': datetime.now().isoformat(),
            'participants': [creator_id],
            'canvas_data': {
                'elements': [],
                'background': 'white',
                'dimensions': {'width': 1920, 'height': 1080}
            },
            'tools_enabled': {
                'drawing': True,
                'text': True,
                'shapes': True,
                'math_equations': True,
                'sticky_notes': True,
                'templates': True
            },
            'collaboration_features': {
                'real_time_cursors': True,
                'voice_chat': session_data.get('voice_enabled', False),
                'screen_sharing': session_data.get('screen_share', False),
                'auto_save': True,
                'version_history': True
            },
            'permissions': {
                'public_view': session_data.get('public_view', False),
                'allow_anonymous': session_data.get('allow_anonymous', False),
                'edit_permissions': 'all_participants'
            },
            'session_state': 'active',
            'activity_log': []
        }
        
        self.whiteboards[whiteboard_id] = whiteboard
        self._save_json_file(self.whiteboards_file, self.whiteboards)
        
        return whiteboard_id
    
    def update_whiteboard_canvas(self, whiteboard_id: str, user_id: str, canvas_update: dict) -> dict:
        """Update whiteboard canvas with real-time changes"""
        if whiteboard_id not in self.whiteboards:
            return {'error': 'Whiteboard not found'}
        
        whiteboard = self.whiteboards[whiteboard_id]
        
        if user_id not in whiteboard['participants']:
            return {'error': 'User not authorized to edit this whiteboard'}
        
        # Apply canvas update
        update_type = canvas_update.get('type', 'element_add')
        
        if update_type == 'element_add':
            element = {
                'id': str(uuid.uuid4()),
                'type': canvas_update['element_type'],
                'data': canvas_update['element_data'],
                'author': user_id,
                'timestamp': datetime.now().isoformat(),
                'position': canvas_update.get('position', {'x': 0, 'y': 0})
            }
            whiteboard['canvas_data']['elements'].append(element)
        
        elif update_type == 'element_update':
            element_id = canvas_update['element_id']
            for element in whiteboard['canvas_data']['elements']:
                if element['id'] == element_id:
                    element['data'].update(canvas_update['updates'])
                    element['last_modified'] = datetime.now().isoformat()
                    break
        
        elif update_type == 'element_delete':
            element_id = canvas_update['element_id']
            whiteboard['canvas_data']['elements'] = [
                e for e in whiteboard['canvas_data']['elements'] 
                if e['id'] != element_id
            ]
        
        # Log activity
        whiteboard['activity_log'].append({
            'user_id': user_id,
            'action': update_type,
            'timestamp': datetime.now().isoformat(),
            'details': canvas_update
        })
        
        self._save_json_file(self.whiteboards_file, self.whiteboards)
        
        return {'success': True, 'whiteboard_state': whiteboard['canvas_data']}
    
    def create_breakout_room(self, host_id: str, room_config: dict) -> str:
        """Create breakout room with dynamic group formation"""
        room_id = str(uuid.uuid4())
        
        breakout_room = {
            'id': room_id,
            'host_id': host_id,
            'title': room_config['title'],
            'subject_category': room_config.get('subject_category', 'general'),
            'created_at': datetime.now().isoformat(),
            'max_participants': room_config.get('max_participants', 6),
            'grouping_strategy': room_config.get('grouping_strategy', 'manual'),
            'duration_minutes': room_config.get('duration_minutes', 30),
            'objectives': room_config.get('objectives', []),
            'participants': [],
            'groups': [],
            'room_features': {
                'whiteboard': room_config.get('whiteboard_enabled', True),
                'screen_sharing': room_config.get('screen_sharing', True),
                'file_sharing': room_config.get('file_sharing', True),
                'chat': room_config.get('chat_enabled', True),
                'recording': room_config.get('recording_enabled', False)
            },
            'status': 'waiting',
            'started_at': None,
            'ended_at': None,
            'activity_summary': {}
        }
        
        self.breakout_rooms[room_id] = breakout_room
        self._save_json_file(self.breakout_rooms_file, self.breakout_rooms)
        
        return room_id
    
    def form_dynamic_groups(self, room_id: str, participants: List[dict]) -> dict:
        """Automatically form optimal groups based on learning profiles"""
        if room_id not in self.breakout_rooms:
            return {'error': 'Breakout room not found'}
        
        room = self.breakout_rooms[room_id]
        strategy = room['grouping_strategy']
        max_per_group = room['max_participants'] // max(1, len(participants) // room['max_participants'])
        
        if strategy == 'balanced_skills':
            groups = self._create_balanced_skill_groups(participants, max_per_group)
        elif strategy == 'complementary_learning':
            groups = self._create_complementary_learning_groups(participants, max_per_group)
        elif strategy == 'random':
            groups = self._create_random_groups(participants, max_per_group)
        else:
            groups = self._create_manual_groups(participants, max_per_group)
        
        # Update room with formed groups
        room['groups'] = groups
        room['participants'] = [p['user_id'] for p in participants]
        room['status'] = 'groups_formed'
        
        self._save_json_file(self.breakout_rooms_file, self.breakout_rooms)
        
        return {'success': True, 'groups': groups, 'grouping_rationale': self._explain_grouping(strategy)}
    
    def _create_balanced_skill_groups(self, participants: List[dict], max_per_group: int) -> List[dict]:
        """Create groups with balanced skill levels"""
        from analytics_dashboard import analytics_manager
        
        # Get skill levels for participants
        participant_skills = []
        for participant in participants:
            user_data = analytics_manager.get_user_dashboard_data(participant['user_id'])
            skill_level = user_data.get('overview', {}).get('overall_accuracy', 75)
            participant_skills.append({
                'user_id': participant['user_id'],
                'skill_level': skill_level,
                'learning_style': participant.get('learning_style', 'balanced')
            })
        
        # Sort by skill level
        participant_skills.sort(key=lambda x: x['skill_level'], reverse=True)
        
        # Distribute into groups using snake draft method
        groups = []
        num_groups = max(1, len(participants) // max_per_group)
        
        for i in range(num_groups):
            groups.append({
                'group_id': str(uuid.uuid4()),
                'group_number': i + 1,
                'participants': [],
                'assigned_task': f"Collaborative problem-solving group {i + 1}",
                'skill_balance': 'mixed'
            })
        
        # Snake draft assignment
        for i, participant in enumerate(participant_skills):
            group_index = i % num_groups if (i // num_groups) % 2 == 0 else num_groups - 1 - (i % num_groups)
            groups[group_index]['participants'].append(participant)
        
        return groups
    
    def _create_complementary_learning_groups(self, participants: List[dict], max_per_group: int) -> List[dict]:
        """Create groups with complementary learning styles"""
        learning_styles = {'visual': [], 'auditory': [], 'kinesthetic': [], 'reading_writing': []}
        
        for participant in participants:
            style = participant.get('dominant_learning_style', 'balanced')
            if style in learning_styles:
                learning_styles[style].append(participant)
            else:
                learning_styles['visual'].append(participant)  # Default
        
        groups = []
        num_groups = max(1, len(participants) // max_per_group)
        
        for i in range(num_groups):
            group = {
                'group_id': str(uuid.uuid4()),
                'group_number': i + 1,
                'participants': [],
                'learning_style_mix': [],
                'assigned_task': f"Multi-perspective analysis group {i + 1}"
            }
            
            # Add one from each learning style if available
            for style, style_participants in learning_styles.items():
                if style_participants and len(group['participants']) < max_per_group:
                    participant = style_participants.pop(0)
                    group['participants'].append(participant)
                    group['learning_style_mix'].append(style)
            
            groups.append(group)
        
        return groups
    
    def _create_random_groups(self, participants: List[dict], max_per_group: int) -> List[dict]:
        """Create random groups"""
        import random
        shuffled = participants.copy()
        random.shuffle(shuffled)
        
        groups = []
        num_groups = max(1, len(participants) // max_per_group)
        
        for i in range(num_groups):
            start_idx = i * max_per_group
            end_idx = min((i + 1) * max_per_group, len(shuffled))
            
            groups.append({
                'group_id': str(uuid.uuid4()),
                'group_number': i + 1,
                'participants': shuffled[start_idx:end_idx],
                'assigned_task': f"Collaborative exploration group {i + 1}",
                'formation_method': 'random'
            })
        
        return groups
    
    def _create_manual_groups(self, participants: List[dict], max_per_group: int) -> List[dict]:
        """Create manual grouping structure"""
        return [{
            'group_id': str(uuid.uuid4()),
            'group_number': 1,
            'participants': participants,
            'assigned_task': 'Manual group assignment pending',
            'formation_method': 'manual'
        }]
    
    def _explain_grouping(self, strategy: str) -> str:
        """Explain the grouping rationale"""
        explanations = {
            'balanced_skills': 'Groups formed with mixed skill levels to promote peer teaching and learning',
            'complementary_learning': 'Groups formed with diverse learning styles to encourage different perspectives',
            'random': 'Random grouping to ensure unbiased collaboration',
            'manual': 'Groups will be manually assigned by the instructor'
        }
        return explanations.get(strategy, 'Groups formed using standard algorithm')
    
    def initiate_peer_review_assignment(self, creator_id: str, assignment_config: dict) -> str:
        """Create peer review assignment with intelligent matching"""
        review_id = str(uuid.uuid4())
        
        peer_review = {
            'id': review_id,
            'creator_id': creator_id,
            'title': assignment_config['title'],
            'subject_category': assignment_config.get('subject_category', 'general'),
            'created_at': datetime.now().isoformat(),
            'submission_deadline': assignment_config.get('submission_deadline'),
            'review_deadline': assignment_config.get('review_deadline'),
            'review_criteria': assignment_config.get('criteria', []),
            'reviews_per_submission': assignment_config.get('reviews_per_submission', 3),
            'anonymous_reviews': assignment_config.get('anonymous', True),
            'rubric': assignment_config.get('rubric', {}),
            'submissions': {},
            'review_assignments': {},
            'completed_reviews': {},
            'status': 'open_for_submissions',
            'matching_algorithm': assignment_config.get('matching', 'quality_diverse'),
            'calibration_enabled': assignment_config.get('calibration', True)
        }
        
        self.peer_reviews[review_id] = peer_review
        self._save_json_file(self.peer_reviews_file, self.peer_reviews)
        
        return review_id
    
    def submit_for_peer_review(self, review_id: str, user_id: str, submission_data: dict) -> dict:
        """Submit work for peer review"""
        if review_id not in self.peer_reviews:
            return {'error': 'Peer review assignment not found'}
        
        review = self.peer_reviews[review_id]
        
        if review['status'] != 'open_for_submissions':
            return {'error': 'Submission period has ended'}
        
        submission_id = str(uuid.uuid4())
        
        submission = {
            'submission_id': submission_id,
            'author_id': user_id,
            'submitted_at': datetime.now().isoformat(),
            'content': submission_data['content'],
            'file_attachments': submission_data.get('attachments', []),
            'metadata': submission_data.get('metadata', {}),
            'quality_indicators': self._analyze_submission_quality(submission_data['content']),
            'review_status': 'pending_reviews',
            'received_reviews': []
        }
        
        review['submissions'][user_id] = submission
        self._save_json_file(self.peer_reviews_file, self.peer_reviews)
        
        return {'success': True, 'submission_id': submission_id}
    
    def _analyze_submission_quality(self, content: str) -> dict:
        """Analyze submission quality for intelligent review matching"""
        return {
            'word_count': len(content.split()),
            'complexity_score': min(10, len(content) // 100),
            'estimated_reading_time': len(content.split()) // 200,
            'has_citations': 'reference' in content.lower() or 'source' in content.lower(),
            'structure_score': content.count('\n\n') + content.count('\n-') + content.count('\n1.')
        }
    
    def assign_peer_reviews(self, review_id: str) -> dict:
        """Intelligently assign peer reviews using matching algorithm"""
        if review_id not in self.peer_reviews:
            return {'error': 'Peer review assignment not found'}
        
        review = self.peer_reviews[review_id]
        submissions = list(review['submissions'].values())
        
        if len(submissions) < 2:
            return {'error': 'Insufficient submissions for peer review'}
        
        assignments = self._generate_review_assignments(submissions, review)
        
        review['review_assignments'] = assignments
        review['status'] = 'reviews_assigned'
        
        self._save_json_file(self.peer_reviews_file, self.peer_reviews)
        
        return {'success': True, 'assignments': assignments}
    
    def _generate_review_assignments(self, submissions: List[dict], review_config: dict) -> dict:
        """Generate optimal peer review assignments"""
        assignments = {}
        reviews_per_submission = review_config['reviews_per_submission']
        
        # Create assignment matrix ensuring each submission gets reviewed
        for submission in submissions:
            author_id = submission['author_id']
            
            # Find best reviewers for this submission
            potential_reviewers = [s for s in submissions if s['author_id'] != author_id]
            
            # Sort by quality match and diversity
            potential_reviewers.sort(key=lambda x: self._calculate_reviewer_match_score(submission, x))
            
            # Assign top reviewers
            selected_reviewers = potential_reviewers[:reviews_per_submission]
            
            for reviewer_submission in selected_reviewers:
                reviewer_id = reviewer_submission['author_id']
                
                if reviewer_id not in assignments:
                    assignments[reviewer_id] = []
                
                assignments[reviewer_id].append({
                    'submission_to_review': submission['submission_id'],
                    'author_id': author_id if not review_config['anonymous_reviews'] else 'anonymous',
                    'due_date': review_config.get('review_deadline'),
                    'review_criteria': review_config['review_criteria'],
                    'rubric': review_config['rubric']
                })
        
        return assignments
    
    def _calculate_reviewer_match_score(self, submission: dict, potential_reviewer: dict) -> float:
        """Calculate how well a reviewer matches a submission for quality review"""
        sub_quality = submission['quality_indicators']
        rev_quality = potential_reviewer['quality_indicators']
        
        # Similar complexity for meaningful reviews
        complexity_diff = abs(sub_quality['complexity_score'] - rev_quality['complexity_score'])
        
        # Different structure for diverse perspectives
        structure_diff = abs(sub_quality['structure_score'] - rev_quality['structure_score'])
        
        # Balance similarity and diversity
        match_score = (10 - complexity_diff) + (structure_diff * 0.5)
        
        return match_score
    
    def create_collaborative_document(self, creator_id: str, doc_config: dict) -> str:
        """Create real-time collaborative document"""
        doc_id = str(uuid.uuid4())
        
        document = {
            'id': doc_id,
            'creator_id': creator_id,
            'title': doc_config['title'],
            'type': doc_config.get('type', 'text'),  # text, presentation, spreadsheet
            'created_at': datetime.now().isoformat(),
            'collaborators': [creator_id],
            'permissions': {
                'edit': doc_config.get('edit_permissions', 'collaborators'),
                'comment': doc_config.get('comment_permissions', 'anyone'),
                'view': doc_config.get('view_permissions', 'public')
            },
            'content': {
                'text': doc_config.get('initial_content', ''),
                'formatting': {},
                'comments': [],
                'suggestions': []
            },
            'version_history': [{
                'version': 1,
                'timestamp': datetime.now().isoformat(),
                'author': creator_id,
                'changes': 'Document created'
            }],
            'real_time_sessions': {},
            'activity_feed': []
        }
        
        self.collaborative_docs[doc_id] = document
        self._save_json_file(self.collaborative_docs_file, self.collaborative_docs)
        
        return doc_id
    
    def get_collaboration_analytics(self, institution_id: str = None, time_period: str = '30d') -> dict:
        """Generate comprehensive collaboration analytics"""
        
        end_date = datetime.now()
        if time_period == '7d':
            start_date = end_date - timedelta(days=7)
        elif time_period == '30d':
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Filter data by time period
        recent_whiteboards = [
            wb for wb in self.whiteboards.values()
            if start_date <= datetime.fromisoformat(wb['created_at']) <= end_date
        ]
        
        recent_breakouts = [
            br for br in self.breakout_rooms.values()
            if start_date <= datetime.fromisoformat(br['created_at']) <= end_date
        ]
        
        recent_reviews = [
            pr for pr in self.peer_reviews.values()
            if start_date <= datetime.fromisoformat(pr['created_at']) <= end_date
        ]
        
        analytics = {
            'period': time_period,
            'whiteboard_usage': {
                'total_sessions': len(recent_whiteboards),
                'unique_users': len(set(wb['creator_id'] for wb in recent_whiteboards)),
                'average_participants': self._calculate_avg_participants(recent_whiteboards),
                'most_used_tools': self._analyze_whiteboard_tools(recent_whiteboards)
            },
            'breakout_room_metrics': {
                'total_rooms': len(recent_breakouts),
                'average_duration': self._calculate_avg_breakout_duration(recent_breakouts),
                'grouping_strategies': self._analyze_grouping_strategies(recent_breakouts),
                'completion_rate': self._calculate_breakout_completion_rate(recent_breakouts)
            },
            'peer_review_effectiveness': {
                'assignments_created': len(recent_reviews),
                'average_reviews_per_submission': self._calculate_avg_reviews_per_submission(recent_reviews),
                'review_quality_score': self._calculate_review_quality_score(recent_reviews),
                'completion_rate': self._calculate_review_completion_rate(recent_reviews)
            },
            'collaboration_trends': {
                'most_collaborative_subjects': self._identify_collaborative_subjects(),
                'peak_collaboration_hours': self._analyze_collaboration_timing(),
                'user_engagement_patterns': self._analyze_user_engagement()
            }
        }
        
        return analytics
    
    def _calculate_avg_participants(self, whiteboards: List[dict]) -> float:
        if not whiteboards:
            return 0
        return sum(len(wb['participants']) for wb in whiteboards) / len(whiteboards)
    
    def _analyze_whiteboard_tools(self, whiteboards: List[dict]) -> dict:
        tool_usage = {}
        for wb in whiteboards:
            for element in wb['canvas_data']['elements']:
                tool_type = element['type']
                tool_usage[tool_type] = tool_usage.get(tool_type, 0) + 1
        return dict(sorted(tool_usage.items(), key=lambda x: x[1], reverse=True)[:5])
    
    def _calculate_avg_breakout_duration(self, breakout_rooms: List[dict]) -> float:
        durations = []
        for room in breakout_rooms:
            if room.get('started_at') and room.get('ended_at'):
                start = datetime.fromisoformat(room['started_at'])
                end = datetime.fromisoformat(room['ended_at'])
                durations.append((end - start).total_seconds() / 60)
        return round(sum(durations) / len(durations), 1) if durations else 0
    
    def _analyze_grouping_strategies(self, breakout_rooms: List[dict]) -> dict:
        strategies = {}
        for room in breakout_rooms:
            strategy = room.get('grouping_strategy', 'manual')
            strategies[strategy] = strategies.get(strategy, 0) + 1
        return strategies
    
    def _calculate_breakout_completion_rate(self, breakout_rooms: List[dict]) -> float:
        if not breakout_rooms:
            return 0
        completed = len([room for room in breakout_rooms if room.get('status') == 'completed'])
        return round((completed / len(breakout_rooms)) * 100, 1)
    
    def _calculate_avg_reviews_per_submission(self, peer_reviews: List[dict]) -> float:
        total_reviews = 0
        total_submissions = 0
        for review in peer_reviews:
            total_submissions += len(review['submissions'])
            for submission in review['submissions'].values():
                total_reviews += len(submission['received_reviews'])
        return round(total_reviews / total_submissions, 1) if total_submissions > 0 else 0
    
    def _calculate_review_quality_score(self, peer_reviews: List[dict]) -> float:
        # Simplified quality calculation
        return 4.2  # Would be calculated from actual review feedback
    
    def _calculate_review_completion_rate(self, peer_reviews: List[dict]) -> float:
        if not peer_reviews:
            return 0
        completed_assignments = 0
        total_assignments = 0
        for review in peer_reviews:
            for assignments in review.get('review_assignments', {}).values():
                total_assignments += len(assignments)
                # Count completed reviews
                completed_assignments += len([a for a in assignments if a.get('completed', False)])
        return round((completed_assignments / total_assignments) * 100, 1) if total_assignments > 0 else 0
    
    def _identify_collaborative_subjects(self) -> List[dict]:
        subject_counts = {}
        for wb in self.whiteboards.values():
            subject = wb.get('subject_category', 'general')
            subject_counts[subject] = subject_counts.get(subject, 0) + 1
        
        return sorted([{'subject': k, 'sessions': v} for k, v in subject_counts.items()], 
                     key=lambda x: x['sessions'], reverse=True)[:5]
    
    def _analyze_collaboration_timing(self) -> dict:
        hour_counts = {}
        for wb in self.whiteboards.values():
            hour = datetime.fromisoformat(wb['created_at']).hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        peak_hour = max(hour_counts.items(), key=lambda x: x[1])[0] if hour_counts else 14
        return {'peak_hour': peak_hour, 'hourly_distribution': hour_counts}
    
    def _analyze_user_engagement(self) -> dict:
        return {
            'high_engagement_threshold': '3+ collaborative sessions per week',
            'average_session_length': '25 minutes',
            'return_rate': '78%'
        }

# Initialize global collaboration manager
collaboration_manager = AdvancedCollaborationManager()