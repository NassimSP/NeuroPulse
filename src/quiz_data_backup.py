"""
Quiz data management - Enhanced for NeuroPulse adaptive learning
Contains quiz content with difficulty levels based on user testing feedback
"""

# Enhanced quiz data incorporating ChatGPT testing results
QUIZ_DATA = [
    {
        'id': 1,
        'title': 'Time Management for ADHD',
        'description': 'Master time management with ADHD-optimized strategies',
        'category': 'Professional Development',
        'difficulty': 'Adaptive',
        'estimated_time': '5-7 minutes',
        'learning_path': 'ADHD Skills',
        'questions': [
            {
                'question': 'What\'s a super simple way to start focusing?',
                'options': [
                    'Write a novel',
                    'Set a timer',
                    'Clean your room',
                    'Wait for motivation'
                ],
                'correct_answer': 'Set a timer',
                'explanation': 'A timer kicks your brain into gear! Try a 5 or 25-minute sprint—small wins lead to big ones!',
                'difficulty_level': 'beginner',
                'aha_moment': 'Timers create urgency and structure for ADHD brains'
            },
            {
                'question': 'What\'s "time blocking"?',
                'options': [
                    'Avoiding the clock',
                    'Guessing time left',
                    'Scheduling tasks in chunks',
                    'Turning off your phone'
                ],
                'correct_answer': 'Scheduling tasks in chunks',
                'explanation': 'Time blocking gives your day a "map." Your brain loves structure—it\'s like GPS for your to-do list!',
                'difficulty_level': 'beginner',
                'aha_moment': 'Visual time structure reduces ADHD overwhelm'
            },
            {
                'question': 'You\'ve got a 2-hour study block. What\'s the best way to structure it?',
                'options': [
                    'Work nonstop',
                    '25-min sprints + breaks',
                    'Check phone hourly',
                    'Study 10 minutes, then nap'
                ],
                'correct_answer': '25-min sprints + breaks',
                'explanation': 'Using 25-minute "Pomodoro" sessions keeps focus fresh. Brains love breaks—it\'s like charging your mental battery!',
                'difficulty_level': 'intermediate',
                'aha_moment': 'Strategic breaks prevent ADHD burnout'
            },
            {
                'question': 'You time-blocked your day but keep ignoring the blocks. What should you do next?',
                'options': [
                    'Delete the plan',
                    'Shame yourself',
                    'Review and adjust',
                    'Add more tasks'
                ],
                'correct_answer': 'Review and adjust',
                'explanation': 'Flexibility beats perfection. Your schedule is a tool, not a boss. Adjust, don\'t abandon!',
                'difficulty_level': 'advanced',
                'aha_moment': 'Adaptive systems work better than rigid ones for ADHD'
            },
            {
                'question': 'Why is "dopamine pairing" useful for task follow-through?',
                'options': [
                    'It shortens tasks',
                    'It avoids deadlines',
                    'It links tasks with rewards',
                    'It makes you tired'
                ],
                'correct_answer': 'It links tasks with rewards',
                'explanation': 'Pair boring tasks with tiny joys (music, snacks, praise). ADHD needs dopamine to drive action.',
                'difficulty_level': 'advanced',
                'aha_moment': 'Strategic reward pairing leverages ADHD neurology'
            }
        ]
    },
    {
        'id': 2,
        'title': 'Basic Chemistry: Enzymes',
        'description': 'Learn about enzymes with ADHD-friendly explanations',
        'category': 'Science',
        'difficulty': 'Adaptive',
        'estimated_time': '5-7 minutes',
        'learning_path': 'Science Foundation',
        'questions': [
            {
                'question': 'What are enzymes?',
                'options': [
                    'Sugars',
                    'Fats',
                    'Proteins',
                    'Minerals'
                ],
                'correct_answer': 'Proteins',
                'explanation': 'Enzymes are proteins with superpowers! They help speed up reactions without being used up.',
                'difficulty_level': 'beginner',
                'aha_moment': 'Enzymes are biological catalysts made of protein'
            },
            {
                'question': 'What do enzymes do?',
                'options': [
                    'Slow reactions',
                    'Stop digestion',
                    'Speed up reactions',
                    'Add energy'
                ],
                'correct_answer': 'Speed up reactions',
                'explanation': 'Enzymes are your body\'s fast-forward button! They make life\'s chemistry happen quicker.',
                'difficulty_level': 'beginner',
                'aha_moment': 'Enzymes accelerate biochemical reactions'
            },
            {
                'question': 'What is the enzyme\'s "active site"?',
                'options': [
                    'Storage room',
                    'Resting area',
                    'Reaction zone',
                    'Exit door'
                ],
                'correct_answer': 'Reaction zone',
                'explanation': 'The active site is like a lock. Only the right molecule (the key!) fits in.',
                'difficulty_level': 'beginner',
                'aha_moment': 'Active sites ensure enzyme specificity'
            },
            {
                'question': 'What happens if the enzyme changes shape?',
                'options': [
                    'It speeds up',
                    'It works better',
                    'It stops working',
                    'It multiplies'
                ],
                'correct_answer': 'It stops working',
                'explanation': 'If the shape changes (denaturation), the enzyme can\'t do its job. It\'s like a broken key!',
                'difficulty_level': 'beginner',
                'aha_moment': 'Enzyme shape determines function'
            },
            {
                'question': 'What helps enzymes work best?',
                'options': [
                    'Loud music',
                    'Perfect pH and temperature',
                    'Strong light',
                    'High sugar levels'
                ],
                'correct_answer': 'Perfect pH and temperature',
                'explanation': 'Enzymes are picky! They need just-right conditions to work their magic. Think Goldilocks!',
                'difficulty_level': 'beginner',
                'aha_moment': 'Optimal conditions maintain enzyme structure'
            }
        ]
    },
    {
        'id': 3,
        'title': 'Basic Math: Asymptotes',
        'description': 'Understanding asymptotes with visual thinking',
        'category': 'Mathematics',
        'difficulty': 'Adaptive',
        'estimated_time': '5-7 minutes',
        'learning_path': 'Math Foundation',
        'questions': [
            {
                'question': 'What is an asymptote?',
                'options': [
                    'A graph\'s mirror',
                    'A point of intersection',
                    'A line a graph approaches',
                    'A data cluster'
                ],
                'correct_answer': 'A line a graph approaches',
                'explanation': 'Asymptotes are like invisible forcefields. The graph gets close… but never crosses. Magic math!',
                'difficulty_level': 'beginner',
                'aha_moment': 'Asymptotes represent mathematical limits'
            },
            {
                'question': 'Which function has a vertical asymptote at x = 0?',
                'options': [
                    'y = x',
                    'y = 1/x',
                    'y = x²',
                    'y = √x'
                ],
                'correct_answer': 'y = 1/x',
                'explanation': 'y = 1/x shoots off to infinity near x = 0. It\'s like hitting a math wall!',
                'difficulty_level': 'beginner',
                'aha_moment': 'Division by zero creates vertical asymptotes'
            },
            {
                'question': 'What type of asymptote does y = 1/x have as y gets really big or small?',
                'options': [
                    'Curved',
                    'Diagonal',
                    'Horizontal',
                    'Circular'
                ],
                'correct_answer': 'Horizontal',
                'explanation': 'It flattens toward y = 0. That\'s your horizontal asymptote – a calm finish after wild turns!',
                'difficulty_level': 'beginner',
                'aha_moment': 'Functions can approach horizontal limits'
            },
            {
                'question': 'What causes a vertical asymptote in a rational function?',
                'options': [
                    'Adding zero',
                    'Dividing by zero',
                    'Multiplying by x',
                    'Exponents'
                ],
                'correct_answer': 'Dividing by zero',
                'explanation': 'Division by zero is a big no-no in math. That\'s when vertical asymptotes show up!',
                'difficulty_level': 'beginner',
                'aha_moment': 'Undefined points create vertical asymptotes'
            },
            {
                'question': 'True or false: Graphs can cross horizontal asymptotes.',
                'options': [
                    'True',
                    'False',
                    'Only for parabolas',
                    'Depends on x'
                ],
                'correct_answer': 'True',
                'explanation': 'Surprise! They can cross… but only temporarily. Long-term? They still flatten out.',
                'difficulty_level': 'beginner',
                'aha_moment': 'Horizontal asymptotes show long-term behavior'
            }
        ]
    }
]

