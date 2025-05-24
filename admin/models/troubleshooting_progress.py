from datetime import datetime
import json
from __init__ import db

class TroubleshootingProgress(db.Model):
    """
    Model to track user progress and attempts on troubleshooting scenarios
    """
    __tablename__ = 'troubleshooting_progress'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    troubleshooting_id = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    completion_time = db.Column(db.DateTime, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer, default=0)
    attempts = db.Column(db.Integer, default=0)
    hints_used = db.Column(db.Integer, default=0)
    _user_solution = db.Column('user_solution', db.Text, nullable=True)  # JSON string of user solution
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def user_solution(self):
        """Get the user solution as a Python object"""
        if not self._user_solution:
            return {}
        try:
            return json.loads(self._user_solution)
        except (ValueError, TypeError):
            return {}
    
    @user_solution.setter
    def user_solution(self, solution):
        """Set the user solution from a Python object"""
        if isinstance(solution, dict):
            self._user_solution = json.dumps(solution)
        else:
            self._user_solution = solution
    
    def calculate_score(self, time_limit=15, base_score=10, time_bonus=5, solution_bonus=5):
        """
        Calculate the user's score based on time taken, hints used, and solution correctness
        
        Args:
            time_limit: Time limit in minutes
            base_score: Base score for completing the scenario
            time_bonus: Maximum time bonus points
            solution_bonus: Bonus for perfect solution
        """
        score = base_score
        
        # Apply time bonus if completed within time limit
        if self.completion_time and self.start_time:
            minutes_taken = (self.completion_time - self.start_time).total_seconds() / 60
            if minutes_taken < time_limit:
                # Calculate time bonus - more time remaining = higher bonus
                time_factor = (time_limit - minutes_taken) / time_limit
                score += int(time_bonus * time_factor)
        
        # Reduce score for hints used (each hint reduces score by 1)
        if self.hints_used > 0:
            score = max(base_score // 2, score - self.hints_used)
        
        # This is a placeholder - actual solution comparison would be more complex
        # and would be implemented in the troubleshooting controller
        # Additional solution_bonus would be added there if solution perfectly matches
        
        return score
