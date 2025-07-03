from socket_manager import socketio, authenticated_only, admin_only
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from __init__ import db
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

# ===== COLLABORATIVE TROUBLESHOOTING LOBBY SYSTEM =====
# Import the lobby manager
try:
    from services.troubleshooting_lobbies import lobby_manager
    print("✅ Troubleshooting lobby manager imported successfully")
except ImportError as e:
    print(f"⚠️ Warning: Could not import lobby manager: {e}")
    lobby_manager = None

# Lobby Management Events
@socketio.on('create_troubleshooting_lobby')
@authenticated_only
def handle_create_lobby(data):
    """Create a new collaborative troubleshooting lobby"""
    if not lobby_manager:
        emit('lobby_created', {'success': False, 'error': 'Lobby system not available'})
        return
    
    try:
        lobby_config = {
            'name': data.get('name', f"{current_user.username}'s Session"),
            'scenario_type': data.get('scenario_type', 'easy'),
            'scenario_id': data.get('scenario_id', 'network'),
            'max_participants': data.get('max_participants', 6)
        }
        
        lobby = lobby_manager.create_lobby(
            creator_id=str(current_user.id),
            creator_name=current_user.username,
            creator_profile_image=current_user.profile_img,
            lobby_config=lobby_config
        )
        
        # Join the lobby room
        room_name = f"troubleshooting_lobby_{lobby.id}"
        join_room(room_name)
        
        # Notify user of successful creation
        emit('lobby_created', {
            'success': True,
            'lobby': lobby.to_dict()
        })
        
        # Broadcast lobby availability to other users in lobby browser
        emit('new_lobby_available', {
            'lobby': lobby.to_dict()
        }, room='troubleshooting_browser')
        
        print(f"✅ User {current_user.username} created lobby {lobby.id}")
        
    except Exception as e:
        print(f"❌ Error creating lobby: {str(e)}")
        emit('lobby_created', {
            'success': False,
            'error': str(e)
        })

@socketio.on('join_troubleshooting_lobby')
@authenticated_only
def handle_join_lobby(data):
    """Join an existing troubleshooting lobby"""
    if not lobby_manager:
        emit('lobby_joined', {'success': False, 'error': 'Lobby system not available'})
        return
    
    try:
        lobby_id = data.get('lobby_id')
        
        if not lobby_id:
            emit('lobby_joined', {'success': False, 'error': 'Lobby ID required'})
            return
        
        result = lobby_manager.join_lobby(
            lobby_id=lobby_id,
            user_id=str(current_user.id),
            user_info={
                'username': current_user.username,
                'profile_image': current_user.profile_img
            }
        )
        
        if result['success']:
            lobby = result['lobby']
            room_name = f"troubleshooting_lobby_{lobby.id}"
            
            # Join the lobby room
            join_room(room_name)
            
            # Notify user of successful join
            emit('lobby_joined', {
                'success': True,
                'lobby': lobby.to_dict()
            })
            
            # Notify other participants of new user
            participant_data = lobby.participants[str(current_user.id)]
            join_event_data = {
                'user_id': str(current_user.id),
                'username': current_user.username,
                'participant_data': participant_data
            }
            
            print(f"🔍 Emitting participant_joined event:")
            print(f"   Room: {room_name}")
            print(f"   Event data: {join_event_data}")
            print(f"   Participants in lobby: {list(lobby.participants.keys())}")
            
            emit('participant_joined', join_event_data, room=room_name, include_self=False)
            
            # Send current network state to new participant
            emit('network_state_sync', {
                'network_state': lobby.network_state,
                'participants': lobby.participants
            })
            
            print(f"✅ User {current_user.username} joined lobby {lobby.id}")
        else:
            emit('lobby_joined', result)
            
    except Exception as e:
        print(f"❌ Error joining lobby: {str(e)}")
        emit('lobby_joined', {
            'success': False,
            'error': str(e)
        })

