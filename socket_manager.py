from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask import request
from flask_login import current_user
import functools
import eventlet

# Apply eventlet monkey patch for better performance
eventlet.monkey_patch()

# Initialize SocketIO without an app (we'll attach it later)
socketio = SocketIO(
    cors_allowed_origins="*", 
    async_mode='eventlet',
    ping_timeout=60,
    ping_interval=25,
    max_http_buffer_size=1024 * 1024 * 10  # 10MB buffer
)

# Store active user connections
user_connections = {}

def authenticated_only(f):
    """Decorator to ensure WebSocket connections are authenticated"""
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped

def init_socketio(app):
    """Initialize SocketIO with the Flask app"""
    socketio.init_app(app)
    register_handlers()
    return socketio

def register_handlers():
    """Register all WebSocket event handlers"""
    # Connection events
    @socketio.on('connect')
    def handle_connect():
        """Handle user connection"""
        if current_user.is_authenticated:
            user_id = current_user.id
            username = getattr(current_user, 'username', f'User{user_id}')
            
            # Store connection info
            user_connections[request.sid] = {
                'user_id': user_id,
                'username': username,
                'connected_at': socketio.server.manager.get_timestamp()
            }
            
            # Join user-specific room
            join_room(f'user_{user_id}')
            join_room('all_users')
            
            # Check if user is admin and join admin room
            if hasattr(current_user, 'is_admin') and current_user.is_admin:
                join_room('admin_room')
            
            print(f"✅ User {username} (ID: {user_id}) connected via WebSocket")
            
            # Notify admins of user connection
            emit('user_connected', {
                'user_id': user_id,
                'username': username,
                'timestamp': socketio.server.manager.get_timestamp()
            }, room='admin_room')
            
        else:
            print("❌ Unauthenticated user attempted WebSocket connection")
            disconnect()

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle user disconnection"""
        if request.sid in user_connections:
            user_info = user_connections[request.sid]
            user_id = user_info['user_id']
            username = user_info['username']
            
            # Remove from tracking
            del user_connections[request.sid]
            
            print(f"🔌 User {username} (ID: {user_id}) disconnected from WebSocket")
            
            # Notify admins of user disconnection
            emit('user_disconnected', {
                'user_id': user_id,
                'username': username,
                'timestamp': socketio.server.manager.get_timestamp()
            }, room='admin_room')

def get_active_users_list():
    """Get list of currently connected users"""
    active_users = []
    for sid, user_info in user_connections.items():
        active_users.append({
            'user_id': user_info['user_id'],
            'username': user_info['username'],
            'connected_at': user_info['connected_at'],
            'session_id': sid
        })
    return active_users

def notify_admins(event_name, data):
    """Helper function to notify all admins"""
    socketio.emit(event_name, data, room='admin_room')

def notify_user(user_id, event_name, data):
    """Helper function to notify a specific user"""
    socketio.emit(event_name, data, room=f'user_{user_id}')

def broadcast_to_all(event_name, data):
    """Helper function to broadcast to all connected users"""
    socketio.emit(event_name, data, room='all_users')

# Health check endpoint
@socketio.on('health_check')
def handle_health_check():
    """Handle health check requests"""
    emit('health_status', {
        'status': 'healthy',
        'server_time': socketio.server.manager.get_timestamp(),
        'active_connections': len(user_connections)
    })

print("✅ Socket manager initialized successfully")
