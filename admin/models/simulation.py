from datetime import datetime
from flask import current_app
from admin.models import db

class Simulation(db.Model):
    """Model for storing simulation data created by admins"""
    __tablename__ = 'simulations'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    simulation_type = db.Column(db.String(50), nullable=False)  # 'networking1', 'networking2', etc.
    category = db.Column(db.String(100))
    difficulty = db.Column(db.String(20))  # 'beginner', 'intermediate', 'advanced', 'expert'
    
    # Learning objectives and metadata
    learning_objectives = db.Column(db.JSON, default=list)
    estimated_duration = db.Column(db.Integer)  # in minutes
    prerequisite_knowledge = db.Column(db.JSON, default=list)
    
    # Step definitions and configuration
    step_definitions = db.Column(db.JSON, default=list)
    validation_rules = db.Column(db.JSON, default=dict)
    simulation_config = db.Column(db.JSON, default=dict)
    
    # Scoring
    base_score = db.Column(db.Integer, default=100)
    time_bonus = db.Column(db.Integer, default=20)
    perfect_completion_bonus = db.Column(db.Integer, default=10)
    
    # State tracking
    initial_state = db.Column(db.JSON, default=dict)
    expected_outcomes = db.Column(db.JSON, default=dict)
    
    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_published = db.Column(db.Boolean, default=False)
    tags = db.Column(db.String(255))
    
    # For learning path integration
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'), nullable=True)
    
    # Relationships
    creator = db.relationship('User', backref='created_simulations')
    learning_path = db.relationship('LearningPath', backref='simulations')

    def to_dict(self):
        """Convert simulation to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'simulation_type': self.simulation_type,
            'category': self.category,
            'difficulty': self.difficulty,
            'learning_objectives': self.learning_objectives,
            'estimated_duration': self.estimated_duration,
            'prerequisite_knowledge': self.prerequisite_knowledge,
            'step_definitions': self.step_definitions,
            'validation_rules': self.validation_rules,
            'simulation_config': self.simulation_config,
            'base_score': self.base_score,
            'time_bonus': self.time_bonus,
            'perfect_completion_bonus': self.perfect_completion_bonus,
            'initial_state': self.initial_state,
            'expected_outcomes': self.expected_outcomes,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'is_published': self.is_published,
            'tags': self.tags,
            'learning_path_id': self.learning_path_id
        }
