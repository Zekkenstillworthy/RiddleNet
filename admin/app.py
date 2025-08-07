from flask import Flask, redirect, url_for, request, flash, session
import os
from admin import db, login_manager
from flask_login import current_user
class AdminApp:
    def __init__(self):
        # Specify the template folder as an absolute path pointing to the project's templates directory
        template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
        static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
        
        self.app = Flask(__name__, 
                        template_folder=template_dir,
                        static_folder=static_dir)
        
        self.configure_app()
        self.init_db()
        self.init_login_manager()
        self.register_template_filters()

    def configure_app(self):
        """Configure the Flask application."""
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///riddlenet.db'
        self.app.config['SECRET_KEY'] = 'your_secret_key'
        self.app.config['ADMIN_PORT'] = 5001
        
        # Configure session settings
        self.app.config['SESSION_TYPE'] = 'filesystem'
        self.app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours in seconds
        self.app.config['SESSION_USE_SIGNER'] = True
        self.app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
        self.app.config['SESSION_COOKIE_HTTPONLY'] = True

        # Debug template path
        template_dir = self.app.template_folder
        print(f"Looking for templates in: {template_dir}")

    def init_db(self):
        """Initialize the database with the app."""
        db.init_app(self.app)
        
    def init_login_manager(self):
        """Initialize the Flask-Login manager with the app."""
        login_manager.init_app(self.app)
        # We no longer use url_for for login_view since we're using a prefixed blueprint
        login_manager.login_view = '/admin/login'
        login_manager.login_message_category = 'info'
        
        @login_manager.user_loader
        def load_user(user_id):
            # Try to load from Admin model first (since admin login is being used)
            from admin.models.user import Admin, User
              # Check if the ID starts with 'admin-' which would indicate it's an admin
            if isinstance(user_id, str) and user_id.startswith('admin-'):
                admin_id = int(user_id.replace('admin-', ''))
                return db.session.get(Admin, admin_id)
            
            # Try Admin table first
            admin = db.session.get(Admin, int(user_id))
            if admin:
                return admin
                
                # If not found in Admin, try User table
                user = db.session.get(User, int(user_id))
                return user
                
    def register_template_filters(self):
        """Register custom template filters."""
        @self.app.template_filter('from_json')
        def from_json_filter(value):
            import json
            try:
                return json.loads(value)
            except (ValueError, TypeError):
                return []
                
        # Add context processors for static file server
        @self.app.context_processor
        def utility_processor():
            def static_url(path):
                """Generate URL for static files from separate server"""
                return f"http://localhost:5001/static/{path}"
                
            def media_url(type, path):
                """Generate URL for media files (video/audio)"""
                return f"http://localhost:5001/media/{type}/{path}"
                
            return dict(static_url=static_url, media_url=media_url)

    def register_blueprints(self):
        """Register all blueprints with the application."""
        # Use absolute imports instead of relative imports
        from admin.controllers.auth_controller import auth_bp
        from admin.controllers.user_controller import user_bp
        from admin.controllers.question_controller import question_bp
        from admin.controllers.score_controller import score_bp
        from admin.controllers.essay_controller import essay_bp
        from admin.controllers.dashboard_controller import dashboard_bp
        from admin.controllers.question_group_controller import question_group_bp
        from admin.controllers.class_controller import class_controller
        from admin.controllers.class_content_controller import class_content_controller
        from admin.controllers.notification_controller import notification_controller
        # from admin.controllers.scenario_controller import scenario_bp
        from admin.controllers.audit_log_controller import audit_log_bp
        from admin.routes.topology_routes import topology_bp
        from admin.routes.topology_api_routes import topology_api_bp
        from admin.routes.troubleshooting_routes import troubleshooting_bp
        from user.routes.universal_class_routes import universal_class_bp
        from admin.routes.api_routes import api_bp
        
        print("📝 Registering universal_class_bp blueprint...")
        
        # Register only available blueprints
        self.app.register_blueprint(auth_bp)
        self.app.register_blueprint(user_bp)
        self.app.register_blueprint(question_bp)
        self.app.register_blueprint(score_bp)
        self.app.register_blueprint(essay_bp)
        self.app.register_blueprint(dashboard_bp)
        self.app.register_blueprint(question_group_bp)        
        self.app.register_blueprint(class_controller)
        self.app.register_blueprint(class_content_controller)
        self.app.register_blueprint(notification_controller)
        # self.app.register_blueprint(scenario_bp)
        self.app.register_blueprint(audit_log_bp)        # audit_log_bp registration removed (controller deleted)
        self.app.register_blueprint(topology_bp)
        self.app.register_blueprint(topology_api_bp)
        self.app.register_blueprint(troubleshooting_bp)
        self.app.register_blueprint(universal_class_bp)
        print("✅ universal_class_bp registered successfully!")
        self.app.register_blueprint(api_bp)
        
        # Add root route to redirect to admin dashboard
        @self.app.route('/')
        def index():
            return redirect(url_for('dashboard.index'))

    def setup_admin_protection(self):
        """Set up admin route protection"""
        # Implement app-level protection for all admin routes
        @self.app.before_request
        def check_admin_auth():
            # Debug output
            print(f"🔍 ADMIN APP Protection check for path: {request.path}")
            
            # List of paths that don't require authentication
            exempt_routes = [
                '/static/', 
                '/login',
                '/signup',  # Add signup to exempt routes
                '/admin/login',  # Add admin login with prefix
                '/admin/signup',  # Add admin signup with prefix
                '/auth/login',
                '/auth/signup',  # Add auth/signup to exempt routes
                '/logout',
                '/auth/logout'
            ]
            
            # Debug: show which routes are exempt
            is_exempt = any(request.path.startswith(route) for route in exempt_routes)
            print(f"🛡️ ADMIN APP - Path '{request.path}' is exempt: {is_exempt}")
            
            # Skip check for exempt routes
            if any(request.path.startswith(route) for route in exempt_routes):
                print("✅ ADMIN APP - Route is exempt, allowing access")
                return None
            
            # Check if user is authenticated
            if not current_user.is_authenticated:
                print(f"🚫 ADMIN APP - Blocking unauthenticated access to: {request.path}")
                flash('Please log in to access the admin area', 'warning')
                return redirect(url_for('auth.login', next=request.url))

    def setup(self):
        """Setup the application by registering blueprints and initializing database."""
        self.register_blueprints()
        self.setup_admin_protection()  # Add admin route protection
        
        with self.app.app_context():
            # Use absolute import for database_setup
            from admin.utils.database_setup import setup_database
            setup_database()
        
        return self.app

    def run(self, host=None, port=None, debug=True):
        """Run the Flask application."""
        if port is None:
            port = self.app.config['ADMIN_PORT']
        
        print(f"Admin app running on port {port}")
        print("Admin authentication protection enabled - all routes require login")
        
        if host:
            self.app.run(debug=debug, port=port, host=host)
        else:
            self.app.run(debug=debug, port=port)
