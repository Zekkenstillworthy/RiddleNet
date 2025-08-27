from socket_manager import socketio, authenticated_only, admin_only
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from __init__ import db
from datetime import datetime, timedelta
from typing import List
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

# Real-time notification system
def emit_assignment_notification(user_id: int, notification_data: dict):
    """Emit assignment notification to a specific user"""
    try:
        socketio.emit('assignment_notification', notification_data, room=f'user_{user_id}')
        print(f"📢 Sent assignment notification to user {user_id}: {notification_data['title']}")
    except Exception as e:
        print(f"❌ Error sending assignment notification: {str(e)}")

def emit_simulation_update(class_id: int, update_data: dict):
    """Emit simulation update to all users in a class"""
    try:
        socketio.emit('simulation_update', update_data, room=f'class_{class_id}')
        print(f"📢 Sent simulation update to class {class_id}")
    except Exception as e:
        print(f"❌ Error sending simulation update: {str(e)}")

def emit_grade_notification(user_id: int, grade_data: dict):
    """Emit grade notification to a specific user"""
    try:
        socketio.emit('grade_notification', grade_data, room=f'user_{user_id}')
        print(f"📢 Sent grade notification to user {user_id}")
    except Exception as e:
        print(f"❌ Error sending grade notification: {str(e)}")

# ===== WEEK 2 ENHANCEMENT: REAL-TIME CONTENT UPDATES =====

