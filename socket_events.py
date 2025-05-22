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
    timestamp = data.get('timestamp', datetime.datetime.utcnow().timestamp() * 1000)
    emit('pong', {
        'server_time': datetime.datetime.utcnow().timestamp() * 1000,
        'client_time': timestamp,
        'latency': 0  # Client will calculate
    })

# Troubleshooting events
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
    
    # You could also save this progress to the database here

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
    
# Admin specific events
@socketio.on('admin_broadcast')
@authenticated_only
def handle_admin_broadcast(data):
    """Allow admins to broadcast messages to all users"""
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