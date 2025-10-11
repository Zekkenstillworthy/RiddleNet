"""
Challenge Progress Model - MVP
Store user progress for resumable challenges across all game types
"""
from __init__ import db
from datetime import datetime


class ChallengeProgress(db.Model):
    """
    Store user progress for resumable challenges
    Supports all challenge types: crimping, osi, linkup, quiz, etc.
    """
    __tablename__ = 'challenge_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_type = db.Column(db.String(50), nullable=False, index=True)  # 'crimping', 'osi', 'linkup', 'quiz'
    state_data = db.Column(db.JSON, nullable=False)  # JSON blob for challenge state
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Composite unique constraint - one progress per user per challenge type
    __table_args__ = (
        db.UniqueConstraint('user_id', 'challenge_type', name='unique_user_challenge'),
    )
    
    def __repr__(self):
        return f'<ChallengeProgress {self.user_id}-{self.challenge_type} (completed={self.is_completed})>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'challenge_type': self.challenge_type,
            'state_data': self.state_data,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'is_completed': self.is_completed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def get_or_create(user_id, challenge_type):
        """Get existing progress or create new one"""
        progress = ChallengeProgress.query.filter_by(
            user_id=user_id,
            challenge_type=challenge_type
        ).first()
        
        if not progress:
            progress = ChallengeProgress(
                user_id=user_id,
                challenge_type=challenge_type,
                state_data={}
            )
            db.session.add(progress)
        
        return progress
    
    @staticmethod
    def save_progress(user_id, challenge_type, state_data, is_completed=False):
        """Save or update progress for a user and challenge"""
        progress = ChallengeProgress.get_or_create(user_id, challenge_type)
        progress.state_data = state_data
        progress.is_completed = is_completed
        progress.last_updated = datetime.utcnow()
        
        db.session.commit()
        return progress
    
    @staticmethod
    def load_progress(user_id, challenge_type):
        """Load progress for a user and challenge"""
        return ChallengeProgress.query.filter_by(
            user_id=user_id,
            challenge_type=challenge_type
        ).first()
    
    @staticmethod
    def clear_progress(user_id, challenge_type):
        """Clear progress for a user and challenge"""
        progress = ChallengeProgress.query.filter_by(
            user_id=user_id,
            challenge_type=challenge_type
        ).first()
        
        if progress:
            db.session.delete(progress)
            db.session.commit()
            return True
        
        return False
