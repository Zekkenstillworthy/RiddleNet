from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from __init__ import db
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from flask_login import UserMixin
import secrets

class InstructorUser(db.Model, UserMixin):
    """
    Instructor User model - Separate model for instructor operations to avoid conflicts
    This model now uses the 'instructor_users' table to avoid conflicts with the regular 'user' table
    """
    __tablename__ = 'instructor_users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(150), nullable=False)
    email = Column(String(150), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    totp_key = Column(String(32), nullable=True)
    profile_img = Column(String(150), nullable=True)
    is_instructor = Column(Boolean, default=False)
    user_type = Column(String(20), default='student')  # student, instructor, superinstructor
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, nullable=True)
    force_password_change = Column(Boolean, default=False)
    notes = Column(db.Text, nullable=True)
    
    # NO RELATIONSHIPS - avoid conflicts with the User model
    # Use explicit queries when needed
    
    def get_scores(self):
        """Get scores for this user via explicit query"""
        from instructor.models.score import InstructorScore
        return InstructorScore.query.filter_by(user_id=self.id).all()
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'user_type': self.user_type,
            'status': self.status,
            'is_instructor': self.is_instructor,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'last_active': self.last_active.strftime('%Y-%m-%d %H:%M:%S') if self.last_active else None,
            'has_2fa': bool(self.totp_key),
            'notes': self.notes
        }

# Define the Instructor model to match your 'instructor' table
class Instructor(db.Model, UserMixin):
    __tablename__ = 'instructor'  # Match actual table name
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=True)
    role = db.Column(db.String(50), default='instructor')
    profile_img = db.Column(db.String(150), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Removed columns that don't exist in the actual table:
    # first_name, last_name, totp_key, force_password_change, notes

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'last_login': self.last_login.strftime('%Y-%m-%d %H:%M:%S') if self.last_login else None,
        }

class InstructorPasswordReset(db.Model):
    """
    Model for storing password reset tokens for instructor users
    """
    __tablename__ = 'instructor_password_resets'
    
    id = db.Column(db.Integer, primary_key=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    used_at = db.Column(db.DateTime, nullable=True)
    
    # Relationship to instructor user
    instructor = db.relationship('Instructor', backref=db.backref('password_resets', lazy=True))
    
    def __init__(self, instructor_id, expiry_hours=1):
        self.instructor_id = instructor_id
        self.token = secrets.token_urlsafe(32)
        self.expires_at = datetime.utcnow() + timedelta(hours=expiry_hours)
    
    @property
    def is_expired(self):
        """Check if the token has expired"""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if the token is valid (not used and not expired)"""
        return not self.used and not self.is_expired
    
    def mark_as_used(self):
        """Mark the token as used"""
        self.used = True
        self.used_at = datetime.utcnow()
        db.session.commit()
    
    @classmethod
    def create_token(cls, instructor_id, expiry_hours=1):
        """Create a new password reset token for an instructor user"""
        # Invalidate any existing tokens for this instructor
        existing_tokens = cls.query.filter_by(instructor_id=instructor_id, used=False).all()
        for token in existing_tokens:
            token.used = True
            token.used_at = datetime.utcnow()
        
        # Create new token
        new_token = cls(instructor_id=instructor_id, expiry_hours=expiry_hours)
        db.session.add(new_token)
        db.session.commit()
        return new_token
    
    @classmethod
    def get_valid_token(cls, token_string):
        """Get a valid token by token string"""
        token = cls.query.filter_by(token=token_string).first()
        if token and token.is_valid:
            return token
        return None
