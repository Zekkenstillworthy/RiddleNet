from datetime import datetime
from __init__ import db
from user.models.user import User

class TroubleshootingProgress(db.Model):
    """
    Model for tracking user progress on troubleshooting scenarios
    """
    __tablename__ = 'troubleshooting_progress'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    troubleshooting_id = db.Column(db.Integer, db.ForeignKey('troubleshootings.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False, default=0)
    time_taken = db.Column(db.Integer, nullable=True)  # Time in seconds
    is_completed = db.Column(db.Boolean, default=False)
    topology_match_percentage = db.Column(db.Float, default=0.0)  # How close they got to the solution
    attempts = db.Column(db.Integer, default=1)
    _user_solution = db.Column('user_solution', db.Text, nullable=True)  # JSON string of user's solution
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', 
                          primaryjoin="TroubleshootingProgress.user_id == User.id",
                          backref=db.backref('troubleshooting_progress', lazy=True),
                          foreign_keys=[user_id])
    troubleshooting = db.relationship('Troubleshooting', 
                                     primaryjoin="TroubleshootingProgress.troubleshooting_id == Troubleshooting.id",
                                     backref=db.backref('user_progress', lazy=True), 
                                     foreign_keys=[troubleshooting_id])
    
    @property
    def user_solution(self):
        """Get the user solution as a dictionary"""
        import json
        if not self._user_solution:
            return {}
        try:
            return json.loads(self._user_solution)
        except (ValueError, TypeError):
            return {}
    
    @user_solution.setter
    def user_solution(self, solution_dict):
        """Set the user solution from a dictionary"""
        import json
        if isinstance(solution_dict, dict):
            self._user_solution = json.dumps(solution_dict)
        else:
            self._user_solution = solution_dict

    def to_dict(self):
        """Convert the model to a dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'troubleshooting_id': self.troubleshooting_id,
            'score': self.score,
            'time_taken': self.time_taken,
            'is_completed': self.is_completed,
            'topology_match_percentage': self.topology_match_percentage,
            'attempts': self.attempts,
            'user_solution': self.user_solution,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }