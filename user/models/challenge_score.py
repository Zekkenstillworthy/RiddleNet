"""
Challenge Score Model - MVP
Unified tracking of challenge completions across all challenge types
"""
from __init__ import db
from datetime import datetime
from sqlalchemy.orm.attributes import flag_modified
from user.constants.linkup import (
    LINKUP_FOUNDATION_TOTAL,
    canonicalize_completed_ids,
    calculate_linkup_counts,
)


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
    
    # ---------------------------------------------------------------------
    # Helper methods for interpreting challenge progress consistently
    # ---------------------------------------------------------------------
    @staticmethod
    def _normalize_score(value):
        """Clamp arbitrary values to the 0-100 range as a float."""
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(numeric, 100.0))

    @staticmethod
    def _evaluate_osi_progress(challenge):
        """Compute progress and completion flags for the OSI/TCP-IP challenge."""
        metadata = challenge.challenge_metadata or {}
        if not isinstance(metadata, dict):
            metadata = {}

        challenge_data = metadata.get('challenge_data', {})
        if not isinstance(challenge_data, dict):
            challenge_data = {}

        level1_score = ChallengeScore._normalize_score(challenge_data.get('level1_score'))
        level2_score = ChallengeScore._normalize_score(challenge_data.get('level2_score'))
        combined_score = ChallengeScore._normalize_score(
            challenge_data.get('combined_score', (level1_score + level2_score) / 2.0)
        )
        both_levels_complete = bool(challenge_data.get('both_levels_complete', False))

        # Treat the challenge as fully complete only when the user legitimately
        # cleared both levels with perfect scores and the final flag was set.
        fully_completed = bool(
            both_levels_complete and level1_score == 100.0 and level2_score == 100.0
        )

        # Progress is the average of both levels so partial progress surfaces correctly.
        progress_score = (level1_score + level2_score) / 2.0

        return {
            'level1_score': level1_score,
            'level2_score': level2_score,
            'combined_score': combined_score,
            'progress_score': progress_score,
            'fully_completed': fully_completed,
            'both_levels_complete_flag': both_levels_complete
        }

    @staticmethod
    def effective_best_score(challenge):
        """Return the score that should drive UI progress for a challenge."""
        if not challenge:
            return 0.0

        if challenge.challenge_type == 'osi':
            osi_state = ChallengeScore._evaluate_osi_progress(challenge)
            return osi_state['progress_score'] if not osi_state['fully_completed'] else osi_state['combined_score']

        return challenge.best_score or 0.0

    @staticmethod
    def is_effectively_completed(challenge):
        """Determine completion status with challenge-specific rules."""
        if not challenge:
            return False

        if challenge.challenge_type == 'osi':
            osi_state = ChallengeScore._evaluate_osi_progress(challenge)
            return osi_state['fully_completed']
        
        # 🔧 FIX: Link Up! completion requires ALL 16 foundation modules (not just is_completed flag)
        if challenge.challenge_type == 'troubleshooting':
            if challenge.challenge_metadata:
                counts = challenge.challenge_metadata.get('challenge_counts') or {}
                foundation_completed = counts.get('foundation')

                if foundation_completed is None:
                    completed = canonicalize_completed_ids(
                        challenge.challenge_metadata.get('completed_challenges', [])
                    )
                    foundation_completed = calculate_linkup_counts(completed)['foundation']

                return foundation_completed >= LINKUP_FOUNDATION_TOTAL
            return False
        
        # 🔧 FIX: Crimping completion requires ALL 3 difficulties complete (not just high score)
        if challenge.challenge_type == 'crimping':
            if challenge.challenge_metadata:
                easy_complete = challenge.challenge_metadata.get('easyCompleted', False)
                medium_complete = challenge.challenge_metadata.get('mediumCompleted', False)
                hard_complete = challenge.challenge_metadata.get('hardCompleted', False)
                return easy_complete and medium_complete and hard_complete
            return False
        
        # 🔧 FIX: Quiz completion requires all 3 sets complete (not just high score)
        if challenge.challenge_type == 'quiz':
            if challenge.challenge_metadata:
                completed_sets = challenge.challenge_metadata.get('completedSets', [])
                return len(completed_sets) >= 3
            return False

        return bool(challenge.is_completed)

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
                print(f"[DEBUG] DEEP MERGE DEBUG:")
                print(f"  Existing: {existing_challenge_data}")
                print(f"  New: {new_challenge_data}")
                print(f"  Merged: {merged_challenge_data}")
                
                # Update metadata with merged challenge_data
                self.challenge_metadata.update(metadata)
                self.challenge_metadata['challenge_data'] = merged_challenge_data
            else:
                # No nested challenge_data to merge, use regular update
                self.challenge_metadata.update(metadata)
            
            # CRITICAL: Mark JSONB field as modified for SQLAlchemy to detect changes
            flag_modified(self, 'challenge_metadata')
        
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
        # [OK] MVP: Define the 4 main challenge types for dashboard statistics
        # Note: 'troubleshooting' and 'linkup' refer to the same challenge (Link Up!)
        MAIN_CHALLENGE_TYPES = ['crimping', 'osi', 'troubleshooting', 'quiz']
        
        # Only query the 4 main challenge types
        challenges = ChallengeScore.query.filter_by(user_id=user_id).filter(
            ChallengeScore.challenge_type.in_(MAIN_CHALLENGE_TYPES)
        ).all()
        
        if not challenges:
            return {
                'total_challenges_completed': 0,
                'total_challenges': 4,  # [OK] MVP: 4 challenges (crimping, osi, troubleshooting/linkup, quiz)
                'average_score': 0.0,
                'total_attempts': 0,
                'completion_rate': 0.0
            }

        completed_challenges = []
        total_completed_score = 0.0

        for challenge in challenges:
            if ChallengeScore.is_effectively_completed(challenge):
                completed_challenges.append(challenge)
                total_completed_score += ChallengeScore.effective_best_score(challenge)

        completed_count = len(completed_challenges)

        if completed_count > 0:
            average_score = total_completed_score / completed_count
            display_average = min(average_score, 100.0)
        else:
            display_average = 0.0
        
        total_attempts = sum(c.total_attempts for c in challenges)
        
        return {
            'total_challenges_completed': completed_count,
            'total_challenges': 4,  # [OK] MVP: crimping, osi, troubleshooting (Link Up!), quiz
            'average_score': display_average,  # [OK] MVP: Average of completed challenges only
            'total_attempts': total_attempts,
            'completion_rate': (completed_count / 4) * 100  # [OK] MVP: Percentage of 4 challenges completed
        }
    
    @staticmethod
    def get_troubleshooting_progress(user_id):
        """Return normalized Link Up! progress across foundation and advanced tiers."""
        # Query all troubleshooting-related challenges (across all difficulty levels)
        challenges = ChallengeScore.query.filter_by(
            user_id=user_id
        ).filter(
            ChallengeScore.challenge_type.in_(['linkup_easy', 'troubleshooting_medium', 'troubleshooting_hard', 'troubleshooting'])
        ).order_by(ChallengeScore.updated_at.desc()).all()
        
        # If no challenges exist, return zero progress
        if not challenges:
            return {
                'completed_challenges': [],
                'challenge_counts': {'foundation': 0, 'easy': 0, 'intermediate': 0, 'hard': 0, 'total': 0},
                'progress_percentage': 0.0,
                'is_complete': False
            }
        
        # Find the most recent challenge with metadata
        latest_metadata = {}
        for challenge in challenges:
            if challenge.challenge_metadata:
                latest_metadata = challenge.challenge_metadata
                break
        
        completed_challenges = canonicalize_completed_ids(latest_metadata.get('completed_challenges', []))
        challenge_counts = latest_metadata.get('challenge_counts')

        if not challenge_counts:
            challenge_counts = calculate_linkup_counts(completed_challenges)

        foundation_completed = min(challenge_counts.get('foundation', 0), LINKUP_FOUNDATION_TOTAL)
        progress_percentage = (foundation_completed / LINKUP_FOUNDATION_TOTAL) * 100.0 if LINKUP_FOUNDATION_TOTAL else 0.0

        return {
            'completed_challenges': completed_challenges,
            'challenge_counts': challenge_counts,
            'progress_percentage': round(progress_percentage, 1),
            'is_complete': foundation_completed >= LINKUP_FOUNDATION_TOTAL
        }
