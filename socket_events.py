from socket_manager import socketio, authenticated_only
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from user.models import db
import datetime
import json

try:
    from user.models import User as UserModel
except ImportError:
    # Handle case where UserModel might be in a different module
    UserModel = None

# Health check events
@socketio.on('ping')
def handle_ping(data):
    """Handle ping from client for health check"""
<<<<<<< HEAD
    emit('pong', {
        'server_time': datetime.datetime.now().isoformat(),
        'client_time': data.get('timestamp', 0)
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

=======
    timestamp = data.get('timestamp', datetime.datetime.utcnow().timestamp() * 1000)
    emit('pong', {
        'server_time': datetime.datetime.utcnow().timestamp() * 1000,
        'client_time': timestamp,
        'latency': 0  # Client will calculate
    })

# Troubleshooting events
>>>>>>> b4bcdda9fa30ee62712a08acef07916d94b94d26
@socketio.on('troubleshooting_progress')
@authenticated_only
def handle_troubleshooting_progress(data):
    """Handle real-time troubleshooting progress updates"""
    scenario_id = data.get('scenario_id')
    current_step = data.get('current_step')
    completed_steps = data.get('completed_steps', [])
    
<<<<<<< HEAD
    # Broadcast to other users in the same troubleshooting room
    room = f"troubleshooting_{scenario_id}"
    emit('user_troubleshooting_progress', {
        'user_id': current_user.id,
        'username': getattr(current_user, 'username', 'Unknown'),
        'scenario_id': scenario_id,
        'current_step': current_step,
        'completed_steps': completed_steps,
        'timestamp': datetime.datetime.now().isoformat()
    }, room=room, include_self=False)
    
    # Notify admins
    emit('user_troubleshooting_progress', {
        'user_id': current_user.id,
        'username': getattr(current_user, 'username', 'Unknown'),
        'scenario_id': scenario_id,
        'current_step': current_step,
        'completed_steps': completed_steps,
        'timestamp': datetime.datetime.now().isoformat()
    }, room='admin_room')
=======
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
    
    # You could also save this progress to the database here
>>>>>>> b4bcdda9fa30ee62712a08acef07916d94b94d26

# Topology network events
@socketio.on('topology_network_update')
@authenticated_only
def handle_topology_network_update(data):
    """Handle real-time topology network updates"""
    topology_id = data.get('topology_id')
    network_state = data.get('network_state')
    
<<<<<<< HEAD
    # Broadcast to other users in the same topology room
    room = f"topology_{topology_id}"
    emit('topology_state_updated', {
        'user_id': current_user.id,
        'username': getattr(current_user, 'username', 'Unknown'),
        'topology_id': topology_id,
        'network_state': network_state,
        'timestamp': datetime.datetime.now().isoformat()
    }, room=room, include_self=False)

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
        'timestamp': datetime.datetime.now().isoformat()
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
        'timestamp': datetime.datetime.now().isoformat()
    })
    
    # Notify admins of new essay submission
    emit('new_essay_submission', {
        'user_id': current_user.id,
        'username': getattr(current_user, 'username', 'Unknown'),
        'category': category,
        'content_length': len(content),
        'timestamp': datetime.datetime.now().isoformat()
    }, room='admin_room')

=======
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
    
>>>>>>> b4bcdda9fa30ee62712a08acef07916d94b94d26
# Admin specific events
@socketio.on('admin_broadcast')
@authenticated_only
def handle_admin_broadcast(data):
    """Allow admins to broadcast messages to all users"""
<<<<<<< HEAD
    # Check if user is admin (implement your admin check here)
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        emit('error', {'message': 'Unauthorized: Admin access required'})
        return
    
    title = data.get('title', 'Admin Message')
    message = data.get('message', '')
    message_type = data.get('type', 'info')
    target = data.get('target', 'all_users')  # Can be 'all_users', specific user_id, etc.
    
    broadcast_data = {
        'title': title,
        'message': message,
        'type': message_type,
        'admin_name': getattr(current_user, 'username', 'Admin'),
        'admin_id': current_user.id,
        'timestamp': datetime.datetime.now().isoformat()
    }
    
    recipients_count = 0
    if target == 'all_users':
        emit('admin_message', broadcast_data, room='all_users')
        # Count active users for feedback
        # This would require tracking active users in socket_manager
        recipients_count = len(getattr(socketio.server.manager, 'rooms', {}).get('all_users', []))
    else:
        # Handle specific user targeting
        emit('admin_message', broadcast_data, room=f'user_{target}')
        recipients_count = 1
    
    # Send confirmation back to admin
    emit('broadcast_status', {
        'success': True,
        'recipients': recipients_count,
        'message': f'Broadcast sent to {recipients_count} users'
    })

@socketio.on('get_active_users')
@authenticated_only
def handle_get_active_users():
    """Get list of currently active users - admin only"""
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        emit('error', {'message': 'Unauthorized: Admin access required'})
        return
    
    # Get active users from socket manager
    active_users = []
    try:
        # This would require implementing user tracking in socket_manager
        # For now, return a sample response
        from socket_manager import get_active_users_list
        active_users = get_active_users_list()
    except (ImportError, AttributeError):
        # Fallback if tracking not implemented
        active_users = [
            {
                'user_id': current_user.id,
                'username': getattr(current_user, 'username', 'Current User'),
                'connected_at': datetime.datetime.now().isoformat(),
                'current_activity': 'Dashboard'
            }
        ]
    
    emit('active_users_update', {'users': active_users})

# Real-time notifications
@socketio.on('send_notification')
@authenticated_only
def handle_send_notification(data):
    """Send real-time notifications to users"""
    # Check if user is admin
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
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
        'timestamp': datetime.datetime.now().isoformat()
    }
    
    if target_user:
        emit('notification', notification_data, room=f'user_{target_user}')
    else:
        emit('notification', notification_data, room='all_users')

# Error handling
@socketio.on_error_default
def default_error_handler(e):
    """Handle WebSocket errors"""
    print(f"WebSocket error: {e}")
    emit('error', {'message': 'An error occurred during WebSocket communication'})
=======
    # Check for admin role
    is_admin = hasattr(current_user, 'is_admin') and current_user.is_admin
    
    if not is_admin:
        emit('error', {'message': 'Unauthorized'})
        return
    
    message = data.get('message')
    target = data.get('target', 'all')  # 'all', 'user_{id}', 'topology_{id}', etc.
    
    if not message:
        return
    
    emit('admin_message', {
        'message': message,
        'admin_id': current_user.id,
        'admin_name': current_user.username,
        'timestamp': datetime.datetime.utcnow().isoformat()
    }, room=target)
>>>>>>> b4bcdda9fa30ee62712a08acef07916d94b94d26
