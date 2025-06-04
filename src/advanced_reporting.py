"""
Advanced Reporting Dashboard for NeuroPulse Enterprise
Provides executive insights, institutional analytics, and comprehensive reporting
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import statistics

class ReportingManager:
    def __init__(self):
        self.reports_file = 'executive_reports_data.json'
        self.metrics_file = 'institutional_metrics_data.json'
        self.benchmarks_file = 'benchmark_data.json'
        self.custom_reports_file = 'custom_reports_data.json'
        
        self.load_data()
    
    def load_data(self):
        """Load reporting data"""
        self.reports = self._load_json_file(self.reports_file, {})
        self.metrics = self._load_json_file(self.metrics_file, {})
        self.benchmarks = self._load_json_file(self.benchmarks_file, {})
        self.custom_reports = self._load_json_file(self.custom_reports_file, {})
    
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
    
    def generate_executive_dashboard(self, institution_id: str, time_period: str = '30d') -> dict:
        """Generate comprehensive executive dashboard"""
        from lms_integration import lms_manager
        from analytics_dashboard import analytics_manager
        from social_learning import social_manager
        
        # Calculate date range
        end_date = datetime.now()
        if time_period == '7d':
            start_date = end_date - timedelta(days=7)
        elif time_period == '30d':
            start_date = end_date - timedelta(days=30)
        elif time_period == '90d':
            start_date = end_date - timedelta(days=90)
        elif time_period == '1y':
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Key Performance Indicators
        kpis = self._calculate_institutional_kpis(institution_id, start_date, end_date)
        
        # Student engagement metrics
        engagement_metrics = self._calculate_engagement_metrics(institution_id, start_date, end_date)
        
        # Learning outcomes analysis
        outcomes_analysis = self._analyze_learning_outcomes(institution_id, start_date, end_date)
        
        # Resource utilization
        resource_utilization = self._calculate_resource_utilization(institution_id, start_date, end_date)
        
        # Predictive analytics
        predictions = self._generate_predictive_insights(institution_id)
        
        # Comparative benchmarks
        benchmarks = self._get_benchmark_comparisons(institution_id)
        
        dashboard = {
            'generated_at': datetime.now().isoformat(),
            'institution_id': institution_id,
            'time_period': time_period,
            'date_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'key_performance_indicators': kpis,
            'engagement_metrics': engagement_metrics,
            'learning_outcomes': outcomes_analysis,
            'resource_utilization': resource_utilization,
            'predictive_insights': predictions,
            'benchmark_comparisons': benchmarks,
            'executive_summary': self._generate_executive_summary(kpis, engagement_metrics, outcomes_analysis)
        }
        
        # Save report
        report_id = str(uuid.uuid4())
        self.reports[report_id] = dashboard
        self._save_json_file(self.reports_file, self.reports)
        
        return dashboard
    
    def _calculate_institutional_kpis(self, institution_id: str, start_date: datetime, end_date: datetime) -> dict:
        """Calculate key performance indicators for institution"""
        from lms_integration import lms_manager
        
        # Get institution courses
        institution_courses = [c for c in lms_manager.courses.values() 
                             if c.get('institution_id') == institution_id]
        
        # Active enrollments
        active_enrollments = []
        for course in institution_courses:
            course_enrollments = [e for e in lms_manager.enrollments.values() 
                                if e['course_id'] == course['id'] and e['status'] == 'active']
            active_enrollments.extend(course_enrollments)
        
        # Course completion rates
        completion_rates = []
        for course in institution_courses:
            course_enrollments = [e for e in lms_manager.enrollments.values() 
                                if e['course_id'] == course['id']]
            if course_enrollments:
                completed = len([e for e in course_enrollments if e['status'] == 'completed'])
                rate = (completed / len(course_enrollments)) * 100
                completion_rates.append(rate)
        
        # Average grades
        institution_grades = []
        for course in institution_courses:
            course_grades = [g['overall_grade'] for g in lms_manager.gradebook.values() 
                           if g['course_id'] == course['id'] and g['overall_grade'] is not None]
            institution_grades.extend(course_grades)
        
        # Student satisfaction (placeholder for real surveys)
        satisfaction_score = 85.5  # Would integrate with actual survey data
        
        # Time to completion analysis
        time_to_completion = self._calculate_average_completion_time(institution_courses)
        
        return {
            'total_active_students': len(set(e['student_id'] for e in active_enrollments)),
            'total_courses': len(institution_courses),
            'average_completion_rate': round(statistics.mean(completion_rates), 2) if completion_rates else 0,
            'average_grade': round(statistics.mean(institution_grades), 2) if institution_grades else 0,
            'student_satisfaction_score': satisfaction_score,
            'average_time_to_completion_weeks': time_to_completion,
            'retention_rate': self._calculate_retention_rate(institution_id, start_date, end_date),
            'course_success_rate': len([r for r in completion_rates if r >= 70]) / len(completion_rates) * 100 if completion_rates else 0
        }
    
    def _calculate_engagement_metrics(self, institution_id: str, start_date: datetime, end_date: datetime) -> dict:
        """Calculate student engagement metrics"""
        from analytics_dashboard import analytics_manager
        from social_learning import social_manager
        from video_sessions import video_manager
        
        # Learning session frequency
        institution_sessions = []
        for user_id, user_data in analytics_manager.analytics_data.items():
            for session in user_data.get('sessions', {}).values():
                session_date = datetime.fromisoformat(session['timestamp'])
                if start_date <= session_date <= end_date:
                    institution_sessions.append(session)
        
        # Social learning participation
        social_participants = set()
        for challenge in social_manager.challenges.values():
            if start_date <= datetime.fromisoformat(challenge['created_at']) <= end_date:
                social_participants.update(challenge['participants'].keys())
        
        # Video session participation
        video_participants = set()
        for session in video_manager.sessions.values():
            if start_date <= datetime.fromisoformat(session['created_at']) <= end_date:
                video_participants.update(session['participants'])
        
        # Platform usage patterns
        daily_active_users = self._calculate_daily_active_users(institution_id, start_date, end_date)
        
        return {
            'total_learning_sessions': len(institution_sessions),
            'average_session_length_minutes': round(statistics.mean([s['time_spent_minutes'] for s in institution_sessions]), 2) if institution_sessions else 0,
            'social_learning_participation_rate': len(social_participants) / max(daily_active_users, 1) * 100,
            'video_session_participation_rate': len(video_participants) / max(daily_active_users, 1) * 100,
            'daily_active_users': daily_active_users,
            'platform_stickiness': self._calculate_platform_stickiness(institution_id, start_date, end_date),
            'feature_adoption_rates': self._calculate_feature_adoption_rates(institution_id)
        }
    
    def _analyze_learning_outcomes(self, institution_id: str, start_date: datetime, end_date: datetime) -> dict:
        """Analyze learning outcomes and effectiveness"""
        from lms_integration import lms_manager
        from analytics_dashboard import analytics_manager
        
        # Subject performance analysis
        subject_performance = defaultdict(lambda: {'scores': [], 'completion_rates': []})
        
        institution_courses = [c for c in lms_manager.courses.values() 
                             if c.get('institution_id') == institution_id]
        
        for course in institution_courses:
            subject = course['subject_category']
            
            # Get grades for this course
            course_grades = [g['overall_grade'] for g in lms_manager.gradebook.values() 
                           if g['course_id'] == course['id'] and g['overall_grade'] is not None]
            subject_performance[subject]['scores'].extend(course_grades)
            
            # Calculate completion rate
            enrollments = [e for e in lms_manager.enrollments.values() if e['course_id'] == course['id']]
            if enrollments:
                completed = len([e for e in enrollments if e['status'] == 'completed'])
                completion_rate = (completed / len(enrollments)) * 100
                subject_performance[subject]['completion_rates'].append(completion_rate)
        
        # Skill progression tracking
        skill_progression = self._analyze_skill_progression(institution_id)
        
        # Learning efficiency metrics
        efficiency_metrics = self._calculate_learning_efficiency(institution_id)
        
        return {
            'subject_performance_breakdown': {
                subject: {
                    'average_score': round(statistics.mean(data['scores']), 2) if data['scores'] else 0,
                    'average_completion_rate': round(statistics.mean(data['completion_rates']), 2) if data['completion_rates'] else 0,
                    'student_count': len(data['scores'])
                }
                for subject, data in subject_performance.items()
            },
            'skill_progression_analysis': skill_progression,
            'learning_efficiency_metrics': efficiency_metrics,
            'competency_achievements': self._track_competency_achievements(institution_id),
            'learning_path_effectiveness': self._analyze_learning_path_effectiveness(institution_id)
        }
    
    def _calculate_resource_utilization(self, institution_id: str, start_date: datetime, end_date: datetime) -> dict:
        """Calculate resource utilization metrics"""
        from lms_integration import lms_manager
        from video_sessions import video_manager
        
        # Course capacity utilization
        institution_courses = [c for c in lms_manager.courses.values() 
                             if c.get('institution_id') == institution_id]
        
        total_capacity = sum(course['max_students'] for course in institution_courses)
        total_enrolled = 0
        
        for course in institution_courses:
            enrollments = [e for e in lms_manager.enrollments.values() 
                          if e['course_id'] == course['id'] and e['status'] == 'active']
            total_enrolled += len(enrollments)
        
        capacity_utilization = (total_enrolled / total_capacity * 100) if total_capacity > 0 else 0
        
        # Video session utilization
        video_sessions = [s for s in video_manager.sessions.values() 
                         if start_date <= datetime.fromisoformat(s['created_at']) <= end_date]
        
        total_video_capacity = sum(session['max_participants'] for session in video_sessions)
        total_video_participants = sum(len(session['participants']) for session in video_sessions)
        
        video_utilization = (total_video_participants / total_video_capacity * 100) if total_video_capacity > 0 else 0
        
        # Content usage analytics
        content_usage = self._analyze_content_usage(institution_id, start_date, end_date)
        
        return {
            'course_capacity_utilization': round(capacity_utilization, 2),
            'video_session_utilization': round(video_utilization, 2),
            'content_usage_analytics': content_usage,
            'peak_usage_times': self._identify_peak_usage_times(institution_id),
            'resource_efficiency_score': self._calculate_resource_efficiency_score(institution_id)
        }
    
    def _generate_predictive_insights(self, institution_id: str) -> dict:
        """Generate predictive analytics and insights"""
        from lms_integration import lms_manager
        from analytics_dashboard import analytics_manager
        
        # Student at-risk prediction
        at_risk_students = self._identify_at_risk_students(institution_id)
        
        # Enrollment projections
        enrollment_trends = self._calculate_enrollment_trends(institution_id)
        
        # Resource needs forecasting
        resource_forecast = self._forecast_resource_needs(institution_id)
        
        # Success probability modeling
        success_predictions = self._model_success_probability(institution_id)
        
        return {
            'at_risk_students': at_risk_students,
            'enrollment_projections': enrollment_trends,
            'resource_needs_forecast': resource_forecast,
            'success_probability_models': success_predictions,
            'intervention_recommendations': self._generate_intervention_recommendations(at_risk_students)
        }
    
    def _get_benchmark_comparisons(self, institution_id: str) -> dict:
        """Get comparative benchmarks against industry standards"""
        from lms_integration import lms_manager
        
        # Industry benchmarks (would be real data in production)
        industry_benchmarks = {
            'average_completion_rate': 75.0,
            'average_grade': 82.5,
            'student_satisfaction': 88.0,
            'retention_rate': 85.0,
            'time_to_completion_weeks': 14.0
        }
        
        # Calculate institution metrics
        institution_kpis = self._calculate_institutional_kpis(
            institution_id, 
            datetime.now() - timedelta(days=90), 
            datetime.now()
        )
        
        # Compare against benchmarks
        comparisons = {}
        for metric, benchmark_value in industry_benchmarks.items():
            institution_value = institution_kpis.get(metric, 0)
            variance = ((institution_value - benchmark_value) / benchmark_value * 100) if benchmark_value > 0 else 0
            
            comparisons[metric] = {
                'institution_value': institution_value,
                'benchmark_value': benchmark_value,
                'variance_percentage': round(variance, 2),
                'performance': 'above_average' if variance > 5 else 'below_average' if variance < -5 else 'average'
            }
        
        return {
            'industry_comparisons': comparisons,
            'peer_institution_ranking': self._calculate_peer_ranking(institution_id),
            'improvement_opportunities': self._identify_improvement_opportunities(comparisons)
        }
    
    def _generate_executive_summary(self, kpis: dict, engagement: dict, outcomes: dict) -> dict:
        """Generate executive summary with key insights"""
        # Identify key strengths
        strengths = []
        if kpis['average_completion_rate'] >= 80:
            strengths.append("High course completion rates demonstrate strong program effectiveness")
        if engagement['social_learning_participation_rate'] >= 60:
            strengths.append("Excellent social learning adoption drives collaborative learning")
        if kpis['average_grade'] >= 85:
            strengths.append("Students achieving above-average academic performance")
        
        # Identify areas for improvement
        improvements = []
        if kpis['retention_rate'] < 80:
            improvements.append("Student retention requires focused intervention strategies")
        if engagement['platform_stickiness'] < 70:
            improvements.append("Platform engagement could be enhanced through gamification")
        if kpis['average_time_to_completion_weeks'] > 16:
            improvements.append("Course completion timelines exceed optimal targets")
        
        # Strategic recommendations
        recommendations = []
        if kpis['student_satisfaction_score'] < 85:
            recommendations.append("Implement student feedback loops to improve satisfaction")
        if engagement['video_session_participation_rate'] < 40:
            recommendations.append("Expand video session offerings and marketing")
        
        return {
            'key_strengths': strengths,
            'improvement_areas': improvements,
            'strategic_recommendations': recommendations,
            'overall_performance_score': self._calculate_overall_performance_score(kpis, engagement, outcomes),
            'trend_direction': self._determine_trend_direction(kpis),
            'priority_actions': self._prioritize_action_items(improvements, recommendations)
        }
    
    def generate_custom_report(self, institution_id: str, report_config: dict) -> dict:
        """Generate custom report based on configuration"""
        report_id = str(uuid.uuid4())
        
        # Process report configuration
        metrics = report_config.get('metrics', [])
        filters = report_config.get('filters', {})
        time_range = report_config.get('time_range', '30d')
        visualization_type = report_config.get('visualization', 'table')
        
        # Generate data based on selected metrics
        report_data = {}
        for metric in metrics:
            if metric == 'student_performance':
                report_data[metric] = self._get_student_performance_data(institution_id, filters)
            elif metric == 'course_analytics':
                report_data[metric] = self._get_course_analytics_data(institution_id, filters)
            elif metric == 'engagement_trends':
                report_data[metric] = self._get_engagement_trends_data(institution_id, filters)
            elif metric == 'financial_metrics':
                report_data[metric] = self._get_financial_metrics_data(institution_id, filters)
        
        custom_report = {
            'id': report_id,
            'institution_id': institution_id,
            'generated_at': datetime.now().isoformat(),
            'configuration': report_config,
            'data': report_data,
            'summary_statistics': self._calculate_summary_statistics(report_data),
            'visualizations': self._generate_visualization_configs(report_data, visualization_type)
        }
        
        self.custom_reports[report_id] = custom_report
        self._save_json_file(self.custom_reports_file, self.custom_reports)
        
        return custom_report
    
    def _calculate_overall_performance_score(self, kpis: dict, engagement: dict, outcomes: dict) -> float:
        """Calculate weighted overall performance score"""
        scores = []
        
        # Academic performance (30%)
        academic_score = (kpis['average_grade'] / 100) * 100
        scores.append(academic_score * 0.3)
        
        # Completion rates (25%)
        completion_score = kpis['average_completion_rate']
        scores.append(completion_score * 0.25)
        
        # Engagement (25%)
        engagement_score = engagement['platform_stickiness']
        scores.append(engagement_score * 0.25)
        
        # Retention (20%)
        retention_score = kpis['retention_rate']
        scores.append(retention_score * 0.2)
        
        return round(sum(scores), 2)
    
    def _identify_at_risk_students(self, institution_id: str) -> list:
        """Identify students at risk of dropping out or failing"""
        from lms_integration import lms_manager
        from analytics_dashboard import analytics_manager
        
        at_risk_students = []
        
        # Get all students in institution
        institution_courses = [c for c in lms_manager.courses.values() 
                             if c.get('institution_id') == institution_id]
        
        student_ids = set()
        for course in institution_courses:
            enrollments = [e for e in lms_manager.enrollments.values() 
                          if e['course_id'] == course['id'] and e['status'] == 'active']
            student_ids.update(e['student_id'] for e in enrollments)
        
        for student_id in student_ids:
            risk_factors = []
            risk_score = 0
            
            # Check academic performance
            student_grades = [g['overall_grade'] for g in lms_manager.gradebook.values() 
                            if g['student_id'] == student_id and g['overall_grade'] is not None]
            
            if student_grades:
                avg_grade = statistics.mean(student_grades)
                if avg_grade < 70:
                    risk_factors.append("Below average academic performance")
                    risk_score += 30
                elif avg_grade < 80:
                    risk_score += 15
            
            # Check engagement patterns
            if student_id in analytics_manager.user_metrics:
                metrics = analytics_manager.user_metrics[student_id]
                engagement_score = metrics['engagement_metrics']['engagement_score']
                
                if engagement_score < 40:
                    risk_factors.append("Low platform engagement")
                    risk_score += 25
                elif engagement_score < 60:
                    risk_score += 10
                
                # Check learning streak
                if metrics['current_streak'] == 0:
                    risk_factors.append("No recent learning activity")
                    risk_score += 20
            
            # Check assignment submission patterns
            recent_submissions = self._get_recent_submissions(student_id, days=14)
            if len(recent_submissions) == 0:
                risk_factors.append("No recent assignment submissions")
                risk_score += 15
            
            if risk_score >= 50:  # High risk threshold
                at_risk_students.append({
                    'student_id': student_id,
                    'risk_score': risk_score,
                    'risk_factors': risk_factors,
                    'recommended_interventions': self._suggest_interventions(risk_factors)
                })
        
        return sorted(at_risk_students, key=lambda x: x['risk_score'], reverse=True)
    
    def _suggest_interventions(self, risk_factors: list) -> list:
        """Suggest interventions based on risk factors"""
        interventions = []
        
        if "Below average academic performance" in risk_factors:
            interventions.append("Schedule tutoring sessions")
            interventions.append("Provide additional learning resources")
        
        if "Low platform engagement" in risk_factors:
            interventions.append("Send personalized engagement notifications")
            interventions.append("Recommend relevant study groups")
        
        if "No recent learning activity" in risk_factors:
            interventions.append("Direct outreach from instructor")
            interventions.append("Flexible scheduling options")
        
        if "No recent assignment submissions" in risk_factors:
            interventions.append("Assignment deadline extensions")
            interventions.append("One-on-one academic counseling")
        
        return interventions
    
    def _get_recent_submissions(self, student_id: str, days: int = 14) -> list:
        """Get student's recent assignment submissions"""
        from lms_integration import lms_manager
        
        cutoff_date = datetime.now() - timedelta(days=days)
        submissions = []
        
        for assignment in lms_manager.assignments.values():
            for submission in assignment['submissions'].values():
                if (submission['student_id'] == student_id and 
                    datetime.fromisoformat(submission['submitted_at']) >= cutoff_date):
                    submissions.append(submission)
        
        return submissions
    
    # Placeholder methods for complex calculations (would be fully implemented in production)
    def _calculate_retention_rate(self, institution_id: str, start_date: datetime, end_date: datetime) -> float:
        return 82.5  # Placeholder
    
    def _calculate_average_completion_time(self, courses: list) -> float:
        return 12.5  # Placeholder
    
    def _calculate_daily_active_users(self, institution_id: str, start_date: datetime, end_date: datetime) -> int:
        return 150  # Placeholder
    
    def _calculate_platform_stickiness(self, institution_id: str, start_date: datetime, end_date: datetime) -> float:
        return 75.0  # Placeholder
    
    def _calculate_feature_adoption_rates(self, institution_id: str) -> dict:
        return {'video_sessions': 65, 'social_learning': 80, 'analytics': 45}  # Placeholder
    
    def _analyze_skill_progression(self, institution_id: str) -> dict:
        return {'average_progression_rate': 85.0, 'skills_mastered': 120}  # Placeholder
    
    def _calculate_learning_efficiency(self, institution_id: str) -> dict:
        return {'efficiency_score': 78.5, 'time_to_mastery_hours': 15.2}  # Placeholder
    
    def _track_competency_achievements(self, institution_id: str) -> dict:
        return {'competencies_achieved': 85, 'certification_rate': 70.5}  # Placeholder
    
    def _analyze_learning_path_effectiveness(self, institution_id: str) -> dict:
        return {'path_completion_rate': 82.0, 'average_satisfaction': 4.2}  # Placeholder
    
    def _analyze_content_usage(self, institution_id: str, start_date: datetime, end_date: datetime) -> dict:
        return {'most_used_content': 'video_sessions', 'usage_hours': 1250}  # Placeholder
    
    def _identify_peak_usage_times(self, institution_id: str) -> dict:
        return {'peak_hour': 14, 'peak_day': 'Tuesday'}  # Placeholder
    
    def _calculate_resource_efficiency_score(self, institution_id: str) -> float:
        return 76.5  # Placeholder

# Initialize global reporting manager
reporting_manager = ReportingManager()