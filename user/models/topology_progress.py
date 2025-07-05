from __init__ import db
from datetime import datetime

class TopologyProgress(db.Model):
    """Model for tracking user progress on topology exercises"""
    __tablename__ = 'topology_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topology_type = db.Column(db.String(50), nullable=False)
    highest_score = db.Column(db.Integer, default=0)
    completion_count = db.Column(db.Integer, default=0)
    last_attempt = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('topology_progress', lazy='dynamic'))
    
    def __repr__(self):
        return f'<TopologyProgress {self.user_id}:{self.topology_type}>'
