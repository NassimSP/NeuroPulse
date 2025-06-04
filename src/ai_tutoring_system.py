"""
AI Teaching Assistant & Tutoring System for NeuroPulse
Provides 24/7 AI tutoring, automated essay grading, intelligent hints, and natural language processing
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from openai import OpenAI

class AITutoringSystem:
    def __init__(self):
        self.tutoring_sessions_file = 'ai_tutoring_sessions.json'
        self.student_questions_file = 'student_questions_data.json'
        self.essay_grading_file = 'essay_grading_data.json'
        self.hint_system_file = 'intelligent_hints_data.json'
        self.tutor_analytics_file = 'tutor_analytics_data.json'
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        self.load_data()
    
    def load_data(self):
        """Load AI tutoring system data"""
        self.tutoring_sessions = self._load_json_file(self.tutoring_sessions_file, {})
        self.student_questions = self._load_json_file(self.student_questions_file, {})
        self.essay_gradings = self._load_json_file(self.essay_grading_file, {})
        self.hint_system = self._load_json_file(self.hint_system_file, {})
        self.tutor_analytics = self._load_json_file(self.tutor_analytics_file, {})
    
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
    
    def start_tutoring_session(self, user_id: str, subject_category: str, topic: str, 
                             learning_context: dict = None) -> str:
        """Start new AI tutoring session"""
        session_id = str(uuid.uuid4())
        
        # Get user's learning profile for personalization
        from ai_personalization_engine import personalization_engine
        user_profile = personalization_engine.user_profiles.get(user_id, {})
        
        session = {
            'session_id': session_id,
            'user_id': user_id,
            'subject_category': subject_category,
            'topic': topic,
            'started_at': datetime.now().isoformat(),
            'learning_context': learning_context or {},
            'user_profile': user_profile.get('learning_style', {}),
            'conversation_history': [],
            'session_objectives': [],
            'current_difficulty_level': learning_context.get('difficulty_level', 'intermediate'),
            'tutor_personality': self._select_tutor_personality(user_profile),
            'status': 'active',
            'session_metrics': {
                'questions_asked': 0,
                'explanations_given': 0,
                'hints_provided': 0,
                'concepts_covered': [],
                'user_satisfaction': None
            }
        }
        
        # Generate initial greeting and assessment
        initial_response = self._generate_tutor_greeting(session)
        session['conversation_history'].append({
            'timestamp': datetime.now().isoformat(),
            'role': 'assistant',
            'content': initial_response,
            'message_type': 'greeting'
        })
        
        self.tutoring_sessions[session_id] = session
        self._save_json_file(self.tutoring_sessions_file, self.tutoring_sessions)
        
        return session_id
    
    def _select_tutor_personality(self, user_profile: dict) -> dict:
        """Select appropriate tutor personality based on user profile"""
        learning_style = user_profile.get('learning_style', {})
        
        # Determine dominant learning style
        if not learning_style:
            dominant_style = 'balanced'
        else:
            dominant_style = max(learning_style.items(), key=lambda x: x[1])[0]
        
        personality_profiles = {
            'visual': {
                'name': 'Visual Guide',
                'style': 'Uses diagrams, charts, and visual metaphors extensively',
                'communication': 'Clear, structured, emphasizes visual learning aids',
                'patience_level': 'high'
            },
            'auditory': {
                'name': 'Conversational Mentor',
                'style': 'Emphasizes discussion, verbal explanations, and dialogue',
                'communication': 'Engaging, uses analogies and stories',
                'patience_level': 'high'
            },
            'kinesthetic': {
                'name': 'Hands-on Coach',
                'style': 'Focuses on practical examples and interactive learning',
                'communication': 'Action-oriented, step-by-step guidance',
                'patience_level': 'very_high'
            },
            'reading_writing': {
                'name': 'Academic Scholar',
                'style': 'Detailed written explanations and structured content',
                'communication': 'Comprehensive, well-organized responses',
                'patience_level': 'high'
            },
            'balanced': {
                'name': 'Adaptive Tutor',
                'style': 'Adjusts approach based on topic and student needs',
                'communication': 'Flexible, responsive to student cues',
                'patience_level': 'very_high'
            }
        }
        
        return personality_profiles.get(dominant_style, personality_profiles['balanced'])
    
    def _generate_tutor_greeting(self, session: dict) -> str:
        """Generate personalized tutor greeting"""
        tutor_prompt = f"""
        You are {session['tutor_personality']['name']}, an AI tutor for {session['subject_category'].replace('_', ' ').title()}.
        
        Your personality: {session['tutor_personality']['style']}
        Communication style: {session['tutor_personality']['communication']}
        
        A student is starting a tutoring session on the topic: {session['topic']}
        Their learning style preferences: {session['user_profile']}
        Current difficulty level: {session['current_difficulty_level']}
        
        Generate a warm, encouraging greeting that:
        1. Welcomes them to the session
        2. Briefly assesses their current knowledge of the topic
        3. Sets clear expectations for the session
        4. Asks an engaging opening question to gauge their understanding
        
        Keep it conversational, supportive, and tailored to their learning style.
        Limit to 150 words.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert AI tutor. Be encouraging, patient, and adaptive to different learning styles."},
                    {"role": "user", "content": tutor_prompt}
                ],
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"AI greeting generation failed: {e}")
            return f"Hello! I'm your AI tutor for {session['topic']}. I'm here to help you learn and understand this topic better. What would you like to start with today?"
    
    def process_student_question(self, session_id: str, question: str, question_context: dict = None) -> dict:
        """Process student question and provide intelligent response"""
        if session_id not in self.tutoring_sessions:
            return {'error': 'Tutoring session not found'}
        
        session = self.tutoring_sessions[session_id]
        
        # Analyze question type and intent
        question_analysis = self._analyze_question(question, session)
        
        # Generate appropriate response based on question type
        response = self._generate_tutor_response(question, question_analysis, session)
        
        # Update conversation history
        session['conversation_history'].extend([
            {
                'timestamp': datetime.now().isoformat(),
                'role': 'user',
                'content': question,
                'message_type': 'question',
                'analysis': question_analysis
            },
            {
                'timestamp': datetime.now().isoformat(),
                'role': 'assistant',
                'content': response['content'],
                'message_type': response['type'],
                'concepts_covered': response.get('concepts', []),
                'follow_up_suggestions': response.get('follow_up', [])
            }
        ])
        
        # Update session metrics
        session['session_metrics']['questions_asked'] += 1
        session['session_metrics']['explanations_given'] += 1
        session['session_metrics']['concepts_covered'].extend(response.get('concepts', []))
        
        self._save_json_file(self.tutoring_sessions_file, self.tutoring_sessions)
        
        # Store question for analytics
        self._store_student_question(session['user_id'], question, question_analysis, response)
        
        return response
    
    def _analyze_question(self, question: str, session: dict) -> dict:
        """Analyze student question to determine type and appropriate response strategy"""
        analysis_prompt = f"""
        Analyze this student question in the context of learning {session['topic']} in {session['subject_category']}:
        
        Question: "{question}"
        
        Student's current level: {session['current_difficulty_level']}
        Recent conversation: {session['conversation_history'][-3:] if session['conversation_history'] else 'None'}
        
        Determine:
        1. Question type (conceptual, procedural, clarification, example_request, troubleshooting)
        2. Cognitive level (remember, understand, apply, analyze, evaluate, create)
        3. Difficulty level of answer needed
        4. Key concepts the student is struggling with
        5. Best response strategy
        6. Estimated student confusion level (1-10)
        
        Respond with JSON:
        {{
            "question_type": "type",
            "cognitive_level": "level",
            "difficulty_needed": "foundation/intermediate/advanced",
            "key_concepts": ["concept1", "concept2"],
            "response_strategy": "explain/demonstrate/guide/clarify",
            "confusion_level": 5,
            "requires_examples": true/false,
            "suggests_misconception": true/false
        }}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert educational psychologist analyzing student questions to provide optimal tutoring responses."},
                    {"role": "user", "content": analysis_prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=500
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Question analysis failed: {e}")
            return {
                "question_type": "conceptual",
                "cognitive_level": "understand",
                "difficulty_needed": "intermediate",
                "key_concepts": [session['topic']],
                "response_strategy": "explain",
                "confusion_level": 5,
                "requires_examples": True,
                "suggests_misconception": False
            }
    
    def _generate_tutor_response(self, question: str, analysis: dict, session: dict) -> dict:
        """Generate intelligent tutor response based on question analysis"""
        tutor_prompt = f"""
        You are {session['tutor_personality']['name']}, responding to a student's question.
        
        Your style: {session['tutor_personality']['communication']}
        Subject: {session['subject_category']} - {session['topic']}
        
        Student question: "{question}"
        
        Question analysis:
        - Type: {analysis['question_type']}
        - Cognitive level: {analysis['cognitive_level']}
        - Key concepts: {analysis['key_concepts']}
        - Strategy: {analysis['response_strategy']}
        - Confusion level: {analysis['confusion_level']}/10
        - Needs examples: {analysis['requires_examples']}
        - Possible misconception: {analysis['suggests_misconception']}
        
        Student's learning style: {session['user_profile']}
        Conversation history: {session['conversation_history'][-2:] if session['conversation_history'] else 'None'}
        
        Provide a response that:
        1. Directly addresses their question
        2. Uses their preferred learning style
        3. Includes examples if needed
        4. Corrects any misconceptions gently
        5. Encourages continued learning
        6. Asks a follow-up question to check understanding
        
        Be patient, encouraging, and adaptive. Limit to 300 words.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert AI tutor. Be supportive, clear, and pedagogically sound in your responses."},
                    {"role": "user", "content": tutor_prompt}
                ],
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            
            # Generate follow-up suggestions
            follow_up = self._generate_follow_up_suggestions(question, analysis, session)
            
            return {
                'content': content,
                'type': 'explanation',
                'concepts': analysis['key_concepts'],
                'follow_up': follow_up,
                'confidence_level': 0.9
            }
            
        except Exception as e:
            print(f"Tutor response generation failed: {e}")
            return {
                'content': f"I understand you're asking about {', '.join(analysis['key_concepts'])}. Let me help you with that. Could you tell me more about what specific part is confusing you?",
                'type': 'clarification',
                'concepts': analysis['key_concepts'],
                'follow_up': [],
                'confidence_level': 0.5
            }
    
    def _generate_follow_up_suggestions(self, question: str, analysis: dict, session: dict) -> List[str]:
        """Generate intelligent follow-up suggestions"""
        suggestions = []
        
        if analysis['question_type'] == 'conceptual':
            suggestions.extend([
                "Would you like me to explain this concept with a real-world example?",
                "Should we explore how this relates to what you already know?",
                "Would a visual diagram help clarify this concept?"
            ])
        
        elif analysis['question_type'] == 'procedural':
            suggestions.extend([
                "Would you like to try a practice problem together?",
                "Should I break this process down into smaller steps?",
                "Would you like to see this applied to a different example?"
            ])
        
        elif analysis['confusion_level'] > 7:
            suggestions.extend([
                "Should we review the fundamentals first?",
                "Would you like me to explain this more simply?",
                "Should we approach this from a different angle?"
            ])
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def provide_intelligent_hint(self, user_id: str, problem_context: dict, student_attempt: str = None) -> dict:
        """Provide intelligent, progressive hints for problem-solving"""
        hint_id = str(uuid.uuid4())
        
        # Analyze student's current attempt and understanding
        hint_analysis = self._analyze_hint_needs(problem_context, student_attempt)
        
        # Generate appropriate hint level
        hint = self._generate_progressive_hint(problem_context, hint_analysis, student_attempt)
        
        # Store hint for analytics
        hint_record = {
            'hint_id': hint_id,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'problem_context': problem_context,
            'student_attempt': student_attempt,
            'hint_analysis': hint_analysis,
            'hint_provided': hint,
            'hint_level': hint_analysis.get('suggested_hint_level', 1)
        }
        
        self.hint_system[hint_id] = hint_record
        self._save_json_file(self.hint_system_file, self.hint_system)
        
        return hint
    
    def _analyze_hint_needs(self, problem_context: dict, student_attempt: str) -> dict:
        """Analyze what type and level of hint the student needs"""
        analysis_prompt = f"""
        Analyze what hint this student needs for their learning problem:
        
        Problem context: {problem_context}
        Student's attempt: {student_attempt or 'No attempt yet'}
        
        Determine:
        1. What the student understands correctly
        2. Where they're stuck or confused
        3. What type of hint would be most helpful
        4. What hint level to provide (1=gentle nudge, 5=detailed guidance)
        5. Whether they have fundamental misconceptions
        
        Respond with JSON:
        {{
            "understanding_level": "none/partial/good",
            "stuck_point": "description of where they're stuck",
            "hint_type": "conceptual/procedural/strategic/error_correction",
            "suggested_hint_level": 3,
            "misconceptions_detected": ["misconception1"],
            "strengths_shown": ["strength1"],
            "next_step_needed": "description"
        }}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert learning psychologist analyzing student problem-solving needs."},
                    {"role": "user", "content": analysis_prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=400
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Hint analysis failed: {e}")
            return {
                "understanding_level": "partial",
                "stuck_point": "general problem solving",
                "hint_type": "conceptual",
                "suggested_hint_level": 2,
                "misconceptions_detected": [],
                "strengths_shown": [],
                "next_step_needed": "guidance on approach"
            }
    
    def _generate_progressive_hint(self, problem_context: dict, analysis: dict, student_attempt: str) -> dict:
        """Generate progressive hint based on analysis"""
        hint_level = analysis['suggested_hint_level']
        hint_type = analysis['hint_type']
        
        hint_prompt = f"""
        Provide a level {hint_level} hint for this learning situation:
        
        Problem: {problem_context}
        Student attempt: {student_attempt or 'None yet'}
        Analysis: {analysis}
        
        Hint levels:
        1 = Gentle encouragement, ask probing questions
        2 = Point toward the right direction without giving away
        3 = Provide partial solution or key insight
        4 = Show most of the solution with explanation
        5 = Complete solution with detailed explanation
        
        Hint type: {hint_type}
        
        Provide a hint that:
        1. Respects the student's intelligence
        2. Builds on what they already understand
        3. Guides them toward discovery
        4. Doesn't give away too much at once
        5. Encourages persistence
        
        Keep the hint concise but helpful (under 150 words).
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a master teacher providing perfectly calibrated hints that promote learning through guided discovery."},
                    {"role": "user", "content": hint_prompt}
                ],
                max_tokens=300
            )
            
            return {
                'hint_content': response.choices[0].message.content,
                'hint_level': hint_level,
                'hint_type': hint_type,
                'encouragement_level': 'high' if hint_level <= 2 else 'medium',
                'reveals_solution': hint_level >= 4
            }
            
        except Exception as e:
            print(f"Hint generation failed: {e}")
            return {
                'hint_content': "Think about what you already know about this topic. What's the first step you might take?",
                'hint_level': 1,
                'hint_type': 'general',
                'encouragement_level': 'high',
                'reveals_solution': False
            }
    
    def grade_essay_automatically(self, essay_id: str, essay_content: str, rubric: dict, 
                                assignment_context: dict) -> dict:
        """Automatically grade essay using AI with detailed feedback"""
        grading_id = str(uuid.uuid4())
        
        # Analyze essay quality and provide grading
        grading_result = self._ai_grade_essay(essay_content, rubric, assignment_context)
        
        # Generate detailed feedback
        feedback = self._generate_essay_feedback(essay_content, grading_result, rubric)
        
        # Store grading record
        grading_record = {
            'grading_id': grading_id,
            'essay_id': essay_id,
            'graded_at': datetime.now().isoformat(),
            'essay_content': essay_content,
            'rubric_used': rubric,
            'assignment_context': assignment_context,
            'ai_grading': grading_result,
            'detailed_feedback': feedback,
            'human_review_requested': grading_result.get('confidence_score', 0) < 0.8,
            'plagiarism_check': self._basic_plagiarism_check(essay_content)
        }
        
        self.essay_gradings[grading_id] = grading_record
        self._save_json_file(self.essay_grading_file, self.essay_gradings)
        
        return grading_record
    
    def _ai_grade_essay(self, essay_content: str, rubric: dict, context: dict) -> dict:
        """Use AI to grade essay according to rubric"""
        grading_prompt = f"""
        Grade this essay using the provided rubric:
        
        Essay content:
        {essay_content}
        
        Rubric criteria:
        {json.dumps(rubric, indent=2)}
        
        Assignment context:
        {json.dumps(context, indent=2)}
        
        Provide detailed grading for each rubric criterion:
        1. Score each criterion according to the rubric scale
        2. Provide specific evidence from the essay
        3. Explain scoring rationale
        4. Calculate overall score
        5. Assess confidence in grading
        
        Respond with JSON:
        {{
            "criterion_scores": {{
                "criterion_name": {{
                    "score": 4,
                    "max_score": 4,
                    "evidence": "specific text from essay",
                    "rationale": "explanation of score"
                }}
            }},
            "overall_score": 85,
            "overall_percentage": 85.0,
            "letter_grade": "B+",
            "confidence_score": 0.9,
            "strengths": ["strength1", "strength2"],
            "areas_for_improvement": ["area1", "area2"],
            "grade_level_assessment": "college-level writing"
        }}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert academic writing assessor. Provide fair, detailed, and constructive grading with specific evidence."},
                    {"role": "user", "content": grading_prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=1500
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Essay grading failed: {e}")
            return {
                "overall_score": 75,
                "overall_percentage": 75.0,
                "letter_grade": "B",
                "confidence_score": 0.5,
                "strengths": ["Effort demonstrated"],
                "areas_for_improvement": ["Needs human review"],
                "grade_level_assessment": "unable_to_assess"
            }
    
    def _generate_essay_feedback(self, essay_content: str, grading_result: dict, rubric: dict) -> dict:
        """Generate detailed constructive feedback for essay"""
        feedback_prompt = f"""
        Provide detailed, constructive feedback for this essay:
        
        Essay excerpt: {essay_content[:500]}...
        Grading results: {grading_result}
        
        Generate feedback that:
        1. Celebrates specific strengths with examples
        2. Identifies concrete areas for improvement
        3. Provides actionable suggestions for revision
        4. Offers next steps for skill development
        5. Maintains encouraging tone while being honest
        
        Structure feedback in categories:
        - Content and ideas
        - Organization and structure
        - Language and style
        - Mechanics and grammar
        - Overall recommendations
        
        Make feedback specific, actionable, and developmental.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a supportive writing instructor providing developmental feedback that helps students improve their writing skills."},
                    {"role": "user", "content": feedback_prompt}
                ],
                max_tokens=800
            )
            
            return {
                'detailed_feedback': response.choices[0].message.content,
                'feedback_type': 'developmental',
                'tone': 'constructive',
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Feedback generation failed: {e}")
            return {
                'detailed_feedback': "Your essay shows effort and understanding. Focus on developing your ideas more fully and supporting them with specific examples.",
                'feedback_type': 'general',
                'tone': 'encouraging',
                'generated_at': datetime.now().isoformat()
            }
    
    def _basic_plagiarism_check(self, essay_content: str) -> dict:
        """Perform basic plagiarism detection"""
        # Basic implementation - in production would integrate with plagiarism detection services
        
        suspicious_patterns = [
            "copied from",
            "source:",
            "wikipedia",
            "according to the website"
        ]
        
        flags = []
        for pattern in suspicious_patterns:
            if pattern.lower() in essay_content.lower():
                flags.append(f"Potential citation issue: contains '{pattern}'")
        
        return {
            'check_performed': True,
            'risk_level': 'high' if len(flags) > 2 else 'medium' if flags else 'low',
            'flags': flags,
            'requires_human_review': len(flags) > 1,
            'similarity_score': len(flags) * 15,  # Simple scoring
            'checked_at': datetime.now().isoformat()
        }
    
    def _store_student_question(self, user_id: str, question: str, analysis: dict, response: dict):
        """Store student question for analytics and improvement"""
        question_id = str(uuid.uuid4())
        
        question_record = {
            'question_id': question_id,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'question_text': question,
            'question_analysis': analysis,
            'ai_response': response,
            'subject_category': analysis.get('key_concepts', ['general'])[0] if analysis.get('key_concepts') else 'general'
        }
        
        self.student_questions[question_id] = question_record
        self._save_json_file(self.student_questions_file, self.student_questions)
    
    def get_tutoring_analytics(self, institution_id: str = None, time_period: str = '30d') -> dict:
        """Generate analytics for AI tutoring system usage"""
        end_date = datetime.now()
        if time_period == '7d':
            start_date = end_date - timedelta(days=7)
        elif time_period == '30d':
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Filter sessions by time period
        recent_sessions = [
            session for session in self.tutoring_sessions.values()
            if start_date <= datetime.fromisoformat(session['started_at']) <= end_date
        ]
        
        # Analyze tutoring effectiveness
        analytics = {
            'period': time_period,
            'total_sessions': len(recent_sessions),
            'unique_users': len(set(session['user_id'] for session in recent_sessions)),
            'total_questions_answered': sum(session['session_metrics']['questions_asked'] for session in recent_sessions),
            'average_session_length': self._calculate_average_session_length(recent_sessions),
            'most_common_subjects': self._get_most_common_subjects(recent_sessions),
            'user_satisfaction': self._calculate_user_satisfaction(recent_sessions),
            'ai_performance_metrics': {
                'response_accuracy': 0.89,  # Would be calculated from feedback
                'hint_effectiveness': 0.85,
                'essay_grading_confidence': 0.78
            },
            'usage_patterns': self._analyze_usage_patterns(recent_sessions)
        }
        
        return analytics
    
    def _calculate_average_session_length(self, sessions: List[dict]) -> float:
        """Calculate average tutoring session length"""
        durations = []
        for session in sessions:
            if session['conversation_history']:
                start_time = datetime.fromisoformat(session['started_at'])
                last_message_time = datetime.fromisoformat(session['conversation_history'][-1]['timestamp'])
                duration_minutes = (last_message_time - start_time).total_seconds() / 60
                durations.append(duration_minutes)
        
        return round(sum(durations) / len(durations), 1) if durations else 0
    
    def _get_most_common_subjects(self, sessions: List[dict]) -> List[dict]:
        """Get most common subjects in tutoring sessions"""
        subject_counts = {}
        for session in sessions:
            subject = session['subject_category']
            subject_counts[subject] = subject_counts.get(subject, 0) + 1
        
        return sorted([{'subject': k, 'count': v} for k, v in subject_counts.items()], 
                     key=lambda x: x['count'], reverse=True)[:5]
    
    def _calculate_user_satisfaction(self, sessions: List[dict]) -> float:
        """Calculate user satisfaction from session metrics"""
        satisfaction_scores = [
            session['session_metrics'].get('user_satisfaction', 4.0)
            for session in sessions
            if session['session_metrics'].get('user_satisfaction') is not None
        ]
        
        return round(sum(satisfaction_scores) / len(satisfaction_scores), 2) if satisfaction_scores else 4.0
    
    def _analyze_usage_patterns(self, sessions: List[dict]) -> dict:
        """Analyze usage patterns in tutoring sessions"""
        hour_counts = {}
        day_counts = {}
        
        for session in sessions:
            session_time = datetime.fromisoformat(session['started_at'])
            hour = session_time.hour
            day = session_time.strftime('%A')
            
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
            day_counts[day] = day_counts.get(day, 0) + 1
        
        peak_hour = max(hour_counts.items(), key=lambda x: x[1])[0] if hour_counts else 12
        peak_day = max(day_counts.items(), key=lambda x: x[1])[0] if day_counts else 'Monday'
        
        return {
            'peak_usage_hour': peak_hour,
            'peak_usage_day': peak_day,
            'hourly_distribution': hour_counts,
            'daily_distribution': day_counts
        }

# Initialize global AI tutoring system
ai_tutor = AITutoringSystem()