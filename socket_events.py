from socket_manager import socketio, authenticated_only, admin_only, user_connections
from flask_socketio import emit, join_room, leave_room
from flask import request
from flask_login import current_user
from utils.auth_decorators import admin_required
from __init__ import db
from datetime import datetime, timedelta
from typing import List
import json
import time
import uuid

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

def emit_admin_simulation_updated(simulation_id: int, update_data: dict):
    """Emit real-time simulation update to users currently viewing the simulation"""
    try:
        notification_data = {
            'type': 'admin_simulation_update',
            'simulation_id': simulation_id,
            'update_data': update_data,
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Simulation updated by admin'
        }
        
        # Emit to users currently viewing this simulation
        socketio.emit('admin_simulation_updated', notification_data, room=f'simulation_{simulation_id}')
        
        # Also emit to any class rooms that might have this simulation assigned
        from admin.models.simulation import Simulation
        from admin.models.class_content import ClassAssignment
        
        simulation = Simulation.query.get(simulation_id)
        if simulation:
            # Find classes that have this simulation assigned
            assignments = ClassAssignment.query.filter_by(simulation_id=simulation_id).all()
            for assignment in assignments:
                socketio.emit('simulation_update', notification_data, room=f'class_{assignment.class_id}')
        
        print(f"📢 Sent admin simulation update for simulation {simulation_id} to active viewers")
    except Exception as e:
        print(f"❌ Error sending admin simulation update: {str(e)}")

def emit_module_content_updated(class_id: int, module_id: int, update_data: dict):
    """Emit real-time module content update to users currently viewing the module"""
    try:
        notification_data = {
            'type': 'module_content_update',
            'class_id': class_id,
            'module_id': module_id,
            'update_data': update_data,
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Module content updated by admin'
        }
        
        # Emit to users currently viewing this module
        socketio.emit('module_content_updated', notification_data, room=f'module_{module_id}')
        
        # Also emit to class room
        socketio.emit('module_content_updated', notification_data, room=f'class_{class_id}')
        
        print(f"📢 Sent module content update for module {module_id} in class {class_id}")
    except Exception as e:
        print(f"❌ Error sending module content update: {str(e)}")

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

@socketio.on('join_simulation_room')
@authenticated_only
def handle_join_simulation_room(data):
    """Join simulation-specific room for real-time updates"""
    if current_user.is_authenticated:
        simulation_id = data.get('simulation_id')
        if simulation_id:
            room = f'simulation_{simulation_id}'
            join_room(room)
            emit('joined_room', {'room': room, 'type': 'simulation', 'simulation_id': simulation_id})
            print(f"🎮 User {current_user.id} joined simulation room {room}")

@socketio.on('leave_simulation_room')
@authenticated_only
def handle_leave_simulation_room(data):
    """Leave simulation-specific room"""
    if current_user.is_authenticated:
        simulation_id = data.get('simulation_id')
        if simulation_id:
            room = f'simulation_{simulation_id}'
            leave_room(room)
            emit('left_room', {'room': room, 'type': 'simulation', 'simulation_id': simulation_id})
            print(f"🎮 User {current_user.id} left simulation room {room}")

@socketio.on('join_module_room')
@authenticated_only
def handle_join_module_room(data):
    """Join module-specific room for content updates"""
    if current_user.is_authenticated:
        module_id = data.get('module_id')
        if module_id:
            room = f'module_{module_id}'
            join_room(room)
            emit('joined_room', {'room': room, 'type': 'module', 'module_id': module_id})
            print(f"📚 User {current_user.id} joined module room {room}")

@socketio.on('leave_module_room')
@authenticated_only
def handle_leave_module_room(data):
    """Leave module-specific room"""
    if current_user.is_authenticated:
        module_id = data.get('module_id')
        if module_id:
            room = f'module_{module_id}'
            leave_room(room)
            emit('left_room', {'room': room, 'type': 'module', 'module_id': module_id})
            print(f"📚 User {current_user.id} left module room {room}")

