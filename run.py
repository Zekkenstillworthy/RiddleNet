import eventlet
eventlet.monkey_patch()

from __init__ import create_app, db, login_manager
from socket_manager import socketio  
import os
from user.quiz import QuizController
from flask_login import current_user
from flask import redirect, url_for, request, flash
from flask_cors import CORS
import socket_events 

template_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
app = create_app({
    'TEMPLATE_FOLDER': template_dir
})

# Configure session settings for production
# This fixes the login redirect loop by properly configuring session cookies
app.config.update(
    SESSION_COOKIE_SECURE=True,      # Only send cookies over HTTPS
    SESSION_COOKIE_HTTPONLY=True,    # Prevent JavaScript access to session cookie
    SESSION_COOKIE_SAMESITE='Lax',   # CSRF protection
    SESSION_PERMANENT=True,          # Make sessions persistent
    PERMANENT_SESSION_LIFETIME=86400 # 24 hour session lifetime
)

ctx = app.app_context()
ctx.push()

from socket_manager import init_socketio
init_socketio(app)

# Configure structured logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inject socketio instance into notification controller
try:
    from admin.controllers.notification_controller import set_socketio_instance
    set_socketio_instance(socketio)
    logger.info("✅ SocketIO instance injected into notification controller")
except ImportError as e:
    logger.warning(f"Could not inject socketio into notification controller: {e}")
except Exception as e:
    logger.error(f"Unexpected error injecting socketio: {e}", exc_info=True)

cors = CORS(app, resources={
    r"/admin/topology/*": {"origins": "*"},
    r"/admin/troubleshooting/*": {"origins": "*"}
})

instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
os.makedirs(instance_path, exist_ok=True)

# Initialize database with proper migration support
with app.app_context():
    try:
        # In production, use Flask-Migrate for schema management
        if app.config.get('FLASK_ENV') == 'production':
            logger.info("Production mode: Using Flask-Migrate for database management")
            logger.info("Run 'flask db upgrade' to apply migrations")
        else:
            # Development mode: still use create_all for convenience
            logger.info("Development mode: Creating database tables")
            db.create_all()
            logger.info("Database tables created successfully")
            
        # Run custom database setup if available
        try:
            from admin.utils.database_setup import setup_database, migrate_existing_tables
            logger.info("Running database migrations and setup...")
            migrate_existing_tables()
            setup_database()
            logger.info("Database setup completed successfully")
        except ImportError:
            logger.info("No custom database setup found, skipping")
        except Exception as e:
            logger.warning(f"Database setup completed with warnings: {e}")
            
    except Exception as e:
        logger.error(f"Database initialization error: {e}", exc_info=True)
        if app.config.get('FLASK_ENV') == 'production':
            logger.critical("Database initialization failed in production mode")
            raise  # Don't continue in production if DB setup fails
        else:
            logger.warning("Continuing with application startup despite database errors")

# Initialize session cleanup middleware
try:
    logger.info("Initializing session cleanup middleware...")
    from utils.session_cleanup_middleware import init_session_cleanup
    logger.info("Session cleanup middleware imported successfully")
    init_session_cleanup(app)
    logger.info("Session cleanup middleware initialized successfully")
except ImportError as e:
    logger.warning(f"Failed to import session cleanup middleware: {e}")
except Exception as e:
    logger.error(f"Error initializing session cleanup middleware: {e}", exc_info=True)

quiz_controller = QuizController(app)

# Register dynamic simulation routes - already registered in __init__.py
# try:
#     from user.dynamic_simulation_routes import register_dynamic_routes
#     register_dynamic_routes(app)
#     print("✅ Dynamic simulation routes registered")
# except ImportError as e:
#     print(f"⚠️ Could not register dynamic routes: {e}")

