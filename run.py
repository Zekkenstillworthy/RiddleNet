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

ctx = app.app_context()
ctx.push()

from socket_manager import init_socketio
init_socketio(app)

# Inject socketio instance into notification controller
try:
    from admin.controllers.notification_controller import set_socketio_instance
    set_socketio_instance(socketio)
    print("✅ SocketIO instance injected into notification controller")
except ImportError as e:
    print(f"⚠️ Could not inject socketio into notification controller: {e}")

cors = CORS(app, resources={
    r"/admin/topology/*": {"origins": "*"},
    r"/admin/troubleshooting/*": {"origins": "*"}
})

instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
os.makedirs(instance_path, exist_ok=True)

with app.app_context():
    db.create_all()

# Initialize session cleanup middleware
try:
    print("🔧 Trying to import session cleanup middleware...")
    from utils.session_cleanup_middleware import init_session_cleanup
    print("🔧 Session cleanup middleware imported successfully")
    init_session_cleanup(app)
    print("🔧 Session cleanup middleware initialized")
except ImportError as e:
    print(f"❌ Failed to import session cleanup middleware: {e}")
except Exception as e:
    print(f"❌ Error initializing session cleanup middleware: {e}")

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

from utils.route_guards import enforce_admin_namespace
enforce_admin_namespace(app)

@app.before_request
def check_admin_auth():
    if request.path.startswith('/admin'):
        from flask import session
        print("=" * 80)
        print(f"🚨 BEFORE_REQUEST HANDLER CALLED FOR: {request.path}")
        print(f"🔍 current_user: {current_user}")
        print(f"🔍 is_authenticated: {current_user.is_authenticated}")
        print(f"🔍 current_user type: {type(current_user)}")
        print(f"🔍 session keys: {list(session.keys())}")
        print(f"🔍 session _user_id: {session.get('_user_id', 'NOT FOUND')}")
        print(f"🔍 session auth_namespace: {session.get('auth_namespace', 'NOT FOUND')}")
        print("=" * 80)
        
        exempt_routes = [
            '/admin/login',
            '/admin/signup',  # Add signup route to exempt routes
            '/admin/forgot-password',  # Add forgot password route
            '/admin/reset-password/',  # Add reset password route (with token)
            '/admin/logout',
            '/admin/static/',
            '/admin/topology/',
            '/admin/troubleshooting/'
        ]
        
        if any(request.path.startswith(route) for route in exempt_routes):
            print(f"✅ Path {request.path} is exempt, allowing through")
            return None
        
        if not current_user.is_authenticated:
            flash('Please log in to access the admin area', 'warning')
            # Preserve intended destination so we return here after login
            next_url = (request.full_path if request.query_string else request.path).rstrip('?')
            return redirect(url_for('auth.login', next=next_url))
        
        # Only check admin instance if user is authenticated
        if current_user.is_authenticated:
            from admin.models.user import Admin
            if not isinstance(current_user, Admin):
                flash('Access denied. Admin credentials required.', 'error')
                # Preserve intended destination so we return here after login
                next_url = (request.full_path if request.query_string else request.path).rstrip('?')
                return redirect(url_for('auth.login', next=next_url))

try:
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    from user.api import api_blueprint as user_api_blueprint
    app.register_blueprint(user_api_blueprint, url_prefix='/api')
    print("API Blueprint registered successfully")
    try:
        from user.api.topology_progress_api import topology_progress_bp
        app.register_blueprint(topology_progress_bp)
        print("Topology Progress API Blueprint registered successfully")
    except Exception as e:
        print(f"Error registering Topology Progress API blueprint: {e}")   
    try:
        from user.routes.troubleshooting_routes import troubleshooting_bp
        app.register_blueprint(troubleshooting_bp)
        print("User Troubleshooting Blueprint registered successfully")
        
        # Register collaborative troubleshooting API blueprint
        from user.routes.collaborative_troubleshooting_api import collaborative_troubleshooting_api_bp
        app.register_blueprint(collaborative_troubleshooting_api_bp)
        print("Collaborative Troubleshooting API Blueprint registered successfully")
        
        # Register feedback API blueprint
        from user.api.feedback_api import feedback_api
        app.register_blueprint(feedback_api)
        print("Feedback API Blueprint registered successfully")
        
        # Register user notification routes
        from user.routes.notification_routes import notification_bp
        app.register_blueprint(notification_bp)
        print("User Notification Blueprint registered successfully")
        
        # Register user assignment routes
        from user.routes.assignment_routes import user_assignment_bp
        app.register_blueprint(user_assignment_bp)
        print("User Assignment Blueprint registered successfully")
        
        # Register enhanced simulation API
        from user.api.enhanced_simulation_api import enhanced_simulation_api
        app.register_blueprint(enhanced_simulation_api, url_prefix='/dynamic')
        print("Enhanced Simulation API Blueprint registered successfully")
        
        # NOTE: Dynamic simulation blueprint is registered in __init__.py to avoid duplicates
        print("Dynamic Simulation Blueprint already registered in __init__.py")
    except Exception as e:
        print(f"Error registering User Troubleshooting blueprint: {e}")
    # No separate simulation blueprint registration needed
        
