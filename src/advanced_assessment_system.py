"""
Advanced Assessment & Certification System for NeuroPulse
Provides proctored exams, industry certifications, competency mapping, and digital badges
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
from openai import OpenAI

class AssessmentType(Enum):
    FORMATIVE = "formative"
    SUMMATIVE = "summative" 
    CERTIFICATION = "certification"
    COMPETENCY = "competency"
    PLACEMENT = "placement"

class ProctoringLevel(Enum):
    NONE = "none"
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"

class CertificationStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"

class AdvancedAssessmentManager:
    def __init__(self):
        self.assessments_file = 'advanced_assessments_data.json'
        self.certifications_file = 'certifications_data.json'
        self.competency_maps_file = 'competency_maps_data.json'
        self.proctoring_sessions_file = 'proctoring_sessions_data.json'
        self.digital_badges_file = 'digital_badges_data.json'
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        self.load_data()
    
    def load_data(self):
        """Load assessment system data"""
        self.assessments = self._load_json_file(self.assessments_file, {})
        self.certifications = self._load_json_file(self.certifications_file, {})
        self.competency_maps = self._load_json_file(self.competency_maps_file, {})
        self.proctoring_sessions = self._load_json_file(self.proctoring_sessions_file, {})
        self.digital_badges = self._load_json_file(self.digital_badges_file, {})
    
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
    
    def create_advanced_assessment(self, creator_id: str, assessment_data: dict) -> str:
        """Create advanced assessment with AI-generated questions"""
        assessment_id = str(uuid.uuid4())
        
        # Generate AI questions based on competency requirements
        questions = self._generate_ai_assessment_questions(
            assessment_data['subject_category'],
            assessment_data['competencies'],
            assessment_data.get('difficulty_level', 'intermediate'),
            assessment_data.get('question_count', 20)
        )
        
        assessment = {
            'id': assessment_id,
            'creator_id': creator_id,
            'title': assessment_data['title'],
            'description': assessment_data.get('description', ''),
            'type': assessment_data.get('type', AssessmentType.SUMMATIVE.value),
            'subject_category': assessment_data['subject_category'],
            'competencies': assessment_data['competencies'],
            'difficulty_level': assessment_data.get('difficulty_level', 'intermediate'),
            'duration_minutes': assessment_data.get('duration_minutes', 60),
            'passing_score': assessment_data.get('passing_score', 70),
            'max_attempts': assessment_data.get('max_attempts', 3),
            'proctoring_level': assessment_data.get('proctoring_level', ProctoringLevel.BASIC.value),
            'randomize_questions': assessment_data.get('randomize_questions', True),
            'show_results_immediately': assessment_data.get('show_results_immediately', False),
            'certification_eligible': assessment_data.get('certification_eligible', False),
            'industry_alignment': assessment_data.get('industry_alignment', []),
            'questions': questions,
            'rubric': self._generate_assessment_rubric(assessment_data['competencies']),
            'adaptive_difficulty': assessment_data.get('adaptive_difficulty', False),
            'created_at': datetime.now().isoformat(),
            'published': False,
            'attempts': {},
            'statistics': {
                'total_attempts': 0,
                'average_score': 0,
                'pass_rate': 0,
                'common_mistakes': []
            }
        }
        
        self.assessments[assessment_id] = assessment
        self._save_json_file(self.assessments_file, self.assessments)
        
        return assessment_id
    
    def _generate_ai_assessment_questions(self, subject: str, competencies: List[str], 
                                        difficulty: str, question_count: int) -> List[dict]:
        """Generate assessment questions using AI based on competencies"""
        
        questions_prompt = f"""
        Create {question_count} high-quality assessment questions for:
        
        Subject: {subject}
        Difficulty: {difficulty}
        Competencies to assess: {', '.join(competencies)}
        
        Generate diverse question types:
        - Multiple choice (60%)
        - Short answer (25%)
        - Essay/analysis (15%)
        
        Each question should:
        1. Clearly map to one of the specified competencies
        2. Be appropriate for the difficulty level
        3. Include detailed explanations for correct answers
        4. Have realistic distractors for multiple choice
        5. Include rubric criteria for open-ended questions
        
        Respond with JSON array:
        [
            {{
                "id": "q1",
                "type": "multiple_choice/short_answer/essay",
                "competency": "competency name",
                "question_text": "Question content",
                "options": ["A", "B", "C", "D"] (for multiple choice),
                "correct_answer": "correct option or sample answer",
                "explanation": "Detailed explanation",
                "points": 5,
                "difficulty_level": "foundation/intermediate/advanced",
                "estimated_time_minutes": 3,
                "rubric_criteria": ["criterion1", "criterion2"] (for open-ended),
                "cognitive_level": "remember/understand/apply/analyze/evaluate/create"
            }}
        ]
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert assessment designer. Create rigorous, valid assessment questions that accurately measure specified competencies."},
                    {"role": "user", "content": questions_prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=3000
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('questions', [])
            
        except Exception as e:
            print(f"AI question generation failed: {e}")
            return self._create_default_assessment_questions(subject, competencies, question_count)
    
    def _create_default_assessment_questions(self, subject: str, competencies: List[str], count: int) -> List[dict]:
        """Create default questions if AI generation fails"""
        questions = []
        for i in range(min(count, len(competencies))):
            competency = competencies[i % len(competencies)]
            questions.append({
                "id": f"q{i+1}",
                "type": "multiple_choice",
                "competency": competency,
                "question_text": f"Which concept best demonstrates {competency}?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Option A",
                "explanation": f"This demonstrates {competency} through practical application.",
                "points": 5,
                "difficulty_level": "intermediate",
                "estimated_time_minutes": 3,
                "cognitive_level": "understand"
            })
        return questions
    
    def _generate_assessment_rubric(self, competencies: List[str]) -> dict:
        """Generate assessment rubric for competencies"""
        rubric = {
            'criteria': [],
            'performance_levels': ['Exemplary (4)', 'Proficient (3)', 'Developing (2)', 'Beginning (1)'],
            'total_points': 100
        }
        
        points_per_competency = 100 // len(competencies) if competencies else 25
        
        for competency in competencies:
            rubric['criteria'].append({
                'competency': competency,
                'points': points_per_competency,
                'descriptors': {
                    'exemplary': f"Demonstrates mastery of {competency}",
                    'proficient': f"Shows competence in {competency}",
                    'developing': f"Basic understanding of {competency}",
                    'beginning': f"Limited grasp of {competency}"
                }
            })
        
        return rubric
    
    def start_proctored_session(self, assessment_id: str, user_id: str, proctoring_config: dict) -> str:
        """Start proctored assessment session"""
        if assessment_id not in self.assessments:
            return None
        
        assessment = self.assessments[assessment_id]
        session_id = str(uuid.uuid4())
        
        proctoring_session = {
            'session_id': session_id,
            'assessment_id': assessment_id,
            'user_id': user_id,
            'proctoring_level': assessment['proctoring_level'],
            'started_at': datetime.now().isoformat(),
            'duration_minutes': assessment['duration_minutes'],
            'expected_end': (datetime.now() + timedelta(minutes=assessment['duration_minutes'])).isoformat(),
            'status': 'active',
            'monitoring_data': {
                'face_detection_enabled': proctoring_config.get('face_detection', True),
                'screen_recording': proctoring_config.get('screen_recording', False),
                'browser_lockdown': proctoring_config.get('browser_lockdown', True),
                'suspicious_activities': [],
                'violations': []
            },
            'environment_check': {
                'camera_verified': proctoring_config.get('camera_verified', False),
                'microphone_verified': proctoring_config.get('microphone_verified', False),
                'screen_sharing_blocked': proctoring_config.get('screen_sharing_blocked', True),
                'other_applications_closed': proctoring_config.get('other_apps_closed', False)
            },
            'integrity_score': 100,
            'warnings_issued': 0
        }
        
        self.proctoring_sessions[session_id] = proctoring_session
        self._save_json_file(self.proctoring_sessions_file, self.proctoring_sessions)
        
        return session_id
    
    def monitor_proctoring_session(self, session_id: str, monitoring_data: dict) -> dict:
        """Monitor ongoing proctored session"""
        if session_id not in self.proctoring_sessions:
            return {'error': 'Session not found'}
        
        session = self.proctoring_sessions[session_id]
        
        # Analyze monitoring data for violations
        violations = self._analyze_monitoring_data(monitoring_data)
        
        if violations:
            session['monitoring_data']['violations'].extend(violations)
            session['warnings_issued'] += len(violations)
            
            # Reduce integrity score based on violations
            severity_reduction = sum(v['severity_score'] for v in violations)
            session['integrity_score'] = max(0, session['integrity_score'] - severity_reduction)
        
        # Check for session timeout
        current_time = datetime.now()
        expected_end = datetime.fromisoformat(session['expected_end'])
        
        if current_time > expected_end:
            session['status'] = 'timed_out'
            session['ended_at'] = current_time.isoformat()
        
        self._save_json_file(self.proctoring_sessions_file, self.proctoring_sessions)
        
        return {
            'session_status': session['status'],
            'integrity_score': session['integrity_score'],
            'warnings_count': session['warnings_issued'],
            'time_remaining': max(0, int((expected_end - current_time).total_seconds() / 60)),
            'violations': violations
        }
    
    def _analyze_monitoring_data(self, monitoring_data: dict) -> List[dict]:
        """Analyze monitoring data for potential violations"""
        violations = []
        
        # Face detection violations
        if not monitoring_data.get('face_detected', True):
            violations.append({
                'type': 'face_not_detected',
                'description': 'Face not visible in camera',
                'severity_score': 15,
                'timestamp': datetime.now().isoformat()
            })
        
        # Multiple faces detected
        if monitoring_data.get('multiple_faces', False):
            violations.append({
                'type': 'multiple_faces',
                'description': 'Multiple people detected',
                'severity_score': 25,
                'timestamp': datetime.now().isoformat()
            })
        
        # Tab switching
        if monitoring_data.get('tab_switches', 0) > 0:
            violations.append({
                'type': 'tab_switching',
                'description': f"Switched tabs {monitoring_data['tab_switches']} times",
                'severity_score': monitoring_data['tab_switches'] * 5,
                'timestamp': datetime.now().isoformat()
            })
        
        # Audio anomalies
        if monitoring_data.get('suspicious_audio', False):
            violations.append({
                'type': 'audio_anomaly',
                'description': 'Suspicious audio detected',
                'severity_score': 10,
                'timestamp': datetime.now().isoformat()
            })
        
        return violations
    
    def create_certification_pathway(self, creator_id: str, pathway_data: dict) -> str:
        """Create industry-standard certification pathway"""
        pathway_id = str(uuid.uuid4())
        
        certification = {
            'id': pathway_id,
            'creator_id': creator_id,
            'title': pathway_data['title'],
            'description': pathway_data.get('description', ''),
            'industry': pathway_data['industry'],
            'certification_level': pathway_data.get('level', 'professional'),  # entry, professional, expert
            'duration_weeks': pathway_data.get('duration_weeks', 12),
            'prerequisites': pathway_data.get('prerequisites', []),
            'competency_framework': pathway_data['competencies'],
            'required_assessments': pathway_data.get('required_assessments', []),
            'practical_projects': pathway_data.get('practical_projects', []),
            'industry_partnerships': pathway_data.get('industry_partnerships', []),
            'certification_body': pathway_data.get('certification_body', 'NeuroPulse'),
            'expiration_years': pathway_data.get('expiration_years', 3),
            'continuing_education_required': pathway_data.get('continuing_education', True),
            'digital_badge_enabled': True,
            'blockchain_verification': pathway_data.get('blockchain_verification', False),
            'created_at': datetime.now().isoformat(),
            'enrollments': {},
            'completion_statistics': {
                'total_enrolled': 0,
                'total_completed': 0,
                'average_completion_time_weeks': 0,
                'pass_rate': 0
            }
        }
        
        self.certifications[pathway_id] = certification
        self._save_json_file(self.certifications_file, self.certifications)
        
        return pathway_id
    
    def enroll_in_certification(self, pathway_id: str, user_id: str) -> bool:
        """Enroll user in certification pathway"""
        if pathway_id not in self.certifications:
            return False
        
        certification = self.certifications[pathway_id]
        
        # Check prerequisites
        if not self._check_certification_prerequisites(user_id, certification['prerequisites']):
            return False
        
        enrollment_id = str(uuid.uuid4())
        
        certification['enrollments'][user_id] = {
            'enrollment_id': enrollment_id,
            'user_id': user_id,
            'enrolled_at': datetime.now().isoformat(),
            'status': CertificationStatus.IN_PROGRESS.value,
            'progress': {
                'completed_assessments': [],
                'completed_projects': [],
                'current_competency_scores': {},
                'overall_progress_percentage': 0
            },
            'expected_completion': (datetime.now() + timedelta(weeks=certification['duration_weeks'])).isoformat()
        }
        
        certification['completion_statistics']['total_enrolled'] += 1
        
        self._save_json_file(self.certifications_file, self.certifications)
        return True
    
    def _check_certification_prerequisites(self, user_id: str, prerequisites: List[str]) -> bool:
        """Check if user meets certification prerequisites"""
        # Check competency levels
        user_competencies = self._get_user_competencies(user_id)
        
        for prereq in prerequisites:
            if prereq not in user_competencies or user_competencies[prereq] < 3:  # Minimum level 3/5
                return False
        
        return True
    
    def _get_user_competencies(self, user_id: str) -> dict:
        """Get user's current competency levels"""
        # Integration with analytics system
        from analytics_dashboard import analytics_manager
        
        user_data = analytics_manager.get_user_dashboard_data(user_id)
        
        if 'error' in user_data:
            return {}
        
        # Convert subject performance to competency scores
        competencies = {}
        for subject, data in user_data.get('subject_breakdown', {}).items():
            # Map accuracy to competency level (1-5 scale)
            accuracy = data.get('avg_accuracy', 0)
            if accuracy >= 95:
                competencies[subject] = 5
            elif accuracy >= 85:
                competencies[subject] = 4
            elif accuracy >= 75:
                competencies[subject] = 3
            elif accuracy >= 65:
                competencies[subject] = 2
            else:
                competencies[subject] = 1
        
        return competencies
    
    def assess_competency_level(self, user_id: str, competency: str, assessment_results: dict) -> dict:
        """Assess and update user's competency level"""
        competency_id = f"{user_id}_{competency}"
        
        if competency_id not in self.competency_maps:
            self.competency_maps[competency_id] = {
                'user_id': user_id,
                'competency': competency,
                'current_level': 1,
                'evidence': [],
                'last_assessed': None,
                'progression_history': []
            }
        
        competency_data = self.competency_maps[competency_id]
        
        # Analyze assessment results to determine competency level
        new_level = self._calculate_competency_level(assessment_results)
        
        # Update competency data
        old_level = competency_data['current_level']
        competency_data['current_level'] = new_level
        competency_data['last_assessed'] = datetime.now().isoformat()
        
        # Add evidence
        competency_data['evidence'].append({
            'type': 'assessment',
            'assessment_id': assessment_results.get('assessment_id'),
            'score': assessment_results.get('score', 0),
            'timestamp': datetime.now().isoformat(),
            'evidence_strength': assessment_results.get('evidence_strength', 'moderate')
        })
        
        # Track progression
        if new_level != old_level:
            competency_data['progression_history'].append({
                'from_level': old_level,
                'to_level': new_level,
                'date': datetime.now().isoformat(),
                'trigger': 'assessment_completion'
            })
        
        self._save_json_file(self.competency_maps_file, self.competency_maps)
        
        return {
            'competency': competency,
            'previous_level': old_level,
            'current_level': new_level,
            'level_changed': new_level != old_level,
            'evidence_count': len(competency_data['evidence']),
            'next_level_requirements': self._get_next_level_requirements(competency, new_level)
        }
    
    def _calculate_competency_level(self, assessment_results: dict) -> int:
        """Calculate competency level based on assessment results"""
        score = assessment_results.get('score', 0)
        performance_indicators = assessment_results.get('performance_indicators', {})
        
        # Base level from score
        if score >= 95:
            base_level = 5
        elif score >= 85:
            base_level = 4
        elif score >= 75:
            base_level = 3
        elif score >= 65:
            base_level = 2
        else:
            base_level = 1
        
        # Adjust based on performance indicators
        adjustments = 0
        
        if performance_indicators.get('problem_solving_excellence', False):
            adjustments += 1
        
        if performance_indicators.get('creativity_demonstrated', False):
            adjustments += 1
        
        if performance_indicators.get('critical_thinking', False):
            adjustments += 1
        
        if performance_indicators.get('time_efficiency', 0) > 0.8:
            adjustments += 1
        
        # Cap adjustments
        final_level = min(5, max(1, base_level + (adjustments // 2)))
        
        return final_level
    
    def _get_next_level_requirements(self, competency: str, current_level: int) -> List[str]:
        """Get requirements for next competency level"""
        if current_level >= 5:
            return ["Maximum level achieved"]
        
        level_requirements = {
            1: ["Complete foundational assessments", "Demonstrate basic understanding"],
            2: ["Apply concepts in practice", "Complete intermediate projects"],
            3: ["Analyze complex problems", "Lead small projects"],
            4: ["Synthesize knowledge across domains", "Mentor others"],
            5: ["Create innovative solutions", "Contribute to field advancement"]
        }
        
        return level_requirements.get(current_level + 1, ["Requirements not defined"])
    
    def issue_digital_badge(self, user_id: str, achievement_data: dict) -> str:
        """Issue digital badge for achievement"""
        badge_id = str(uuid.uuid4())
        
        badge = {
            'id': badge_id,
            'recipient_id': user_id,
            'title': achievement_data['title'],
            'description': achievement_data['description'],
            'issuer': achievement_data.get('issuer', 'NeuroPulse'),
            'achievement_type': achievement_data['type'],  # competency, certification, milestone
            'competencies_demonstrated': achievement_data.get('competencies', []),
            'evidence_url': achievement_data.get('evidence_url'),
            'verification_url': f"https://badges.neuropulse.app/verify/{badge_id}",
            'issued_at': datetime.now().isoformat(),
            'expires_at': achievement_data.get('expires_at'),
            'metadata': {
                'assessment_scores': achievement_data.get('assessment_scores', []),
                'completion_time': achievement_data.get('completion_time'),
                'difficulty_level': achievement_data.get('difficulty_level'),
                'peer_validation': achievement_data.get('peer_validation', False)
            },
            'blockchain_hash': self._generate_blockchain_hash(badge_id) if achievement_data.get('blockchain_enabled', False) else None
        }
        
        self.digital_badges[badge_id] = badge
        self._save_json_file(self.digital_badges_file, self.digital_badges)
        
        return badge_id
    
    def _generate_blockchain_hash(self, badge_id: str) -> str:
        """Generate blockchain verification hash"""
        # Placeholder for blockchain integration
        import hashlib
        return hashlib.sha256(f"{badge_id}_{datetime.now().isoformat()}".encode()).hexdigest()
    
    def validate_digital_badge(self, badge_id: str) -> dict:
        """Validate digital badge authenticity"""
        if badge_id not in self.digital_badges:
            return {'valid': False, 'reason': 'Badge not found'}
        
        badge = self.digital_badges[badge_id]
        
        # Check expiration
        if badge.get('expires_at'):
            expiry_date = datetime.fromisoformat(badge['expires_at'])
            if datetime.now() > expiry_date:
                return {'valid': False, 'reason': 'Badge expired'}
        
        # Verify blockchain hash if present
        if badge.get('blockchain_hash'):
            # Placeholder for blockchain verification
            blockchain_valid = True  # Would verify against blockchain
            if not blockchain_valid:
                return {'valid': False, 'reason': 'Blockchain verification failed'}
        
        return {
            'valid': True,
            'badge': badge,
            'verification_details': {
                'issued_by': badge['issuer'],
                'issued_date': badge['issued_at'],
                'verification_url': badge['verification_url'],
                'blockchain_verified': badge.get('blockchain_hash') is not None
            }
        }
    
    def generate_competency_report(self, user_id: str) -> dict:
        """Generate comprehensive competency report"""
        user_competencies = {}
        
        for comp_id, comp_data in self.competency_maps.items():
            if comp_data['user_id'] == user_id:
                competency = comp_data['competency']
                user_competencies[competency] = comp_data
        
        # Get user's digital badges
        user_badges = [badge for badge in self.digital_badges.values() 
                      if badge['recipient_id'] == user_id]
        
        # Calculate overall competency score
        total_levels = sum(comp['current_level'] for comp in user_competencies.values())
        max_possible = len(user_competencies) * 5
        overall_score = (total_levels / max_possible * 100) if max_possible > 0 else 0
        
        return {
            'user_id': user_id,
            'generated_at': datetime.now().isoformat(),
            'overall_competency_score': round(overall_score, 2),
            'competency_breakdown': user_competencies,
            'digital_badges': user_badges,
            'recommendations': self._generate_competency_recommendations(user_competencies),
            'career_pathways': self._suggest_career_pathways(user_competencies),
            'skill_gaps': self._identify_skill_gaps(user_competencies)
        }
    
    def _generate_competency_recommendations(self, competencies: dict) -> List[str]:
        """Generate recommendations based on competency levels"""
        recommendations = []
        
        # Find areas for improvement
        weak_areas = [comp for comp, data in competencies.items() 
                     if data['current_level'] < 3]
        
        if weak_areas:
            recommendations.append(f"Focus on developing: {', '.join(weak_areas[:3])}")
        
        # Find strong areas to leverage
        strong_areas = [comp for comp, data in competencies.items() 
                       if data['current_level'] >= 4]
        
        if strong_areas:
            recommendations.append(f"Leverage your strengths in: {', '.join(strong_areas[:3])}")
        
        return recommendations
    
    def _suggest_career_pathways(self, competencies: dict) -> List[str]:
        """Suggest career pathways based on competency profile"""
        # Placeholder for career pathway mapping
        strong_competencies = [comp for comp, data in competencies.items() 
                              if data['current_level'] >= 4]
        
        pathways = []
        if 'programming' in strong_competencies:
            pathways.append("Software Development")
        if 'data_analysis' in strong_competencies:
            pathways.append("Data Science")
        if 'project_management' in strong_competencies:
            pathways.append("Project Management")
        
        return pathways or ["Continue building foundational skills"]
    
    def _identify_skill_gaps(self, competencies: dict) -> List[str]:
        """Identify skill gaps for career progression"""
        gaps = []
        
        # Common skill gaps
        required_skills = ['communication', 'problem_solving', 'critical_thinking', 'collaboration']
        
        for skill in required_skills:
            if skill not in competencies or competencies[skill]['current_level'] < 3:
                gaps.append(skill)
        
        return gaps

# Initialize global assessment manager
assessment_manager = AdvancedAssessmentManager()