def get_quiz_data():
    """Return all available quizzes"""
    return QUIZ_DATA

def get_quiz_by_id(quiz_id):
    """Get a specific quiz by its ID"""
    for quiz in QUIZ_DATA:
        if quiz['id'] == quiz_id:
            return quiz
    return None

def get_quiz_categories():
    """Get all unique categories"""
    categories = set()
    for quiz in QUIZ_DATA:
        categories.add(quiz['category'])
    return sorted(list(categories))

def get_questions_by_difficulty(quiz_id, difficulty='beginner'):
    """Filter quiz questions by difficulty level"""
    quiz = get_quiz_by_id(quiz_id)
    if not quiz:
        return []
    
    filtered_questions = []
    for question in quiz['questions']:
        if question.get('difficulty_level') == difficulty:
            filtered_questions.append(question)
    
    return filtered_questions

def get_adaptive_question_set(quiz_id, user_performance=None):
    """Get adaptive question set based on user performance"""
    quiz = get_quiz_by_id(quiz_id)
    if not quiz:
        return []
    
    # Start with beginner if no performance data
    if not user_performance:
        return get_questions_by_difficulty(quiz_id, 'beginner')
    
    # Adaptive logic based on performance
    avg_score = sum(user_performance) / len(user_performance)
    
    if avg_score >= 0.8:
        return get_questions_by_difficulty(quiz_id, 'advanced')
    elif avg_score >= 0.6:
        return get_questions_by_difficulty(quiz_id, 'intermediate')
    else:
        return get_questions_by_difficulty(quiz_id, 'beginner')