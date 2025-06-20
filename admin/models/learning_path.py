from datetime import datetime
from admin.models import db

class LearningPath(db.Model):
    """Model for storing learning paths"""
    __tablename__ = 'learning_paths'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    course_level = db.Column(db.String(50), nullable=False)  # 'networking1', 'networking2', 'advanced'
    
    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_published = db.Column(db.Boolean, default=False)
    
    # Relationships
    creator = db.relationship('User', backref='created_learning_paths')
    
    # Additional fields
    total_duration = db.Column(db.Integer)  # Total estimated duration in minutes
    difficulty = db.Column(db.String(20))  # Overall difficulty
    
    def to_dict(self):
        """Convert learning path to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'course_level': self.course_level,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'is_published': self.is_published,
            'total_duration': self.total_duration,
            'difficulty': self.difficulty,
            'simulations': [sim.to_dict() for sim in self.simulations] if hasattr(self, 'simulations') else []
        }

class LearningPathSimulation(db.Model):
    """Association model for learning paths and simulations"""
    __tablename__ = 'learning_path_simulations'

    id = db.Column(db.Integer, primary_key=True)
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'), nullable=False)
    simulation_id = db.Column(db.Integer, db.ForeignKey('simulations.id'), nullable=False)
    
    # Order and requirements
    order_index = db.Column(db.Integer, nullable=False)
    is_required = db.Column(db.Boolean, default=True)
    unlock_criteria = db.Column(db.JSON, default=dict)
    
    # Relationships
    learning_path = db.relationship('LearningPath', backref=db.backref(
        'simulation_associations', order_by=order_index, cascade="all, delete-orphan"
    ))
    simulation = db.relationship('Simulation')

class UserLearningProgress(db.Model):
    """Model to track user progress in learning paths and simulations"""
    __tablename__ = 'user_learning_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'), nullable=True)
    simulation_id = db.Column(db.Integer, db.ForeignKey('simulations.id'), nullable=False)
    
    # Progress tracking
    status = db.Column(db.String(20), default='not_started')  # 'not_started', 'in_progress', 'completed'
    progress_data = db.Column(db.JSON, default=dict)
    score = db.Column(db.Integer)
    time_spent = db.Column(db.Integer)  # in seconds
    
    # Timestamps
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='learning_progress')
    learning_path = db.relationship('LearningPath')
    simulation = db.relationship('Simulation')
