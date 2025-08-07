from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from __init__ import db
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from flask_login import UserMixin

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
