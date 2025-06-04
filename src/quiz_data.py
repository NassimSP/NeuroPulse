"""
Quiz data management
Contains sample quiz content for testing the neurodivergent-friendly quiz app
"""

# Enhanced quiz data with adaptive difficulty levels and NeuroPulse features
QUIZ_DATA = [
    {
        'id': 1,
        'title': 'Time Management for ADHD',
        'description': 'Master time management with ADHD-optimized strategies',
        'category': 'Professional Development',
        'difficulty_levels': ['beginner', 'intermediate', 'advanced'],
        'estimated_time': '5-7 minutes',
        'learning_path': 'ADHD Skills',
        'questions': {
            'beginner': [
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
                    'aha_moment': 'Visual time structure reduces ADHD overwhelm'
                },
                {
                    'question': 'Why do ADHD brains love "micro tasks"?',
                    'options': [
                        'They\'re expensive',
                        'They sound cool',
                        'They feel doable',
                        'They take hours'
                    ],
                    'correct_answer': 'They feel doable',
                    'explanation': 'Breaking things down makes it easier to start. You\'re not lazy—you just need the right entry point!',
                    'aha_moment': 'Task initiation is easier with smaller entry points'
                },
                {
                    'question': 'What\'s a "body double" in productivity?',
                    'options': [
                        'A stunt person',
                        'Your reflection',
                        'A robot assistant',
                        'Someone working beside you'
                    ],
                    'correct_answer': 'Someone working beside you',
                    'explanation': 'Just having someone there helps your brain stay on track. You\'re not alone in this!',
                    'aha_moment': 'Social presence increases ADHD focus naturally'
                },
                {
                    'question': 'What\'s the best first step when you\'re overwhelmed?',
                    'options': [
                        'Take a nap',
                        'Pick one task',
                        'Eat candy',
                        'Open every tab'
                    ],
                    'correct_answer': 'Pick one task',
                    'explanation': 'Just pick one small thing. Momentum beats motivation. You\'ve got this—one task at a time!',
                    'aha_moment': 'Starting anywhere creates momentum for ADHD minds'
                }
            ],
            'intermediate': [
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
                    'aha_moment': 'Strategic breaks prevent ADHD burnout'
                },
                {
                    'question': 'What\'s one way to stop hyperfocus from wrecking your schedule?',
                    'options': [
                        'Set a timer',
                        'Work until tired',
                        'Skip lunch',
                        'Do everything at once'
                    ],
                    'correct_answer': 'Set a timer',
                    'explanation': 'Hyperfocus is powerful, but timers help pull you back before burnout. You\'re the one in control!',
                    'aha_moment': 'External cues can manage ADHD hyperfocus positively'
                },
                {
                    'question': 'You\'re avoiding a boring task. What\'s a smart first move?',
                    'options': [
                        'Wait till tomorrow',
                        'Multitask',
                        'Break it into micro steps',
                        'Force yourself to do it all'
                    ],
                    'correct_answer': 'Break it into micro steps',
                    'explanation': 'ADHD brains resist overwhelm. Small steps lower resistance and make action easier. Slice it up!',
                    'aha_moment': 'Resistance decreases with smaller task chunks'
                },
                {
                    'question': 'Why do visuals like color-coded calendars work well?',
                    'options': [
                        'They look pretty',
                        'They make time visible',
                        'Everyone uses them',
                        'They\'re fast to create'
                    ],
                    'correct_answer': 'They make time visible',
                    'explanation': 'ADHD brains struggle with time blindness. Colors and visuals help time feel real. It\'s like x-ray vision for your day!',
                    'aha_moment': 'Visual systems combat ADHD time blindness'
                },
                {
                    'question': 'You often forget appointments. What\'s a great fix?',
                    'options': [
                        'Trust your memory',
                        'Hope for reminders',
                        'Use alarms + calendar',
                        'Tell a friend'
                    ],
                    'correct_answer': 'Use alarms + calendar',
                    'explanation': 'External systems = brain relief. Alarms + calendars = a second brain that never forgets!',
                    'aha_moment': 'External memory systems reduce ADHD cognitive load'
                }
            ],
            'advanced': [
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
                    'aha_moment': 'Strategic reward pairing leverages ADHD neurology'
                },
                {
                    'question': 'How can you prevent burnout from over-scheduling?',
                    'options': [
                        'Work faster',
                        'Plan recovery time',
                        'Skip meals',
                        'Avoid rest'
                    ],
                    'correct_answer': 'Plan recovery time',
                    'explanation': 'Recharge is productive! Planned downtime = stronger focus later. Burnout is a glitch, not a badge.',
                    'aha_moment': 'Proactive recovery prevents ADHD energy crashes'
                },
                {
                    'question': 'You notice certain times of day are more focused. What\'s the smart move?',
                    'options': [
                        'Ignore it',
                        'Work anytime',
                        'Schedule high-focus tasks then',
                        'Do chores instead'
                    ],
                    'correct_answer': 'Schedule high-focus tasks then',
                    'explanation': 'Everyone has energy peaks. ADHD brains thrive with aligned timing. Guard your "golden hours"!',
                    'aha_moment': 'Energy alignment maximizes ADHD productivity'
                },
                {
                    'question': 'You keep switching tasks mid-way. What system can help most?',
                    'options': [
                        'Random lists',
                        'Unstructured days',
                        'Visual task tracker',
                        'Sticky notes only'
                    ],
                    'correct_answer': 'Visual task tracker',
                    'explanation': 'Visual systems reduce memory overload and boost follow-through. Trello, Notion, whiteboards… your brain loves visual anchors!',
                    'aha_moment': 'Visual tracking systems support ADHD working memory'
                }
            ]
        }
    },
    {
        'id': 2,
        'title': 'Basic Chemistry: Enzymes',
        'description': 'Learn about enzymes with ADHD-friendly explanations',
        'category': 'Science',
        'difficulty_levels': ['beginner', 'intermediate', 'advanced'],
        'estimated_time': '5-7 minutes',
        'learning_path': 'Science Foundation',
        'questions': {
            'beginner': [
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
                    'aha_moment': 'Optimal conditions maintain enzyme structure'
                }
            ]
        }
    },
    {
        'id': 3,
        'title': 'Basic Math: Asymptotes',
        'description': 'Understanding asymptotes with visual thinking',
        'category': 'Mathematics',
        'difficulty_levels': ['beginner', 'intermediate', 'advanced'],
        'estimated_time': '5-7 minutes',
        'learning_path': 'Math Foundation',
        'questions': {
            'beginner': [
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
                    'aha_moment': 'Horizontal asymptotes show long-term behavior'
                }
            ]
        }
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

def get_quiz_by_difficulty(quiz_id, difficulty='beginner'):
    """Get quiz questions filtered by difficulty level"""
    quiz = get_quiz_by_id(quiz_id)
    if not quiz or difficulty not in quiz.get('difficulty_levels', []):
        return None
    
    quiz_copy = quiz.copy()
    if isinstance(quiz['questions'], dict):
        quiz_copy['questions'] = quiz['questions'].get(difficulty, [])
    else:
        # Legacy format - return as is
        quiz_copy['questions'] = quiz['questions']
    
    return quiz_copy