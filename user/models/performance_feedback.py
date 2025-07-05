from __init__ import db
from datetime import datetime
import json

class PerformanceFeedback(db.Model):
    """
    Model for tracking real-time performance feedback during troubleshooting scenarios
    """
    __tablename__ = 'performance_feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False)  # Unique session identifier
    scenario_id = db.Column(db.String(50), nullable=False)  # Scenario being worked on
    lobby_id = db.Column(db.String(100), nullable=True)  # Collaborative lobby ID if applicable
    
    # Action tracking
    action_type = db.Column(db.String(50), nullable=False)  # 'device_placement', 'connection_creation', 'cli_command', etc.
    action_details = db.Column(db.Text, nullable=True)  # JSON string with action specifics
    
    # Feedback information
    feedback_type = db.Column(db.String(20), nullable=False)  # 'success', 'warning', 'error', 'hint'
    feedback_message = db.Column(db.Text, nullable=False)  # The feedback message shown to user
    feedback_score = db.Column(db.Integer, default=0)  # Points awarded for this action
    
    # Context information
    device_id = db.Column(db.String(100), nullable=True)  # Device involved in action
    connection_ids = db.Column(db.Text, nullable=True)  # JSON array of connection IDs
    cli_command = db.Column(db.Text, nullable=True)  # CLI command if applicable
    
    # Progress tracking
    scenario_progress = db.Column(db.Float, default=0.0)  # 0.0 to 100.0 percentage
    step_completed = db.Column(db.Boolean, default=False)  # Whether this action completed a step
    hints_used = db.Column(db.Integer, default=0)  # Number of hints used
    
    # Timing information
    action_timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # When action occurred
    response_time = db.Column(db.Float, nullable=True)  # Time taken for action (seconds)
    
    # Collaborative context
    is_collaborative = db.Column(db.Boolean, default=False)
    team_members = db.Column(db.Text, nullable=True)  # JSON array of team member IDs
    
    # Relationships
    user = db.relationship('User', backref=db.backref('performance_feedback', lazy='dynamic'))
    
    def __repr__(self):
        return f'<PerformanceFeedback {self.action_type} by User {self.user_id} - {self.feedback_type}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'scenario_id': self.scenario_id,
            'lobby_id': self.lobby_id,
            'action_type': self.action_type,
            'action_details': json.loads(self.action_details) if self.action_details else {},
            'feedback_type': self.feedback_type,
            'feedback_message': self.feedback_message,
            'feedback_score': self.feedback_score,
            'device_id': self.device_id,
            'connection_ids': json.loads(self.connection_ids) if self.connection_ids else [],
            'cli_command': self.cli_command,
            'scenario_progress': self.scenario_progress,
            'step_completed': self.step_completed,
            'hints_used': self.hints_used,
            'action_timestamp': self.action_timestamp.isoformat() if self.action_timestamp else None,
            'response_time': self.response_time,
            'is_collaborative': self.is_collaborative,
            'team_members': json.loads(self.team_members) if self.team_members else []
        }
    
    @classmethod
    def create_feedback(cls, user_id, session_id, scenario_id, action_type, feedback_type, 
                       feedback_message, **kwargs):
        """Helper method to create feedback entries"""
        feedback = cls(
            user_id=user_id,
            session_id=session_id,
            scenario_id=scenario_id,
            action_type=action_type,
            feedback_type=feedback_type,
            feedback_message=feedback_message,
            **kwargs
        )
        
        # Convert dict fields to JSON strings
        if 'action_details' in kwargs and isinstance(kwargs['action_details'], dict):
            feedback.action_details = json.dumps(kwargs['action_details'])
        if 'connection_ids' in kwargs and isinstance(kwargs['connection_ids'], list):
            feedback.connection_ids = json.dumps(kwargs['connection_ids'])
        if 'team_members' in kwargs and isinstance(kwargs['team_members'], list):
            feedback.team_members = json.dumps(kwargs['team_members'])
        
        db.session.add(feedback)
        db.session.commit()
        return feedback

