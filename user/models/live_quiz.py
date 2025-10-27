"""
Live Quiz Models for Slido-style quiz with leaderboard
"""
from __init__ import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class LiveQuizSession(db.Model):
    """Represents a live quiz session for a specific module/lesson"""
    __tablename__ = 'live_quiz_sessions'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    question_group_id = db.Column(db.Integer, db.ForeignKey('question_groups.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=True)
    
    session_code = db.Column(db.String(10), unique=True, nullable=False)  # Unique code for joining
    title = db.Column(db.String(200), nullable=False)
    
    # Session status
    status = db.Column(db.String(20), default='waiting')  # waiting, active, paused, completed
    
    # Timing
    started_at = db.Column(db.DateTime, nullable=True)
    ended_at = db.Column(db.DateTime, nullable=True)
    current_question_index = db.Column(db.Integer, default=0)
    time_per_question = db.Column(db.Integer, default=30)  # seconds
    
    # Settings
    show_leaderboard = db.Column(db.Boolean, default=True)
    allow_join_after_start = db.Column(db.Boolean, default=True)
    randomize_questions = db.Column(db.Boolean, default=False)
    randomize_answers = db.Column(db.Boolean, default=True)
    
    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('instructor.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    participants = db.relationship('LiveQuizParticipant', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<LiveQuizSession {self.id}: {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_code': self.session_code,
            'title': self.title,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'current_question_index': self.current_question_index,
            'time_per_question': self.time_per_question,
            'show_leaderboard': self.show_leaderboard,
            'participant_count': len(self.participants),
            'question_group_id': self.question_group_id
        }


class LiveQuizParticipant(db.Model):
    """Tracks individual participants in a live quiz session"""
    __tablename__ = 'live_quiz_participants'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('live_quiz_sessions.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Participant data
    display_name = db.Column(db.String(100), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Scores
    total_score = db.Column(db.Integer, default=0)
    total_correct = db.Column(db.Integer, default=0)
    total_answered = db.Column(db.Integer, default=0)
    
    # Timing (for ranking)
    average_response_time = db.Column(db.Float, default=0.0)  # seconds
    total_time = db.Column(db.Float, default=0.0)  # total time taken
    
    # Position
    rank = db.Column(db.Integer, nullable=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    responses = db.relationship('LiveQuizResponse', backref='participant', lazy=True, cascade='all, delete-orphan')
    user = db.relationship('User', backref='quiz_participations', foreign_keys=[user_id])
    
    def __repr__(self):
        return f'<LiveQuizParticipant {self.id}: {self.display_name}>'
    
    def calculate_rank_score(self):
        """Calculate ranking score based on correctness and speed"""
        # Score = (correct_answers * 1000) - (total_time_in_seconds)
        # This rewards both accuracy and speed
        return (self.total_correct * 1000) - int(self.total_time)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'display_name': self.display_name,
            'joined_at': self.joined_at.isoformat(),
            'total_score': self.total_score,
            'total_correct': self.total_correct,
            'total_answered': self.total_answered,
            'average_response_time': round(self.average_response_time, 2),
            'rank': self.rank,
            'is_active': self.is_active,
            'rank_score': self.calculate_rank_score()
        }


class LiveQuizResponse(db.Model):
    """Tracks individual responses to quiz questions"""
    __tablename__ = 'live_quiz_responses'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('live_quiz_participants.id', ondelete='CASCADE'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('live_quiz_sessions.id', ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    
    # Response data
    selected_answer = db.Column(db.String(1000), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    
    # Timing
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    response_time = db.Column(db.Float, nullable=False)  # seconds taken to answer
    
    # Points awarded (can vary based on speed)
    points_awarded = db.Column(db.Integer, default=0)
    
    # Question metadata at time of response (for historical accuracy)
    question_text = db.Column(db.String(500), nullable=True)
    correct_answer = db.Column(db.String(1000), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<LiveQuizResponse {self.id}: Q{self.question_id} - {"Correct" if self.is_correct else "Incorrect"}>'
    
    def calculate_points(self, max_time=30, max_points=1000):
        """
        Calculate points based on correctness and speed (Slido-style)
        - Correct answer: base points + time bonus
        - Faster answers get more points
        - Incorrect answer: 0 points
        """
        if not self.is_correct:
            return 0
        
        # Base points for correct answer
        base_points = max_points * 0.5
        
        # Time bonus (faster = more points)
        # Remaining time as percentage of max time
        time_remaining = max(0, max_time - self.response_time)
        time_bonus = (time_remaining / max_time) * (max_points * 0.5)
        
        return int(base_points + time_bonus)
    
    def to_dict(self):
        return {
            'id': self.id,
            'question_id': self.question_id,
            'selected_answer': self.selected_answer,
            'is_correct': self.is_correct,
            'response_time': round(self.response_time, 2),
            'points_awarded': self.points_awarded,
            'answered_at': self.answered_at.isoformat()
        }
