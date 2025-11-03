"""
Authentication utilities for handling both instructor and user access
"""

from functools import wraps
from flask import session, redirect, url_for, flash, request
from flask_login import current_user

def flexible_login_required(f):
    """
    UPDATED: Decorator that BLOCKS instructor access to user routes 
    Only allows regular users to access user routes for proper separation
    TEMPORARY: Allow instructor access for debugging assignments
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            print(f"[AUTH] flexible_login_required: path={request.path}")
            print(f"[AUTH] current_user.is_authenticated={getattr(current_user, 'is_authenticated', None)}")
            print(f"[AUTH] session keys={list(session.keys())}")
        except Exception as _e:
            # Avoid breaking the route from debug logging
            print(f"[AUTH][WARN] flexible_login_required pre-log failed: {_e}")
        # TEMPORARY: Allow instructor access for debugging - comment out the block below
        # FIRST: Block instructor access to user routes
        if False and current_user.is_authenticated:  # Temporarily disabled
            from instructor.models.user import Instructor
            if isinstance(current_user, Instructor):
                # Instructor trying to access user route - block it
                print(f"🚫 BLOCKED: Instructor {current_user.username} attempting to access user route: {request.path}")
                flash('Instructors cannot access student portals. Please use the instructor panel instead.', 'warning')
                return redirect('/instructor/')
        
        # Check if regular user is authenticated via Flask-Login
        if current_user.is_authenticated:
            from instructor.models.user import Instructor
            # TEMPORARY: Allow instructor access for debugging
            try:
                print(f"[AUTH] Flask-Login authenticated as: {getattr(current_user, 'username', None)} (type={type(current_user).__name__}) -> allow")
            except Exception:
                print("[AUTH] Flask-Login user detected -> allow")
            return f(*args, **kwargs)
        
        # Check if user is in session (user authentication)
        if 'user_id' in session:
            print(f"[AUTH] Session auth found user_id={session.get('user_id')} -> allow")
            return f(*args, **kwargs)
        
        # No authentication found - redirect to user login
        try:
            print(f"[AUTH] No auth found -> redirect to user.login with next={request.url}")
        except Exception:
            print("[AUTH] No auth found -> redirect to user.login")
        flash('You need to log in first!', 'error')
        return redirect(url_for('user.login', next=request.url))
    
    return decorated_function

def get_current_user_context():
    """
    Get current user context for templates, handling both instructor and user authentication
    FIXED: Prevents instructor session contamination in user templates
    """
    user_context = {
        'is_authenticated': False,
        'is_instructor': False,
        'user': None,
        'user_id': None,
        'username': None,
        'profile_img': None  # Add profile_img to the context
    }
    
    print(f"[DEBUG] get_current_user_context: Starting with default context")
    
    # Check Flask-Login authentication (instructor or user)
    if current_user.is_authenticated:
        print(f"[DEBUG] Flask-Login user authenticated: {current_user.username}")
        user_context['is_authenticated'] = True
        user_context['user_id'] = current_user.id
        user_context['username'] = current_user.username
        
        # STRICT instructor check - only Instructor model instances are instructors
        from instructor.models.user import Instructor
        if isinstance(current_user, Instructor):
            print(f"[DEBUG] Instructor user detected: {current_user.username}")
            user_context['is_instructor'] = True
            # CRITICAL FIX: Do NOT pass instructor object as 'user' to prevent contamination
            # Instructor templates can use current_user directly
            user_context['user'] = None  # Prevents instructor data bleeding into user templates
            
            # Try to find a corresponding regular user account with the same username
            # This allows instructors to have profile pictures when viewing student interfaces
            from user.models.user import User
            regular_user = User.query.filter_by(username=current_user.username).first()
            if regular_user and regular_user.profile_img:
                print(f"[DEBUG] Found matching regular user with profile: {regular_user.profile_img}")
                user_context['profile_img'] = regular_user.profile_img
            else:
                print(f"[DEBUG] No matching regular user or no profile image")
                user_context['profile_img'] = getattr(current_user, 'profile_img', None)
        else:
            print(f"[DEBUG] Regular user detected: {current_user.username}")
            # Regular user - safe to pass user object
            user_context['user'] = current_user
            user_context['profile_img'] = getattr(current_user, 'profile_img', None)
            print(f"[DEBUG] Regular user profile_img: {user_context['profile_img']}")
    
    # Check session-based authentication (user only)
    elif 'user_id' in session:
        print(f"[DEBUG] Session-based authentication found: user_id={session['user_id']}")
        from user.models.user import User
        user = User.query.get(session['user_id'])
        if user:
            print(f"[DEBUG] Session user found: {user.username}, profile_img: {user.profile_img}")
            user_context['is_authenticated'] = True
            user_context['user'] = user
            user_context['user_id'] = user.id
            user_context['username'] = user.username
            user_context['profile_img'] = getattr(user, 'profile_img', None)
            user_context['is_instructor'] = False
    else:
        print(f"[DEBUG] No authentication found")
    
    print(f"[DEBUG] Final user_context: {user_context}")
    return user_context
