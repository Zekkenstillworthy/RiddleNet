from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask import request
from flask_login import current_user
import functools

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

# Store active user connections with additional details
user_details = {}  # Store additional user info like connection time, activity

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
        if current_user.is_authenticated:
            user_id = current_user.id
            user_connections[request.sid] = user_id
            
            # Store additional user details
            user_details[request.sid] = {
                'username': getattr(current_user, 'username', 'Unknown'),
                'connected_at': datetime.datetime.now().isoformat(),
                'current_activity': 'Connected'
            }
            
            join_room(f"user_{user_id}")
            join_room("all_users")
            print(f"User {user_id} connected with session {request.sid}")
            
            # Notify admins of new connection
            emit('user_connected', {
                'user_id': user_id,
                'username': getattr(current_user, 'username', 'Unknown'),
                'timestamp': datetime.datetime.now().isoformat()
            }, room='admin_room')
        else:
            disconnect()

    @socketio.on('disconnect')
    def handle_disconnect():
        if request.sid in user_connections:
            user_id = user_connections[request.sid]
            username = user_details.get(request.sid, {}).get('username', 'Unknown')
            
            leave_room(f"user_{user_id}")
            leave_room("all_users")
            del user_connections[request.sid]
            
            # Clean up user details
            if request.sid in user_details:
                del user_details[request.sid]
                
            print(f"User {user_id} disconnected")
            
            # Notify admins of disconnection
            emit('user_disconnected', {
                'user_id': user_id,
                'username': username,
                'timestamp': datetime.datetime.now().isoformat()
            }, room='admin_room')

    # General room joining
    @socketio.on('join_general')
    @authenticated_only
    def handle_join_general(data):
        join_room("all_users")
        emit('joined', {'room': 'general'})

    # Admin room joining
    @socketio.on('join_admin')
    @authenticated_only
    def handle_join_admin(data):
        # Check if user is admin (you'll need to implement this check)
        if hasattr(current_user, 'is_admin') and current_user.is_admin:
            join_room("admin_room")
            emit('joined', {'room': 'admin'})

# Helper functions for emitting events
def notify_user(user_id, event, data):
    """Send event to a specific user"""
    room = f"user_{user_id}"
    socketio.emit(event, data, room=room)

def notify_topology_users(topology_id, event, data):
    """Send event to users in a specific topology room"""
    room = f"topology_{topology_id}"
    socketio.emit(event, data, room=room)

def notify_troubleshooting_users(scenario_id, event, data):
    """Send event to users in a specific troubleshooting room"""
    room = f"troubleshooting_{scenario_id}"
    socketio.emit(event, data, room=room)

def broadcast_to_all(event, data):
    """Send event to all connected users"""
    socketio.emit(event, data, room="all_users")

def notify_admins(event, data):
    """Send event to all connected admins"""
    socketio.emit(event, data, room="admin_room")

# Import datetime for timestamps
import datetime

def get_active_users_list():
    """Get list of currently active users with details"""
    active_users = []
    
    try:
        from user.models import User as UserModel
        
        for session_id, user_id in user_connections.items():
            user_info = user_details.get(session_id, {})
            
            # Try to get username from current stored details or database
            username = user_info.get('username')
            if not username and UserModel:
                try:
                    user = UserModel.query.get(user_id)
                    username = user.username if user else f"User_{user_id}"
                except:
                    username = f"User_{user_id}"
            
            active_users.append({
                'user_id': user_id,
                'username': username or f"User_{user_id}",
                'connected_at': user_info.get('connected_at', datetime.datetime.now().isoformat()),
                'current_activity': user_info.get('current_activity', 'Online'),
                'session_id': session_id
            })
    except Exception as e:
        print(f"Error getting active users: {e}")
        # Return basic info if there's an error
        for session_id, user_id in user_connections.items():
            active_users.append({
                'user_id': user_id,
                'username': f"User_{user_id}",
                'connected_at': datetime.datetime.now().isoformat(),
                'current_activity': 'Online',
                'session_id': session_id
            })
    
    return active_users

def update_user_activity(user_id, activity):
    """Update the current activity for a user"""
    session_id = None
    for sid, uid in user_connections.items():
        if uid == user_id:
            session_id = sid
            break
    
    if session_id and session_id in user_details:
        user_details[session_id]['current_activity'] = activity
