"""
Challenge Score Model - MVP
Unified tracking of challenge completions across all challenge types
"""
from __init__ import db
from datetime import datetime


class ChallengeScore(db.Model):
    """
    Unified model to track challenge completion scores for all challenge types
    Replaces fragmented localStorage approach with database persistence
    """
    __tablename__ = 'challenge_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_type = db.Column(db.String(50), nullable=False, index=True)  # 'crimping', 'osi', 'troubleshooting', 'quiz'
    
    # Score tracking
    best_score = db.Column(db.Float, default=0.0, nullable=False)  # Best score achieved (0-100)
    latest_score = db.Column(db.Float, default=0.0, nullable=False)  # Most recent score
    total_attempts = db.Column(db.Integer, default=0, nullable=False)
    
    # Completion tracking
    is_completed = db.Column(db.Boolean, default=False, nullable=False)  # Has passed threshold (75%+)
    first_completed_at = db.Column(db.DateTime, nullable=True)
    last_completed_at = db.Column(db.DateTime, nullable=True)
    
    # Performance metrics
    total_score = db.Column(db.Float, default=0.0, nullable=False)  # Sum of all scores
    average_score = db.Column(db.Float, default=0.0, nullable=False)  # Average score
    completion_time_seconds = db.Column(db.Integer, nullable=True)  # Time taken for best score
    
    # Challenge-specific metadata (stored as JSON)
    # Renamed from 'metadata' to avoid SQLAlchemy reserved word conflict
    challenge_metadata = db.Column(db.JSON, nullable=True)  # Store mode, wiring_type, difficulty, etc.
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('challenge_scores', lazy='dynamic'))
    
    # Composite unique constraint
    __table_args__ = (
        db.UniqueConstraint('user_id', 'challenge_type', name='unique_user_challenge_score'),
    )
    
    def __repr__(self):
        return f'<ChallengeScore {self.user_id}-{self.challenge_type} best={self.best_score}%>'
    
    def record_attempt(self, score, metadata=None, completion_time=None):
        """
        Record a new challenge attempt
        Args:
            score: Score percentage (0-100)
            metadata: Optional dict with challenge-specific data (mode, difficulty, etc.)
            completion_time: Optional completion time in seconds
        """
        # Ensure values are initialized (fix NoneType += error)
        if self.total_attempts is None:
            self.total_attempts = 0
        if self.total_score is None:
            self.total_score = 0.0
        if self.best_score is None:
            self.best_score = 0.0
        if self.average_score is None:
            self.average_score = 0.0
        
        self.total_attempts += 1
        self.latest_score = score
        self.total_score += score
        self.average_score = self.total_score / self.total_attempts
        
        # Update best score
        if score > self.best_score:
            self.best_score = score
            if completion_time:
                self.completion_time_seconds = completion_time
        
        # Update completion status
        completion_threshold = 75.0
        if score >= completion_threshold:
            if not self.is_completed:
                self.is_completed = True
                self.first_completed_at = datetime.utcnow()
            self.last_completed_at = datetime.utcnow()
        
        # Update metadata with deep merge for challenge_data
        if metadata:
            if self.challenge_metadata is None:
                self.challenge_metadata = {}
            
            # Deep merge challenge_data to preserve both level1 and level2 scores
            if 'challenge_data' in metadata and 'challenge_data' in self.challenge_metadata:
                # Merge nested challenge_data dict
                existing_challenge_data = self.challenge_metadata.get('challenge_data', {})
                new_challenge_data = metadata.get('challenge_data', {})
                merged_challenge_data = {**existing_challenge_data, **new_challenge_data}
                
                # DEBUG: Log merge process
                print(f"🔍 DEEP MERGE DEBUG:")
                print(f"  Existing: {existing_challenge_data}")
                print(f"  New: {new_challenge_data}")
                print(f"  Merged: {merged_challenge_data}")
                
                # Update metadata with merged challenge_data
                self.challenge_metadata.update(metadata)
                self.challenge_metadata['challenge_data'] = merged_challenge_data
            else:
                # No nested challenge_data to merge, use regular update
                self.challenge_metadata.update(metadata)
        
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'challenge_type': self.challenge_type,
            'best_score': self.best_score,
            'latest_score': self.latest_score,
            'total_attempts': self.total_attempts,
            'is_completed': self.is_completed,
            'first_completed_at': self.first_completed_at.isoformat() if self.first_completed_at else None,
            'last_completed_at': self.last_completed_at.isoformat() if self.last_completed_at else None,
            'average_score': self.average_score,
            'completion_time_seconds': self.completion_time_seconds,
            'challenge_metadata': self.challenge_metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def get_or_create(user_id, challenge_type):
        """Get existing challenge score or create new one"""
        # Force refresh from database to get latest committed data
        # This prevents race conditions when multiple saves happen rapidly
        challenge_score = ChallengeScore.query.filter_by(
            user_id=user_id,
            challenge_type=challenge_type
        ).with_for_update().first()  # Adds SELECT FOR UPDATE lock
        
        if not challenge_score:
            challenge_score = ChallengeScore(
                user_id=user_id,
                challenge_type=challenge_type
            )
            db.session.add(challenge_score)
            # Flush to get the ID and lock the row
            db.session.flush()
        else:
            # Refresh to get latest data from database
            db.session.refresh(challenge_score)
        
        return challenge_score
    
    @staticmethod
    def save_score(user_id, challenge_type, score, metadata=None, completion_time=None):
        """
        Save or update score for a challenge
        Returns: challenge_score (caller must commit the session)
        """
        challenge_score = ChallengeScore.get_or_create(user_id, challenge_type)
        challenge_score.record_attempt(score, metadata, completion_time)
        # Don't commit here - let the caller manage the transaction
        return challenge_score
    
    @staticmethod
    def get_user_stats(user_id):
        """Get aggregated stats for a user across all challenges"""
        # Define the 4 main challenge types for dashboard statistics
        MAIN_CHALLENGE_TYPES = ['crimping', 'osi', 'troubleshooting', 'quiz']
        
        # Only query the 4 main challenge types
        challenges = ChallengeScore.query.filter_by(user_id=user_id).filter(
            ChallengeScore.challenge_type.in_(MAIN_CHALLENGE_TYPES)
        ).all()
        
        if not challenges:
            return {
                'total_challenges_completed': 0,
                'total_challenges': 4,
                'average_score': 0.0,
                'total_attempts': 0,
                'completion_rate': 0.0
            }
        
        # Count only completed challenges from the main 4 types
        completed = sum(1 for c in challenges if c.is_completed)
        
        # Calculate average score correctly: sum of best scores / 4 (max possible)
        total_score = sum(c.best_score for c in challenges)
        average_score = total_score / 4  # Always divide by 4 (total challenges)
        
        # Cap display average at 100% for cleaner UI (individual scores can still exceed 100%)
        display_average = min(average_score, 100.0)
        
        total_attempts = sum(c.total_attempts for c in challenges)
        
        return {
            'total_challenges_completed': completed,
            'total_challenges': 4,  # crimping, osi, troubleshooting, quiz
            'average_score': display_average,  # Capped at 100% for display
            'total_attempts': total_attempts,
            'completion_rate': (completed / 4) * 100
        }