@socketio.on('leave_troubleshooting_lobby')
@authenticated_only
def handle_leave_lobby(data=None):
    """Leave current troubleshooting lobby"""
    if not lobby_manager:
        emit('lobby_left', {'success': False, 'error': 'Lobby system not available'})
        return
    
    try:
        lobby = lobby_manager.get_user_lobby(str(current_user.id))
        
        if lobby:
            room_name = f"troubleshooting_lobby_{lobby.id}"
            
            # Notify other participants
            emit('participant_left', {
                'user_id': str(current_user.id),
                'username': current_user.username
            }, room=room_name, include_self=False)
            
            # Leave the room
            leave_room(room_name)
            
            # Remove from lobby
            lobby_manager.leave_lobby(str(current_user.id))
            
            emit('lobby_left', {'success': True})
            
            print(f"✅ User {current_user.username} left lobby {lobby.id}")
        else:
            emit('lobby_left', {'success': True, 'message': 'Not in any lobby'})
        
    except Exception as e:
        print(f"❌ Error leaving lobby: {str(e)}")
        emit('lobby_left', {
            'success': False,
            'error': str(e)
        })

@socketio.on('get_public_lobbies')
@authenticated_only
def handle_get_public_lobbies(data=None):
    """Get list of available public lobbies"""
    if not lobby_manager:
        emit('public_lobbies', {'success': False, 'error': 'Lobby system not available'})
        return
    
    try:
        lobbies = lobby_manager.get_public_lobbies()
        emit('public_lobbies', {
            'success': True,
            'lobbies': lobbies
        })
    except Exception as e:
        print(f"❌ Error getting public lobbies: {str(e)}")
        emit('public_lobbies', {
            'success': False,
            'error': str(e)
        })

@socketio.on('get_my_lobby')
@authenticated_only
def handle_get_my_lobby(data=None):
    """Get current user's lobby"""
    if not lobby_manager:
        emit('my_lobby', {'success': False, 'error': 'Lobby system not available'})
        return
    
    try:
        lobby = lobby_manager.get_user_lobby(str(current_user.id))
        if lobby:
            emit('my_lobby', {
                'success': True,
                'lobby': lobby.to_dict()
            })
        else:
            emit('my_lobby', {
                'success': False,
                'error': 'Not in any lobby'
            })
    except Exception as e:
        print(f"❌ Error getting user lobby: {str(e)}")
        emit('my_lobby', {
            'success': False,
            'error': str(e)
        })

# Real-time Collaboration Events
@socketio.on('update_cursor_position')
@authenticated_only
def handle_cursor_update(data):
    """Update user's cursor position for real-time collaboration"""
    if not lobby_manager:
        return
    
    try:
        lobby = lobby_manager.get_user_lobby(str(current_user.id))
        if not lobby:
            return
        
        position = {
            'x': data.get('x', 0),
            'y': data.get('y', 0)
        }
        
        lobby.update_participant_cursor(str(current_user.id), position)
        lobby_manager.update_participant_activity(str(current_user.id))
        
        # Broadcast cursor position to other participants
        room_name = f"troubleshooting_lobby_{lobby.id}"
        emit('cursor_moved', {
            'user_id': str(current_user.id),
            'username': current_user.username,
            'position': position,
            'color': lobby.participants[str(current_user.id)]['color'],
            'profile_image': current_user.profile_img
        }, room=room_name, include_self=False)
        
    except Exception as e:
        print(f"❌ Error updating cursor: {str(e)}")

