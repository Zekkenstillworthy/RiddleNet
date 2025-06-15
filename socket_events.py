from socket_manager import socketio, authenticated_only, admin_only
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from __init__ import db
import datetime
import datetime
import json

try:
    # Use a lazy import to avoid circular dependencies
    def get_user_model():
        from user.models.user import User
        return User
    
    UserModel = get_user_model()
except ImportError:
    # Handle case where UserModel might be in a different module
    UserModel = None

# Health check events
@socketio.on('ping')
def handle_ping(data):
    """Handle ping from client for health check"""
    timestamp = data.get('timestamp', datetime.datetime.utcnow().timestamp() * 1000)
    emit('pong', {
        'server_time': datetime.datetime.utcnow().timestamp() * 1000,
        'client_time': timestamp,
        'latency': 0  # Client will calculate
    })

# Topology events
@socketio.on('join_topology')
@authenticated_only
def handle_join_topology(topology_id):
    """Join a topology-specific room"""
    room = f"topology_{topology_id}"
    join_room(room)
    emit('joined', {'room': f'topology_{topology_id}'})
    print(f"User {current_user.id} joined topology room {topology_id}")

@socketio.on('leave_topology')
@authenticated_only
def handle_leave_topology(topology_id):
    """Leave a topology-specific room"""
    room = f"topology_{topology_id}"
    leave_room(room)
    emit('left', {'room': f'topology_{topology_id}'})

# Troubleshooting events
@socketio.on('join_troubleshooting')
@authenticated_only
def handle_join_troubleshooting(scenario_id):
    """Join a troubleshooting-specific room"""
    room = f"troubleshooting_{scenario_id}"
    join_room(room)
    emit('joined', {'room': f'troubleshooting_{scenario_id}'})
    print(f"User {current_user.id} joined troubleshooting room {scenario_id}")

@socketio.on('troubleshooting_progress')
@authenticated_only
def handle_troubleshooting_progress(data):
    """Handle real-time troubleshooting progress updates"""
    scenario_id = data.get('scenario_id')
    current_step = data.get('current_step')
    completed_steps = data.get('completed_steps', [])
    
    if not scenario_id:
        return
    
    # Join the scenario room if not already joined
    room_name = f"troubleshooting_{scenario_id}"
    join_room(room_name)
    
    # Broadcast progress to all users in this scenario (including admins)
    emit('user_troubleshooting_progress', {
        'user_id': current_user.id,
        'username': current_user.username,
        'scenario_id': scenario_id,
        'current_step': current_step,
        'completed_steps': completed_steps,
        'timestamp': datetime.datetime.utcnow().isoformat()
    }, room=room_name)

# Topology network events
@socketio.on('topology_network_update')
@authenticated_only
def handle_topology_network_update(data):
    """Handle real-time topology network updates"""
    topology_id = data.get('topology_id')
    network_state = data.get('network_state')
    
    if not topology_id or not network_state:
        return
    
    # Join the topology room if not already joined
    room_name = f"topology_{topology_id}"
    join_room(room_name)
    
    # Broadcast network state to all users in this topology
    emit('topology_state_updated', {
        'user_id': current_user.id,
        'username': current_user.username, 
        'topology_id': topology_id,
        'network_state': network_state,
        'timestamp': datetime.datetime.utcnow().isoformat()
    }, room=room_name)

@socketio.on('topology_completed')
@authenticated_only
def handle_topology_completion(data):
    """Handle topology completion events"""
    topology_type = data.get('topology_type')
    score = data.get('score', 0)
    
    # Notify the user
    emit('topology_completed', {
        'topology_type': topology_type,
        'score': score,
        'message': f"Congratulations! You've completed the {topology_type} topology."
    })
    
    # Notify admins
    emit('user_completed_topology', {
        'user_id': current_user.id,
        'username': getattr(current_user, 'username', 'Unknown'),
        'topology_type': topology_type,
        'score': score,
        'timestamp': datetime.datetime.utcnow().isoformat()
    }, room='admin_room')

# Essay submission events
@socketio.on('essay_submission')
@authenticated_only
def handle_essay_submission(data):
    """Handle essay submission events"""
    category = data.get('category')
    content = data.get('content', '')
    
    # Notify the user of successful submission
    emit('essay_submitted', {
        'message': f"Your essay for {category} has been submitted successfully.",
        'category': category,
        'timestamp': datetime.datetime.utcnow().isoformat()
    })
    
    # Notify admins of new essay submission
    emit('new_essay_submission', {
        'user_id': current_user.id,
        'username': getattr(current_user, 'username', 'Unknown'),
        'category': category,
        'content_length': len(content),
        'timestamp': datetime.datetime.utcnow().isoformat()
    }, room='admin_room')

