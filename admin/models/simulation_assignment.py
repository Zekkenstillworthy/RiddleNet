"""
SimulationAssignment Model for RiddleNet
========================================

This model manages the assignment of simulations to classes, groups, and individual students.
It supports multi-level assignment logic with due dates, attempts, and scoring.
"""

from datetime import datetime, timedelta
from admin import db

class SimulationAssignment(db.Model):
    """
    Model for managing simulation assignments to classes, groups, or individuals
    """
    __tablename__ = 'simulation_assignments'
    __table_args__ = {'extend_existing': True}
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Assignment metadata
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Assignment relationships
    simulation_id = db.Column(db.Integer, db.ForeignKey('simulations.id'), nullable=False)
    assigned_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Assignment targets (one of these should be set)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=True)  # New: Module organization
    group_id = db.Column(db.Integer, nullable=True)  # Optional for future group assignments
    individual_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Assignment configuration
    assignment_type = db.Column(db.String(50), nullable=False, default='class')  # 'class', 'group', 'individual', 'lesson', 'category', 'explicit'
    
    # Week 2 Enhancement: Multi-level assignment logic
    lesson_name = db.Column(db.String(100), nullable=True)  # For lesson-based assignments
    category_match = db.Column(db.String(100), nullable=True)  # For category-based assignments
    auto_assign = db.Column(db.Boolean, default=False)  # For automatic assignment based on category
    
    # Timing and attempts
    assigned_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    available_from = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    available_until = db.Column(db.DateTime, nullable=True)
    
    # Attempt configuration
    max_attempts = db.Column(db.Integer, default=3)
    time_limit_minutes = db.Column(db.Integer, nullable=True)  # Per attempt
    
    # Scoring configuration
    total_points = db.Column(db.Integer, default=100)
    passing_score = db.Column(db.Integer, default=70)
    
    # Assignment settings
    allow_late_submission = db.Column(db.Boolean, default=False)
    late_penalty_percent = db.Column(db.Integer, default=10)  # Percentage deduction per day late
    
    show_correct_answers = db.Column(db.Boolean, default=True)
    show_results_immediately = db.Column(db.Boolean, default=True)
    
    # Randomization
    randomize_questions = db.Column(db.Boolean, default=False)
    randomize_answers = db.Column(db.Boolean, default=False)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_published = db.Column(db.Boolean, default=False)
    
    # Instructions and feedback
    instructions = db.Column(db.Text)
    feedback_template = db.Column(db.Text)
    
    # Relationships
    simulation = db.relationship('Simulation', backref='assignments')
    assigner = db.relationship('User', foreign_keys=[assigned_by], backref='created_assignments')
    assigned_class = db.relationship('Class', backref='simulation_assignments')
    # assigned_group = db.relationship('Group', backref='simulation_assignments')
    assigned_individual = db.relationship('User', foreign_keys=[individual_user_id], backref='individual_assignments')
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        if not self.title and hasattr(self, 'simulation') and self.simulation:
            self.title = f"{self.simulation.title} Assignment"
    
    @property
    def is_available(self):
        """Check if assignment is currently available for completion"""
        now = datetime.utcnow()
        
        if not self.is_active or not self.is_published:
            return False
        
        if self.available_from and now < self.available_from:
            return False
            
        if self.available_until and now > self.available_until:
            return False
            
        return True
    
    @property
    def is_overdue(self):
        """Check if assignment is past due date"""
        if not self.due_date:
            return False
        return datetime.utcnow() > self.due_date
    
    @property
    def days_until_due(self):
        """Get days until due date (negative if overdue)"""
        if not self.due_date:
            return None
        delta = self.due_date - datetime.utcnow()
        return delta.days
    
    def get_target_users(self):
        """Get all users who should receive this assignment"""
        users = []
        
        if self.assignment_type == 'individual' and self.individual_user_id:
            from admin.models.user import User
            user = User.query.get(self.individual_user_id)
            if user:
                users.append(user)
                
        elif self.assignment_type == 'class' and self.class_id:
            from admin.models.class_model import Class
            class_obj = Class.query.get(self.class_id)
            if class_obj:
                users.extend(class_obj.students)
                
        elif self.assignment_type == 'group' and self.group_id:
            # TODO: Implement when Group model is available
            pass
        
        return users
    
    def get_user_attempts(self, user_id):
        """Get all attempts by a specific user for this assignment"""
        return SimulationAssignmentAttempt.query.filter_by(
            assignment_id=self.id,
            user_id=user_id
        ).order_by(SimulationAssignmentAttempt.started_at.desc()).all()
    
    def can_user_attempt(self, user_id):
        """Check if user can make a new attempt"""
        if not self.is_available:
            return False, "Assignment is not currently available"
        
        attempts = self.get_user_attempts(user_id)
        
        if len(attempts) >= self.max_attempts:
            return False, f"Maximum attempts ({self.max_attempts}) reached"
        
        # Check if user has an active (in-progress) attempt
        active_attempt = next((a for a in attempts if a.status == 'in_progress'), None)
        if active_attempt:
            return False, "You have an active attempt in progress"
        
        return True, "Can attempt"
    
    def calculate_score(self, raw_score, submission_time=None):
        """Calculate final score with late penalties and bonuses"""
        if submission_time is None:
            submission_time = datetime.utcnow()
        
        final_score = raw_score
        
        # Apply late penalty if applicable
        if self.due_date and submission_time > self.due_date and not self.allow_late_submission:
            return 0  # No score for late submission when not allowed
        
        if self.due_date and submission_time > self.due_date and self.allow_late_submission:
            days_late = (submission_time - self.due_date).days + 1
            penalty = days_late * self.late_penalty_percent
            final_score = max(0, raw_score - (raw_score * penalty / 100))
        
        return min(final_score, self.total_points)
    
    def get_assignment_statistics(self):
        """Get statistics for this assignment"""
        attempts = SimulationAssignmentAttempt.query.filter_by(assignment_id=self.id).all()
        completed_attempts = [a for a in attempts if a.status == 'completed']
        
        target_users = self.get_target_users()
        
        stats = {
            'total_assigned': len(target_users),
            'total_attempts': len(attempts),
            'completed_attempts': len(completed_attempts),
            'completion_rate': len(completed_attempts) / len(target_users) if target_users else 0,
            'average_score': sum(a.final_score for a in completed_attempts) / len(completed_attempts) if completed_attempts else 0,
            'passing_count': len([a for a in completed_attempts if a.final_score >= self.passing_score]),
            'failing_count': len([a for a in completed_attempts if a.final_score < self.passing_score])
        }
        
        stats['passing_rate'] = stats['passing_count'] / len(completed_attempts) if completed_attempts else 0
        
        return stats
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'simulation_id': self.simulation_id,
            'simulation_title': self.simulation.title if self.simulation else None,
            'assignment_type': self.assignment_type,
            'assigned_date': self.assigned_date.isoformat() if self.assigned_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'available_from': self.available_from.isoformat() if self.available_from else None,
            'available_until': self.available_until.isoformat() if self.available_until else None,
            'max_attempts': self.max_attempts,
            'time_limit_minutes': self.time_limit_minutes,
            'total_points': self.total_points,
            'passing_score': self.passing_score,
            'is_available': self.is_available,
            'is_overdue': self.is_overdue,
            'days_until_due': self.days_until_due,
            'is_active': self.is_active,
            'is_published': self.is_published,
            'instructions': self.instructions,
            'allow_late_submission': self.allow_late_submission,
            'late_penalty_percent': self.late_penalty_percent
        }