login_manager.init_app(app)
login_manager.login_view = 'user.login'  
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """ENHANCED user_loader - Proper session isolation between admin and user"""
    from admin.models.user import Admin
    from user.models import User
    from flask import request, session
    
    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        print(f"❌ Invalid user_id: {user_id}")
        return None
    
    # CRITICAL FIX: Check session namespace FIRST - this works for both HTTP and WebSocket
    auth_namespace = session.get('auth_namespace', 'unknown')
    request_path = getattr(request, 'path', '') if request else ''
    
    print(f"🔍 User loader: ID={user_id_int}, namespace={auth_namespace}, path={request_path}")
    
    # PRIORITY 1: Load admin user if session indicates admin auth (works for WebSocket + HTTP)
    if auth_namespace == 'admin':
        admin = db.session.get(Admin, user_id_int)
        if admin:
            print(f"🔐 Admin session: Loaded admin {admin.username} (ID: {user_id_int})")
            return admin
        print(f"❌ Admin session: No admin found for ID {user_id_int}")
        return None
    
    # PRIORITY 2: Load user if session indicates user auth
    elif auth_namespace == 'user':
        user = db.session.get(User, user_id_int)
        if user:
            print(f"👤 User session: Loaded user {user.username} (ID: {user_id_int})")
            return user
        print(f"❌ User session: No user found for ID {user_id_int}")
        return None
    
    # FALLBACK: Use path-based detection if no namespace in session (legacy support)
    elif request_path.startswith('/admin'):
        admin = db.session.get(Admin, user_id_int)
        if admin:
            print(f"🔐 Admin path fallback: Loaded admin {admin.username} (ID: {user_id_int})")
            return admin
        print(f"❌ Admin path fallback: No admin found for ID {user_id_int}")
        return None
    
    else:
        # Try user table as final fallback
        user = db.session.get(User, user_id_int)
        if user:
            print(f"👤 User path fallback: Loaded user {user.username} (ID: {user_id_int})")
            return user
        print(f"❌ No user found in any table for ID {user_id_int}")
        return None

# Consolidated before_request handler for better performance
@app.before_request
def before_request_handler():
    """Consolidated request handler for authentication and debugging"""
    
    # Debug logging (only in debug mode)
    if app.debug and ('/preview' in request.path or '/class-content-manager' in request.path):
        logger.debug("="*80)
        logger.debug(f"REQUEST DEBUG: {request.method} {request.path}")
        logger.debug(f"Full URL: {request.url}")
        logger.debug(f"Referrer: {request.referrer}")
        logger.debug(f"User-Agent: {request.headers.get('User-Agent', 'N/A')[:100]}")
        if request.args:
            logger.debug(f"Query params: {dict(request.args)}")
        logger.debug("="*80)
    
    # Admin authentication check
    if request.path.startswith('/admin'):
        from flask import session
        
        if app.debug:  # Only log in debug mode
            logger.debug("="*80)
            logger.debug(f"ADMIN AUTH CHECK: {request.path}")
            logger.debug(f"current_user: {current_user}")
            logger.debug(f"is_authenticated: {current_user.is_authenticated}")
            logger.debug(f"current_user type: {type(current_user)}")
            logger.debug(f"session keys: {list(session.keys())}")
            logger.debug(f"session _user_id: {session.get('_user_id', 'NOT FOUND')}")
            logger.debug(f"session auth_namespace: {session.get('auth_namespace', 'NOT FOUND')}")
            logger.debug("="*80)
        
        # Get exempt routes from configuration instead of hardcoding
        exempt_routes = app.config.get('ADMIN_EXEMPT_ROUTES', [
            '/admin/login',
            '/admin/signup',
            '/admin/forgot-password',
            '/admin/reset-password/',
            '/admin/logout',
            '/admin/static/',
            '/admin/topology/',
            '/admin/troubleshooting/'
        ])
        
        # Check if route is exempt
        if any(request.path.startswith(route) for route in exempt_routes):
            logger.debug(f"Path {request.path} is exempt, allowing through")
            return None
        
        # Check authentication
        if not current_user.is_authenticated:
            flash('Please log in to access the admin area', 'warning')
            next_url = (request.full_path if request.query_string else request.path).rstrip('?')
            return redirect(url_for('auth.login', next=next_url))
        
        # Check admin privileges
        if current_user.is_authenticated:
            from admin.models.user import Admin
            if not isinstance(current_user, Admin):
                flash('Access denied. Admin credentials required.', 'error')
                next_url = (request.full_path if request.query_string else request.path).rstrip('?')
                return redirect(url_for('auth.login', next=next_url))

