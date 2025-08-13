# Instance-specific configuration
import os

basedir = os.path.abspath(os.path.dirname(__file__))

# Use Railway's DATABASE_URL if available, otherwise fallback to SQLite
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Railway provides PostgreSQL
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
else:
    # Local development with SQLite
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'riddlenet.db')

SQLALCHEMY_TRACK_MODIFICATIONS = False

# Use environment variable for secret key in production
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_for_development_only_change_in_production')