@socketio.on('module_simulation_linked')
@admin_required
def handle_module_simulation_linked(data):
    """Handle module-simulation linking/unlinking events"""
    try:
        module_id = data.get('module_id')
        simulation_id = data.get('simulation_id')
        assignment_id = data.get('assignment_id')
        class_id = data.get('class_id')
        action = data.get('action')  # 'linked' or 'unlinked'
        
        print(f"🔗 Module-simulation {action}: module={module_id}, simulation={simulation_id}, class={class_id}")
        
        # Broadcast to module room
        if module_id:
            module_room = f'module_{module_id}'
            emit('module_content_updated', {
                'module_id': module_id,
                'simulation_id': simulation_id,
                'assignment_id': assignment_id,
                'action': action,
                'type': 'simulation_link',
                'updated_by': current_user.username if current_user.is_authenticated else 'System',
                'timestamp': data.get('timestamp', time.time() * 1000)
            }, room=module_room)
            
        # Also broadcast to class room if class_id is provided
        if class_id:
            class_room = f'class_{class_id}'
            emit('class_module_updated', {
                'class_id': class_id,
                'module_id': module_id,
                'simulation_id': simulation_id,
                'assignment_id': assignment_id,
                'action': action,
                'type': 'simulation_link',
                'updated_by': current_user.username if current_user.is_authenticated else 'System',
                'timestamp': data.get('timestamp', time.time() * 1000)
            }, room=class_room)
            
        print(f"✅ Broadcasted module-simulation {action} to relevant rooms")
        
    except Exception as e:
        print(f"❌ Error handling module-simulation link event: {str(e)}")
        emit('error', {'message': f'Error processing module link: {str(e)}'}, room=request.sid)

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

# ===== COLLABORATION SERVICE INTEGRATION =====
# Import the collaboration service
try:
    from services.collaboration_service import get_collaboration_service
    collaboration_service = get_collaboration_service()
    print("✅ Collaboration service imported successfully")
except ImportError as e:
    print(f"⚠️ Warning: Could not import collaboration service: {e}")
    collaboration_service = None

# Lobby Management Events
@socketio.on('create_troubleshooting_lobby')
@authenticated_only
def handle_create_lobby(data):
    """Create a new collaborative troubleshooting lobby - RESTRICTED TO ADMINS ONLY"""
    # DISABLED: Users can no longer create lobbies directly
    emit('lobby_created', {
        'success': False, 
        'error': 'Lobby creation is restricted to administrators only. Please contact your teacher to create collaboration sessions.'
    })
    return

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
            
            # Notify user of successful join with chat history
            emit('lobby_joined', {
                'success': True,
                'lobby': lobby.to_dict(),
                'chat_history': lobby.chat_history  # Send chat history to new participant
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

# ===== TEAM LOBBY HANDLERS =====
@socketio.on('join_team_lobby')
@authenticated_only
def handle_join_team_lobby(data):
    """Join a team lobby (collaboration session)"""
    if not lobby_manager:
        emit('team_lobby_joined', {'success': False, 'error': 'Lobby system not available'})
        return
    
    try:
        lobby_id = data.get('lobby_id')
        if not lobby_id:
            emit('team_lobby_joined', {'success': False, 'error': 'Lobby ID required'})
            return
        
        # Join the lobby
        result = lobby_manager.join_lobby(
            lobby_id=lobby_id,
            user_id=str(current_user.id),
            user_info={
                'username': current_user.username,
                'profile_image': getattr(current_user, 'profile_img', None)
            }
        )
        
        if result['success']:
            lobby = lobby_manager.get_lobby_by_id(lobby_id)
            if lobby:
                room_name = f'lobby_{lobby_id}'
                join_room(room_name)
                
                # Also join session room for chat compatibility
                join_room(f'session_{lobby_id}')
                
                emit('team_lobby_joined', {
                    'success': True,
                    'lobby': lobby.to_dict(),
                    'team_assignment': result.get('team_assignment'),
                    'chat_history': lobby.chat_history[-20:] if lobby.chat_history else []
                })
                
                # Notify other participants of new user
                participant_data = lobby.participants[str(current_user.id)]
                join_event_data = {
                    'user_id': str(current_user.id),
                    'username': current_user.username,
                    'participant_data': participant_data
                }
                
                emit('participant_joined', join_event_data, room=room_name, include_self=False)
                
                # Send current network state to new participant
                emit('network_state_sync', {
                    'network_state': lobby.network_state,
                    'participants': lobby.participants
                })
                
                print(f"✅ User {current_user.username} joined team lobby {lobby.id}")
        else:
            emit('team_lobby_joined', result)
            
    except Exception as e:
        print(f"❌ Error joining team lobby: {str(e)}")
        emit('team_lobby_joined', {
            'success': False,
            'error': str(e)
        })

@socketio.on('join_lobby')
@authenticated_only  
def handle_join_lobby_generic(data):
    """Generic join lobby handler for collaboration sessions"""  
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
                'profile_image': getattr(current_user, 'profile_img', None)
            }
        )
        
        if result['success']:
            lobby = result['lobby']
            room_name = f"lobby_{lobby.id}"
            
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

