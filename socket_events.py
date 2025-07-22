from socket_manager import socketio, authenticated_only, admin_only
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from __init__ import db
from datetime import datetime, timedelta
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
    timestamp = data.get('timestamp', datetime.utcnow().timestamp() * 1000)
    emit('pong', {
        'server_time': datetime.utcnow().timestamp() * 1000,
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
        'timestamp': datetime.utcnow().isoformat()
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
        'timestamp': datetime.utcnow().isoformat()
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
        'timestamp': datetime.utcnow().isoformat()
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
        'timestamp': datetime.utcnow().isoformat()
    })
    
    # Notify admins of new essay submission
    emit('new_essay_submission', {
        'user_id': current_user.id,
        'username': getattr(current_user, 'username', 'Unknown'),
        'category': category,
        'content_length': len(content),
        'timestamp': datetime.utcnow().isoformat()
    }, room='admin_room')

# Admin specific events

@socketio.on('get_active_users')
@admin_only
def handle_get_active_users(data=None):
    """Get list of currently active users - admin only"""
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
                'connected_at': datetime.utcnow().isoformat(),
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
    # Use the new notification service for enhanced notifications
    try:
        from services.notification_service import get_notification_service, NotificationType, NotificationPriority, NotificationChannel
        notification_service = get_notification_service(socketio)
        
        target_user = data.get('target_user')
        title = data.get('title', 'Notification')
        message = data.get('message', '')
        notification_type = NotificationType(data.get('notification_type', 'admin_notice'))
        priority = NotificationPriority(data.get('priority', 'normal'))
        channel = NotificationChannel(data.get('channel', 'websocket'))
        
        if target_user == 'all':
            # Send to all users
            result = notification_service.send_system_announcement(
                title=title,
                message=message,
                priority=priority
            )
        elif target_user == 'admins':
            # Send to all admins
            result = notification_service.send_admin_notification(
                notification_type=notification_type,
                title=title,
                message=message,
                priority=priority
            )
        else:
            # Send to specific user
            try:
                user_id = int(target_user)
                result = notification_service.send_user_notification(
                    user_id=user_id,
                    notification_type=notification_type,
                    title=title,
                    message=message,
                    priority=priority,
                    channel=channel
                )
            except (ValueError, TypeError):
                emit('error', {'message': 'Invalid user ID'})
                return
        
        # Send result back to admin
        emit('notification_sent', result)
        
    except Exception as e:
        print(f"Enhanced notification failed, falling back to legacy: {e}")
        
        # Fallback to legacy notification system
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
        'timestamp': datetime.utcnow().isoformat()
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
            'timestamp': datetime.utcnow().isoformat()
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
            'timestamp': datetime.utcnow().isoformat()
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
            device_data['id'] = f"{device_data.get('type', 'device')}_{datetime.utcnow().timestamp()}_{str(current_user.id)}"
        
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
            'timestamp': datetime.utcnow().isoformat()
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
            'timestamp': datetime.utcnow().isoformat()
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
            'id': f"conn_{device1_id}_{device2_id}_{datetime.utcnow().timestamp()}",
            'device1_id': device1_id,
            'device2_id': device2_id,
            'type': connection_type,
            'created_by': str(current_user.id),
            'created_at': datetime.utcnow().isoformat()
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
            'timestamp': datetime.utcnow().isoformat()
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
            'timestamp': datetime.utcnow().isoformat()
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
            'timestamp': datetime.utcnow().isoformat()
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
            'last_updated_at': datetime.utcnow().isoformat(),
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
            'timestamp': datetime.utcnow().isoformat()
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
            'timestamp': datetime.utcnow().isoformat()
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

# ===== LIVE LEADERBOARD SYSTEM =====
@socketio.on('join_leaderboard')
@authenticated_only
def handle_join_leaderboard(data):
    """Join leaderboard room for real-time updates"""
    try:
        user_id = data.get('user_id', str(current_user.id))
        page = data.get('page', 'leaderboard')
        
        # Join leaderboard room
        join_room('leaderboard_room')
        
        # Join category-specific rooms
        categories = ['networking', 'troubleshooting', 'collaboration', 'topology', 'crimping', 'riddle']
        for category in categories:
            join_room(f'leaderboard_{category}')
        
        # Send current leaderboard data
        leaderboard_data = get_live_leaderboard_data()
        emit('leaderboard_initialized', leaderboard_data)
        
        print(f"✅ User {current_user.username} joined leaderboard room")
        
    except Exception as e:
        print(f"❌ Error joining leaderboard: {str(e)}")
        emit('leaderboard_error', {'error': str(e)})

@socketio.on('get_leaderboard_data')
@authenticated_only
def handle_get_leaderboard_data(data):
    """Get current leaderboard data with filters"""
    try:
        category = data.get('category', 'all')
        time_period = data.get('time_period', 'all_time')
        limit = data.get('limit', 50)
        
        leaderboard_data = get_filtered_leaderboard_data(category, time_period, limit)
        emit('leaderboard_data', leaderboard_data)
        
    except Exception as e:
        print(f"❌ Error getting leaderboard data: {str(e)}")
        emit('leaderboard_error', {'error': str(e)})

@socketio.on('score_achieved')
@authenticated_only
def handle_score_achieved(data):
    """Handle new score achievement and update leaderboards"""
    try:
        from user.models.score import Score
        
        category = data.get('category', 'general')
        score = data.get('score', 0)
        
        # Save score to database
        new_score = Score(
            user_id=current_user.id,
            score=score,
            category=category,
            date_attempted=datetime.utcnow()
        )
        db.session.add(new_score)
        db.session.commit()
        
        # Get user's previous best score
        previous_best = db.session.query(Score).filter(
            Score.user_id == current_user.id,
            Score.category == category,
            Score.id != new_score.id
        ).order_by(Score.score.desc()).first()
        
        previous_score = previous_best.score if previous_best else 0
        is_new_high_score = score > previous_score
        
        # Get updated leaderboard data
        leaderboard_data = get_live_leaderboard_data()
        
        # Find user's new rank
        user_rank = get_user_rank(current_user.id, category)
        
        # Broadcast to all leaderboard rooms
        broadcast_data = {
            'type': 'score_update',
            'user_id': current_user.id,
            'username': current_user.username,
            'category': category,
            'score': score,
            'previous_score': previous_score,
            'is_new_high_score': is_new_high_score,
            'new_rank': user_rank,
            'timestamp': datetime.utcnow().isoformat(),
            'leaderboard_data': leaderboard_data
        }
        
        # Broadcast to all users in leaderboard room
        socketio.emit('live_leaderboard_update', broadcast_data, room='leaderboard_room')
        
        # Broadcast to category-specific room
        socketio.emit('category_leaderboard_update', broadcast_data, room=f'leaderboard_{category}')
        
        # Special broadcast for new high scores
        if is_new_high_score:
            socketio.emit('new_high_score_achieved', {
                'user_id': current_user.id,
                'username': current_user.username,
                'category': category,
                'score': score,
                'rank': user_rank,
                'timestamp': datetime.utcnow().isoformat()
            }, room='leaderboard_room')
        
        # Send confirmation to user
        emit('score_saved_successfully', {
            'score': score,
            'category': category,
            'rank': user_rank,
            'is_new_high_score': is_new_high_score
        })
        
        print(f"🏆 Score achieved: {current_user.username} scored {score} in {category}")
        
    except Exception as e:
        print(f"❌ Error handling score achievement: {str(e)}")
        emit('score_save_error', {'error': str(e)})

