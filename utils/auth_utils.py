"""
Authentication utilities for handling both admin and user access
"""

from functools import wraps
from flask import session, redirect, url_for, flash, request
from flask_login import current_user

def flexible_login_required(f):
    """
    Decorator that allows both admin and user access to class routes.
    Checks for admin authentication first, then user authentication.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated via Flask-Login (covers both admin and user)
        if current_user.is_authenticated:
            return f(*args, **kwargs)
        
        # Check if user is in session (user authentication)
        if 'user_id' in session:
            return f(*args, **kwargs)
        
        # No authentication found - redirect appropriately
        # If accessing from admin area, redirect to admin login
        if request.path.startswith('/class/') and request.referrer and '/admin' in request.referrer:
            flash('Please log in to access the admin area', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        # Otherwise, redirect to user login
        flash('You need to log in first!', 'error')
        return redirect(url_for('user.login', next=request.url))
    
    return decorated_function

def get_current_user_context():
    """
    Get current user context for templates, handling both admin and user authentication
    """
    user_context = {
        'is_authenticated': False,
        'is_admin': False,
        'user': None,
        'user_id': None,
        'username': None
    }
    
    # Check Flask-Login authentication (admin or user)
    if current_user.is_authenticated:
        user_context['is_authenticated'] = True
        user_context['user'] = current_user
        user_context['user_id'] = current_user.id
        user_context['username'] = current_user.username
        
        # Check if it's an admin user
        from admin.models.user import Admin
        if isinstance(current_user, Admin):
            user_context['is_admin'] = True
        elif hasattr(current_user, 'is_admin') and current_user.is_admin:
            user_context['is_admin'] = True
    
    # Check session-based authentication (user only)
    elif 'user_id' in session:
        from user.models.user import User
        user = User.query.get(session['user_id'])
        if user:
            user_context['is_authenticated'] = True
            user_context['user'] = user
            user_context['user_id'] = user.id
            user_context['username'] = user.username
            user_context['is_admin'] = False
    
    return user_context