@socketio.on('leave_team_lobby')
@authenticated_only
def handle_leave_team_lobby(data=None):
    """Leave current team lobby"""
    if not lobby_manager:
        emit('team_lobby_left', {'success': False, 'error': 'Lobby system not available'})
        return
    
    try:
        lobby = lobby_manager.get_user_lobby(str(current_user.id))
        
        if lobby:
            room_name = f"team_lobby_{lobby.id}"
            
            # Notify other participants
            emit('participant_left', {
                'user_id': str(current_user.id),
                'username': current_user.username
            }, room=room_name, include_self=False)
            
            # Leave the room
            leave_room(room_name)
            
            # Remove from lobby
            lobby_manager.leave_lobby(str(current_user.id))
            
            emit('team_lobby_left', {'success': True})
            print(f"✅ User {current_user.username} left team lobby {lobby.id}")
        else:
            emit('team_lobby_left', {'success': True, 'message': 'Not in any lobby'})
        
    except Exception as e:
        print(f"❌ Error leaving team lobby: {str(e)}")
        emit('team_lobby_left', {
            'success': False,
            'error': str(e)
        })

@socketio.on('leave_lobby')
@authenticated_only
def handle_leave_lobby_generic(data=None):
    """Generic leave lobby handler"""
    if not lobby_manager:
        emit('lobby_left', {'success': False, 'error': 'Lobby system not available'})
        return
    
    try:
        lobby = lobby_manager.get_user_lobby(str(current_user.id))
        
        if lobby:
            room_name = f"lobby_{lobby.id}"
            
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

@socketio.on('collaboration_chat_message')
@authenticated_only
def handle_collaboration_chat_message(data):
    """Handle chat message in collaboration session"""
    try:
        print(f"💬 Received collaboration chat message from {current_user.username}: {data}")
        
        message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not message:
            emit('collaboration_chat_error', {'error': 'Message cannot be empty'})
            return
        
        if not session_id:
            emit('collaboration_chat_error', {'error': 'Session ID required'})
            return
        
        # Create standardized message object
        chat_message = {
            'id': str(uuid.uuid4()) if 'uuid' in globals() else f'msg_{int(time.time())}',
            'user_id': str(current_user.id),
            'username': current_user.username,
            'message': message,
            'message_type': 'text',
            'timestamp': datetime.utcnow().isoformat(),
            'session_id': session_id
        }
        
        # Use collaboration service if available
        if collaboration_service:
            result = collaboration_service.send_chat_message(
                session_id=session_id,
                user_id=str(current_user.id),
                message=message,
                message_type='text'
            )
            
            if result['success']:
                # Broadcast to all session participants
                emit('collaboration_chat_message', {
                    'success': True,
                    'message': result['message'],
                    'session_id': session_id
                }, room=f'session_{session_id}')
                
                # Also emit as team_chat_message for compatibility
                emit('team_chat_message', result['message'], room=f'session_{session_id}')
                
                print(f"✅ Chat message sent and broadcasted: {message[:50]}...")
            else:
                emit('collaboration_chat_error', {'error': result['error']})
        else:
            # Fallback: broadcast directly to session room
            emit('collaboration_chat_message', {
                'success': True,
                'message': chat_message,
                'session_id': session_id
            }, room=f'session_{session_id}')
            
            # Also emit as team_chat_message for compatibility
            emit('team_chat_message', chat_message, room=f'session_{session_id}')
            
            print(f"✅ Chat message broadcasted (fallback): {message[:50]}...")
            
    except Exception as e:
        print(f"❌ Error handling collaboration chat message: {str(e)}")
        emit('collaboration_chat_error', {
            'error': f'Failed to send message: {str(e)}'
        })

