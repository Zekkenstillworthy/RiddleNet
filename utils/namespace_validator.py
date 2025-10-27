"""
Namespace Validator - Session Poisoning Prevention
====================================================
This module provides decorators and utilities to enforce strict namespace
isolation between Instructor and user sessions, preventing session poisoning attacks.
"""

from functools import wraps
from flask import session, redirect, url_for, flash, request
from flask_login import current_user


def require_namespace(namespace):
    """
    Decorator to enforce strict namespace validation on routes.
    
    Args:
        namespace (str): The required namespace ('instructor' or 'user')
    
    Usage:
        @app.route('/admin/profile')
        @login_required
        @require_namespace('instructor')
        def admin_profile():
            # This route can only be accessed with Instructor namespace
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get current namespace from session
            auth_namespace = session.get('auth_namespace', 'unknown')
            
            # Validate namespace matches requirement
            if auth_namespace != namespace:
                flash(f'Access denied. {namespace.title()} credentials required.', 'error')
                session.clear()  # Clear potentially poisoned session
                
                # Redirect to appropriate login page
                if namespace == 'instructor':
                    return redirect(url_for('auth.login'))
                else:
                    return redirect(url_for('user.login'))
            
            # Additional validation: Check current_user type matches namespace
            if current_user.is_authenticated:
                if namespace == 'instructor':
                    from instructor.models.user import Instructor
                    if not isinstance(current_user, Instructor):
                        flash('Access denied. Instructor credentials required.', 'error')
                        session.clear()
                        return redirect(url_for('auth.login'))
                
                elif namespace == 'user':
                    from user.models.user import User
                    if not isinstance(current_user, User):
                        flash('Access denied. User credentials required.', 'error')
                        session.clear()
                        return redirect(url_for('user.login'))
            
            # Namespace validated - proceed with route
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_namespace_on_request():
    """
    Flask before_request handler to validate namespace on every request.
    This provides an additional layer of protection.
    
    Usage in __init__.py or application.py:
        @app.before_request
        def check_namespace():
            validate_namespace_on_request()
    """
    # Skip validation for static files and public routes
    if request.endpoint in ['static', None]:
        return None
    
    # Skip validation for login/logout routes
    exempt_endpoints = ['auth.login', 'auth.logout', 'user.login', 'user.logout', 
                       'user.index', 'user.signup', 'auth.signup']
    if request.endpoint in exempt_endpoints:
        return None
    
    # Get request path and namespace
    path = request.path
    auth_namespace = session.get('auth_namespace', 'unknown')
    
    # Validate instructor routes
    if path.startswith('/instructor'):
        if auth_namespace != 'instructor':
            if current_user.is_authenticated:
                flash('Access denied. Instructor credentials required.', 'error')
                session.clear()
                return redirect(url_for('auth.login'))
    
    # Validate user routes (with some exceptions for Instructor access)
    elif path.startswith('/users') or path.startswith('/class'):
        # Some routes like /users/profile should be user-only
        if '/profile' in path and auth_namespace != 'user':
            if current_user.is_authenticated:
                flash('Access denied. User credentials required.', 'error')
                session.clear()
                return redirect(url_for('user.login'))
    
    return None


def clear_session_on_namespace_mismatch():
    """
    Utility function to check for namespace mismatches and clear session if found.
    
    Returns:
        bool: True if namespace is valid, False if session was cleared
    """
    if not current_user.is_authenticated:
        return True
    
    auth_namespace = session.get('auth_namespace', 'unknown')
    
    # Check if namespace matches user type
    try:
        from instructor.models.user import Instructor
        from user.models.user import User
        
        if isinstance(current_user, Instructor) and auth_namespace != 'instructor':
            print(f"[SECURITY] Namespace mismatch: Instructor user with namespace '{auth_namespace}'")
            session.clear()
            return False
        
        if isinstance(current_user, User) and auth_namespace != 'user':
            print(f"[SECURITY] Namespace mismatch: User with namespace '{auth_namespace}'")
            session.clear()
            return False
        
        return True
        
    except Exception as e:
        print(f"[SECURITY] Error validating namespace: {e}")
        session.clear()
        return False


def get_safe_namespace():
    """
    Get the current namespace with validation.
    
    Returns:
        str: 'instructor', 'user', or None if invalid
    """
    if not current_user.is_authenticated:
        return None
    
    auth_namespace = session.get('auth_namespace', 'unknown')
    
    # Validate namespace matches user type
    try:
        from instructor.models.user import Instructor
        from user.models.user import User
        
        if isinstance(current_user, Instructor):
            if auth_namespace != 'instructor':
                print(f"[SECURITY] Namespace poisoning detected: Instructor with namespace '{auth_namespace}'")
                session.clear()
                return None
            return 'instructor'
        
        if isinstance(current_user, User):
            if auth_namespace != 'user':
                print(f"[SECURITY] Namespace poisoning detected: User with namespace '{auth_namespace}'")
                session.clear()
                return None
            return 'user'
        
        print(f"[SECURITY] Unknown user type: {type(current_user)}")
        return None
        
    except Exception as e:
        print(f"[SECURITY] Error getting safe namespace: {e}")
        return None


def enforce_namespace_isolation(admin_func, user_func):
    """
    Decorator that routes to different functions based on namespace.
    
    Args:
        admin_func: Function to call for Instructor namespace
        user_func: Function to call for user namespace
    
    Usage:
        @enforce_namespace_isolation(admin_profile_view, user_profile_view)
        def profile():
            pass  # This will be replaced by admin_func or user_func
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            namespace = get_safe_namespace()
            
            if namespace == 'instructor':
                return admin_func(*args, **kwargs)
            elif namespace == 'user':
                return user_func(*args, **kwargs)
            else:
                flash('Invalid session. Please log in again.', 'error')
                session.clear()
                return redirect(url_for('user.index'))
        
        return decorated_function
    return decorator


# Security logging helper
def log_security_event(event_type, details):
    """
    Log security-related events for monitoring and auditing.
    
    Args:
        event_type (str): Type of security event
        details (dict): Additional details about the event
    """
    import logging
    from datetime import datetime
    
    logger = logging.getLogger('security')
    
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'user_id': current_user.id if current_user.is_authenticated else None,
        'username': current_user.username if current_user.is_authenticated else None,
        'namespace': session.get('auth_namespace', 'unknown'),
        'ip_address': request.environ.get('REMOTE_ADDR', 'unknown'),
        'user_agent': request.headers.get('User-Agent', 'unknown'),
        'path': request.path,
        'details': details
    }
    
    logger.warning(f"Security Event: {event_type} - {log_entry}")
    
    # Send real-time alert via WebSocket if available
    try:
        from socket_manager import socketio
        if socketio:
            socketio.emit('security_alert', log_entry, room='instructor_room')
    except:
        pass  # WebSocket not available