@socketio.on('update_network_topology')
@authenticated_only
def handle_network_update(data):
    """Handle real-time network topology updates"""
    if not lobby_manager:
        return
    
    try:
        lobby = lobby_manager.get_user_lobby(str(current_user.id))
        if not lobby:
            return
        
        changes = {
            'action': data.get('action', 'update'),
            'devices': data.get('devices', {}),
            'connections': data.get('connections', []),
            'removed_devices': data.get('removed_devices', []),
            'removed_connections': data.get('removed_connections', []),
            'selected_device': data.get('selected_device')
        }
        
        lobby.update_network_state(str(current_user.id), changes)
        lobby_manager.update_participant_activity(str(current_user.id))
        
        # Update participant's selected device
        if str(current_user.id) in lobby.participants:
            lobby.participants[str(current_user.id)]['selected_device'] = changes['selected_device']
        
        # Broadcast changes to other participants
        room_name = f"troubleshooting_lobby_{lobby.id}"
        emit('network_topology_updated', {
            'user_id': str(current_user.id),
            'username': current_user.username,
            'changes': changes,
            'network_state': lobby.network_state,
            'timestamp': datetime.datetime.utcnow().isoformat()
        }, room=room_name, include_self=False)
        
        print(f"🔄 Network topology updated by {current_user.username} in lobby {lobby.id}")
        
    except Exception as e:
        print(f"❌ Error updating network topology: {str(e)}")

# Device Locking Events
@socketio.on('lock_device')
@authenticated_only
def handle_lock_device(data):
    """Lock a device for exclusive editing"""
    if not lobby_manager:
        return
    
    try:
        lobby = lobby_manager.get_user_lobby(str(current_user.id))
        if not lobby:
            return
        
        device_id = data.get('device_id')
        if not device_id:
            return
        
        # Check if device is already locked by another user
        lock_result = lobby.lock_device(device_id, str(current_user.id))
        
        if lock_result['success']:
            room_name = f"troubleshooting_lobby_{lobby.id}"
            
            # Notify user of successful lock
            emit('device_locked', {
                'device_id': device_id,
                'locked_by': str(current_user.id),
                'username': current_user.username,
                'success': True
            })
            
            # Notify other participants
            emit('device_lock_changed', {
                'device_id': device_id,
                'locked_by': str(current_user.id),
                'username': current_user.username,
                'action': 'locked'
            }, room=room_name, include_self=False)
        else:
            emit('device_locked', {
                'device_id': device_id,
                'success': False,
                'error': lock_result['error'],
                'locked_by': lock_result.get('locked_by')
            })
    
    except Exception as e:
        print(f"❌ Error locking device: {str(e)}")

@socketio.on('unlock_device')
@authenticated_only  
def handle_unlock_device(data):
    """Unlock a device"""
    if not lobby_manager:
        return
    
    try:
        lobby = lobby_manager.get_user_lobby(str(current_user.id))
        if not lobby:
            return
        
        device_id = data.get('device_id')
        if not device_id:
            return
        
        unlock_result = lobby.unlock_device(device_id, str(current_user.id))
        
        if unlock_result['success']:
            room_name = f"troubleshooting_lobby_{lobby.id}"
            
            # Notify user of successful unlock
            emit('device_unlocked', {
                'device_id': device_id,
                'success': True
            })
            
            # Notify other participants
            emit('device_lock_changed', {
                'device_id': device_id,
                'locked_by': None,
                'action': 'unlocked'
            }, room=room_name, include_self=False)
        else:
            emit('device_unlocked', {
                'device_id': device_id,
                'success': False,
                'error': unlock_result['error']
            })
    
    except Exception as e:
        print(f"❌ Error unlocking device: {str(e)}")

# Real-time Device Movement
@socketio.on('move_device')
@authenticated_only
def handle_move_device(data):
    """Handle real-time device movement"""
    if not lobby_manager:
        return
    
    try:
        lobby = lobby_manager.get_user_lobby(str(current_user.id))
        if not lobby:
            return
        
        device_id = data.get('device_id')
        position = data.get('position', {})
        
        if not device_id or not position:
            return
        
        # Check if user has lock on this device
        if not lobby.user_has_device_lock(device_id, str(current_user.id)):
            emit('device_move_denied', {
                'device_id': device_id,
                'error': 'Device is locked by another user'
            })
            return
        
        # Update device position in network state
        lobby.update_device_position(device_id, position, str(current_user.id))
        
        room_name = f"troubleshooting_lobby_{lobby.id}"
        
        # Broadcast movement to other participants
        emit('device_moved', {
            'device_id': device_id,
            'position': position,
            'moved_by': str(current_user.id),
            'username': current_user.username
        }, room=room_name, include_self=False)
        
    except Exception as e:
        print(f"❌ Error moving device: {str(e)}")

