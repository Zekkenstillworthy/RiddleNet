from __init__ import db
from datetime import datetime

class NetworkingProgress(db.Model):
    """
    Model for tracking user progress in networking lessons
    """
    __tablename__ = 'networking_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    module_id = db.Column(db.String(10), nullable=False)  # Format: "1" for module 1
    lesson_id = db.Column(db.String(10), nullable=False)  # Format: "1.1" for module 1, lesson 1
    completed = db.Column(db.Boolean, default=False)
    progress_percent = db.Column(db.Integer, default=0)  # 0-100
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('networking_progress', lazy='dynamic'))
    
    def __repr__(self):
        return f'<NetworkingProgress user_id={self.user_id}, lesson_id={self.lesson_id}, completed={self.completed}>'
