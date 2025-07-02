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
            'max_participants': data.get('max_participants', 6),
            'is_private': data.get('is_private', False),
            'password': data.get('password')
        }
        
        lobby = lobby_manager.create_lobby(
            creator_id=str(current_user.id),
            creator_name=current_user.username,
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
        password = data.get('password')
        
        if not lobby_id:
            emit('lobby_joined', {'success': False, 'error': 'Lobby ID required'})
            return
        
        result = lobby_manager.join_lobby(
            lobby_id=lobby_id,
            user_id=str(current_user.id),
            user_info={'username': current_user.username},
            password=password
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
            emit('participant_joined', {
                'user_id': str(current_user.id),
                'username': current_user.username,
                'participant_data': lobby.participants[str(current_user.id)]
            }, room=room_name, include_self=False)
            
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
            'color': lobby.participants[str(current_user.id)]['color']
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

@socketio.on('send_lobby_chat')
@authenticated_only
def handle_lobby_chat(data):
    """Handle chat messages in lobby"""
    if not lobby_manager:
        return
    
    try:
        lobby = lobby_manager.get_user_lobby(str(current_user.id))
        if not lobby:
            return
        
        message = data.get('message', '').strip()
        message_type = data.get('type', 'text')
        
        if not message:
            return
        
        chat_message = lobby.add_chat_message(str(current_user.id), message, message_type)
        lobby_manager.update_participant_activity(str(current_user.id))
        
        # Broadcast message to all participants
        room_name = f"troubleshooting_lobby_{lobby.id}"
        emit('lobby_chat_message', chat_message, room=room_name)
        
    except Exception as e:
        print(f"❌ Error sending chat message: {str(e)}")

@socketio.on('update_troubleshooting_progress')
@authenticated_only
def handle_troubleshooting_progress_update(data):
    """Handle troubleshooting progress updates"""
    if not lobby_manager:
        return
    
    try:
        lobby = lobby_manager.get_user_lobby(str(current_user.id))
        if not lobby:
            return
        
        progress_data = {
            'step': data.get('step'),
            'completed_steps': data.get('completed_steps', []),
            'issues_found': data.get('issues_found', []),
            'solutions_applied': data.get('solutions_applied', [])
        }
        
        lobby.update_progress(str(current_user.id), progress_data)
        lobby_manager.update_participant_activity(str(current_user.id))
        
        # Broadcast progress to all participants
        room_name = f"troubleshooting_lobby_{lobby.id}"
        emit('troubleshooting_progress_updated', {
            'user_progress': lobby.progress['team_progress'][str(current_user.id)],
            'overall_progress': lobby.progress['overall'],
            'team_progress': lobby.progress['team_progress']
        }, room=room_name)
        
        # Add progress message to chat
        step_name = progress_data.get('step', 'Unknown step')
        lobby.add_chat_message('system', 
            f"{current_user.username} completed step: {step_name}", 
            'progress')
        
        emit('lobby_chat_message', lobby.chat_history[-1], room=room_name)
        
    except Exception as e:
        print(f"❌ Error updating troubleshooting progress: {str(e)}")

@socketio.on('request_lobby_sync')
@authenticated_only
def handle_request_lobby_sync(data=None):
    """Request full lobby state synchronization"""
    if not lobby_manager:
        return
    
    try:
        lobby = lobby_manager.get_user_lobby(str(current_user.id))
        if not lobby:
            return
        
        lobby_manager.update_participant_activity(str(current_user.id))
        
        # Send complete lobby state
        emit('lobby_state_sync', {
            'lobby': lobby.to_dict(),
            'network_state': lobby.network_state,
            'participants': lobby.participants,
            'chat_history': lobby.chat_history[-20:],  # Last 20 messages
            'progress': lobby.progress
        })
        
    except Exception as e:
        print(f"❌ Error syncing lobby state: {str(e)}")

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
