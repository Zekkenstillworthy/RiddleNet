"""
WSGI Entry Point for RiddleNet - Gunicorn Compatible
This file provides the WSGI entry point for production deployment with Gunicorn.
"""
import os
import sys

# Add the application directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Set production environment variables if not already set
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_DEBUG', 'false')

# Import the configured app and socketio from run.py
from run import app, socketio

# For Gunicorn, we need to expose both the Flask app and SocketIO app
# The SocketIO app wraps the Flask app for WebSocket support
application = socketio

# Also expose the Flask app directly for compatibility
flask_app = app

# Health check for load balancers
@app.route('/wsgi-health')
def wsgi_health():
    return {'status': 'healthy', 'server': 'wsgi'}, 200

if __name__ == "__main__":
    # This shouldn't be called in production, but useful for testing
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))