from datetime import datetime
from __init__ import db


class Tutorial(db.Model):
	__tablename__ = 'tutorials'

	id = db.Column(db.Integer, primary_key=True)
	simulation_id = db.Column(db.Integer, db.ForeignKey('simulations.id'), nullable=False, index=True)
	title = db.Column(db.String(255), nullable=False)
	created_by = db.Column(db.Integer, nullable=True)
	created_at = db.Column(db.DateTime, default=datetime.utcnow)
	updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

	steps = db.relationship('TutorialStep', backref='tutorial', cascade='all, delete-orphan', order_by='TutorialStep.order_index')

	def to_dict(self, include_steps: bool = True):
		data = {
			'id': self.id,
			'simulation_id': self.simulation_id,
			'title': self.title,
			'created_by': self.created_by,
			'created_at': self.created_at.isoformat() if self.created_at else None,
			'updated_at': self.updated_at.isoformat() if self.updated_at else None,
		}
		if include_steps:
			data['steps'] = [s.to_dict() for s in self.steps]
		return data


class TutorialStep(db.Model):
	__tablename__ = 'tutorial_steps'

	id = db.Column(db.Integer, primary_key=True)
	tutorial_id = db.Column(db.Integer, db.ForeignKey('tutorials.id'), nullable=False, index=True)
	order_index = db.Column(db.Integer, nullable=False, default=1)
	step_type = db.Column(db.String(50), default='text')  # text, image, video, code, tip
	content = db.Column(db.Text, nullable=True)  # for text/code
	media_url = db.Column(db.String(512), nullable=True)
	caption = db.Column(db.String(512), nullable=True)

	def to_dict(self):
		return {
			'id': self.id,
			'tutorial_id': self.tutorial_id,
			'order_index': self.order_index,
			'step_type': self.step_type,
			'content': self.content,
			'media_url': self.media_url,
			'caption': self.caption,
		}
