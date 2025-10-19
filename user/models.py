# Backward compatibility module for user model imports
# All models are organized in user.models.* - use direct imports when possible

from __init__ import db

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
        from instructor.models.class_model import class_students
        return class_students
    elif name == 'SimulationProgress':
        from instructor.models.simulation_progress import SimulationProgress
        return SimulationProgress
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")