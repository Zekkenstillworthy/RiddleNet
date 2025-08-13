"""
Production entry point for RiddleNet application.
This file is used by Render for deployment.
"""
import os
import eventlet
eventlet.monkey_patch()

# Import your main application
from run import app, socketio

# Configure for production
if __name__ != "__main__":
    # This is being imported by gunicorn
    # Make sure the app is ready for production
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    
    # Use environment variables for production settings
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    
    # Database configuration for production
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Fix for Heroku/Render PostgreSQL URL
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    
    print("✅ Production configuration loaded")

# Export the application for gunicorn
if __name__ == "__main__":
    # Development mode
    socketio.run(app, debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))
else:
    # Production mode - let gunicorn handle this
    pass
