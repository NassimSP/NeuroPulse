"""
Learning Management System Integration for NeuroPulse
Provides enterprise-grade course management, assignment tracking, and institutional features
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

class CourseStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published" 
    ARCHIVED = "archived"
    SUSPENDED = "suspended"

class AssignmentType(Enum):
    QUIZ = "quiz"
    PROJECT = "project"
    DISCUSSION = "discussion"
    ASSESSMENT = "assessment"
    VIDEO_SESSION = "video_session"

class UserRole(Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"
    TEACHING_ASSISTANT = "teaching_assistant"

class LMSManager:
    def __init__(self):
        self.courses_file = 'lms_courses_data.json'
        self.enrollments_file = 'lms_enrollments_data.json'
        self.assignments_file = 'lms_assignments_data.json'
        self.gradebook_file = 'lms_gradebook_data.json'
        self.institutions_file = 'lms_institutions_data.json'
        self.learning_paths_file = 'lms_learning_paths_data.json'
        
        self.load_data()
    
    def load_data(self):
        """Load LMS data"""
        self.courses = self._load_json_file(self.courses_file, {})
        self.enrollments = self._load_json_file(self.enrollments_file, {})
        self.assignments = self._load_json_file(self.assignments_file, {})
        self.gradebook = self._load_json_file(self.gradebook_file, {})
        self.institutions = self._load_json_file(self.institutions_file, {})
        self.learning_paths = self._load_json_file(self.learning_paths_file, {})
    
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
    
    def create_institution(self, admin_id: str, institution_data: dict) -> str:
        """Create new educational institution"""
        institution_id = str(uuid.uuid4())
        
        institution = {
            'id': institution_id,
            'name': institution_data['name'],
            'domain': institution_data.get('domain'),
            'type': institution_data.get('type', 'university'),  # university, school, corporate, training
            'admin_id': admin_id,
            'created_at': datetime.now().isoformat(),
            'settings': {
                'allow_self_enrollment': institution_data.get('allow_self_enrollment', False),
                'require_approval': institution_data.get('require_approval', True),
                'enable_analytics': institution_data.get('enable_analytics', True),
                'custom_branding': institution_data.get('custom_branding', {}),
                'integration_settings': institution_data.get('integration_settings', {})
            },
            'departments': {},
            'user_roles': {admin_id: UserRole.ADMIN.value},
            'subscription_plan': institution_data.get('subscription_plan', 'basic'),
            'license_count': institution_data.get('license_count', 100),
            'active_users': 1
        }
        
        self.institutions[institution_id] = institution
        self._save_json_file(self.institutions_file, self.institutions)
        
        return institution_id
    
    def create_course(self, instructor_id: str, course_data: dict) -> str:
        """Create new course"""
        course_id = str(uuid.uuid4())
        
        course = {
            'id': course_id,
            'title': course_data['title'],
            'description': course_data.get('description', ''),
            'instructor_id': instructor_id,
            'institution_id': course_data.get('institution_id'),
            'subject_category': course_data['subject_category'],
            'difficulty_level': course_data.get('difficulty_level', 'intermediate'),
            'estimated_duration_hours': course_data.get('estimated_duration_hours', 40),
            'max_students': course_data.get('max_students', 50),
            'status': CourseStatus.DRAFT.value,
            'created_at': datetime.now().isoformat(),
            'start_date': course_data.get('start_date'),
            'end_date': course_data.get('end_date'),
            'enrollment_deadline': course_data.get('enrollment_deadline'),
            'prerequisites': course_data.get('prerequisites', []),
            'learning_objectives': course_data.get('learning_objectives', []),
            'course_modules': [],
            'grading_scheme': course_data.get('grading_scheme', {
                'assignments': 40,
                'quizzes': 30,
                'participation': 20,
                'final_project': 10
            }),
            'passing_grade': course_data.get('passing_grade', 70),
            'certificate_enabled': course_data.get('certificate_enabled', True),
            'auto_enrollment': course_data.get('auto_enrollment', False),
            'tags': course_data.get('tags', []),
            'resources': course_data.get('resources', [])
        }
        
        self.courses[course_id] = course
        self._save_json_file(self.courses_file, self.courses)
        
        return course_id
    
    def add_course_module(self, course_id: str, module_data: dict) -> str:
        """Add module to course"""
        if course_id not in self.courses:
            return None
        
        module_id = str(uuid.uuid4())
        
        module = {
            'id': module_id,
            'title': module_data['title'],
            'description': module_data.get('description', ''),
            'order': module_data.get('order', len(self.courses[course_id]['course_modules']) + 1),
            'topics': module_data.get('topics', []),
            'assignments': [],
            'video_sessions': [],
            'reading_materials': module_data.get('reading_materials', []),
            'estimated_hours': module_data.get('estimated_hours', 4),
            'unlock_requirements': module_data.get('unlock_requirements', []),
            'available_from': module_data.get('available_from'),
            'available_until': module_data.get('available_until')
        }
        
        self.courses[course_id]['course_modules'].append(module)
        self._save_json_file(self.courses_file, self.courses)
        
        return module_id
    
    def create_assignment(self, course_id: str, instructor_id: str, assignment_data: dict) -> str:
        """Create course assignment"""
        assignment_id = str(uuid.uuid4())
        
        assignment = {
            'id': assignment_id,
            'course_id': course_id,
            'module_id': assignment_data.get('module_id'),
            'instructor_id': instructor_id,
            'title': assignment_data['title'],
            'description': assignment_data.get('description', ''),
            'type': assignment_data.get('type', AssignmentType.QUIZ.value),
            'subject_category': assignment_data['subject_category'],
            'topic': assignment_data['topic'],
            'difficulty_level': assignment_data.get('difficulty_level', 'intermediate'),
            'points_possible': assignment_data.get('points_possible', 100),
            'weight': assignment_data.get('weight', 1.0),
            'due_date': assignment_data.get('due_date'),
            'available_from': assignment_data.get('available_from'),
            'available_until': assignment_data.get('available_until'),
            'attempts_allowed': assignment_data.get('attempts_allowed', 3),
            'time_limit_minutes': assignment_data.get('time_limit_minutes'),
            'instructions': assignment_data.get('instructions', ''),
            'rubric': assignment_data.get('rubric', {}),
            'auto_grade': assignment_data.get('auto_grade', True),
            'show_correct_answers': assignment_data.get('show_correct_answers', True),
            'randomize_questions': assignment_data.get('randomize_questions', False),
            'question_bank': assignment_data.get('question_bank', []),
            'question_count': assignment_data.get('question_count', 10),
            'created_at': datetime.now().isoformat(),
            'published': False,
            'submissions': {}
        }
        
        self.assignments[assignment_id] = assignment
        self._save_json_file(self.assignments_file, self.assignments)
        
        return assignment_id
    
    def enroll_student(self, course_id: str, student_id: str, enrollment_data: dict = None) -> bool:
        """Enroll student in course"""
        if course_id not in self.courses:
            return False
        
        course = self.courses[course_id]
        
        # Check enrollment limits
        current_enrollments = len([e for e in self.enrollments.values() 
                                 if e['course_id'] == course_id and e['status'] == 'active'])
        
        if current_enrollments >= course['max_students']:
            return False
        
        enrollment_id = str(uuid.uuid4())
        
        enrollment = {
            'id': enrollment_id,
            'course_id': course_id,
            'student_id': student_id,
            'enrolled_at': datetime.now().isoformat(),
            'status': 'active',  # active, completed, dropped, suspended
            'enrollment_type': enrollment_data.get('enrollment_type', 'standard') if enrollment_data else 'standard',
            'grade': None,
            'completion_percentage': 0,
            'last_activity': datetime.now().isoformat(),
            'module_progress': {},
            'assignment_submissions': {},
            'participation_score': 0,
            'attendance_record': {}
        }
        
        self.enrollments[enrollment_id] = enrollment
        self._save_json_file(self.enrollments_file, self.enrollments)
        
        return True
    
    def submit_assignment(self, assignment_id: str, student_id: str, submission_data: dict) -> str:
        """Submit assignment solution"""
        if assignment_id not in self.assignments:
            return None
        
        assignment = self.assignments[assignment_id]
        submission_id = str(uuid.uuid4())
        
        # Check if student is enrolled in course
        course_enrollment = self._get_student_enrollment(assignment['course_id'], student_id)
        if not course_enrollment:
            return None
        
        # Check attempt limits
        existing_submissions = [s for s in assignment['submissions'].values() 
                              if s['student_id'] == student_id]
        
        if len(existing_submissions) >= assignment['attempts_allowed']:
            return None
        
        submission = {
            'id': submission_id,
            'assignment_id': assignment_id,
            'student_id': student_id,
            'attempt_number': len(existing_submissions) + 1,
            'submitted_at': datetime.now().isoformat(),
            'answers': submission_data.get('answers', {}),
            'time_spent_minutes': submission_data.get('time_spent_minutes', 0),
            'score': None,
            'percentage': None,
            'feedback': '',
            'graded': False,
            'graded_at': None,
            'graded_by': None,
            'late_submission': self._is_late_submission(assignment),
            'plagiarism_check': submission_data.get('plagiarism_check', {}),
            'auto_graded': False
        }
        
        # Auto-grade if enabled and it's a quiz
        if assignment['auto_grade'] and assignment['type'] == AssignmentType.QUIZ.value:
            submission = self._auto_grade_submission(assignment, submission)
        
        assignment['submissions'][submission_id] = submission
        self._save_json_file(self.assignments_file, self.assignments)
        
        # Update gradebook
        self._update_gradebook(assignment['course_id'], student_id, assignment_id, submission)
        
        return submission_id
    
    def _auto_grade_submission(self, assignment: dict, submission: dict) -> dict:
        """Auto-grade quiz submission"""
        correct_answers = 0
        total_questions = len(assignment['question_bank'])
        
        for question_id, student_answer in submission['answers'].items():
            # Find correct answer in question bank
            for question in assignment['question_bank']:
                if question.get('id') == question_id:
                    if question.get('correct_answer') == student_answer:
                        correct_answers += 1
                    break
        
        if total_questions > 0:
            percentage = (correct_answers / total_questions) * 100
            score = (percentage / 100) * assignment['points_possible']
            
            submission['score'] = round(score, 2)
            submission['percentage'] = round(percentage, 2)
            submission['graded'] = True
            submission['auto_graded'] = True
            submission['graded_at'] = datetime.now().isoformat()
            
            # Generate basic feedback
            if percentage >= 90:
                submission['feedback'] = "Excellent work! You've mastered this material."
            elif percentage >= 80:
                submission['feedback'] = "Great job! Strong understanding demonstrated."
            elif percentage >= 70:
                submission['feedback'] = "Good work. Consider reviewing the areas you missed."
            else:
                submission['feedback'] = "Please review the material and consider retaking if attempts remain."
        
        return submission
    
    def _is_late_submission(self, assignment: dict) -> bool:
        """Check if submission is late"""
        if not assignment.get('due_date'):
            return False
        
        due_date = datetime.fromisoformat(assignment['due_date'])
        return datetime.now() > due_date
    
    def _get_student_enrollment(self, course_id: str, student_id: str) -> dict:
        """Get student enrollment in course"""
        for enrollment in self.enrollments.values():
            if (enrollment['course_id'] == course_id and 
                enrollment['student_id'] == student_id and 
                enrollment['status'] == 'active'):
                return enrollment
        return None
    
    def _update_gradebook(self, course_id: str, student_id: str, assignment_id: str, submission: dict):
        """Update gradebook entry"""
        gradebook_key = f"{course_id}_{student_id}"
        
        if gradebook_key not in self.gradebook:
            self.gradebook[gradebook_key] = {
                'course_id': course_id,
                'student_id': student_id,
                'assignments': {},
                'overall_grade': None,
                'letter_grade': None,
                'last_updated': datetime.now().isoformat()
            }
        
        # Update assignment grade
        self.gradebook[gradebook_key]['assignments'][assignment_id] = {
            'score': submission.get('score'),
            'percentage': submission.get('percentage'),
            'submission_id': submission['id'],
            'submitted_at': submission['submitted_at'],
            'late': submission['late_submission']
        }
        
        # Recalculate overall grade
        self._calculate_overall_grade(course_id, student_id)
        
        self._save_json_file(self.gradebook_file, self.gradebook)
    
    def _calculate_overall_grade(self, course_id: str, student_id: str):
        """Calculate student's overall course grade"""
        gradebook_key = f"{course_id}_{student_id}"
        
        if gradebook_key not in self.gradebook:
            return
        
        course = self.courses[course_id]
        grading_scheme = course['grading_scheme']
        student_grades = self.gradebook[gradebook_key]
        
        # Get all course assignments by type
        course_assignments = {aid: assignment for aid, assignment in self.assignments.items() 
                            if assignment['course_id'] == course_id}
        
        # Calculate weighted grade
        total_weighted_score = 0
        total_weight = 0
        
        for category, weight in grading_scheme.items():
            category_assignments = [aid for aid, assignment in course_assignments.items() 
                                  if assignment['type'] == category]
            
            if category_assignments:
                category_scores = []
                for aid in category_assignments:
                    if aid in student_grades['assignments']:
                        score = student_grades['assignments'][aid]['percentage']
                        if score is not None:
                            category_scores.append(score)
                
                if category_scores:
                    category_average = sum(category_scores) / len(category_scores)
                    total_weighted_score += category_average * (weight / 100)
                    total_weight += weight
        
        if total_weight > 0:
            overall_percentage = (total_weighted_score / total_weight) * 100
            student_grades['overall_grade'] = round(overall_percentage, 2)
            student_grades['letter_grade'] = self._calculate_letter_grade(overall_percentage)
            student_grades['last_updated'] = datetime.now().isoformat()
    
    def _calculate_letter_grade(self, percentage: float) -> str:
        """Convert percentage to letter grade"""
        if percentage >= 97: return 'A+'
        elif percentage >= 93: return 'A'
        elif percentage >= 90: return 'A-'
        elif percentage >= 87: return 'B+'
        elif percentage >= 83: return 'B'
        elif percentage >= 80: return 'B-'
        elif percentage >= 77: return 'C+'
        elif percentage >= 73: return 'C'
        elif percentage >= 70: return 'C-'
        elif percentage >= 67: return 'D+'
        elif percentage >= 63: return 'D'
        elif percentage >= 60: return 'D-'
        else: return 'F'
    
    def create_learning_path(self, creator_id: str, path_data: dict) -> str:
        """Create structured learning path"""
        path_id = str(uuid.uuid4())
        
        learning_path = {
            'id': path_id,
            'title': path_data['title'],
            'description': path_data.get('description', ''),
            'creator_id': creator_id,
            'institution_id': path_data.get('institution_id'),
            'target_audience': path_data.get('target_audience', ''),
            'estimated_duration_weeks': path_data.get('estimated_duration_weeks', 12),
            'difficulty_progression': path_data.get('difficulty_progression', 'linear'),
            'prerequisites': path_data.get('prerequisites', []),
            'learning_outcomes': path_data.get('learning_outcomes', []),
            'courses': path_data.get('courses', []),  # Ordered list of course IDs
            'milestones': path_data.get('milestones', []),
            'certificates': path_data.get('certificates', []),
            'created_at': datetime.now().isoformat(),
            'status': 'draft',  # draft, published, archived
            'enrollments': {},
            'success_metrics': path_data.get('success_metrics', {
                'completion_rate_target': 80,
                'average_grade_target': 85,
                'time_to_completion_weeks': 12
            })
        }
        
        self.learning_paths[path_id] = learning_path
        self._save_json_file(self.learning_paths_file, self.learning_paths)
        
        return path_id
    
    def get_student_dashboard(self, student_id: str, institution_id: str = None) -> dict:
        """Get comprehensive student dashboard data"""
        # Get enrollments
        student_enrollments = [e for e in self.enrollments.values() 
                             if e['student_id'] == student_id and e['status'] == 'active']
        
        # Get courses
        enrolled_courses = []
        for enrollment in student_enrollments:
            course = self.courses.get(enrollment['course_id'])
            if course and (not institution_id or course.get('institution_id') == institution_id):
                course_data = course.copy()
                course_data['enrollment'] = enrollment
                
                # Get gradebook data
                gradebook_key = f"{course['id']}_{student_id}"
                course_data['grades'] = self.gradebook.get(gradebook_key, {})
                
                enrolled_courses.append(course_data)
        
        # Get upcoming assignments
        upcoming_assignments = []
        for course in enrolled_courses:
            course_assignments = [a for a in self.assignments.values() 
                                if a['course_id'] == course['id'] and a['published']]
            
            for assignment in course_assignments:
                if assignment.get('due_date'):
                    due_date = datetime.fromisoformat(assignment['due_date'])
                    if due_date > datetime.now():
                        assignment_data = assignment.copy()
                        assignment_data['course_title'] = course['title']
                        upcoming_assignments.append(assignment_data)
        
        # Sort by due date
        upcoming_assignments.sort(key=lambda x: x['due_date'])
        
        return {
            'enrolled_courses': enrolled_courses,
            'upcoming_assignments': upcoming_assignments[:5],  # Next 5 assignments
            'overall_progress': self._calculate_student_progress(student_id),
            'achievements': self._get_student_achievements(student_id),
            'learning_paths': self._get_student_learning_paths(student_id)
        }
    
    def get_instructor_dashboard(self, instructor_id: str, institution_id: str = None) -> dict:
        """Get comprehensive instructor dashboard data"""
        # Get instructor courses
        instructor_courses = [c for c in self.courses.values() 
                            if c['instructor_id'] == instructor_id and 
                            (not institution_id or c.get('institution_id') == institution_id)]
        
        # Get course statistics
        course_stats = []
        for course in instructor_courses:
            enrollments = [e for e in self.enrollments.values() 
                          if e['course_id'] == course['id'] and e['status'] == 'active']
            
            assignments = [a for a in self.assignments.values() 
                          if a['course_id'] == course['id']]
            
            # Calculate average grade
            gradebook_entries = [g for g in self.gradebook.values() 
                               if g['course_id'] == course['id'] and g['overall_grade'] is not None]
            
            avg_grade = sum(g['overall_grade'] for g in gradebook_entries) / len(gradebook_entries) if gradebook_entries else 0
            
            course_stats.append({
                'course': course,
                'enrollment_count': len(enrollments),
                'assignment_count': len(assignments),
                'average_grade': round(avg_grade, 2),
                'completion_rate': self._calculate_course_completion_rate(course['id'])
            })
        
        # Get pending grading
        pending_grading = []
        for course in instructor_courses:
            course_assignments = [a for a in self.assignments.values() 
                                if a['course_id'] == course['id'] and not a['auto_grade']]
            
            for assignment in course_assignments:
                ungraded_submissions = [s for s in assignment['submissions'].values() 
                                      if not s['graded']]
                
                if ungraded_submissions:
                    pending_grading.append({
                        'assignment': assignment,
                        'course_title': course['title'],
                        'ungraded_count': len(ungraded_submissions)
                    })
        
        return {
            'course_statistics': course_stats,
            'pending_grading': pending_grading,
            'total_students': sum(cs['enrollment_count'] for cs in course_stats),
            'average_course_grade': round(sum(cs['average_grade'] for cs in course_stats) / len(course_stats), 2) if course_stats else 0
        }
    
    def _calculate_student_progress(self, student_id: str) -> dict:
        """Calculate overall student progress metrics"""
        enrollments = [e for e in self.enrollments.values() 
                      if e['student_id'] == student_id and e['status'] == 'active']
        
        if not enrollments:
            return {'courses_completed': 0, 'average_grade': 0, 'total_courses': 0}
        
        completed_courses = len([e for e in enrollments if e['status'] == 'completed'])
        
        # Calculate average grade across all courses
        gradebook_entries = [g for g in self.gradebook.values() 
                           if g['student_id'] == student_id and g['overall_grade'] is not None]
        
        avg_grade = sum(g['overall_grade'] for g in gradebook_entries) / len(gradebook_entries) if gradebook_entries else 0
        
        return {
            'courses_completed': completed_courses,
            'courses_in_progress': len(enrollments) - completed_courses,
            'total_courses': len(enrollments),
            'average_grade': round(avg_grade, 2)
        }
    
    def _get_student_achievements(self, student_id: str) -> list:
        """Get student achievements and badges"""
        achievements = []
        
        # Course completion badges
        completed_courses = [e for e in self.enrollments.values() 
                           if e['student_id'] == student_id and e['status'] == 'completed']
        
        if len(completed_courses) >= 1:
            achievements.append({'type': 'course_completion', 'title': 'First Course Complete'})
        
        if len(completed_courses) >= 5:
            achievements.append({'type': 'course_completion', 'title': 'Dedicated Learner'})
        
        # Grade-based achievements
        gradebook_entries = [g for g in self.gradebook.values() 
                           if g['student_id'] == student_id and g['overall_grade'] is not None]
        
        high_grades = [g for g in gradebook_entries if g['overall_grade'] >= 90]
        if len(high_grades) >= 3:
            achievements.append({'type': 'academic_excellence', 'title': 'High Achiever'})
        
        return achievements
    
    def _get_student_learning_paths(self, student_id: str) -> list:
        """Get student's learning path progress"""
        enrolled_paths = []
        
        for path in self.learning_paths.values():
            if student_id in path['enrollments']:
                path_data = path.copy()
                path_data['progress'] = self._calculate_path_progress(path['id'], student_id)
                enrolled_paths.append(path_data)
        
        return enrolled_paths
    
    def _calculate_path_progress(self, path_id: str, student_id: str) -> dict:
        """Calculate learning path progress for student"""
        path = self.learning_paths.get(path_id)
        if not path:
            return {}
        
        completed_courses = 0
        total_courses = len(path['courses'])
        
        for course_id in path['courses']:
            enrollment = self._get_student_enrollment(course_id, student_id)
            if enrollment and enrollment['status'] == 'completed':
                completed_courses += 1
        
        completion_percentage = (completed_courses / total_courses * 100) if total_courses > 0 else 0
        
        return {
            'completed_courses': completed_courses,
            'total_courses': total_courses,
            'completion_percentage': round(completion_percentage, 2)
        }
    
    def _calculate_course_completion_rate(self, course_id: str) -> float:
        """Calculate course completion rate"""
        enrollments = [e for e in self.enrollments.values() 
                      if e['course_id'] == course_id]
        
        if not enrollments:
            return 0
        
        completed = len([e for e in enrollments if e['status'] == 'completed'])
        return round((completed / len(enrollments)) * 100, 2)

# Initialize global LMS manager
lms_manager = LMSManager()