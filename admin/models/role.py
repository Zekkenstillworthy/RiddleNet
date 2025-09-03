from datetime import datetime
from __init__ import db


class Role(db.Model):
    """Simple role model (admin, instructor, student)."""
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Role {self.name}>"


class RoleAssignment(db.Model):
    """Assign roles to principals (admin or user)."""
    __tablename__ = 'role_assignments'

    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False, index=True)
    principal_type = db.Column(db.String(20), nullable=False)  # 'admin' or 'user'
    principal_id = db.Column(db.Integer, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    role = db.relationship('Role')

    __table_args__ = (
        db.UniqueConstraint('role_id', 'principal_type', 'principal_id', name='uq_role_assignment'),
    )

    def __repr__(self):
        return f"<RoleAssignment {self.principal_type}:{self.principal_id} -> {self.role_id}>"
