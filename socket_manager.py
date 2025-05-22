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
    
    @socketio.on('connect')
    def handle_connect():
        """Handle new connections"""
        if current_user.is_authenticated:
            user_id = current_user.id
            # Store connection info
            if user_id not in user_connections:
                user_connections[user_id] = set()
            user_connections[user_id].add(request.sid)
            
            # Join user-specific room for direct messages
            join_room(f"user_{user_id}")
            
            # Join room for admin broadcasts
            join_room("all_users")
            
            print(f"User {user_id} connected with session ID: {request.sid}")
        else:
            print(f"Anonymous user connected: {request.sid}")
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnections"""
        if current_user.is_authenticated:
            user_id = current_user.id
            if user_id in user_connections and request.sid in user_connections[user_id]:
                user_connections[user_id].remove(request.sid)
                if not user_connections[user_id]:
                    del user_connections[user_id]
            print(f"User {user_id} disconnected")
        else:
            print(f"Anonymous user disconnected: {request.sid}")
    
    # Handle ping-pong for health checks
    @socketio.on('ping')
    def handle_ping(data):
        """Handle ping from client for connection health checks"""
        emit('pong', {'timestamp': data.get('timestamp')})
    
    # Topology-related events
    @socketio.on('join_topology')
    @authenticated_only
    def handle_join_topology(topology_id):
        """Join a specific topology room"""
        room_name = f"topology_{topology_id}"
        join_room(room_name)
        print(f"User {current_user.id} joined topology room: {room_name}")
    
    # Troubleshooting-related events
    @socketio.on('join_troubleshooting')
    @authenticated_only
    def handle_join_troubleshooting(scenario_id):
        """Join a specific troubleshooting scenario room"""
        room_name = f"troubleshooting_{scenario_id}"
        join_room(room_name)
        print(f"User {current_user.id} joined troubleshooting room: {room_name}")

# Helper functions for emitting events
def notify_user(user_id, event, data):
    """Send event to a specific user"""
    room = f"user_{user_id}"
    socketio.emit(event, data, room=room)

def notify_topology_users(topology_id, event, data):
    """Send event to all users in a specific topology room"""
    room = f"topology_{topology_id}"
    socketio.emit(event, data, room=room)

def notify_troubleshooting_users(scenario_id, event, data):
    """Send event to all users in a specific troubleshooting room"""
    room = f"troubleshooting_{scenario_id}"
    socketio.emit(event, data, room=room)

def broadcast_to_all(event, data):
    """Send event to all connected users"""
    socketio.emit(event, data, room="all_users")
