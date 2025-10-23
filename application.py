
import os
import sys

# Ensure the application directory is in the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Set up environment for production
os.environ.setdefault('FLASK_ENV', 'production')

# Import the application factory
from __init__ import create_app, db

# Create the application instance
template_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
application = create_app({
    'TEMPLATE_FOLDER': template_dir
})

# Initialize SocketIO for the application
from socket_manager import socketio, init_socketio
init_socketio(application)

# Set up application context for database operations
ctx = application.app_context()
ctx.push()

# Create database tables
with application.app_context():
    db.create_all()

# Configure CORS for admin topology and troubleshooting
from flask_cors import CORS
cors = CORS(application, resources={
    r"/admin/topology/*": {"origins": "*"},
    r"/admin/troubleshooting/*": {"origins": "*"}
})

# Set up instance path
instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
os.makedirs(instance_path, exist_ok=True)

# Initialize session cleanup middleware
try:
    from utils.session_cleanup_middleware import init_session_cleanup
    init_session_cleanup(application)
    print("✅ Session cleanup middleware initialized")
except ImportError as e:
    print(f"⚠️ Could not initialize session cleanup middleware: {e}")

# Initialize login manager
from flask_login import LoginManager
login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'user.login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """Enhanced user_loader with proper session isolation and poisoning prevention"""
    from instructor.models.user import Instructor
    from user.models import User
    from flask import session
    
    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        print(f"[SECURITY] Invalid user_id format: {user_id}")
        return None
    
    auth_namespace = session.get('auth_namespace', 'unknown')
    
    # CRITICAL FIX: Strict namespace validation with no fallback
    if auth_namespace == 'instructor':
        user = db.session.get(Instructor, user_id_int)
        if user:
            # Verify the loaded user is actually an Instructor instance
            if not isinstance(user, Instructor):
                print(f"[SECURITY] Namespace poisoning: Expected Instructor, got {type(user)}")
                session.clear()
                return None
            print(f"[AUTH] Loaded instructor user: {user.username} (ID: {user_id_int})")
            return user
        return None
    
    elif auth_namespace == 'user':
        user = db.session.get(User, user_id_int)
        if user:
            # Verify the loaded user is actually a User instance
            if not isinstance(user, User):
                print(f"[SECURITY] Namespace poisoning: Expected User, got {type(user)}")
                session.clear()
                return None
            print(f"[AUTH] Loaded user: {user.username} (ID: {user_id_int})")
            return user
        return None
    
    else:
        # NO FALLBACK - if namespace is invalid, reject the session
        print(f"[SECURITY] Invalid or missing auth_namespace: {auth_namespace}")
        session.clear()
        return None