# Register API blueprints with proper error handling
try:
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    from user.api import api_blueprint as user_api_blueprint
    app.register_blueprint(user_api_blueprint, url_prefix='/api')
    logger.info("User API Blueprint registered successfully")
    
    # Register additional user blueprints
    additional_blueprints = [
        ('user.api.topology_progress_api', 'topology_progress_bp', None),
        ('user.routes.troubleshooting_routes', 'troubleshooting_bp', None),
        ('user.routes.collaborative_troubleshooting_api', 'collaborative_troubleshooting_api_bp', None),
        ('user.api.feedback_api', 'feedback_api', None),
        ('user.routes.notification_routes', 'notification_bp', None),
        ('user.routes.assignment_routes', 'user_assignment_bp', None),
        ('user.api.enhanced_simulation_api', 'enhanced_simulation_api', '/dynamic'),
    ]
    
    for module_path, blueprint_name, url_prefix in additional_blueprints:
        try:
            module = __import__(module_path, fromlist=[blueprint_name])
            blueprint = getattr(module, blueprint_name)
            app.register_blueprint(blueprint, url_prefix=url_prefix)
            logger.info(f"Registered {blueprint_name} from {module_path}")
        except (ImportError, AttributeError) as e:
            logger.warning(f"Could not register {blueprint_name} from {module_path}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error registering {blueprint_name}: {e}", exc_info=True)
            
except Exception as e:
    logger.error(f"Critical error registering user API blueprints: {e}", exc_info=True)
    # Don't fail completely, continue with app initialization
        
# Register Admin Blueprints with structured error handling
logger.info("Registering Admin Blueprints...")
try:
    import importlib
    blueprints_to_register = [
        ('admin.controllers.auth_controller', 'auth_bp', '/admin', None),
        ('admin.controllers.dashboard_controller', 'dashboard_bp', '/admin', None),
        ('admin.controllers.user_controller', 'user_bp', '/admin', 'admin_user_bp'),
        ('admin.controllers.score_controller', 'score_bp', '/admin', None),
        ('admin.controllers.essay_controller', 'essay_bp', '/admin', None),
        ('admin.controllers.question_group_controller', 'question_group_bp', '/admin/groups', None),
        ('admin.controllers.class_controller', 'class_controller', '/admin', None),
        ('admin.controllers.class_content_controller', 'class_content_controller_old', '/admin', None),
        ('admin.controllers.lesson_editor_controller', 'lesson_editor_bp', None, 'lesson_editor_bp'),
        ('admin.controllers.enhanced_module_controller', 'enhanced_module_bp', '/admin', None),
        ('admin.controllers.module_lesson_editor_controller', 'module_lesson_editor_bp', None, None),
        ('admin.controllers.audit_log_controller', 'audit_log_bp', '/admin', None),
        ('admin.controllers.notification_controller', 'notification_controller', None, None),
        ('admin.controllers.lesson_controller', 'lesson_bp', '/admin', None),
        ('admin.controllers.tutorial_controller', 'tutorial_bp', None, None),
        ('admin.controllers.rubric_controller', 'rubric_bp', None, None),
        ('admin.controllers.admin_settings_controller', 'admin_settings_bp', None, None),
        ('admin.routes.api_routes', 'api_bp', None, 'admin_api_bp'),
        ('admin.routes.topology_routes', 'topology_bp', None, None),
        ('admin.routes.topology_api_routes', 'topology_api_bp', None, None),
        ('admin.routes.troubleshooting_routes', 'troubleshooting_bp', None, None),
        ('admin.routes.troubleshooting_api_routes', 'troubleshooting_api_bp', None, None),
        ('admin.routes.simulation_routes', 'admin_simulation_bp', None, 'admin_simulation_bp'),
        ('admin.routes.device_sync_api', 'device_sync_bp', None, 'device_sync_bp'),
        ('admin.routes.collaboration_api', 'admin_collaboration_api_bp', None, 'admin_collaboration_api'),
        ('admin.controllers.instructor_lab_controller', 'instructor_lab_bp', None, None),
        ('admin.routes.lab_api', 'lab_api', None, None),
        ('admin.routes.rnet_viewer_routes', 'rnet_viewer_bp', None, 'rnet_viewer_bp')
    ]
    
    successful_registrations = 0
    failed_registrations = 0
    
    for module_path, blueprint_name, url_prefix, alias_name in blueprints_to_register:
        try:
            module = importlib.import_module(module_path)
            blueprint = getattr(module, blueprint_name)
            app.register_blueprint(blueprint, url_prefix=url_prefix)
            
            # Update the blueprint's template search paths
            try:
                from utils.template_utils import ensure_blueprint_can_find_templates
                ensure_blueprint_can_find_templates(blueprint, [
                    app.template_folder,
                    os.path.join(app.template_folder, 'admin')
                ])
            except ImportError:
                pass  # Template utils not available
            
            display_name = alias_name or blueprint_name
            logger.info(f"Registered {display_name} from {module_path}")
            successful_registrations += 1
            
        except (ImportError, AttributeError) as e:
            logger.warning(f"Could not register {blueprint_name} from {module_path}: {e}")
            failed_registrations += 1
        except Exception as e:
            logger.error(f"Unexpected error registering {blueprint_name}: {e}", exc_info=True)
            failed_registrations += 1
    
    logger.info(f"Admin blueprints registration complete: {successful_registrations} successful, {failed_registrations} failed")
    