except Exception as e:
    print(f"Error registering API blueprint: {e}")
    try:
        import importlib.util
        api_path = os.path.join(os.path.dirname(__file__), 'user', 'api.py')
        spec = importlib.util.spec_from_file_location("api_module", api_path)
        api_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(api_module)
        app.register_blueprint(api_module.api_blueprint, url_prefix='/api')
        print("API Blueprint registered successfully using direct file import")
    except Exception as e2:
        print(f"Second attempt also failed: {e2}")
        
print("\n=== Registering Admin Blueprints ===")
try:
    import importlib
    blueprints_to_register = [        ('admin.controllers.auth_controller', 'auth_bp', '/admin', None),
        ('admin.controllers.dashboard_controller', 'dashboard_bp', '/admin', None),
        ('admin.controllers.user_controller', 'user_bp', '/admin', 'admin_user_bp'),
        ('admin.controllers.score_controller', 'score_bp', '/admin', None),
        ('admin.controllers.essay_controller', 'essay_bp', '/admin', None),

        
        ('admin.controllers.question_group_controller', 'question_group_bp', '/admin/groups', None),
        ('admin.controllers.class_controller', 'class_controller', '/admin', None),
    ('admin.controllers.class_content_controller', 'class_content_controller_old', '/admin', None),
        # Advanced lesson editor (blueprint has its own /admin/lessons prefix)
        ('admin.controllers.lesson_editor_controller', 'lesson_editor_bp', None, 'lesson_editor_bp'),
        ('admin.controllers.enhanced_module_controller', 'enhanced_module_bp', '/admin', None),  # Module management
        ('admin.controllers.module_lesson_editor_controller', 'module_lesson_editor_bp', None, None),  # Module lesson editor
        ('admin.controllers.audit_log_controller', 'audit_log_bp', '/admin', None),
    ('admin.controllers.notification_controller', 'notification_controller', None, None),  # Notification center
        ('admin.controllers.lesson_controller', 'lesson_bp', '/admin', None),  # Lesson management
    ('admin.controllers.tutorial_controller', 'tutorial_bp', None, None),  # Tutorial management
    ('admin.controllers.rubric_controller', 'rubric_bp', None, None),  # Rubric management
    ('admin.controllers.admin_settings_controller', 'admin_settings_bp', None, None),  # Admin settings

        ('admin.routes.api_routes', 'api_bp', None, 'admin_api_bp'),  # Admin API routes with internal prefix
        ('admin.routes.topology_routes', 'topology_bp', None, None),  # No prefix, has /admin/topology in routes
        ('admin.routes.topology_api_routes', 'topology_api_bp', None, None),  # API routes for topology
        ('admin.routes.troubleshooting_routes', 'troubleshooting_bp', None, None),  # No prefix, has /admin/troubleshooting in routes        ('admin.routes.troubleshooting_api_routes', 'troubleshooting_api_bp', None, None),  # API routes for troubleshooting
    ('admin.routes.simulation_routes', 'admin_simulation_bp', None, 'admin_simulation_bp'),  # Enhanced simulation routes
    ('admin.routes.collaboration_api', 'admin_collaboration_api_bp', None, 'admin_collaboration_api'),  # Admin collaboration API
    ('admin.controllers.instructor_lab_controller', 'instructor_lab_bp', None, None),  # Instructor labs dashboard
    ('admin.routes.lab_api', 'lab_api', None, None)  # Instructor-scoped lab API
    ]
    
    for module_path, blueprint_name, url_prefix, alias_name in blueprints_to_register:
        try:
            module = importlib.import_module(module_path)
            blueprint = getattr(module, blueprint_name)
            
            # Register with the specified URL prefix (or None if not needed)
            app.register_blueprint(blueprint, url_prefix=url_prefix)
            
            # Update the blueprint's template search paths
            from utils.template_utils import ensure_blueprint_can_find_templates
            ensure_blueprint_can_find_templates(blueprint, [
                app.template_folder,
                os.path.join(app.template_folder, 'admin')
            ])
            
            if alias_name:  # If we provided an alias name for clarity
                print(f"Registered {alias_name} from {module_path}")            
            else:
                print(f"Registered {blueprint_name} from {module_path}")
                
        except (ImportError, AttributeError) as e:
            print(f"Could not import or register {blueprint_name} from {module_path}: {e}")
    
    print("Admin blueprints registration complete")
