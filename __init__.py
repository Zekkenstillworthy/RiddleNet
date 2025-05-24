from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

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
    app = Flask(__name__, instance_path=instance_path)

    # Configure the app
    # Use local config file instead of user.config
    app.config.from_pyfile('config.py', silent=True)
    
    # Set sensible defaults if config file doesn't exist
    if 'SQLALCHEMY_DATABASE_URI' not in app.config:
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "test.db")}'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_development_only')
    
    if config:
        app.config.update(config)    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize SocketIO with the app - moved to run.py to avoid circular imports
    
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
    mail.init_app(app)
    
    # Define the user loader function
    @login_manager.user_loader
    def load_user(user_id):
        # Make sure we're in an application context
        if not current_app:
            return None
            
        # Try different import paths to find User model
        try:
            # Import as UserModel to avoid conflicts
            from user.models import User as UserModel
            with app.app_context():
                return UserModel.query.get(int(user_id))
        except (ImportError, AttributeError):
            try:
                # Import as UserModel to avoid conflicts
                from user.models.user import User as UserModel
                with app.app_context():
                    return UserModel.query.get(int(user_id))
            except (ImportError, AttributeError):
                return None

    # Register blueprints
    try:
        from user.views import user_bp
        app.register_blueprint(user_bp)
        
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
        '''
        
        # Print registered rules for debugging
        print("Registered URL rules:")
        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint}: {rule.rule}")
    except ImportError as e:
        # If a blueprint can't be imported, continue without it
        print(f"Warning: Could not import blueprint: {e}")

    return app