# Configure eventlet to work better with Windows - MUST BE FIRST
import eventlet
eventlet.monkey_patch()

# Now import the rest of the modules
from __init__ import create_app, db, login_manager
from socket_manager import socketio  # Import socketio directly from socket_manager
import os
from user.quiz import QuizController
from flask_login import current_user
from flask import redirect, url_for, request, flash
from flask_cors import CORS
import socket_events  # Import the socket events module

# Create the Flask application with template folder explicitly set
template_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
app = create_app({
    'TEMPLATE_FOLDER': template_dir
})

# Create an application context for use outside of request handling
ctx = app.app_context()
ctx.push()

# Initialize SocketIO with the app
from socket_manager import init_socketio
init_socketio(app)

# Enable CORS for specific routes
cors = CORS(app, resources={
    r"/admin/topology/*": {"origins": "*"},
    r"/admin/troubleshooting/*": {"origins": "*"}
})

# Ensure the instance folder exists
instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
os.makedirs(instance_path, exist_ok=True)

# Create database tables if they don't exist
with app.app_context():
    db.create_all()

# Initialize the QuizController with our Flask app to register all quiz routes
quiz_controller = QuizController(app)

# Set up Flask-Login
login_manager.init_app(app)
login_manager.login_view = 'user.login'  # Use user login view by default
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    # Import models
    from admin.models.user import Admin, AdminUser
    from user.models import User
    
    # Check if the ID starts with 'admin-' which would indicate it's an admin
    if isinstance(user_id, str) and user_id.startswith('admin-'):
        admin_id = int(user_id.replace('admin-', ''))
        return db.session.get(Admin, admin_id)
    
    # Try to convert to int for database lookup
    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        return None
    
    # Check session context to determine user type
    # If we're in an admin route context, try Admin first
    if request and request.path.startswith('/admin'):
        admin = db.session.get(Admin, user_id_int)
        if admin:
            return admin
    
    # For non-admin routes or if not found in Admin, try User table
    user = db.session.get(User, user_id_int)
    if user:
        return user
        
    # If not found in User table and we haven't tried Admin yet, try Admin as fallback
    if not (request and request.path.startswith('/admin')):
        admin = db.session.get(Admin, user_id_int)
        if admin:
            return admin
    
    return None

# Set up admin route protection
@app.before_request
def check_admin_auth():
    # Only protect admin routes
    if request.path.startswith('/admin'):
        # List of paths that don't require authentication
        exempt_routes = [
            '/admin/login',
            '/admin/logout',
            '/admin/static/',
            '/admin/topology/',
            '/admin/troubleshooting/'
        ]
        
        # Skip check for exempt routes
        if any(request.path.startswith(route) for route in exempt_routes):
            return None
        
        # Check if user is authenticated AND is an admin user
        if not current_user.is_authenticated:
            flash('Please log in to access the admin area', 'warning')
            # Since the auth blueprint is registered with a prefix, we need to construct the login URL directly
            return redirect('/admin/login')
        
        # Check if the authenticated user is actually an admin (not a regular user)
        from admin.models.user import Admin
        if not isinstance(current_user, Admin):
            # If it's a regular user trying to access admin area, redirect them to user login
            flash('Access denied. Admin credentials required.', 'error')
            return redirect('/admin/login')

# Now register the API blueprint AFTER the QuizController to avoid conflicts
# Any conflicts will result in the QuizController routes taking precedence
try:
    # Import directly from the file, not the package
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    # Direct import from the api.py file
    from user.api import api_blueprint as user_api_blueprint
    app.register_blueprint(user_api_blueprint, url_prefix='/api')
    print("API Blueprint registered successfully")
      # Register topology progress API blueprint
    try:
        from user.api.topology_progress_api import topology_progress_bp
        app.register_blueprint(topology_progress_bp)
        print("Topology Progress API Blueprint registered successfully")
    except Exception as e:
        print(f"Error registering Topology Progress API blueprint: {e}")    # Register user troubleshooting routes
    try:
        from user.routes.troubleshooting_routes import troubleshooting_bp
        app.register_blueprint(troubleshooting_bp)
        print("User Troubleshooting Blueprint registered successfully")
    except Exception as e:
        print(f"Error registering User Troubleshooting blueprint: {e}")    # Simulation routes are now included in the main user_bp blueprint
    # No separate simulation blueprint registration needed
        
except Exception as e:
    print(f"Error registering API blueprint: {e}")
    # If we can't import from the package, try to import from the file directly
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
        
