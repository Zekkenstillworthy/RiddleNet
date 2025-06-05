# This file provides backward compatibility for user model imports
# All models are now properly organized in their respective modules

# Import db instance first to avoid circular imports
from __init__ import db

# For backward compatibility, provide access to commonly used models
def __getattr__(name):
    """Dynamically import models to avoid circular imports"""
    if name == 'User':
        from user.models.user import User
        return User
    elif name == 'Score':
        from user.models.score import Score
        return Score
    elif name == 'TopologyProgress':
        from user.models.topology_progress import TopologyProgress
        return TopologyProgress
    elif name == 'class_students':
        from admin.models.class_model import class_students
        return class_students
    elif name == 'Class':
        from admin.models.class_model import Class
        return Class
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")