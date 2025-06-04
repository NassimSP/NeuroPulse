"""
Voice Navigation System for NeuroPulse
ADHD-optimized voice commands for hands-free learning
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class VoiceNavigationEngine:
    """Advanced voice navigation with 50+ ADHD-friendly commands"""
    
    def __init__(self):
        self.commands = {}
        self.user_voice_data = {}
        self.command_history = {}
        self.voice_preferences = {}
        self.initialize_commands()
        self.load_data()
    
    def load_data(self):
        """Load voice navigation data"""
        try:
            with open('data/voice_navigation_data.json', 'r') as f:
                data = json.load(f)
                self.user_voice_data = data.get('user_data', {})
                self.command_history = data.get('command_history', {})
                self.voice_preferences = data.get('preferences', {})
        except FileNotFoundError:
            self.user_voice_data = {}
            self.command_history = {}
            self.voice_preferences = {}
    
    def save_data(self):
        """Save voice navigation data"""
        import os
        os.makedirs('data', exist_ok=True)
        
        data = {
            'user_data': self.user_voice_data,
            'command_history': self.command_history,
            'preferences': self.voice_preferences,
            'last_updated': datetime.now().isoformat()
        }
        
        with open('data/voice_navigation_data.json', 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def initialize_commands(self):
        """Initialize all voice commands with ADHD-friendly patterns"""
        
        # Navigation Commands
        self.commands.update({
            # Primary Navigation
            'go home': {'action': 'navigate', 'target': '/', 'description': 'Go to main dashboard'},
            'dashboard': {'action': 'navigate', 'target': '/dashboard', 'description': 'Open learning dashboard'},
            'explore subjects': {'action': 'navigate', 'target': '/explore', 'description': 'Browse available subjects'},
            'my profile': {'action': 'navigate', 'target': '/profile', 'description': 'View user profile'},
            'settings': {'action': 'navigate', 'target': '/settings', 'description': 'Open settings panel'},
            
            # Learning Session Commands
            'start learning': {'action': 'start_session', 'description': 'Begin new learning session'},
            'quick session': {'action': 'start_session', 'params': {'questions': 5}, 'description': 'Start 5-question session'},
            'standard session': {'action': 'start_session', 'params': {'questions': 10}, 'description': 'Start 10-question session'},
            'extended session': {'action': 'start_session', 'params': {'questions': 15}, 'description': 'Start 15-question session'},
            'deep dive': {'action': 'start_session', 'params': {'questions': 20}, 'description': 'Start 20-question session'},
            
            # Subject Selection
            'learn python': {'action': 'start_subject', 'subject': 'Python Programming', 'description': 'Start Python learning'},
            'learn electrical': {'action': 'start_subject', 'subject': 'Electrical Engineering', 'description': 'Start electrical engineering'},
            'learn finance': {'action': 'start_subject', 'subject': 'Financial Planning', 'description': 'Start financial planning'},
            'learn data analysis': {'action': 'start_subject', 'subject': 'Data Analysis', 'description': 'Start data analysis'},
            'learn botany': {'action': 'start_subject', 'subject': 'Botany', 'description': 'Start botany learning'},
            'learn chemistry': {'action': 'start_subject', 'subject': 'Chemistry', 'description': 'Start chemistry learning'},
            'learn physics': {'action': 'start_subject', 'subject': 'Physics', 'description': 'Start physics learning'},
            'learn math': {'action': 'start_subject', 'subject': 'Mathematics', 'description': 'Start mathematics learning'},
            
            # Difficulty Commands
            'foundation level': {'action': 'set_difficulty', 'level': 'foundation', 'description': 'Set to foundation difficulty'},
            'beginner level': {'action': 'set_difficulty', 'level': 'beginner', 'description': 'Set to beginner difficulty'},
            'intermediate level': {'action': 'set_difficulty', 'level': 'intermediate', 'description': 'Set to intermediate difficulty'},
            'advanced level': {'action': 'set_difficulty', 'level': 'advanced', 'description': 'Set to advanced difficulty'},
            'expert level': {'action': 'set_difficulty', 'level': 'expert', 'description': 'Set to expert difficulty'},
            'make easier': {'action': 'adjust_difficulty', 'direction': 'down', 'description': 'Decrease difficulty level'},
            'make harder': {'action': 'adjust_difficulty', 'direction': 'up', 'description': 'Increase difficulty level'},
            
            # Quiz Interaction
            'answer a': {'action': 'select_answer', 'option': 'A', 'description': 'Select answer option A'},
            'answer b': {'action': 'select_answer', 'option': 'B', 'description': 'Select answer option B'},
            'answer c': {'action': 'select_answer', 'option': 'C', 'description': 'Select answer option C'},
            'answer d': {'action': 'select_answer', 'option': 'D', 'description': 'Select answer option D'},
            'first option': {'action': 'select_answer', 'option': 'A', 'description': 'Select first answer option'},
            'second option': {'action': 'select_answer', 'option': 'B', 'description': 'Select second answer option'},
            'third option': {'action': 'select_answer', 'option': 'C', 'description': 'Select third answer option'},
            'fourth option': {'action': 'select_answer', 'option': 'D', 'description': 'Select fourth answer option'},
            'submit answer': {'action': 'submit_answer', 'description': 'Submit current answer selection'},
            'next question': {'action': 'next_question', 'description': 'Move to next question'},
            'skip question': {'action': 'skip_question', 'description': 'Skip current question'},
            'hint please': {'action': 'show_hint', 'description': 'Show hint for current question'},
            'explain answer': {'action': 'show_explanation', 'description': 'Show detailed explanation'},
            'repeat question': {'action': 'repeat_question', 'description': 'Read question again'},
            
            # Confidence Rating
            'very confident': {'action': 'set_confidence', 'level': 5, 'description': 'Set confidence to very high'},
            'confident': {'action': 'set_confidence', 'level': 4, 'description': 'Set confidence to high'},
            'somewhat confident': {'action': 'set_confidence', 'level': 3, 'description': 'Set confidence to medium'},
            'not confident': {'action': 'set_confidence', 'level': 2, 'description': 'Set confidence to low'},
            'guessing': {'action': 'set_confidence', 'level': 1, 'description': 'Set confidence to very low'},
            
            # Session Management
            'pause session': {'action': 'pause_session', 'description': 'Pause current learning session'},
            'resume session': {'action': 'resume_session', 'description': 'Resume paused session'},
            'end session': {'action': 'end_session', 'description': 'End current learning session'},
            'save progress': {'action': 'save_progress', 'description': 'Save current progress'},
            'session stats': {'action': 'show_stats', 'description': 'Show current session statistics'},
            
            # Progress and Analytics
            'my progress': {'action': 'show_progress', 'description': 'Show learning progress'},
            'my badges': {'action': 'show_badges', 'description': 'Display earned badges'},
            'my streak': {'action': 'show_streak', 'description': 'Show current learning streak'},
            'leaderboard': {'action': 'show_leaderboard', 'description': 'Show leaderboard rankings'},
            'my stats': {'action': 'show_user_stats', 'description': 'Display comprehensive statistics'},
            
            # ADHD-Specific Commands
            'focus mode': {'action': 'toggle_focus_mode', 'description': 'Toggle distraction-free focus mode'},
            'break time': {'action': 'suggest_break', 'description': 'Suggest taking a learning break'},
            'energy check': {'action': 'check_energy', 'description': 'Assess current energy level'},
            'mood update': {'action': 'update_mood', 'description': 'Update current mood state'},
            'motivation boost': {'action': 'motivation_boost', 'description': 'Get motivational encouragement'},
            'celebrate': {'action': 'celebrate_achievement', 'description': 'Celebrate recent achievement'},
            
            # Accessibility Commands
            'read aloud': {'action': 'text_to_speech', 'description': 'Read current content aloud'},
            'increase text size': {'action': 'adjust_text_size', 'direction': 'up', 'description': 'Make text larger'},
            'decrease text size': {'action': 'adjust_text_size', 'direction': 'down', 'description': 'Make text smaller'},
            'high contrast': {'action': 'toggle_high_contrast', 'description': 'Toggle high contrast mode'},
            'dark mode': {'action': 'toggle_dark_mode', 'description': 'Toggle dark theme'},
            'reduce motion': {'action': 'toggle_reduced_motion', 'description': 'Toggle reduced motion mode'},
            
            # Help and Information
            'help': {'action': 'show_help', 'description': 'Show help information'},
            'voice commands': {'action': 'list_commands', 'description': 'List all voice commands'},
            'what can I say': {'action': 'list_commands', 'description': 'Show available voice commands'},
            'keyboard shortcuts': {'action': 'show_shortcuts', 'description': 'Display keyboard shortcuts'},
            'about': {'action': 'show_about', 'description': 'Show about information'},
            
            # System Commands
            'refresh page': {'action': 'refresh', 'description': 'Refresh current page'},
            'go back': {'action': 'go_back', 'description': 'Navigate to previous page'},
            'full screen': {'action': 'toggle_fullscreen', 'description': 'Toggle fullscreen mode'},
            'minimize': {'action': 'minimize_window', 'description': 'Minimize application window'},
            'logout': {'action': 'logout', 'description': 'Log out of account'},
            
            # Advanced Learning Commands
            'spaced repetition': {'action': 'open_spaced_repetition', 'description': 'Open spaced repetition review'},
            'review cards': {'action': 'review_flashcards', 'description': 'Start flashcard review session'},
            'study group': {'action': 'join_study_group', 'description': 'Join or create study group'},
            'ai tutor': {'action': 'activate_ai_tutor', 'description': 'Activate AI tutoring assistant'},
            'practice mode': {'action': 'enter_practice_mode', 'description': 'Enter practice mode'},
            'test mode': {'action': 'enter_test_mode', 'description': 'Enter assessment mode'},
        })
    
    def process_voice_command(self, user_id: str, voice_input: str, context: Dict = None) -> Dict:
        """Process voice input and return command response"""
        
        # Initialize user data if needed
        if user_id not in self.user_voice_data:
            self.user_voice_data[user_id] = {
                'command_count': 0,
                'successful_commands': 0,
                'preferred_commands': {},
                'voice_patterns': [],
                'accessibility_preferences': {}
            }
        
        if user_id not in self.command_history:
            self.command_history[user_id] = []
        
        # Clean and normalize input
        cleaned_input = self._clean_voice_input(voice_input)
        
        # Find matching command
        command_match = self._find_command_match(cleaned_input)
        
        # Record command attempt
        command_record = {
            'timestamp': datetime.now().isoformat(),
            'input': voice_input,
            'cleaned_input': cleaned_input,
            'command_found': command_match is not None,
            'context': context or {}
        }
        
        if command_match:
            command_record['command'] = command_match
            command_record['action'] = self.commands[command_match]['action']
            
            # Update user statistics
            self.user_voice_data[user_id]['command_count'] += 1
            self.user_voice_data[user_id]['successful_commands'] += 1
            
            # Track preferred commands
            preferred = self.user_voice_data[user_id]['preferred_commands']
            preferred[command_match] = preferred.get(command_match, 0) + 1
            
            # Execute command
            response = self._execute_command(user_id, command_match, context)
            command_record['response'] = response
            
        else:
            # Handle unrecognized command
            self.user_voice_data[user_id]['command_count'] += 1
            response = self._handle_unrecognized_command(cleaned_input)
            command_record['response'] = response
        
        # Store command history
        self.command_history[user_id].append(command_record)
        
        # Keep only recent history (last 100 commands)
        if len(self.command_history[user_id]) > 100:
            self.command_history[user_id] = self.command_history[user_id][-100:]
        
        self.save_data()
        return command_record['response']
    
    def _clean_voice_input(self, voice_input: str) -> str:
        """Clean and normalize voice input for better matching"""
        # Convert to lowercase
        cleaned = voice_input.lower().strip()
        
        # Remove common voice recognition artifacts
        artifacts = ['um', 'uh', 'er', 'ah', 'please', 'can you', 'could you', 'would you']
        for artifact in artifacts:
            cleaned = re.sub(rf'\b{artifact}\b', '', cleaned)
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Handle common variations
        replacements = {
            'programme': 'program',
            'colour': 'color',
            'favourite': 'favorite',
            'centre': 'center',
            'learnt': 'learned',
        }
        
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)
        
        return cleaned
    
    def _find_command_match(self, cleaned_input: str) -> Optional[str]:
        """Find the best matching command for the input"""
        
        # Direct exact match
        if cleaned_input in self.commands:
            return cleaned_input
        
        # Fuzzy matching for flexibility
        best_match = None
        highest_score = 0
        
        for command in self.commands.keys():
            score = self._calculate_similarity(cleaned_input, command)
            if score > highest_score and score >= 0.7:  # Minimum 70% similarity
                highest_score = score
                best_match = command
        
        # Pattern matching for flexible commands
        if not best_match:
            best_match = self._pattern_match(cleaned_input)
        
        return best_match
    
    def _calculate_similarity(self, input_text: str, command: str) -> float:
        """Calculate similarity between input and command"""
        input_words = set(input_text.split())
        command_words = set(command.split())
        
        if not command_words:
            return 0
        
        # Jaccard similarity
        intersection = len(input_words.intersection(command_words))
        union = len(input_words.union(command_words))
        
        return intersection / union if union > 0 else 0
    
    def _pattern_match(self, cleaned_input: str) -> Optional[str]:
        """Pattern matching for more flexible command recognition"""
        
        patterns = {
            r'learn\s+(\w+)': 'learn {}',
            r'start\s+(\w+)': 'learn {}',
            r'study\s+(\w+)': 'learn {}',
            r'answer\s+([abcd]|\d)': 'answer {}',
            r'option\s+([abcd]|\d)': 'answer {}',
            r'confidence\s+(\d)': 'set_confidence_{}',
            r'difficulty\s+(\w+)': '{} level',
            r'(\d+)\s+questions?': '{}_question_session',
        }
        
        for pattern, template in patterns.items():
            match = re.search(pattern, cleaned_input)
            if match:
                param = match.group(1).lower()
                potential_command = template.format(param)
                
                # Check if this creates a valid command
                if potential_command in self.commands:
                    return potential_command
                
                # Handle subject learning commands
                if 'learn' in template:
                    subject_map = {
                        'python': 'learn python',
                        'electrical': 'learn electrical',
                        'finance': 'learn finance',
                        'data': 'learn data analysis',
                        'math': 'learn math',
                        'chemistry': 'learn chemistry',
                        'physics': 'learn physics',
                        'botany': 'learn botany'
                    }
                    if param in subject_map:
                        return subject_map[param]
        
        return None
    
    def _execute_command(self, user_id: str, command: str, context: Dict) -> Dict:
        """Execute the matched voice command"""
        command_data = self.commands[command]
        action = command_data['action']
        
        response = {
            'success': True,
            'command': command,
            'action': action,
            'message': f"Executing: {command_data['description']}",
            'ui_action': None,
            'data': {}
        }
        
        # Handle different action types
        if action == 'navigate':
            response['ui_action'] = 'navigate'
            response['data']['url'] = command_data['target']
            response['message'] = f"Navigating to {command_data['target']}"
        
        elif action == 'start_session':
            response['ui_action'] = 'start_learning_session'
            response['data'] = command_data.get('params', {})
            response['message'] = "Starting new learning session"
        
        elif action == 'start_subject':
            response['ui_action'] = 'start_subject_learning'
            response['data']['subject'] = command_data['subject']
            response['message'] = f"Starting {command_data['subject']} learning"
        
        elif action == 'select_answer':
            response['ui_action'] = 'select_quiz_answer'
            response['data']['option'] = command_data['option']
            response['message'] = f"Selected answer {command_data['option']}"
        
        elif action == 'set_confidence':
            response['ui_action'] = 'set_confidence_level'
            response['data']['level'] = command_data['level']
            response['message'] = f"Confidence set to level {command_data['level']}"
        
        elif action == 'toggle_focus_mode':
            response['ui_action'] = 'toggle_focus_mode'
            response['message'] = "Toggling focus mode"
        
        elif action == 'show_help':
            response['ui_action'] = 'show_help_modal'
            response['data']['help_type'] = 'voice_commands'
            response['message'] = "Showing voice command help"
        
        elif action == 'list_commands':
            response['ui_action'] = 'show_command_list'
            response['data']['commands'] = self._get_user_relevant_commands(user_id)
            response['message'] = "Showing available voice commands"
        
        else:
            # Generic action handling
            response['ui_action'] = action
            response['message'] = command_data['description']
        
        return response
    
    def _handle_unrecognized_command(self, cleaned_input: str) -> Dict:
        """Handle unrecognized voice commands with helpful suggestions"""
        
        # Find similar commands for suggestions
        suggestions = []
        for command in self.commands.keys():
            similarity = self._calculate_similarity(cleaned_input, command)
            if similarity >= 0.3:  # Lower threshold for suggestions
                suggestions.append((command, similarity))
        
        # Sort by similarity and take top 3
        suggestions.sort(key=lambda x: x[1], reverse=True)
        top_suggestions = [cmd for cmd, _ in suggestions[:3]]
        
        return {
            'success': False,
            'message': f"Voice command not recognized: '{cleaned_input}'",
            'suggestions': top_suggestions,
            'ui_action': 'show_voice_help',
            'data': {
                'unrecognized_input': cleaned_input,
                'suggestions': top_suggestions
            }
        }
    
    def _get_user_relevant_commands(self, user_id: str) -> List[Dict]:
        """Get commands most relevant to the user"""
        
        # Get user's most used commands
        user_data = self.user_voice_data.get(user_id, {})
        preferred_commands = user_data.get('preferred_commands', {})
        
        # Categorize commands by relevance
        categories = {
            'Most Used': [],
            'Navigation': [],
            'Learning': [],
            'Accessibility': [],
            'Advanced': []
        }
        
        for command, data in self.commands.items():
            cmd_info = {
                'command': command,
                'description': data['description'],
                'usage_count': preferred_commands.get(command, 0)
            }
            
            # Categorize based on action type
            action = data['action']
            if cmd_info['usage_count'] > 0:
                categories['Most Used'].append(cmd_info)
            elif action in ['navigate', 'go_back', 'refresh']:
                categories['Navigation'].append(cmd_info)
            elif action in ['start_session', 'start_subject', 'select_answer']:
                categories['Learning'].append(cmd_info)
            elif action in ['text_to_speech', 'toggle_high_contrast', 'adjust_text_size']:
                categories['Accessibility'].append(cmd_info)
            else:
                categories['Advanced'].append(cmd_info)
        
        # Sort most used by usage count
        categories['Most Used'].sort(key=lambda x: x['usage_count'], reverse=True)
        
        return categories
    
    def get_voice_analytics(self, user_id: str) -> Dict:
        """Generate voice command analytics for user"""
        
        if user_id not in self.user_voice_data:
            return {
                'total_commands': 0,
                'success_rate': 0,
                'most_used_commands': [],
                'insights': []
            }
        
        user_data = self.user_voice_data[user_id]
        total_commands = user_data['command_count']
        successful_commands = user_data['successful_commands']
        
        if total_commands == 0:
            return {
                'total_commands': 0,
                'success_rate': 0,
                'most_used_commands': [],
                'insights': ['Start using voice commands to see analytics']
            }
        
        success_rate = (successful_commands / total_commands) * 100
        
        # Get most used commands
        preferred_commands = user_data['preferred_commands']
        most_used = sorted(preferred_commands.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Generate insights
        insights = []
        if success_rate >= 90:
            insights.append("Excellent voice command accuracy! You're mastering hands-free navigation.")
        elif success_rate >= 70:
            insights.append("Good voice command usage. Try exploring more advanced commands.")
        else:
            insights.append("Voice commands need practice. Use 'help' to see available commands.")
        
        if len(preferred_commands) >= 10:
            insights.append("You're using a diverse range of voice commands - great for efficiency!")
        
        if total_commands >= 50:
            insights.append("Voice navigation expert! You're leveraging hands-free learning effectively.")
        
        return {
            'total_commands': total_commands,
            'successful_commands': successful_commands,
            'success_rate': round(success_rate, 1),
            'most_used_commands': most_used,
            'command_diversity': len(preferred_commands),
            'insights': insights,
            'recommendations': self._generate_voice_recommendations(user_data)
        }
    
    def _generate_voice_recommendations(self, user_data: Dict) -> List[str]:
        """Generate personalized voice command recommendations"""
        recommendations = []
        preferred_commands = user_data['preferred_commands']
        
        # Recommend underused but useful commands
        useful_commands = [
            'focus mode', 'break time', 'energy check', 'my progress',
            'spaced repetition', 'ai tutor', 'celebration'
        ]
        
        unused_useful = [cmd for cmd in useful_commands if cmd not in preferred_commands]
        if unused_useful:
            recommendations.append(f"Try these ADHD-helpful commands: {', '.join(unused_useful[:3])}")
        
        # Recommend based on learning patterns
        if 'start learning' in preferred_commands:
            recommendations.append("Use 'quick session' or 'deep dive' for specific session lengths")
        
        if any('learn' in cmd for cmd in preferred_commands):
            recommendations.append("Try 'spaced repetition' for better long-term retention")
        
        return recommendations

# Global instance
voice_navigation_system = VoiceNavigationEngine()