except Exception as e:
    logger.error(f"Critical error in admin blueprint registration: {e}", exc_info=True)

# Register Enhanced User Routes for User-Facing Integration
logger.info("Registering Enhanced User Routes...")
try:
    from user.routes.enhanced.hybrid_routes import enhanced_user_bp
    app.register_blueprint(enhanced_user_bp, url_prefix='/enhanced')
    logger.info("Enhanced user routes registered successfully")
except Exception as e:
    logger.error(f"Error registering enhanced user routes: {e}", exc_info=True)

# Register Progression API for sequential unlock mechanics
print("\n=== Registering Progression API ===")
try:
    from user.api.progression_api import progression_api
    app.register_blueprint(progression_api)
    print("✅ Progression API registered successfully")
    print("   • /api/progression/simulation/<id>/unlock-status - Check unlock status")
    print("   • /api/progression/learning-path/<id>/progress - Get progress")
    print("   • /api/progression/simulation/<id>/complete - Mark completed")
    print("   • /api/progression/user/achievements - Get achievements")
except Exception as e:
    print(f"❌ Error registering progression API: {e}")
    import traceback
    traceback.print_exc()

# Register User Lesson Routes
print("\n=== Registering User Lesson Routes ===")
try:
    from user.routes.lesson_routes import lesson_bp
    app.register_blueprint(lesson_bp)
    print("✅ User lesson routes registered successfully")
    print("   • /lesson/class/<id>/lesson/<id> - View lesson content")
    print("   • /lesson/class/<id>/lesson/<id>/complete - Mark lesson complete")
    print("   • /lesson/class/<id>/lesson/<id>/progress - Update reading progress")
    print("   • /lesson/class/<id>/lesson/<id>/start-simulation/<id> - Start simulation")
    print("   • /lesson/api/class/<id>/lesson/<id>/analytics - Get lesson analytics")
except Exception as e:
    print(f"❌ Error registering user lesson routes: {e}")
    import traceback
    traceback.print_exc()

# Register Enhanced User Simulation Routes
print("\n=== Registering Enhanced User Simulation Routes ===")
try:
    from user.routes.simulation_runner import user_simulation_bp
    app.register_blueprint(user_simulation_bp)
    print("✅ Enhanced user simulation routes registered successfully")
    print("   • /simulation/dashboard - Simulation dashboard for users")
    print("   • /simulation/<id> - Run specific simulation")
    print("   • /simulation/<id>/results/<attempt_id> - View simulation results")
    print("   • /simulation/api/<id>/submit-step - Submit step response")
    print("   • /simulation/api/<id>/complete - Complete simulation")
    print("   • /simulation/api/<id>/restart - Restart simulation")
