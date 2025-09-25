from __init__ import db
from datetime import datetime

class TopologyProgress(db.Model):
    """Enhanced model for tracking user progress on gamified topology exercises"""
    __tablename__ = 'topology_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topology_type = db.Column(db.String(50), nullable=False)  # point-to-point, star, mesh, etc.
    difficulty = db.Column(db.String(20), nullable=False)     # easy, medium, hard
    
    # Completion tracking
    is_completed = db.Column(db.Boolean, default=False)
    completion_count = db.Column(db.Integer, default=0)
    first_completed = db.Column(db.DateTime, nullable=True)
    last_completed = db.Column(db.DateTime, nullable=True)
    
    # Scoring and performance
    best_score = db.Column(db.Integer, default=0)
    total_score = db.Column(db.Integer, default=0)
    average_score = db.Column(db.Float, default=0.0)
    
    # Time tracking
    best_time = db.Column(db.Integer, nullable=True)  # Best completion time in seconds
    total_time = db.Column(db.Integer, default=0)     # Total time spent in seconds
    last_attempt_start = db.Column(db.DateTime, nullable=True)
    last_attempt_duration = db.Column(db.Integer, nullable=True)
    
    # Attempt tracking
    total_attempts = db.Column(db.Integer, default=0)
    failed_attempts = db.Column(db.Integer, default=0)
    
    # Achievements and milestones
    achievements_earned = db.Column(db.Text, nullable=True)  # JSON string of achievement IDs
    hints_used = db.Column(db.Integer, default=0)
    tutorial_completed = db.Column(db.Boolean, default=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('topology_progress', lazy='dynamic'))
    
    # Composite unique constraint
    __table_args__ = (
        db.UniqueConstraint('user_id', 'topology_type', 'difficulty', name='_user_topology_difficulty'),
    )
    
    def __repr__(self):
        return f'<TopologyProgress {self.user_id}:{self.topology_type}:{self.difficulty}>'
    
    def calculate_average_score(self):
        """Calculate and update average score"""
        if self.completion_count > 0:
            self.average_score = self.total_score / self.completion_count
        else:
            self.average_score = 0.0
    
    def add_completion(self, score, completion_time=None):
        """Add a new completion attempt"""
        self.completion_count += 1
        self.total_score += score
        self.total_attempts += 1
        
        # Update best score
        if score > self.best_score:
            self.best_score = score
        
        # Update completion status and timing
        if not self.is_completed:
            self.is_completed = True
            self.first_completed = datetime.utcnow()
        
        self.last_completed = datetime.utcnow()
        
        # Update time tracking
        if completion_time:
            self.last_attempt_duration = completion_time
            self.total_time += completion_time
            
            if not self.best_time or completion_time < self.best_time:
                self.best_time = completion_time
        
        # Recalculate average
        self.calculate_average_score()
    
    def add_failed_attempt(self, attempt_time=None):
        """Add a failed attempt"""
        self.total_attempts += 1
        self.failed_attempts += 1
        
        if attempt_time:
            self.total_time += attempt_time
            self.last_attempt_duration = attempt_time
    
    def get_success_rate(self):
        """Calculate success rate as percentage"""
        if self.total_attempts == 0:
            return 0.0
        return ((self.total_attempts - self.failed_attempts) / self.total_attempts) * 100
    
    def get_achievements(self):
        """Get list of earned achievements"""
        if not self.achievements_earned:
            return []
        
        try:
            import json
            return json.loads(self.achievements_earned)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def add_achievement(self, achievement_id):
        """Add an achievement to the earned list"""
        achievements = self.get_achievements()
        if achievement_id not in achievements:
            achievements.append(achievement_id)
            import json
            self.achievements_earned = json.dumps(achievements)
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'topology_type': self.topology_type,
            'difficulty': self.difficulty,
            'is_completed': self.is_completed,
            'completion_count': self.completion_count,
            'first_completed': self.first_completed.isoformat() if self.first_completed else None,
            'last_completed': self.last_completed.isoformat() if self.last_completed else None,
            'best_score': self.best_score,
            'total_score': self.total_score,
            'average_score': round(self.average_score, 2),
            'best_time': self.best_time,
            'total_time': self.total_time,
            'total_attempts': self.total_attempts,
            'failed_attempts': self.failed_attempts,
            'success_rate': round(self.get_success_rate(), 2),
            'achievements_earned': self.get_achievements(),
            'hints_used': self.hints_used,
            'tutorial_completed': self.tutorial_completed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
