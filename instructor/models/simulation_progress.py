"""Simulation progress tracking model."""

from datetime import datetime

from sqlalchemy import JSON

from __init__ import db


class SimulationProgress(db.Model):
	"""Persist per-user simulation progress snapshots."""

	__tablename__ = "simulation_progress"
	__table_args__ = (
		db.UniqueConstraint("user_id", "simulation_id", name="uq_simulation_progress_user_sim"),
		{"extend_existing": True},
	)

	id = db.Column(db.Integer, primary_key=True)
	simulation_id = db.Column(db.Integer, db.ForeignKey("simulations.id"), nullable=False, index=True)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
	status = db.Column(db.String(50), nullable=False, default="in_progress")
	last_step = db.Column(db.String(120), nullable=True)
	progress_data = db.Column(JSON, default=dict)
	score = db.Column(db.Float, nullable=True)
	created_at = db.Column(db.DateTime, default=datetime.utcnow)
	updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

	simulation = db.relationship(
		"Simulation",
		backref=db.backref("progress_entries", lazy="dynamic", cascade="all, delete-orphan"),
	)
	user = db.relationship("User", backref=db.backref("simulation_progress", lazy="dynamic"))

	def to_dict(self, include_data: bool = False) -> dict:
		"""Serialize the progress record for API responses."""

		payload = {
			"id": self.id,
			"simulation_id": self.simulation_id,
			"user_id": self.user_id,
			"status": self.status,
			"last_step": self.last_step,
			"score": self.score,
			"created_at": self.created_at.isoformat() if self.created_at else None,
			"updated_at": self.updated_at.isoformat() if self.updated_at else None,
		}

		if include_data:
			payload["progress_data"] = self.progress_data or {}

		return payload

	@classmethod
	def get_or_create(cls, simulation_id: int, user_id: int) -> "SimulationProgress":
		"""Fetch an existing record or instantiate a new one for the user/simulation pair."""

		instance = cls.query.filter_by(simulation_id=simulation_id, user_id=user_id).first()
		if instance:
			return instance

		instance = cls(simulation_id=simulation_id, user_id=user_id)
		db.session.add(instance)
		return instance
