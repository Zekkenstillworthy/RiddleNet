# This file is a proxy for importing models from the proper location
# All model definitions have been moved to the user/models/ directory or are imported from admin

# Import db instance first to avoid circular imports
from __init__ import db

# Define functions to get models to avoid circular imports
def get_user_model():
    from user.models.user import User
    return User

def get_score_model():
    from user.models.score import Score
    return Score

def get_question_model():
    from admin.models.question import Question
    return Question

def get_essay_response_model():
    from admin.models.essay_response import EssayResponse
    return EssayResponse

def get_class_students_table():
    from admin.models.class_model import class_students
    return class_students

def get_class_model():
    from admin.models.class_model import Class
    return Class

# For backward compatibility, still provide direct access to these models
# Using __getattr__ to avoid circular imports at module load time
def __getattr__(name):
    if name == 'User':
        return get_user_model()
    elif name == 'Score':
        return get_score_model()
    elif name == 'Question':
        return get_question_model()
    elif name == 'EssayResponse':
        return get_essay_response_model()
    elif name == 'class_students':
        return get_class_students_table()
    elif name == 'Class':
        return get_class_model()
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")