def emit_new_simulation_available(simulation_id: int, category: str, class_ids: List[int] = None):
    """Notify users when new simulation is available"""
    try:
        from admin.models.simulation import Simulation
        from admin.models.class_model import Class
        from admin.services.enhanced_class_template_generator import EnhancedClassTemplateGenerator
        
        simulation = Simulation.query.get(simulation_id)
        if not simulation:
            return
            
        notification_data = {
            'type': 'new_simulation',
            'simulation_id': simulation_id,
            'title': simulation.title,
            'category': category,
            'message': f'🎉 New simulation available: {simulation.title}',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Find affected classes
        if class_ids:
            affected_classes = Class.query.filter(Class.id.in_(class_ids)).all()
        else:
            affected_classes = Class.query.filter(
                Class.name.ilike(f'%{category}%')
            ).all()
        
        generator = EnhancedClassTemplateGenerator()
        
        for class_obj in affected_classes:
            # Regenerate class template with new simulation
            try:
                generator.regenerate_class_resources(class_obj.id)
                print(f"✅ Regenerated template for class {class_obj.name}")
            except Exception as e:
                print(f"❌ Failed to regenerate template for class {class_obj.name}: {e}")
            
            # Notify users in this class
            class_notification = notification_data.copy()
            class_notification['class_id'] = class_obj.id
            class_notification['class_name'] = class_obj.name
            
            socketio.emit('new_simulation_available', class_notification, room=f'class_{class_obj.id}')
            print(f"📢 Notified class {class_obj.id} about new simulation {simulation_id}")
        
        # Broadcast to category room for users not in specific classes
        socketio.emit('new_simulation_available', notification_data, room=f'category_{category}')
        
    except Exception as e:
        print(f"❌ Error sending new simulation notification: {str(e)}")

def emit_new_learning_path_available(path_id: int, category: str, class_ids: List[int] = None):
    """Notify users when new learning path is available - DEPRECATED"""
    try:
        # Learning Path feature has been removed from RiddleNet
        # This function now returns without doing anything
        print(f"⚠️ Learning Path feature removed - ignoring emit for path_id: {path_id}")
        return
        
    except Exception as e:
        print(f"❌ Error in deprecated learning path notification: {e}")
        return
        
        for class_obj in affected_classes:
            # Regenerate class template with new learning path
            try:
                generator.regenerate_class_resources(class_obj.id)
                print(f"✅ Regenerated template for class {class_obj.name}")
            except Exception as e:
                print(f"❌ Failed to regenerate template for class {class_obj.name}: {e}")
            
            # Notify users in this class
            class_notification = notification_data.copy()
            class_notification['class_id'] = class_obj.id
            class_notification['class_name'] = class_obj.name
            
            socketio.emit('new_learning_path_available', class_notification, room=f'class_{class_obj.id}')
            print(f"📢 Notified class {class_obj.id} about new learning path {path_id}")
        
        # Broadcast to category room
        socketio.emit('new_learning_path_available', notification_data, room=f'category_{category}')
        
    except Exception as e:
        print(f"❌ Error sending new learning path notification: {str(e)}")

def emit_assignment_created(assignment_id: int, class_id: int, assignment_type: str):
    """Notify users when new assignment is created"""
    try:
        from admin.models.simulation_assignment import SimulationAssignment
        from admin.models.simulation import Simulation
        
        assignment = SimulationAssignment.query.get(assignment_id)
        if not assignment:
            return
            
        simulation = Simulation.query.get(assignment.simulation_id)
        
        notification_data = {
            'type': 'new_assignment',
            'assignment_id': assignment_id,
            'assignment_title': assignment.title,
            'simulation_title': simulation.title if simulation else 'Unknown',
            'assignment_type': assignment_type,
            'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
            'class_id': class_id,
            'message': f'📝 New assignment: {assignment.title}',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Notify all users in the class
        socketio.emit('new_assignment_created', notification_data, room=f'class_{class_id}')
        print(f"📢 Notified class {class_id} about new assignment {assignment_id}")
        
    except Exception as e:
        print(f"❌ Error sending assignment creation notification: {str(e)}")

# WebSocket Event Handlers for Week 2 Features
@socketio.on('join_category_room')
@authenticated_only  
def handle_join_category_room(data):
    """Join category-specific room for content updates"""
    if current_user.is_authenticated:
        category = data.get('category')
        if category:
            room = f'category_{category}'
            join_room(room)
            emit('joined_room', {'room': room, 'type': 'category', 'category': category})
            print(f"📂 User {current_user.id} joined category room {room}")

@socketio.on('simulation_created')
def handle_simulation_created(data):
    """Handle notification when admin creates new simulation"""
    simulation_id = data.get('simulation_id')
    category = data.get('category')
    class_ids = data.get('class_ids')
    
    if simulation_id and category:
        emit_new_simulation_available(simulation_id, category, class_ids)

@socketio.on('learning_path_created')
def handle_learning_path_created(data):
    """Handle notification when admin creates new learning path"""
    path_id = data.get('path_id')
    category = data.get('category')
    class_ids = data.get('class_ids')
    
    if path_id and category:
        emit_new_learning_path_available(path_id, category, class_ids)

@socketio.on('assignment_created')
def handle_assignment_created(data):
    """Handle notification when admin creates new assignment"""
    assignment_id = data.get('assignment_id')
    class_id = data.get('class_id')
    assignment_type = data.get('assignment_type', 'class')
    
    if assignment_id and class_id:
        emit_assignment_created(assignment_id, class_id, assignment_type)

# User room management
@socketio.on('join_user_room')
@authenticated_only
def handle_join_user_room():
    """Join user-specific room for notifications"""
    if current_user.is_authenticated:
        room = f'user_{current_user.id}'
        join_room(room)
        emit('joined_room', {'room': room, 'type': 'user'})
        print(f"👤 User {current_user.id} joined room {room}")

@socketio.on('join_class_room')
@authenticated_only
def handle_join_class_room(data):
    """Join class-specific room for updates"""
    if current_user.is_authenticated:
        class_id = data.get('class_id')
        if class_id:
            room = f'class_{class_id}'
            join_room(room)
            emit('joined_room', {'room': room, 'type': 'class', 'class_id': class_id})
            print(f"🏫 User {current_user.id} joined class room {room}")

@socketio.on('leave_class_room')
@authenticated_only
def handle_leave_class_room(data):
    """Leave class-specific room"""
    if current_user.is_authenticated:
        class_id = data.get('class_id')
        if class_id:
            room = f'class_{class_id}'
            leave_room(room)
            emit('left_room', {'room': room, 'type': 'class', 'class_id': class_id})
            print(f"🏫 User {current_user.id} left class room {room}")

# Assignment-related events
@socketio.on('assignment_started')
@authenticated_only
def handle_assignment_started(data):
    """Handle when a user starts an assignment"""
    if current_user.is_authenticated:
        assignment_id = data.get('assignment_id')
        attempt_id = data.get('attempt_id')
        
        # Emit to class room that someone started the assignment
        if 'class_id' in data:
            update_data = {
                'type': 'assignment_started',
                'assignment_id': assignment_id,
                'attempt_id': attempt_id,
                'user_id': current_user.id,
                'username': getattr(current_user, 'username', 'Unknown'),
                'timestamp': datetime.utcnow().isoformat()
            }
            emit_simulation_update(data['class_id'], update_data)

@socketio.on('assignment_completed')
@authenticated_only
def handle_assignment_completed(data):
    """Handle when a user completes an assignment"""
    if current_user.is_authenticated:
        assignment_id = data.get('assignment_id')
        attempt_id = data.get('attempt_id')
        score = data.get('score', 0)
        
        # Emit grade notification to user
        grade_data = {
            'assignment_id': assignment_id,
            'attempt_id': attempt_id,
            'score': score,
            'completed_at': datetime.utcnow().isoformat(),
            'message': f"Assignment completed! Score: {score}%"
        }
        emit_grade_notification(current_user.id, grade_data)
        
        # Emit to class room that someone completed the assignment
        if 'class_id' in data:
            update_data = {
                'type': 'assignment_completed',
                'assignment_id': assignment_id,
                'attempt_id': attempt_id,
                'user_id': current_user.id,
                'username': getattr(current_user, 'username', 'Unknown'),
                'score': score,
                'timestamp': datetime.utcnow().isoformat()
            }
            emit_simulation_update(data['class_id'], update_data)

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
        
        # ===== ADMIN MONITORING INTEGRATION =====
        # Notify admin collaboration monitoring of new session
        emit('collaboration_started', {
            'id': lobby.id,
            'activity_name': lobby_config['name'],
            'participants': [current_user.username],
            'status': 'active',
            'duration': '0m',
            'type': 'troubleshooting',
            'scenario': lobby_config.get('scenario_type', 'Unknown'),
            'created_at': datetime.utcnow().isoformat()
        }, room='admin_collaboration_monitoring')
        
        print(f"✅ User {current_user.username} created lobby {lobby.id}")
        print(f"📊 Notified admin monitoring of new collaboration session")
        
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
            
            # ===== ADMIN MONITORING INTEGRATION =====
            # Notify admin monitoring of user joining
            emit('collaboration_updated', {
                'id': lobby.id,
                'activity_name': lobby.name,
                'participants': list(lobby.participants.keys()),
                'participant_names': [lobby.participants[pid].get('username', 'Unknown') for pid in lobby.participants.keys()],
                'status': 'active',
                'type': 'troubleshooting',
                'action': 'participant_joined',
                'new_participant': current_user.username
            }, room='admin_collaboration_monitoring')
            
            print(f"✅ User {current_user.username} joined lobby {lobby.id}")
            print(f"📊 Notified admin monitoring of participant join")
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
            
            # ===== ADMIN MONITORING INTEGRATION =====
            # Check if lobby is now empty and notify admin monitoring
            updated_lobby = lobby_manager.get_lobby(lobby.id)
            if updated_lobby and len(updated_lobby.participants) == 0:
                # Lobby is now empty - mark as ended
                emit('collaboration_ended', {
                    'id': lobby.id,
                    'activity_name': lobby.name,
                    'reason': 'all_participants_left',
                    'duration': lobby.get_duration_string()
                }, room='admin_collaboration_monitoring')
                print(f"📊 Notified admin monitoring: lobby {lobby.id} ended (empty)")
            else:
                # Lobby still has participants - update participant list
                if updated_lobby:
                    emit('collaboration_updated', {
                        'id': lobby.id,
                        'activity_name': lobby.name,
                        'participants': list(updated_lobby.participants.keys()),
                        'participant_names': [updated_lobby.participants[pid].get('username', 'Unknown') for pid in updated_lobby.participants.keys()],
                        'status': 'active',
                        'type': 'troubleshooting',
                        'action': 'participant_left',
                        'left_participant': current_user.username
                    }, room='admin_collaboration_monitoring')
                    print(f"📊 Notified admin monitoring of participant leave")
            
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

# ===== ENHANCED ADMIN WEBSOCKET EVENTS =====

@socketio.on('join_admin_room')
@admin_only
def handle_join_admin_room(data=None):
    """Join admin room for real-time admin updates"""
    try:
        join_room('admin_room')
        emit('joined_admin_room', {'success': True, 'message': 'Connected to admin updates'})
        print(f"👑 Admin {current_user.username} joined admin room")
        
        # Send current admin stats on join
        emit_admin_dashboard_stats()
        
    except Exception as e:
        print(f"❌ Error joining admin room: {str(e)}")
        emit('admin_room_error', {'error': str(e)})

@socketio.on('join_admin_dashboard')
@admin_only
def handle_join_admin_dashboard(data=None):
    """Join admin dashboard room for real-time dashboard updates"""
    try:
        join_room('admin_dashboard')
        emit('joined_admin_dashboard', {'success': True})
        print(f"📊 Admin {current_user.username} joined dashboard room")
        
        # Send initial dashboard data
        emit_admin_dashboard_stats()
        emit_recent_admin_activity()
        
    except Exception as e:
        print(f"❌ Error joining admin dashboard: {str(e)}")
        emit('admin_dashboard_error', {'error': str(e)})

@socketio.on('join_user_management')
@admin_only
def handle_join_user_management(data=None):
    """Join user management room for real-time user activity updates"""
    try:
        join_room('user_management')
        emit('joined_user_management', {'success': True})
        print(f"👥 Admin {current_user.username} joined user management room")
        
        # Send current user stats
        emit_user_management_stats()
        
    except Exception as e:
        print(f"❌ Error joining user management: {str(e)}")
        emit('user_management_error', {'error': str(e)})

@socketio.on('join_notification_center')
@admin_only
def handle_join_notification_center(data=None):
    """Join notification center room for real-time notification management"""
    try:
        join_room('notification_center')
        emit('joined_notification_center', {'success': True})
        print(f"🔔 Admin {current_user.username} joined notification center room")
        
        # Send current notification stats
        emit_notification_stats()
        
    except Exception as e:
        print(f"❌ Error joining notification center: {str(e)}")
        emit('notification_center_error', {'error': str(e)})

@socketio.on('join_analytics_room')
@admin_only
def handle_join_analytics_room(data=None):
    """Join analytics room for real-time analytics updates"""
    try:
        join_room('analytics_room')
        emit('joined_analytics_room', {'success': True})
        print(f"📈 Admin {current_user.username} joined analytics room")
        
        # Send current analytics data
        emit_analytics_data()
        
    except Exception as e:
        print(f"❌ Error joining analytics room: {str(e)}")
        emit('analytics_room_error', {'error': str(e)})

@socketio.on('admin_presence')
@admin_only
def handle_admin_presence(data):
    """Update admin presence information"""
    try:
        page = data.get('page', 'unknown')
        timestamp = data.get('timestamp', datetime.utcnow().timestamp() * 1000)
        user_agent = data.get('user_agent', 'Unknown')
        
        # Store admin presence info (could be stored in cache/db if needed)
        presence_data = {
            'admin_id': current_user.id,
            'admin_name': current_user.username,
            'page': page,
            'timestamp': timestamp,
            'user_agent': user_agent
        }
        
        # Broadcast admin presence to other admins
        emit('admin_presence_update', presence_data, room='admin_room', include_self=False)
        
        print(f"👑 Admin presence updated: {current_user.username} on {page}")
        
    except Exception as e:
        print(f"❌ Error updating admin presence: {str(e)}")

# Content Management Events
@socketio.on('content_auto_saved')
@admin_only
def handle_content_auto_saved(data):
    """Handle content auto-save events"""
    try:
        content_id = data.get('content_id')
        content_type = data.get('content_type')
        auto_save_data = {
            'content_id': content_id,
            'content_type': content_type,
            'saved_by': current_user.username,
            'timestamp': datetime.utcnow().isoformat(),
            'message': f'{content_type} auto-saved'
        }
        
        # Broadcast to other admins working on content
        emit('content_auto_saved_broadcast', auto_save_data, room='module_builder', include_self=False)
        
        # Confirm to sender
        emit('content_auto_save_confirmed', auto_save_data)
        
        print(f"💾 Content auto-saved: {content_type} by {current_user.username}")
        
    except Exception as e:
        print(f"❌ Error handling content auto-save: {str(e)}")

@socketio.on('concurrent_edit_detected')
@admin_only
def handle_concurrent_edit_detected(data):
    """Handle concurrent editing detection"""
    try:
        content_id = data.get('content_id')
        content_type = data.get('content_type')
        
        warning_data = {
            'content_id': content_id,
            'content_type': content_type,
            'editor': current_user.username,
            'message': f'{current_user.username} is also editing this {content_type}',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Warn other editors
        emit('concurrent_edit_warning', warning_data, room='module_builder', include_self=False)
        
        print(f"⚠️ Concurrent editing detected: {content_type} by {current_user.username}")
        
    except Exception as e:
        print(f"❌ Error handling concurrent edit detection: {str(e)}")

@socketio.on('content_published')
@admin_only
def handle_content_published(data):
    """Handle content publishing events"""
    try:
        content_data = data.get('content')
        content_type = data.get('content_type', 'content')
        class_id = data.get('class_id')
        
        publish_data = {
            'content': content_data,
            'content_type': content_type,
            'class_id': class_id,
            'published_by': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Broadcast to admin rooms
        emit('content_published_broadcast', publish_data, room='admin_room')
        emit('content_published_broadcast', publish_data, room='module_builder')
        
        # Notify students in class if class_id provided
        if class_id:
            emit('new_content_available', {
                'content_type': content_type,
                'content_title': content_data.get('title', 'New Content'),
                'class_id': class_id,
                'published_by': current_user.username
            }, room=f'class_{class_id}')
        
        print(f"📤 Content published: {content_type} by {current_user.username}")
        
    except Exception as e:
        print(f"❌ Error handling content publishing: {str(e)}")

# User Management Events
@socketio.on('user_status_changed')
@admin_only
def handle_user_status_changed(data):
    """Handle user status changes (enable/disable/role changes)"""
    try:
        user_id = data.get('user_id')
        old_status = data.get('old_status')
        new_status = data.get('new_status')
        action = data.get('action')  # 'enable', 'disable', 'role_change', etc.
        
        status_change_data = {
            'user_id': user_id,
            'old_status': old_status,
            'new_status': new_status,
            'action': action,
            'changed_by': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Broadcast to admin rooms
        emit('user_status_changed_broadcast', status_change_data, room='admin_room')
        emit('user_status_changed_broadcast', status_change_data, room='user_management')
        
        # Update real-time user stats
        emit_user_management_stats()
        
        print(f"👤 User status changed: User {user_id} {action} by {current_user.username}")
        
    except Exception as e:
        print(f"❌ Error handling user status change: {str(e)}")

@socketio.on('bulk_user_action')
@admin_only
def handle_bulk_user_action(data):
    """Handle bulk user actions"""
    try:
        user_ids = data.get('user_ids', [])
        action = data.get('action')
        additional_data = data.get('additional_data', {})
        
        bulk_action_data = {
            'user_ids': user_ids,
            'action': action,
            'additional_data': additional_data,
            'executed_by': current_user.username,
            'affected_count': len(user_ids),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Broadcast to admin rooms
        emit('bulk_user_action_broadcast', bulk_action_data, room='admin_room')
        emit('bulk_user_action_broadcast', bulk_action_data, room='user_management')
        
        print(f"👥 Bulk user action: {action} on {len(user_ids)} users by {current_user.username}")
        
    except Exception as e:
        print(f"❌ Error handling bulk user action: {str(e)}")

# Simulation Management Events
@socketio.on('simulation_created')
@admin_only
def handle_simulation_created_admin(data):
    """Handle simulation creation by admin"""
    try:
        simulation_data = data.get('simulation')
        category = data.get('category')
        
        creation_data = {
            'simulation': simulation_data,
            'category': category,
            'created_by': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Broadcast to admin rooms
        emit('simulation_created_broadcast', creation_data, room='admin_room')
        emit('simulation_created_broadcast', creation_data, room='simulation_builder')
        
        print(f"🎮 Simulation created: {simulation_data.get('title', 'Unknown')} by {current_user.username}")
        
    except Exception as e:
        print(f"❌ Error handling simulation creation: {str(e)}")

@socketio.on('simulation_auto_saved')
@admin_only
def handle_simulation_auto_saved(data):
    """Handle simulation auto-save events"""
    try:
        simulation_id = data.get('simulation_id')
        auto_save_data = {
            'simulation_id': simulation_id,
            'saved_by': current_user.username,
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Simulation auto-saved'
        }
        
        # Broadcast to simulation builder room
        emit('simulation_auto_saved_broadcast', auto_save_data, room='admin_room', include_self=False)
        
        # Confirm to sender
        emit('simulation_auto_save_confirmed', auto_save_data)
        
        print(f"💾 Simulation auto-saved: {simulation_id} by {current_user.username}")
        
    except Exception as e:
        print(f"❌ Error handling simulation auto-save: {str(e)}")

@socketio.on('simulation_validated')
@admin_only
def handle_simulation_validated(data):
    """Handle simulation validation results"""
    try:
        simulation_id = data.get('simulation_id')
        validation_results = data.get('validation_results')
        is_valid = data.get('is_valid')
        
        validation_data = {
            'simulation_id': simulation_id,
            'validation_results': validation_results,
            'is_valid': is_valid,
            'validated_by': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Broadcast to admin room
        emit('simulation_validated_broadcast', validation_data, room='admin_room')
        
        print(f"✅ Simulation validated: {simulation_id} ({'valid' if is_valid else 'invalid'}) by {current_user.username}")
        
    except Exception as e:
        print(f"❌ Error handling simulation validation: {str(e)}")

# Analytics Events
@socketio.on('request_analytics_update')
@admin_only
def handle_request_analytics_update(data):
    """Handle request for analytics data update"""
    try:
        analytics_type = data.get('analytics_type', 'general')
        time_range = data.get('time_range', 'last_7_days')
        
        # Emit current analytics data
        emit_analytics_data(analytics_type, time_range)
        
        print(f"📊 Analytics update requested: {analytics_type} for {time_range} by {current_user.username}")
        
    except Exception as e:
        print(f"❌ Error handling analytics update request: {str(e)}")

@socketio.on('performance_threshold_breach')
@admin_only
def handle_performance_threshold_breach(data):
    """Handle performance threshold breach alerts"""
    try:
        metric_name = data.get('metric_name')
        current_value = data.get('current_value')
        threshold_value = data.get('threshold_value')
        severity = data.get('severity', 'warning')
        
        alert_data = {
            'metric_name': metric_name,
            'current_value': current_value,
            'threshold_value': threshold_value,
            'severity': severity,
            'timestamp': datetime.utcnow().isoformat(),
            'message': f'{metric_name} threshold breached: {current_value} > {threshold_value}'
        }
        
        # Broadcast performance alert to all admin rooms
        emit('performance_alert_broadcast', alert_data, room='admin_room')
        emit('performance_alert_broadcast', alert_data, room='admin_dashboard')
        emit('performance_alert_broadcast', alert_data, room='analytics_room')
        
        print(f"🚨 Performance alert: {metric_name} threshold breached")
        
    except Exception as e:
        print(f"❌ Error handling performance threshold breach: {str(e)}")

# WebSocket Monitoring Events
@socketio.on('websocket_connection_stats')
@admin_only
def handle_websocket_connection_stats(data):
    """Handle WebSocket connection statistics updates"""
    try:
        stats_data = data.get('stats')
        
        # Broadcast WebSocket stats to admin monitoring
        emit('websocket_stats_updated', {
            'stats': stats_data,
            'timestamp': datetime.utcnow().isoformat()
        }, room='admin_collaboration_monitoring')
        
        print(f"🔌 WebSocket stats updated by {current_user.username}")
        
    except Exception as e:
        print(f"❌ Error handling WebSocket stats: {str(e)}")

@socketio.on('connection_diagnostic_request')
@admin_only
def handle_connection_diagnostic_request(data):
    """Handle connection diagnostic requests"""
    try:
        diagnostic_type = data.get('diagnostic_type', 'general')
        target_user_id = data.get('target_user_id')
        
        diagnostic_data = {
            'diagnostic_type': diagnostic_type,
            'target_user_id': target_user_id,
            'requested_by': current_user.username,
            'timestamp': datetime.utcnow().isoformat(),
            'results': {
                'connection_status': 'active',
                'latency': '45ms',
                'transport': 'websocket',
                'rooms': ['admin_room', 'admin_collaboration_monitoring']
            }
        }
        
        # Send diagnostic results
        emit('connection_diagnostic_results', diagnostic_data)
        
        print(f"🔍 Connection diagnostic requested: {diagnostic_type} by {current_user.username}")
        
    except Exception as e:
        print(f"❌ Error handling connection diagnostic: {str(e)}")

# Helper Functions for Admin Events
def emit_admin_dashboard_stats():
    """Emit current admin dashboard statistics"""
    try:
        # Get dashboard stats (would normally come from database queries)
        stats = {
            'total_users': get_total_users_count(),
            'active_users': get_active_users_count(),
            'total_classes': get_total_classes_count(),
            'pending_submissions': get_pending_submissions_count(),
            'system_load': get_system_load_percentage(),
            'active_simulations': get_active_simulations_count(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Broadcast to admin dashboard
        socketio.emit('dashboard_stats_update', stats, room='admin_dashboard')
        
    except Exception as e:
        print(f"❌ Error emitting dashboard stats: {str(e)}")

def emit_recent_admin_activity():
    """Emit recent admin activity feed"""
    try:
        # Get recent activity (would normally come from audit log)
        activities = [
            {
                'id': 1,
                'admin_name': 'System',
                'action': 'User Login',
                'details': 'Student user logged in',
                'timestamp': datetime.utcnow().isoformat(),
                'type': 'info'
            },
            {
                'id': 2,
                'admin_name': current_user.username,
                'action': 'Content Created',
                'details': 'New module created',
                'timestamp': datetime.utcnow().isoformat(),
                'type': 'success'
            }
        ]
        
        socketio.emit('recent_activity_update', {
            'activities': activities,
            'timestamp': datetime.utcnow().isoformat()
        }, room='admin_dashboard')
        
    except Exception as e:
        print(f"❌ Error emitting recent activity: {str(e)}")

def emit_user_management_stats():
    """Emit user management statistics"""
    try:
        stats = {
            'total_users': get_total_users_count(),
            'active_users': get_active_users_count(),
            'inactive_users': get_inactive_users_count(),
            'new_registrations_today': get_new_registrations_today(),
            'online_users': get_online_users_count(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        socketio.emit('user_management_stats_update', stats, room='user_management')
        
    except Exception as e:
        print(f"❌ Error emitting user management stats: {str(e)}")

def emit_notification_stats():
    """Emit notification statistics"""
    try:
        stats = {
            'total_notifications': get_total_notifications_count(),
            'unread_notifications': get_unread_notifications_count(),
            'notifications_sent_today': get_notifications_sent_today(),
            'notification_delivery_rate': get_notification_delivery_rate(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        socketio.emit('notification_stats_update', stats, room='notification_center')
        
    except Exception as e:
        print(f"❌ Error emitting notification stats: {str(e)}")

def emit_analytics_data(analytics_type='general', time_range='last_7_days'):
    """Emit analytics data"""
    try:
        # Generate analytics data based on type and time range
        analytics_data = {
            'analytics_type': analytics_type,
            'time_range': time_range,
            'data': get_analytics_data(analytics_type, time_range),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        socketio.emit('analytics_data_update', analytics_data, room='analytics_room')
        
    except Exception as e:
        print(f"❌ Error emitting analytics data: {str(e)}")

# Placeholder functions for statistics (these would be implemented with actual database queries)
def get_total_users_count():
    try:
        if UserModel:
            return UserModel.query.count()
        return 150  # Placeholder
    except:
        return 150

def get_active_users_count():
    try:
        # Would check for users active in last 24 hours
        return 45  # Placeholder
    except:
        return 45

def get_total_classes_count():
    try:
        from admin.models.class_model import Class
        return Class.query.count()
    except:
        return 12

def get_pending_submissions_count():
    try:
        # Would check for ungraded submissions
        return 8  # Placeholder
    except:
        return 8

def get_system_load_percentage():
    try:
        import psutil
        return psutil.cpu_percent()
    except:
        return 35  # Placeholder

def get_active_simulations_count():
    try:
        # Would check for currently running simulations
        return 5  # Placeholder
    except:
        return 5

def get_inactive_users_count():
    return get_total_users_count() - get_active_users_count()

def get_new_registrations_today():
    try:
        # Would check for users registered today
        return 3  # Placeholder
    except:
        return 3

def get_online_users_count():
    try:
        # Would check currently connected users
        return len(leaderboard_users) if 'leaderboard_users' in globals() else 15
    except:
        return 15

def get_total_notifications_count():
    try:
        # Would get from notification table
        return 245  # Placeholder
    except:
        return 245

def get_unread_notifications_count():
    try:
        # Would get unread notifications
        return 18  # Placeholder
    except:
        return 18

def get_notifications_sent_today():
    try:
        # Would check notifications sent today
        return 67  # Placeholder
    except:
        return 67

def get_notification_delivery_rate():
    try:
        # Would calculate delivery success rate
        return 94.5  # Placeholder percentage
    except:
        return 94.5

def get_analytics_data(analytics_type, time_range):
    """Get analytics data based on type and time range"""
    try:
        # This would be implemented with actual database queries
        return {
            'user_activity': [10, 15, 8, 23, 18, 12, 20],
            'simulation_completions': [5, 8, 3, 12, 9, 6, 11],
            'performance_metrics': {
                'average_score': 78.5,
                'completion_rate': 85.2,
                'engagement_time': 45.3
            }
        }
    except:
        return {}

@socketio.on('join_admin_collaboration_monitoring')
@admin_only
def handle_join_admin_collaboration_monitoring(data=None):
    """Join admin collaboration monitoring room for real-time collaboration tracking"""
    try:
        join_room('admin_collaboration_monitoring')
        emit('joined_collaboration_monitoring', {
            'success': True, 
            'message': 'Connected to collaboration monitoring'
        })
        print(f"👑 Admin {current_user.username} joined collaboration monitoring room")
        
        # Send current collaboration stats on join
        if lobby_manager:
            active_lobbies = lobby_manager.get_public_lobbies()
            total_participants = sum(len(lobby.get('participants', [])) for lobby in active_lobbies)
            
            # Calculate average duration (simplified)
            avg_duration = "0m"
            if active_lobbies:
                durations = []
                for lobby_data in active_lobbies:
                    if 'created_at' in lobby_data:
                        try:
                            created_time = datetime.fromisoformat(lobby_data['created_at'].replace('Z', '+00:00'))
                            duration_minutes = int((datetime.utcnow() - created_time.replace(tzinfo=None)).total_seconds() / 60)
                            durations.append(duration_minutes)
                        except:
                            pass
                if durations:
                    avg_duration = f"{int(sum(durations) / len(durations))}m"
            
            emit('stats_updated', {
                'activeGroups': len(active_lobbies),
                'totalParticipants': total_participants,
                'avgDuration': avg_duration
            })
            
            # Send current active collaborations
            collaboration_sessions = []
            for lobby_data in active_lobbies:
                collaboration_sessions.append({
                    'id': lobby_data.get('id'),
                    'activity_name': lobby_data.get('name', 'Unknown Session'),
                    'participants': [p.get('username', 'Unknown') for p in lobby_data.get('participants', [])],
                    'duration': avg_duration,  # Simplified - would need actual calculation per lobby
                    'status': 'active'
                })
            
            if collaboration_sessions:
                emit('collaboration_list_update', collaboration_sessions)
        
    except Exception as e:
        print(f"❌ Error joining collaboration monitoring room: {str(e)}")
        emit('collaboration_monitoring_error', {'error': str(e)})

@socketio.on('join_module_builder')
@admin_only
def handle_join_module_builder(data):
    """Join module builder room for real-time module updates"""
    try:
        class_id = data.get('class_id')
        
        # Join general module builder room
        join_room('module_builder')
        
        # Join class-specific room if class_id provided
        if class_id:
            join_room(f'class_{class_id}')
            emit('joined_module_builder', {
                'success': True, 
                'class_id': class_id,
                'rooms': ['module_builder', f'class_{class_id}']
            })
        else:
            emit('joined_module_builder', {
                'success': True,
                'rooms': ['module_builder']
            })
        
        print(f"🏗️ Admin {current_user.username} joined module builder room")
        
    except Exception as e:
        print(f"❌ Error joining module builder: {str(e)}")
        emit('module_builder_error', {'error': str(e)})

@socketio.on('leave_module_builder')
@authenticated_only
def handle_leave_module_builder(data=None):
    """Leave module builder room"""
    try:
        class_id = data.get('class_id') if data else None
        
        leave_room('module_builder')
        if class_id:
            leave_room(f'class_{class_id}')
        
        emit('left_module_builder', {'success': True})
        print(f"🏗️ User {current_user.username} left module builder room")
        
    except Exception as e:
        print(f"❌ Error leaving module builder: {str(e)}")

@socketio.on('module_created')
@admin_only
def handle_module_created(data):
    """Handle module creation event and broadcast to other admins"""
    try:
        module_data = data.get('module')
        class_id = data.get('class_id')
        
        if not module_data or not class_id:
            emit('module_creation_error', {'error': 'Module data and class_id required'})
            return
        
        # Broadcast to admin room
        socketio.emit('module_created_broadcast', {
            'module': module_data,
            'class_id': class_id,
            'created_by': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, room='admin_room')
        
        # Broadcast to module builder room
        socketio.emit('module_created_broadcast', {
            'module': module_data,
            'class_id': class_id,
            'created_by': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, room='module_builder')
        
        # Broadcast to class-specific room
        socketio.emit('module_created_broadcast', {
            'module': module_data,
            'class_id': class_id,
            'created_by': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, room=f'class_{class_id}')
        
        emit('module_creation_success', {'message': 'Module creation broadcasted'})
        print(f"📝 Module creation broadcasted by {current_user.username}: {module_data.get('title', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Error broadcasting module creation: {str(e)}")
        emit('module_creation_error', {'error': str(e)})

@socketio.on('module_updated')
@admin_only
def handle_module_updated(data):
    """Handle module update event and broadcast to other admins"""
    try:
        module_data = data.get('module')
        class_id = data.get('class_id')
        
        if not module_data or not class_id:
            emit('module_update_error', {'error': 'Module data and class_id required'})
            return
        
        # Broadcast to admin room
        socketio.emit('module_updated_broadcast', {
            'module': module_data,
            'class_id': class_id,
            'updated_by': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, room='admin_room')
        
        # Broadcast to module builder room
        socketio.emit('module_updated_broadcast', {
            'module': module_data,
            'class_id': class_id,
            'updated_by': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, room='module_builder')
        
        # Broadcast to class-specific room
        socketio.emit('module_updated_broadcast', {
            'module': module_data,
            'class_id': class_id,
            'updated_by': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, room=f'class_{class_id}')
        
        emit('module_update_success', {'message': 'Module update broadcasted'})
        print(f"📝 Module update broadcasted by {current_user.username}: {module_data.get('title', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Error broadcasting module update: {str(e)}")
        emit('module_update_error', {'error': str(e)})

# Helper functions for module WebSocket events
def emit_module_deleted(module_data, class_id):
    """Helper function to emit module deletion events"""
    try:
        from socket_manager import socketio
        
        broadcast_data = {
            'module': module_data,
            'class_id': class_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Emit to admin room
        socketio.emit('module_deleted_broadcast', broadcast_data, room='admin_room')
        
        # Emit to module builder room
        socketio.emit('module_deleted_broadcast', broadcast_data, room='module_builder')
        
        # Emit to class-specific room
        socketio.emit('module_deleted_broadcast', broadcast_data, room=f'class_{class_id}')
        
        print(f"📡 Module deletion events emitted for module {module_data.get('id')} in class {class_id}")
        
    except Exception as e:
        print(f"❌ Error emitting module deletion events: {str(e)}")

def emit_module_created(module_data, class_id, created_by):
    """Helper function to emit module creation events"""
    try:
        from socket_manager import socketio
        
        broadcast_data = {
            'module': module_data,
            'class_id': class_id,
            'created_by': created_by,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Emit to admin room
        socketio.emit('module_created_broadcast', broadcast_data, room='admin_room')
        
        # Emit to module builder room
        socketio.emit('module_created_broadcast', broadcast_data, room='module_builder')
        
        # Emit to class-specific room
        socketio.emit('module_created_broadcast', broadcast_data, room=f'class_{class_id}')
        
        print(f"📡 Module creation events emitted for module {module_data.get('title')} in class {class_id}")
        
    except Exception as e:
        print(f"❌ Error emitting module creation events: {str(e)}")

def emit_module_updated(module_data, class_id, updated_by):
    """Helper function to emit module update events"""
    try:
        from socket_manager import socketio
        
        broadcast_data = {
            'module': module_data,
            'class_id': class_id,
            'updated_by': updated_by,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Emit to admin room
        socketio.emit('module_updated_broadcast', broadcast_data, room='admin_room')
        
        # Emit to module builder room
        socketio.emit('module_updated_broadcast', broadcast_data, room='module_builder')
        
        # Emit to class-specific room
        socketio.emit('module_updated_broadcast', broadcast_data, room=f'class_{class_id}')
        
        print(f"📡 Module update events emitted for module {module_data.get('title')} in class {class_id}")
        
    except Exception as e:
        print(f"❌ Error emitting module update events: {str(e)}")

# ===== ADMIN WEBSOCKET TEST HANDLERS =====

@socketio.on('admin_test_message')
@authenticated_only
def handle_admin_test_message(data):
    """Handle admin test messages for WebSocket testing"""
    try:
        message = data.get('message', 'Test message')
        message_id = data.get('messageId', 'unknown')
        timestamp = data.get('timestamp', datetime.utcnow().isoformat())
        
        print(f"📨 Admin test message received: {message} (ID: {message_id})")
        
        # Emit response back to sender
        emit('admin_test_response', {
            'original_message': message,
            'message_id': message_id,
            'response': 'Message received successfully',
            'timestamp': timestamp,
            'response_timestamp': datetime.utcnow().isoformat(),
            'status': 'success'
        })
        
    except Exception as e:
        print(f"❌ Error handling admin test message: {str(e)}")
        emit('admin_test_response', {
            'error': str(e),
            'status': 'error'
        })

@socketio.on('admin_echo_test')
@authenticated_only
def handle_admin_echo_test(data):
    """Handle admin echo test for response time testing"""
    try:
        message = data.get('message', 'Echo test')
        timestamp = data.get('timestamp', datetime.utcnow().isoformat())
        
        # Echo the message back immediately
        emit('admin_echo_response', {
            'message': f"Echo: {message}",
            'original_timestamp': timestamp,
            'echo_timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error in admin echo test: {str(e)}")

@socketio.on('admin_broadcast_test')
@authenticated_only
@admin_only
def handle_admin_broadcast_test(data):
    """Handle admin broadcast testing"""
    try:
        message = data.get('message', 'Admin broadcast test')
        target = data.get('target', 'all_admins')
        timestamp = data.get('timestamp', datetime.utcnow().isoformat())
        
        broadcast_data = {
            'message': message,
            'from': current_user.username if current_user.is_authenticated else 'Admin',
            'timestamp': timestamp,
            'test_id': f"broadcast_{int(datetime.utcnow().timestamp())}"
        }
        
        if target == 'all_admins':
            # Broadcast to admin room
            socketio.emit('admin_broadcast_received', broadcast_data, room='admin_room')
        else:
            # Broadcast to all connected clients
            socketio.emit('admin_broadcast_received', broadcast_data)
        
        print(f"📡 Admin broadcast test sent: {message} (target: {target})")
        
        # Confirm to sender
        emit('admin_broadcast_test_response', {
            'status': 'sent',
            'target': target,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error in admin broadcast test: {str(e)}")
        emit('admin_broadcast_test_response', {
            'status': 'error',
            'error': str(e)
        })

@socketio.on('admin_join_room')
@authenticated_only
@admin_only
def handle_admin_join_room(data):
    """Handle admin joining test rooms"""
    try:
        room = data.get('room', 'admin_test_room')
        join_room(room)
        
        print(f"👥 Admin {current_user.username} joined room: {room}")
        
        # Notify others in the room
        emit('admin_room_user_joined', {
            'user': current_user.username,
            'room': room,
            'timestamp': datetime.utcnow().isoformat()
        }, room=room, include_self=False)
        
        # Confirm to sender
        emit('admin_room_joined', {
            'room': room,
            'status': 'joined',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error joining admin room: {str(e)}")

@socketio.on('admin_leave_room')
@authenticated_only
@admin_only
def handle_admin_leave_room(data):
    """Handle admin leaving test rooms"""
    try:
        room = data.get('room', 'admin_test_room')
        leave_room(room)
        
        print(f"👋 Admin {current_user.username} left room: {room}")
        
        # Notify others in the room
        emit('admin_room_user_left', {
            'user': current_user.username,
            'room': room,
            'timestamp': datetime.utcnow().isoformat()
        }, room=room)
        
        # Confirm to sender
        emit('admin_room_left', {
            'room': room,
            'status': 'left',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error leaving admin room: {str(e)}")

@socketio.on('admin_room_message')
@authenticated_only
@admin_only
def handle_admin_room_message(data):
    """Handle admin room messages for testing"""
    try:
        room = data.get('room', 'admin_test_room')
        message = data.get('message', 'Test room message')
        
        room_message_data = {
            'user': current_user.username,
            'message': message,
            'room': room,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Send to everyone in the room
        socketio.emit('admin_room_message_received', room_message_data, room=room)
        
        print(f"💬 Room message sent to {room}: {message}")
        
    except Exception as e:
        print(f"❌ Error sending room message: {str(e)}")

@socketio.on('admin_monitoring_request')
@authenticated_only
@admin_only
def handle_admin_monitoring_request(data):
    """Handle admin monitoring data requests"""
    try:
        metrics = data.get('metrics', ['connection_count', 'active_rooms'])
        timestamp = data.get('timestamp', datetime.utcnow().isoformat())
        
        # Simulate monitoring data (in real implementation, get actual metrics)
        monitoring_data = {
            'connection_count': len(socketio.server.manager.rooms.get('/', {})),
            'active_rooms': list(socketio.server.manager.rooms.get('/', {}).keys()),
            'message_rate': '10/sec',  # Simulated
            'server_status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'request_timestamp': timestamp
        }
        
        emit('admin_monitoring_response', monitoring_data)
        
        print(f"📊 Monitoring data sent: {len(monitoring_data)} metrics")
        
    except Exception as e:
        print(f"❌ Error getting monitoring data: {str(e)}")
        emit('admin_monitoring_response', {
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        })

print("🚀 Admin WebSocket test handlers loaded successfully")
