from __init__ import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

class User(db.Model, UserMixin):
    """
    User model for the quiz application
    """
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}  # Allow table to be redefined
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    profile_img = db.Column(db.String(128))
    totp_key = db.Column(db.String(32))
    email = db.Column(db.String(120))
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime)
    last_active = db.Column(db.DateTime)
    totp_secret = db.Column(db.String(32))
    totp_enabled = db.Column(db.Boolean, default=False)
    otp = db.Column(db.String(6))  # For storing the email OTP
    otp_generated_at = db.Column(db.DateTime)  # Timestamp when OTP was generated
    
    # Define relationship with scores - let SQLAlchemy figure out the join automatically
    scores = db.relationship('Score', backref='user', lazy=True, cascade='all, delete-orphan')
    
    # Session tracking relationship - temporarily commented out due to missing UserSession model
    # sessions = db.relationship('UserSession', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    # The relationship with classes is defined in the Class model
    # It will be available as 'enrolled_classes' attribute due to the backref
    
    def set_password(self, password):
        """Set a hashed password for the user"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Check if the password matches the stored hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_current_session(self):
        """Get the user's current active session"""
        # Temporarily disabled due to missing UserSession model
        return None
        # from user.models.user_session import UserSession
        # return UserSession.get_current_session(self.id)
    
    def create_session(self, session_id, request=None):
        """Create a new session for this user"""
        # Temporarily disabled due to missing UserSession model
        return None
        # from user.models.user_session import UserSession
        # return UserSession.create_session(self.id, session_id, request)
    
    def end_current_session(self):
        """End the user's current active session"""
        # Temporarily disabled due to missing UserSession model
        return None
        # current_session = self.get_current_session()
        # if current_session:
        #     current_session.end_session()
        # return current_session
    
    def get_session_history(self, limit=10):
        """Get user's session history"""
        # Temporarily disabled due to missing UserSession model
        return []
        # from user.models.user_session import UserSession
        # return UserSession.get_user_sessions(self.id, limit=limit)
    
    def update_session_activity(self, page=None, module_id=None, lesson_id=None, activity_type=None, details=None):
        """Update current session activity"""
        # Temporarily disabled due to missing UserSession model
        return None
        # current_session = self.get_current_session()
        # if current_session:
        #     current_session.update_activity(page, module_id, lesson_id, activity_type, details)
        # return current_session
