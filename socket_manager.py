from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask import request, session
from flask_login import current_user
import functools
import eventlet
from datetime import datetime

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
    engineio_logger=False,  # Disable engine.io logging
    transports=['polling', 'websocket'],  # Allow both transports
    allow_upgrades=True,  # Allow transport upgrades
    cookie=None  # Disable cookies for better compatibility
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
        admin_check_results = []
        
        # Method 1: Check if user is instance of Admin model (from admins table)
        try:
            from admin.models.user import Admin
            if isinstance(current_user, Admin):
                is_admin = True
                admin_check_results.append(f"✅ Admin model instance ({current_user.__tablename__})")
        except ImportError as e:
            admin_check_results.append(f"⚠️ Admin model import failed: {e}")
        
        # Method 2: Check if user is instance of AdminUser model (from admin_users table)
        if not is_admin:
            try:
                from admin.models.user import AdminUser
                if isinstance(current_user, AdminUser):
                    is_admin = True
                    admin_check_results.append(f"✅ AdminUser model instance ({current_user.__tablename__})")
            except ImportError:
                admin_check_results.append("⚠️ AdminUser model not available")
        
        # Method 3: Check for is_admin attribute
        if not is_admin and hasattr(current_user, 'is_admin') and current_user.is_admin:
            is_admin = True
            admin_check_results.append(f"✅ is_admin=True")
        
        # Method 4: Check for admin role
        if not is_admin and hasattr(current_user, 'role'):
            role = getattr(current_user, 'role', '').lower()
            if role in ['admin', 'super_admin', 'administrator']:
                is_admin = True
                admin_check_results.append(f"✅ Admin role: {current_user.role}")
        
        # Method 5: Check table name directly
        if not is_admin and hasattr(current_user, '__tablename__'):
            if current_user.__tablename__ in ['admins', 'admin_users']:
                is_admin = True
                admin_check_results.append(f"✅ Admin table: {current_user.__tablename__}")
        
        # Method 6: Check if user exists in admin tables by username
        if not is_admin and hasattr(current_user, 'username'):
            try:
                from admin.models.user import Admin, AdminUser
                # Check admins table
                admin_user = Admin.query.filter_by(username=current_user.username).first()
                if admin_user:
                    is_admin = True
                    admin_check_results.append(f"✅ Found in admins table (ID: {admin_user.id})")
                else:
                    # Check admin_users table
                    admin_user = AdminUser.query.filter_by(username=current_user.username).first()
                    if admin_user and admin_user.is_admin:
                        is_admin = True
                        admin_check_results.append(f"✅ Found in admin_users table (ID: {admin_user.id})")
            except Exception as e:
                admin_check_results.append(f"⚠️ Admin table lookup failed: {e}")
        
        # Log all validation results for debugging
        print(f"🔍 Admin validation for user: {getattr(current_user, 'username', 'unknown')}")
        print(f"   - User type: {type(current_user)}")
        print(f"   - User ID: {getattr(current_user, 'id', 'N/A')}")
        print(f"   - Table name: {getattr(current_user, '__tablename__', 'N/A')}")
        print(f"   - Has is_admin: {hasattr(current_user, 'is_admin')}")
        print(f"   - is_admin value: {getattr(current_user, 'is_admin', 'N/A')}")
        print(f"   - Has role: {hasattr(current_user, 'role')}")
        print(f"   - Role value: {getattr(current_user, 'role', 'N/A')}")
        for result in admin_check_results:
            print(f"   {result}")
        
        # Final validation
        if not is_admin:
            print(f"❌ Admin validation failed - all methods returned false")
            emit('error', {'message': 'Unauthorized: Admin access required'})
            return
        
        print(f"✅ Admin validation successful for: {current_user.username}")
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
            print(f"\n🔌 WebSocket Connection Attempt - Session ID: {request.sid}")
            print(f"📍 Remote Address: {request.remote_addr}")
            print(f"🔍 Request headers: {dict(request.headers)}")
            print(f"🍪 Session data: {dict(session) if session else 'No session'}")
            print(f"👤 Current user: {current_user}")
            print(f"🔐 Is authenticated: {current_user.is_authenticated}")
            print(f"🧩 User type: {type(current_user)}")
            
            if current_user.is_authenticated:
                user_id = current_user.id
                username = getattr(current_user, 'username', f'User{user_id}')
                
                print(f"✅ Authenticated user detected: {username} (ID: {user_id})")
                print(f"📋 User type: {type(current_user)}")
                print(f"📋 User table: {getattr(current_user, '__tablename__', 'unknown')}")
                
                # Register with monitor
                socket_monitor.register_connection(request.sid, user_id)
                
                # Store connection info
                user_connections[request.sid] = {
                    'user_id': user_id,
                    'username': username,
                    'connected_at': datetime.utcnow().isoformat()
                }
                
                # Join user-specific room
                join_room(f'user_{user_id}')
                join_room('all_users')
                
                # ENHANCED admin detection - support both Admin and AdminUser models
                is_admin = False
                admin_detection_log = []
                
                # Method 1: Check if user is instance of Admin model (from admins table)
                try:
                    from admin.models.user import Admin
                    if isinstance(current_user, Admin):
                        is_admin = True
                        admin_detection_log.append("✅ Admin model instance detected")
                        print(f"🔐 Admin detected: {username} (instance of Admin model)")
                except ImportError:
                    admin_detection_log.append("⚠️ Admin model import failed")
                
                # Method 2: Check if user is instance of AdminUser model (from admin_users table)
                try:
                    from admin.models.user import AdminUser
                    if isinstance(current_user, AdminUser):
                        is_admin = True
                        admin_detection_log.append("✅ AdminUser model instance detected")
                        print(f"🔐 AdminUser detected: {username} (instance of AdminUser model)")
                    else:
                        # Check if user exists in AdminUser table by ID or username
                        admin_by_id = AdminUser.query.filter_by(id=user_id).first()
                        admin_by_username = AdminUser.query.filter_by(username=username).first()
                        
                        if admin_by_id and admin_by_id.is_admin:
                            is_admin = True
                            admin_detection_log.append(f"✅ Found in AdminUser table by ID (Admin: {admin_by_id.is_admin})")
                            print(f"🔐 Admin found in AdminUser table by ID: {username}")
                        elif admin_by_username and admin_by_username.is_admin:
                            is_admin = True
                            admin_detection_log.append(f"✅ Found in AdminUser table by username (Admin: {admin_by_username.is_admin})")
                            print(f"🔐 Admin found in AdminUser table by username: {username}")
                        else:
                            admin_detection_log.append("❌ Not found in AdminUser table or not admin")
                except ImportError:
                    admin_detection_log.append("⚠️ AdminUser model import failed")
                except Exception as e:
                    admin_detection_log.append(f"❌ AdminUser check error: {e}")
                
                # Method 3: Check if regular User has admin privileges (is_admin field)
                try:
                    if hasattr(current_user, 'is_admin') and current_user.is_admin:
                        is_admin = True
                        admin_detection_log.append("✅ is_admin=True on current_user")
                        print(f"🔐 Admin privileges detected: {username} (is_admin=True)")
                except:
                    admin_detection_log.append("❌ is_admin check failed")
                
                # Method 4: Check if user_type indicates admin role
                try:
                    if hasattr(current_user, 'user_type') and current_user.user_type in ['admin', 'instructor']:
                        is_admin = True
                        admin_detection_log.append(f"✅ Admin user_type: {current_user.user_type}")
                        print(f"🔐 Admin role detected: {username} (user_type={getattr(current_user, 'user_type', 'unknown')})")
                except:
                    admin_detection_log.append("❌ user_type check failed")
                
                # Method 5: Check tablename for admin tables
                try:
                    if hasattr(current_user, '__tablename__') and current_user.__tablename__ in ['admin_users', 'admins']:
                        is_admin = True
                        admin_detection_log.append(f"✅ Admin table: {current_user.__tablename__}")
                        print(f"🔐 Admin table detected: {username} (table: {current_user.__tablename__})")
                except:
                    admin_detection_log.append("❌ tablename check failed")
                
                # Log all admin detection results
                print(f"🔍 Admin detection results for {username}:")
                for log_entry in admin_detection_log:
                    print(f"   {log_entry}")
                print(f"🎯 Final admin status: {'ADMIN' if is_admin else 'USER'}")
                
                if is_admin:
                    join_room('admin_room')
                    print(f"✅ Admin {username} joined admin room")
                else:
                    print(f"🔍 Regular user {username} - not joining admin room")
                
                print(f"✅ User {username} (ID: {user_id}) connected via WebSocket")
                
                # Notify admins of user connection
                emit('user_connected', {
                    'user_id': user_id,
                    'username': username,
                    'timestamp': datetime.utcnow().isoformat(),
                    'is_admin': is_admin
                }, room='admin_room')
                
            else:
                print("❌ Unauthenticated user attempted WebSocket connection")
                print(f"📋 Anonymous user: {current_user.is_anonymous}")
                print(f"📋 Session keys: {list(session.keys()) if 'session' in globals() else 'No session'}")
                disconnect()
        except Exception as e:
            print(f"❌ Error in connect handler: {str(e)}")
            import traceback
            print(f"📋 Traceback: {traceback.format_exc()}")
            disconnect()
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
                    'timestamp': datetime.utcnow().isoformat()
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
                'server_time': datetime.utcnow().isoformat(),
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
