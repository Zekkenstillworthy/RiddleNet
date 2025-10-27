"""
Session Cleanup Middleware
Prevents admin session contamination in user class routes
"""

from flask import session, request, g
from flask_login import current_user

def clean_instructor_session_contamination():
    """ENHANCED: Allow admin access to all routes while preventing contamination"""
    
    # Define user-only routes that should clear admin namespace only for non-instructor users
    user_only_routes = [
        '/register',
        '/login',
        '/user/',
        '/quiz/',
        '/troubleshooting',
        '/profile'
    ]
    
    # Define routes that admins can access but should preserve admin namespace
    admin_accessible_routes = [
        '/admin',
        '/class/',
        '/classes',
        '/dynamic/',
        '/learning/'
    ]
    
    # Check if this is a route that admins can access
    is_instructor_accessible = any(request.path.startswith(route) for route in admin_accessible_routes)
    
    # Check if this is a user-only route
    is_user_only_route = any(request.path.startswith(route) for route in user_only_routes)
    
    # For admin-accessible routes, preserve instructor authentication
    if is_instructor_accessible and current_user.is_authenticated:
        from instructor.models.user import Instructor
        if isinstance(current_user, Instructor):
            # Ensure admin namespace is set for instructor users
            if 'auth_namespace' not in session or session['auth_namespace'] != 'instructor':
                session['auth_namespace'] = 'instructor'
            print(f"[AUTH] Preserving admin session for admin accessing: {request.path}")
            return
    
    # For user-only routes, clear admin namespace (but don't redirect)
    if is_user_only_route and 'auth_namespace' in session:
        if session.get('auth_namespace') == 'instructor':
            session.pop('auth_namespace', None)
            print(f"🧹 Cleaned admin auth_namespace from user-only route: {request.path}")
            return

def init_session_cleanup(app):
    """Initialize session cleanup middleware"""
    
    @app.before_request
    def cleanup_session_before_request():
        result = clean_instructor_session_contamination()
        if result is not None:
            return result  # Return redirect if admin is blocked
    
    print("[OK] Session cleanup middleware initialized")
