"""
Production Configuration for RiddleNet
Optimized for AWS deployment with proper environment variable handling
"""
import os
from datetime import timedelta

class ProductionConfig:
    """Production configuration with AWS optimizations"""
    
    # Basic Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fallback-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Database Configuration (AWS RDS)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://username:password@localhost/riddlenet_production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 120,
        'pool_pre_ping': True,
        'max_overflow': 20
    }
    
    # AWS Configuration
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    
    # S3 Configuration
    S3_BUCKET = os.environ.get('S3_BUCKET')
    S3_REGION = os.environ.get('S3_REGION', 'us-east-1')
    S3_LOCATION = f'https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/' if S3_BUCKET else None
    
    # Security Configuration
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Upload Configuration
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max upload
    UPLOAD_FOLDER = '/tmp/uploads'
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    # Redis Configuration (if using Redis)
    REDIS_URL = os.environ.get('REDIS_URL')
    
    # Cache Configuration
    CACHE_TYPE = "redis" if REDIS_URL else "simple"
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Mail Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # SocketIO Configuration
    SOCKETIO_ASYNC_MODE = 'eventlet'
    SOCKETIO_PING_TIMEOUT = 60
    SOCKETIO_PING_INTERVAL = 25
    
    # Static Files Configuration (for S3)
    if S3_BUCKET:
        # Use S3 for static files in production
        STATIC_URL_PATH = '/static'
        SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year cache
    
    @staticmethod
    def init_app(app):
        """Initialize application with production-specific settings"""
        
        # Configure logging for production
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug and not app.testing:
            # File handler for errors
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

# Create config object
config = ProductionConfig()