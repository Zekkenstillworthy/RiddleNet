from datetime import datetime
from __init__ import db


class PointTransaction(db.Model):
	__tablename__ = 'point_transactions'

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True, nullable=False)
	change = db.Column(db.Integer, nullable=False)  # positive earn, negative spend
	reason = db.Column(db.String(120), nullable=False)  # e.g., 'correct_solution', 'hint_purchase'
	metadata_json = db.Column(db.Text, nullable=True)
	created_at = db.Column(db.DateTime, default=datetime.utcnow)

	def to_dict(self):
		return {
			'id': self.id,
			'user_id': self.user_id,
			'change': self.change,
			'reason': self.reason,
			'metadata_json': self.metadata_json,
			'created_at': self.created_at.isoformat() if self.created_at else None,
		}