class FeedbackSession(db.Model):
    """
    Model for tracking feedback sessions and aggregated metrics
    """
    __tablename__ = 'feedback_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    scenario_id = db.Column(db.String(50), nullable=False)
    lobby_id = db.Column(db.String(100), nullable=True)
    
    # Session metadata
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    total_duration = db.Column(db.Float, nullable=True)  # In seconds
    
    # Aggregated metrics
    total_actions = db.Column(db.Integer, default=0)
    successful_actions = db.Column(db.Integer, default=0)
    failed_actions = db.Column(db.Integer, default=0)
    hints_used = db.Column(db.Integer, default=0)
    total_score = db.Column(db.Integer, default=0)
    completion_percentage = db.Column(db.Float, default=0.0)
    
    # Performance metrics
    average_response_time = db.Column(db.Float, nullable=True)
    fastest_action_time = db.Column(db.Float, nullable=True)
    slowest_action_time = db.Column(db.Float, nullable=True)
    
    # Learning progress indicators
    mistakes_made = db.Column(db.Integer, default=0)
    improvements_shown = db.Column(db.Integer, default=0)
    concepts_mastered = db.Column(db.Text, nullable=True)  # JSON array
    
    # Collaborative metrics
    is_collaborative = db.Column(db.Boolean, default=False)
    team_size = db.Column(db.Integer, default=1)
    collaboration_score = db.Column(db.Float, default=0.0)
    
    # Status
    is_completed = db.Column(db.Boolean, default=False)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('feedback_sessions', lazy='dynamic'))
    
    def __repr__(self):
        return f'<FeedbackSession {self.session_id} - User {self.user_id}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'scenario_id': self.scenario_id,
            'lobby_id': self.lobby_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'total_duration': self.total_duration,
            'total_actions': self.total_actions,
            'successful_actions': self.successful_actions,
            'failed_actions': self.failed_actions,
            'hints_used': self.hints_used,
            'total_score': self.total_score,
            'completion_percentage': self.completion_percentage,
            'average_response_time': self.average_response_time,
            'fastest_action_time': self.fastest_action_time,
            'slowest_action_time': self.slowest_action_time,
            'mistakes_made': self.mistakes_made,
            'improvements_shown': self.improvements_shown,
            'concepts_mastered': json.loads(self.concepts_mastered) if self.concepts_mastered else [],
            'is_collaborative': self.is_collaborative,
            'team_size': self.team_size,
            'collaboration_score': self.collaboration_score,
            'is_completed': self.is_completed
        }
    
    def update_metrics(self):
        """Update aggregated metrics based on feedback entries"""
        from sqlalchemy import func
        
        # Get all feedback for this session
        feedback_query = PerformanceFeedback.query.filter_by(session_id=self.session_id)
        
        # Calculate basic metrics
        self.total_actions = feedback_query.count()
        self.successful_actions = feedback_query.filter_by(feedback_type='success').count()
        self.failed_actions = feedback_query.filter_by(feedback_type='error').count()
        self.hints_used = feedback_query.filter(PerformanceFeedback.hints_used > 0).count()
        
        # Calculate score
        score_sum = db.session.query(func.sum(PerformanceFeedback.feedback_score)).filter_by(
            session_id=self.session_id
        ).scalar()
        self.total_score = score_sum or 0
        
        # Calculate response times
        response_times = [f.response_time for f in feedback_query.all() if f.response_time]
        if response_times:
            self.average_response_time = sum(response_times) / len(response_times)
            self.fastest_action_time = min(response_times)
            self.slowest_action_time = max(response_times)
        
        # Update completion percentage (get latest)
        latest_feedback = feedback_query.order_by(PerformanceFeedback.action_timestamp.desc()).first()
        if latest_feedback:
            self.completion_percentage = latest_feedback.scenario_progress
        
        db.session.commit()