class SimulationAssignmentAttempt(db.Model):
    """
    Model for tracking individual user attempts at simulation assignments
    """
    __tablename__ = 'simulation_assignment_attempts'
    __table_args__ = (
        db.UniqueConstraint('assignment_id', 'user_id', 'attempt_number', name='unique_assignment_attempt_per_user'),
        {'extend_existing': True}
    )
    
    # Primary key and base fields
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Attempt metadata
    assignment_id = db.Column(db.Integer, db.ForeignKey('simulation_assignments.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    attempt_number = db.Column(db.Integer, nullable=False)  # 1, 2, 3, etc.
    
    # Timing
    started_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    submitted_at = db.Column(db.DateTime, nullable=True)
    time_spent_minutes = db.Column(db.Integer, default=0)
    
    # Status and progress
    status = db.Column(db.String(50), default='in_progress')  # 'in_progress', 'completed', 'abandoned', 'expired'
    current_step = db.Column(db.Integer, default=0)
    total_steps = db.Column(db.Integer, default=0)
    
    # Scoring
    raw_score = db.Column(db.Integer, default=0)
    final_score = db.Column(db.Integer, default=0)
    max_possible_score = db.Column(db.Integer, default=100)
    
    # Attempt data
    responses = db.Column(db.JSON)  # User responses to simulation steps
    simulation_state = db.Column(db.JSON)  # Current state of simulation
    feedback_data = db.Column(db.JSON)  # Feedback and hints provided
    
    # Performance metrics
    correct_answers = db.Column(db.Integer, default=0)
    incorrect_answers = db.Column(db.Integer, default=0)
    hints_used = db.Column(db.Integer, default=0)
    
    # Relationships
    assignment = db.relationship('SimulationAssignment', backref='attempts')
    user = db.relationship('User', backref='simulation_attempts')
    
    __table_args__ = (
        db.UniqueConstraint('assignment_id', 'user_id', 'attempt_number', name='unique_attempt_per_user'),
        {'extend_existing': True}
    )
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        if not self.attempt_number:
            # Auto-increment attempt number for this user/assignment
            last_attempt = SimulationAssignmentAttempt.query.filter_by(
                assignment_id=self.assignment_id,
                user_id=self.user_id
            ).order_by(SimulationAssignmentAttempt.attempt_number.desc()).first()
            
            self.attempt_number = (last_attempt.attempt_number + 1) if last_attempt else 1
    
    @property
    def is_active(self):
        """Check if attempt is currently active"""
        return self.status == 'in_progress'
    
    @property
    def is_completed(self):
        """Check if attempt is completed"""
        return self.status == 'completed'
    
    @property
    def completion_percentage(self):
        """Get completion percentage"""
        if self.total_steps == 0:
            return 0
        return min(100, (self.current_step / self.total_steps) * 100)
    
    @property
    def grade_letter(self):
        """Get letter grade based on score percentage"""
        if not self.assignment:
            return 'N/A'
        
        percentage = (self.final_score / self.assignment.total_points) * 100
        
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'
    
    @property
    def is_passing(self):
        """Check if attempt meets passing score"""
        if not self.assignment:
            return False
        return self.final_score >= self.assignment.passing_score
    
    def calculate_final_score(self):
        """Calculate and update final score"""
        if self.assignment:
            self.final_score = self.assignment.calculate_score(
                self.raw_score, 
                self.submitted_at
            )
        return self.final_score
    
    def submit_attempt(self):
        """Mark attempt as completed and calculate final score"""
        self.submitted_at = datetime.utcnow()
        self.status = 'completed'
        
        # Calculate time spent
        if self.started_at:
            time_delta = self.submitted_at - self.started_at
            self.time_spent_minutes = int(time_delta.total_seconds() / 60)
        
        # Calculate final score
        self.calculate_final_score()
        
        return self
    
    def abandon_attempt(self):
        """Mark attempt as abandoned"""
        self.status = 'abandoned'
        return self
    
    def expire_attempt(self):
        """Mark attempt as expired (time limit exceeded)"""
        self.status = 'expired'
        self.submitted_at = datetime.utcnow()
        self.calculate_final_score()
        return self
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'assignment_id': self.assignment_id,
            'user_id': self.user_id,
            'attempt_number': self.attempt_number,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'time_spent_minutes': self.time_spent_minutes,
            'status': self.status,
            'current_step': self.current_step,
            'total_steps': self.total_steps,
            'completion_percentage': self.completion_percentage,
            'raw_score': self.raw_score,
            'final_score': self.final_score,
            'max_possible_score': self.max_possible_score,
            'grade_letter': self.grade_letter,
            'is_passing': self.is_passing,
            'correct_answers': self.correct_answers,
            'incorrect_answers': self.incorrect_answers,
            'hints_used': self.hints_used,
            'responses': self.responses,
            'simulation_state': self.simulation_state
        }
