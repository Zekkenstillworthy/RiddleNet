from datetime import datetime
import json
from __init__ import db

class Troubleshooting(db.Model):
    """
    Model for troubleshooting scenarios in the admin panel
    """
    __tablename__ = 'troubleshootings'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), default='medium')  # easy, medium, hard
    scenario = db.Column(db.Text, nullable=False)
    solution = db.Column(db.Text, nullable=False)
    _hints = db.Column('hints', db.Text, nullable=True)  # JSON string
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def hints(self):
        """Get the hints as a list of strings"""
        if not self._hints:
            return []
        try:
            return json.loads(self._hints)
        except (ValueError, TypeError):
            return []

    @hints.setter
    def hints(self, hints_list):
        """Set the hints from a list of strings"""
        if isinstance(hints_list, list):
            self._hints = json.dumps(hints_list)
        else:
            self._hints = hints_list

    def to_dict(self):
        """Convert the model to a dictionary for API responses"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'difficulty': self.difficulty,
            'scenario': self.scenario,
            'solution': self.solution,
            'hints': self.hints,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }