"""
Video Study Sessions for NeuroPulse Social Learning
Handles virtual study rooms, screen sharing, and collaborative video learning
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class VideoSessionManager:
    def __init__(self):
        self.sessions_file = 'video_sessions_data.json'
        self.recordings_file = 'session_recordings_data.json'
        self.participants_file = 'session_participants_data.json'
        
        self.load_data()
    
    def load_data(self):
        """Load video session data"""
        self.sessions = self._load_json_file(self.sessions_file, {})
        self.recordings = self._load_json_file(self.recordings_file, {})
        self.participants = self._load_json_file(self.participants_file, {})
    
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
    
    def create_study_session(self, host_id: str, session_data: dict) -> str:
        """Create a new video study session"""
        session_id = str(uuid.uuid4())
        
        session = {
            'id': session_id,
            'host_id': host_id,
            'title': session_data.get('title'),
            'description': session_data.get('description'),
            'subject_category': session_data.get('subject_category'),
            'topic': session_data.get('topic'),
            'scheduled_start': session_data.get('scheduled_start'),
            'duration_minutes': session_data.get('duration_minutes', 60),
            'max_participants': session_data.get('max_participants', 8),
            'session_type': session_data.get('session_type', 'collaborative'), # collaborative, presentation, workshop
            'requires_approval': session_data.get('requires_approval', False),
            'recording_enabled': session_data.get('recording_enabled', True),
            'screen_sharing_enabled': session_data.get('screen_sharing_enabled', True),
            'whiteboard_enabled': session_data.get('whiteboard_enabled', True),
            'breakout_rooms_enabled': session_data.get('breakout_rooms_enabled', False),
            'created_at': datetime.now().isoformat(),
            'status': 'scheduled', # scheduled, active, completed, cancelled
            'room_url': f"https://meet.neuropulse.app/room/{session_id}",
            'participants': [host_id],
            'waiting_room': [],
            'session_materials': session_data.get('materials', []),
            'learning_objectives': session_data.get('learning_objectives', []),
            'prerequisites': session_data.get('prerequisites', []),
            'tags': session_data.get('tags', [])
        }
        
        self.sessions[session_id] = session
        self.participants[session_id] = {
            host_id: {
                'user_id': host_id,
                'role': 'host',
                'joined_at': None,
                'left_at': None,
                'speaking_time': 0,
                'questions_asked': 0,
                'resources_shared': 0,
                'engagement_score': 0
            }
        }
        
        self._save_json_file(self.sessions_file, self.sessions)
        self._save_json_file(self.participants_file, self.participants)
        
        return session_id
    
    def join_session(self, session_id: str, user_id: str, user_name: str = None) -> dict:
        """Join a video study session"""
        if session_id not in self.sessions:
            return {'error': 'Session not found'}
        
        session = self.sessions[session_id]
        
        # Check session capacity
        if len(session['participants']) >= session['max_participants']:
            if session['requires_approval']:
                session['waiting_room'].append({
                    'user_id': user_id,
                    'user_name': user_name or f"Learner_{user_id[:8]}",
                    'requested_at': datetime.now().isoformat()
                })
                self._save_json_file(self.sessions_file, self.sessions)
                return {'status': 'waiting_room', 'message': 'Added to waiting room'}
            else:
                return {'error': 'Session is full'}
        
        # Add participant
        if user_id not in session['participants']:
            session['participants'].append(user_id)
        
        # Initialize participant data
        if session_id not in self.participants:
            self.participants[session_id] = {}
        
        self.participants[session_id][user_id] = {
            'user_id': user_id,
            'user_name': user_name or f"Learner_{user_id[:8]}",
            'role': 'participant',
            'joined_at': datetime.now().isoformat(),
            'left_at': None,
            'speaking_time': 0,
            'questions_asked': 0,
            'resources_shared': 0,
            'engagement_score': 0,
            'camera_enabled': True,
            'microphone_enabled': True,
            'screen_sharing': False
        }
        
        self._save_json_file(self.sessions_file, self.sessions)
        self._save_json_file(self.participants_file, self.participants)
        
        return {
            'status': 'joined',
            'session': session,
            'room_url': session['room_url']
        }
    
    def start_session(self, session_id: str, host_id: str) -> bool:
        """Start a scheduled video session"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        
        if session['host_id'] != host_id:
            return False
        
        session['status'] = 'active'
        session['actual_start'] = datetime.now().isoformat()
        
        # Initialize recording if enabled
        if session['recording_enabled']:
            self.recordings[session_id] = {
                'session_id': session_id,
                'recording_url': f"https://recordings.neuropulse.app/{session_id}",
                'started_at': datetime.now().isoformat(),
                'duration': 0,
                'file_size': 0,
                'status': 'recording'
            }
            self._save_json_file(self.recordings_file, self.recordings)
        
        self._save_json_file(self.sessions_file, self.sessions)
        return True
    
    def end_session(self, session_id: str, host_id: str) -> dict:
        """End an active video session"""
        if session_id not in self.sessions:
            return {'error': 'Session not found'}
        
        session = self.sessions[session_id]
        
        if session['host_id'] != host_id:
            return {'error': 'Only host can end session'}
        
        session['status'] = 'completed'
        session['ended_at'] = datetime.now().isoformat()
        
        # Calculate actual duration
        if 'actual_start' in session:
            start_time = datetime.fromisoformat(session['actual_start'])
            end_time = datetime.now()
            session['actual_duration'] = int((end_time - start_time).total_seconds() / 60)
        
        # Finalize recording
        if session_id in self.recordings:
            recording = self.recordings[session_id]
            recording['status'] = 'completed'
            recording['ended_at'] = datetime.now().isoformat()
            if 'started_at' in recording:
                start_time = datetime.fromisoformat(recording['started_at'])
                end_time = datetime.now()
                recording['duration'] = int((end_time - start_time).total_seconds())
            
            self._save_json_file(self.recordings_file, self.recordings)
        
        # Update participant data
        if session_id in self.participants:
            for participant in self.participants[session_id].values():
                if participant['left_at'] is None:
                    participant['left_at'] = datetime.now().isoformat()
        
        # Calculate session analytics
        session_analytics = self._calculate_session_analytics(session_id)
        session['analytics'] = session_analytics
        
        self._save_json_file(self.sessions_file, self.sessions)
        self._save_json_file(self.participants_file, self.participants)
        
        return {'success': True, 'analytics': session_analytics}
    
    def update_participant_activity(self, session_id: str, user_id: str, activity_data: dict):
        """Update participant activity during session"""
        if session_id not in self.participants or user_id not in self.participants[session_id]:
            return False
        
        participant = self.participants[session_id][user_id]
        
        # Update activity metrics
        if 'speaking_time' in activity_data:
            participant['speaking_time'] += activity_data['speaking_time']
        
        if 'questions_asked' in activity_data:
            participant['questions_asked'] += activity_data['questions_asked']
        
        if 'resources_shared' in activity_data:
            participant['resources_shared'] += activity_data['resources_shared']
        
        if 'camera_enabled' in activity_data:
            participant['camera_enabled'] = activity_data['camera_enabled']
        
        if 'microphone_enabled' in activity_data:
            participant['microphone_enabled'] = activity_data['microphone_enabled']
        
        if 'screen_sharing' in activity_data:
            participant['screen_sharing'] = activity_data['screen_sharing']
        
        # Calculate engagement score
        participant['engagement_score'] = self._calculate_engagement_score(participant)
        
        self._save_json_file(self.participants_file, self.participants)
        return True
    
    def _calculate_engagement_score(self, participant: dict) -> float:
        """Calculate engagement score for a participant"""
        score = 0
        
        # Speaking time (normalized)
        speaking_score = min(participant['speaking_time'] / 300, 1.0) * 30  # Max 30 points for 5+ minutes
        
        # Questions asked
        questions_score = min(participant['questions_asked'] * 5, 25)  # Max 25 points
        
        # Resources shared
        resources_score = min(participant['resources_shared'] * 10, 20)  # Max 20 points
        
        # Camera/mic enabled bonus
        media_score = 0
        if participant.get('camera_enabled', False):
            media_score += 12.5
        if participant.get('microphone_enabled', False):
            media_score += 12.5
        
        score = speaking_score + questions_score + resources_score + media_score
        return round(score, 1)
    
    def get_upcoming_sessions(self, user_id: str = None, subject_category: str = None) -> List[dict]:
        """Get upcoming video sessions"""
        upcoming_sessions = []
        current_time = datetime.now()
        
        for session_id, session in self.sessions.items():
            if session['status'] == 'scheduled':
                scheduled_time = datetime.fromisoformat(session['scheduled_start'])
                
                # Filter by user participation
                if user_id and user_id not in session['participants']:
                    continue
                
                # Filter by subject
                if subject_category and session['subject_category'] != subject_category:
                    continue
                
                # Only include sessions starting within next 7 days
                if scheduled_time > current_time and scheduled_time <= current_time + timedelta(days=7):
                    session_info = session.copy()
                    session_info['spots_available'] = session['max_participants'] - len(session['participants'])
                    session_info['time_until_start'] = int((scheduled_time - current_time).total_seconds() / 60)
                    upcoming_sessions.append(session_info)
        
        # Sort by scheduled start time
        upcoming_sessions.sort(key=lambda x: x['scheduled_start'])
        return upcoming_sessions
    
    def get_session_history(self, user_id: str, limit: int = 20) -> List[dict]:
        """Get user's session history"""
        user_sessions = []
        
        for session_id, session in self.sessions.items():
            if user_id in session['participants'] and session['status'] == 'completed':
                session_info = session.copy()
                
                # Add user-specific data
                if session_id in self.participants and user_id in self.participants[session_id]:
                    session_info['user_participation'] = self.participants[session_id][user_id]
                
                # Add recording info
                if session_id in self.recordings:
                    session_info['recording'] = self.recordings[session_id]
                
                user_sessions.append(session_info)
        
        # Sort by most recent first
        user_sessions.sort(key=lambda x: x.get('ended_at', x['created_at']), reverse=True)
        return user_sessions[:limit]
    
    def _calculate_session_analytics(self, session_id: str) -> dict:
        """Calculate comprehensive session analytics"""
        if session_id not in self.sessions or session_id not in self.participants:
            return {}
        
        session = self.sessions[session_id]
        participants = self.participants[session_id]
        
        # Basic metrics
        total_participants = len(participants)
        avg_engagement = sum(p['engagement_score'] for p in participants.values()) / total_participants if total_participants > 0 else 0
        
        # Speaking time distribution
        total_speaking_time = sum(p['speaking_time'] for p in participants.values())
        speaking_distribution = {}
        for user_id, participant in participants.items():
            speaking_percentage = (participant['speaking_time'] / total_speaking_time * 100) if total_speaking_time > 0 else 0
            speaking_distribution[user_id] = round(speaking_percentage, 1)
        
        # Participation metrics
        questions_total = sum(p['questions_asked'] for p in participants.values())
        resources_total = sum(p['resources_shared'] for p in participants.values())
        
        # Engagement levels
        high_engagement = len([p for p in participants.values() if p['engagement_score'] >= 70])
        medium_engagement = len([p for p in participants.values() if 40 <= p['engagement_score'] < 70])
        low_engagement = len([p for p in participants.values() if p['engagement_score'] < 40])
        
        return {
            'total_participants': total_participants,
            'average_engagement_score': round(avg_engagement, 1),
            'total_speaking_time': total_speaking_time,
            'speaking_distribution': speaking_distribution,
            'total_questions_asked': questions_total,
            'total_resources_shared': resources_total,
            'engagement_levels': {
                'high': high_engagement,
                'medium': medium_engagement,
                'low': low_engagement
            },
            'session_quality_score': self._calculate_session_quality(session, participants)
        }
    
    def _calculate_session_quality(self, session: dict, participants: dict) -> float:
        """Calculate overall session quality score"""
        score = 0
        
        # Participation rate (participants vs max capacity)
        participation_rate = len(participants) / session['max_participants']
        score += participation_rate * 25
        
        # Average engagement
        avg_engagement = sum(p['engagement_score'] for p in participants.values()) / len(participants) if participants else 0
        score += (avg_engagement / 100) * 35
        
        # Duration factor (did session run close to planned duration?)
        planned_duration = session['duration_minutes']
        actual_duration = session.get('actual_duration', 0)
        duration_factor = min(actual_duration / planned_duration, 1.0) if planned_duration > 0 else 0
        score += duration_factor * 20
        
        # Interaction factor (questions, resources shared)
        interaction_score = min((sum(p['questions_asked'] for p in participants.values()) + 
                               sum(p['resources_shared'] for p in participants.values())) / len(participants) * 5, 20)
        score += interaction_score
        
        return round(score, 1)
    
    def schedule_recurring_session(self, host_id: str, session_template: dict, recurrence_data: dict) -> List[str]:
        """Schedule recurring video sessions"""
        session_ids = []
        
        start_date = datetime.fromisoformat(recurrence_data['start_date'])
        end_date = datetime.fromisoformat(recurrence_data['end_date'])
        frequency = recurrence_data['frequency']  # daily, weekly, monthly
        interval = recurrence_data.get('interval', 1)  # every N days/weeks/months
        
        current_date = start_date
        
        while current_date <= end_date:
            session_data = session_template.copy()
            session_data['scheduled_start'] = current_date.isoformat()
            session_data['title'] = f"{session_template['title']} - {current_date.strftime('%Y-%m-%d')}"
            
            session_id = self.create_study_session(host_id, session_data)
            session_ids.append(session_id)
            
            # Calculate next occurrence
            if frequency == 'daily':
                current_date += timedelta(days=interval)
            elif frequency == 'weekly':
                current_date += timedelta(weeks=interval)
            elif frequency == 'monthly':
                # Approximate monthly increment
                current_date += timedelta(days=30 * interval)
        
        return session_ids

# Initialize global video session manager
video_manager = VideoSessionManager()