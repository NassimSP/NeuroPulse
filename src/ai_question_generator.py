"""
AI-Powered Question Generation for NeuroPulse
Generates adaptive questions for any subject using OpenAI GPT-4
"""

import os
import json
import logging
from openai import OpenAI

class AIQuestionGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = "gpt-4o"  # Latest OpenAI model for best performance
        
    def generate_questions(self, subject, topic, difficulty, subtopic=None, question_count=1, learning_objectives=None):
        """
        Generate adaptive questions for any subject and topic
        
        Args:
            subject: Main subject area (e.g., 'electrical_engineering', 'botany', 'finance')
            topic: Specific topic within subject (e.g., 'circuit_analysis', 'plant_anatomy', 'investment_analysis')
            difficulty: Difficulty level ('foundation', 'intermediate', 'advanced', 'expert')
            subtopic: Optional specific subtopic for focused learning
            question_count: Number of questions to generate
            learning_objectives: Optional specific learning goals
        """
        
        # Build comprehensive prompt for question generation
        prompt = self._build_question_prompt(subject, topic, difficulty, subtopic, question_count, learning_objectives)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7  # Balance creativity with accuracy
            )
            
            content = response.choices[0].message.content or ""
            if not content:
                return self._get_fallback_questions(subject, topic, difficulty)
            result = json.loads(content)
            return self._validate_and_format_questions(result)
            
        except Exception as e:
            logging.error(f"Error generating questions: {e}")
            return self._get_fallback_questions(subject, topic, difficulty)
    
    def _get_system_prompt(self):
        """System prompt for AI question generation optimized for neurodivergent learners"""
        return """You are an expert educational content creator specializing in neurodivergent-friendly learning. 
        
        Your role is to generate high-quality, engaging questions for any subject that:
        1. Are clear and concise (ADHD-friendly)
        2. Include practical, real-world applications
        3. Provide encouraging, insight-rich explanations
        4. Feature "aha moments" that connect concepts
        5. Are appropriate for the specified difficulty level
        6. Accommodate different learning styles
        
        Always respond with valid JSON in this exact format:
        {
            "questions": [
                {
                    "question": "Clear, specific question text",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option A",
                    "explanation": "Encouraging explanation with practical context",
                    "aha_moment": "Key insight that connects this concept to bigger picture",
                    "difficulty_level": "foundation/intermediate/advanced/expert",
                    "real_world_application": "How this applies in real situations",
                    "learning_tip": "Memory aid or learning strategy"
                }
            ]
        }"""
    
    def _build_question_prompt(self, subject, topic, difficulty, subtopic, question_count, learning_objectives):
        """Build detailed prompt for specific subject and topic"""
        
        difficulty_descriptions = {
            'foundation': 'Basic concepts and terminology - suitable for complete beginners',
            'intermediate': 'Application of concepts with some complexity - for learners with basic knowledge',
            'advanced': 'Complex problem-solving and analysis - for experienced learners',
            'expert': 'Professional-level mastery and synthesis - for specialists'
        }
        
        prompt = f"""Generate {question_count} high-quality educational question(s) for:

Subject: {subject.replace('_', ' ').title()}
Topic: {topic.replace('_', ' ').title()}
Difficulty: {difficulty.title()} - {difficulty_descriptions.get(difficulty, '')}
"""
        
        if subtopic:
            prompt += f"Subtopic Focus: {subtopic}\n"
        
        if learning_objectives:
            prompt += f"Learning Objectives: {learning_objectives}\n"
        
        prompt += f"""
Requirements:
1. Questions must be accurate and factually correct
2. Use clear, jargon-free language appropriate for the difficulty level
3. Include practical examples and real-world connections
4. Provide encouraging explanations that build confidence
5. Add "aha moments" that help concepts click
6. Ensure questions test understanding, not just memorization
7. Make content engaging and relevant to modern applications

Context Examples:
- For electrical engineering: Include safety considerations, code compliance, practical troubleshooting
- For botany: Connect to gardening, ecology, plant identification, conservation
- For finance: Link to personal budgeting, investment decisions, business applications
- For any trade: Emphasize safety, best practices, and professional standards

Focus on creating questions that someone would actually encounter in real-world situations or that build toward practical competency in the subject.
"""
        
        return prompt
    
    def _validate_and_format_questions(self, ai_response):
        """Validate and format AI-generated questions"""
        questions = []
        
        if 'questions' not in ai_response:
            return self._get_emergency_fallback()
        
        for q in ai_response['questions']:
            # Validate required fields
            if not all(key in q for key in ['question', 'options', 'correct_answer', 'explanation']):
                continue
                
            # Ensure we have 4 options
            if len(q['options']) != 4:
                continue
                
            # Verify correct answer is in options
            if q['correct_answer'] not in q['options']:
                continue
            
            formatted_question = {
                'question': q['question'][:200],  # Limit question length
                'options': q['options'],
                'correct_answer': q['correct_answer'],
                'explanation': q['explanation'],
                'aha_moment': q.get('aha_moment', 'Every step forward builds your expertise!'),
                'difficulty_level': q.get('difficulty_level', 'intermediate'),
                'real_world_application': q.get('real_world_application', ''),
                'learning_tip': q.get('learning_tip', ''),
                'generated_by_ai': True
            }
            
            questions.append(formatted_question)
        
        return questions if questions else self._get_emergency_fallback()
    
    def _get_fallback_questions(self, subject, topic, difficulty):
        """Provide subject-appropriate fallback questions when AI fails"""
        fallback_templates = {
            'electrical_engineering': {
                'question': f'What is a fundamental concept in {topic.replace("_", " ")} at the {difficulty} level?',
                'options': ['Voltage and current relationship', 'Color coding systems', 'Safety procedures', 'Circuit analysis'],
                'correct_answer': 'Voltage and current relationship',
                'explanation': 'Understanding the relationship between voltage and current is foundational to electrical engineering.',
                'aha_moment': 'Ohms Law connects voltage, current, and resistance - the building blocks of all electrical systems.'
            },
            'biology': {
                'question': f'What is an important principle in {topic.replace("_", " ")}?',
                'options': ['Cell structure', 'DNA replication', 'Photosynthesis', 'Evolution'],
                'correct_answer': 'Cell structure',
                'explanation': 'Cell structure is fundamental to understanding how living organisms function.',
                'aha_moment': 'Cells are the basic units of life - understanding them unlocks biology.'
            }
        }
        
        template = fallback_templates.get(subject, {
            'question': f'What is a key concept in {topic.replace("_", " ")}?',
            'options': ['Fundamental principles', 'Basic terminology', 'Core concepts', 'Essential knowledge'],
            'correct_answer': 'Fundamental principles',
            'explanation': f'Understanding fundamental principles is essential for mastering {topic.replace("_", " ")}.',
            'aha_moment': 'Building strong foundations makes advanced concepts much easier to grasp.'
        })
        
        template.update({
            'difficulty_level': difficulty,
            'generated_by_ai': False,
            'fallback_used': True
        })
        
        return [template]
    
    def _get_emergency_fallback(self):
        """Emergency fallback when everything fails"""
        return [{
            'question': 'This question is being generated. Please try again in a moment.',
            'options': ['Option A', 'Option B', 'Option C', 'Option D'],
            'correct_answer': 'Option A',
            'explanation': 'Questions are being prepared for this topic.',
            'aha_moment': 'Learning is a journey - every step counts!',
            'difficulty_level': 'intermediate',
            'generated_by_ai': False,
            'emergency_fallback': True
        }]
    
    def generate_learning_path(self, subject, current_level, learning_goals=None):
        """Generate adaptive learning path for progressive skill building"""
        prompt = f"""Create a comprehensive learning path for {subject.replace('_', ' ').title()}.

Current Level: {current_level}
Learning Goals: {learning_goals or 'General mastery'}

Provide a structured progression plan with:
1. Immediate next steps (what to learn now)
2. Short-term goals (next 2-4 weeks)
3. Medium-term objectives (next 2-3 months)
4. Long-term mastery targets (6+ months)

Include specific topics, estimated time investments, and key milestones.
Format as JSON with clear progression levels."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a learning path designer. Create structured, progressive learning plans."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content or ""
            return json.loads(content) if content else {"error": "No content generated"}
            
        except Exception as e:
            logging.error(f"Error generating learning path: {e}")
            return {"error": "Learning path generation temporarily unavailable"}

# Initialize global question generator
ai_generator = AIQuestionGenerator()