# Admin specific events
@socketio.on('admin_broadcast')
@admin_only
def handle_admin_broadcast(data):
    """Allow admins to broadcast messages to all users"""
    title = data.get('title', 'Admin Message')
    message = data.get('message')
    msg_type = data.get('type', 'info')
    target = data.get('target', 'all_users')
    
    if not message:
        emit('broadcast_status', {'success': False, 'error': 'Message content required'})
        return
    
    # Prepare broadcast data
    broadcast_data = {
        'title': title,
        'message': message,
        'type': msg_type,
        'admin_id': current_user.id,
        'admin_name': getattr(current_user, 'username', 'Admin'),
        'timestamp': datetime.datetime.utcnow().isoformat()
    }
    
    # Determine target room and send broadcast
    recipients_count = 0
    try:
        from socket_manager import user_connections
        
        if target == 'all_users':
            emit('admin_message', broadcast_data, room='all_users')
            recipients_count = len(user_connections)
        elif target.startswith('user_'):
            emit('admin_message', broadcast_data, room=target)
            recipients_count = 1
        elif target.startswith('topology_'):
            emit('admin_message', broadcast_data, room=target)
            recipients_count = len([conn for conn in user_connections.values() 
                                  if conn.get('current_activity', '').startswith('topology')])
        elif target.startswith('troubleshooting_'):
            emit('admin_message', broadcast_data, room=target)
            recipients_count = len([conn for conn in user_connections.values() 
                                  if conn.get('current_activity', '').startswith('troubleshooting')])
        else:
            emit('admin_message', broadcast_data, room='all_users')
            recipients_count = len(user_connections)
        
        # Send success confirmation to admin
        emit('broadcast_status', {
            'success': True,
            'recipients': recipients_count,
            'target': target,
            'message': f'Broadcast sent to {recipients_count} users'
        })
        
        print(f"Admin {current_user.username} broadcast '{title}' to {recipients_count} users")
        
    except Exception as e:
        print(f"Error in admin broadcast: {str(e)}")
        emit('broadcast_status', {'success': False, 'error': str(e)})

@socketio.on('get_active_users')
@admin_only
def handle_get_active_users(data=None):
    """Get list of currently active users - admin only"""
    # Check if user is admin - handle both Admin model and AdminUser with is_admin=True
    is_admin = False
    
    # Check if it's an Admin model instance (from 'admins' table)
    if hasattr(current_user, '__tablename__') and current_user.__tablename__ == 'admins':
        is_admin = True
    # Check if it's an AdminUser with is_admin=True (from 'user' table)
    elif hasattr(current_user, 'is_admin') and current_user.is_admin:
        is_admin = True
    
    if not is_admin:
        emit('error', {'message': 'Unauthorized: Admin access required'})
        return
      # Get active users from socket manager
    active_users = []
    try:
        from socket_manager import get_active_users_list
        active_users = get_active_users_list()
    except (ImportError, AttributeError):
        # Fallback if tracking not implemented
        active_users = [
            {
                'user_id': current_user.id,
                'username': getattr(current_user, 'username', 'Current User'),
                'connected_at': datetime.datetime.utcnow().isoformat(),
                'current_activity': 'Dashboard'
            }
        ]
    
    emit('active_users_update', {'users': active_users})

@socketio.on('admin_get_users')
@admin_only
def handle_admin_get_users(data=None):
    """Alternative endpoint for getting users - admin only"""
    handle_get_active_users(data)

# Real-time notifications
@socketio.on('send_notification')
@admin_only
def handle_send_notification(data):
    """Send real-time notifications to users"""
    # Check if user is admin - handle both Admin model and AdminUser with is_admin=True
    is_admin = False
    
    # Check if it's an Admin model instance (from 'admins' table)
    if hasattr(current_user, '__tablename__') and current_user.__tablename__ == 'admins':
        is_admin = True
    # Check if it's an AdminUser with is_admin=True (from 'user' table)
    elif hasattr(current_user, 'is_admin') and current_user.is_admin:
        is_admin = True
    
    if not is_admin:
        emit('error', {'message': 'Unauthorized: Admin access required'})
        return
    
    target_user = data.get('target_user')
    title = data.get('title', 'Notification')
    message = data.get('message', '')
    notification_type = data.get('type', 'info')
    
    notification_data = {
        'title': title,
        'message': message,
        'type': notification_type,
        'from_admin': True,
        'admin_name': getattr(current_user, 'username', 'Admin'),
        'timestamp': datetime.datetime.utcnow().isoformat()
    }
    
    if target_user:
        emit('notification', notification_data, room=f'user_{target_user}')
    else:
        emit('notification', notification_data, room='all_users')

# Debug WebSocket event handler
@socketio.on('debug_admin_status')
@authenticated_only
def handle_debug_admin_status(data=None):
    """Debug endpoint to check admin status"""
    try:
        user_info = {
            'user_id': current_user.id,
            'username': getattr(current_user, 'username', 'Unknown'),
            'user_type': str(type(current_user)),
            'is_authenticated': current_user.is_authenticated,
            'has_is_admin': hasattr(current_user, 'is_admin'),
            'is_admin_value': getattr(current_user, 'is_admin', None),
            'has_role': hasattr(current_user, 'role'),
            'role_value': getattr(current_user, 'role', None),
            'timestamp': datetime.datetime.utcnow().isoformat()
        }
        
        # Check if user exists in admin table
        try:
            from admin.models.user import Admin
            admin_user = Admin.query.filter_by(username=current_user.username).first()
            user_info['exists_in_admin_table'] = admin_user is not None
            if admin_user:
                user_info['admin_table_id'] = admin_user.id
                user_info['admin_table_role'] = getattr(admin_user, 'role', 'admin')
        except Exception as e:
            user_info['admin_table_error'] = str(e)
        
        print(f"🔍 Debug admin status for {user_info['username']}: {user_info}")
        emit('debug_admin_response', user_info)
        
    except Exception as e:
        print(f"❌ Error in debug_admin_status: {str(e)}")
        emit('debug_admin_response', {'error': str(e)})

# Error handling
@socketio.on_error_default
def default_error_handler(e):
    """Handle WebSocket errors"""
    print(f"WebSocket error: {e}")
    emit('error', {'message': 'An error occurred during WebSocket communication'})

print("✅ Socket events module loaded successfully")
