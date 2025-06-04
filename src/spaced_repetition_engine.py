"""
Spaced Repetition Engine for NeuroPulse
Implements advanced spaced repetition algorithms for optimal learning retention
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import math
import random

class SpacedRepetitionEngine:
    def __init__(self):
        self.user_cards_file = 'spaced_repetition_cards.json'
        self.learning_schedules_file = 'learning_schedules.json'
        self.retention_analytics_file = 'retention_analytics.json'
        
        self.load_data()
        
        # Algorithm parameters
        self.initial_interval = 1  # days
        self.ease_factor = 2.5
        self.minimum_ease = 1.3
        self.maximum_ease = 5.0
        self.graduation_interval = 4  # days
        self.maximum_interval = 365  # days
    
    def load_data(self):
        """Load spaced repetition data"""
        self.user_cards = self._load_json_file(self.user_cards_file, {})
        self.learning_schedules = self._load_json_file(self.learning_schedules_file, {})
        self.retention_analytics = self._load_json_file(self.retention_analytics_file, {})
    
    def _load_json_file(self, filename: str, default: dict) -> dict:
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return default
    
    def _save_json_file(self, filename: str, data: dict):
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_learning_card(self, user_id: str, content: dict) -> str:
        """Create a new learning card for spaced repetition"""
        card_id = str(uuid.uuid4())
        
        learning_card = {
            'card_id': card_id,
            'user_id': user_id,
            'content': {
                'question': content['question'],
                'answer': content['answer'],
                'subject_category': content.get('subject_category', 'general'),
                'difficulty_level': content.get('difficulty_level', 'intermediate'),
                'topic': content.get('topic', ''),
                'concept_tags': content.get('concept_tags', [])
            },
            'spaced_repetition': {
                'ease_factor': self.ease_factor,
                'interval': self.initial_interval,
                'repetitions': 0,
                'quality_responses': [],
                'last_reviewed': None,
                'next_review': datetime.now().isoformat(),
                'graduation_stage': 'learning',  # learning, review, mature
                'lapses': 0,
                'total_study_time': 0
            },
            'performance_metrics': {
                'total_reviews': 0,
                'correct_responses': 0,
                'average_response_time': 0,
                'retention_strength': 0.0,
                'memory_stability': 0.0,
                'forgetting_curve_fit': 0.0
            },
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Store in user's card collection
        if user_id not in self.user_cards:
            self.user_cards[user_id] = {}
        
        self.user_cards[user_id][card_id] = learning_card
        self._save_json_file(self.user_cards_file, self.user_cards)
        
        return card_id
    
    def review_card(self, user_id: str, card_id: str, quality_response: int, 
                   response_time: float, difficulty_felt: int = 3) -> dict:
        """
        Process card review with quality response
        quality_response: 0-5 scale (0=total blackout, 5=perfect recall)
        response_time: time taken to respond in seconds
        difficulty_felt: 1-5 scale of perceived difficulty
        """
        if user_id not in self.user_cards or card_id not in self.user_cards[user_id]:
            return {'error': 'Card not found'}
        
        card = self.user_cards[user_id][card_id]
        sr_data = card['spaced_repetition']
        performance = card['performance_metrics']
        
        # Record review
        review_record = {
            'timestamp': datetime.now().isoformat(),
            'quality': quality_response,
            'response_time': response_time,
            'difficulty_felt': difficulty_felt,
            'interval_before': sr_data['interval'],
            'ease_before': sr_data['ease_factor']
        }
        
        # Update performance metrics
        performance['total_reviews'] += 1
        if quality_response >= 3:  # Correct response
            performance['correct_responses'] += 1
        
        # Update average response time
        total_time = performance['average_response_time'] * (performance['total_reviews'] - 1) + response_time
        performance['average_response_time'] = total_time / performance['total_reviews']
        
        # Calculate new interval and ease factor using modified SM-2+ algorithm
        next_interval, new_ease_factor = self._calculate_next_interval(
            sr_data, quality_response, difficulty_felt
        )
        
        # Update spaced repetition data
        sr_data['ease_factor'] = new_ease_factor
        sr_data['interval'] = next_interval
        sr_data['repetitions'] += 1
        sr_data['quality_responses'].append(quality_response)
        sr_data['last_reviewed'] = datetime.now().isoformat()
        sr_data['next_review'] = (datetime.now() + timedelta(days=next_interval)).isoformat()
        sr_data['total_study_time'] += response_time
        
        # Handle lapses (quality < 3)
        if quality_response < 3:
            sr_data['lapses'] += 1
            sr_data['graduation_stage'] = 'learning'  # Reset to learning stage
        elif sr_data['repetitions'] >= 2 and sr_data['graduation_stage'] == 'learning':
            sr_data['graduation_stage'] = 'review'
        elif sr_data['interval'] >= 21 and sr_data['graduation_stage'] == 'review':
            sr_data['graduation_stage'] = 'mature'
        
        # Calculate retention metrics
        self._update_retention_metrics(card, review_record)
        
        card['updated_at'] = datetime.now().isoformat()
        
        # Store review record
        if 'review_history' not in card:
            card['review_history'] = []
        card['review_history'].append(review_record)
        
        self._save_json_file(self.user_cards_file, self.user_cards)
        
        # Update retention analytics
        self._update_retention_analytics(user_id, card, review_record)
        
        return {
            'success': True,
            'next_review_date': sr_data['next_review'],
            'next_interval_days': next_interval,
            'ease_factor': new_ease_factor,
            'graduation_stage': sr_data['graduation_stage'],
            'retention_strength': performance['retention_strength'],
            'performance_trend': self._calculate_performance_trend(card)
        }
    
    def _calculate_next_interval(self, sr_data: dict, quality: int, difficulty: int) -> tuple:
        """Calculate next review interval using enhanced SM-2+ algorithm"""
        current_ease = sr_data['ease_factor']
        current_interval = sr_data['interval']
        repetitions = sr_data['repetitions']
        
        # Quality factor adjustments
        if quality < 3:
            # Failed recall - reset to learning phase
            new_interval = max(1, current_interval * 0.2)
            new_ease = max(self.minimum_ease, current_ease - 0.2)
        else:
            # Successful recall
            if repetitions == 0:
                new_interval = 1
            elif repetitions == 1:
                new_interval = self.graduation_interval
            else:
                # Apply ease factor with difficulty adjustment
                difficulty_modifier = (6 - difficulty) / 10  # Convert 1-5 to 0.5-0.1
                adjusted_ease = current_ease + difficulty_modifier
                new_interval = current_interval * adjusted_ease
            
            # Adjust ease factor based on quality
            ease_adjustment = 0.1 * (quality - 3)  # -0.3 to +0.2
            new_ease = max(self.minimum_ease, 
                          min(self.maximum_ease, current_ease + ease_adjustment))
        
        # Apply interval limits
        new_interval = max(1, min(self.maximum_interval, new_interval))
        
        # Add randomization for natural spacing (±10%)
        randomization = random.uniform(0.9, 1.1)
        new_interval = int(new_interval * randomization)
        
        return new_interval, round(new_ease, 2)
    
    def _update_retention_metrics(self, card: dict, review_record: dict):
        """Update advanced retention metrics"""
        performance = card['performance_metrics']
        sr_data = card['spaced_repetition']
        
        # Calculate retention strength (0-1 scale)
        recent_qualities = sr_data['quality_responses'][-5:]  # Last 5 responses
        if recent_qualities:
            avg_quality = sum(recent_qualities) / len(recent_qualities)
            performance['retention_strength'] = max(0, min(1, (avg_quality - 1) / 4))
        
        # Calculate memory stability based on interval progression
        if sr_data['repetitions'] > 1:
            interval_growth = sr_data['interval'] / sr_data['repetitions']
            performance['memory_stability'] = min(1, interval_growth / 30)  # Normalize to 30-day baseline
        
        # Estimate forgetting curve fit
        if len(sr_data['quality_responses']) >= 3:
            performance['forgetting_curve_fit'] = self._calculate_forgetting_curve_fit(card)
    
    def _calculate_forgetting_curve_fit(self, card: dict) -> float:
        """Calculate how well the card fits the expected forgetting curve"""
        review_history = card.get('review_history', [])
        if len(review_history) < 3:
            return 0.5
        
        # Simplified forgetting curve analysis
        intervals = []
        qualities = []
        
        for i, review in enumerate(review_history[-10:]):  # Last 10 reviews
            if i > 0:
                prev_review = review_history[-(10-i+1)]
                interval_hours = (datetime.fromisoformat(review['timestamp']) - 
                                datetime.fromisoformat(prev_review['timestamp'])).total_seconds() / 3600
                intervals.append(interval_hours)
                qualities.append(review['quality'])
        
        if not intervals:
            return 0.5
        
        # Calculate correlation between interval and retention
        # Higher correlation indicates better fit to forgetting curve
        correlation = self._calculate_correlation(intervals, qualities)
        return max(0, min(1, (correlation + 1) / 2))  # Normalize -1,1 to 0,1
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient"""
        if len(x) != len(y) or len(x) < 2:
            return 0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(xi * xi for xi in x)
        sum_y2 = sum(yi * yi for yi in y)
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = math.sqrt((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y))
        
        if denominator == 0:
            return 0
        
        return numerator / denominator
    
    def _calculate_performance_trend(self, card: dict) -> str:
        """Calculate performance trend over recent reviews"""
        recent_qualities = card['spaced_repetition']['quality_responses'][-5:]
        if len(recent_qualities) < 3:
            return 'insufficient_data'
        
        # Calculate trend using simple linear regression
        x = list(range(len(recent_qualities)))
        correlation = self._calculate_correlation(x, recent_qualities)
        
        if correlation > 0.3:
            return 'improving'
        elif correlation < -0.3:
            return 'declining'
        else:
            return 'stable'
    
    def get_cards_due_for_review(self, user_id: str, limit: int = 20) -> List[dict]:
        """Get cards due for review, prioritized by urgency and importance"""
        if user_id not in self.user_cards:
            return []
        
        due_cards = []
        current_time = datetime.now()
        
        for card_id, card in self.user_cards[user_id].items():
            next_review = datetime.fromisoformat(card['spaced_repetition']['next_review'])
            
            if next_review <= current_time:
                # Calculate priority score
                overdue_hours = (current_time - next_review).total_seconds() / 3600
                retention_strength = card['performance_metrics']['retention_strength']
                
                # Higher priority for overdue cards with low retention
                priority_score = overdue_hours * (1 - retention_strength)
                
                due_cards.append({
                    'card_id': card_id,
                    'card': card,
                    'priority_score': priority_score,
                    'overdue_hours': max(0, overdue_hours)
                })
        
        # Sort by priority score (highest first)
        due_cards.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return due_cards[:limit]
    
    def generate_optimal_study_schedule(self, user_id: str, study_time_minutes: int = 30,
                                      preferred_times: List[str] = None) -> dict:
        """Generate optimal study schedule based on spaced repetition needs"""
        if user_id not in self.user_cards:
            return {'error': 'No cards found for user'}
        
        schedule_id = str(uuid.uuid4())
        
        # Get cards due in next 7 days
        upcoming_cards = []
        current_time = datetime.now()
        
        for card_id, card in self.user_cards[user_id].items():
            next_review = datetime.fromisoformat(card['spaced_repetition']['next_review'])
            days_until_due = (next_review - current_time).days
            
            if days_until_due <= 7:
                upcoming_cards.append({
                    'card_id': card_id,
                    'card': card,
                    'days_until_due': days_until_due,
                    'estimated_time': self._estimate_review_time(card)
                })
        
        # Group cards by day and optimize study sessions
        daily_schedule = {}
        for i in range(8):  # Next 7 days + today
            date = (current_time + timedelta(days=i)).strftime('%Y-%m-%d')
            daily_cards = [c for c in upcoming_cards if c['days_until_due'] == i]
            
            if daily_cards:
                # Optimize card order within study time
                optimized_session = self._optimize_study_session(daily_cards, study_time_minutes)
                daily_schedule[date] = optimized_session
        
        study_schedule = {
            'schedule_id': schedule_id,
            'user_id': user_id,
            'generated_at': datetime.now().isoformat(),
            'study_time_minutes': study_time_minutes,
            'daily_schedule': daily_schedule,
            'optimization_metrics': {
                'total_cards_scheduled': len(upcoming_cards),
                'estimated_retention_improvement': self._calculate_retention_improvement(upcoming_cards),
                'study_efficiency_score': self._calculate_study_efficiency(daily_schedule)
            }
        }
        
        self.learning_schedules[schedule_id] = study_schedule
        self._save_json_file(self.learning_schedules_file, self.learning_schedules)
        
        return study_schedule
    
    def _estimate_review_time(self, card: dict) -> float:
        """Estimate time needed to review a card based on complexity and performance"""
        base_time = 30  # seconds
        
        # Adjust based on difficulty
        difficulty_factor = {
            'beginner': 0.8,
            'intermediate': 1.0,
            'advanced': 1.3,
            'expert': 1.6
        }.get(card['content'].get('difficulty_level', 'intermediate'), 1.0)
        
        # Adjust based on past performance
        retention_strength = card['performance_metrics']['retention_strength']
        performance_factor = 2.0 - retention_strength  # Weaker retention = more time
        
        # Adjust based on graduation stage
        stage_factor = {
            'learning': 1.5,
            'review': 1.0,
            'mature': 0.7
        }.get(card['spaced_repetition']['graduation_stage'], 1.0)
        
        estimated_time = base_time * difficulty_factor * performance_factor * stage_factor
        return min(300, max(15, estimated_time))  # 15-300 seconds
    
    def _optimize_study_session(self, cards: List[dict], time_limit_minutes: int) -> dict:
        """Optimize card order and selection within time constraints"""
        time_limit_seconds = time_limit_minutes * 60
        
        # Sort cards by priority (overdue + low retention first)
        cards.sort(key=lambda x: (
            x['days_until_due'],  # Overdue cards first
            -x['card']['performance_metrics']['retention_strength']  # Low retention first
        ))
        
        selected_cards = []
        total_time = 0
        
        for card_data in cards:
            estimated_time = card_data['estimated_time']
            if total_time + estimated_time <= time_limit_seconds:
                selected_cards.append(card_data)
                total_time += estimated_time
            else:
                break
        
        return {
            'cards': selected_cards,
            'estimated_duration_minutes': total_time / 60,
            'cards_count': len(selected_cards),
            'optimization_efficiency': len(selected_cards) / len(cards) if cards else 0
        }
    
    def _calculate_retention_improvement(self, cards: List[dict]) -> float:
        """Calculate expected retention improvement from reviewing scheduled cards"""
        if not cards:
            return 0
        
        total_improvement = 0
        for card_data in cards:
            current_retention = card_data['card']['performance_metrics']['retention_strength']
            # Estimate improvement based on current retention (diminishing returns)
            improvement = (1 - current_retention) * 0.3  # Max 30% improvement
            total_improvement += improvement
        
        return round(total_improvement / len(cards), 3)
    
    def _calculate_study_efficiency(self, daily_schedule: dict) -> float:
        """Calculate overall study efficiency score"""
        if not daily_schedule:
            return 0
        
        total_efficiency = 0
        day_count = 0
        
        for day_data in daily_schedule.values():
            if day_data['cards']:
                efficiency = day_data['optimization_efficiency']
                total_efficiency += efficiency
                day_count += 1
        
        return round(total_efficiency / day_count, 3) if day_count > 0 else 0
    
    def _update_retention_analytics(self, user_id: str, card: dict, review_record: dict):
        """Update retention analytics for insights and optimization"""
        if user_id not in self.retention_analytics:
            self.retention_analytics[user_id] = {
                'total_reviews': 0,
                'total_cards': 0,
                'average_retention': 0,
                'subject_performance': {},
                'study_patterns': {},
                'optimization_suggestions': []
            }
        
        analytics = self.retention_analytics[user_id]
        analytics['total_reviews'] += 1
        
        # Update subject performance
        subject = card['content']['subject_category']
        if subject not in analytics['subject_performance']:
            analytics['subject_performance'][subject] = {
                'reviews': 0,
                'avg_quality': 0,
                'retention_trend': 'stable'
            }
        
        subject_data = analytics['subject_performance'][subject]
        subject_data['reviews'] += 1
        
        # Update average quality for subject
        total_quality = subject_data['avg_quality'] * (subject_data['reviews'] - 1) + review_record['quality']
        subject_data['avg_quality'] = total_quality / subject_data['reviews']
        
        self._save_json_file(self.retention_analytics_file, self.retention_analytics)
    
    def get_retention_insights(self, user_id: str) -> dict:
        """Generate comprehensive retention insights and recommendations"""
        if user_id not in self.user_cards:
            return {'error': 'No learning data found'}
        
        user_analytics = self.retention_analytics.get(user_id, {})
        user_cards = self.user_cards[user_id]
        
        # Calculate overall statistics
        total_cards = len(user_cards)
        cards_by_stage = {'learning': 0, 'review': 0, 'mature': 0}
        avg_retention = 0
        
        for card in user_cards.values():
            stage = card['spaced_repetition']['graduation_stage']
            cards_by_stage[stage] += 1
            avg_retention += card['performance_metrics']['retention_strength']
        
        avg_retention = avg_retention / total_cards if total_cards > 0 else 0
        
        # Identify challenging subjects
        challenging_subjects = []
        if user_analytics.get('subject_performance'):
            for subject, data in user_analytics['subject_performance'].items():
                if data['avg_quality'] < 3.0:
                    challenging_subjects.append({
                        'subject': subject,
                        'avg_quality': data['avg_quality'],
                        'recommendation': self._generate_subject_recommendation(data)
                    })
        
        return {
            'user_id': user_id,
            'generated_at': datetime.now().isoformat(),
            'overview': {
                'total_cards': total_cards,
                'cards_by_stage': cards_by_stage,
                'average_retention': round(avg_retention, 3),
                'total_reviews': user_analytics.get('total_reviews', 0)
            },
            'performance_insights': {
                'strongest_subjects': self._get_strongest_subjects(user_analytics),
                'challenging_subjects': challenging_subjects,
                'retention_trend': self._calculate_overall_retention_trend(user_cards),
                'study_consistency': self._calculate_study_consistency(user_cards)
            },
            'optimization_recommendations': self._generate_optimization_recommendations(user_cards, user_analytics)
        }
    
    def _generate_subject_recommendation(self, subject_data: dict) -> str:
        """Generate recommendation for challenging subject"""
        avg_quality = subject_data['avg_quality']
        
        if avg_quality < 2.0:
            return "Focus on fundamental concepts and increase study frequency"
        elif avg_quality < 2.5:
            return "Review basic principles and add more practice exercises"
        else:
            return "Adjust difficulty level and improve understanding methods"
    
    def _get_strongest_subjects(self, analytics: dict) -> List[dict]:
        """Get subjects with highest performance"""
        if not analytics.get('subject_performance'):
            return []
        
        subjects = []
        for subject, data in analytics['subject_performance'].items():
            if data['reviews'] >= 5:  # Minimum reviews for significance
                subjects.append({
                    'subject': subject,
                    'avg_quality': data['avg_quality'],
                    'reviews': data['reviews']
                })
        
        return sorted(subjects, key=lambda x: x['avg_quality'], reverse=True)[:3]
    
    def _calculate_overall_retention_trend(self, user_cards: dict) -> str:
        """Calculate overall retention trend across all cards"""
        trends = []
        
        for card in user_cards.values():
            trend = self._calculate_performance_trend(card)
            if trend != 'insufficient_data':
                trends.append(trend)
        
        if not trends:
            return 'insufficient_data'
        
        improving = trends.count('improving')
        declining = trends.count('declining')
        
        if improving > declining * 1.5:
            return 'improving'
        elif declining > improving * 1.5:
            return 'declining'
        else:
            return 'stable'
    
    def _calculate_study_consistency(self, user_cards: dict) -> float:
        """Calculate study consistency score based on review patterns"""
        if not user_cards:
            return 0
        
        review_dates = []
        for card in user_cards.values():
            if card.get('review_history'):
                for review in card['review_history']:
                    review_dates.append(datetime.fromisoformat(review['timestamp']).date())
        
        if len(review_dates) < 7:
            return 0.5  # Insufficient data
        
        # Calculate study days in last 30 days
        recent_dates = [d for d in review_dates if (datetime.now().date() - d).days <= 30]
        unique_study_days = len(set(recent_dates))
        
        # Consistency score: unique study days / 30 days
        return min(1.0, unique_study_days / 30)
    
    def _generate_optimization_recommendations(self, user_cards: dict, analytics: dict) -> List[str]:
        """Generate personalized optimization recommendations"""
        recommendations = []
        
        # Calculate metrics
        total_cards = len(user_cards)
        overdue_cards = len([c for c in user_cards.values() 
                           if datetime.fromisoformat(c['spaced_repetition']['next_review']) < datetime.now()])
        
        # Overdue cards recommendation
        if overdue_cards > total_cards * 0.3:
            recommendations.append(f"You have {overdue_cards} overdue cards. Consider shorter, more frequent study sessions.")
        
        # Study consistency recommendation
        consistency = self._calculate_study_consistency(user_cards)
        if consistency < 0.5:
            recommendations.append("Improve retention by studying more consistently. Aim for daily 15-minute sessions.")
        
        # Difficult subjects recommendation
        if analytics.get('subject_performance'):
            poor_subjects = [s for s, d in analytics['subject_performance'].items() if d['avg_quality'] < 2.5]
            if poor_subjects:
                recommendations.append(f"Focus extra attention on: {', '.join(poor_subjects[:2])}")
        
        # Learning stage distribution
        learning_cards = len([c for c in user_cards.values() 
                            if c['spaced_repetition']['graduation_stage'] == 'learning'])
        if learning_cards > total_cards * 0.6:
            recommendations.append("Many cards are still in learning stage. Be patient and focus on understanding.")
        
        return recommendations[:5]  # Limit to top 5 recommendations

# Initialize global spaced repetition engine
spaced_repetition_engine = SpacedRepetitionEngine()