from datetime import datetime
from __init__ import db


class Rubric(db.Model):
    __tablename__ = 'rubrics'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    assignment_id = db.Column(db.Integer, nullable=True, index=True)
    created_by = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    criteria = db.relationship('RubricCriterion', backref='rubric', cascade='all, delete-orphan')

    def to_dict(self, include_criteria: bool = True):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'assignment_id': self.assignment_id,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_criteria:
            data['criteria'] = [c.to_dict() for c in self.criteria]
        return data


class RubricCriterion(db.Model):
    __tablename__ = 'rubric_criteria'

    id = db.Column(db.Integer, primary_key=True)
    rubric_id = db.Column(db.Integer, db.ForeignKey('rubrics.id'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    max_points = db.Column(db.Float, nullable=False, default=0.0)
    weight = db.Column(db.Float, nullable=False, default=1.0)
    order_index = db.Column(db.Integer, nullable=False, default=1)

    def to_dict(self):
        return {
            'id': self.id,
            'rubric_id': self.rubric_id,
            'title': self.title,
            'description': self.description,
            'max_points': self.max_points,
            'weight': self.weight,
            'order_index': self.order_index,
        }


class RubricAssessment(db.Model):
    __tablename__ = 'rubric_assessments'

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('assignment_submissions.id'), nullable=False, index=True)
    rubric_id = db.Column(db.Integer, db.ForeignKey('rubrics.id'), nullable=False)
    criterion_id = db.Column(db.Integer, db.ForeignKey('rubric_criteria.id'), nullable=False)
    awarded_points = db.Column(db.Float, nullable=False, default=0.0)
    feedback = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'submission_id': self.submission_id,
            'rubric_id': self.rubric_id,
            'criterion_id': self.criterion_id,
            'awarded_points': self.awarded_points,
            'feedback': self.feedback,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
