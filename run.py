# Configure eventlet to work better with Windows - MUST BE FIRST
import eventlet
eventlet.monkey_patch()



# Now import the rest of the modules
from __init__ import create_app, db, login_manager, socketio
import os
from user.quiz import QuizController
from admin.controllers.question_controller import QuestionController
from flask_login import current_user
from flask import redirect, url_for, request, flash
from flask_cors import CORS
import socket_events  # Import the socket events module

# Create the Flask application with template folder explicitly set
# This ensures the admin templates can be found
template_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
app = create_app({
    'TEMPLATE_FOLDER': template_dir
})

# Create an application context for use outside of request handling
ctx = app.app_context()
ctx.push()

# Debug template path
print(f"Looking for templates in: {app.template_folder}")

# Check if the admin templates directory exists
admin_templates_path = os.path.join(template_dir, 'admin')
if os.path.exists(admin_templates_path):
    print(f"Admin templates found in: {admin_templates_path}")
    # List all admin templates
    print("Available admin templates:")
    for template in os.listdir(admin_templates_path):
        print(f"  - {template}")
else:
    print(f"WARNING: Admin templates directory not found at {admin_templates_path}")

# Add additional template folders for admin templates if they exist
admin_template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'admin', 'templates')
if os.path.exists(admin_template_dir):
    print(f"Adding additional admin template directory: {admin_template_dir}")
    # Add it to the existing template loader
    app.jinja_loader.searchpath.append(admin_template_dir)

# Debug information for template paths
print("\n=== Template Search Paths ===")
print(f"Default template folder: {app.template_folder}")
for path in app.jinja_loader.searchpath:
    print(f"- {path}")
print("============================\n")

# Create a function to modify templates path for all blueprints
def update_blueprint_template_paths(blueprint, template_folders):
    """Update a blueprint's template folders to include additional paths"""
    if not hasattr(blueprint, 'jinja_loader'):
        print(f"Blueprint {blueprint.name} has no jinja_loader")
        return
        
    for folder in template_folders:
        if folder not in blueprint.jinja_loader.searchpath:
            blueprint.jinja_loader.searchpath.append(folder)
            print(f"Added {folder} to blueprint {blueprint.name}'s template search path")
            
# Set a unified template folder for all blueprints
def register_template_folder_for_blueprints():
    """Register the main template folder in all registered blueprints"""
    main_template_folder = app.template_folder
    print(f"Registering main template folder for all blueprints: {main_template_folder}")
    
    # Get all registered blueprints
    for name, blueprint in app.blueprints.items():
        # Use the enhanced utility from template_utils
        from utils.template_utils import ensure_blueprint_can_find_templates
        ensure_blueprint_can_find_templates(blueprint, [
            main_template_folder,
            os.path.join(main_template_folder, 'admin')
        ])
        
# Register the template folder for all currently registered blueprints
register_template_folder_for_blueprints()

# Debug information for template paths
print("\n=== Template Search Paths ===")
print(f"Default template folder: {app.template_folder}")
for path in app.jinja_loader.searchpath:
    print(f"- {path}")
print("============================\n")

# Add a context processor to support admin templates
@app.context_processor
def inject_admin_helpers():
    def admin_url_for(endpoint, **kwargs):
        """Helper to generate URLs for admin routes"""
        # If the endpoint already has a blueprint prefix, use it directly
        if '.' in endpoint:
            return url_for(endpoint, **kwargs)
        # Otherwise, assume it's an admin endpoint
        return url_for(f"admin.{endpoint}", **kwargs)
    
    return {
        'admin_url_for': admin_url_for,
        'is_admin_route': lambda: request.path.startswith('/admin')
    }

# Enable CORS for specific routes
cors = CORS(app, resources={
    r"/admin/topology/*": {"origins": "*"},
    r"/admin/troubleshooting/*": {"origins": "*"}
})
print("CORS enabled for topology and troubleshooting API endpoints")

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
    # Try to load from Admin model first (since admin login is being used)
    from admin.models.user import Admin, AdminUser
    
    # Check if the ID starts with 'admin-' which would indicate it's an admin
    if isinstance(user_id, str) and user_id.startswith('admin-'):
        admin_id = int(user_id.replace('admin-', ''))
        return Admin.query.get(admin_id)
    
    # Try Admin table first
    admin = Admin.query.get(int(user_id))
    if admin:
        return admin
            
    # If not found in Admin, try User table from user.models
    from user.models import User
    user = User.query.get(int(user_id))
    return user

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
        
        # Check if user is authenticated
        if not current_user.is_authenticated:
            flash('Please log in to access the admin area', 'warning')
            # Since the auth blueprint is registered with a prefix, we need to construct the login URL directly
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
        print(f"Error registering Topology Progress API blueprint: {e}")
    
    # Register user troubleshooting routes
    try:
        from user.routes.troubleshooting_routes import troubleshooting_bp
        app.register_blueprint(troubleshooting_bp)
        print("User Troubleshooting Blueprint registered successfully")
    except Exception as e:
        print(f"Error registering User Troubleshooting blueprint: {e}")
        
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
try:    # Import admin blueprints using a more robust approach
    blueprints_to_register = [
        ('admin.controllers.auth_controller', 'auth_bp', '/admin', None),
        ('admin.controllers.dashboard_controller', 'dashboard_bp', '/admin', None),
        ('admin.controllers.user_controller', 'user_bp', '/admin', 'admin_user_bp'),
        ('admin.controllers.question_controller', 'question_bp', '/admin/questions', None),
        ('admin.controllers.score_controller', 'score_bp', '/admin', None),
        ('admin.controllers.essay_controller', 'essay_bp', '/admin', None),
        ('admin.controllers.scenario_controller', 'scenario_bp', '/admin', None),
        ('admin.controllers.question_group_controller', 'question_group_bp', '/admin/groups', None),
        ('admin.controllers.class_controller', 'class_controller', '/admin', None),
        ('admin.controllers.audit_log_controller', 'audit_log_bp', '/admin', None),        ('admin.routes.topology_routes', 'topology_bp', None, None),  # No prefix, has /admin/topology in routes
        ('admin.routes.troubleshooting_routes', 'troubleshooting_bp', None, None),  # No prefix, has /admin/troubleshooting in routes
        ('admin.routes.scenario_routes', 'scenario_routes', '/admin', None)
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
    
    # Run the WebSocket server in the main thread
    run_websocket_server()