# CLI Command Execution Events
@socketio.on('execute_cli_command')
@authenticated_only
def handle_cli_command(data):
    """Handle CLI command execution in collaborative session"""
    if not lobby_manager:
        return
    
    try:
        lobby = lobby_manager.get_user_lobby(str(current_user.id))
        if not lobby:
            return
        
        device_id = data.get('device_id')
        command = data.get('command', '').strip()
        
        if not device_id or not command:
            return
        
        # Check if user can access this device
        if not lobby.user_can_access_device(device_id, str(current_user.id)):
            emit('cli_command_denied', {
                'device_id': device_id,
                'error': 'Device access denied'
            })
            return
        
        # Process CLI command (this would include the actual command processing)
        output = f"Command executed: {command}"  # Placeholder for actual command processing
        
        # Add to lobby CLI history
        command_entry = lobby.add_cli_command(
            device_id=device_id,
            user_id=str(current_user.id),
            command=command,
            output=output
        )
        
        room_name = f"troubleshooting_lobby_{lobby.id}"
        
        # Broadcast CLI command to other participants
        emit('cli_command_executed', {
            'device_id': device_id,
            'command': command,
            'output': output,
            'user_id': str(current_user.id),
            'username': current_user.username,
            'timestamp': command_entry['timestamp']
        }, room=room_name, include_self=False)
        
        # Confirm to sender
        emit('cli_command_success', {
            'device_id': device_id,
            'command': command,
            'output': output
        })
        
        print(f"🖥️ CLI command executed by {current_user.username}: {command}")
        
    except Exception as e:
        print(f"❌ Error executing CLI command: {str(e)}")
        emit('cli_command_error', {
            'error': str(e)
        })

# Device Management Events
@socketio.on('add_device')
@authenticated_only
def handle_add_device(data):
    """Handle real-time device addition"""
    if not lobby_manager:
        return
    
    try:
        lobby = lobby_manager.get_user_lobby(str(current_user.id))
        if not lobby:
            return
        
        device_data = data.get('device')
        if not device_data:
            return
        
        # Generate unique device ID if not provided
        if 'id' not in device_data:
            device_data['id'] = f"{device_data.get('type', 'device')}_{datetime.datetime.utcnow().timestamp()}_{str(current_user.id)}"
        
        # Update network state
        changes = {
            'action': 'add_device',
            'devices': {device_data['id']: device_data}
        }
        
        lobby.update_network_state(str(current_user.id), changes)
        
        room_name = f"troubleshooting_lobby_{lobby.id}"
        
        # Broadcast device addition to other participants
        emit('device_added', {
            'device': device_data,
            'user_id': str(current_user.id),
            'username': current_user.username,
            'timestamp': datetime.datetime.utcnow().isoformat()
        }, room=room_name, include_self=False)
        
        print(f"➕ Device added by {current_user.username}: {device_data.get('type', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Error adding device: {str(e)}")

