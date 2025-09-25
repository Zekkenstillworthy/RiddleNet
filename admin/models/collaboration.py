"""
Database models for collaboration settings and lobby management
"""

from admin import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON


class CollaborationSetting(db.Model):
    """Store collaboration settings for simulations"""
    __tablename__ = 'collaboration_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    simulation_id = db.Column(db.Integer, db.ForeignKey('simulations.id'), nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)
    
    # Collaboration configuration
    collaboration_enabled = db.Column(db.Boolean, default=False)
    team_size = db.Column(db.Integer, default=2)
    shared_terminal = db.Column(db.Boolean, default=False)
    individual_terminals = db.Column(db.Boolean, default=True)
    follow_leader = db.Column(db.Boolean, default=False)
    
    # Communication settings
    chat_enabled = db.Column(db.Boolean, default=False)
    transcript_logging = db.Column(db.Boolean, default=False)
    
    # Room policies
    allow_late_join = db.Column(db.Boolean, default=True)
    require_instructor = db.Column(db.Boolean, default=False)
    time_window = db.Column(db.Integer, nullable=True)  # minutes
    
    # Roles and permissions
    roles = db.Column(JSON, default=lambda: ['Leader', 'Observer', 'Operator'])
    
    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    simulation = db.relationship('Simulation', backref='collaboration_setting')
    class_ref = db.relationship('Class', backref='collaboration_settings')
    created_by_admin = db.relationship('Admin', backref='collaboration_settings')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'simulation_id': self.simulation_id,
            'class_id': self.class_id,
            'collaboration_enabled': self.collaboration_enabled,
            'team_size': self.team_size,
            'shared_terminal': self.shared_terminal,
            'individual_terminals': self.individual_terminals,
            'follow_leader': self.follow_leader,
            'chat_enabled': self.chat_enabled,
            'transcript_logging': self.transcript_logging,
            'allow_late_join': self.allow_late_join,
            'require_instructor': self.require_instructor,
            'time_window': self.time_window,
            'roles': self.roles or ['Leader', 'Observer', 'Operator'],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class CollaborationLobby(db.Model):
    """Store active collaboration lobbies in database for persistence"""
    __tablename__ = 'collaboration_lobbies'
    
    id = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    scenario_type = db.Column(db.String(50), default='medium')
    scenario_id = db.Column(db.String(100), default='network')
    max_participants = db.Column(db.Integer, default=6)
    
    # Scoping
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)
    simulation_id = db.Column(db.Integer, db.ForeignKey('simulations.id'), nullable=True)
    
    # Creator information
    creator_id = db.Column(db.String(50), nullable=False)
    creator_name = db.Column(db.String(255), nullable=False)
    creator_profile_image = db.Column(db.Text, nullable=True)
    
    # State
    is_active = db.Column(db.Boolean, default=True)
    is_locked = db.Column(db.Boolean, default=False)
    
    # Session data
    participants = db.Column(JSON, default=dict)
    network_state = db.Column(JSON, default=dict)
    device_locks = db.Column(JSON, default=dict)
    cli_history = db.Column(JSON, default=dict)
    progress = db.Column(JSON, default=dict)
    chat_history = db.Column(JSON, default=list)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    class_ref = db.relationship('Class', backref='collaboration_lobbies')
    simulation = db.relationship('Simulation', backref='collaboration_lobbies')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'scenario_type': self.scenario_type,
            'scenario_id': self.scenario_id,
            'max_participants': self.max_participants,
            'class_id': self.class_id,
            'simulation_id': self.simulation_id,
            'creator_id': self.creator_id,
            'creator_name': self.creator_name,
            'creator_profile_image': self.creator_profile_image,
            'is_active': self.is_active,
            'is_locked': self.is_locked,
            'participants': self.participants or {},
            'participant_count': len(self.participants or {}),
            'network_state': self.network_state or {},
            'device_locks': self.device_locks or {},
            'cli_history': self.cli_history or {},
            'progress': self.progress or {},
            'recent_chat': (self.chat_history or [])[-5:] if self.chat_history else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        }
    
    def get_participant_count(self):
        """Get active participant count"""
        if not self.participants:
            return 0
        return len([p for p in self.participants.values() if p.get('is_active', True)])
    
    def is_joinable(self):
        """Check if lobby can accept new participants"""
        return (self.is_active and 
                not self.is_locked and 
                self.get_participant_count() < self.max_participants)


class TeamAssignment(db.Model):
    """Store team assignments for collaborative sessions"""
    __tablename__ = 'team_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    simulation_id = db.Column(db.Integer, db.ForeignKey('simulations.id'), nullable=True)
    lobby_id = db.Column(db.String(8), db.ForeignKey('collaboration_lobbies.id'), nullable=True)
    
    # Team configuration
    team_name = db.Column(db.String(255), nullable=False)
    team_members = db.Column(JSON, nullable=False)  # List of user IDs
    team_leader = db.Column(db.String(50), nullable=True)  # User ID of team leader
    
    # Assignment metadata
    created_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    class_ref = db.relationship('Class', backref='team_assignments')
    simulation = db.relationship('Simulation', backref='team_assignments')
    lobby = db.relationship('CollaborationLobby', backref='team_assignments')
    created_by_admin = db.relationship('Admin', backref='team_assignments')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'class_id': self.class_id,
            'simulation_id': self.simulation_id,
            'lobby_id': self.lobby_id,
            'team_name': self.team_name,
            'team_members': self.team_members or [],
            'team_leader': self.team_leader,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }