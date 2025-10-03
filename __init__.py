from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

from flask_socketio import SocketIO  # Add this import
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Skip static file handling in main app - will be served by static_server
os.environ['FLASK_SKIP_STATIC'] = '1'

# Initialize extensions
# Create a SINGLE SQLAlchemy instance for the entire application
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()


# Note: SocketIO is imported and initialized in run.py to avoid circular imports

def create_app(config=None):
    # Set the instance path explicitly to ensure using the correct database location
    instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    
    # Get template folder from config or use default
    template_folder = None
    if config and 'TEMPLATE_FOLDER' in config:
        template_folder = config['TEMPLATE_FOLDER']
    
    app = Flask(__name__, instance_path=instance_path, template_folder=template_folder)    # Configure the app
    # Use local instance config file (PostgreSQL settings) instead of user.config
    loaded_instance_config = app.config.from_pyfile('config.py', silent=True)
    print(f"[create_app] Attempted to load instance/config.py (silent=True). Exists: {os.path.exists(os.path.join(instance_path, 'config.py'))}")
    # If not loaded, attempt to construct URI from env vars as emergency fallback
    if 'SQLALCHEMY_DATABASE_URI' not in app.config:
        print("[create_app] SQLALCHEMY_DATABASE_URI not found after from_pyfile. Building from environment variables...")
        pg_host = os.getenv("POSTGRES_HOST", "localhost")
        pg_port = os.getenv("POSTGRES_PORT", "5432")
        pg_db = os.getenv("POSTGRES_DB", "riddlenet")
        pg_user = os.getenv("POSTGRES_USER", "postgres")
        pg_password = os.getenv("POSTGRES_PASSWORD", "")
        pg_sslmode = os.getenv("POSTGRES_SSL_MODE")
        if not (pg_host and pg_db and pg_user):
            print(f"[create_app] Incomplete PostgreSQL env configuration: host={pg_host} db={pg_db} user={pg_user}")
        auth_segment = f"{pg_user}:{pg_password}" if pg_password else pg_user
        uri = f"postgresql+psycopg2://{auth_segment}@{pg_host}:{pg_port}/{pg_db}"
        if pg_sslmode:
            uri += f"?sslmode={pg_sslmode}"
        app.config['SQLALCHEMY_DATABASE_URI'] = uri
        print(f"[create_app] Constructed PostgreSQL URI from env: {uri}")
    
    # Enforce that the instance config provided a PostgreSQL URI
    if 'SQLALCHEMY_DATABASE_URI' not in app.config:
        raise RuntimeError("SQLALCHEMY_DATABASE_URI not set. PostgreSQL configuration required (instance/config.py or environment)")
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_development_only')
    
    # Set maximum content length for uploads (100MB)
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload
    
    # Fix session cookie configuration to ensure proper admin_session cookie delivery
    app.config['SESSION_COOKIE_PATH'] = '/'
    app.config['SESSION_COOKIE_DOMAIN'] = None  # Allow for localhost
    app.config['SESSION_COOKIE_SECURE'] = False  # Allow HTTP for development
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Allow cross-context cookies
    
    if config:
        app.config.update(config)
    
    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Add custom Jinja2 filters
    @app.template_filter('strftime')
    def strftime_filter(date, format='%Y-%m-%d %H:%M:%S'):
        """Convert a datetime to a string using strftime."""
        if date:
            return date.strftime(format)
        return ""
    
    # Initialize Login Manager
    login_manager.init_app(app)
    login_manager.login_view = 'user.login'  # Specify the login view endpoint
      # Initialize Flask-Mail
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USE_SSL"] = False
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_USERNAME")
    # Add timeout settings for better network handling
    app.config["MAIL_TIMEOUT"] = 10
    app.config["MAIL_MAX_EMAILS"] = None
    mail.init_app(app)
    
    # Define the user loader function - DISABLED: Using main user_loader in run.py
    # @login_manager.user_loader
    # def load_user(user_id):
    #     # Make sure we're in an application context
    #     if not current_app:
    #         return None
    #         
    #     # Try different import paths to find User model
    #     try:
    #         # Import as UserModel to avoid conflicts
    #         from user.models import User as UserModel
    #         with app.app_context():
    #             return UserModel.query.get(int(user_id))
    #     except (ImportError, AttributeError):
    #         try:
    #             # Import as UserModel to avoid conflicts
    #             from user.models.user import User as UserModel
    #             with app.app_context():
    #                 return UserModel.query.get(int(user_id))
    #         except (ImportError, AttributeError):
    #             return None

    # Install split session interface to isolate admin/user auth states
    try:
        from utils.split_session_interface import SplitSessionInterface
        app.session_interface = SplitSessionInterface()
        print("[create_app] SplitSessionInterface enabled (admin_session / user_session cookies)")
    except Exception as e:
        print(f"[create_app] WARNING: Could not enable SplitSessionInterface: {e}")

    # Register blueprints
    try:
        from user.views import user_bp
        app.register_blueprint(user_bp)
        
        # Register universal class routes
        print("🔍 Attempting to register universal class routes...")
        try:
            from user.routes.universal_class_routes import universal_class_bp
            print("🔍 Universal class blueprint imported successfully")
            app.register_blueprint(universal_class_bp)
            print("✅ Universal class routes registered successfully")
        except Exception as e:
            print(f"⚠️ Error registering universal class blueprint: {e}")
            import traceback
            traceback.print_exc()
        
        # Register dynamic simulation routes blueprint
        try:
            from user.dynamic_simulation_routes import dynamic_sim_bp
            app.register_blueprint(dynamic_sim_bp)
            print("✅ Dynamic simulation routes registered successfully")
        except Exception as e:
            print(f"⚠️ Error registering dynamic simulation blueprint: {e}")
        
        # Register the API blueprint with explicit url_prefix
        # Commented out to avoid conflicts with QuizController routes
        # We'll register this in run.py after the QuizController
        '''
        try:
            from user.api import api_blueprint as user_api_blueprint
            app.register_blueprint(user_api_blueprint, url_prefix='/api')
        except Exception as e:
            print(f"Error registering API blueprint: {e}")
            # Continue without the API if it fails to load
            
        # Register admin blueprints
        try:
            from admin.controllers.auth_controller import auth_bp
            app.register_blueprint(auth_bp, url_prefix='/admin')
            print("✅ Admin auth blueprint registered")
        except Exception as e:
            print(f"⚠️ Error registering admin auth blueprint: {e}")
            
        try:
            from admin.controllers.dashboard_controller import dashboard_bp
            app.register_blueprint(dashboard_bp, url_prefix='/admin')
            print("✅ Admin dashboard blueprint registered")
        except Exception as e:
            print(f"⚠️ Error registering admin dashboard blueprint: {e}")
            
        try:
            from admin.controllers.class_content_controller import class_content_controller_old
            app.register_blueprint(class_content_controller_old, url_prefix='/admin')
            print("✅ Admin class content controller blueprint registered")
        except Exception as e:
            print(f"⚠️ Error registering admin class content controller blueprint: {e}")
            
        try:
            from admin.controllers.essay_controller import essay_bp
            app.register_blueprint(essay_bp, url_prefix='/admin')
            print("✅ Admin essay controller blueprint registered")
        except Exception as e:
            print(f"⚠️ Error registering admin essay controller blueprint: {e}")
            
        try:
            from admin.routes.collaboration_api import admin_collaboration_api_bp
            app.register_blueprint(admin_collaboration_api_bp)
            print("✅ Admin collaboration API blueprint registered")
        except Exception as e:
            print(f"⚠️ Error registering admin collaboration API blueprint: {e}")
            
        try:
            from admin.routes.rnet_viewer_routes import rnet_viewer_bp
            app.register_blueprint(rnet_viewer_bp)
            print("✅ RNet file viewer blueprint registered")
        except Exception as e:
            print(f"⚠️ Error registering RNet file viewer blueprint: {e}")
            
        '''
        
        # Print registered rules for debugging        print("Registered URL rules:")
        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint}: {rule.rule}")
    except ImportError as e:
        # If a blueprint can't be imported, continue without it
        print(f"Warning: Could not import blueprint: {e}")
    
    # Register RNet file viewer blueprint (moved out of commented section)
    try:
        from admin.routes.rnet_viewer_routes import rnet_viewer_bp
        app.register_blueprint(rnet_viewer_bp)
        print("✅ RNet file viewer blueprint registered")
    except Exception as e:
        print(f"⚠️ Error registering RNet file viewer blueprint: {e}")
    
    # Register admin user controller blueprint (moved out of commented section)
    try:
        from admin.controllers.user_controller import user_bp
        app.register_blueprint(user_bp, url_prefix='/users')
        print("✅ Admin user controller blueprint registered")
    except Exception as e:
        print(f"⚠️ Error registering admin user controller blueprint: {e}")
    
    # Add context processors for static file server
    @app.context_processor
    def utility_processor():
        def static_url(path):
            """Generate URL for static files from separate server"""
            return f"http://localhost:5001/static/{path}"
            
        def media_url(type, path):
            """Generate URL for media files (video/audio)"""
            return f"http://localhost:5001/media/{type}/{path}"
            
        return dict(static_url=static_url, media_url=media_url)
    
    # Add global user context processor
    @app.context_processor
    def inject_user():
        """CRITICAL FIX: Inject user information with proper namespace isolation"""
        from flask_login import current_user
        from flask import session, request
        
        # Debug: Print current request info
        try:
            path = request.path if request else "unknown"
        except:
            path = "unknown"
        
        auth_namespace = session.get('auth_namespace', 'none')
        
        # CRITICAL FIX: Strict namespace-based isolation
        if path.startswith('/admin'):
            # Admin routes: ONLY allow admin namespace
            if current_user.is_authenticated and auth_namespace == 'admin':
                from admin.models.user import Admin
                if isinstance(current_user, Admin):
                    print(f"Context processor [{path}]: Admin route - authenticated admin: {current_user.username} (namespace: {auth_namespace})")
                    return dict(user=current_user)
            
            print(f"Context processor [{path}]: Admin route - no admin authentication (namespace: {auth_namespace})")
            return dict(user=None)
        
        # User routes: Support both user and admin access with namespace checking
        if current_user.is_authenticated:
            from user.models.user import User
            from admin.models.user import Admin
            
            if isinstance(current_user, User) and auth_namespace == 'user':
                print(f"Context processor [{path}]: User route - authenticated user: {current_user.username} (namespace: {auth_namespace})")
                return dict(user=current_user)
            elif isinstance(current_user, Admin) and auth_namespace == 'admin':
                # Allow admin to access class routes but maintain admin context
                if '/class/' in path:
                    print(f"Context processor [{path}]: Admin {current_user.username} accessing class route (namespace: {auth_namespace})")
                    return dict(user=current_user)
                else:
                    print(f"Context processor [{path}]: Admin {current_user.username} blocked from user route (namespace: {auth_namespace})")
                    return dict(user=None)
            else:
                print(f"Context processor [{path}]: Authentication type/namespace mismatch - user type: {type(current_user)}, namespace: {auth_namespace}")
                return dict(user=None)
        
        # Session-based authentication ONLY for user namespace
        if 'user_id' in session and auth_namespace == 'user':
            try:
                from user.models.user import User
                user = User.query.get(session['user_id'])
                if user:
                    print(f"Context processor [{path}]: Found user via session: {user.username} (namespace: {auth_namespace})")
                    return dict(user=user)
                else:
                    print(f"Context processor [{path}]: User ID {session['user_id']} not found - clearing session")
                    session.pop('user_id', None)
                    session.pop('auth_namespace', None)
            except Exception as e:
                print(f"Context processor [{path}]: Error getting user from session: {e}")
                session.pop('user_id', None)
                session.pop('auth_namespace', None)
        
        # No user found
        print(f"Context processor [{path}]: No user found (namespace: {auth_namespace})")
        return dict(user=None)
    
    # Add context processor for admin sidebar classes
    @app.context_processor
    def inject_admin_sidebar_context():
        """Inject classes for admin sidebar display"""
        from flask import request
        from flask_login import current_user
        
        try:
            path = request.path if request else "unknown"
        except:
            path = "unknown"
        
        # Only inject for admin routes
        if path.startswith('/admin'):
            try:
                from admin.models.class_model import Class
                
                # Check if user is authenticated admin
                if current_user.is_authenticated and hasattr(current_user, 'role'):
                    # If super_admin, show all classes
                    if current_user.role == 'super_admin':
                        all_classes_query = Class.query.all()
                    else:
                        all_classes_query = Class.query.filter_by(created_by=getattr(current_user, 'id', None)).all()
                    
                    # Filter for active classes, but include all if no active ones found
                    active_classes = [cls for cls in all_classes_query if getattr(cls, 'status', None) == 'active']
                    all_classes = active_classes if active_classes else all_classes_query
                    all_classes = sorted(all_classes, key=lambda x: x.name) if all_classes else []
                    
                    print(f"Context processor [{path}]: Injected {len(all_classes)} classes for sidebar")
                    return dict(all_classes=all_classes)
                else:
                    return dict(all_classes=[])
            except Exception as e:
                print(f"Context processor [{path}]: Error loading classes for sidebar: {e}")
                return dict(all_classes=[])
        
        return dict()
    
    # Register template helpers
    try:
        from user.template_helpers import register_template_helpers
        register_template_helpers(app)
    except ImportError:
        pass  # Template helpers not available yet
    
    return app