@socketio.on('remove_device')
@authenticated_only
def handle_remove_device(data):
    """Handle real-time device removal"""
    if not lobby_manager:
        return
    
    try:
        lobby = lobby_manager.get_user_lobby(str(current_user.id))
        if not lobby:
            return
        
        device_id = data.get('device_id')
        if not device_id:
            return
        
        # Check if device is locked by another user
        if not lobby.user_has_device_lock(device_id, str(current_user.id)):
            emit('device_removal_denied', {
                'device_id': device_id,
                'error': 'Device is locked by another user'
            })
            return
        
        # Update network state
        changes = {
            'action': 'remove_device',
            'removed_devices': [device_id]
        }
        
        lobby.update_network_state(str(current_user.id), changes)
        
        # Release any locks on this device
        if device_id in lobby.device_locks:
            del lobby.device_locks[device_id]
        
        room_name = f"troubleshooting_lobby_{lobby.id}"
        
        # Broadcast device removal to other participants
        emit('device_removed', {
            'device_id': device_id,
            'user_id': str(current_user.id),
            'username': current_user.username,
            'timestamp': datetime.datetime.utcnow().isoformat()
        }, room=room_name, include_self=False)
        
        print(f"➖ Device removed by {current_user.username}: {device_id}")
        
    except Exception as e:
        print(f"❌ Error removing device: {str(e)}")

# Connection Management Events
@socketio.on('add_connection')
@authenticated_only
def handle_add_connection(data):
    """Handle real-time connection addition"""
    if not lobby_manager:
        return
    
    try:
        lobby = lobby_manager.get_user_lobby(str(current_user.id))
        if not lobby:
            return
        
        device1_id = data.get('device1_id')
        device2_id = data.get('device2_id')
        connection_type = data.get('type', 'ethernet')
        
        if not device1_id or not device2_id:
            return
        
        # Create connection data
        connection_data = {
            'id': f"conn_{device1_id}_{device2_id}_{datetime.datetime.utcnow().timestamp()}",
            'device1_id': device1_id,
            'device2_id': device2_id,
            'type': connection_type,
            'created_by': str(current_user.id),
            'created_at': datetime.datetime.utcnow().isoformat()
        }
        
        # Update network state
        changes = {
            'action': 'add_connection',
            'connections': [connection_data]
        }
        
        lobby.update_network_state(str(current_user.id), changes)
        
        room_name = f"troubleshooting_lobby_{lobby.id}"
        
        # Broadcast connection addition to other participants
        emit('connection_added', {
            'connection': connection_data,
            'user_id': str(current_user.id),
            'username': current_user.username,
            'timestamp': datetime.datetime.utcnow().isoformat()
        }, room=room_name, include_self=False)
        
        print(f"🔗 Connection added by {current_user.username}: {device1_id} <-> {device2_id}")
        
    except Exception as e:
        print(f"❌ Error adding connection: {str(e)}")

@socketio.on('remove_connection')
@authenticated_only
def handle_remove_connection(data):
    """Handle real-time connection removal"""
    if not lobby_manager:
        return
    
    try:
        lobby = lobby_manager.get_user_lobby(str(current_user.id))
        if not lobby:
            return
        
        connection_id = data.get('connection_id')
        device1_id = data.get('device1_id')
        device2_id = data.get('device2_id')
        
        if not (connection_id or (device1_id and device2_id)):
            return
        
        # Update network state
        if connection_id:
            changes = {
                'action': 'remove_connection',
                'removed_connections': [{'id': connection_id}]
            }
        else:
            changes = {
                'action': 'remove_connection',
                'removed_connections': [{'device1_id': device1_id, 'device2_id': device2_id}]
            }
        
        lobby.update_network_state(str(current_user.id), changes)
        
        room_name = f"troubleshooting_lobby_{lobby.id}"
        
        # Broadcast connection removal to other participants
        emit('connection_removed', {
            'connection_id': connection_id,
            'device1_id': device1_id,
            'device2_id': device2_id,
            'user_id': str(current_user.id),
            'username': current_user.username,
            'timestamp': datetime.datetime.utcnow().isoformat()
        }, room=room_name, include_self=False)
        
        print(f"🔗❌ Connection removed by {current_user.username}")
        
    except Exception as e:
        print(f"❌ Error removing connection: {str(e)}")