@socketio.on('team_chat_message')
@authenticated_only
def handle_team_chat_message(data):
    """Handle team chat message (compatibility endpoint)"""
    try:
        print(f"💬 Received team chat message from {current_user.username}: {data}")
        
        message = data.get('message', '').strip()
        session_id = data.get('session_id') or data.get('lobby_id')
        
        if not message:
            emit('team_chat_error', {'error': 'Message cannot be empty'})
            return
        
        # Create message object
        chat_message = {
            'id': str(uuid.uuid4()) if 'uuid' in globals() else f'msg_{int(time.time())}',
            'user_id': str(current_user.id),
            'username': current_user.username,
            'message': message,
            'message_type': 'text',
            'timestamp': datetime.utcnow().isoformat(),
            'session_id': session_id
        }
        
        # Broadcast to session participants
        if session_id:
            emit('team_chat_message', chat_message, room=f'session_{session_id}')
            emit('collaboration_chat_message', {
                'success': True,
                'message': chat_message,
                'session_id': session_id
            }, room=f'session_{session_id}')
        else:
            # Broadcast to all connected users as fallback
            emit('team_chat_message', chat_message, broadcast=True)
        
        print(f"✅ Team chat message broadcasted: {message[:50]}...")
        
    except Exception as e:
        print(f"❌ Error handling team chat message: {str(e)}")
        emit('team_chat_error', {
            'error': f'Failed to send message: {str(e)}'
        })

@socketio.on('join_collaboration_session')
@authenticated_only
def handle_join_collaboration_session(data):
    """Join a collaboration session room for chat"""
    try:
        session_id = data.get('session_id')
        if not session_id:
            emit('collaboration_join_error', {'error': 'Session ID required'})
            return
        
        # Join the session room
        join_room(f'session_{session_id}')
        
        # Get chat history if collaboration service is available
        chat_history = []
        if collaboration_service:
            history_result = collaboration_service.get_chat_history(
                session_id=session_id,
                user_id=str(current_user.id),
                limit=50
            )
            if history_result['success']:
                chat_history = history_result['chat_history']
        
        emit('collaboration_session_joined', {
            'success': True,
            'session_id': session_id,
            'chat_history': chat_history,
            'user_id': str(current_user.id),
            'username': current_user.username
        })
        
        # Notify other participants
        emit('collaboration_participant_joined', {
            'user_id': str(current_user.id),
            'username': current_user.username,
            'session_id': session_id
        }, room=f'session_{session_id}', include_self=False)
        
        print(f"✅ User {current_user.username} joined collaboration session {session_id}")
        
    except Exception as e:
        print(f"❌ Error joining collaboration session: {str(e)}")
        emit('collaboration_join_error', {
            'error': f'Failed to join session: {str(e)}'
        })