# Register Admin routes
print("\n=== Registering Admin Blueprints ===")
try:
    import importlib
    # Import admin blueprints using a more robust approach
    blueprints_to_register = [        ('admin.controllers.auth_controller', 'auth_bp', '/admin', None),
        ('admin.controllers.dashboard_controller', 'dashboard_bp', '/admin', None),
        ('admin.controllers.user_controller', 'user_bp', '/admin', 'admin_user_bp'),
        ('admin.controllers.question_controller', 'question_bp', '/admin/questions', None),
        ('admin.controllers.score_controller', 'score_bp', '/admin', None),
        ('admin.controllers.essay_controller', 'essay_bp', '/admin', None),
        ('admin.controllers.question_group_controller', 'question_group_bp', '/admin/groups', None),
        ('admin.controllers.class_controller', 'class_controller', '/admin', None),
        ('admin.controllers.audit_log_controller', 'audit_log_bp', '/admin', None),
        ('admin.routes.topology_routes', 'topology_bp', None, None),  # No prefix, has /admin/topology in routes
        ('admin.routes.topology_api_routes', 'topology_api_bp', None, None),  # API routes for topology
        ('admin.routes.troubleshooting_routes', 'troubleshooting_bp', None, None),  # No prefix, has /admin/troubleshooting in routes        ('admin.routes.troubleshooting_api_routes', 'troubleshooting_api_bp', None, None),  # API routes for troubleshooting
        ('admin.routes.simulation_routes', 'admin_simulation_bp', None, 'admin_simulation_bp'),  # Enhanced simulation routes
        ('admin.routes.learning_routes', 'learning_path_bp', None, 'learning_path_bp')  # Learning path routes
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

# Print all registered routes for debugging
print("\n=== Registered Routes ===")
for rule in sorted(app.url_map.iter_rules(), key=lambda x: str(x)):
    methods = ', '.join(sorted(rule.methods)) if rule.methods else ''
    print(f"{rule.endpoint:30} {methods:20} {rule.rule}")
print("=========================\n")

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

    # Start the unified server with WebSocket support
    print("Starting unified Flask-SocketIO server on port 5001...")
    print("WebSocket events loaded and ready")
    print("Static files will be served by Flask's built-in handler")
    # Start the Flask-SocketIO server
    socketio.run(
        app, 
        debug=True, 
        host='127.0.0.1',
        port=5001,
        use_reloader=False,  # Disable reloader to prevent threading issues
        allow_unsafe_werkzeug=True  # Allow eventlet with Werkzeug
    )
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
    # Import modules needed for the server
    import threading
    import logging
    from flask import Flask, send_from_directory, request
    
    # Configure logging for static server
    logging.basicConfig(level=logging.INFO, 
                      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('static_server')
    
    # Create a separate Flask app for static files
    static_app = Flask(__name__)
    
    # Define the static folder path
    STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    
    @static_app.route('/static/<path:path>')
    def serve_static(path):
        """Serve static files"""
        logger.debug(f"Serving static file: {path}")
        return send_from_directory(STATIC_FOLDER, path)
    
    @static_app.route('/media/video/<path:filename>')
    def serve_video(filename):
        """Serve video files with optimized settings"""
        logger.debug(f"Serving video file: {filename}")
        video_path = os.path.join(STATIC_FOLDER, 'video', filename)
        
        # Handle range requests for video streaming
        range_header = request.headers.get('Range', None)
        if range_header:
            logger.debug(f"Range request: {range_header}")
        
        response = send_from_directory(os.path.dirname(video_path), os.path.basename(video_path))
        
        # Add caching headers
        response.headers['Cache-Control'] = 'public, max-age=43200'  # 12 hours
        return response
    
    @static_app.route('/media/audio/<path:filename>')
    def serve_audio(filename):
        """Serve audio files with optimized settings"""
        logger.debug(f"Serving audio file: {filename}")
        audio_path = os.path.join(STATIC_FOLDER, 'audio', filename)
        
        response = send_from_directory(os.path.dirname(audio_path), os.path.basename(audio_path))
        
        # Add caching headers
        response.headers['Cache-Control'] = 'public, max-age=43200'  # 12 hours
        return response
    
    @static_app.route('/health')
    def health_check():
        """Health check endpoint"""
        return {'status': 'ok', 'service': 'static_file_server'}, 200
    def run_static_server():
        """Run the static file server with waitress instead of eventlet"""
        from waitress import serve
        print("Starting static file server on port 5001...")
        serve(static_app, host='127.0.0.1', port=5001, threads=8)
    
    def run_websocket_server():
        """Run the WebSocket server"""
        print("Starting WebSocket server on port 5000...")
        socketio.run(
            app, 
            debug=True, 
            host='127.0.0.1',
            port=5000,
            use_reloader=False  # Set to False to avoid issues with reloading
        )
    
    # Start the static server in a separate thread
    static_thread = threading.Thread(target=run_static_server, daemon=True)
    static_thread.start()
    
    # Give the static server a moment to start
    import time
    time.sleep(1)
      # Check if static server is running
    from utils.static_server_monitor import static_server_monitor
    if not static_server_monitor.check_availability():
        print("\n⚠️ WARNING: Static file server failed to start on port 5001!")
        print("Check if the port is already in use or if there are any errors.\n")
    else:
        print("✅ Static file server running at http://localhost:5001")
    
    # Run the WebSocket server in the main thread (commented out for API testing)
    # run_websocket_server()
    
    # For now, run a simple Flask server for API testing
    print("Starting Flask server for API testing on port 5001...")
    app.run(debug=True, host='127.0.0.1', port=5001, use_reloader=False)

if __name__ == '__main__':
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

