from admin import db
from datetime import datetime
import json
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import or_, and_

class Simulation(db.Model):
    """
    Enhanced Simulation Model for Computer Networking Education Platform
    Supports step-by-step simulations with validation, scoring, and analytics
    """
    __tablename__ = 'simulations'
    __table_args__ = {'extend_existing': True}
    
    # Basic Information
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    simulation_type = db.Column(db.String(50), nullable=False, index=True)  # 'Networking 1', 'Networking 2', etc.
    category = db.Column(db.String(50), nullable=False, index=True)  # 'Subnetting', 'Routing', 'Switching', etc.
    difficulty = db.Column(db.String(20), nullable=False, default='Beginner')  # Beginner, Intermediate, Advanced, Expert
    
    # Learning Objectives and Prerequisites
    learning_objectives = db.Column(JSON, default=list)  # List of learning objectives
    prerequisite_knowledge = db.Column(JSON, default=list)  # Required knowledge before starting
    
    # Simulation Structure
    step_definitions = db.Column(JSON, default=list)  # Step-by-step definition of the simulation
    validation_rules = db.Column(JSON, default=dict)  # Validation rules for each step
    simulation_config = db.Column(JSON, default=dict)  # Configuration like network topology, devices, etc.
    
    # Scoring and Assessment
    base_score = db.Column(db.Integer, default=100)
    time_bonus = db.Column(db.Integer, default=20)  # Bonus points for completing quickly
    perfect_completion_bonus = db.Column(db.Integer, default=30)  # Bonus for perfect completion
    estimated_duration = db.Column(db.Integer, default=30)  # Estimated duration in minutes
    
    # Status and Metadata
    is_active = db.Column(db.Boolean, default=True)
    is_published = db.Column(db.Boolean, default=False)
    tags = db.Column(JSON, default=list)  # Tags for categorization and search
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Version Control
    version = db.Column(db.String(10), default='1.0')
    parent_simulation_id = db.Column(db.Integer, db.ForeignKey('simulations.id'), nullable=True)
    
    # Analytics Fields
    total_attempts = db.Column(db.Integer, default=0)
    successful_completions = db.Column(db.Integer, default=0)
    average_score = db.Column(db.Float, default=0.0)
    average_duration = db.Column(db.Float, default=0.0)
    
    
    # Learning Path Integration
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'), nullable=True)
    order_in_path = db.Column(db.Integer, nullable=True)
    
    # Advanced Features
    tutorial_content = db.Column(db.Text, nullable=True)  # Optional tutorial/guide content
    reference_materials = db.Column(JSON, default=list)  # Links to reference materials
    hints_and_tips = db.Column(JSON, default=list)  # Hints for each step
    
    # Initial and Expected States (for complex simulations)
    initial_state = db.Column(JSON, default=dict)  # Starting state of the simulation
    expected_outcomes = db.Column(JSON, default=dict)  # Expected final outcomes
    
    # Relationships
    attempts = db.relationship('SimulationAttempt', backref='simulation', lazy='dynamic', cascade='all, delete-orphan')
    children = db.relationship('Simulation', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    
    def __repr__(self):
        return f"Simulation('{self.title}', '{self.simulation_type}', '{self.difficulty}')"
    
    @property
    def max_score(self):
        """Calculate maximum possible score"""
        return self.base_score + self.time_bonus + self.perfect_completion_bonus
    
    @property
    def completion_rate(self):
        """Calculate completion rate percentage"""
        if self.total_attempts == 0:
            return 0.0
        return (self.successful_completions / self.total_attempts) * 100
    
    @property
    def engagement_score(self):
        """Calculate engagement score based on attempts and completions"""
        base_engagement = min(self.total_attempts / 10, 10)  # Max 10 points for attempts
        completion_bonus = self.completion_rate / 10  # Max 10 points for completion rate
        return round(base_engagement + completion_bonus, 2)
    
    @property
    def step_count(self):
        """Get number of steps in simulation"""
        return len(self.step_definitions) if self.step_definitions else 0
    
    def get_step(self, step_index):
        """Get specific step definition"""
        if 0 <= step_index < len(self.step_definitions):
            return self.step_definitions[step_index]
        return None
    
    def validate_step_response(self, step_index, user_response):
        """Validate user response for a specific step"""
        if str(step_index) not in self.validation_rules:
            return {'valid': False, 'message': 'No validation rules found for this step'}
        
        rule = self.validation_rules[str(step_index)]
        validation_type = rule.get('type', 'exact_match')
        expected_answer = rule.get('expected_answer', '')
        
        if validation_type == 'exact_match':
            is_valid = user_response.lower().strip() == expected_answer.lower().strip()
        elif validation_type == 'contains':
            is_valid = expected_answer.lower() in user_response.lower()
        elif validation_type == 'regex':
            import re
            is_valid = bool(re.match(expected_answer, user_response, re.IGNORECASE))
        elif validation_type == 'multiple_choice':
            is_valid = user_response == expected_answer
        else:
            is_valid = True  # Default to valid if no specific validation
        
        return {
            'valid': is_valid,
            'score': rule.get('score', 0) if is_valid else 0,
            'feedback': rule.get('success_message' if is_valid else 'error_message', ''),
            'hint': rule.get('hint', '') if not is_valid else ''
        }
    
    def update_analytics(self, completion_data):
        """Update simulation analytics based on attempt completion"""
        self.total_attempts += 1
        
        if completion_data.get('completed', False):
            self.successful_completions += 1
        
        # Update average score
        if completion_data.get('score') is not None:
            total_score = (self.average_score * (self.total_attempts - 1)) + completion_data['score']
            self.average_score = round(total_score / self.total_attempts, 2)
        
        # Update average duration
        if completion_data.get('duration') is not None:
            total_duration = (self.average_duration * (self.total_attempts - 1)) + completion_data['duration']
            self.average_duration = round(total_duration / self.total_attempts, 2)
    
    def to_dict(self, include_steps=False, include_analytics=False):
        """Convert simulation to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'simulation_type': self.simulation_type,
            'category': self.category,
            'difficulty': self.difficulty,
            'learning_objectives': self.learning_objectives,
            'estimated_duration': self.estimated_duration,
            'max_score': self.max_score,
            'is_active': self.is_active,
            'is_published': self.is_published,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'version': self.version
        }
        
        if include_steps:
            data.update({
                'step_definitions': self.step_definitions,
                'validation_rules': self.validation_rules,
                'simulation_config': self.simulation_config,
                'initial_state': self.initial_state,
                'expected_outcomes': self.expected_outcomes
            })
        
        if include_analytics:
            data.update({
                'total_attempts': self.total_attempts,
                'successful_completions': self.successful_completions,
                'completion_rate': self.completion_rate,
                'average_score': self.average_score,
                'average_duration': self.average_duration,
                'engagement_score': self.engagement_score
            })
        
        return data
    
    @classmethod
    def get_dashboard_stats(cls):
        """Get dashboard statistics"""
        total_simulations = cls.query.filter_by(is_active=True).count()
        published_simulations = cls.query.filter_by(is_active=True, is_published=True).count()
        
        # Get popular simulations (most attempts)
        popular_simulations = cls.query.filter_by(is_active=True, is_published=True)\
            .order_by(cls.total_attempts.desc()).limit(5).all()
        
        # Get recent simulations
        recent_simulations = cls.query.filter_by(is_active=True)\
            .order_by(cls.created_at.desc()).limit(5).all()
        
        return {
            'total_simulations': total_simulations,
            'published_simulations': published_simulations,
            'popular_simulations': [sim.to_dict() for sim in popular_simulations],
            'recent_simulations': [sim.to_dict() for sim in recent_simulations]
        }
    
    @classmethod
    def search_simulations(cls, query, simulation_type=None, difficulty=None, category=None):
        """Search simulations with filters"""
        filters = [cls.is_active == True]
        
        if query:
            search_filter = or_(
                cls.title.ilike(f'%{query}%'),
                cls.description.ilike(f'%{query}%'),
                cls.tags.contains([query])
            )
            filters.append(search_filter)
        
        if simulation_type:
            filters.append(cls.simulation_type == simulation_type)
        
        if difficulty:
            filters.append(cls.difficulty == difficulty)
        
        if category:
            filters.append(cls.category == category)
        
        return cls.query.filter(and_(*filters)).order_by(cls.created_at.desc()).all()


class SimulationAttempt(db.Model):
    """
    Model for tracking individual simulation attempts by users
    """
    __tablename__ = 'simulation_attempts'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    simulation_id = db.Column(db.Integer, db.ForeignKey('simulations.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Attempt Details
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    
    # Progress Tracking
    current_step = db.Column(db.Integer, default=0)
    step_responses = db.Column(JSON, default=dict)  # User responses for each step
    step_scores = db.Column(JSON, default=dict)  # Scores achieved for each step
    step_timestamps = db.Column(JSON, default=dict)  # Timestamps for each step completion
    
    # Scoring
    total_score = db.Column(db.Integer, default=0)
    time_spent_seconds = db.Column(db.Integer, default=0)
    perfect_completion = db.Column(db.Boolean, default=False)
    
    # Session Data
    session_data = db.Column(JSON, default=dict)  # Store simulation state, configurations, etc.
    feedback_given = db.Column(JSON, default=list)  # Feedback provided during the attempt
    hints_used = db.Column(JSON, default=list)  # Hints that were used
    
    # Quality Metrics
    accuracy_score = db.Column(db.Float, default=0.0)  # Percentage of correct answers
    efficiency_score = db.Column(db.Float, default=0.0)  # Based on time taken vs estimated
    
    def __repr__(self):
        return f"SimulationAttempt(simulation_id={self.simulation_id}, user_id={self.user_id}, completed={self.is_completed})"
    
    @property
    def duration_minutes(self):
        """Get duration in minutes"""
        return round(self.time_spent_seconds / 60, 2) if self.time_spent_seconds else 0
    
    @property
    def completion_percentage(self):
        """Get completion percentage"""
        if not self.simulation or not self.simulation.step_definitions:
            return 0
        return (self.current_step / len(self.simulation.step_definitions)) * 100
    
    def record_step_completion(self, step_index, response, score, is_correct):
        """Record completion of a simulation step"""
        self.step_responses[str(step_index)] = response
        self.step_scores[str(step_index)] = score
        self.step_timestamps[str(step_index)] = datetime.utcnow().isoformat()
        
        self.total_score += score
        self.current_step = max(self.current_step, step_index + 1)
        
        # Update accuracy
        correct_steps = sum(1 for s in self.step_scores.values() if s > 0)
        total_steps = len(self.step_scores)
        self.accuracy_score = (correct_steps / total_steps * 100) if total_steps > 0 else 0
    
    def complete_attempt(self, final_score=None):
        """Mark attempt as completed"""
        self.is_completed = True
        self.completed_at = datetime.utcnow()
        
        if final_score is not None:
            self.total_score = final_score
        
        # Calculate efficiency score
        if self.simulation and self.simulation.estimated_duration:
            expected_seconds = self.simulation.estimated_duration * 60
            if self.time_spent_seconds <= expected_seconds:
                self.efficiency_score = 100
            else:
                self.efficiency_score = max(0, 100 - ((self.time_spent_seconds - expected_seconds) / expected_seconds * 50))
        
        # Check for perfect completion
        if self.simulation:
            total_possible_steps = len(self.simulation.step_definitions)
            completed_steps = len([s for s in self.step_scores.values() if s > 0])
            self.perfect_completion = (completed_steps == total_possible_steps and self.accuracy_score >= 95)
    
    def to_dict(self):
        """Convert attempt to dictionary"""
        return {
            'id': self.id,
            'simulation_id': self.simulation_id,
            'user_id': self.user_id,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'is_completed': self.is_completed,
            'current_step': self.current_step,
            'total_score': self.total_score,
            'duration_minutes': self.duration_minutes,
            'completion_percentage': self.completion_percentage,
            'accuracy_score': self.accuracy_score,
            'efficiency_score': self.efficiency_score,
            'perfect_completion': self.perfect_completion,
            'step_responses': self.step_responses,
            'step_scores': self.step_scores
        }
