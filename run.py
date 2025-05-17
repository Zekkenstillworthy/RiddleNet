from __init__ import create_app, db, login_manager
import os
from user.quiz import QuizController
from admin.controllers.question_controller import QuestionController
from flask_login import current_user
from flask import redirect, url_for, request, flash

# Create the Flask application
app = create_app()

# Create an application context for use outside of request handling
ctx = app.app_context()
ctx.push()

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
            '/admin/static/'
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
    # Import admin blueprints one by one and handle possible import errors for each
    try:
        print("Importing auth_bp...")
        from admin.controllers.auth_controller import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/admin')
        print("Registered auth_bp")
    except Exception as e:
        print(f"Error with auth_bp: {str(e)}")
    
    try:
        print("Importing dashboard_bp...")
        from admin.controllers.dashboard_controller import dashboard_bp
        app.register_blueprint(dashboard_bp, url_prefix='/admin')
        print("Registered dashboard_bp")
    except Exception as e:
        print(f"Error with dashboard_bp: {str(e)}")
    
    try:
        print("Importing user_bp...")
        from admin.controllers.user_controller import user_bp as admin_user_bp
        app.register_blueprint(admin_user_bp, url_prefix='/admin')
        print("Registered admin_user_bp")
    except Exception as e:
        print(f"Error with user_bp: {str(e)}")    
    try:
        print("Importing question_bp...")
        from admin.controllers.question_controller import question_bp
        app.register_blueprint(question_bp, url_prefix='/admin/questions')  # Changed to avoid conflict with user routes
        print("Registered question_bp")
    except Exception as e:
        print(f"Error with question_bp: {str(e)}")
    
    try:
        print("Importing score_bp...")
        from admin.controllers.score_controller import score_bp
        app.register_blueprint(score_bp, url_prefix='/admin')
        print("Registered score_bp")
    except Exception as e:
        print(f"Error with score_bp: {str(e)}")
    
    try:
        print("Importing essay_bp...")
        from admin.controllers.essay_controller import essay_bp
        app.register_blueprint(essay_bp, url_prefix='/admin')
        print("Registered essay_bp")
    except Exception as e:
        print(f"Error with essay_bp: {str(e)}")
    
    try:
        print("Importing scenario_bp...")
        from admin.controllers.scenario_controller import scenario_bp
        app.register_blueprint(scenario_bp, url_prefix='/admin')
        print("Registered scenario_bp")
    except Exception as e:
        print(f"Error with scenario_bp: {str(e)}")
    
    try:
        print("Importing question_group_bp...")
        from admin.controllers.question_group_controller import question_group_bp
        app.register_blueprint(question_group_bp, url_prefix='/admin/groups')  # Changed to avoid conflict
        print("Registered question_group_bp")
    except Exception as e:
        print(f"Error with question_group_bp: {str(e)}")
    
    try:
        print("Importing class_controller...")
        from admin.controllers.class_controller import class_controller
        app.register_blueprint(class_controller, url_prefix='/admin')
        print("Registered class_controller")
    except Exception as e:
        print(f"Error with class_controller: {str(e)}")
    
    try:
        print("Importing audit_log_bp...")
        from admin.controllers.audit_log_controller import audit_log_bp
        app.register_blueprint(audit_log_bp, url_prefix='/admin')
        print("Registered audit_log_bp")
    except Exception as e:
        print(f"Error with audit_log_bp: {str(e)}")
    
    try:
        print("Importing topology_bp...")
        from admin.routes.topology_routes import topology_bp
        app.register_blueprint(topology_bp, url_prefix='/admin')
        print("Registered topology_bp")
    except Exception as e:
        print(f"Error with topology_bp: {str(e)}")
    
    try:
        print("Importing scenario_routes...")
        from admin.routes.scenario_routes import scenario_routes
        app.register_blueprint(scenario_routes, url_prefix='/admin')
        print("Registered scenario_routes")
    except Exception as e:
        print(f"Error with scenario_routes: {str(e)}")
    
    print("Admin blueprints registration complete")
except Exception as e:
    print(f"General error registering admin blueprints: {e}")
    
    try:
        from admin.controllers.class_controller import class_controller
        app.register_blueprint(class_controller, url_prefix='/admin')
    except ImportError as e:
        print(f"Could not import class_controller: {e}")
    
    try:
        from admin.controllers.audit_log_controller import audit_log_bp
        app.register_blueprint(audit_log_bp, url_prefix='/admin')
    except ImportError as e:
        print(f"Could not import audit_log_controller: {e}")
        
    try:
        from admin.routes.topology_routes import topology_bp
        app.register_blueprint(topology_bp, url_prefix='/admin')
    except ImportError as e:
        print(f"Could not import topology_routes: {e}")
        
    try:
        from admin.routes.scenario_routes import scenario_routes
        app.register_blueprint(scenario_routes, url_prefix='/admin')
    except ImportError as e:
        print(f"Could not import scenario_routes: {e}")
    
    # Register the blueprints that are more likely to exist
    app.register_blueprint(auth_bp, url_prefix='/admin')
    app.register_blueprint(dashboard_bp, url_prefix='/admin')
    app.register_blueprint(question_bp, url_prefix='/admin/questions')  # Changed to avoid conflict with user routes
    app.register_blueprint(score_bp, url_prefix='/admin')
    app.register_blueprint(essay_bp, url_prefix='/admin')
    app.register_blueprint(scenario_bp, url_prefix='/admin')
    app.register_blueprint(question_group_bp, url_prefix='/admin/groups')  # Changed to avoid conflict
    
    print("Admin blueprints registered successfully")
except Exception as e:
    print(f"Error registering admin blueprints: {e}")

# Print all registered routes for debugging
print("\n=== Registered Routes ===")
for rule in sorted(app.url_map.iter_rules(), key=lambda x: str(x)):
    methods = ', '.join(sorted(rule.methods)) if rule.methods else ''
    print(f"{rule.endpoint:30} {methods:20} {rule.rule}")
print("=========================\n")

if __name__ == "__main__":
    # Run the app with debug mode enabled
    app.run(debug=True)

