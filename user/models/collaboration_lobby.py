"""
Database models for collaborative troubleshooting lobby system
Persists lobby data to PostgreSQL for durability and recovery
"""

from __init__ import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship


class CollaborationLobby(db.Model):
    """Main lobby/session table for collaborative troubleshooting"""
    __tablename__ = 'collaboration_lobby'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.String(8), primary_key=True)  # 8-character lobby code
    name = db.Column(db.String(200), nullable=False)
    scenario_type = db.Column(db.String(50), nullable=False)  # 'easy', 'medium', 'hard'
    scenario_id = db.Column(db.String(100), nullable=False)  # specific scenario identifier
    max_participants = db.Column(db.Integer, default=6)
    
    # Optional class restriction (foreign key to classes table)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)
    
    # Creator/owner information
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator_name = db.Column(db.String(80), nullable=False)
    
    # Status flags
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_locked = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_activity_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = db.Column(db.DateTime, nullable=True)
    
    # Network topology state (JSON)
    network_state = db.Column(JSON, default=dict)
    
    # Team progress tracking (JSON)
    progress = db.Column(JSON, default=dict)
    
    # Relationships
    participants = db.relationship('LobbyParticipant', backref='lobby', lazy='dynamic', 
                                   cascade='all, delete-orphan')
    chat_messages = db.relationship('LobbyChatMessage', backref='lobby', lazy='dynamic',
                                    cascade='all, delete-orphan', order_by='LobbyChatMessage.timestamp')
    device_locks = db.relationship('LobbyDeviceLock', backref='lobby', lazy='dynamic',
                                   cascade='all, delete-orphan')
    cli_history = db.relationship('LobbyCLIHistory', backref='lobby', lazy='dynamic',
                                  cascade='all, delete-orphan', order_by='LobbyCLIHistory.timestamp')
    
    # Creator relationship
    creator = db.relationship('User', foreign_keys=[creator_id], backref='created_lobbies')
    
    def __repr__(self):
        return f'<CollaborationLobby {self.id}: {self.name}>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'scenario_type': self.scenario_type,
            'scenario_id': self.scenario_id,
            'max_participants': self.max_participants,
            'class_id': self.class_id,
            'creator_id': self.creator_id,
            'creator_name': self.creator_name,
            'is_active': self.is_active,
            'is_locked': self.is_locked,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_activity_at': self.last_activity_at.isoformat() if self.last_activity_at else None,
            'network_state': self.network_state or {},
            'progress': self.progress or {},
            'participant_count': self.participants.filter_by(is_active=True).count(),
            'participants': [p.to_dict() for p in self.participants.filter_by(is_active=True).all()],
            'recent_chat': [msg.to_dict() for msg in self.chat_messages.limit(5).all()],
            'is_joinable': self.is_active and not self.is_locked and 
                          self.participants.filter_by(is_active=True).count() < self.max_participants
        }


class LobbyParticipant(db.Model):
    """Participants in a collaborative lobby"""
    __tablename__ = 'lobby_participant'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    lobby_id = db.Column(db.String(8), db.ForeignKey('collaboration_lobby.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    profile_image = db.Column(db.String(255), nullable=True)
    
    # Participant role
    role = db.Column(db.String(20), default='participant')  # 'creator', 'moderator', 'participant'
    
    # Collaboration state
    cursor_x = db.Column(db.Integer, default=0)
    cursor_y = db.Column(db.Integer, default=0)
    selected_device = db.Column(db.String(100), nullable=True)
    user_color = db.Column(db.String(7), nullable=False)  # Hex color code
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Scores
    individual_score = db.Column(db.Integer, default=0)
    team_contribution = db.Column(db.Integer, default=0)
    
    # Timestamps
    joined_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    left_at = db.Column(db.DateTime, nullable=True)
    
    # User relationship
    user = db.relationship('User', foreign_keys=[user_id], backref='lobby_participations')
    
    def __repr__(self):
        return f'<LobbyParticipant {self.username} in {self.lobby_id}>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'profile_image': self.profile_image,
            'role': self.role,
            'cursor_position': {'x': self.cursor_x, 'y': self.cursor_y},
            'selected_device': self.selected_device,
            'color': self.user_color,
            'is_active': self.is_active,
            'score': {
                'individual': self.individual_score,
                'team_contribution': self.team_contribution
            },
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        }


class LobbyChatMessage(db.Model):
    """Chat messages within a lobby"""
    __tablename__ = 'lobby_chat_message'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    lobby_id = db.Column(db.String(8), db.ForeignKey('collaboration_lobby.id'), nullable=False)
    user_id = db.Column(db.String(20), nullable=False)  # Can be 'system' or user ID
    username = db.Column(db.String(80), nullable=False)
    profile_image = db.Column(db.String(255), nullable=True)
    
    message = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # 'text', 'system', 'action', 'progress'
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<LobbyChatMessage {self.id} by {self.username}>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'profile_image': self.profile_image,
            'message': self.message,
            'type': self.message_type,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class LobbyDeviceLock(db.Model):
    """Device locks for exclusive editing in a lobby"""
    __tablename__ = 'lobby_device_lock'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    lobby_id = db.Column(db.String(8), db.ForeignKey('collaboration_lobby.id'), nullable=False)
    device_id = db.Column(db.String(100), nullable=False)
    
    locked_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    
    locked_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    auto_unlock_at = db.Column(db.DateTime, nullable=False)  # 5 minutes from lock
    
    # User relationship
    user = db.relationship('User', foreign_keys=[locked_by])
    
    # Unique constraint: one lock per device per lobby
    __table_args__ = (
        db.UniqueConstraint('lobby_id', 'device_id', name='unique_device_lock'),
        {'extend_existing': True}
    )
    
    def __repr__(self):
        return f'<LobbyDeviceLock {self.device_id} by {self.username}>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'device_id': self.device_id,
            'locked_by': self.locked_by,
            'username': self.username,
            'locked_at': self.locked_at.isoformat() if self.locked_at else None,
            'auto_unlock_at': self.auto_unlock_at.isoformat() if self.auto_unlock_at else None
        }


class LobbyCLIHistory(db.Model):
    """CLI command history for devices in a lobby"""
    __tablename__ = 'lobby_cli_history'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    lobby_id = db.Column(db.String(8), db.ForeignKey('collaboration_lobby.id'), nullable=False)
    device_id = db.Column(db.String(100), nullable=False)
    
    command = db.Column(db.Text, nullable=False)
    output = db.Column(db.Text, nullable=True)
    
    executed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # User relationship
    user = db.relationship('User', foreign_keys=[executed_by])
    
    def __repr__(self):
        return f'<LobbyCLIHistory {self.command[:30]} on {self.device_id}>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'command': self.command,
            'output': self.output,
            'executed_by': self.executed_by,
            'username': self.username,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
