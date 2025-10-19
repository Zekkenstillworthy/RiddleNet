from flask import redirect, url_for, flash, request, session
from flask_login import current_user
from functools import wraps

def instructor_login_required(f):
    """
    Custom decorator to check if the user is authenticated as an admin.
    If not, redirects to the admin login page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        if not current_user.is_authenticated:
            flash('Please log in to access the instructor area', 'warning')
            next_url = request.url  # Save the URL the user was trying to access
            return redirect(url_for('auth.login', next=next_url))
        
        # Check if user is an admin (additional check if needed)
        # Assuming instructor users have an 'is_instructor' attribute or similar
        if hasattr(current_user, 'is_instructor') and not current_user.is_instructor:
            flash('You do not have permission to access this area', 'danger')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function

def protect_instructor_routes(app):
    """
    Add a before_request handler to protect all instructor routes.
    This should be called during application setup.
    """
    @app.before_request
    def check_instructor_auth():
        # Debug output
        print(f"🔍 Protection check for path: {request.path}")
        
        # List of routes that don't require authentication (login/static files)
        exempt_routes = [
            '/static/', 
            '/instructor/login',
            '/instructor/signup',  # Add admin signup route
            '/instructor/forgot-password',  # Add forgot password route
            '/instructor/reset-password/',  # Add reset password route (with token)
            '/instructor/auth/login',
            '/instructor/auth/signup',  # Add admin auth signup route
            '/instructor/logout',
            '/instructor/auth/logout'
        ]
        
        # Special case: Allow access to landing page at exactly /instructor/ or /instructor
        if request.path == '/instructor/' or request.path == '/instructor':
            print(f"✅ Allowing access to instructor landing page")
            return None
        
        # Debug: show which routes are exempt
        is_exempt = any(request.path.startswith(route) for route in exempt_routes)
        print(f"🛡️ Path '{request.path}' is exempt: {is_exempt}")
        
        # Skip check for exempt routes
        if any(request.path.startswith(route) for route in exempt_routes):
            return None
            
        # Check if user is authenticated
        if not current_user.is_authenticated:
            if request.path.startswith('/instructor'):
                print(f"🚫 Blocking unauthenticated access to: {request.path}")
                flash('Please log in to access the instructor area', 'warning')
                return redirect(url_for('auth.login', next=request.url))