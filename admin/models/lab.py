from datetime import datetime
from __init__ import db


class Lab(db.Model):
    __tablename__ = 'labs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    owner_admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), index=True, nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), index=True, nullable=True)
    rubric_id = db.Column(db.Integer, db.ForeignKey('rubrics.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    topology = db.relationship('LabTopology', backref='lab', uselist=False, cascade='all, delete-orphan')
    submissions = db.relationship('LabSubmission', backref='lab', cascade='all, delete-orphan')
    deadlines = db.relationship('LabDeadline', backref='lab', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'owner_admin_id': self.owner_admin_id,
            'class_id': self.class_id,
            'rubric_id': self.rubric_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class LabTopology(db.Model):
    __tablename__ = 'lab_topologies'

    id = db.Column(db.Integer, primary_key=True)
    lab_id = db.Column(db.Integer, db.ForeignKey('labs.id'), index=True, nullable=False)
    initial_config_json = db.Column(db.Text, nullable=True)
    expected_config_json = db.Column(db.Text, nullable=True)
    validations_json = db.Column(db.Text, nullable=True)  # extra validation rules

    devices = db.relationship('LabDevice', backref='topology', cascade='all, delete-orphan')


class LabDevice(db.Model):
    __tablename__ = 'lab_devices'

    id = db.Column(db.Integer, primary_key=True)
    topology_id = db.Column(db.Integer, db.ForeignKey('lab_topologies.id'), index=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.String(50), nullable=False)  # router/switch/pc

    ip_configs = db.relationship('LabIPConfig', backref='device', cascade='all, delete-orphan')


class LabIPConfig(db.Model):
    __tablename__ = 'lab_ip_configs'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('lab_devices.id'), index=True, nullable=False)
    interface = db.Column(db.String(50), nullable=True)
    ip_address = db.Column(db.String(50), nullable=False)
    subnet_mask = db.Column(db.String(50), nullable=False)
    gateway = db.Column(db.String(50), nullable=True)
    valid = db.Column(db.Boolean, default=True)


class LabSubmission(db.Model):
    __tablename__ = 'lab_submissions'

    id = db.Column(db.Integer, primary_key=True)
    lab_id = db.Column(db.Integer, db.ForeignKey('labs.id'), index=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    data_json = db.Column(db.Text, nullable=True)
    score = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    rubric_breakdown_json = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='submitted')  # submitted/graded/returned


class LabDeadline(db.Model):
    __tablename__ = 'lab_deadlines'

    id = db.Column(db.Integer, primary_key=True)
    lab_id = db.Column(db.Integer, db.ForeignKey('labs.id'), index=True, nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
    late_allowed_until = db.Column(db.DateTime, nullable=True)
    late_penalty_per_day = db.Column(db.Float, default=10.0)


class ExportHash(db.Model):
    __tablename__ = 'export_hashes'

    id = db.Column(db.Integer, primary_key=True)
    lab_id = db.Column(db.Integer, db.ForeignKey('labs.id'), index=True, nullable=True)
    export_type = db.Column(db.String(30), nullable=False)  # lab|submissions|grades
    sha256 = db.Column(db.String(64), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    created_by = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AntiCheatAction(db.Model):
    __tablename__ = 'anti_cheat_actions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    lab_id = db.Column(db.Integer, db.ForeignKey('labs.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    context_json = db.Column(db.Text, nullable=True)
    flagged = db.Column(db.Boolean, default=False)
    resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

