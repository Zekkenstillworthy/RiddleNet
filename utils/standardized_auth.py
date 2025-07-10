"""
Standardized Authentication Utilities for RiddleNet
Consolidates all admin authentication checks into a single, reliable system
"""

from functools import wraps
from flask import request, redirect, url_for, flash, session
from flask_login import current_user
from admin.models.user import Admin


class AuthenticationManager:
    """Centralized authentication management for consistent admin checks"""
    
    @staticmethod
    def is_admin(user=None):
        """
        Standardized admin check - use this everywhere instead of custom checks
        
        Returns:
            bool: True if user is admin, False otherwise
        """
        if user is None:
            user = current_user
            
        if not user.is_authenticated:
            return False
        
        # Method 1: Check if user is instance of Admin model (primary check)
        if isinstance(user, Admin):
            return True
            
        # Method 2: Check for is_admin attribute (fallback for legacy users)
        if hasattr(user, 'is_admin') and user.is_admin:
            return True
            
        return False
    
    @staticmethod
    def get_user_type(user=None):
        """
        Get standardized user type
        
        Returns:
            str: 'admin', 'user', or 'anonymous'
        """
        if user is None:
            user = current_user
            
        if not user.is_authenticated:
            return 'anonymous'
            
        return 'admin' if AuthenticationManager.is_admin(user) else 'user'
    
    @staticmethod
    def require_admin(f):
        """
        Decorator for admin-only routes
        Replaces all existing admin decorators
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access the admin area', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            if not AuthenticationManager.is_admin():
                flash('Admin access required', 'danger')
                return redirect(url_for('auth.login'))
                
            return f(*args, **kwargs)
        return decorated_function
    
    @staticmethod
    def require_auth_flexible(f):
        """
        Decorator for routes accessible by both admin and users
        Replaces flexible_login_required
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check Flask-Login authentication
            if current_user.is_authenticated:
                return f(*args, **kwargs)
            
            # Check session-based authentication
            if 'user_id' in session:
                return f(*args, **kwargs)
            
            # Redirect to appropriate login
            if request.path.startswith('/admin') or (request.referrer and '/admin' in request.referrer):
                return redirect(url_for('auth.login', next=request.url))
            else:
                return redirect(url_for('user.login', next=request.url))
                
        return decorated_function
    
    @staticmethod
    def get_template_context():
        """
        Get standardized user context for templates
        Replaces get_current_user_context
        """
        user_type = AuthenticationManager.get_user_type()
        
        context = {
            'is_authenticated': current_user.is_authenticated,
            'is_admin': user_type == 'admin',
            'user_type': user_type,
            'user': current_user if current_user.is_authenticated else None,
            'user_id': current_user.id if current_user.is_authenticated else None,
            'username': getattr(current_user, 'username', None) if current_user.is_authenticated else None
        }
        
        # Add session-based user info for legacy support
        if not context['is_authenticated'] and 'user_id' in session:
            from user.models.user import User
            user = User.query.get(session['user_id'])
            if user:
                context.update({
                    'is_authenticated': True,
                    'user': user,
                    'user_id': user.id,
                    'username': user.username,
                    'is_admin': False
                })
        
        return context


# Convenience functions for backward compatibility
def is_admin(user=None):
    """Shorthand for AuthenticationManager.is_admin()"""
    return AuthenticationManager.is_admin(user)

def require_admin(f):
    """Shorthand for AuthenticationManager.require_admin()"""
    return AuthenticationManager.require_admin(f)

def require_auth_flexible(f):
    """Shorthand for AuthenticationManager.require_auth_flexible()"""
    return AuthenticationManager.require_auth_flexible(f)

def get_template_context():
    """Shorthand for AuthenticationManager.get_template_context()"""
    return AuthenticationManager.get_template_context()