def get_live_leaderboard_data():
    """Get comprehensive leaderboard data for real-time updates"""
    try:
        from user.models.score import Score
        from user.models.user import User
        from sqlalchemy import func
        
        # Get overall leaderboard (top score per user)
        overall_leaderboard = db.session.query(
            User.id,
            User.username,
            User.profile_img,
            func.max(Score.score).label('best_score'),
            func.max(Score.date_attempted).label('latest_attempt'),
            Score.category
        ).select_from(User).join(Score).group_by(
            User.id, User.username, User.profile_img
        ).order_by(func.max(Score.score).desc()).limit(50).all()
        
        # Get category-specific leaderboards
        categories = ['networking', 'troubleshooting', 'collaboration', 'topology', 'crimping', 'riddle']
        category_leaderboards = {}
        
        for category in categories:
            category_data = db.session.query(
                User.id,
                User.username,
                User.profile_img,
                func.max(Score.score).label('best_score'),
                func.max(Score.date_attempted).label('latest_attempt')
            ).select_from(User).join(Score).filter(
                Score.category == category
            ).group_by(
                User.id, User.username, User.profile_img
            ).order_by(func.max(Score.score).desc()).limit(20).all()
            
            category_leaderboards[category] = [
                {
                    'user_id': entry.id,
                    'username': entry.username,
                    'profile_img': entry.profile_img,
                    'score': entry.best_score,
                    'category': category,
                    'date_attempted': entry.latest_attempt.isoformat() if entry.latest_attempt else None
                } for entry in category_data
            ]
        
        # Format overall leaderboard
        overall_entries = []
        for entry in overall_leaderboard:
            overall_entries.append({
                'user_id': entry.id,
                'username': entry.username,
                'profile_img': entry.profile_img,
                'score': entry.best_score,
                'category': entry.category,
                'date_attempted': entry.latest_attempt.isoformat() if entry.latest_attempt else None
            })
        
        return {
            'overall': overall_entries,
            'categories': category_leaderboards,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error getting leaderboard data: {str(e)}")
        return {'overall': [], 'categories': {}, 'timestamp': datetime.utcnow().isoformat()}

def get_filtered_leaderboard_data(category='all', time_period='all_time', limit=50):
    """Get filtered leaderboard data based on category and time period"""
    try:
        from user.models.score import Score
        from user.models.user import User
        from sqlalchemy import func
        
        # Base query
        query = db.session.query(
            User.id,
            User.username,
            User.profile_img,
            func.max(Score.score).label('best_score'),
            func.max(Score.date_attempted).label('latest_attempt'),
            Score.category
        ).select_from(User).join(Score)
        
        # Apply category filter
        if category != 'all':
            query = query.filter(Score.category == category)
        
        # Apply time period filter
        if time_period != 'all_time':
            now = datetime.utcnow()
            if time_period == 'daily':
                cutoff = now - datetime.timedelta(days=1)
            elif time_period == 'weekly':
                cutoff = now - datetime.timedelta(weeks=1)
            elif time_period == 'monthly':
                cutoff = now - datetime.timedelta(days=30)
            else:
                cutoff = now - datetime.timedelta(days=365)  # yearly
            
            query = query.filter(Score.date_attempted >= cutoff)
        
        # Group and order
        results = query.group_by(
            User.id, User.username, User.profile_img
        ).order_by(func.max(Score.score).desc()).limit(limit).all()
        
        # Format results
        entries = []
        for entry in results:
            entries.append({
                'user_id': entry.id,
                'username': entry.username,
                'profile_img': entry.profile_img,
                'score': entry.best_score,
                'category': entry.category,
                'date_attempted': entry.latest_attempt.isoformat() if entry.latest_attempt else None
            })
        
        return {
            'entries': entries,
            'category': category,
            'time_period': time_period,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error getting filtered leaderboard data: {str(e)}")
        return {'entries': [], 'category': category, 'time_period': time_period, 'timestamp': datetime.utcnow().isoformat()}

def get_user_rank(user_id, category='all'):
    """Get specific user's rank in leaderboard"""
    try:
        from user.models.score import Score
        from user.models.user import User
        from sqlalchemy import func
        
        # Get user's best score
        user_score_query = db.session.query(
            func.max(Score.score).label('best_score')
        ).filter(Score.user_id == user_id)
        
        if category != 'all':
            user_score_query = user_score_query.filter(Score.category == category)
        
        user_best_score = user_score_query.scalar()
        
        if not user_best_score:
            return None
        
        # Count users with better scores
        rank_query = db.session.query(
            func.count(func.distinct(Score.user_id)).label('rank')
        ).filter(Score.score > user_best_score)
        
        if category != 'all':
            rank_query = rank_query.filter(Score.category == category)
        
        users_above = rank_query.scalar() or 0
        
        return users_above + 1
        
    except Exception as e:
        print(f"❌ Error getting user rank: {str(e)}")
        return None

# ===== REAL-TIME PERFORMANCE FEEDBACK SYSTEM =====
try:
    from services.feedback_service import feedback_service
    print("✅ Feedback service imported successfully")
except ImportError as e:
    print(f"⚠️ Warning: Could not import feedback service: {e}")
    feedback_service = None

# Performance Feedback Events
@socketio.on('start_feedback_session')
@authenticated_only
def handle_start_feedback_session(data):
    """Start a new real-time feedback session"""
    if not feedback_service:
        emit('feedback_session_started', {'success': False, 'error': 'Feedback system not available'})
        return
    
    try:
        scenario_id = data.get('scenario_id', 'default')
        lobby_id = data.get('lobby_id')
        
        session_id = feedback_service.start_session(
            user_id=current_user.id,
            scenario_id=scenario_id,
            lobby_id=lobby_id
        )
        
        emit('feedback_session_started', {
            'success': True,
            'session_id': session_id,
            'scenario_id': scenario_id
        })
        
        print(f"✅ Feedback session started for user {current_user.username}: {session_id}")
        
    except Exception as e:
        print(f"❌ Error starting feedback session: {str(e)}")
        emit('feedback_session_started', {
            'success': False,
            'error': str(e)
        })

@socketio.on('end_feedback_session')
@authenticated_only
def handle_end_feedback_session(data):
    """End a feedback session"""
    if not feedback_service:
        emit('feedback_session_ended', {'success': False, 'error': 'Feedback system not available'})
        return
    
    try:
        session_id = data.get('session_id')
        
        if not session_id:
            emit('feedback_session_ended', {'success': False, 'error': 'Session ID required'})
            return
        
        session_analytics = feedback_service.end_session(session_id)
        
        emit('feedback_session_ended', {
            'success': True,
            'session_analytics': session_analytics
        })
        
        print(f"✅ Feedback session ended for user {current_user.username}: {session_id}")
        
    except Exception as e:
        print(f"❌ Error ending feedback session: {str(e)}")
        emit('feedback_session_ended', {
            'success': False,
            'error': str(e)
        })

@socketio.on('track_user_action')
@authenticated_only
def handle_track_user_action(data):
    """Track and provide real-time feedback for user actions"""
    if not feedback_service:
        return
    
    try:
        session_id = data.get('session_id')
        action_type = data.get('action_type')
        action_data = data.get('action_data', {})
        scenario_context = data.get('scenario_context', {})
        
        if not session_id or not action_type:
            emit('feedback_error', {'error': 'Session ID and action type required'})
            return
        
        # Add user context to action data
        action_data.update({
            'user_id': current_user.id,
            'username': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Record feedback and get real-time response
        feedback_data = feedback_service.record_feedback(
            session_id=session_id,
            user_id=current_user.id,
            action_type=action_type,
            action_data=action_data,
            scenario_context=scenario_context
        )
        
        # Send real-time feedback to user
        emit('real_time_feedback', feedback_data)
        
        # If in collaborative session, notify other participants
        lobby_id = action_data.get('lobby_id')
        if lobby_id:
            room_name = f"troubleshooting_lobby_{lobby_id}"
            emit('participant_action_feedback', {
                'user_id': current_user.id,
                'username': current_user.username,
                'action_type': action_type,
                'feedback': feedback_data
            }, room=room_name, include_self=False)
        
        print(f"📊 Action tracked for {current_user.username}: {action_type} -> {feedback_data['type']}")
        
    except Exception as e:
        print(f"❌ Error tracking user action: {str(e)}")
        emit('feedback_error', {'error': str(e)})

@socketio.on('get_progress_update')
@authenticated_only
def handle_get_progress_update(data):
    """Get current progress for a session"""
    if not feedback_service:
        return
    
    try:
        session_id = data.get('session_id')
        
        if not session_id:
            emit('progress_update_error', {'error': 'Session ID required'})
            return
        
        analytics = feedback_service.get_session_analytics(session_id)
        
        if analytics:
            emit('progress_update', {
                'session_id': session_id,
                'current_score': analytics['session']['total_score'],
                'completion_percentage': analytics['session']['completion_percentage'],
                'successful_actions': analytics['session']['successful_actions'],
                'total_actions': analytics['session']['total_actions'],
                'recommendations': analytics['recommendations']
            })
        else:
            emit('progress_update_error', {'error': 'Session not found'})
        
    except Exception as e:
        print(f"❌ Error getting progress update: {str(e)}")
        emit('progress_update_error', {'error': str(e)})

@socketio.on('get_session_analytics')
@authenticated_only
def handle_get_session_analytics(data):
    """Get detailed analytics for a completed session"""
    if not feedback_service:
        emit('session_analytics', {'success': False, 'error': 'Feedback system not available'})
        return
    
    try:
        session_id = data.get('session_id')
        
        if not session_id:
            emit('session_analytics', {'success': False, 'error': 'Session ID required'})
            return
        
        analytics = feedback_service.get_session_analytics(session_id)
        
        if analytics:
            emit('session_analytics', {
                'success': True,
                'analytics': analytics
            })
        else:
            emit('session_analytics', {
                'success': False,
                'error': 'Session not found'
            })
        
    except Exception as e:
        print(f"❌ Error getting session analytics: {str(e)}")
        emit('session_analytics', {
            'success': False,
            'error': str(e)
        })

@socketio.on('request_hint')
@authenticated_only
def handle_request_hint(data):
    """Handle hint requests and provide contextual help"""
    try:
        session_id = data.get('session_id')
        current_context = data.get('context', {})
        hint_type = data.get('hint_type', 'general')
        
        # Generate contextual hints based on current state
        hints = {
            'device_placement': [
                "Try placing devices according to the network topology diagram.",
                "Make sure to follow the logical network hierarchy.",
                "Consider the physical constraints and cable lengths."
            ],
            'connection_creation': [
                "Check device compatibility before connecting.",
                "Use the appropriate cable type for the connection.",
                "Verify that both devices have available ports."
            ],
            'cli_command': [
                "Start with basic connectivity tests like 'ping'.",
                "Use 'show' commands to check device status.",
                "Remember to enter configuration mode for changes."
            ],
            'configuration': [
                "Double-check IP addresses and subnet masks.",
                "Ensure routing protocols are configured correctly.",
                "Save your configuration after making changes."
            ],
            'general': [
                "Take your time to analyze the problem step by step.",
                "Use the network diagram as a reference.",
                "Don't hesitate to use troubleshooting commands."
            ]
        }
        
        hint_messages = hints.get(hint_type, hints['general'])
        selected_hint = hint_messages[0]  # Could be randomized or context-aware
        
        # Track hint usage if session exists
        if session_id and feedback_service:
            feedback_service.record_feedback(
                session_id=session_id,
                user_id=current_user.id,
                action_type='hint_request',
                action_data={
                    'hint_type': hint_type,
                    'context': current_context,
                    'hint_provided': selected_hint
                }
            )
        
        emit('hint_provided', {
            'hint': selected_hint,
            'hint_type': hint_type,
            'icon': 'fas fa-lightbulb',
            'timestamp': datetime.utcnow().isoformat()
        })
        
        print(f"💡 Hint provided to {current_user.username}: {hint_type}")
        
    except Exception as e:
        print(f"❌ Error providing hint: {str(e)}")
        emit('hint_error', {'error': str(e)})

@socketio.on('validate_solution')
@authenticated_only
def handle_validate_solution(data):
    """Validate complete solution and provide comprehensive feedback"""
    if not feedback_service:
        emit('solution_validation', {'success': False, 'error': 'Feedback system not available'})
        return
    
    try:
        session_id = data.get('session_id')
        solution_data = data.get('solution', {})
        scenario_requirements = data.get('requirements', {})
        
        if not session_id:
            emit('solution_validation', {'success': False, 'error': 'Session ID required'})
            return
        
        # Validate solution components
        validation_results = {
            'overall_score': 0,
            'component_scores': {},
            'missing_components': [],
            'errors': [],
            'recommendations': []
        }
        
        # Validate devices
        required_devices = scenario_requirements.get('devices', [])
        solution_devices = solution_data.get('devices', [])
        
        device_score = 0
        for req_device in required_devices:
            matching_device = next(
                (d for d in solution_devices if d.get('type') == req_device.get('type')),
                None
            )
            if matching_device:
                device_score += 20
            else:
                validation_results['missing_components'].append(f"Missing {req_device.get('type')} device")
        
        validation_results['component_scores']['devices'] = device_score
        
        # Validate connections
        required_connections = scenario_requirements.get('connections', [])
        solution_connections = solution_data.get('connections', [])
        
        connection_score = 0
        for req_conn in required_connections:
            # Check if connection exists (simplified validation)
            if len(solution_connections) >= len(required_connections):
                connection_score += 15
        
        validation_results['component_scores']['connections'] = connection_score
        
        # Validate configurations
        required_configs = scenario_requirements.get('configurations', {})
        solution_configs = solution_data.get('configurations', {})
        
        config_score = 0
        for device_id, req_config in required_configs.items():
            solution_config = solution_configs.get(device_id, {})
            if solution_config:
                config_score += 25
        
        validation_results['component_scores']['configurations'] = config_score
        
        # Calculate overall score
        validation_results['overall_score'] = sum(validation_results['component_scores'].values())
        
        # Generate recommendations
        if validation_results['overall_score'] < 60:
            validation_results['recommendations'].append("Review the network requirements and topology")
        if device_score < 40:
            validation_results['recommendations'].append("Ensure all required devices are properly placed")
        if connection_score < 30:
            validation_results['recommendations'].append("Check all network connections and cable types")
        if config_score < 50:
            validation_results['recommendations'].append("Verify device configurations and IP settings")
        
        # Record validation feedback
        feedback_service.record_feedback(
            session_id=session_id,
            user_id=current_user.id,
            action_type='solution_validation',
            action_data={
                'solution': solution_data,
                'validation_results': validation_results,
                'overall_score': validation_results['overall_score']
            }
        )
        
        emit('solution_validation', {
            'success': True,
            'validation_results': validation_results,
            'is_complete': validation_results['overall_score'] >= 80,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        print(f"✅ Solution validated for {current_user.username}: {validation_results['overall_score']}%")
        
    except Exception as e:
        print(f"❌ Error validating solution: {str(e)}")
        emit('solution_validation', {
            'success': False,
            'error': str(e)
        })

# Live Leaderboard System Implementation
from sqlalchemy import desc, func

# Store connected users for leaderboard rooms
leaderboard_users = {}

@socketio.on('join_leaderboard')
@authenticated_only
def handle_join_leaderboard(data):
    """Join live leaderboard room and get real-time updates"""
    try:
        user_id = data.get('user_id', current_user.id)
        page = data.get('page', 'leaderboard')
        
        # Join general leaderboard room
        join_room('leaderboard')
        
        # Track user in leaderboard room
        leaderboard_users[current_user.id] = {
            'user_id': current_user.id,
            'username': current_user.username,
            'page': page,
            'joined_at': datetime.utcnow().isoformat()
        }
        
        # Get initial leaderboard data
        initial_data = get_live_leaderboard_data()
        
        # Send initial data to user
        emit('leaderboard_initialized', {
            'overall': initial_data['overall'],
            'categories': initial_data['categories'],
            'recent_achievements': initial_data['recent_achievements'],
            'user_stats': initial_data['user_stats']
        })
        
        # Notify others that user joined leaderboard
        emit('user_joined_leaderboard', {
            'user_id': current_user.id,
            'username': current_user.username,
            'page': page
        }, room='leaderboard', include_self=False)
        
        print(f"✅ User {current_user.username} joined live leaderboard from {page}")
        
    except Exception as e:
        print(f"❌ Error joining leaderboard: {str(e)}")
        emit('leaderboard_error', {'error': str(e)})

@socketio.on('leave_leaderboard')
@authenticated_only
def handle_leave_leaderboard():
    """Leave live leaderboard room"""
    try:
        leave_room('leaderboard')
        
        # Remove user from tracking
        if current_user.id in leaderboard_users:
            del leaderboard_users[current_user.id]
        
        emit('user_left_leaderboard', {
            'user_id': current_user.id,
            'username': current_user.username
        }, room='leaderboard')
        
        print(f"✅ User {current_user.username} left live leaderboard")
        
    except Exception as e:
        print(f"❌ Error leaving leaderboard: {str(e)}")

@socketio.on('get_leaderboard_data')
@authenticated_only
def handle_get_leaderboard_data(data):
    """Get filtered leaderboard data based on category and time period"""
    try:
        category = data.get('category', 'all')
        time_period = data.get('time_period', 'all_time')
        limit = data.get('limit', 20)
        
        filtered_data = get_filtered_leaderboard_data(category, time_period, limit)
        
        emit('leaderboard_data', {
            'category': category,
            'time_period': time_period,
            'entries': filtered_data['entries'],
            'total_count': filtered_data['total_count'],
            'user_rank': filtered_data['user_rank']
        })
        
        print(f"✅ Leaderboard data sent to {current_user.username}: {category} - {time_period}")
        
    except Exception as e:
        print(f"❌ Error getting leaderboard data: {str(e)}")
        emit('leaderboard_error', {'error': str(e)})

@socketio.on('score_achieved')
@authenticated_only
def handle_score_achieved(data):
    """Handle new score achievements and update leaderboard"""
    try:
        score = data.get('score')
        category = data.get('category')
        challenge_type = data.get('challenge_type')
        
        if not score or not category:
            return
        
        # Check if this is a new high score
        is_new_high_score = check_new_high_score(current_user.id, category, score)
        
        # Get updated leaderboard data
        updated_data = get_live_leaderboard_data()
        
        # Broadcast to all leaderboard users
        emit('live_leaderboard_update', {
            'user_id': current_user.id,
            'username': current_user.username,
            'score': score,
            'category': category,
            'challenge_type': challenge_type,
            'is_new_high_score': is_new_high_score,
            'leaderboard_data': updated_data,
            'timestamp': datetime.utcnow().isoformat()
        }, room='leaderboard')
        
        # Handle new high score achievements
        if is_new_high_score:
            emit('new_high_score_achieved', {
                'user_id': current_user.id,
                'username': current_user.username,
                'score': score,
                'category': category,
                'previous_best': get_user_previous_best(current_user.id, category),
                'new_rank': get_user_rank(current_user.id, category)
            }, room='leaderboard')
        
        print(f"✅ Score achievement broadcast: {current_user.username} - {score}% in {category}")
        
    except Exception as e:
        print(f"❌ Error handling score achievement: {str(e)}")

def get_live_leaderboard_data():
    """Get comprehensive live leaderboard data"""
    try:
        # Import Score model
        from user.models.score import Score
        
        # Get overall leaderboard (best scores across all categories)
        overall_query = db.session.query(
            Score.user_id,
            UserModel.username,
            UserModel.profile_img,
            func.max(Score.score).label('best_score'),
            func.max(Score.date_attempted).label('latest_attempt'),
            Score.category
        ).join(UserModel, Score.user_id == UserModel.id)\
         .group_by(Score.user_id, UserModel.username, UserModel.profile_img, Score.category)\
         .subquery()
        
        # Get the absolute best score per user
        overall_leaderboard = db.session.query(
            overall_query.c.user_id,
            overall_query.c.username,
            overall_query.c.profile_img,
            func.max(overall_query.c.best_score).label('score'),
            func.max(overall_query.c.latest_attempt).label('date_attempted'),
            overall_query.c.category
        ).group_by(overall_query.c.user_id, overall_query.c.username, overall_query.c.profile_img, overall_query.c.category)\
         .order_by(desc(func.max(overall_query.c.best_score)))\
         .limit(20).all()
        
        # Get category-specific leaderboards
        categories = ['networking', 'topology', 'troubleshooting', 'crimping', 'riddle', 'collaboration']
        category_leaderboards = {}
        
        for category in categories:
            category_data = db.session.query(
                Score.user_id,
                UserModel.username,
                UserModel.profile_img,
                func.max(Score.score).label('score'),
                func.max(Score.date_attempted).label('date_attempted')
            ).join(UserModel, Score.user_id == UserModel.id)\
             .filter(Score.category == category)\
             .group_by(Score.user_id, UserModel.username, UserModel.profile_img)\
             .order_by(desc(func.max(Score.score)))\
             .limit(10).all()
            
            category_leaderboards[category] = [
                {
                    'user_id': entry.user_id,
                    'username': entry.username,
                    'profile_img': entry.profile_img,
                    'score': entry.score,
                    'date_attempted': entry.date_attempted.isoformat() if entry.date_attempted else None,
                    'category': category
                }
                for entry in category_data
            ]
        
        # Get recent achievements (last 24 hours)
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_achievements = db.session.query(
            Score.user_id,
            UserModel.username,
            UserModel.profile_img,
            Score.score,
            Score.category,
            Score.date_attempted
        ).join(UserModel, Score.user_id == UserModel.id)\
         .filter(Score.date_attempted >= recent_cutoff)\
         .order_by(desc(Score.date_attempted))\
         .limit(10).all()
        
        # Get user statistics
        user_stats = None
        if current_user.is_authenticated:
            user_stats = get_user_leaderboard_stats(current_user.id)
        
        return {
            'overall': [
                {
                    'user_id': entry.user_id,
                    'username': entry.username,
                    'profile_img': entry.profile_img,
                    'score': entry.score,
                    'date_attempted': entry.date_attempted.isoformat() if entry.date_attempted else None,
                    'category': entry.category
                }
                for entry in overall_leaderboard
            ],
            'categories': category_leaderboards,
            'recent_achievements': [
                {
                    'user_id': entry.user_id,
                    'username': entry.username,
                    'profile_img': entry.profile_img,
                    'score': entry.score,
                    'category': entry.category,
                    'date_attempted': entry.date_attempted.isoformat() if entry.date_attempted else None
                }
                for entry in recent_achievements
            ],
            'user_stats': user_stats
        }
        
    except Exception as e:
        print(f"❌ Error getting live leaderboard data: {str(e)}")
        return {
            'overall': [],
            'categories': {},
            'recent_achievements': [],
            'user_stats': None
        }

def get_filtered_leaderboard_data(category='all', time_period='all_time', limit=20):
    """Get filtered leaderboard data based on category and time period"""
    try:
        from user.models.score import Score
        
        # Base query
        query = db.session.query(
            Score.user_id,
            UserModel.username,
            UserModel.profile_img,
            func.max(Score.score).label('score'),
            func.max(Score.date_attempted).label('date_attempted'),
            Score.category
        ).join(UserModel, Score.user_id == UserModel.id)
        
        # Apply category filter
        if category != 'all':
            query = query.filter(Score.category == category)
        
        # Apply time period filter
        if time_period != 'all_time':
            cutoff_date = datetime.utcnow()
            
            if time_period == 'daily':
                cutoff_date = cutoff_date - timedelta(days=1)
            elif time_period == 'weekly':
                cutoff_date = cutoff_date - timedelta(weeks=1)
            elif time_period == 'monthly':
                cutoff_date = cutoff_date - timedelta(days=30)
            
            query = query.filter(Score.date_attempted >= cutoff_date)
        
        # Group and order
        if category == 'all':
            # For overall leaderboard, get best score per user across all categories
            subquery = query.group_by(Score.user_id, UserModel.username, UserModel.profile_img, Score.category).subquery()
            
            final_query = db.session.query(
                subquery.c.user_id,
                subquery.c.username,
                subquery.c.profile_img,
                func.max(subquery.c.score).label('score'),
                func.max(subquery.c.date_attempted).label('date_attempted'),
                subquery.c.category
            ).group_by(subquery.c.user_id, subquery.c.username, subquery.c.profile_img, subquery.c.category)\
             .order_by(desc(func.max(subquery.c.score)))\
             .limit(limit)
            
            results = final_query.all()
        else:
            # For category-specific leaderboard
            results = query.group_by(Score.user_id, UserModel.username, UserModel.profile_img, Score.category)\
                          .order_by(desc(func.max(Score.score)))\
                          .limit(limit).all()
        
        # Get user's rank if authenticated
        user_rank = None
        if current_user.is_authenticated:
            user_rank = get_user_rank(current_user.id, category)
        
        return {
            'entries': [
                {
                    'user_id': entry.user_id,
                    'username': entry.username,
                    'profile_img': entry.profile_img,
                    'score': entry.score,
                    'date_attempted': entry.date_attempted.isoformat() if entry.date_attempted else None,
                    'category': entry.category if hasattr(entry, 'category') else category
                }
                for entry in results
            ],
            'total_count': len(results),
            'user_rank': user_rank
        }
        
    except Exception as e:
        print(f"❌ Error getting filtered leaderboard data: {str(e)}")
        return {
            'entries': [],
            'total_count': 0,
            'user_rank': None
        }

def check_new_high_score(user_id, category, new_score):
    """Check if the new score is a personal best"""
    try:
        from user.models.score import Score
        
        best_score = db.session.query(func.max(Score.score)).filter(
            Score.user_id == user_id,
            Score.category == category
        ).scalar()
        
        return best_score is None or new_score > best_score
        
    except Exception as e:
        print(f"❌ Error checking high score: {str(e)}")
        return False

def get_user_previous_best(user_id, category):
    """Get user's previous best score in a category"""
    try:
        from user.models.score import Score
        
        previous_best = db.session.query(func.max(Score.score)).filter(
            Score.user_id == user_id,
            Score.category == category
        ).scalar()
        
        return previous_best or 0
        
    except Exception as e:
        print(f"❌ Error getting previous best: {str(e)}")
        return 0

def get_user_rank(user_id, category='all'):
    """Get user's current rank in specified category"""
    try:
        from user.models.score import Score
        
        if category == 'all':
            # Get rank across all categories (best overall score)
            user_best_score = db.session.query(func.max(Score.score)).filter(
                Score.user_id == user_id
            ).scalar()
            
            if user_best_score is None:
                return None
            
            better_users = db.session.query(func.count(func.distinct(Score.user_id))).filter(
                Score.score > user_best_score
            ).scalar()
            
            return better_users + 1
        else:
            # Get rank in specific category
            user_best_score = db.session.query(func.max(Score.score)).filter(
                Score.user_id == user_id,
                Score.category == category
            ).scalar()
            
            if user_best_score is None:
                return None
            
            better_users = db.session.query(func.count(func.distinct(Score.user_id))).filter(
                Score.category == category,
                Score.score > user_best_score
            ).scalar()
            
            return better_users + 1
        
    except Exception as e:
        print(f"❌ Error getting user rank: {str(e)}")
        return None

def get_user_leaderboard_stats(user_id):
    """Get comprehensive user statistics for leaderboard"""
    try:
        from user.models.score import Score
        
        # Get user's best scores per category
        category_scores = db.session.query(
            Score.category,
            func.max(Score.score).label('best_score'),
            func.count(Score.id).label('attempt_count')
        ).filter(Score.user_id == user_id)\
         .group_by(Score.category)\
         .all()
        
        # Get overall statistics
        total_attempts = db.session.query(func.count(Score.id)).filter(
            Score.user_id == user_id
        ).scalar()
        
        overall_best = db.session.query(func.max(Score.score)).filter(
            Score.user_id == user_id
        ).scalar()
        
        # Get recent activity
        recent_cutoff = datetime.utcnow() - timedelta(days=7)
        recent_activity = db.session.query(func.count(Score.id)).filter(
            Score.user_id == user_id,
            Score.date_attempted >= recent_cutoff
        ).scalar()
        
        return {
            'category_scores': {
                entry.category: {
                    'best_score': entry.best_score,
                    'attempt_count': entry.attempt_count,
                    'rank': get_user_rank(user_id, entry.category)
                }
                for entry in category_scores
            },
            'overall_stats': {
                'total_attempts': total_attempts,
                'overall_best': overall_best,
                'overall_rank': get_user_rank(user_id, 'all'),
                'recent_activity': recent_activity
            }
        }
        
    except Exception as e:
        print(f"❌ Error getting user stats: {str(e)}")
        return None

# ===== SCENARIO TIMER SYSTEM =====
try:
    from admin.models.scenario_timer import ScenarioTimer
    print("✅ Scenario timer model imported successfully")
except ImportError as e:
    print(f"⚠️ Warning: Could not import scenario timer model: {e}")
    ScenarioTimer = None

# Timer Management Events
@socketio.on('start_scenario_timer')
@authenticated_only
def handle_start_scenario_timer(data):
    """Start a new scenario timer"""
    if not ScenarioTimer:
        emit('timer_error', {'error': 'Timer system not available'})
        return
    
    try:
        scenario_id = data.get('scenario_id')
        scenario_type = data.get('scenario_type', 'troubleshooting')
        difficulty = data.get('difficulty', 'medium')
        time_limit_minutes = data.get('time_limit_minutes')
        lobby_id = data.get('lobby_id')
        is_collaborative = bool(lobby_id)
        
        if not scenario_id:
            emit('timer_error', {'error': 'Scenario ID required'})
            return
        
        # Check for existing active timer
        existing_timer = ScenarioTimer.get_active_timer(current_user.id, scenario_id)
        if existing_timer:
            emit('timer_already_active', {
                'timer': existing_timer.to_dict(),
                'message': 'Timer already active for this scenario'
            })
            return
        
        # Create new timer
        timer = ScenarioTimer.create_timer(
            user_id=current_user.id,
            scenario_id=scenario_id,
            scenario_type=scenario_type,
            difficulty=difficulty,
            time_limit_minutes=time_limit_minutes,
            lobby_id=lobby_id,
            is_collaborative=is_collaborative
        )
        
        db.session.add(timer)
        db.session.commit()
        
        # Join timer room
        timer_room = f"timer_{timer.id}"
        join_room(timer_room)
        
        # If collaborative, sync with lobby participants
        if is_collaborative and lobby_id:
            lobby_room = f"troubleshooting_lobby_{lobby_id}"
            emit('collaborative_timer_started', {
                'timer': timer.to_dict(),
                'started_by': current_user.username
            }, room=lobby_room, include_self=False)
        
        # Send timer started confirmation
        emit('timer_started', {
            'success': True,
            'timer': timer.to_dict(),
            'room': timer_room
        })
        
        print(f"✅ Timer started for {current_user.username}: {scenario_id} ({difficulty})")
        
    except Exception as e:
        print(f"❌ Error starting timer: {str(e)}")
        emit('timer_error', {'error': str(e)})

@socketio.on('get_timer_status')
@authenticated_only
def handle_get_timer_status(data):
    """Get current timer status"""
    if not ScenarioTimer:
        emit('timer_error', {'error': 'Timer system not available'})
        return
    
    try:
        scenario_id = data.get('scenario_id')
        timer_id = data.get('timer_id')
        
        timer = None
        if timer_id:
            timer = ScenarioTimer.query.get(timer_id)
        elif scenario_id:
            timer = ScenarioTimer.get_active_timer(current_user.id, scenario_id)
        else:
            timer = ScenarioTimer.get_active_timer(current_user.id)
        
        if timer:
            emit('timer_status', {
                'success': True,
                'timer': timer.to_dict(),
                'remaining_seconds': timer.get_current_remaining_seconds()
            })
        else:
            emit('timer_status', {
                'success': False,
                'message': 'No active timer found'
            })
            
    except Exception as e:
        print(f"❌ Error getting timer status: {str(e)}")
        emit('timer_error', {'error': str(e)})

@socketio.on('pause_timer')
@authenticated_only
def handle_pause_timer(data):
    """Pause an active timer"""
    if not ScenarioTimer:
        emit('timer_error', {'error': 'Timer system not available'})
        return
    
    try:
        timer_id = data.get('timer_id')
        reason = data.get('reason', 'User paused')
        
        timer = ScenarioTimer.query.get(timer_id)
        if not timer or timer.user_id != current_user.id:
            emit('timer_error', {'error': 'Timer not found or unauthorized'})
            return
        
        if timer.is_paused:
            emit('timer_error', {'error': 'Timer is already paused'})
            return
        
        # Update timer state
        timer.is_paused = True
        timer.pause_time = datetime.utcnow()
        timer.remaining_seconds = timer.get_current_remaining_seconds()
        timer.add_pause_event('pause', reason)
        
        db.session.commit()
        
        # Notify participants if collaborative
        if timer.is_collaborative and timer.lobby_id:
            lobby_room = f"troubleshooting_lobby_{timer.lobby_id}"
            emit('timer_paused', {
                'timer_id': timer.id,
                'paused_by': current_user.username,
                'reason': reason,
                'remaining_seconds': timer.remaining_seconds
            }, room=lobby_room)
        
        emit('timer_paused_success', {
            'timer': timer.to_dict(),
            'message': 'Timer paused successfully'
        })
        
        print(f"⏸️ Timer paused by {current_user.username}: {timer.scenario_id}")
        
    except Exception as e:
        print(f"❌ Error pausing timer: {str(e)}")
        emit('timer_error', {'error': str(e)})

@socketio.on('resume_timer')
@authenticated_only
def handle_resume_timer(data):
    """Resume a paused timer"""
    if not ScenarioTimer:
        emit('timer_error', {'error': 'Timer system not available'})
        return
    
    try:
        timer_id = data.get('timer_id')
        
        timer = ScenarioTimer.query.get(timer_id)
        if not timer or timer.user_id != current_user.id:
            emit('timer_error', {'error': 'Timer not found or unauthorized'})
            return
        
        if not timer.is_paused:
            emit('timer_error', {'error': 'Timer is not paused'})
            return
        
        # Update timer state
        timer.is_paused = False
        timer.resume_time = datetime.utcnow()
        timer.add_pause_event('resume')
        
        db.session.commit()
        
        # Notify participants if collaborative
        if timer.is_collaborative and timer.lobby_id:
            lobby_room = f"troubleshooting_lobby_{timer.lobby_id}"
            emit('timer_resumed', {
                'timer_id': timer.id,
                'resumed_by': current_user.username,
                'remaining_seconds': timer.get_current_remaining_seconds()
            }, room=lobby_room)
        
        emit('timer_resumed_success', {
            'timer': timer.to_dict(),
            'message': 'Timer resumed successfully'
        })
        
        print(f"▶️ Timer resumed by {current_user.username}: {timer.scenario_id}")
        
    except Exception as e:
        print(f"❌ Error resuming timer: {str(e)}")
        emit('timer_error', {'error': str(e)})

@socketio.on('extend_timer')
@authenticated_only
def handle_extend_timer(data):
    """Extend timer duration (admin only or emergency situations)"""
    if not ScenarioTimer:
        emit('timer_error', {'error': 'Timer system not available'})
        return
    
    try:
        timer_id = data.get('timer_id')
        additional_minutes = data.get('additional_minutes', 5)
        reason = data.get('reason', 'Emergency extension')
        
        # Check if user has permission to extend (timer owner or admin)
        timer = ScenarioTimer.query.get(timer_id)
        if not timer:
            emit('timer_error', {'error': 'Timer not found'})
            return
        
        can_extend = (timer.user_id == current_user.id or 
                     getattr(current_user, 'is_admin', False) or
                     hasattr(current_user, '__tablename__') and current_user.__tablename__ == 'admins')
        
        if not can_extend:
            emit('timer_error', {'error': 'Unauthorized to extend timer'})
            return
        
        # Add extension
        additional_seconds = additional_minutes * 60
        timer.add_timer_extension(
            additional_seconds=additional_seconds,
            reason=reason,
            granted_by=current_user.username
        )
        
        db.session.commit()
        
        # Notify all participants
        timer_room = f"timer_{timer.id}"
        emit('timer_extended', {
            'timer': timer.to_dict(),
            'additional_minutes': additional_minutes,
            'reason': reason,
            'extended_by': current_user.username
        }, room=timer_room)
        
        # Notify lobby if collaborative
        if timer.is_collaborative and timer.lobby_id:
            lobby_room = f"troubleshooting_lobby_{timer.lobby_id}"
            emit('collaborative_timer_extended', {
                'timer_id': timer.id,
                'additional_minutes': additional_minutes,
                'reason': reason,
                'extended_by': current_user.username
            }, room=lobby_room)
        
        print(f"⏰ Timer extended by {current_user.username}: +{additional_minutes} minutes")
        
    except Exception as e:
        print(f"❌ Error extending timer: {str(e)}")
        emit('timer_error', {'error': str(e)})

@socketio.on('complete_scenario')
@authenticated_only
def handle_complete_scenario(data):
    """Mark scenario as completed and stop timer"""
    if not ScenarioTimer:
        emit('timer_error', {'error': 'Timer system not available'})
        return
    
    try:
        timer_id = data.get('timer_id')
        final_score = data.get('final_score', 0)
        completion_percentage = data.get('completion_percentage', 100)
        solution_data = data.get('solution_data', {})
        
        timer = ScenarioTimer.query.get(timer_id)
        if not timer or timer.user_id != current_user.id:
            emit('timer_error', {'error': 'Timer not found or unauthorized'})
            return
        
        # Complete the timer
        timer.is_completed = True
        timer.is_active = False
        timer.end_time = datetime.utcnow()
        timer.elapsed_seconds = int((timer.end_time - timer.start_time).total_seconds())
        timer.final_score = final_score
        timer.completion_percentage = completion_percentage
        
        # Calculate time bonus
        remaining = timer.get_current_remaining_seconds()
        if remaining > 0:
            # Give bonus based on time remaining (up to 20% of final score)
            time_bonus_percentage = (remaining / timer.time_limit_seconds) * 0.2
            timer.time_bonus = int(final_score * time_bonus_percentage)
        
        # Calculate performance metrics
        timer.time_efficiency = timer.calculate_time_efficiency(completion_percentage)
        timer.pressure_score = timer.calculate_pressure_score()
        
        db.session.commit()
        
        # Notify participants if collaborative
        if timer.is_collaborative and timer.lobby_id:
            lobby_room = f"troubleshooting_lobby_{timer.lobby_id}"
            emit('scenario_completed_by_participant', {
                'timer_id': timer.id,
                'completed_by': current_user.username,
                'final_score': final_score,
                'completion_time': timer.elapsed_seconds,
                'time_bonus': timer.time_bonus
            }, room=lobby_room, include_self=False)
        
        # Send completion confirmation
        emit('scenario_completed_success', {
            'timer': timer.to_dict(),
            'performance_summary': {
                'final_score': final_score,
                'time_bonus': timer.time_bonus,
                'total_score': final_score + timer.time_bonus,
                'time_efficiency': timer.time_efficiency,
                'pressure_score': timer.pressure_score,
                'completion_time': timer.elapsed_seconds
            }
        })
        
        print(f"✅ Scenario completed by {current_user.username}: {timer.scenario_id} - Score: {final_score}")
        
    except Exception as e:
        print(f"❌ Error completing scenario: {str(e)}")
        emit('timer_error', {'error': str(e)})

@socketio.on('timer_warning_acknowledged')
@authenticated_only
def handle_timer_warning_acknowledged(data):
    """Acknowledge timer warning"""
    try:
        timer_id = data.get('timer_id')
        warning_type = data.get('warning_type')
        remaining_seconds = data.get('remaining_seconds')
        
        timer = ScenarioTimer.query.get(timer_id)
        if timer and timer.user_id == current_user.id:
            timer.add_warning_event(warning_type, remaining_seconds)
            db.session.commit()
        
        print(f"⚠️ Warning acknowledged by {current_user.username}: {warning_type}")
        
    except Exception as e:
        print(f"❌ Error acknowledging warning: {str(e)}")

@socketio.on('get_timer_analytics')
@authenticated_only
def handle_get_timer_analytics(data):
    """Get timer analytics for user"""
    if not ScenarioTimer:
        emit('timer_analytics', {'success': False, 'error': 'Timer system not available'})
        return
    
    try:
        scenario_type = data.get('scenario_type')
        time_period = data.get('time_period', 'all_time')
        
        # Get user timer statistics
        stats = ScenarioTimer.get_user_timer_stats(current_user.id, scenario_type)
        
        # Get recent timers
        query = ScenarioTimer.query.filter_by(
            user_id=current_user.id,
            is_completed=True
        ).order_by(ScenarioTimer.created_at.desc())
        
        if scenario_type:
            query = query.filter_by(scenario_type=scenario_type)
        
        # Apply time filter
        if time_period != 'all_time':
            cutoff = datetime.utcnow()
            if time_period == 'weekly':
                cutoff -= timedelta(weeks=1)
            elif time_period == 'monthly':
                cutoff -= timedelta(days=30)
            else:  # daily
                cutoff -= timedelta(days=1)
            
            query = query.filter(ScenarioTimer.created_at >= cutoff)
        
        recent_timers = query.limit(10).all()
        
        emit('timer_analytics', {
            'success': True,
            'stats': stats,
            'recent_timers': [timer.to_dict() for timer in recent_timers],
            'time_period': time_period
        })
        
    except Exception as e:
        print(f"❌ Error getting timer analytics: {str(e)}")
        emit('timer_analytics', {'success': False, 'error': str(e)})

# Auto-expiration handling
@socketio.on('check_timer_expiration')
@authenticated_only
def handle_check_timer_expiration(data):
    """Check if timer has expired and handle auto-submission"""
    if not ScenarioTimer:
        return
    
    try:
        timer_id = data.get('timer_id')
        
        timer = ScenarioTimer.query.get(timer_id)
        if not timer or timer.user_id != current_user.id:
            return
        
        remaining = timer.get_current_remaining_seconds()
        
        if remaining <= 0 and not timer.is_expired:
            # Timer has expired
            timer.is_expired = True
            timer.is_active = False
            timer.auto_submitted = True
            timer.end_time = datetime.utcnow()
            timer.elapsed_seconds = timer.time_limit_seconds
            
            # Get current progress for auto-submission
            current_progress = data.get('current_progress', {})
            timer.completion_percentage = current_progress.get('completion_percentage', 0)
            timer.final_score = current_progress.get('current_score', 0)
            
            # No time bonus for expired timers
            timer.time_bonus = 0
            timer.time_efficiency = timer.calculate_time_efficiency()
            timer.pressure_score = 0  # No pressure score for expired timers
            
            db.session.commit()
            
            # Notify user of expiration and auto-submission
            emit('timer_expired', {
                'timer': timer.to_dict(),
                'auto_submitted': True,
                'final_score': timer.final_score,
                'message': 'Time expired - scenario auto-submitted'
            })
            
            # Notify collaborative participants
            if timer.is_collaborative and timer.lobby_id:
                lobby_room = f"troubleshooting_lobby_{timer.lobby_id}"
                emit('participant_timer_expired', {
                    'user_id': current_user.id,
                    'username': current_user.username,
                    'timer_id': timer.id,
                    'auto_submitted': True
                }, room=lobby_room, include_self=False)
            
            print(f"⏰❌ Timer expired and auto-submitted for {current_user.username}: {timer.scenario_id}")
        
        elif remaining <= 300 and remaining > 280:  # 5 minute warning
            timer.add_warning_event('5_minute_warning', remaining)
            db.session.commit()
            
            emit('timer_warning', {
                'type': '5_minute_warning',
                'remaining_seconds': remaining,
                'message': timer.get_warning_message('5_minute_warning', remaining),
                'urgency': 'medium'
            })
            
        elif remaining <= 60 and remaining > 55:  # 1 minute warning
            timer.add_warning_event('1_minute_warning', remaining)
            db.session.commit()
            
            emit('timer_warning', {
                'type': '1_minute_warning',
                'remaining_seconds': remaining,
                'message': timer.get_warning_message('1_minute_warning', remaining),
                'urgency': 'high'
            })
            
        elif remaining <= 30 and remaining > 25:  # 30 second warning
            timer.add_warning_event('30_second_warning', remaining)
            db.session.commit()
            
            emit('timer_warning', {
                'type': '30_second_warning',
                'remaining_seconds': remaining,
                'message': timer.get_warning_message('30_second_warning', remaining),
                'urgency': 'critical'
            })
        
        # Send current status
        emit('timer_status_update', {
            'timer_id': timer.id,
            'remaining_seconds': remaining,
            'is_expired': timer.is_expired,
            'auto_submitted': timer.auto_submitted
        })
        
    except Exception as e:
        print(f"❌ Error checking timer expiration: {str(e)}")

# Collaborative timer synchronization
@socketio.on('sync_collaborative_timer')
@authenticated_only
def handle_sync_collaborative_timer(data):
    """Synchronize timer across collaborative session participants"""
    if not ScenarioTimer:
        return
    
    try:
        lobby_id = data.get('lobby_id')
        timer_action = data.get('action')  # 'start', 'pause', 'resume', 'complete'
        timer_data = data.get('timer_data', {})
        
        if not lobby_id:
            return
        
        lobby_room = f"troubleshooting_lobby_{lobby_id}"
        
        # Broadcast timer sync to all participants
        emit('timer_sync_update', {
            'action': timer_action,
            'timer_data': timer_data,
            'sync_by': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, room=lobby_room, include_self=False)
        
        print(f"🔄 Timer sync broadcast by {current_user.username}: {timer_action}")
        
    except Exception as e:
        print(f"❌ Error syncing collaborative timer: {str(e)}")

print("✅ Socket events module loaded successfully with live leaderboard and timer systems")
