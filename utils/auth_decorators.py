"""
Authentication decorators for RiddleNet
Provides secure access control for admin functions
"""

from functools import wraps
from flask import jsonify, request, current_app
from flask_login import current_user

def admin_required(f):
    """
    Decorator to ensure only authenticated admin users can access endpoints
    Supports multiple admin validation methods for flexibility
    ENHANCED: No longer relies on session namespace for admin validation
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("=" * 80)
        print(f"🚨 ADMIN_REQUIRED DECORATOR CALLED FOR: {request.path}")
        print("=" * 80)
        print(f"🔍 Admin decorator: current_user={current_user}")
        print(f"🔍 Admin decorator: is_authenticated={current_user.is_authenticated}")
        print(f"🔍 Admin decorator: user type={type(current_user)}")
        print(f"🔍 Admin decorator: request path={request.path}")
        
        if not current_user.is_authenticated:
            print("❌ Admin decorator: User not authenticated, redirecting to login")
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            # For admin routes, redirect to admin login instead of user login
            from flask import redirect, url_for, session
            session['admin_login_redirect'] = request.url
            return redirect(url_for('auth.login'))
        
        # Check multiple admin validation methods
        is_admin = False
        
        # Method 1: Check Admin model instance (MOST RELIABLE)
        try:
            from admin.models.user import Admin
            if isinstance(current_user, Admin):
                is_admin = True
                print(f"✅ Admin decorator: Admin model instance detected for {current_user.username}")
                current_app.logger.debug(f"Admin validation successful: {current_user.username} (Admin model instance)")
        except ImportError:
            pass
        
        # Method 2: Check is_admin attribute
        if not is_admin and hasattr(current_user, 'is_admin') and current_user.is_admin:
            is_admin = True
            print(f"✅ Admin decorator: is_admin=True for {current_user.username}")
            current_app.logger.debug(f"Admin validation successful: {current_user.username} (is_admin=True)")
        
        # Method 3: Check role attribute
        if not is_admin and hasattr(current_user, 'role') and current_user.role in ['admin', 'super_admin']:
            is_admin = True
            print(f"✅ Admin decorator: role={current_user.role} for {current_user.username}")
            current_app.logger.debug(f"Admin validation successful: {current_user.username} (role={current_user.role})")
        
        # Method 4: Check if user ID is in admin table (FALLBACK)
        if not is_admin:
            try:
                from admin.models.user import Admin
                admin_user = Admin.query.filter_by(username=current_user.username).first()
                if admin_user:
                    is_admin = True
                    print(f"✅ Admin decorator: Found in admin table for {current_user.username}")
                    current_app.logger.debug(f"Admin validation successful: {current_user.username} (found in admin table)")
            except Exception as e:
                print(f"❌ Admin decorator: Admin table lookup failed: {e}")
                current_app.logger.warning(f"Admin table lookup failed: {e}")
        
        if not is_admin:
            print(f"❌ Admin decorator: Admin validation failed for user: {getattr(current_user, 'username', 'unknown')}")
            current_app.logger.warning(f"Admin validation failed for user: {getattr(current_user, 'username', 'unknown')}")
            if request.is_json:
                return jsonify({'error': 'Admin access required'}), 403
            # For admin routes, redirect to admin login instead of user login
            from flask import redirect, url_for, session
            session['admin_login_redirect'] = request.url
            return redirect(url_for('auth.login'))
        
        print(f"✅ Admin decorator: Access granted for {current_user.username}")
        return f(*args, **kwargs)
    return decorated_function

def api_admin_required(f):
    """
    Decorator specifically for API endpoints that require admin access
    Always returns JSON responses
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Use the same admin validation logic as admin_required
        is_admin = False
        
        try:
            from admin.models.user import Admin
            if isinstance(current_user, Admin):
                is_admin = True
        except ImportError:
            pass
        
        if not is_admin and hasattr(current_user, 'is_admin') and current_user.is_admin:
            is_admin = True
        
        if not is_admin and hasattr(current_user, 'role') and current_user.role in ['admin', 'super_admin']:
            is_admin = True
        
        if not is_admin:
            try:
                from admin.models.user import Admin
                admin_user = Admin.query.filter_by(username=current_user.username).first()
                if admin_user:
                    is_admin = True
            except Exception:
                pass
        
        if not is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    """
    Decorator to ensure only authenticated users can access endpoints
    Less strict than admin_required
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            return current_app.login_manager.unauthorized()
        
        return f(*args, **kwargs)
    return decorated_function
