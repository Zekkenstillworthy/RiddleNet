from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask import request
from flask_login import current_user
import functools
import eventlet
import datetime

# Apply eventlet monkey patch for better performance
eventlet.monkey_patch()

# Initialize SocketIO without an app (we'll attach it later)
socketio = SocketIO(
    cors_allowed_origins="*", 
    async_mode='eventlet',
    ping_timeout=60,
    ping_interval=25,
    max_http_buffer_size=1024 * 1024 * 10,
    logger=False,  # Disable verbose logging
    engineio_logger=False  # Disable engine.io logging
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

def admin_only(f):
    """Decorator to ensure WebSocket connections are authenticated AND admin"""
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            emit('error', {'message': 'Authentication required'})
            disconnect()
            return
        
        # Enhanced admin check with multiple validation methods
        is_admin = False
        
        # Method 1: Check if user is instance of Admin model
        try:
            from admin.models.user import Admin
            if isinstance(current_user, Admin):
                is_admin = True
                print(f"✅ Admin validation successful: {current_user.username} (Admin model instance)")
        except ImportError as e:
            print(f"⚠️ Admin model import failed: {e}")
        
        # Method 2: Check for is_admin attribute
        if not is_admin and hasattr(current_user, 'is_admin') and current_user.is_admin:
            is_admin = True
            print(f"✅ Admin validation successful: {current_user.username} (is_admin=True)")
        
        # Method 3: Check for role attribute
        if not is_admin and hasattr(current_user, 'role') and current_user.role in ['admin', 'super_admin']:
            is_admin = True
            print(f"✅ Admin validation successful: {current_user.username} (role={current_user.role})")
        
        # Method 4: Check if user ID is in admin table
        if not is_admin:
            try:
                from admin.models.user import Admin
                admin_user = Admin.query.filter_by(username=current_user.username).first()
                if admin_user:
                    is_admin = True
                    print(f"✅ Admin validation successful: {current_user.username} (found in admin table)")
            except Exception as e:
                print(f"⚠️ Admin table lookup failed: {e}")
        
        # Final validation
        if not is_admin:
            print(f"❌ Admin validation failed for user: {getattr(current_user, 'username', 'unknown')}")
            print(f"   - User type: {type(current_user)}")
            print(f"   - Has is_admin: {hasattr(current_user, 'is_admin')}")
            print(f"   - is_admin value: {getattr(current_user, 'is_admin', 'N/A')}")
            print(f"   - Has role: {hasattr(current_user, 'role')}")
            print(f"   - Role value: {getattr(current_user, 'role', 'N/A')}")
            emit('error', {'message': 'Unauthorized: Admin access required'})
            return
        
        return f(*args, **kwargs)
    return wrapped

def init_socketio(app):
    """Initialize SocketIO with the Flask app"""
    socketio.init_app(app)
    register_handlers()
    return socketio

def register_handlers():
    """Register all WebSocket event handlers"""
    from utils.socket_monitor import socket_monitor
    
    # Connection events
    @socketio.on('connect')
    def handle_connect():
        """Handle user connection"""
        try:
            if current_user.is_authenticated:
                user_id = current_user.id
                username = getattr(current_user, 'username', f'User{user_id}')
                
                # Register with monitor
                socket_monitor.register_connection(request.sid, user_id)
                
                # Store connection info
                user_connections[request.sid] = {
                    'user_id': user_id,
                    'username': username,
                    'connected_at': datetime.datetime.utcnow().isoformat()
                }
                
                # Join user-specific room
                join_room(f'user_{user_id}')
                join_room('all_users')
                
                # Check if user is admin and join admin room
                is_admin = False
                if hasattr(current_user, 'is_admin') and current_user.is_admin:
                    is_admin = True
                else:
                    # Alternative check for Admin model
                    try:
                        from admin.models.user import Admin
                        if isinstance(current_user, Admin):
                            is_admin = True
                    except ImportError:
                        pass
                
                if is_admin:
                    join_room('admin_room')
                    print(f"✅ Admin {username} joined admin room")
                
                print(f"✅ User {username} (ID: {user_id}) connected via WebSocket")
                
                # Notify admins of user connection
                emit('user_connected', {
                    'user_id': user_id,
                    'username': username,
                    'timestamp': datetime.datetime.utcnow().isoformat()
                }, room='admin_room')
                
            else:
                print("❌ Unauthenticated user attempted WebSocket connection")
                disconnect()
        except Exception as e:
            print(f"❌ Error in connect handler: {str(e)}")
            socket_monitor.register_error(request.sid, e)

    @socketio.on('disconnect')
    def handle_disconnect(reason=None):
        """Handle user disconnection"""
        try:
            if request.sid in user_connections:
                user_info = user_connections[request.sid]
                user_id = user_info['user_id']
                username = user_info['username']
                
                # Register with monitor
                socket_monitor.register_disconnect(request.sid)
                
                # Remove from tracking
                del user_connections[request.sid]
                
                print(f"🔌 User {username} (ID: {user_id}) disconnected from WebSocket")
                
                # Notify admins of user disconnection
                emit('user_disconnected', {
                    'user_id': user_id,
                    'username': username,
                    'timestamp': datetime.datetime.utcnow().isoformat()
                }, room='admin_room')
        except Exception as e:
            print(f"❌ Error in disconnect handler: {str(e)}")

    @socketio.on('health_check')
    def handle_health_check(data):
        """Handle health check requests"""
        try:
            socket_monitor.update_activity(request.sid)
            emit('health_status', {
                'status': 'healthy',
                'server_time': datetime.datetime.utcnow().isoformat(),
                'active_connections': len(user_connections),
                'client_time': data.get('client_time') if data else None
            })
        except Exception as e:
            print(f"❌ Error in health check handler: {str(e)}")
            socket_monitor.register_error(request.sid, e)

    @socketio.on_error_default
    def default_error_handler(e):
        """Handle any unhandled socket errors"""
        print(f"❌ Unhandled WebSocket error: {str(e)}")
        socket_monitor.register_error(request.sid, e)

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

def update_user_activity(user_id, activity_type):
    """Update user activity tracking"""
    try:
        from utils.socket_monitor import socket_monitor
        
        # Find the user's session
        for sid, user_info in user_connections.items():
            if user_info['user_id'] == user_id:
                socket_monitor.update_activity(sid)
                break
    except Exception as e:
        print(f"❌ Error updating user activity: {str(e)}")

print("✅ Socket manager initialized successfully")
