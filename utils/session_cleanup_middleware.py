"""
Session Cleanup Middleware
Prevents admin session contamination in user class routes
"""

from flask import session, request, g
from flask_login import current_user

def clean_admin_session_contamination():
    """ENHANCED: Block admin access to user routes and redirect to admin panel"""
    
    # Define user-only routes that admins should NOT access
    user_only_routes = [
        '/class/',
        '/user/',
        '/classes',
        '/dynamic/',
        '/learning/',
        '/quiz/',
        '/troubleshooting',
        '/leaderboard',
        '/profile'
    ]
    
    # Check if this is a user route
    is_user_route = any(request.path.startswith(route) for route in user_only_routes)
    
    if is_user_route and not request.path.startswith('/admin'):
        # Clear admin namespace markers from user routes
        if 'auth_namespace' in session and session['auth_namespace'] == 'admin':
            session.pop('auth_namespace', None)
            print(f"🧹 Cleaned admin auth_namespace from user route: {request.path}")
        
        # If current user is admin but accessing user routes, redirect them
        if current_user.is_authenticated:
            from admin.models.user import Admin
            if isinstance(current_user, Admin):
                print(f"🚫 REDIRECTING: Admin user {current_user.username} accessing user route: {request.path}")
                from flask import redirect, flash
                flash('Admins cannot access student portals. Use the admin panel instead.', 'warning')
                return redirect('/admin/dashboard')

def init_session_cleanup(app):
    """Initialize session cleanup middleware"""
    
    @app.before_request
    def cleanup_session_before_request():
        result = clean_admin_session_contamination()
        if result is not None:
            return result  # Return redirect if admin is blocked
    
    print("✅ Session cleanup middleware initialized")