# Device Configuration Events
@socketio.on('update_device_config')
@authenticated_only
def handle_device_config_update(data):
    """Handle real-time device configuration updates"""
    if not lobby_manager:
        return
    
    try:
        lobby = lobby_manager.get_user_lobby(str(current_user.id))
        if not lobby:
            return
        
        device_id = data.get('device_id')
        config_updates = data.get('config', {})
        
        if not device_id or not config_updates:
            return
        
        # Check if user has lock on this device
        if not lobby.user_has_device_lock(device_id, str(current_user.id)):
            emit('device_config_denied', {
                'device_id': device_id,
                'error': 'Device is locked by another user'
            })
            return
        
        # Update device configuration in network state
        if 'devices' not in lobby.network_state:
            lobby.network_state['devices'] = {}
        
        if device_id in lobby.network_state['devices']:
            lobby.network_state['devices'][device_id].update(config_updates)
        
        room_name = f"troubleshooting_lobby_{lobby.id}"
        
        # Broadcast configuration update to other participants
        emit('device_config_updated', {
            'device_id': device_id,
            'config': config_updates,
            'user_id': str(current_user.id),
            'username': current_user.username,
            'timestamp': datetime.datetime.utcnow().isoformat()
        }, room=room_name, include_self=False)
        
        print(f"⚙️ Device config updated by {current_user.username}: {device_id}")
        
    except Exception as e:
        print(f"❌ Error updating device config: {str(e)}")

# Progress Tracking Events
@socketio.on('update_scenario_progress')
@authenticated_only
def handle_scenario_progress_update(data):
    """Handle collaborative scenario progress updates"""
    if not lobby_manager:
        return
    
    try:
        lobby = lobby_manager.get_user_lobby(str(current_user.id))
        if not lobby:
            return
        
        progress_data = data.get('progress', {})
        
        # Update lobby progress
        if 'progress' not in lobby.__dict__:
            lobby.progress = {}
        
        lobby.progress.update({
            'last_updated_by': str(current_user.id),
            'last_updated_at': datetime.datetime.utcnow().isoformat(),
            **progress_data
        })
        
        # Update participant's individual progress
        if str(current_user.id) in lobby.participants:
            if 'progress' not in lobby.participants[str(current_user.id)]:
                lobby.participants[str(current_user.id)]['progress'] = {}
            lobby.participants[str(current_user.id)]['progress'].update(progress_data)
        
        room_name = f"troubleshooting_lobby_{lobby.id}"
        
        # Broadcast progress update to other participants
        emit('scenario_progress_updated', {
            'progress': progress_data,
            'user_id': str(current_user.id),
            'username': current_user.username,
            'lobby_progress': lobby.progress,
            'timestamp': datetime.datetime.utcnow().isoformat()
        }, room=room_name, include_self=False)
        
        print(f"📈 Progress updated by {current_user.username}")
        
    except Exception as e:
        print(f"❌ Error updating progress: {str(e)}")

# Chat Events
@socketio.on('send_lobby_chat')
@authenticated_only
def handle_send_lobby_chat(data):
    """Handle sending chat messages in collaborative lobby"""
    if not lobby_manager:
        return
    
    try:
        lobby = lobby_manager.get_user_lobby(str(current_user.id))
        if not lobby:
            emit('lobby_chat_error', {'error': 'Not in any lobby'})
            return
        
        message = data.get('message', '').strip()
        message_type = data.get('type', 'text')
        
        if not message:
            emit('lobby_chat_error', {'error': 'Message cannot be empty'})
            return
        
        # Add chat message to lobby
        chat_message = lobby.add_chat_message(
            user_id=str(current_user.id),
            message=message,
            message_type=message_type
        )
        
        room_name = f"troubleshooting_lobby_{lobby.id}"
        
        # Broadcast chat message to all participants in the lobby
        emit('lobby_chat_message', chat_message, room=room_name)
        
        print(f"💬 Chat message from {current_user.username} in lobby {lobby.id}: {message}")
        
    except Exception as e:
        print(f"❌ Error sending chat message: {str(e)}")
        emit('lobby_chat_error', {'error': str(e)})