# Import and register all blueprints
def register_blueprints():
    """Register all application blueprints"""
    import importlib
    
    # User API blueprints
    try:
        from user.api import api_blueprint as user_api_blueprint
        application.register_blueprint(user_api_blueprint, url_prefix='/api')
        
        from user.api.topology_progress_api import topology_progress_bp
        application.register_blueprint(topology_progress_bp)
        
        from user.routes.troubleshooting_routes import troubleshooting_bp
        application.register_blueprint(troubleshooting_bp)
        
        from user.routes.quiz_routes import quiz_bp
        application.register_blueprint(quiz_bp)
        
        from user.routes.collaborative_troubleshooting_api import collaborative_troubleshooting_api_bp
        application.register_blueprint(collaborative_troubleshooting_api_bp)
        
        from user.api.feedback_api import feedback_api
        application.register_blueprint(feedback_api)
        
        from user.routes.notification_routes import notification_bp
        application.register_blueprint(notification_bp)
        
        from user.routes.assignment_routes import user_assignment_bp
        application.register_blueprint(user_assignment_bp)
        
        from user.api.enhanced_simulation_api import enhanced_simulation_api
        application.register_blueprint(enhanced_simulation_api, url_prefix='/dynamic')
        
        print("✅ User blueprints registered")
    except Exception as e:
        print(f"⚠️ Error registering user blueprints: {e}")
    
    # Admin blueprints
    admin_blueprints = [
        ('instructor.controllers.auth_controller', 'auth_bp', '/admin'),
        ('instructor.controllers.dashboard_controller', 'dashboard_bp', '/admin'),
        ('instructor.controllers.user_controller', 'user_bp', '/admin'),
        ('instructor.controllers.score_controller', 'score_bp', '/admin'),
        ('instructor.controllers.essay_controller', 'essay_bp', '/admin'),
        ('instructor.controllers.question_group_controller', 'question_group_bp', '/admin/groups'),
        ('instructor.controllers.class_controller', 'class_controller', '/admin'),
        ('instructor.controllers.class_content_controller', 'class_content_controller_old', '/admin'),
        ('instructor.controllers.lesson_editor_controller', 'lesson_editor_bp', None),
        ('instructor.controllers.enhanced_module_controller', 'enhanced_module_bp', '/admin'),
        ('instructor.controllers.module_lesson_editor_controller', 'module_lesson_editor_bp', None),
        ('instructor.controllers.audit_log_controller', 'audit_log_bp', '/admin'),
        ('instructor.controllers.notification_controller', 'notification_controller', None),
        ('instructor.controllers.lesson_controller', 'lesson_bp', '/admin'),
        ('instructor.controllers.tutorial_controller', 'tutorial_bp', None),
        ('instructor.controllers.rubric_controller', 'rubric_bp', None),
        ('instructor.controllers.admin_settings_controller', 'admin_settings_bp', None),
        ('instructor.controllers.deadline_controller', 'deadline_controller_bp', None),
        ('instructor.routes.api_routes', 'api_bp', None),
        ('instructor.routes.topology_routes', 'topology_bp', None),
        ('instructor.routes.topology_api_routes', 'topology_api_bp', None),
        ('instructor.routes.troubleshooting_routes', 'troubleshooting_bp', None),
        ('instructor.routes.troubleshooting_api_routes', 'troubleshooting_api_bp', None),
        ('instructor.routes.simulation_routes', 'admin_simulation_bp', None),
        ('instructor.routes.collaboration_api', 'admin_collaboration_api_bp', None),
        ('instructor.controllers.instructor_lab_controller', 'instructor_lab_bp', None),
        ('instructor.routes.lab_api', 'lab_api', None)
    ]
    
    for module_path, blueprint_name, url_prefix in admin_blueprints:
        try:
            module = importlib.import_module(module_path)
            blueprint = getattr(module, blueprint_name)
            application.register_blueprint(blueprint, url_prefix=url_prefix)
        except Exception as e:
            print(f"⚠️ Could not register {blueprint_name}: {e}")
    
    print("✅ Admin blueprints registered")

# Register all blueprints
register_blueprints()

# Health check endpoint for AWS
@application.route('/health')
def health_check():
    return {'status': 'healthy', 'server': 'aws'}, 200

# Add before_request handlers
from flask import request, redirect, url_for, flash, session
from flask_login import current_user

