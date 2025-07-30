"""
Template Helper Functions for Dynamic Content
Provides access to database simulations and learning paths in templates
"""

from admin.models.simulation import Simulation
from admin.models.learning_path import LearningPath
from admin.models.class_model import Class

def get_class_simulations(class_id):
    """Get simulations assigned to a specific class"""
    try:
        class_obj = Class.query.get(class_id)
        if not class_obj:
            return []
        
        # Simple assignment logic based on class name
        if "networking 1" in class_obj.name.lower():
            return Simulation.query.filter_by(
                simulation_type='Networking 1',
                is_published=True
            ).all()
        elif "networking 2" in class_obj.name.lower():
            return Simulation.query.filter_by(
                simulation_type='Networking 2',
                is_published=True
            ).all()
        else:
            return Simulation.query.filter_by(is_published=True).limit(10).all()
    except:
        return []

def get_class_learning_paths(class_id):
    """Get learning paths relevant to a class"""
    try:
        return LearningPath.query.filter_by(is_published=True).all()
    except:
        return []

def get_all_simulations():
    """Get all published simulations"""
    try:
        return Simulation.query.filter_by(is_published=True).all()
    except:
        return []

def register_template_helpers(app):
    """Register helper functions with Flask app"""
    app.jinja_env.globals.update(
        get_class_simulations=get_class_simulations,
        get_class_learning_paths=get_class_learning_paths,
        get_all_simulations=get_all_simulations
    )
