"""
Personalized Dashboard with Mood-Based Themes and Learning Energy Visualization
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import math
import random

class PersonalizedDashboard:
    def __init__(self):
        self.user_preferences_file = 'user_dashboard_preferences.json'
        self.mood_data_file = 'user_mood_data.json'
        self.learning_energy_file = 'learning_energy_data.json'
        self.theme_customizations_file = 'theme_customizations.json'
        
        self.load_data()
        
        # Available themes with mood mappings
        self.mood_themes = {
            'focused': {
                'name': 'Deep Focus',
                'primary_color': '#2563eb',
                'secondary_color': '#1e40af',
                'accent_color': '#3b82f6',
                'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                'description': 'Calming blues and purples for concentrated learning',
                'characteristics': ['calm', 'focused', 'productive']
            },
            'energetic': {
                'name': 'Energy Boost',
                'primary_color': '#dc2626',
                'secondary_color': '#b91c1c',
                'accent_color': '#ef4444',
                'background': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                'description': 'Vibrant reds and oranges to energize your learning',
                'characteristics': ['energetic', 'motivated', 'dynamic']
            },
            'creative': {
                'name': 'Creative Flow',
                'primary_color': '#7c3aed',
                'secondary_color': '#6d28d9',
                'accent_color': '#8b5cf6',
                'background': 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
                'description': 'Inspiring purples and pastels for creative thinking',
                'characteristics': ['creative', 'imaginative', 'innovative']
            },
            'calm': {
                'name': 'Zen Mode',
                'primary_color': '#059669',
                'secondary_color': '#047857',
                'accent_color': '#10b981',
                'background': 'linear-gradient(135deg, #d299c2 0%, #fef9d7 100%)',
                'description': 'Peaceful greens and earth tones for relaxed learning',
                'characteristics': ['peaceful', 'balanced', 'mindful']
            },
            'confident': {
                'name': 'Power Mode',
                'primary_color': '#d97706',
                'secondary_color': '#b45309',
                'accent_color': '#f59e0b',
                'background': 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
                'description': 'Bold oranges and golds to boost confidence',
                'characteristics': ['confident', 'powerful', 'determined']
            },
            'curious': {
                'name': 'Explorer',
                'primary_color': '#0891b2',
                'secondary_color': '#0e7490',
                'accent_color': '#06b6d4',
                'background': 'linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%)',
                'description': 'Adventure-inspiring blues and cyans for exploration',
                'characteristics': ['curious', 'adventurous', 'inquisitive']
            }
        }
        
        # Learning energy states
        self.energy_states = {
            'peak': {'range': (80, 100), 'color': '#10b981', 'icon': '⚡'},
            'high': {'range': (60, 79), 'color': '#3b82f6', 'icon': '🔥'},
            'medium': {'range': (40, 59), 'color': '#f59e0b', 'icon': '💫'},
            'low': {'range': (20, 39), 'color': '#ef4444', 'icon': '🔋'},
            'depleted': {'range': (0, 19), 'color': '#6b7280', 'icon': '😴'}
        }
    
    def load_data(self):
        """Load dashboard data"""
        self.user_preferences = self._load_json_file(self.user_preferences_file, {})
        self.mood_data = self._load_json_file(self.mood_data_file, {})
        self.learning_energy = self._load_json_file(self.learning_energy_file, {})
        self.theme_customizations = self._load_json_file(self.theme_customizations_file, {})
    
    def _load_json_file(self, filename: str, default: dict) -> dict:
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return default
    
    def _save_json_file(self, filename: str, data: dict):
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def initialize_user_dashboard(self, user_id: str, initial_preferences: dict = None) -> dict:
        """Initialize personalized dashboard for user"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {
                'current_theme': 'focused',
                'auto_theme_detection': True,
                'preferred_themes': ['focused', 'calm'],
                'dashboard_layout': 'standard',
                'learning_goals': [],
                'daily_study_time_goal': 60,  # minutes
                'energy_tracking_enabled': True,
                'mood_check_frequency': 'daily',
                'personalization_level': 'adaptive',
                'accessibility_settings': {
                    'high_contrast': False,
                    'reduced_motion': False,
                    'large_text': False,
                    'color_blind_friendly': False
                },
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Apply initial preferences if provided
            if initial_preferences:
                self.user_preferences[user_id].update(initial_preferences)
        
        # Initialize mood tracking
        if user_id not in self.mood_data:
            self.mood_data[user_id] = {
                'current_mood': 'focused',
                'mood_history': [],
                'mood_patterns': {},
                'last_mood_check': None
            }
        
        # Initialize energy tracking
        if user_id not in self.learning_energy:
            self.learning_energy[user_id] = {
                'current_energy': 70,
                'energy_history': [],
                'daily_patterns': {},
                'factors_affecting_energy': {},
                'energy_predictions': {}
            }
        
        self._save_json_file(self.user_preferences_file, self.user_preferences)
        self._save_json_file(self.mood_data_file, self.mood_data)
        self._save_json_file(self.learning_energy_file, self.learning_energy)
        
        return self.get_dashboard_config(user_id)
    
    def update_mood(self, user_id: str, mood: str, context: dict = None) -> dict:
        """Update user's current mood and adjust theme accordingly"""
        self.initialize_user_dashboard(user_id)
        
        # Record mood data
        mood_entry = {
            'timestamp': datetime.now().isoformat(),
            'mood': mood,
            'context': context or {},
            'previous_mood': self.mood_data[user_id]['current_mood']
        }
        
        self.mood_data[user_id]['current_mood'] = mood
        self.mood_data[user_id]['mood_history'].append(mood_entry)
        self.mood_data[user_id]['last_mood_check'] = datetime.now().isoformat()
        
        # Update theme based on mood if auto-detection is enabled
        if self.user_preferences[user_id]['auto_theme_detection']:
            new_theme = self._select_theme_for_mood(mood, user_id)
            self.user_preferences[user_id]['current_theme'] = new_theme
        
        # Analyze mood patterns
        self._analyze_mood_patterns(user_id)
        
        # Update energy based on mood
        self._update_energy_from_mood(user_id, mood, context)
        
        self._save_json_file(self.mood_data_file, self.mood_data)
        self._save_json_file(self.user_preferences_file, self.user_preferences)
        
        return {
            'mood_updated': True,
            'new_theme': self.user_preferences[user_id]['current_theme'],
            'energy_impact': self._calculate_mood_energy_impact(mood),
            'recommendations': self._generate_mood_recommendations(user_id, mood)
        }
    
    def _select_theme_for_mood(self, mood: str, user_id: str) -> str:
        """Select optimal theme based on current mood"""
        user_prefs = self.user_preferences[user_id]
        preferred_themes = user_prefs['preferred_themes']
        
        # Direct mood-to-theme mapping
        mood_theme_map = {
            'excited': 'energetic',
            'focused': 'focused',
            'creative': 'creative',
            'calm': 'calm',
            'confident': 'confident',
            'curious': 'curious',
            'tired': 'calm',
            'stressed': 'calm',
            'motivated': 'energetic',
            'relaxed': 'calm',
            'inspired': 'creative',
            'determined': 'confident'
        }
        
        # Get theme for mood
        suggested_theme = mood_theme_map.get(mood, 'focused')
        
        # Check if suggested theme is in user's preferred themes
        if suggested_theme in preferred_themes:
            return suggested_theme
        
        # Otherwise, select from preferred themes based on characteristics
        theme_characteristics = self.mood_themes[suggested_theme]['characteristics']
        
        for theme_name in preferred_themes:
            if theme_name in self.mood_themes:
                theme_chars = self.mood_themes[theme_name]['characteristics']
                if any(char in theme_chars for char in theme_characteristics):
                    return theme_name
        
        return preferred_themes[0] if preferred_themes else 'focused'
    
    def _analyze_mood_patterns(self, user_id: str):
        """Analyze user's mood patterns over time"""
        mood_history = self.mood_data[user_id]['mood_history']
        
        if len(mood_history) < 5:
            return
        
        patterns = {}
        
        # Analyze daily mood patterns
        daily_moods = {}
        for entry in mood_history[-30:]:  # Last 30 entries
            timestamp = datetime.fromisoformat(entry['timestamp'])
            hour = timestamp.hour
            mood = entry['mood']
            
            if hour not in daily_moods:
                daily_moods[hour] = []
            daily_moods[hour].append(mood)
        
        # Find most common mood for each hour
        for hour, moods in daily_moods.items():
            most_common = max(set(moods), key=moods.count)
            patterns[f'hour_{hour}'] = most_common
        
        # Analyze mood transitions
        transitions = {}
        for i in range(1, len(mood_history)):
            prev_mood = mood_history[i-1]['mood']
            curr_mood = mood_history[i]['mood']
            transition = f"{prev_mood}_to_{curr_mood}"
            
            if transition not in transitions:
                transitions[transition] = 0
            transitions[transition] += 1
        
        patterns['common_transitions'] = transitions
        
        self.mood_data[user_id]['mood_patterns'] = patterns
    
    def update_learning_energy(self, user_id: str, energy_level: int, factors: dict = None) -> dict:
        """Update user's learning energy level"""
        self.initialize_user_dashboard(user_id)
        
        # Clamp energy level between 0-100
        energy_level = max(0, min(100, energy_level))
        
        # Record energy data
        energy_entry = {
            'timestamp': datetime.now().isoformat(),
            'energy_level': energy_level,
            'factors': factors or {},
            'previous_energy': self.learning_energy[user_id]['current_energy']
        }
        
        self.learning_energy[user_id]['current_energy'] = energy_level
        self.learning_energy[user_id]['energy_history'].append(energy_entry)
        
        # Analyze energy patterns
        self._analyze_energy_patterns(user_id)
        
        # Generate energy insights
        insights = self._generate_energy_insights(user_id, energy_level)
        
        self._save_json_file(self.learning_energy_file, self.learning_energy)
        
        return {
            'energy_updated': True,
            'current_energy': energy_level,
            'energy_state': self._get_energy_state(energy_level),
            'insights': insights,
            'recommendations': self._generate_energy_recommendations(user_id, energy_level)
        }
    
    def _update_energy_from_mood(self, user_id: str, mood: str, context: dict = None):
        """Automatically update energy based on mood change"""
        mood_energy_impact = {
            'excited': 15,
            'motivated': 10,
            'confident': 8,
            'focused': 5,
            'curious': 5,
            'creative': 3,
            'calm': 0,
            'relaxed': -5,
            'tired': -15,
            'stressed': -10,
            'frustrated': -8
        }
        
        current_energy = self.learning_energy[user_id]['current_energy']
        energy_change = mood_energy_impact.get(mood, 0)
        
        # Apply context modifiers
        if context:
            if context.get('well_rested', False):
                energy_change += 5
            if context.get('after_break', False):
                energy_change += 3
            if context.get('caffeine', False):
                energy_change += 8
            if context.get('after_exercise', False):
                energy_change += 10
        
        new_energy = max(0, min(100, current_energy + energy_change))
        self.learning_energy[user_id]['current_energy'] = new_energy
    
    def _calculate_mood_energy_impact(self, mood: str) -> dict:
        """Calculate how mood affects energy"""
        impact_map = {
            'excited': {'energy_change': '+15', 'duration': 'short', 'sustainability': 'low'},
            'motivated': {'energy_change': '+10', 'duration': 'medium', 'sustainability': 'high'},
            'confident': {'energy_change': '+8', 'duration': 'long', 'sustainability': 'high'},
            'focused': {'energy_change': '+5', 'duration': 'long', 'sustainability': 'very_high'},
            'tired': {'energy_change': '-15', 'duration': 'long', 'sustainability': 'low'},
            'stressed': {'energy_change': '-10', 'duration': 'medium', 'sustainability': 'medium'}
        }
        
        return impact_map.get(mood, {'energy_change': '0', 'duration': 'short', 'sustainability': 'medium'})
    
    def _analyze_energy_patterns(self, user_id: str):
        """Analyze user's energy patterns over time"""
        energy_history = self.learning_energy[user_id]['energy_history']
        
        if len(energy_history) < 10:
            return
        
        patterns = {}
        
        # Analyze daily energy patterns
        daily_energy = {}
        for entry in energy_history[-50:]:  # Last 50 entries
            timestamp = datetime.fromisoformat(entry['timestamp'])
            hour = timestamp.hour
            energy = entry['energy_level']
            
            if hour not in daily_energy:
                daily_energy[hour] = []
            daily_energy[hour].append(energy)
        
        # Calculate average energy for each hour
        for hour, energies in daily_energy.items():
            patterns[f'avg_energy_hour_{hour}'] = sum(energies) / len(energies)
        
        # Find peak energy times
        if patterns:
            peak_hour = max(patterns.items(), key=lambda x: x[1])
            patterns['peak_energy_time'] = peak_hour[0].replace('avg_energy_hour_', '')
            patterns['peak_energy_level'] = peak_hour[1]
        
        # Analyze energy trends
        recent_energies = [e['energy_level'] for e in energy_history[-10:]]
        if len(recent_energies) >= 5:
            trend = (recent_energies[-1] - recent_energies[0]) / len(recent_energies)
            patterns['recent_trend'] = 'increasing' if trend > 2 else 'decreasing' if trend < -2 else 'stable'
        
        self.learning_energy[user_id]['daily_patterns'] = patterns
    
    def _get_energy_state(self, energy_level: int) -> dict:
        """Get energy state information based on level"""
        for state, info in self.energy_states.items():
            if info['range'][0] <= energy_level <= info['range'][1]:
                return {
                    'state': state,
                    'color': info['color'],
                    'icon': info['icon'],
                    'level': energy_level
                }
        
        return {
            'state': 'unknown',
            'color': '#6b7280',
            'icon': '❓',
            'level': energy_level
        }
    
    def get_dashboard_config(self, user_id: str) -> dict:
        """Get complete dashboard configuration for user"""
        self.initialize_user_dashboard(user_id)
        
        user_prefs = self.user_preferences[user_id]
        current_theme_name = user_prefs['current_theme']
        current_theme = self.mood_themes[current_theme_name]
        
        mood_data = self.mood_data[user_id]
        energy_data = self.learning_energy[user_id]
        
        return {
            'user_id': user_id,
            'theme': {
                'name': current_theme['name'],
                'colors': {
                    'primary': current_theme['primary_color'],
                    'secondary': current_theme['secondary_color'],
                    'accent': current_theme['accent_color'],
                    'background': current_theme['background']
                },
                'description': current_theme['description']
            },
            'mood': {
                'current': mood_data['current_mood'],
                'last_updated': mood_data['last_mood_check'],
                'patterns': mood_data.get('mood_patterns', {}),
                'available_moods': list(self.mood_themes.keys())
            },
            'energy': {
                'current_level': energy_data['current_energy'],
                'state': self._get_energy_state(energy_data['current_energy']),
                'patterns': energy_data.get('daily_patterns', {}),
                'visualization_data': self._generate_energy_visualization_data(user_id)
            },
            'preferences': user_prefs,
            'insights': self._generate_dashboard_insights(user_id),
            'recommendations': self._generate_dashboard_recommendations(user_id)
        }
    
    def _generate_energy_visualization_data(self, user_id: str) -> dict:
        """Generate data for energy visualization charts"""
        energy_history = self.learning_energy[user_id]['energy_history']
        
        if not energy_history:
            return {'no_data': True}
        
        # Last 24 hours of energy data
        now = datetime.now()
        last_24h = [e for e in energy_history 
                   if (now - datetime.fromisoformat(e['timestamp'])).total_seconds() <= 86400]
        
        # Last 7 days of energy data
        last_7d = [e for e in energy_history 
                  if (now - datetime.fromisoformat(e['timestamp'])).days <= 7]
        
        visualization_data = {
            'hourly_pattern': self._generate_hourly_energy_pattern(last_24h),
            'daily_trend': self._generate_daily_energy_trend(last_7d),
            'energy_distribution': self._generate_energy_distribution(energy_history[-100:]),
            'factors_correlation': self._analyze_energy_factors(energy_history[-50:])
        }
        
        return visualization_data
    
    def _generate_hourly_energy_pattern(self, energy_data: List[dict]) -> dict:
        """Generate hourly energy pattern for visualization"""
        hourly_data = {}
        
        for entry in energy_data:
            hour = datetime.fromisoformat(entry['timestamp']).hour
            if hour not in hourly_data:
                hourly_data[hour] = []
            hourly_data[hour].append(entry['energy_level'])
        
        # Calculate average energy for each hour
        pattern = {}
        for hour in range(24):
            if hour in hourly_data:
                pattern[hour] = sum(hourly_data[hour]) / len(hourly_data[hour])
            else:
                pattern[hour] = None  # No data for this hour
        
        return {
            'data_points': [(hour, energy) for hour, energy in pattern.items() if energy is not None],
            'peak_hours': [hour for hour, energy in pattern.items() 
                          if energy and energy >= max([e for e in pattern.values() if e]) * 0.9],
            'low_hours': [hour for hour, energy in pattern.items() 
                         if energy and energy <= min([e for e in pattern.values() if e]) * 1.1]
        }
    
    def _generate_daily_energy_trend(self, energy_data: List[dict]) -> dict:
        """Generate daily energy trend for the past week"""
        daily_data = {}
        
        for entry in energy_data:
            date = datetime.fromisoformat(entry['timestamp']).date()
            if date not in daily_data:
                daily_data[date] = []
            daily_data[date].append(entry['energy_level'])
        
        # Calculate average energy for each day
        trend_data = []
        for date in sorted(daily_data.keys()):
            avg_energy = sum(daily_data[date]) / len(daily_data[date])
            trend_data.append({
                'date': date.isoformat(),
                'energy': avg_energy,
                'sessions': len(daily_data[date])
            })
        
        return {
            'daily_averages': trend_data,
            'overall_trend': self._calculate_trend([d['energy'] for d in trend_data]),
            'best_day': max(trend_data, key=lambda x: x['energy']) if trend_data else None,
            'improvement_rate': self._calculate_improvement_rate(trend_data)
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values"""
        if len(values) < 2:
            return 'stable'
        
        slope = (values[-1] - values[0]) / len(values)
        
        if slope > 2:
            return 'strongly_increasing'
        elif slope > 0.5:
            return 'increasing'
        elif slope < -2:
            return 'strongly_decreasing'
        elif slope < -0.5:
            return 'decreasing'
        else:
            return 'stable'
    
    def _calculate_improvement_rate(self, trend_data: List[dict]) -> float:
        """Calculate rate of improvement in energy levels"""
        if len(trend_data) < 2:
            return 0
        
        first_energy = trend_data[0]['energy']
        last_energy = trend_data[-1]['energy']
        days = len(trend_data)
        
        return (last_energy - first_energy) / days
    
    def _generate_energy_distribution(self, energy_data: List[dict]) -> dict:
        """Generate energy level distribution analysis"""
        if not energy_data:
            return {}
        
        energy_levels = [e['energy_level'] for e in energy_data]
        
        distribution = {
            'peak': len([e for e in energy_levels if e >= 80]),
            'high': len([e for e in energy_levels if 60 <= e < 80]),
            'medium': len([e for e in energy_levels if 40 <= e < 60]),
            'low': len([e for e in energy_levels if 20 <= e < 40]),
            'depleted': len([e for e in energy_levels if e < 20])
        }
        
        total = sum(distribution.values())
        percentages = {state: (count / total) * 100 for state, count in distribution.items()}
        
        return {
            'counts': distribution,
            'percentages': percentages,
            'average': sum(energy_levels) / len(energy_levels),
            'median': sorted(energy_levels)[len(energy_levels) // 2],
            'most_common_state': max(distribution.items(), key=lambda x: x[1])[0]
        }
    
    def _analyze_energy_factors(self, energy_data: List[dict]) -> dict:
        """Analyze factors that correlate with energy levels"""
        correlations = {}
        
        for entry in energy_data:
            factors = entry.get('factors', {})
            energy = entry['energy_level']
            
            for factor, value in factors.items():
                if factor not in correlations:
                    correlations[factor] = {'energies': [], 'values': []}
                
                correlations[factor]['energies'].append(energy)
                correlations[factor]['values'].append(value)
        
        # Calculate correlation strength for each factor
        factor_impacts = {}
        for factor, data in correlations.items():
            if len(data['energies']) >= 5:
                # Simple correlation calculation
                avg_energy_with_factor = sum(data['energies']) / len(data['energies'])
                factor_impacts[factor] = {
                    'average_energy': avg_energy_with_factor,
                    'sample_size': len(data['energies']),
                    'impact_strength': abs(avg_energy_with_factor - 50)  # Distance from neutral
                }
        
        return factor_impacts
    
    def _generate_dashboard_insights(self, user_id: str) -> List[str]:
        """Generate personalized insights for dashboard"""
        insights = []
        
        mood_data = self.mood_data[user_id]
        energy_data = self.learning_energy[user_id]
        patterns = energy_data.get('daily_patterns', {})
        
        # Energy insights
        current_energy = energy_data['current_energy']
        if current_energy >= 80:
            insights.append("Your energy levels are excellent - perfect time for challenging topics!")
        elif current_energy <= 30:
            insights.append("Energy is low - consider taking a break or switching to lighter content.")
        
        # Peak time insights
        if 'peak_energy_time' in patterns:
            peak_time = patterns['peak_energy_time']
            insights.append(f"Your peak energy time is around {peak_time}:00 - schedule important learning then.")
        
        # Mood pattern insights
        if mood_data['mood_history']:
            recent_moods = [m['mood'] for m in mood_data['mood_history'][-5:]]
            if len(set(recent_moods)) == 1:
                insights.append(f"You've been consistently {recent_moods[0]} - your learning state is stable.")
        
        return insights[:3]  # Limit to top 3 insights
    
    def _generate_dashboard_recommendations(self, user_id: str) -> List[str]:
        """Generate actionable recommendations for dashboard"""
        recommendations = []
        
        mood_data = self.mood_data[user_id]
        energy_data = self.learning_energy[user_id]
        current_energy = energy_data['current_energy']
        current_mood = mood_data['current_mood']
        
        # Energy-based recommendations
        if current_energy < 40:
            recommendations.append("Take a 10-15 minute break to recharge your learning energy")
        elif current_energy > 80:
            recommendations.append("High energy detected - tackle your most challenging subjects now")
        
        # Mood-based recommendations
        mood_recommendations = {
            'stressed': "Try some breathing exercises or switch to a calmer learning environment",
            'tired': "Consider shorter study sessions with more frequent breaks",
            'excited': "Channel that energy into interactive or hands-on learning activities",
            'creative': "Perfect time for project-based learning or brainstorming sessions"
        }
        
        if current_mood in mood_recommendations:
            recommendations.append(mood_recommendations[current_mood])
        
        return recommendations[:3]  # Limit to top 3 recommendations
    
    def _generate_mood_recommendations(self, user_id: str, mood: str) -> List[str]:
        """Generate mood-specific recommendations"""
        recommendations_map = {
            'excited': [
                "Use this energy for interactive learning activities",
                "Try gamified content or competitions",
                "Set ambitious but achievable learning goals"
            ],
            'focused': [
                "Perfect time for deep work and complex topics",
                "Minimize distractions for maximum productivity",
                "Tackle your most challenging subjects"
            ],
            'creative': [
                "Explore project-based learning",
                "Try mind mapping or visual note-taking",
                "Engage in collaborative discussions"
            ],
            'tired': [
                "Switch to lighter, review-based content",
                "Take regular breaks every 25 minutes",
                "Consider postponing new complex topics"
            ],
            'stressed': [
                "Practice breathing exercises before studying",
                "Break large tasks into smaller chunks",
                "Choose familiar topics to build confidence"
            ]
        }
        
        return recommendations_map.get(mood, ["Continue with your regular learning routine"])
    
    def _generate_energy_recommendations(self, user_id: str, energy_level: int) -> List[str]:
        """Generate energy-level specific recommendations"""
        if energy_level >= 80:
            return [
                "Excellent energy - tackle challenging new concepts",
                "This is perfect timing for problem-solving exercises",
                "Consider extending your study session"
            ]
        elif energy_level >= 60:
            return [
                "Good energy levels - continue with regular content",
                "Mix challenging and easier topics",
                "Maintain current study pace"
            ]
        elif energy_level >= 40:
            return [
                "Moderate energy - focus on review and practice",
                "Take short breaks between topics",
                "Avoid overly complex new material"
            ]
        elif energy_level >= 20:
            return [
                "Low energy - switch to review or light reading",
                "Take frequent breaks",
                "Consider ending session early if needed"
            ]
        else:
            return [
                "Very low energy - take a substantial break",
                "Consider postponing study session",
                "Focus on rest and recovery"
            ]
    
    def _generate_energy_insights(self, user_id: str, energy_level: int) -> List[str]:
        """Generate insights about current energy level"""
        insights = []
        
        energy_history = self.learning_energy[user_id]['energy_history']
        if len(energy_history) >= 5:
            recent_energies = [e['energy_level'] for e in energy_history[-5:]]
            avg_recent = sum(recent_energies) / len(recent_energies)
            
            if energy_level > avg_recent + 10:
                insights.append("Your energy is significantly higher than recent sessions")
            elif energy_level < avg_recent - 10:
                insights.append("Your energy is lower than usual - check what might be affecting it")
        
        # Time-based insights
        current_hour = datetime.now().hour
        if 6 <= current_hour <= 10:
            insights.append("Morning energy - often best for learning new concepts")
        elif 14 <= current_hour <= 16:
            insights.append("Afternoon period - good for review and practice")
        elif 19 <= current_hour <= 21:
            insights.append("Evening study - consider lighter topics")
        
        return insights

# Initialize global personalized dashboard
personalized_dashboard = PersonalizedDashboard()