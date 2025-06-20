from admin import db
from datetime import datetime
import json
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import or_, and_

class LearningPath(db.Model):
    """
    Learning Path Model for organizing simulations into structured courses
    """
    __tablename__ = 'learning_paths'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    course_level = db.Column(db.String(50), nullable=False)  # 'Networking 1', 'Networking 2', etc.
    
    # Structure and Organization
    learning_objectives = db.Column(JSON, default=list)
    prerequisites = db.Column(JSON, default=list)
    estimated_total_duration = db.Column(db.Integer, default=0)  # Total minutes for all simulations
    
    # Status and Metadata
    is_active = db.Column(db.Boolean, default=True)
    is_published = db.Column(db.Boolean, default=False)
    difficulty_level = db.Column(db.String(20), default='Beginner')
    
    # Organization
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Analytics
    total_enrollments = db.Column(db.Integer, default=0)
    total_completions = db.Column(db.Integer, default=0)
    average_completion_time = db.Column(db.Float, default=0.0)
    
    # Relationships
    simulations = db.relationship('Simulation', backref='learning_path', lazy='dynamic')
    simulation_associations = db.relationship('LearningPathSimulation', backref='learning_path', lazy='dynamic', cascade='all, delete-orphan')
    user_progress = db.relationship('UserLearningProgress', backref='learning_path', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"LearningPath('{self.title}', '{self.course_level}')"
    
    @property
    def completion_rate(self):
        """Calculate completion rate percentage"""
        if self.total_enrollments == 0:
            return 0.0
        return (self.total_completions / self.total_enrollments) * 100
    
    @property
    def simulation_count(self):
        """Get number of simulations in this path"""
        return self.simulation_associations.count()
    
    def get_ordered_simulations(self):
        """Get simulations in the correct order"""
        return self.simulation_associations.order_by(LearningPathSimulation.order_index).all()
    
    def get_next_simulation_for_user(self, user_id):
        """Get the next simulation a user should complete"""
        # Get user's progress
        user_progress = UserLearningProgress.query.filter_by(
            user_id=user_id,
            learning_path_id=self.id
        ).all()
        
        completed_sim_ids = [p.simulation_id for p in user_progress if p.status == 'completed']
        
        # Find next simulation
        for sim_assoc in self.get_ordered_simulations():
            if sim_assoc.simulation_id not in completed_sim_ids:
                # Check prerequisites
                if self._check_prerequisites(user_id, sim_assoc):
                    return sim_assoc.simulation
        
        return None  # All simulations completed or no available simulations
    
    def _check_prerequisites(self, user_id, simulation_association):
        """Check if user meets prerequisites for a simulation"""
        if not simulation_association.unlock_criteria:
            return True
        
        criteria = simulation_association.unlock_criteria
        if criteria.get('type') == 'previous_completed':
            # Check if previous simulation is completed
            previous_order = simulation_association.order_index - 1
            if previous_order >= 0:
                previous_assoc = self.simulation_associations.filter_by(order_index=previous_order).first()
                if previous_assoc:
                    user_progress = UserLearningProgress.query.filter_by(
                        user_id=user_id,
                        simulation_id=previous_assoc.simulation_id
                    ).first()
                    return user_progress and user_progress.status == 'completed'
        
        return True
    
    def calculate_user_progress(self, user_id):
        """Calculate user's progress in this learning path"""
        total_simulations = self.simulation_count
        if total_simulations == 0:
            return {'completion_percentage': 100, 'completed_count': 0, 'total_count': 0}
        
        user_progress = UserLearningProgress.query.filter_by(
            user_id=user_id,
            learning_path_id=self.id
        ).all()
        
        completed_count = len([p for p in user_progress if p.status == 'completed'])
        
        return {
            'completion_percentage': (completed_count / total_simulations) * 100,
            'completed_count': completed_count,
            'total_count': total_simulations,
            'in_progress_count': len([p for p in user_progress if p.status == 'in_progress']),
            'not_started_count': total_simulations - len(user_progress)
        }
    
    def to_dict(self, include_simulations=False, user_id=None):
        """Convert learning path to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'course_level': self.course_level,
            'learning_objectives': self.learning_objectives,
            'prerequisites': self.prerequisites,
            'estimated_total_duration': self.estimated_total_duration,
            'is_active': self.is_active,
            'is_published': self.is_published,
            'difficulty_level': self.difficulty_level,
            'simulation_count': self.simulation_count,
            'completion_rate': self.completion_rate,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_simulations:
            ordered_sims = self.get_ordered_simulations()
            data['simulations'] = [
                {
                    'simulation': assoc.simulation.to_dict(),
                    'order_index': assoc.order_index,
                    'is_required': assoc.is_required,
                    'unlock_criteria': assoc.unlock_criteria
                }
                for assoc in ordered_sims
            ]
        
        if user_id:
            data['user_progress'] = self.calculate_user_progress(user_id)
            data['next_simulation'] = self.get_next_simulation_for_user(user_id)
        
        return data


class LearningPathSimulation(db.Model):
    """
    Association table between Learning Paths and Simulations with ordering and requirements
    """
    __tablename__ = 'learning_path_simulations'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'), nullable=False)
    simulation_id = db.Column(db.Integer, db.ForeignKey('simulations.id'), nullable=False)
    
    # Ordering and Requirements
    order_index = db.Column(db.Integer, nullable=False)  # Order in the learning path
    is_required = db.Column(db.Boolean, default=True)  # Whether this simulation is required
    unlock_criteria = db.Column(JSON, default=dict)  # Criteria to unlock this simulation
    
    # Relationships
    simulation = db.relationship('Simulation', backref='path_associations')
    
    def __repr__(self):
        return f"LearningPathSimulation(path_id={self.learning_path_id}, sim_id={self.simulation_id}, order={self.order_index})"


class UserLearningProgress(db.Model):
    """
    Track user progress through learning paths and simulations
    """
    __tablename__ = 'user_learning_progress'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'), nullable=False)
    simulation_id = db.Column(db.Integer, db.ForeignKey('simulations.id'), nullable=False)
    
    # Progress Status
    status = db.Column(db.String(20), default='not_started')  # not_started, in_progress, completed, failed
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Performance Metrics
    attempts_count = db.Column(db.Integer, default=0)
    best_score = db.Column(db.Integer, default=0)
    best_time = db.Column(db.Integer, nullable=True)  # Best completion time in seconds
    total_time_spent = db.Column(db.Integer, default=0)  # Total time spent in seconds
    
    # Additional Tracking
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)  # User or instructor notes
    
    # Relationships
    simulation = db.relationship('Simulation', backref='user_progress_records')
    
    def __repr__(self):
        return f"UserLearningProgress(user_id={self.user_id}, sim_id={self.simulation_id}, status='{self.status}')"
    
    def update_progress(self, attempt_data):
        """Update progress based on simulation attempt"""
        self.attempts_count += 1
        self.last_accessed = datetime.utcnow()
        
        if attempt_data.get('completed', False):
            self.status = 'completed'
            if not self.completed_at:
                self.completed_at = datetime.utcnow()
            
            # Update best score
            score = attempt_data.get('score', 0)
            if score > self.best_score:
                self.best_score = score
            
            # Update best time
            time_spent = attempt_data.get('time_spent_seconds', 0)
            if self.best_time is None or time_spent < self.best_time:
                self.best_time = time_spent
        
        elif self.status == 'not_started':
            self.status = 'in_progress'
            self.started_at = datetime.utcnow()
        
        # Update total time spent
        self.total_time_spent += attempt_data.get('time_spent_seconds', 0)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'learning_path_id': self.learning_path_id,
            'simulation_id': self.simulation_id,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'attempts_count': self.attempts_count,
            'best_score': self.best_score,
            'best_time': self.best_time,
            'total_time_spent': self.total_time_spent,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None
        }
