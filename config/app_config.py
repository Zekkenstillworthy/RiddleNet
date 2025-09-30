"""
Configuration for RiddleNet Application
Contains settings for authentication, routes, and environment-specific configurations
"""
import os

class Config:
    """Base configuration with common settings"""
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    WTF_CSRF_ENABLED = True
    
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Admin Authentication Configuration
    ADMIN_EXEMPT_ROUTES = [
        '/admin/login',
        '/admin/signup',
        '/admin/forgot-password',
        '/admin/reset-password/',
        '/admin/logout',
        '/admin/static/',
        '/admin/topology/',
        '/admin/troubleshooting/',
        '/admin/health'
    ]
    
    # Debug routes (only enabled when FLASK_DEBUG=true)
    DEBUG_ROUTES_ENABLED = os.environ.get('FLASK_DEBUG', '').lower() in ('true', '1', 'yes')
    
    # Server Configuration
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5001))
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    @staticmethod
    def init_app(app):
        """Initialize the application with this configuration"""
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dev.db')

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    # Database (AWS RDS)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://username:password@localhost/riddlenet_production'
    
    # Enhanced security for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # AWS Configuration
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    S3_BUCKET = os.environ.get('S3_BUCKET')
    
    @staticmethod
    def init_app(app):
        """Initialize production-specific settings"""
        Config.init_app(app)
        
        # Set up production logging
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug and not app.testing:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            
            file_handler = RotatingFileHandler(
                'logs/riddlenet.log', 
                maxBytes=10240000, 
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('RiddleNet production startup')

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}