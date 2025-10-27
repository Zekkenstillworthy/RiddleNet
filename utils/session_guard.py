"""
Session Guard Middleware - Enforces single-device login policy
"""
from flask import session, redirect, url_for, flash, request, jsonify
from functools import wraps
from user.models.user_session import UserSession
from instructor.models.instructor_session import InstructorSession
from flask_login import current_user, logout_user
from __init__ import db
import logging

logger = logging.getLogger(__name__)


def validate_user_session():
    """
    Validate that the current user session is still active and is the only active session
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not current_user.is_authenticated:
        return True, None  # Not authenticated, no session to validate
    
    auth_namespace = session.get('auth_namespace')
    session_token = session.get('session_token')
    
    print(f"[LOCK] Session validation: user_id={current_user.id}, namespace={auth_namespace}, token={'Yes' if session_token else 'NO'}")
    
    if not session_token:
        logger.warning(f"No session_token found for authenticated user {current_user.id}")
        print(f"[ERROR] Session validation failed: No session token")
        return False, "Session token missing. Please log in again."
    
    # Validate based on namespace
    if auth_namespace == 'user':
        db_session = UserSession.get_session_by_token(session_token)
        
        if not db_session:
            logger.warning(f"User {current_user.id} session token {session_token[:8]}... not found in database")
            print(f"[ERROR] Session invalid: Token not found in database")
            return False, "Your session has been terminated. Please log in again."
        
        if db_session.user_id != current_user.id:
            logger.error(f"Session token mismatch: token belongs to user {db_session.user_id} but current_user is {current_user.id}")
            print(f"[ERROR] Session invalid: User ID mismatch")
            return False, "Session validation failed. Please log in again."
        
        if db_session.is_expired():
            logger.info(f"User {current_user.id} session expired")
            print(f"[ERROR] Session invalid: Expired")
            db_session.terminate()
            db.session.commit()
            return False, "Your session has expired. Please log in again."
        
        # Update last activity
        db_session.update_activity()
        db.session.commit()
        print(f"[OK] Session valid: Updated activity")
        
        return True, None
    
    elif auth_namespace == 'instructor':
        db_session = InstructorSession.get_session_by_token(session_token)
        
        if not db_session:
            logger.warning(f"Instructor {current_user.id} session token {session_token[:8]}... not found in database")
            print(f"[ERROR] Session invalid: Token not found in database")
            return False, "Your session has been terminated. Please log in again."
        
        if db_session.instructor_id != current_user.id:
            logger.error(f"Session token mismatch: token belongs to instructor {db_session.instructor_id} but current_user is {current_user.id}")
            print(f"[ERROR] Session invalid: Instructor ID mismatch")
            return False, "Session validation failed. Please log in again."
        
        if db_session.is_expired():
            logger.info(f"Instructor {current_user.id} session expired")
            print(f"[ERROR] Session invalid: Expired")
            db_session.terminate()
            db.session.commit()
            return False, "Your session has expired. Please log in again."
        
        # Update last activity
        db_session.update_activity()
        db.session.commit()
        print(f"[OK] Session valid: Updated activity")
        
        return True, None
    
    return True, None  # Unknown namespace, let other auth mechanisms handle it


def register_session_guard(app, exempt_paths=None):
    """Attach the global before_request session guard to the given app."""
    from flask import request, session
    from flask_login import current_user, logout_user

    if getattr(app, "_session_guard_registered", False):
        return getattr(app, "_session_guard_callable", None)

    default_exempt_paths = {
        '/user/login', '/instructor/login',
        '/user/logout', '/instructor/logout',
        '/user/', '/instructor/', '/user', '/instructor',
        '/favicon.ico'
    }
    if exempt_paths:
        default_exempt_paths.update(exempt_paths)

    static_prefixes = ('/static/', '/admin/static/')

    @app.before_request
    def _validate_session_before_request():
        path = getattr(request, 'path', '') or ''
        print(f"[DEBUG] SessionGuard: evaluating path: {path}")

        if path.startswith(static_prefixes) or path in default_exempt_paths:
            print("[SKIP] Session guard skipped (static/exempt path)")
            return None

        if not current_user.is_authenticated:
            print("[SKIP] Session guard skipped: user not authenticated")
            return None

        is_valid, _ = validate_user_session()

        if not is_valid:
            auth_namespace = session.get('auth_namespace')
            session.clear()
            logout_user()

            if auth_namespace == 'instructor':
                return redirect(url_for('auth.login'))
            return redirect(url_for('user.login'))

        print("[OK] Session guard completed validation")
        return None

    app._session_guard_registered = True
    app._session_guard_callable = _validate_session_before_request
    print("[SHIELD] Session guard middleware registered")
    return _validate_session_before_request


def session_guard(f):
    """
    Decorator to enforce single-device login policy
    
    This decorator should be used on routes that require authentication.
    It validates that the user's session is still active and hasn't been
    terminated by a login from another device.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip validation for non-authenticated users
        if not current_user.is_authenticated:
            return f(*args, **kwargs)
        
        # Validate session
        is_valid, error_message = validate_user_session()
        
        if not is_valid:
            # Clear the session and log out
            auth_namespace = session.get('auth_namespace')
            session.clear()
            logout_user()
            
            # Determine redirect based on namespace
            if auth_namespace == 'instructor':
                flash(error_message or 'Your session has been terminated. Another device may have logged in.', 'warning')
                
                # For AJAX requests, return JSON
                if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': False,
                        'message': error_message or 'Session terminated',
                        'redirect': url_for('auth.login')
                    }), 401
                
                return redirect(url_for('auth.login'))
            else:
                flash(error_message or 'Your session has been terminated. Another device may have logged in.', 'warning')
                
                # For AJAX requests, return JSON
                if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': False,
                        'message': error_message or 'Session terminated',
                        'redirect': url_for('user.login')
                    }), 401
                
                return redirect(url_for('user.login'))
        
        return f(*args, **kwargs)
    
    return decorated_function


def check_existing_session(user_id, namespace='user'):
    """
    Check if a user already has an active session
    
    Args:
        user_id: The user's ID
        namespace: 'user' or 'instructor'
        
    Returns:
        tuple: (has_active_session, session_info_dict)
    """
    if namespace == 'user':
        active_session = UserSession.get_active_session(user_id)
    else:
        active_session = InstructorSession.get_active_session(user_id)
    
    if active_session:
        return True, {
            'ip_address': active_session.ip_address,
            'created_at': active_session.created_at.isoformat(),
            'last_activity': active_session.last_activity.isoformat(),
            'user_agent': active_session.user_agent
        }
    
    return False, None


def terminate_existing_sessions(user_id, namespace='user', except_token=None):
    """
    Terminate all existing sessions for a user
    
    Args:
        user_id: The user's ID
        namespace: 'user' or 'instructor'
        except_token: Optional token to keep active
        
    Returns:
        int: Number of sessions terminated
    """
    if namespace == 'user':
        count = UserSession.terminate_user_sessions(user_id, except_token)
    else:
        count = InstructorSession.terminate_instructor_sessions(user_id, except_token)
    
    db.session.commit()
    return count
