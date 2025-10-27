"""
Instructor Session Model - Tracks active instructor sessions to prevent concurrent logins
"""
from __init__ import db
from datetime import datetime, timedelta
from flask import request
import secrets


class InstructorSession(db.Model):
    """
    Track active instructor sessions to prevent concurrent logins from multiple devices
    """
    __tablename__ = 'instructor_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id', ondelete='CASCADE'), nullable=False)
    session_token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    ip_address = db.Column(db.String(45))  # IPv6 support
    user_agent = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationship back to instructor
    instructor = db.relationship('Instructor', backref=db.backref('sessions', lazy='dynamic', cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<InstructorSession instructor_id={self.instructor_id} token={self.session_token[:8]}... active={self.is_active}>'
    
    @staticmethod
    def create_session(instructor_id, expiry_hours=24, request_obj=None):
        """
        Create a new session for an instructor
        
        Args:
            instructor_id: ID of the instructor
            expiry_hours: Hours until session expires (default: 24)
            request_obj: Flask request object for IP/user agent
            
        Returns:
            InstructorSession object
        """
        session_token = secrets.token_urlsafe(48)
        
        new_session = InstructorSession(
            instructor_id=instructor_id,
            session_token=session_token,
            ip_address=request_obj.environ.get('REMOTE_ADDR') if request_obj else None,
            user_agent=request_obj.headers.get('User-Agent', '')[:256] if request_obj else None,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=expiry_hours),
            is_active=True
        )
        
        db.session.add(new_session)
        return new_session
    
    @staticmethod
    def get_active_session(instructor_id):
        """
        Get the active session for an instructor (if any)
        
        Args:
            instructor_id: ID of the instructor
            
        Returns:
            InstructorSession object or None
        """
        return InstructorSession.query.filter_by(
            instructor_id=instructor_id,
            is_active=True
        ).filter(
            InstructorSession.expires_at > datetime.utcnow()
        ).first()
    
    @staticmethod
    def get_session_by_token(session_token):
        """
        Get a session by its token
        
        Args:
            session_token: The session token
            
        Returns:
            InstructorSession object or None
        """
        return InstructorSession.query.filter_by(
            session_token=session_token,
            is_active=True
        ).filter(
            InstructorSession.expires_at > datetime.utcnow()
        ).first()
    
    @staticmethod
    def terminate_instructor_sessions(instructor_id, except_token=None):
        """
        Terminate all active sessions for an instructor
        
        Args:
            instructor_id: ID of the instructor
            except_token: Optional token to keep active (for the current session)
        """
        query = InstructorSession.query.filter_by(instructor_id=instructor_id, is_active=True)
        
        if except_token:
            query = query.filter(InstructorSession.session_token != except_token)
        
        sessions = query.all()
        for session in sessions:
            session.is_active = False
        
        return len(sessions)
    
    def update_activity(self):
        """Update the last activity timestamp"""
        self.last_activity = datetime.utcnow()
        db.session.add(self)
    
    def terminate(self):
        """Terminate this session"""
        self.is_active = False
        db.session.add(self)
    
    def is_expired(self):
        """Check if the session is expired"""
        return datetime.utcnow() > self.expires_at
    
    def extend_session(self, hours=24):
        """Extend the session expiry time"""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)
        self.last_activity = datetime.utcnow()
        db.session.add(self)
    
    @staticmethod
    def cleanup_expired_sessions():
        """Remove expired sessions from the database"""
        expired_sessions = InstructorSession.query.filter(
            InstructorSession.expires_at < datetime.utcnow()
        ).all()
        
        for session in expired_sessions:
            db.session.delete(session)
        
        return len(expired_sessions)
