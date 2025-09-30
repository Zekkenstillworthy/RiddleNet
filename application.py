"""
AWS Elastic Beanstalk Entry Point for RiddleNet
This file serves as the WSGI entry point for AWS deployment.
Elastic Beanstalk looks for 'application' variable in application.py
"""
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
    """Enhanced user_loader with proper session isolation"""
    from admin.models.user import Admin
    from user.models import User
    from flask import session
    
    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        return None
    
    auth_namespace = session.get('auth_namespace', 'unknown')
    
    if auth_namespace == 'admin':
        return db.session.get(Admin, user_id_int)
    elif auth_namespace == 'user':
        return db.session.get(User, user_id_int)
    else:
        # Fallback to user table
        return db.session.get(User, user_id_int)

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
        ('admin.controllers.auth_controller', 'auth_bp', '/admin'),
        ('admin.controllers.dashboard_controller', 'dashboard_bp', '/admin'),
        ('admin.controllers.user_controller', 'user_bp', '/admin'),
        ('admin.controllers.score_controller', 'score_bp', '/admin'),
        ('admin.controllers.essay_controller', 'essay_bp', '/admin'),
        ('admin.controllers.question_group_controller', 'question_group_bp', '/admin/groups'),
        ('admin.controllers.class_controller', 'class_controller', '/admin'),
        ('admin.controllers.class_content_controller', 'class_content_controller_old', '/admin'),
        ('admin.controllers.lesson_editor_controller', 'lesson_editor_bp', None),
        ('admin.controllers.enhanced_module_controller', 'enhanced_module_bp', '/admin'),
        ('admin.controllers.module_lesson_editor_controller', 'module_lesson_editor_bp', None),
        ('admin.controllers.audit_log_controller', 'audit_log_bp', '/admin'),
        ('admin.controllers.notification_controller', 'notification_controller', None),
        ('admin.controllers.lesson_controller', 'lesson_bp', '/admin'),
        ('admin.controllers.tutorial_controller', 'tutorial_bp', None),
        ('admin.controllers.rubric_controller', 'rubric_bp', None),
        ('admin.controllers.admin_settings_controller', 'admin_settings_bp', None),
        ('admin.routes.api_routes', 'api_bp', None),
        ('admin.routes.topology_routes', 'topology_bp', None),
        ('admin.routes.topology_api_routes', 'topology_api_bp', None),
        ('admin.routes.troubleshooting_routes', 'troubleshooting_bp', None),
        ('admin.routes.troubleshooting_api_routes', 'troubleshooting_api_bp', None),
        ('admin.routes.simulation_routes', 'admin_simulation_bp', None),
        ('admin.routes.collaboration_api', 'admin_collaboration_api_bp', None),
        ('admin.controllers.instructor_lab_controller', 'instructor_lab_bp', None),
        ('admin.routes.lab_api', 'lab_api', None)
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
from flask import request, redirect, url_for, flash
from flask_login import current_user

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
            from admin.models.user import Admin
            if not isinstance(current_user, Admin):
                flash('Access denied. Admin credentials required.', 'error')
                next_url = (request.full_path if request.query_string else request.path).rstrip('?')
                return redirect(url_for('auth.login', next=next_url))

# Initialize database setup
try:
    from admin.utils.database_setup import setup_database, migrate_existing_tables
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