except Exception as e:
    print(f"❌ Error registering enhanced user simulation routes: {e}")
    import traceback
    traceback.print_exc()

# Initialize and register dynamic class routes
print("\n=== Registering Dynamic Class Routes ===")
try:
    from admin.services.dynamic_route_registry import route_registry
    
    # Initialize the route registry with the app
    route_registry.init_app(app)
    
    # Get statistics about registered routes
    stats = route_registry.get_statistics()
    print(f"✅ Dynamic route registry initialized")
    print(f"   Total classes: {stats.get('total_classes', 0)}")
    print(f"   Registered classes: {stats.get('registered_classes', 0)}")
    print(f"   Route files: {stats.get('route_files', 0)}")
    print(f"   Registration rate: {stats.get('registration_rate', 0):.1f}%")
    
    if stats.get('registered_class_ids'):
        print(f"   Registered class IDs: {stats['registered_class_ids']}")
    
except Exception as e:
    print(f"❌ Error initializing dynamic route registry: {e}")
    print("✅ Continuing with universal template system only...")
    # Universal template system should handle all classes
    # No need for class-specific route fallback

# Print all registered routes for debugging
print("\n=== Registered Routes ===")
for rule in sorted(app.url_map.iter_rules(), key=lambda x: str(x)):
    methods = ', '.join(sorted(rule.methods)) if rule.methods else ''
    print(f"{rule.endpoint:30} {methods:20} {rule.rule}")
print("=========================\n")

# Set up Jinja2 environment to ensure it can find templates
def setup_jinja_environment():
    """Configure the Jinja2 environment to properly find templates"""
    from jinja2 import ChoiceLoader, FileSystemLoader
    
    # Get all possible template directories
    template_dirs = [
        app.template_folder,  # Main template folder
        os.path.join(app.template_folder, 'admin'),  # Admin subfolder
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'admin', 'templates')  # Admin module templates
    ]
    
    # Filter out non-existent directories
    template_dirs = [d for d in template_dirs if os.path.exists(d)]
    
    # Create loaders for each directory
    loaders = []
    if app.jinja_loader:
        loaders.append(app.jinja_loader)
    
    for template_dir in template_dirs:
        loaders.append(FileSystemLoader(template_dir))
        print(f"Added template directory to Jinja2 environment: {template_dir}")
    
    # Set up the ChoiceLoader
    if len(loaders) > 1:
        app.jinja_loader = ChoiceLoader(loaders)
        print("Created ChoiceLoader for application")

# Configure Jinja2 environment
setup_jinja_environment()

# Essential routes that should be available regardless of deployment method
import logging
from flask import send_from_directory
import os as _os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define static folder path
STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

@app.route('/media/video/<path:filename>')
def serve_video(filename):
    """Serve video files with optimized settings"""
    try:
        video_path = os.path.join(STATIC_FOLDER, 'video')
        response = send_from_directory(video_path, filename)
        
        # Set proper headers for video streaming
        response.headers['Accept-Ranges'] = 'bytes'
        response.headers['Content-Type'] = 'video/mp4'
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Range'
        
        logger.info(f"Served video file: {filename}")
        return response
    except Exception as e:
        logger.error(f"Error serving video file {filename}: {e}")
        return f"Error serving video: {filename}", 404

@app.route('/media/audio/<path:filename>')
def serve_audio(filename):
    """Serve audio files with optimized settings"""
    try:
        audio_path = os.path.join(STATIC_FOLDER, 'audio')
        response = send_from_directory(audio_path, filename)
        # Set proper headers for audio streaming
        response.headers['Accept-Ranges'] = 'bytes'
        response.headers['Content-Type'] = 'audio/mpeg'
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Range'
        
        logger.info(f"Served audio file: {filename}")
        return response
    except Exception as e:
        logger.error(f"Error serving audio file {filename}: {e}")
        return f"Error serving audio: {filename}", 404