except Exception as e:
    print(f"General error registering admin blueprints: {e}")

# Register Enhanced User Routes for User-Facing Integration
print("\n=== Registering Enhanced User Routes ===")
try:
    from user.routes.enhanced.hybrid_routes import enhanced_user_bp
    app.register_blueprint(enhanced_user_bp, url_prefix='/enhanced')
    print("✅ Enhanced user routes registered successfully")
    print("   • /enhanced/networking1-simulations - Shows static + database content")
    print("   • /enhanced/networking2-simulations - Shows static + database content")
    print("   • /enhanced/class/<id>/enhanced - Shows learning paths as modules")
    print("   • /simulation/<id> - Unified simulation runner")
    print("   • /simulation/static/<lesson_key> - Static content runner")
except Exception as e:
    print(f"❌ Error registering enhanced user routes: {e}")
    import traceback
    traceback.print_exc()

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

if __name__ == "__main__":
    import logging
    from flask import send_from_directory
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Define static folder path
    STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    
    # Add optimized static file routes directly to the main app
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

    # DEBUG endpoints for testing module functionality (remove in production)
    @app.route('/api/debug/modules/<int:module_id>/test-delete', methods=['GET'])
    def debug_test_module_delete(module_id):
        """Debug endpoint to test delete functionality without auth"""
        from flask import jsonify
        from admin.models.module import Module
        try:
            print(f"🔧 DEBUG: Testing delete functionality for module {module_id}")
            module = Module.query.get(module_id)
            if not module:
                return jsonify({'success': False, 'message': f'Module {module_id} not found'}), 404
                
            print(f"✅ Found module: {module.title} (is_active: {module.is_active})")
            return jsonify({
                'success': True, 
                'message': f'Module {module_id} exists and can be deleted',
                'module': {
                    'id': module.id,
                    'title': module.title,
                    'is_active': module.is_active,
                    'class_id': module.class_id
                }
            })
            
        except Exception as e:
            print(f"❌ DEBUG Exception: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/api/debug/modules/<int:module_id>/delete-now', methods=['GET'])
    def debug_delete_module_now(module_id):
        """Debug endpoint to actually delete a module without auth"""
        from flask import jsonify
        from admin.models.module import Module
        from admin import db
        from datetime import datetime
        try:
            print(f"🔧 DEBUG: Actually deleting module {module_id}")
            module = Module.query.get(module_id)
            if not module:
                return jsonify({'success': False, 'message': f'Module {module_id} not found'}), 404
                
            print(f"✅ Found module to delete: {module.title} (is_active: {module.is_active})")
            
            # Perform soft delete
            module.is_active = False
            module.updated_at = datetime.utcnow()
            
            db.session.commit()
            print(f"✅ Module soft-deleted successfully: {module.id}")
            
            return jsonify({
                'success': True,
                'message': f'Module {module_id} soft-deleted successfully',
                'module': {
                    'id': module.id,
                    'title': module.title,
                    'is_active': module.is_active,
                    'class_id': module.class_id
                }
            })
            
        except Exception as e:
            print(f"❌ DEBUG DELETE Exception: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500

    # Add debug middleware to track all requests
    @app.before_request
    def debug_requests():
        if '/preview' in request.path or '/class-content-manager' in request.path:
            print("🟡" + "="*80)
            print(f"🟡 REQUEST DEBUG: {request.method} {request.path}")
            print(f"🟡 Full URL: {request.url}")
            print(f"🟡 Referrer: {request.referrer}")
            print(f"🟡 User-Agent: {request.headers.get('User-Agent', 'N/A')[:100]}")
            if request.args:
                print(f"🟡 Query params: {dict(request.args)}")
            print("🟡" + "="*80)

    # Database setup
    with app.app_context():
        try:
            from admin.utils.database_setup import setup_database, migrate_existing_tables
            
            # First, try to migrate existing tables
            print("Checking for database migrations...")
            migrate_existing_tables()
            
            # Then set up database normally
            setup_database()
            
        except Exception as e:
            print(f"Database setup error: {e}")
            print("Continuing with application startup...")

    # Start the unified server with WebSocket support
    print("🚀 Starting unified Flask-SocketIO server on port 5001...")
    print("🔌 WebSocket events loaded and ready")
    print("📁 Static files will be served by Flask's built-in handler")
    
    # Start the Flask-SocketIO server
    socketio.run(
        app, 
        debug=True, 
        host='127.0.0.1',
        port=5001,
        use_reloader=False,  # Disable reloader to prevent threading issues
        allow_unsafe_werkzeug=True  # Allow eventlet with Werkzeug
    )


