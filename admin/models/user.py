from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from __init__ import db
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from flask_login import UserMixin
import secrets

class AdminUser(db.Model, UserMixin):
    """
    Admin User model - Separate model for admin operations to avoid conflicts
    This model now uses the 'admin_users' table to avoid conflicts with the regular 'user' table
    """
    __tablename__ = 'admin_users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(150), nullable=False)
    email = Column(String(150), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    totp_key = Column(String(32), nullable=True)
    profile_img = Column(String(150), nullable=True)
    is_admin = Column(Boolean, default=False)
    is_instructor = Column(Boolean, default=False)
    user_type = Column(String(20), default='student')  # student, instructor, admin
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, nullable=True)
    force_password_change = Column(Boolean, default=False)
    notes = Column(db.Text, nullable=True)
    
    # NO RELATIONSHIPS - avoid conflicts with the User model
    # Use explicit queries when needed
    
    def get_scores(self):
        """Get scores for this user via explicit query"""
        from admin.models.score import AdminScore
        return AdminScore.query.filter_by(user_id=self.id).all()
    
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
            'is_admin': self.is_admin,
            'is_instructor': self.is_instructor,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'last_active': self.last_active.strftime('%Y-%m-%d %H:%M:%S') if self.last_active else None,
            'has_2fa': bool(self.totp_key),
            'notes': self.notes
        }

# Define the Admin model to match your 'admin' table
class Admin(db.Model, UserMixin):
    __tablename__ = 'admin'  # Match actual table name
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=True)
    role = db.Column(db.String(50), default='admin')
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

class AdminPasswordReset(db.Model):
    """
    Model for storing password reset tokens for admin users
    """
    __tablename__ = 'admin_password_resets'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    used_at = db.Column(db.DateTime, nullable=True)
    
    # Relationship to admin user
    admin = db.relationship('Admin', backref=db.backref('password_resets', lazy=True))
    
    def __init__(self, admin_id, expiry_hours=1):
        self.admin_id = admin_id
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
    def create_token(cls, admin_id, expiry_hours=1):
        """Create a new password reset token for an admin user"""
        # Invalidate any existing tokens for this admin
        existing_tokens = cls.query.filter_by(admin_id=admin_id, used=False).all()
        for token in existing_tokens:
            token.used = True
            token.used_at = datetime.utcnow()
        
        # Create new token
        new_token = cls(admin_id=admin_id, expiry_hours=expiry_hours)
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
