"""Route guard decorators to strictly separate instructor and user routes.

These enforce:
 - Instructor routes: only Instructor model instances with session namespace 'instructor'.
 - User routes: only regular users (non-Instructor) with namespace 'user'.
 - Prevents accidental cross-access when a session persists.
"""
from functools import wraps
from flask import session, redirect, flash, request, url_for
from flask_login import current_user

def instructor_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        from instructor.models.user import Instructor
        if not current_user.is_authenticated:
            flash('Please log in as instructor.', 'warning')
            return redirect('/instructor/login?next=' + request.path)
        if not isinstance(current_user, Instructor) or session.get('auth_namespace') != 'instructor':
            flash('Instructor privileges required.', 'error')
            return redirect('/instructor/login?next=' + request.path)
        return view_func(*args, **kwargs)
    return wrapper

def user_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        # Block instructors entirely from user routes
        from instructor.models.user import Instructor
        if current_user.is_authenticated and isinstance(current_user, Instructor):
            flash('Instructors cannot access student pages.', 'warning')
            return redirect('/instructor/')
        # Accept either Flask-Login user or session user with namespace
        if current_user.is_authenticated and session.get('auth_namespace') == 'user':
            return view_func(*args, **kwargs)
        if 'user_id' in session and session.get('auth_namespace') == 'user':
            return view_func(*args, **kwargs)
        flash('Please log in to continue.', 'warning')
        return redirect(url_for('user.login', next=request.path))
    return wrapper

def enforce_instructor_namespace(app):
    """Install a before_request hook that rejects Instructor objects on non-instructor paths.

    This centralizes the separation logic so individual routes can stay clean.
    Static assets, API, and websocket handshake paths are exempt.
    """
    @app.before_request
    def _separate_instructor_user_spaces():
        try:
            path = request.path or ''
            if path.startswith('/instructor'):
                return  # Let existing instructor auth checks handle it
            # Ignore obvious non-app paths
            if path.startswith(('/static/', '/socket.io')):
                return
            from instructor.models.user import Instructor
            if current_user.is_authenticated and isinstance(current_user, Instructor):
                # Instructor trying to access user area -> send to instructor root
                return redirect('/instructor/')
        except Exception:
            # Fail-safe: never block the request due to guard error
            return None

# Keep old names for backwards compatibility
instructor_required = instructor_required
enforce_instructor_namespace = enforce_instructor_namespace

__all__ = ['instructor_required', 'user_required', 'enforce_instructor_namespace', 'instructor_required', 'enforce_instructor_namespace']
