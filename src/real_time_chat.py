"""
Real-time Chat System for NeuroPulse Social Learning
Handles study group discussions, challenge chat, and peer messaging
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

class ChatManager:
    def __init__(self):
        self.chat_rooms_file = 'chat_rooms_data.json'
        self.messages_file = 'chat_messages_data.json'
        self.user_connections_file = 'user_connections_data.json'
        
        self.load_data()
    
    def load_data(self):
        """Load chat data"""
        self.chat_rooms = self._load_json_file(self.chat_rooms_file, {})
        self.messages = self._load_json_file(self.messages_file, {})
        self.user_connections = self._load_json_file(self.user_connections_file, {})
    
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
    
    def create_chat_room(self, room_type: str, room_id: str, room_name: str, participants: List[str]) -> str:
        """Create a new chat room for study groups or challenges"""
        chat_room_id = f"{room_type}_{room_id}"
        
        chat_room = {
            'id': chat_room_id,
            'type': room_type,  # 'study_group', 'challenge', 'direct_message'
            'room_id': room_id,
            'name': room_name,
            'participants': participants,
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat(),
            'message_count': 0,
            'settings': {
                'allow_file_sharing': True,
                'moderation_enabled': True,
                'max_message_length': 500
            }
        }
        
        self.chat_rooms[chat_room_id] = chat_room
        
        # Initialize message history for this room
        if chat_room_id not in self.messages:
            self.messages[chat_room_id] = []
        
        self._save_json_file(self.chat_rooms_file, self.chat_rooms)
        self._save_json_file(self.messages_file, self.messages)
        
        return chat_room_id
    
    def join_chat_room(self, chat_room_id: str, user_id: str) -> bool:
        """Add user to chat room"""
        if chat_room_id not in self.chat_rooms:
            return False
        
        chat_room = self.chat_rooms[chat_room_id]
        if user_id not in chat_room['participants']:
            chat_room['participants'].append(user_id)
            
            # Add system message about user joining
            self.send_message(chat_room_id, 'system', f"User {user_id[:8]} joined the chat", 'system')
            
            self._save_json_file(self.chat_rooms_file, self.chat_rooms)
        
        return True
    
    def send_message(self, chat_room_id: str, user_id: str, content: str, message_type: str = 'text') -> dict:
        """Send a message to a chat room"""
        if chat_room_id not in self.chat_rooms:
            return {'error': 'Chat room not found'}
        
        chat_room = self.chat_rooms[chat_room_id]
        
        # Check if user is participant (except for system messages)
        if message_type != 'system' and user_id not in chat_room['participants']:
            return {'error': 'User not authorized to send messages'}
        
        # Validate message length
        if len(content) > chat_room['settings']['max_message_length']:
            return {'error': 'Message too long'}
        
        message_id = str(uuid.uuid4())
        message = {
            'id': message_id,
            'chat_room_id': chat_room_id,
            'user_id': user_id,
            'content': content,
            'type': message_type,  # 'text', 'image', 'file', 'system', 'reaction'
            'timestamp': datetime.now().isoformat(),
            'edited': False,
            'reactions': {},
            'reply_to': None
        }
        
        # Add message to room history
        if chat_room_id not in self.messages:
            self.messages[chat_room_id] = []
        
        self.messages[chat_room_id].append(message)
        
        # Update room statistics
        chat_room['message_count'] += 1
        chat_room['last_activity'] = datetime.now().isoformat()
        
        # Keep only last 1000 messages per room
        if len(self.messages[chat_room_id]) > 1000:
            self.messages[chat_room_id] = self.messages[chat_room_id][-1000:]
        
        self._save_json_file(self.chat_rooms_file, self.chat_rooms)
        self._save_json_file(self.messages_file, self.messages)
        
        return message
    
    def get_chat_history(self, chat_room_id: str, limit: int = 50, offset: int = 0) -> List[dict]:
        """Get chat history for a room"""
        if chat_room_id not in self.messages:
            return []
        
        messages = self.messages[chat_room_id]
        start_idx = max(0, len(messages) - limit - offset)
        end_idx = len(messages) - offset if offset > 0 else len(messages)
        
        return messages[start_idx:end_idx]
    
    def add_reaction(self, chat_room_id: str, message_id: str, user_id: str, reaction: str) -> bool:
        """Add reaction to a message"""
        if chat_room_id not in self.messages:
            return False
        
        for message in self.messages[chat_room_id]:
            if message['id'] == message_id:
                if reaction not in message['reactions']:
                    message['reactions'][reaction] = []
                
                if user_id not in message['reactions'][reaction]:
                    message['reactions'][reaction].append(user_id)
                else:
                    # Remove reaction if already exists (toggle)
                    message['reactions'][reaction].remove(user_id)
                    if not message['reactions'][reaction]:
                        del message['reactions'][reaction]
                
                self._save_json_file(self.messages_file, self.messages)
                return True
        
        return False
    
    def get_user_chat_rooms(self, user_id: str) -> List[dict]:
        """Get all chat rooms user is part of"""
        user_rooms = []
        
        for chat_room_id, chat_room in self.chat_rooms.items():
            if user_id in chat_room['participants']:
                room_info = chat_room.copy()
                
                # Add recent message preview
                recent_messages = self.get_chat_history(chat_room_id, limit=1)
                if recent_messages:
                    room_info['last_message'] = recent_messages[-1]
                else:
                    room_info['last_message'] = None
                
                # Add unread count (simplified - in real app would track user's last read timestamp)
                room_info['unread_count'] = 0
                
                user_rooms.append(room_info)
        
        # Sort by last activity
        user_rooms.sort(key=lambda x: x['last_activity'], reverse=True)
        return user_rooms
    
    def create_direct_message_room(self, user1_id: str, user2_id: str) -> str:
        """Create or get direct message room between two users"""
        # Create consistent room ID regardless of user order
        sorted_users = sorted([user1_id, user2_id])
        dm_room_id = f"dm_{sorted_users[0]}_{sorted_users[1]}"
        
        if dm_room_id not in self.chat_rooms:
            self.create_chat_room(
                'direct_message',
                dm_room_id,
                f"Direct Message: {user1_id[:8]} & {user2_id[:8]}",
                [user1_id, user2_id]
            )
        
        return dm_room_id
    
    def search_messages(self, chat_room_id: str, query: str, limit: int = 20) -> List[dict]:
        """Search messages in a chat room"""
        if chat_room_id not in self.messages:
            return []
        
        query_lower = query.lower()
        matching_messages = []
        
        for message in self.messages[chat_room_id]:
            if (query_lower in message['content'].lower() and 
                message['type'] == 'text' and
                len(matching_messages) < limit):
                matching_messages.append(message)
        
        return matching_messages
    
    def moderate_message(self, chat_room_id: str, message_id: str, action: str, moderator_id: str) -> bool:
        """Moderate a message (delete, flag, etc.)"""
        if chat_room_id not in self.messages:
            return False
        
        for i, message in enumerate(self.messages[chat_room_id]):
            if message['id'] == message_id:
                if action == 'delete':
                    message['content'] = '[Message deleted by moderator]'
                    message['type'] = 'moderated'
                    message['moderated_by'] = moderator_id
                    message['moderated_at'] = datetime.now().isoformat()
                elif action == 'flag':
                    message['flagged'] = True
                    message['flagged_by'] = moderator_id
                    message['flagged_at'] = datetime.now().isoformat()
                
                self._save_json_file(self.messages_file, self.messages)
                return True
        
        return False
    
    def get_chat_analytics(self, chat_room_id: str) -> dict:
        """Get analytics for a chat room"""
        if chat_room_id not in self.chat_rooms or chat_room_id not in self.messages:
            return {}
        
        chat_room = self.chat_rooms[chat_room_id]
        messages = self.messages[chat_room_id]
        
        # Calculate user activity
        user_activity = {}
        for message in messages:
            if message['type'] == 'text':
                user_id = message['user_id']
                if user_id not in user_activity:
                    user_activity[user_id] = {
                        'message_count': 0,
                        'total_characters': 0,
                        'reactions_given': 0,
                        'reactions_received': 0
                    }
                
                user_activity[user_id]['message_count'] += 1
                user_activity[user_id]['total_characters'] += len(message['content'])
                user_activity[user_id]['reactions_received'] += sum(len(reactions) for reactions in message['reactions'].values())
        
        # Calculate peak activity times
        hourly_activity = {}
        for message in messages:
            hour = datetime.fromisoformat(message['timestamp']).hour
            hourly_activity[hour] = hourly_activity.get(hour, 0) + 1
        
        peak_hour = max(hourly_activity.items(), key=lambda x: x[1])[0] if hourly_activity else 0
        
        return {
            'total_messages': len(messages),
            'total_participants': len(chat_room['participants']),
            'user_activity': user_activity,
            'peak_activity_hour': peak_hour,
            'average_message_length': sum(len(m['content']) for m in messages if m['type'] == 'text') / max(len([m for m in messages if m['type'] == 'text']), 1),
            'most_active_user': max(user_activity.items(), key=lambda x: x[1]['message_count'])[0] if user_activity else None
        }

# Initialize global chat manager
chat_manager = ChatManager()