"""Route guard decorators to strictly separate admin and user routes.

These enforce:
 - Admin routes: only Admin model instances with session namespace 'admin'.
 - User routes: only regular users (non-Admin) with namespace 'user'.
 - Prevents accidental cross-access when a session persists.
"""
from functools import wraps
from flask import session, redirect, flash, request, url_for
from flask_login import current_user

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        from admin.models.user import Admin
        if not current_user.is_authenticated:
            flash('Please log in as admin.', 'warning')
            return redirect('/admin/login?next=' + request.path)
        if not isinstance(current_user, Admin) or session.get('auth_namespace') != 'admin':
            flash('Admin privileges required.', 'error')
            return redirect('/admin/login?next=' + request.path)
        return view_func(*args, **kwargs)
    return wrapper

def user_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        # Block admins entirely from user routes
        from admin.models.user import Admin
        if current_user.is_authenticated and isinstance(current_user, Admin):
            flash('Admins cannot access student pages.', 'warning')
            return redirect('/admin/')
        # Accept either Flask-Login user or session user with namespace
        if current_user.is_authenticated and session.get('auth_namespace') == 'user':
            return view_func(*args, **kwargs)
        if 'user_id' in session and session.get('auth_namespace') == 'user':
            return view_func(*args, **kwargs)
        flash('Please log in to continue.', 'warning')
        return redirect(url_for('user.login', next=request.path))
    return wrapper

def enforce_admin_namespace(app):
    """Install a before_request hook that rejects Admin objects on non-admin paths.

    This centralizes the separation logic so individual routes can stay clean.
    Static assets, API, and websocket handshake paths are exempt.
    """
    @app.before_request
    def _separate_admin_user_spaces():
        try:
            path = request.path or ''
            if path.startswith('/admin'):
                return  # Let existing admin auth checks handle it
            # Ignore obvious non-app paths
            if path.startswith(('/static/', '/socket.io')):
                return
            from admin.models.user import Admin
            if current_user.is_authenticated and isinstance(current_user, Admin):
                # Admin trying to access user area -> send to admin root
                return redirect('/admin/')
        except Exception:
            # Fail-safe: never block the request due to guard error
            return None

__all__ = ['admin_required', 'user_required', 'enforce_admin_namespace']
