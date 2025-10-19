from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask import request, session
from flask_login import current_user
import functools
from datetime import datetime

# Note: eventlet monkey patching is now handled in run.py
# Removed duplicate monkey patching to avoid conflicts

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
        is_instructor = False
        admin_check_results = []
        
        # Method 1: Check if user is instance of Instructor model (from admins table)
        try:
            from instructor.models.user import Instructor
            if isinstance(current_user, Instructor):
                is_instructor = True
                admin_check_results.append(f"✅ Instructor model instance ({current_user.__tablename__})")
        except ImportError as e:
            admin_check_results.append(f"⚠️ Instructor model import failed: {e}")
        
        # Method 2: Check if user is instance of InstructorUser model (from admin_users table)
        if not is_instructor:
            try:
                from instructor.models.user import InstructorUser
                if isinstance(current_user, InstructorUser):
                    is_instructor = True
                    admin_check_results.append(f"✅ InstructorUser model instance ({current_user.__tablename__})")
            except ImportError:
                admin_check_results.append("⚠️ InstructorUser model not available")
        
        # Method 3: Check for is_instructor attribute
        if not is_instructor and hasattr(current_user, 'is_instructor') and current_user.is_instructor:
            is_instructor = True
            admin_check_results.append(f"✅ is_instructor=True")
        
        # Method 4: Check for admin role
        if not is_instructor and hasattr(current_user, 'role'):
            role = getattr(current_user, 'role', '').lower()
            if role in ['admin', 'super_admin', 'administrator']:
                is_instructor = True
                admin_check_results.append(f"✅ Admin role: {current_user.role}")
        
        # Method 5: Check table name directly
        if not is_instructor and hasattr(current_user, '__tablename__'):
            if current_user.__tablename__ in ['admins', 'admin_users']:
                is_instructor = True
                admin_check_results.append(f"✅ Admin table: {current_user.__tablename__}")
        
        # Method 6: Check if user exists in admin tables by username
        if not is_instructor and hasattr(current_user, 'username'):
            try:
                from instructor.models.user import Instructor, InstructorUser
                # Check admins table
                admin_user = Instructor.query.filter_by(username=current_user.username).first()
                if admin_user:
                    is_instructor = True
                    admin_check_results.append(f"✅ Found in admins table (ID: {admin_user.id})")
                else:
                    # Check admin_users table
                    admin_user = InstructorUser.query.filter_by(username=current_user.username).first()
                    if admin_user and admin_user.is_instructor:
                        is_instructor = True
                        admin_check_results.append(f"✅ Found in admin_users table (ID: {admin_user.id})")
            except Exception as e:
                admin_check_results.append(f"⚠️ Admin table lookup failed: {e}")
        
        # Log all validation results for debugging
        print(f"🔍 Admin validation for user: {getattr(current_user, 'username', 'unknown')}")
        print(f"   - User type: {type(current_user)}")
        print(f"   - User ID: {getattr(current_user, 'id', 'N/A')}")
        print(f"   - Table name: {getattr(current_user, '__tablename__', 'N/A')}")
        print(f"   - Has is_instructor: {hasattr(current_user, 'is_instructor')}")
        print(f"   - is_instructor value: {getattr(current_user, 'is_instructor', 'N/A')}")
        print(f"   - Has role: {hasattr(current_user, 'role')}")
        print(f"   - Role value: {getattr(current_user, 'role', 'N/A')}")
        for result in admin_check_results:
            print(f"   {result}")
        
        # Final validation
        if not is_instructor:
            print(f"❌ Admin validation failed - all methods returned false")
            emit('error', {'message': 'Unauthorized: Admin access required'})
            return
        
        print(f"✅ Admin validation successful for: {current_user.username}")
        
        # Debug logging for announcement events
        func_name = f.__name__
        if 'announcement' in func_name.lower():
            print(f"📢 Announcement-related admin function called: {func_name}")
            print(f"   - Instructor user: {current_user.username}")
            print(f"   - Function args: {args}")
            print(f"   - Function kwargs: {kwargs}")
        
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
                
                # Join user-specific room and announcement rooms
                join_room(f'user_{user_id}')
                join_room('all_users')
                join_room('announcements')  # Add this for announcement compatibility
                
                print(f"✅ User {username} joined rooms: user_{user_id}, all_users, announcements")
                
                # ENHANCED admin detection - support both Admin and InstructorUser models
                is_instructor = False
                admin_detection_log = []
                
                # Method 1: Check if user is instance of Instructor model (from admins table)
                try:
                    from instructor.models.user import Instructor
                    if isinstance(current_user, Instructor):
                        is_instructor = True
                        admin_detection_log.append("✅ Instructor model instance detected")
                        print(f"🔐 Admin detected: {username} (instance of Instructor model)")
                except ImportError:
                    admin_detection_log.append("⚠️ Instructor model import failed")
                
                # Method 2: Check if user is instance of InstructorUser model (from admin_users table)
                try:
                    from instructor.models.user import InstructorUser
                    if isinstance(current_user, InstructorUser):
                        is_instructor = True
                        admin_detection_log.append("✅ InstructorUser model instance detected")
                        print(f"🔐 InstructorUser detected: {username} (instance of InstructorUser model)")
                    else:
                        # Check if user exists in InstructorUser table by ID or username
                        admin_by_id = InstructorUser.query.filter_by(id=user_id).first()
                        admin_by_username = InstructorUser.query.filter_by(username=username).first()
                        
                        if admin_by_id and admin_by_id.is_instructor:
                            is_instructor = True
                            admin_detection_log.append(f"✅ Found in InstructorUser table by ID (Admin: {admin_by_id.is_instructor})")
                            print(f"🔐 Admin found in InstructorUser table by ID: {username}")
                        elif admin_by_username and admin_by_username.is_instructor:
                            is_instructor = True
                            admin_detection_log.append(f"✅ Found in InstructorUser table by username (Admin: {admin_by_username.is_instructor})")
                            print(f"🔐 Admin found in InstructorUser table by username: {username}")
                        else:
                            admin_detection_log.append("❌ Not found in InstructorUser table or not admin")
                except ImportError:
                    admin_detection_log.append("⚠️ InstructorUser model import failed")
                except Exception as e:
                    admin_detection_log.append(f"❌ InstructorUser check error: {e}")
                
                # Method 3: Check if regular User has instructor privileges (is_instructor field)
                try:
                    if hasattr(current_user, 'is_instructor') and current_user.is_instructor:
                        is_instructor = True
                        admin_detection_log.append("✅ is_instructor=True on current_user")
                        print(f"🔐 Instructor privileges detected: {username} (is_instructor=True)")
                except:
                    admin_detection_log.append("❌ is_instructor check failed")
                
                # Method 4: Check if user_type indicates admin role
                try:
                    if hasattr(current_user, 'user_type') and current_user.user_type in ['admin', 'instructor']:
                        is_instructor = True
                        admin_detection_log.append(f"✅ Instructor user_type: {current_user.user_type}")
                        print(f"🔐 Admin role detected: {username} (user_type={getattr(current_user, 'user_type', 'unknown')})")
                except:
                    admin_detection_log.append("❌ user_type check failed")
                
                # Method 5: Check tablename for admin tables
                try:
                    if hasattr(current_user, '__tablename__') and current_user.__tablename__ in ['admin_users', 'admins']:
                        is_instructor = True
                        admin_detection_log.append(f"✅ Admin table: {current_user.__tablename__}")
                        print(f"🔐 Admin table detected: {username} (table: {current_user.__tablename__})")
                except:
                    admin_detection_log.append("❌ tablename check failed")
                
                # Log all admin detection results
                print(f"🔍 Admin detection results for {username}:")
                for log_entry in admin_detection_log:
                    print(f"   {log_entry}")
                print(f"🎯 Final admin status: {'ADMIN' if is_instructor else 'USER'}")
                
                if is_instructor:
                    join_room('admin_room')
                    print(f"✅ Admin {username} joined admin room")
                    
                    # Send updated user list to all admins
                    emit_admin_user_update()
                    
                    # Log admin connection activity
                    emit_admin_activity(
                        'admin_connected',
                        username,
                        f'Admin {username} connected to the system',
                        'bx-shield-check'
                    )
                else:
                    print(f"🔍 Regular user {username} - not joining admin room")
                    
                    # Log regular user connection
                    emit_admin_activity(
                        'user_connected', 
                        username,
                        f'User {username} connected to the platform',
                        'bx-user-plus'
                    )
                
                print(f"✅ User {username} (ID: {user_id}) connected via WebSocket")
                
                # Send updated user count to admins
                emit_admin_user_update()
                
                # Notify admins of user connection
                emit('user_connected', {
                    'user_id': user_id,
                    'username': username,
                    'timestamp': datetime.utcnow().isoformat(),
                    'is_instructor': is_instructor
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
                
                # Log disconnection activity
                emit_admin_activity(
                    'user_disconnected',
                    username,
                    f'User {username} disconnected from the platform',
                    'bx-user-minus'
                )
                
                # Remove from tracking
                del user_connections[request.sid]
                
                # Send updated user list
                emit_admin_user_update()
                
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

    # Lightweight ping/pong to support client health checks
    @socketio.on('ping')
    def handle_ping(data=None):
        try:
            emit('pong', {
                'server_time': datetime.utcnow().isoformat(),
                'client_time': (data or {}).get('client_time')
            })
        except Exception as e:
            print(f"❌ Error in ping handler: {str(e)}")

    # Optional dashboard room join (used by user dashboard for bookkeeping)
    @socketio.on('join_dashboard')
    @authenticated_only
    def handle_join_dashboard(data=None):
        try:
            user_id = getattr(current_user, 'id', None)
            username = getattr(current_user, 'username', 'unknown')
            # Ensure user-specific room is joined (already done on connect) and also a shared dashboard room
            if user_id is not None:
                join_room(f'user_{user_id}')
            join_room('dashboard')
            emit('dashboard_joined', {
                'success': True,
                'user_id': user_id,
                'username': username,
                'timestamp': datetime.utcnow().isoformat()
            })
            print(f"🧭 {username} joined dashboard room(s)")
        except Exception as e:
            print(f"❌ Error in join_dashboard handler: {str(e)}")

    @socketio.on('get_admin_user_list')
    @admin_only
    def handle_get_admin_user_list(data=None):
        """Handle request for current user list from admin panel"""
        emit_admin_user_update()

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

def emit_admin_user_update():
    """Send connected users update to admin panel"""
    try:
        connected_users = []
        for sid, conn_info in user_connections.items():
            connected_users.append({
                'username': conn_info['username'],
                'user_id': conn_info['user_id'],
                'connected_at': conn_info['connected_at'],
                'session_id': sid,
                'last_activity': 'Active'
            })
        
        socketio.emit('admin_users_update', {
            'users': connected_users,
            'total_count': len(connected_users)
        }, room='admin_room')
        
        print(f"📊 Sent user update to admin panel: {len(connected_users)} users")
        
    except Exception as e:
        print(f"❌ Error sending instructor user update: {e}")

def emit_admin_activity(activity_type, username, details, icon='bx-info-circle'):
    """Send activity update to admin panel"""
    try:
        activity_data = {
            'type': activity_type,
            'username': username,
            'details': details,
            'timestamp': datetime.utcnow().isoformat(),
            'icon': icon
        }
        
        socketio.emit('admin_activity_update', activity_data, room='admin_room')
        print(f"📈 Activity sent to admin panel: {activity_type} - {username}")
        
    except Exception as e:
        print(f"❌ Error sending admin activity: {e}")

print("✅ Socket manager initialized successfully")