@app.route('/health')
def health_check():
    return {'status': 'healthy', 'server': 'main'}, 200

# Debug endpoints - only register when FLASK_DEBUG is enabled
if os.getenv('FLASK_DEBUG', '').lower() in ('true', '1', 'yes'):
    @app.route('/debug/simulations')
    def debug_simulations():
        """Debug endpoint to check simulations without auth"""
        try:
            from admin.models.simulation import Simulation
            simulations = Simulation.query.limit(10).all()
            sim_list = []
            for sim in simulations:
                sim_list.append({
                    'id': sim.id,
                    'title': sim.title,
                    'is_active': getattr(sim, 'is_active', True),
                    'created_at': str(getattr(sim, 'created_at', 'Unknown'))
                })
            return {
                'total_simulations': len(sim_list),
                'simulations': sim_list
            }
        except Exception as e:
            return {'error': str(e)}, 500
    
    @app.route('/debug/routes')
    def debug_routes():
        """Debug endpoint to list all registered routes"""
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': rule.rule
            })
        return {'routes': sorted(routes, key=lambda x: x['rule'])}
        
    @app.route('/debug/auth')
    def debug_auth():
        """Debug endpoint to check current authentication state"""
        from flask_login import current_user
        from flask import session
        return {
            'is_authenticated': current_user.is_authenticated,
            'current_user_type': str(type(current_user)),
            'current_user_id': getattr(current_user, 'id', None),
            'session_keys': list(session.keys()),
            'auth_namespace': session.get('auth_namespace', 'Not set'),
            'user_id_in_session': session.get('_user_id', 'Not set')
        }
    
    @app.route('/debug/simulation/edit/<int:simulation_id>')
    def debug_simulation_edit(simulation_id):
        """Debug endpoint to access simulation edit without auth"""
        try:
            from admin.controllers.simulation_controller import SimulationController
            simulation_controller = SimulationController()
            simulation_data = simulation_controller.get_simulation_by_id(simulation_id, include_steps=True)
            
            if 'error' in simulation_data:
                return {'error': simulation_data['error']}, 404
            
            return {
                'simulation_id': simulation_id,
                'simulation_found': True,
                'simulation_title': simulation_data.get('simulation', {}).get('title', 'Unknown'),
                'message': f'Simulation {simulation_id} exists and can be edited',
                'edit_url': f'/admin/simulation/edit/{simulation_id}',
                'note': 'This is a debug endpoint. Use the proper admin route after logging in.'
            }
        except Exception as e:
            return {'error': f'Debug error: {str(e)}'}, 500

if __name__ == "__main__":


    # Removed debug/test announcement routes (/demo/announcements, /test/announcements, /api/debug/announce)
    # to prevent accidental broadcast of test system announcements in production.

    import socket as _socket



    # Database setup for development mode only
    if not app.config.get('FLASK_ENV') == 'production':
        with app.app_context():
            try:
                # Re-run database setup for development
                db.create_all()
                logger.info("Development database tables verified")
            except Exception as e:
                logger.error(f"Development database setup error: {e}")
    
    # Determine host, port and debug mode from environment
    env_port = int(_os.getenv('PORT', '5001'))
    env_host = _os.getenv('HOST', '0.0.0.0')  # Changed to 0.0.0.0 for EC2 compatibility
    debug_mode = _os.getenv('FLASK_DEBUG', '').lower() in ('true', '1', 'yes')
    
    # Use the configured port (no fallback needed in production)
    chosen_port = env_port
    chosen_host = env_host

    logger.info(f"Starting unified Flask-SocketIO server on {chosen_host}:{chosen_port}...")
    logger.info(f"Debug mode: {debug_mode}")
    logger.info("WebSocket events loaded and ready")
    logger.info("Static files will be served by Flask's built-in handler")
    
    # Start the Flask-SocketIO server
    socketio.run(
        app,
        debug=debug_mode,  # Use environment variable
        host=chosen_host,
        port=chosen_port,
        use_reloader=False,  # Disable reloader to prevent threading issues
        allow_unsafe_werkzeug=debug_mode  # Only allow in debug mode
    )