# Full State Synchronization
@socketio.on('request_full_sync')
@authenticated_only
def handle_full_sync_request(data=None):
    """Handle request for full lobby state synchronization"""
    if not lobby_manager:
        return
    
    try:
        lobby = lobby_manager.get_user_lobby(str(current_user.id))
        if not lobby:
            return
        
        # Send complete lobby state to requesting user
        emit('full_state_sync', {
            'lobby': lobby.to_dict(),
            'network_state': lobby.network_state,
            'device_locks': lobby.device_locks,
            'participants': lobby.participants,
            'progress': getattr(lobby, 'progress', {}),
            'timestamp': datetime.datetime.utcnow().isoformat()
        })
        
        print(f"🔄 Full sync sent to {current_user.username}")
        
    except Exception as e:
        print(f"❌ Error sending full sync: {str(e)}")

# Browse lobbies room for discovery
@socketio.on('join_lobby_browser')
@authenticated_only
def handle_join_lobby_browser(data=None):
    """Join the lobby browser room to receive lobby updates"""
    join_room('troubleshooting_browser')
    emit('joined_lobby_browser', {'success': True})
    print(f"✅ User {current_user.username} joined lobby browser")

@socketio.on('leave_lobby_browser')
@authenticated_only
def handle_leave_lobby_browser(data=None):
    """Leave the lobby browser room"""
    leave_room('troubleshooting_browser')
    emit('left_lobby_browser', {'success': True})
    print(f"✅ User {current_user.username} left lobby browser")

# Admin lobby management
@socketio.on('admin_get_all_lobbies')
@admin_only
def handle_admin_get_all_lobbies(data=None):
    """Get all lobbies for admin monitoring"""
    if not lobby_manager:
        emit('admin_lobbies', {'success': False, 'error': 'Lobby system not available'})
        return
    
    try:
        all_lobbies = [lobby.to_dict() for lobby in lobby_manager.lobbies.values()]
        stats = lobby_manager.get_stats()
        
        emit('admin_lobbies', {
            'success': True,
            'lobbies': all_lobbies,
            'stats': stats
        })
    except Exception as e:
        print(f"❌ Error getting admin lobbies: {str(e)}")
        emit('admin_lobbies', {
            'success': False,
            'error': str(e)
        })

@socketio.on('admin_close_lobby')
@admin_only
def handle_admin_close_lobby(data):
    """Allow admin to close a lobby"""
    if not lobby_manager:
        emit('admin_lobby_closed', {'success': False, 'error': 'Lobby system not available'})
        return
    
    try:
        lobby_id = data.get('lobby_id')
        if not lobby_id:
            emit('admin_lobby_closed', {'success': False, 'error': 'Lobby ID required'})
            return
        
        lobby = lobby_manager.get_lobby_by_id(lobby_id)
        if not lobby:
            emit('admin_lobby_closed', {'success': False, 'error': 'Lobby not found'})
            return
        
        # Notify participants
        room_name = f"troubleshooting_lobby_{lobby.id}"
        emit('lobby_closed_by_admin', {
            'message': 'This session has been closed by an administrator.',
            'admin_name': current_user.username
        }, room=room_name)
        
        # Mark lobby as inactive
        lobby.is_active = False
        lobby.add_chat_message('system', f"Session closed by administrator {current_user.username}", 'system')
        
        # Force leave all participants
        for user_id in list(lobby.participants.keys()):
            lobby_manager.leave_lobby(user_id)
        
        emit('admin_lobby_closed', {'success': True, 'lobby_id': lobby_id})
        print(f"✅ Admin {current_user.username} closed lobby {lobby_id}")
        
    except Exception as e:
        print(f"❌ Error closing lobby: {str(e)}")
        emit('admin_lobby_closed', {
            'success': False,
            'error': str(e)
        })

print("✅ Socket events module loaded successfully")