@application.before_request
def enforce_namespace_security():
    """
    CRITICAL SECURITY: Enforce namespace isolation on every request.
    This prevents session poisoning attacks where admin/user sessions cross-contaminate.
    """
    from utils.namespace_validator import log_security_event
    
    # Skip for static files and public routes
    if request.endpoint in ['static', None]:
        return None
    
    # Skip for login/logout/signup routes
    exempt_routes = [
        'auth.login', 'auth.logout', 'auth.signup', 'auth.forgot_password', 'auth.reset_password',
        'user.login', 'user.logout', 'user.index', 'user.signup', 'user.send_otp',
        'user.overview', 'health_check'
    ]
    if request.endpoint in exempt_routes:
        return None
    
    # Get request path and namespace
    path = request.path
    auth_namespace = session.get('auth_namespace', 'unknown')
    
    # Validate admin routes - STRICT enforcement
    if path.startswith('/admin'):
        if auth_namespace != 'admin':
            if current_user.is_authenticated:
                # Session poisoning detected
                log_security_event('NAMESPACE_VIOLATION', {
                    'expected': 'admin',
                    'actual': auth_namespace,
                    'user_type': type(current_user).__name__
                })
                flash('Access denied. Admin credentials required.', 'error')
                session.clear()
            return redirect(url_for('auth.login'))
        
        # Double-check user type matches namespace
        from instructor.models.user import Instructor
        if current_user.is_authenticated and not isinstance(current_user, Instructor):
            log_security_event('TYPE_MISMATCH', {
                'namespace': 'admin',
                'user_type': type(current_user).__name__
            })
            flash('Session validation failed. Please log in again.', 'error')
            session.clear()
            return redirect(url_for('auth.login'))
    
    # Validate user profile routes - STRICT enforcement
    elif '/profile' in path or '/update_profile' in path:
        if path.startswith('/users'):
            # Admin profile route
            if auth_namespace != 'admin':
                log_security_event('NAMESPACE_VIOLATION', {
                    'route': 'admin_profile',
                    'expected': 'admin',
                    'actual': auth_namespace
                })
                flash('Access denied. Admin credentials required.', 'error')
                session.clear()
                return redirect(url_for('auth.login'))
        else:
            # User profile route
            if auth_namespace != 'user':
                log_security_event('NAMESPACE_VIOLATION', {
                    'route': 'user_profile',
                    'expected': 'user',
                    'actual': auth_namespace
                })
                flash('Access denied. User credentials required.', 'error')
                session.clear()
                return redirect(url_for('user.login'))
    
    return None

@application.before_request
def check_admin_auth():
    """Admin authentication middleware"""
    if request.path.startswith('/admin'):
        exempt_routes = [
            '/admin/login', '/admin/signup', '/admin/forgot-password',
            '/admin/reset-password/', '/admin/logout', '/admin/static/',
            '/admin/topology/', '/admin/troubleshooting/'
        ]
        
        if any(request.path.startswith(route) for route in exempt_routes):
            return None
        
        if not current_user.is_authenticated:
            flash('Please log in to access the admin area', 'warning')
            next_url = (request.full_path if request.query_string else request.path).rstrip('?')
            return redirect(url_for('auth.login', next=next_url))
        
        if current_user.is_authenticated:
            from instructor.models.user import Instructor
            if not isinstance(current_user, Instructor):
                flash('Access denied. Admin credentials required.', 'error')
                next_url = (request.full_path if request.query_string else request.path).rstrip('?')
                return redirect(url_for('auth.login', next=next_url))
            
            # Update last_login for admin users
            try:
                if hasattr(current_user, 'last_login'):
                    from datetime import datetime
                    # Only update every 5 minutes to reduce DB writes
                    should_update = (
                        current_user.last_login is None or
                        (datetime.utcnow() - current_user.last_login).total_seconds() > 300
                    )
                    if should_update:
                        current_user.last_login = datetime.utcnow()
                        db.session.commit()
            except Exception as e:
                # Don't break the request if last_login update fails
                print(f"Failed to update admin last_login: {e}")

@application.before_request
def update_user_last_active():
    """Update last_active for regular users"""
    # Skip for admin routes and unauthenticated requests
    if request.path.startswith('/admin') or not current_user.is_authenticated:
        return None
    
    # Only update for regular user routes
    try:
        from instructor.models.user import InstructorUser
        from user.models.user import User
        
        # Check if it's a regular user (not admin)
        if isinstance(current_user, (InstructorUser, User)) and hasattr(current_user, 'last_active'):
            from datetime import datetime
            # Only update every 5 minutes to reduce DB writes
            should_update = (
                current_user.last_active is None or
                (datetime.utcnow() - current_user.last_active).total_seconds() > 300
            )
            if should_update:
                current_user.last_active = datetime.utcnow()
                db.session.commit()
    except Exception as e:
        # Don't break the request if last_active update fails
        print(f"Failed to update user last_active: {e}")

# Initialize database setup
try:
    from instructor.utils.database_setup import setup_database, migrate_existing_tables
    migrate_existing_tables()
    setup_database()
except Exception as e:
    print(f"⚠️ Database setup error: {e}")

print("✅ AWS Elastic Beanstalk application initialized successfully")

# For AWS EB, we need to expose the application object
# EB will look for 'application' variable in this file
if __name__ == "__main__":
    # This will only run locally, not on EB
    application.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
