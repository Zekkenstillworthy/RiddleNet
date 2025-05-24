from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask import request
from flask_login import current_user
import functools
<<<<<<< HEAD
=======
import eventlet

# Apply eventlet monkey patch for better performance
eventlet.monkey_patch()
>>>>>>> b4bcdda9fa30ee62712a08acef07916d94b94d26

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

<<<<<<< HEAD
# Store active user connections with additional details
user_details = {}  # Store additional user info like connection time, activity

=======
>>>>>>> b4bcdda9fa30ee62712a08acef07916d94b94d26
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
<<<<<<< HEAD
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
=======
    
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
>>>>>>> b4bcdda9fa30ee62712a08acef07916d94b94d26

# Helper functions for emitting events
def notify_user(user_id, event, data):
    """Send event to a specific user"""
    room = f"user_{user_id}"
    socketio.emit(event, data, room=room)

def notify_topology_users(topology_id, event, data):
<<<<<<< HEAD
    """Send event to users in a specific topology room"""
=======
    """Send event to all users in a specific topology room"""
>>>>>>> b4bcdda9fa30ee62712a08acef07916d94b94d26
    room = f"topology_{topology_id}"
    socketio.emit(event, data, room=room)

def notify_troubleshooting_users(scenario_id, event, data):
<<<<<<< HEAD
    """Send event to users in a specific troubleshooting room"""
=======
    """Send event to all users in a specific troubleshooting room"""
>>>>>>> b4bcdda9fa30ee62712a08acef07916d94b94d26
    room = f"troubleshooting_{scenario_id}"
    socketio.emit(event, data, room=room)

def broadcast_to_all(event, data):
    """Send event to all connected users"""
    socketio.emit(event, data, room="all_users")
<<<<<<< HEAD

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
=======
>>>>>>> b4bcdda9fa30ee62712a08acef07916d94b94d26