@socketio.on('leave_collaboration_session')
@authenticated_only
def handle_leave_collaboration_session(data):
    """Leave a collaboration session room"""
    try:
        session_id = data.get('session_id')
        if not session_id:
            return
        
        # Leave the session room
        leave_room(f'session_{session_id}')
        
        # Notify other participants
        emit('collaboration_participant_left', {
            'user_id': str(current_user.id),
            'username': current_user.username,
            'session_id': session_id
        }, room=f'session_{session_id}')
        
        emit('collaboration_session_left', {
            'success': True,
            'session_id': session_id
        })
        
        print(f"✅ User {current_user.username} left collaboration session {session_id}")
        
    except Exception as e:
        print(f"❌ Error leaving collaboration session: {str(e)}")

@socketio.on('send_lobby_chat')
@authenticated_only
def handle_send_lobby_chat(data):
    """Handle lobby chat message (for troubleshooting lobbies)"""
    try:
        if not lobby_manager:
            emit('lobby_chat_error', {'error': 'Lobby system not available'})
            return
        
        message = data.get('message', '').strip()
        message_type = data.get('type', 'text')
        
        if not message:
            emit('lobby_chat_error', {'error': 'Message cannot be empty'})
            return
        
        # Get user's current lobby
        lobby = lobby_manager.get_user_lobby(str(current_user.id))
        if not lobby:
            emit('lobby_chat_error', {'error': 'You are not in any lobby'})
            return
        
        # Create chat message
        chat_message = {
            'id': str(uuid.uuid4()) if 'uuid' in globals() else f'msg_{int(time.time())}',
            'user_id': str(current_user.id),
            'username': current_user.username,
            'message': message,
            'message_type': message_type,
            'timestamp': datetime.utcnow().isoformat(),
            'lobby_id': lobby.id
        }
        
        # Add to lobby chat history
        lobby.chat_history.append(chat_message)
        
        # Keep only last 100 messages
        if len(lobby.chat_history) > 100:
            lobby.chat_history = lobby.chat_history[-100:]
        
        # Broadcast to all lobby participants
        emit('lobby_chat_message', chat_message, room=f'lobby_{lobby.id}')
        
        print(f"✅ Lobby chat message sent: {message[:50]}...")
        
    except Exception as e:
        print(f"❌ Error handling lobby chat: {str(e)}")
        emit('lobby_chat_error', {
            'error': f'Failed to send message: {str(e)}'
        })

# ===== MVP TEAM CHAT HANDLERS =====
# Import team chat service
try:
    from services.team_chat_service import get_team_chat_service
    team_chat_service = get_team_chat_service()
    print("✅ Team chat service imported successfully")
except ImportError as e:
    print(f"⚠️ Warning: Could not import team chat service: {e}")
    team_chat_service = None

