"""
Spaced Repetition System for NeuroPulse
Implements SM-2+ algorithm with ADHD-optimized scheduling
"""

import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ReviewDifficulty(Enum):
    """User's self-reported difficulty of recall"""
    BLACKOUT = 0     # Complete failure
    INCORRECT = 1    # Incorrect response with correct answer obvious
    HARD = 2         # Correct response with serious difficulty
    MEDIUM = 3       # Correct response with some difficulty
    EASY = 4         # Correct response with little difficulty
    PERFECT = 5      # Perfect response with no difficulty

class SpacedRepetitionEngine:
    """Advanced spaced repetition system with ADHD optimizations"""
    
    def __init__(self):
        self.cards = {}  # card_id -> card_data
        self.user_progress = {}  # user_id -> progress_data
        self.load_data()
    
    def load_data(self):
        """Load spaced repetition data from storage"""
        try:
            with open('data/spaced_repetition_cards.json', 'r') as f:
                self.cards = json.load(f)
        except FileNotFoundError:
            self.cards = {}
        
        try:
            with open('data/user_sr_progress.json', 'r') as f:
                self.user_progress = json.load(f)
        except FileNotFoundError:
            self.user_progress = {}
    
    def save_data(self):
        """Save spaced repetition data to storage"""
        import os
        os.makedirs('data', exist_ok=True)
        
        with open('data/spaced_repetition_cards.json', 'w') as f:
            json.dump(self.cards, f, indent=2, default=str)
        
        with open('data/user_sr_progress.json', 'w') as f:
            json.dump(self.user_progress, f, indent=2, default=str)
    
    def create_card(self, card_id: str, subject: str, question: str, 
                   answer: str, explanation: str = "", tags: List[str] = None) -> Dict:
        """Create a new spaced repetition card"""
        card = {
            'id': card_id,
            'subject': subject,
            'question': question,
            'answer': answer,
            'explanation': explanation,
            'tags': tags or [],
            'created_at': datetime.now().isoformat(),
            'difficulty': 2.5,  # Initial difficulty
            'total_reviews': 0,
            'successful_reviews': 0
        }
        
        self.cards[card_id] = card
        self.save_data()
        return card
    
    def initialize_user_card(self, user_id: str, card_id: str) -> Dict:
        """Initialize spaced repetition data for a user-card combination"""
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {}
        
        if card_id not in self.user_progress[user_id]:
            self.user_progress[user_id][card_id] = {
                'easiness_factor': 2.5,  # SM-2 algorithm starting point
                'interval': 1,  # Days until next review
                'repetitions': 0,  # Number of successful repetitions
                'next_review': datetime.now().isoformat(),
                'last_review': None,
                'review_history': [],
                'learning_phase': 'new',  # new, learning, review, mature
                'adhd_adjustments': {
                    'energy_correlation': [],  # Track energy levels during reviews
                    'time_preference': None,  # Best times for this card
                    'difficulty_perception': [],  # User's perceived difficulty over time
                }
            }
        
        return self.user_progress[user_id][card_id]
    
    def process_review(self, user_id: str, card_id: str, difficulty: ReviewDifficulty,
                      energy_level: int = 5, time_of_day: int = 12) -> Dict:
        """Process a review response using enhanced SM-2+ algorithm"""
        
        # Initialize if needed
        self.initialize_user_card(user_id, card_id)
        card_progress = self.user_progress[user_id][card_id]
        
        # Record the review
        review_record = {
            'date': datetime.now().isoformat(),
            'difficulty': difficulty.value,
            'energy_level': energy_level,
            'time_of_day': time_of_day,
            'interval_before': card_progress['interval']
        }
        
        # Update review history
        card_progress['review_history'].append(review_record)
        card_progress['last_review'] = datetime.now().isoformat()
        
        # Track ADHD-specific data
        card_progress['adhd_adjustments']['energy_correlation'].append({
            'energy': energy_level,
            'performance': difficulty.value,
            'time': time_of_day
        })
        
        card_progress['adhd_adjustments']['difficulty_perception'].append(difficulty.value)
        
        # Apply SM-2+ algorithm with ADHD modifications
        if difficulty.value >= 3:  # Correct response
            card_progress['repetitions'] += 1
            
            if card_progress['repetitions'] == 1:
                card_progress['interval'] = 1
            elif card_progress['repetitions'] == 2:
                card_progress['interval'] = 6
            else:
                # SM-2 formula with ADHD energy adjustment
                energy_multiplier = self._calculate_energy_multiplier(user_id, card_id)
                new_interval = card_progress['interval'] * card_progress['easiness_factor'] * energy_multiplier
                card_progress['interval'] = max(1, round(new_interval))
            
            # Update easiness factor
            q = difficulty.value
            ef = card_progress['easiness_factor']
            new_ef = ef + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
            card_progress['easiness_factor'] = max(1.3, new_ef)
            
            # Update learning phase
            if card_progress['repetitions'] >= 3 and card_progress['interval'] >= 21:
                card_progress['learning_phase'] = 'mature'
            elif card_progress['repetitions'] >= 1:
                card_progress['learning_phase'] = 'review'
            
        else:  # Incorrect response
            card_progress['repetitions'] = 0
            card_progress['interval'] = 1
            card_progress['learning_phase'] = 'learning'
            
            # Reduce easiness factor for very poor performance
            if difficulty.value <= 1:
                card_progress['easiness_factor'] = max(1.3, card_progress['easiness_factor'] - 0.2)
        
        # Calculate next review date with ADHD considerations
        next_review = self._calculate_next_review_date(user_id, card_id, card_progress)
        card_progress['next_review'] = next_review.isoformat()
        
        # Update card statistics
        if card_id in self.cards:
            self.cards[card_id]['total_reviews'] += 1
            if difficulty.value >= 3:
                self.cards[card_id]['successful_reviews'] += 1
        
        self.save_data()
        
        return {
            'next_review': next_review,
            'interval': card_progress['interval'],
            'learning_phase': card_progress['learning_phase'],
            'easiness_factor': round(card_progress['easiness_factor'], 2),
            'repetitions': card_progress['repetitions'],
            'recommendation': self._generate_review_recommendation(card_progress, difficulty)
        }
    
    def _calculate_energy_multiplier(self, user_id: str, card_id: str) -> float:
        """Calculate energy-based interval multiplier for ADHD optimization"""
        card_progress = self.user_progress[user_id][card_id]
        energy_data = card_progress['adhd_adjustments']['energy_correlation']
        
        if len(energy_data) < 3:
            return 1.0  # Not enough data
        
        # Analyze correlation between energy and performance
        recent_data = energy_data[-5:]  # Last 5 reviews
        avg_energy = sum(d['energy'] for d in recent_data) / len(recent_data)
        avg_performance = sum(d['performance'] for d in recent_data) / len(recent_data)
        
        # If high energy correlates with good performance, extend intervals
        if avg_energy >= 7 and avg_performance >= 4:
            return 1.2  # 20% longer intervals
        elif avg_energy <= 4 and avg_performance <= 2:
            return 0.8  # 20% shorter intervals
        
        return 1.0
    
    def _calculate_next_review_date(self, user_id: str, card_id: str, card_progress: Dict) -> datetime:
        """Calculate next review date with ADHD-optimized scheduling"""
        base_date = datetime.now() + timedelta(days=card_progress['interval'])
        
        # Find optimal time of day based on historical performance
        energy_data = card_progress['adhd_adjustments']['energy_correlation']
        if len(energy_data) >= 3:
            # Find times when performance was best
            good_times = [d['time'] for d in energy_data if d['performance'] >= 4]
            if good_times:
                optimal_hour = int(sum(good_times) / len(good_times))
                # Set review for optimal hour
                base_date = base_date.replace(hour=optimal_hour, minute=0, second=0, microsecond=0)
        
        return base_date
    
    def _generate_review_recommendation(self, card_progress: Dict, difficulty: ReviewDifficulty) -> str:
        """Generate ADHD-friendly review recommendations"""
        if difficulty.value <= 1:
            return "This concept needs more practice. Try breaking it into smaller parts or using memory techniques."
        elif difficulty.value == 2:
            return "You're making progress! Review the explanation and try again soon."
        elif difficulty.value == 3:
            return "Good recall with effort. This concept is strengthening in your memory."
        elif difficulty.value == 4:
            return "Excellent! You're mastering this concept. Keep up the momentum."
        else:
            return "Perfect recall! This knowledge is well-established. Intervals will be extended."
    
    def get_cards_due_for_review(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Get cards that are due for review, prioritized for ADHD learning"""
        if user_id not in self.user_progress:
            return []
        
        now = datetime.now()
        due_cards = []
        
        for card_id, progress in self.user_progress[user_id].items():
            next_review = datetime.fromisoformat(progress['next_review'])
            if next_review <= now:
                if card_id in self.cards:
                    card_data = self.cards[card_id].copy()
                    card_data['progress'] = progress
                    card_data['priority'] = self._calculate_card_priority(progress, now)
                    due_cards.append(card_data)
        
        # Sort by priority (highest first)
        due_cards.sort(key=lambda x: x['priority'], reverse=True)
        
        return due_cards[:limit]
    
    def _calculate_card_priority(self, progress: Dict, now: datetime) -> float:
        """Calculate review priority with ADHD considerations"""
        next_review = datetime.fromisoformat(progress['next_review'])
        days_overdue = (now - next_review).days
        
        # Base priority on how overdue the card is
        priority = max(0, days_overdue + 1)
        
        # Boost priority for cards in learning phase
        if progress['learning_phase'] in ['new', 'learning']:
            priority *= 2
        
        # Boost priority for frequently failed cards
        recent_reviews = progress['review_history'][-5:] if progress['review_history'] else []
        recent_failures = sum(1 for r in recent_reviews if r['difficulty'] < 3)
        if recent_failures >= 3:
            priority *= 1.5
        
        return priority
    
    def get_retention_insights(self, user_id: str) -> Dict:
        """Generate retention insights for analytics dashboard"""
        if user_id not in self.user_progress:
            return {'total_cards': 0, 'retention_rate': 0, 'insights': []}
        
        user_data = self.user_progress[user_id]
        total_cards = len(user_data)
        
        if total_cards == 0:
            return {'total_cards': 0, 'retention_rate': 0, 'insights': []}
        
        # Calculate retention metrics
        mature_cards = sum(1 for p in user_data.values() if p['learning_phase'] == 'mature')
        learning_cards = sum(1 for p in user_data.values() if p['learning_phase'] == 'learning')
        
        # Calculate average easiness factor
        avg_easiness = sum(p['easiness_factor'] for p in user_data.values()) / total_cards
        
        # Calculate retention rate based on recent performance
        recent_reviews = []
        for progress in user_data.values():
            recent_reviews.extend(progress['review_history'][-3:])
        
        if recent_reviews:
            successful_reviews = sum(1 for r in recent_reviews if r['difficulty'] >= 3)
            retention_rate = (successful_reviews / len(recent_reviews)) * 100
        else:
            retention_rate = 0
        
        # Generate insights
        insights = []
        if retention_rate >= 85:
            insights.append("Excellent retention! Your spaced repetition is highly effective.")
        elif retention_rate >= 70:
            insights.append("Good retention rate. Consider reviewing difficult cards more frequently.")
        else:
            insights.append("Retention needs improvement. Focus on understanding concepts before memorizing.")
        
        if mature_cards / total_cards >= 0.3:
            insights.append(f"You have {mature_cards} mature cards - knowledge is becoming long-term!")
        
        if avg_easiness < 2.0:
            insights.append("Some concepts are challenging. Break them into smaller, more manageable parts.")
        
        return {
            'total_cards': total_cards,
            'mature_cards': mature_cards,
            'learning_cards': learning_cards,
            'retention_rate': round(retention_rate, 1),
            'avg_easiness_factor': round(avg_easiness, 2),
            'insights': insights,
            'optimal_daily_reviews': self._calculate_optimal_daily_reviews(user_id)
        }
    
    def _calculate_optimal_daily_reviews(self, user_id: str) -> int:
        """Calculate optimal number of daily reviews for ADHD learners"""
        user_data = self.user_progress[user_id]
        
        # Base recommendation on learning phase distribution
        new_cards = sum(1 for p in user_data.values() if p['learning_phase'] == 'new')
        learning_cards = sum(1 for p in user_data.values() if p['learning_phase'] == 'learning')
        
        # ADHD-optimized daily limits
        optimal_new = min(5, new_cards)  # Max 5 new cards per day
        optimal_reviews = min(20, learning_cards)  # Max 20 reviews per day
        
        return optimal_new + optimal_reviews
    
    def create_cards_from_session(self, user_id: str, session_data: Dict) -> List[str]:
        """Create spaced repetition cards from a learning session"""
        created_cards = []
        
        for i, question in enumerate(session_data.get('questions', [])):
            card_id = f"{user_id}_{session_data['subject']}_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create card
            card = self.create_card(
                card_id=card_id,
                subject=session_data['subject'],
                question=question['question'],
                answer=question['correct_answer'],
                explanation=question.get('explanation', ''),
                tags=[session_data['subject'], session_data.get('difficulty', 'intermediate')]
            )
            
            # Initialize for user
            self.initialize_user_card(user_id, card_id)
            created_cards.append(card_id)
        
        return created_cards

# Global instance
spaced_repetition_engine = SpacedRepetitionEngine()