"""
Authentication decorators for RiddleNet
Provides secure access control for admin functions
"""

from functools import wraps
from flask import jsonify, request, current_app
from flask_login import current_user

def instructor_required(f):
    """
    Decorator to ensure only authenticated instructor users can access endpoints
    Supports multiple admin validation methods for flexibility
    ENHANCED: No longer relies on session namespace for admin validation
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("=" * 80)
        print(f"🚨 ADMIN_REQUIRED DECORATOR CALLED FOR: {request.path}")
        print("=" * 80)
        print(f"[DEBUG] Admin decorator: current_user={current_user}")
        print(f"[DEBUG] Admin decorator: is_authenticated={current_user.is_authenticated}")
        print(f"[DEBUG] Admin decorator: user type={type(current_user)}")
        print(f"[DEBUG] Admin decorator: request path={request.path}")
        
        if not current_user.is_authenticated:
            print("[ERROR] Admin decorator: User not authenticated, redirecting to login")
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            # For instructor routes, redirect to admin login instead of user login
            from flask import redirect, url_for, session
            session['admin_login_redirect'] = request.url
            return redirect(url_for('auth.login'))
        
        # Check multiple admin validation methods
        is_instructor = False
        
        # Method 1: Check Instructor model instance (MOST RELIABLE)
        try:
            from instructor.models.user import Instructor
            if isinstance(current_user, Instructor):
                is_instructor = True
                print(f"[OK] Admin decorator: Instructor model instance detected for {current_user.username}")
                current_app.logger.debug(f"Admin validation successful: {current_user.username} (Instructor model instance)")
        except ImportError:
            pass
        
        # Method 2: Check is_instructor attribute
        if not is_instructor and hasattr(current_user, 'is_instructor') and current_user.is_instructor:
            is_instructor = True
            print(f"[OK] Admin decorator: is_instructor=True for {current_user.username}")
            current_app.logger.debug(f"Admin validation successful: {current_user.username} (is_instructor=True)")
        
        # Method 3: Check role attribute
        if not is_instructor and hasattr(current_user, 'role') and current_user.role in ['admin', 'super_admin']:
            is_instructor = True
            print(f"[OK] Admin decorator: role={current_user.role} for {current_user.username}")
            current_app.logger.debug(f"Admin validation successful: {current_user.username} (role={current_user.role})")
        
        # Method 4: Check if user ID is in admin table (FALLBACK)
        if not is_instructor:
            try:
                from instructor.models.user import Instructor
                admin_user = Instructor.query.filter_by(username=current_user.username).first()
                if admin_user:
                    is_instructor = True
                    print(f"[OK] Admin decorator: Found in admin table for {current_user.username}")
                    current_app.logger.debug(f"Admin validation successful: {current_user.username} (found in admin table)")
            except Exception as e:
                print(f"[ERROR] Admin decorator: Admin table lookup failed: {e}")
                current_app.logger.warning(f"Admin table lookup failed: {e}")
        
        if not is_instructor:
            print(f"[ERROR] Admin decorator: Admin validation failed for user: {getattr(current_user, 'username', 'unknown')}")
            current_app.logger.warning(f"Admin validation failed for user: {getattr(current_user, 'username', 'unknown')}")
            if request.is_json:
                return jsonify({'error': 'Admin access required'}), 403
            # For instructor routes, redirect to admin login instead of user login
            from flask import redirect, url_for, session
            session['admin_login_redirect'] = request.url
            return redirect(url_for('auth.login'))
        
        print(f"[OK] Admin decorator: Access granted for {current_user.username}")
        return f(*args, **kwargs)
    return decorated_function

def api_instructor_required(f):
    """
    Decorator specifically for API endpoints that require admin access
    Always returns JSON responses
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Use the same admin validation logic as instructor_required
        is_instructor = False
        
        try:
            from instructor.models.user import Instructor
            if isinstance(current_user, Instructor):
                is_instructor = True
        except ImportError:
            pass
        
        if not is_instructor and hasattr(current_user, 'is_instructor') and current_user.is_instructor:
            is_instructor = True
        
        if not is_instructor and hasattr(current_user, 'role') and current_user.role in ['admin', 'super_admin']:
            is_instructor = True
        
        if not is_instructor:
            try:
                from instructor.models.user import Instructor
                admin_user = Instructor.query.filter_by(username=current_user.username).first()
                if admin_user:
                    is_instructor = True
            except Exception:
                pass
        
        if not is_instructor:
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    """
    Decorator to ensure only authenticated users can access endpoints
    Less strict than instructor_required
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            return current_app.login_manager.unauthorized()
        
        return f(*args, **kwargs)
    return decorated_function

def user_login_required(f):
    """
    Decorator to require user login (alias for user_required for compatibility)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            from flask import redirect, url_for, session
            return redirect(url_for('user.login'))
        
        return f(*args, **kwargs)
    return decorated_function
