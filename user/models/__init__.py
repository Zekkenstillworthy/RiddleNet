# Import the db instance from the main application
from __init__ import db

# Define functions to get models to avoid circular imports
def get_user_model():
    from .user import User
    return User

def get_score_model():
    from .score import Score
    return Score

def get_topology_progress_model():
    from .topology_progress import TopologyProgress
    return TopologyProgress

def get_class_students_table():
    # Import the table from instructor models where it's defined
    from instructor.models.class_model import class_students
    return class_students

def get_simulation_progress_model():
    from instructor.models.simulation_progress import SimulationProgress
    return SimulationProgress

def get_user_notification_model():
    from .user_notification import UserNotification
    return UserNotification

def get_notification_preferences_model():
    from .notification_preferences import NotificationPreferences
    return NotificationPreferences

# For backward compatibility with existing code that imports directly
# These will be available but not imported at module level to avoid circular imports
def __getattr__(name):
    if name == 'User':
        return get_user_model()
    elif name == 'Score':
        return get_score_model()
    elif name == 'TopologyProgress':
        return get_topology_progress_model()
    elif name == 'class_students':
        return get_class_students_table()
    elif name == 'SimulationProgress':
        return get_simulation_progress_model()
    elif name == 'UserNotification':
        return get_user_notification_model()
    elif name == 'NotificationPreferences':
        return get_notification_preferences_model()
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")