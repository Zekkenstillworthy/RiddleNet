from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship

# Use the main app's db
from __init__ import db

class EssayResponse(db.Model):
    """
    Model for storing user essay responses to essay questions
    
    MVP linking:
    - user_id: FK to user.id (existing)
    - question_id: FK to question.id (quiz question table)
    - class linkage: via class_students join in queries (no direct class_id column)
    - grades: stored inline as graded_score/is_graded/feedback
    """
    __tablename__ = 'essay_response'
    __table_args__ = (
        # MVP indexes for fast class and quiz queries
        Index('ix_essay_user_id', 'user_id'),
        Index('ix_essay_question_id', 'question_id'),
        {'extend_existing': True},
    )
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('question.id'), nullable=False)
    question_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=False)
    feedback = Column(Text, nullable=True)
    graded_score = Column(Integer, nullable=True)
    is_graded = Column(Boolean, default=False)
    submission_date = Column(DateTime, default=datetime.utcnow)
    category = Column(String(50), default='riddle')
    
    # Define the relationship using string reference to avoid circular imports
    user = relationship("User")
    question = relationship("Question", foreign_keys=[question_id])
    
    def __repr__(self):
        return f'<EssayResponse {self.id}: {self.question_text[:20]}...>'
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'question_id': self.question_id,
            'question_text': self.question_text,
            'response_text': self.response_text,
            'feedback': self.feedback,
            'graded_score': self.graded_score,
            'is_graded': self.is_graded,
            'submission_date': self.submission_date.strftime('%Y-%m-%d %H:%M:%S'),
            'category': self.category
        }