# Team Chat Events
@socketio.on('team_chat_send')
@authenticated_only
def handle_team_chat_send(data):
    """Handle sending team chat messages"""
    if not team_chat_service:
        emit('team_chat_error', {
            'code': 'server_error',
            'message': 'Team chat service not available'
        })
        return
    
    try:
        # Extract payload data
        simulation_session_id = data.get('simulation_session_id')
        team_id = data.get('team_id')
        lobby_id = data.get('lobby_id')
        content = data.get('content', '').strip()
        
        # Validate required fields
        if not simulation_session_id:
            emit('team_chat_error', {
                'code': 'invalid_payload',
                'message': 'simulation_session_id is required'
            })
            return
        
        if not content:
            emit('team_chat_error', {
                'code': 'invalid_payload',
                'message': 'Message content cannot be empty'
            })
            return
        
        # Check if either team_id or lobby_id is provided
        if not team_id and not lobby_id:
            emit('team_chat_error', {
                'code': 'invalid_payload',
                'message': 'Either team_id or lobby_id must be provided'
            })
            return
        
        # Authorization check - verify user is in the session/team/lobby
        # For MVP, we trust the client to send correct session/team info
        # In production, add proper membership validation here
        
        # Check if chat is enabled (use existing collaboration settings)
        try:
            from admin.models.collaboration import CollaborationSetting
            if simulation_session_id:
                # Check collaboration settings for this simulation
                settings = CollaborationSetting.query.filter_by(
                    simulation_id=simulation_session_id
                ).first()
                
                if settings and not settings.chat_enabled:
                    emit('team_chat_error', {
                        'code': 'chat_disabled',
                        'message': 'Chat is disabled for this simulation'
                    })
                    return
        except Exception as e:
            print(f"⚠️ Could not check chat settings: {e}")
        
        # Save message using team chat service
        result = team_chat_service.save_message(
            simulation_session_id=int(simulation_session_id),
            user_id=current_user.id,
            username=current_user.username,
            content=content,
            team_id=int(team_id) if team_id else None,
            lobby_id=int(lobby_id) if lobby_id else None
        )
        
        if result['success']:
            # Construct room key for broadcasting
            if team_id:
                room_key = f"sim:{simulation_session_id}:team:{team_id}"
            else:
                room_key = f"sim:{simulation_session_id}:lobby:{lobby_id}"
            
            # Prepare broadcast message
            message_data = result['message']
            message_data['is_self'] = False  # Will be overridden by clients
            
            # Broadcast to room participants
            emit('team_chat_message', message_data, room=room_key)
            
            print(f"✅ Team chat message sent by {current_user.username} to {room_key}")
        else:
            # Handle service errors
            error_code = 'server_error'
            if 'rate limit' in result['error'].lower():
                error_code = 'rate_limited'
            elif 'content' in result['error'].lower():
                error_code = 'invalid_payload'
            
            emit('team_chat_error', {
                'code': error_code,
                'message': result['error']
            })
            
    except Exception as e:
        print(f"❌ Error handling team chat send: {str(e)}")
        emit('team_chat_error', {
            'code': 'server_error',
            'message': f'Server error: {str(e)}'
        })

@socketio.on('team_chat_history_request')
@authenticated_only
def handle_team_chat_history_request(data):
    """Handle team chat history requests"""
    if not team_chat_service:
        emit('team_chat_error', {
            'code': 'server_error',
            'message': 'Team chat service not available'
        })
        return
    
    try:
        # Extract payload data
        simulation_session_id = data.get('simulation_session_id')
        team_id = data.get('team_id')
        lobby_id = data.get('lobby_id')
        limit = data.get('limit', 50)
        
        # Validate required fields
        if not simulation_session_id:
            emit('team_chat_error', {
                'code': 'invalid_payload',
                'message': 'simulation_session_id is required'
            })
            return
        
        # Check if either team_id or lobby_id is provided
        if not team_id and not lobby_id:
            emit('team_chat_error', {
                'code': 'invalid_payload',
                'message': 'Either team_id or lobby_id must be provided'
            })
            return
        
        # Enforce limit bounds
        limit = min(max(1, int(limit)), 100)
        
        # Authorization check - verify user is in the session/team/lobby
        # For MVP, we trust the client to send correct session/team info
        
        # Fetch messages using team chat service
        result = team_chat_service.fetch_recent(
            simulation_session_id=int(simulation_session_id),
            team_id=int(team_id) if team_id else None,
            lobby_id=int(lobby_id) if lobby_id else None,
            limit=limit
        )
        
        if result['success']:
            # Send history to requesting user
            emit('team_chat_history', {
                'messages': result['messages'],
                'simulation_session_id': simulation_session_id,
                'team_id': team_id,
                'lobby_id': lobby_id,
                'count': result['count']
            })
            
            print(f"✅ Team chat history sent to {current_user.username}: {result['count']} messages")
        else:
            emit('team_chat_error', {
                'code': 'server_error',
                'message': result['error']
            })
            
    except Exception as e:
        print(f"❌ Error handling team chat history request: {str(e)}")
        emit('team_chat_error', {
            'code': 'server_error',
            'message': f'Server error: {str(e)}'
        })

@socketio.on('user_typing_start')
@authenticated_only
def handle_user_typing_start(data):
    """Handle user typing start events"""
    try:
        simulation_session_id = data.get('simulation_session_id')
        team_id = data.get('team_id')
        lobby_id = data.get('lobby_id')
        
        if not simulation_session_id or (not team_id and not lobby_id):
            return
        
        # Construct room key
        if team_id:
            room_key = f"sim:{simulation_session_id}:team:{team_id}"
        else:
            room_key = f"sim:{simulation_session_id}:lobby:{lobby_id}"
        
        # Broadcast typing start to other participants
        emit('user_typing_start', {
            'user_id': current_user.id,
            'username': current_user.username,
            'simulation_session_id': simulation_session_id,
            'team_id': team_id,
            'lobby_id': lobby_id
        }, room=room_key, include_self=False)
        
    except Exception as e:
        print(f"❌ Error handling typing start: {str(e)}")

@socketio.on('user_typing_stop')
@authenticated_only
def handle_user_typing_stop(data):
    """Handle user typing stop events"""
    try:
        simulation_session_id = data.get('simulation_session_id')
        team_id = data.get('team_id')
        lobby_id = data.get('lobby_id')
        
        if not simulation_session_id or (not team_id and not lobby_id):
            return
        
        # Construct room key
        if team_id:
            room_key = f"sim:{simulation_session_id}:team:{team_id}"
        else:
            room_key = f"sim:{simulation_session_id}:lobby:{lobby_id}"
        
        # Broadcast typing stop to other participants
        emit('user_typing_stop', {
            'user_id': current_user.id,
            'simulation_session_id': simulation_session_id,
            'team_id': team_id,
            'lobby_id': lobby_id
        }, room=room_key, include_self=False)
        
    except Exception as e:
        print(f"❌ Error handling typing stop: {str(e)}")

# Room management for team chat
@socketio.on('join_team_chat_room')
@authenticated_only
def handle_join_team_chat_room(data):
    """Join team chat room for receiving messages"""
    try:
        simulation_session_id = data.get('simulation_session_id')
        team_id = data.get('team_id')
        lobby_id = data.get('lobby_id')
        
        if not simulation_session_id or (not team_id and not lobby_id):
            emit('team_chat_error', {
                'code': 'invalid_payload',
                'message': 'Missing required room parameters'
            })
            return
        
        # Construct room key
        if team_id:
            room_key = f"sim:{simulation_session_id}:team:{team_id}"
        else:
            room_key = f"sim:{simulation_session_id}:lobby:{lobby_id}"
        
        # Join the room
        join_room(room_key)
        
        emit('team_chat_room_joined', {
            'room': room_key,
            'simulation_session_id': simulation_session_id,
            'team_id': team_id,
            'lobby_id': lobby_id
        })
        
        print(f"✅ User {current_user.username} joined team chat room: {room_key}")
        
    except Exception as e:
        print(f"❌ Error joining team chat room: {str(e)}")
        emit('team_chat_error', {
            'code': 'server_error',
            'message': f'Failed to join room: {str(e)}'
        })

@socketio.on('leave_team_chat_room')
@authenticated_only
def handle_leave_team_chat_room(data):
    """Leave team chat room"""
    try:
        simulation_session_id = data.get('simulation_session_id')
        team_id = data.get('team_id')
        lobby_id = data.get('lobby_id')
        
        if not simulation_session_id or (not team_id and not lobby_id):
            return
        
        # Construct room key
        if team_id:
            room_key = f"sim:{simulation_session_id}:team:{team_id}"
        else:
            room_key = f"sim:{simulation_session_id}:lobby:{lobby_id}"
        
        # Leave the room
        leave_room(room_key)
        
        emit('team_chat_room_left', {
            'room': room_key
        })
        
        print(f"✅ User {current_user.username} left team chat room: {room_key}")
        
    except Exception as e:
        print(f"❌ Error leaving team chat room: {str(e)}")
