from socket_manager import socketio, authenticated_only, admin_only, user_connections
from flask_socketio import emit, join_room, leave_room
from flask import request
from flask_login import current_user
from utils.auth_decorators import instructor_required
from __init__ import db
from datetime import datetime, timedelta
from typing import List
import json
import time
import uuid
import threading

# Auto-progression tracking
_active_timers = {}  # session_id -> timer_thread

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
        print(f"[ERROR] Error sending assignment notification: {str(e)}")

def emit_simulation_update(class_id: int, update_data: dict):
    """Emit simulation update to all users in a class"""
    try:
        socketio.emit('simulation_update', update_data, room=f'class_{class_id}')
        print(f"📢 Sent simulation update to class {class_id}")
    except Exception as e:
        print(f"[ERROR] Error sending simulation update: {str(e)}")

def emit_instructor_simulation_updated(simulation_id: int, update_data: dict):
    """Emit real-time simulation update to users currently viewing the simulation"""
    try:
        notification_data = {
            'type': 'instructor_simulation_update',
            'simulation_id': simulation_id,
            'update_data': update_data,
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Simulation updated by admin'
        }
        
        # Emit to users currently viewing this simulation
        socketio.emit('instructor_simulation_updated', notification_data, room=f'simulation_{simulation_id}')
        
        # Also emit to any class rooms that might have this simulation assigned
        from instructor.models.simulation import Simulation
        from instructor.models.class_content import ClassAssignment
        
        simulation = Simulation.query.get(simulation_id)
        if simulation:
            # Find classes that have this simulation assigned
            assignments = ClassAssignment.query.filter_by(simulation_id=simulation_id).all()
            for assignment in assignments:
                socketio.emit('simulation_update', notification_data, room=f'class_{assignment.class_id}')
        
        print(f"📢 Sent admin simulation update for simulation {simulation_id} to active viewers")
    except Exception as e:
        print(f"[ERROR] Error sending admin simulation update: {str(e)}")

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
        print(f"[ERROR] Error sending module content update: {str(e)}")

def emit_grade_notification(user_id: int, grade_data: dict):
    """Emit grade notification to a specific user"""
    try:
        socketio.emit('grade_notification', grade_data, room=f'user_{user_id}')
        print(f"📢 Sent grade notification to user {user_id}")
    except Exception as e:
        print(f"[ERROR] Error sending grade notification: {str(e)}")

# ===== WEEK 2 ENHANCEMENT: REAL-TIME CONTENT UPDATES =====

def emit_new_simulation_available(simulation_id: int, category: str, class_ids: List[int] = None):
    """Notify users when new simulation is available"""
    try:
        from instructor.models.simulation import Simulation
        from instructor.models.class_model import Class
        from instructor.services.enhanced_class_template_generator import EnhancedClassTemplateGenerator
        
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
                print(f"[OK] Regenerated template for class {class_obj.name}")
            except Exception as e:
                print(f"[ERROR] Failed to regenerate template for class {class_obj.name}: {e}")
            
            # Notify users in this class
            class_notification = notification_data.copy()
            class_notification['class_id'] = class_obj.id
            class_notification['class_name'] = class_obj.name
            
            socketio.emit('new_simulation_available', class_notification, room=f'class_{class_obj.id}')
            print(f"📢 Notified class {class_obj.id} about new simulation {simulation_id}")
        
        # Broadcast to category room for users not in specific classes
        socketio.emit('new_simulation_available', notification_data, room=f'category_{category}')
        
    except Exception as e:
        print(f"[ERROR] Error sending new simulation notification: {str(e)}")

def emit_new_learning_path_available(path_id: int, category: str, class_ids: List[int] = None):
    """Notify users when new learning path is available - DEPRECATED"""
    try:
        # Learning Path feature has been removed from RiddleNet
        # This function now returns without doing anything
        print(f"[WARNING] Learning Path feature removed - ignoring emit for path_id: {path_id}")
        return
        
    except Exception as e:
        print(f"[ERROR] Error in deprecated learning path notification: {e}")
        return
        
        for class_obj in affected_classes:
            # Regenerate class template with new learning path
            try:
                generator.regenerate_class_resources(class_obj.id)
                print(f"[OK] Regenerated template for class {class_obj.name}")
            except Exception as e:
                print(f"[ERROR] Failed to regenerate template for class {class_obj.name}: {e}")
            
            # Notify users in this class
            class_notification = notification_data.copy()
            class_notification['class_id'] = class_obj.id
            class_notification['class_name'] = class_obj.name
            
            socketio.emit('new_learning_path_available', class_notification, room=f'class_{class_obj.id}')
            print(f"📢 Notified class {class_obj.id} about new learning path {path_id}")
        
        # Broadcast to category room
        socketio.emit('new_learning_path_available', notification_data, room=f'category_{category}')
        
    except Exception as e:
        print(f"[ERROR] Error sending new learning path notification: {str(e)}")

def emit_assignment_created(assignment_id: int, class_id: int, assignment_type: str):
    """Notify users when new assignment is created"""
    try:
        from instructor.models.simulation_assignment import SimulationAssignment
        from instructor.models.simulation import Simulation
        
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
            'message': f'[NOTE] New assignment: {assignment.title}',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Notify all users in the class
        socketio.emit('new_assignment_created', notification_data, room=f'class_{class_id}')
        print(f"📢 Notified class {class_id} about new assignment {assignment_id}")
        
    except Exception as e:
        print(f"[ERROR] Error sending assignment creation notification: {str(e)}")

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
        print(f"[USER] User {current_user.id} joined room {room}")

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
            print('\n' + '='*80)
            print('[SERVER SOCKET] 🔌 JOIN MODULE ROOM REQUEST')
            print('[SERVER SOCKET] Timestamp:', datetime.now().isoformat())
            print('[SERVER SOCKET] User ID:', current_user.id)
            print('[SERVER SOCKET] Username:', current_user.username)
            print('[SERVER SOCKET] Module ID:', module_id)
            print('[SERVER SOCKET] Room Name:', room)
            print('[SERVER SOCKET] Request SID:', request.sid)
            print('='*80 + '\n')
            
            join_room(room)
            emit('joined_room', {'room': room, 'type': 'module', 'module_id': module_id})
            
            print('\n' + '✅'*40)
            print('[SERVER SOCKET] ✅ USER JOINED ROOM SUCCESSFULLY')
            print('[SERVER SOCKET] User', current_user.username, 'is now in room:', room)
            print('[SERVER SOCKET] Will receive live_quiz_session_status_changed events for module', module_id)
            print('✅'*40 + '\n')

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
@instructor_required
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
            
        print(f"[OK] Broadcasted module-simulation {action} to relevant rooms")
        
    except Exception as e:
        print(f"[ERROR] Error handling module-simulation link event: {str(e)}")
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
    }, room='instructor_room')

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
    }, room='instructor_room')

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
        'from_instructor': True,
        'instructor_name': getattr(current_user, 'username', 'Admin'),
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
            'has_is_instructor': hasattr(current_user, 'is_instructor'),
            'is_instructor_value': getattr(current_user, 'is_instructor', None),
            'has_role': hasattr(current_user, 'role'),
            'role_value': getattr(current_user, 'role', None),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Check if user exists in admin table
        try:
            from instructor.models.user import Instructor
            admin_user = Instructor.query.filter_by(username=current_user.username).first()
            user_info['exists_in_admin_table'] = admin_user is not None
            if admin_user:
                user_info['admin_table_id'] = admin_user.id
                user_info['admin_table_role'] = getattr(admin_user, 'role', 'admin')
        except Exception as e:
            user_info['admin_table_error'] = str(e)
        
        print(f"[DEBUG] Debug admin status for {user_info['username']}: {user_info}")
        emit('debug_admin_response', user_info)
        
    except Exception as e:
        print(f"[ERROR] Error in debug_admin_status: {str(e)}")
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
    print("[OK] Troubleshooting lobby manager imported successfully")
except ImportError as e:
    print(f"[WARNING] Warning: Could not import lobby manager: {e}")
    lobby_manager = None

# ===== COLLABORATION SERVICE INTEGRATION =====
# Import the collaboration service
try:
    from services.collaboration_service import get_collaboration_service
    collaboration_service = get_collaboration_service()
    print("[OK] Collaboration service imported successfully")
except ImportError as e:
    print(f"[WARNING] Warning: Could not import collaboration service: {e}")
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
            
            print(f"[DEBUG] Emitting participant_joined event:")
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
            
            print(f"[OK] User {current_user.username} joined lobby {lobby.id}")
            print(f"[STATS] Notified admin monitoring of participant join")
        else:
            emit('lobby_joined', result)
            
    except Exception as e:
        print(f"[ERROR] Error joining lobby: {str(e)}")
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
                print(f"[STATS] Notified admin monitoring: lobby {lobby.id} ended (empty)")
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
                    print(f"[STATS] Notified admin monitoring of participant leave")
            
            emit('lobby_left', {'success': True})
            
            print(f"[OK] User {current_user.username} left lobby {lobby.id}")
        else:
            emit('lobby_left', {'success': True, 'message': 'Not in any lobby'})
        
    except Exception as e:
        print(f"[ERROR] Error leaving lobby: {str(e)}")
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
        print(f"[ERROR] Error getting public lobbies: {str(e)}")
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
        print(f"[ERROR] Error getting user lobby: {str(e)}")
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
                
                print(f"[OK] User {current_user.username} joined team lobby {lobby.id}")
        else:
            emit('team_lobby_joined', result)
            
    except Exception as e:
        print(f"[ERROR] Error joining team lobby: {str(e)}")
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
            
            print(f"[OK] User {current_user.username} joined lobby {lobby.id}")
        else:
            emit('lobby_joined', result)
            
    except Exception as e:
        print(f"[ERROR] Error joining lobby: {str(e)}")
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
            print(f"[OK] User {current_user.username} left team lobby {lobby.id}")
        else:
            emit('team_lobby_left', {'success': True, 'message': 'Not in any lobby'})
        
    except Exception as e:
        print(f"[ERROR] Error leaving team lobby: {str(e)}")
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
            print(f"[OK] User {current_user.username} left lobby {lobby.id}")
        else:
            emit('lobby_left', {'success': True, 'message': 'Not in any lobby'})
        
    except Exception as e:
        print(f"[ERROR] Error leaving lobby: {str(e)}")
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
            print(f"[WARNING] No lobby found for user {current_user.id}")
            return
        
        position = {
            'x': data.get('x', 0),
            'y': data.get('y', 0)
        }
        
        # Extract viewport data if provided
        viewport = data.get('viewport')
        
        lobby.update_participant_cursor(str(current_user.id), position)
        lobby_manager.update_participant_activity(str(current_user.id))
        
        # Broadcast cursor position to other participants
        # Use the same room name format as join_team_lobby
        room_name = f"lobby_{lobby.id}"
        
        cursor_data = {
            'user_id': str(current_user.id),
            'username': current_user.username,
            'position': position,
            'color': lobby.participants[str(current_user.id)]['color'],
            'profile_image': current_user.profile_img
        }
        
        # Add viewport data if available
        if viewport:
            cursor_data['viewport'] = viewport
            print(f"👁️ [VIEWPORT] User {current_user.username} viewport: {viewport}")
        
        print(f"🖱️ [CURSOR] Emitting cursor_moved to room: {room_name}")
        print(f"🖱️ [CURSOR] Data: {cursor_data}")
        
        emit('cursor_moved', cursor_data, room=room_name, include_self=False)
        
    except Exception as e:
        print(f"[ERROR] Error updating cursor: {str(e)}")

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
        
        print(f"[REFRESH] Network topology updated by {current_user.username} in lobby {lobby.id}")
        
    except Exception as e:
        print(f"[ERROR] Error updating network topology: {str(e)}")

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
        print(f"[ERROR] Error locking device: {str(e)}")

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
        print(f"[ERROR] Error unlocking device: {str(e)}")

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
        print(f"[ERROR] Error moving device: {str(e)}")

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
        print(f"[ERROR] Error executing CLI command: {str(e)}")
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
        print(f"[ERROR] Error adding device: {str(e)}")

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
        print(f"[ERROR] Error removing device: {str(e)}")

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
        print(f"[ERROR] Error adding connection: {str(e)}")

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
        
        print(f"🔗[ERROR] Connection removed by {current_user.username}")
        
    except Exception as e:
        print(f"[ERROR] Error removing connection: {str(e)}")

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
        print(f"[ERROR] Error updating device config: {str(e)}")

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
        
        print(f"[ACTIVITY] Progress updated by {current_user.username}")
        
    except Exception as e:
        print(f"[ERROR] Error updating progress: {str(e)}")

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
        
        print(f"[MSG] Chat message from {current_user.username} in lobby {lobby.id}: {message}")
        
    except Exception as e:
        print(f"[ERROR] Error sending chat message: {str(e)}")
        emit('lobby_chat_error', {'error': str(e)})

@socketio.on('collaboration_chat_message')
@authenticated_only
def handle_collaboration_chat_message(data):
    """Handle chat message in collaboration session"""
    try:
        print(f"[MSG] [DEBUG] ============================================")
        print(f"[MSG] [DEBUG] Received collaboration chat message")
        print(f"[MSG] [DEBUG] current_user.id: {current_user.id} (type: {type(current_user.id)})")
        print(f"[MSG] [DEBUG] current_user.username: {current_user.username}")
        print(f"[MSG] [DEBUG] Data received: {data}")
        print(f"[MSG] [DEBUG] Data user_id: {data.get('user_id')} (type: {type(data.get('user_id'))})")
        print(f"[MSG] [DEBUG] Data username: {data.get('username')}")
        print(f"[MSG] [DEBUG] ============================================")
        
        message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not message:
            emit('collaboration_chat_error', {'error': 'Message cannot be empty'})
            return
        
        if not session_id:
            emit('collaboration_chat_error', {'error': 'Session ID required'})
            return
        
        # CRITICAL FIX: Use current_user from Flask-Login, NOT from client data!
        # Client data can be stale/poisoned, always trust server-side session
        chat_message = {
            'id': str(uuid.uuid4()) if 'uuid' in globals() else f'msg_{int(time.time())}',
            'user_id': str(current_user.id),  # ← From Flask-Login session (trusted)
            'username': current_user.username,  # ← From Flask-Login session (trusted)
            'message': message,
            'message_type': 'text',
            'timestamp': datetime.utcnow().isoformat(),
            'session_id': session_id
        }
        
        print(f"[MSG] [DEBUG] Created chat_message with TRUSTED data:")
        print(f"[MSG] [DEBUG]   - user_id: {chat_message['user_id']}")
        print(f"[MSG] [DEBUG]   - username: {chat_message['username']}")
        print(f"[MSG] [DEBUG]   - message: {chat_message['message']}")
        
        # Use collaboration service if available
        if collaboration_service:
            result = collaboration_service.send_chat_message(
                session_id=session_id,
                user_id=str(current_user.id),  # ← Use trusted current_user
                message=message,
                message_type='text'
            )
            
            print(f"[MSG] [DEBUG] Collaboration service result: {result}")
            
            if result['success']:
                print(f"[MSG] [DEBUG] Broadcasting message with user_id={result['message']['user_id']}, username={result['message']['username']}")
                
                # Broadcast to all session participants
                emit('collaboration_chat_message', {
                    'success': True,
                    'message': result['message'],
                    'session_id': session_id
                }, room=f'session_{session_id}')
                
                # Also emit as team_chat_message for compatibility
                emit('team_chat_message', result['message'], room=f'session_{session_id}')
                
                print(f"[OK] [DEBUG] Chat message sent and broadcasted: {message[:50]}...")
            else:
                print(f"[ERROR] [DEBUG] Collaboration service error: {result['error']}")
                emit('collaboration_chat_error', {'error': result['error']})
        else:
            print(f"[MSG] [DEBUG] Using fallback (no collaboration service)")
            # Fallback: broadcast directly to session room
            emit('collaboration_chat_message', {
                'success': True,
                'message': chat_message,
                'session_id': session_id
            }, room=f'session_{session_id}')
            
            # Also emit as team_chat_message for compatibility
            emit('team_chat_message', chat_message, room=f'session_{session_id}')
            
            print(f"[OK] [DEBUG] Chat message broadcasted (fallback): {message[:50]}...")
            
    except Exception as e:
        print(f"[ERROR] [DEBUG] Error handling collaboration chat message: {str(e)}")
        import traceback
        traceback.print_exc()
        emit('collaboration_chat_error', {
            'error': f'Failed to send message: {str(e)}'
        })

@socketio.on('team_chat_message')
@authenticated_only
def handle_team_chat_message(data):
    """Handle team chat message (compatibility endpoint)"""
    try:
        print(f"[MSG] Received team chat message from {current_user.username}: {data}")
        
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
        
        print(f"[OK] Team chat message broadcasted: {message[:50]}...")
        
    except Exception as e:
        print(f"[ERROR] Error handling team chat message: {str(e)}")
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
        
        print(f"[OK] User {current_user.username} joined collaboration session {session_id}")
        
    except Exception as e:
        print(f"[ERROR] Error joining collaboration session: {str(e)}")
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
        
        print(f"[OK] User {current_user.username} left collaboration session {session_id}")
        
    except Exception as e:
        print(f"[ERROR] Error leaving collaboration session: {str(e)}")

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
        
        print(f"[OK] Lobby chat message sent: {message[:50]}...")
        
    except Exception as e:
        print(f"[ERROR] Error handling lobby chat: {str(e)}")
        emit('lobby_chat_error', {
            'error': f'Failed to send message: {str(e)}'
        })

# ===== MVP TEAM CHAT HANDLERS =====
# Import team chat service
try:
    from services.team_chat_service import get_team_chat_service
    team_chat_service = get_team_chat_service()
    print("[OK] Team chat service imported successfully")
except ImportError as e:
    print(f"[WARNING] Warning: Could not import team chat service: {e}")
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
            from instructor.models.collaboration import CollaborationSetting
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
            print(f"[WARNING] Could not check chat settings: {e}")
        
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
            
            print(f"[OK] Team chat message sent by {current_user.username} to {room_key}")
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
        print(f"[ERROR] Error handling team chat send: {str(e)}")
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
            
            print(f"[OK] Team chat history sent to {current_user.username}: {result['count']} messages")
        else:
            emit('team_chat_error', {
                'code': 'server_error',
                'message': result['error']
            })
            
    except Exception as e:
        print(f"[ERROR] Error handling team chat history request: {str(e)}")
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
        print(f"[ERROR] Error handling typing start: {str(e)}")

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
        print(f"[ERROR] Error handling typing stop: {str(e)}")

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
        
        print(f"[OK] User {current_user.username} joined team chat room: {room_key}")
        
    except Exception as e:
        print(f"[ERROR] Error joining team chat room: {str(e)}")
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
        
        print(f"[OK] User {current_user.username} left team chat room: {room_key}")
        
    except Exception as e:
        print(f"[ERROR] Error leaving team chat room: {str(e)}")


# ===== LIVE QUIZ REAL-TIME EVENTS =====

@socketio.on('join_live_quiz')
@authenticated_only
def handle_join_live_quiz(data):
    """Handle student joining a live quiz session - MVP FIX"""
    try:
        session_id = data.get('session_id')
        
        if not session_id:
            emit('live_quiz_error', {'message': 'No session ID provided'})
            return
        
        from user.models.live_quiz import LiveQuizSession, LiveQuizParticipant
        
        # Get session
        session = LiveQuizSession.query.get(session_id)
        if not session:
            emit('live_quiz_error', {'message': 'Quiz session not found'})
            return
        
        print(f"[MVP LiveQuiz] User {current_user.username} joining session {session_id} with status: {session.status}")
        
        # Check if user already joined
        participant = LiveQuizParticipant.query.filter_by(
            session_id=session_id,
            user_id=current_user.id
        ).first()
        
        if not participant:
            # Create new participant
            participant = LiveQuizParticipant(
                session_id=session_id,
                user_id=current_user.id,
                display_name=current_user.username
            )
            db.session.add(participant)
            db.session.commit()
            print(f"[MVP LiveQuiz] Created new participant for {current_user.username}")
        else:
            # Ensure existing participant stays marked active when rejoining lobby
            if not participant.is_active:
                participant.is_active = True
                db.session.commit()
                print(f"[MVP LiveQuiz] Reactivated participant record for {current_user.username}")
        
        # Join the quiz room
        room = f'live_quiz_{session_id}'
        join_room(room)
        print(f"[MVP LiveQuiz] User {current_user.username} joined room {room}")
        
        # Always calculate participant count fresh to include reloaded relationships
        participant_count = LiveQuizParticipant.query.filter_by(
            session_id=session_id,
            is_active=True
        ).count()

        # Get current leaderboard
        from user.routes.live_quiz_routes import get_session_leaderboard
        leaderboard = get_session_leaderboard(session_id)
        
        # Notify all participants of new joiner (broadcast to room)
        emit('participant_joined', {
            'participant_id': participant.id,
            'display_name': participant.display_name,
            'participant_count': participant_count,
            'session_id': session_id,
            'leaderboard': leaderboard  # Include leaderboard in broadcast
        }, room=room)
        
        print(
            f"[MVP LiveQuiz] Broadcast participant_joined to room {room} "
            f"- Total participants: {participant_count}"
        )
        
        # Send current quiz state to the joining user ONLY
        emit('quiz_state', {
            'status': session.status,
            'current_question_index': session.current_question_index,
            'participant': participant.to_dict(),
            'participant_count': participant_count,
            'leaderboard': leaderboard  # Send initial leaderboard to joiner
        })
        
        print(
            f"[MVP LiveQuiz] Sent quiz_state to {current_user.username} "
            f"- Status: {session.status}, Question: {session.current_question_index}, "
            f"Participants: {participant_count}"
        )
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Error joining live quiz: {str(e)}")
        import traceback
        traceback.print_exc()
        emit('live_quiz_error', {'message': str(e)})


@socketio.on('instructor_join_live_quiz')
@instructor_required
def handle_instructor_join_live_quiz(data):
    """Allow instructors to join the live quiz room for real-time monitoring."""
    try:
        session_id = data.get('session_id')

        if not session_id:
            emit('live_quiz_error', {'message': 'No session ID provided'})
            return

        from user.models.live_quiz import LiveQuizSession, LiveQuizParticipant
        from user.routes.live_quiz_routes import get_session_leaderboard

        session = LiveQuizSession.query.get(session_id)
        if not session:
            emit('live_quiz_error', {'message': 'Quiz session not found'})
            return

        room = f'live_quiz_{session_id}'
        join_room(room)
        print(f"[MVP LiveQuiz] Instructor {current_user.username} joined room {room}")

        # Get fresh participant count from database
        participant_count = LiveQuizParticipant.query.filter_by(
            session_id=session_id,
            is_active=True
        ).count()

        leaderboard = get_session_leaderboard(session_id)

        # Send initial sync to instructor
        emit('instructor_joined_live_quiz', {
            'session_id': session_id,
            'participant_count': participant_count,
            'status': session.status,
            'current_question_index': session.current_question_index,
            'leaderboard': leaderboard
        })

        print(
            f"[MVP LiveQuiz] Sent instructor_joined_live_quiz to {current_user.username} "
            f"- Participants: {participant_count}, Status: {session.status}"
        )
        
        # CRITICAL FIX: Immediately notify instructor of any existing participants
        # This ensures participant count is synced even if students joined before instructor
        if participant_count > 0:
            print(f"[MVP LiveQuiz] Instructor joined AFTER students - broadcasting current state")
            # Broadcast participant count update to ensure instructor UI syncs
            emit('participant_count_sync', {
                'session_id': session_id,
                'participant_count': participant_count,
                'leaderboard': leaderboard
            }, room=room)
            print(f"[MVP LiveQuiz] Sent participant_count_sync to room {room}")

    except Exception as e:
        print(f"[ERROR] Instructor join live quiz: {str(e)}")
        emit('live_quiz_error', {'message': str(e)})


@socketio.on('submit_live_answer')
@authenticated_only
def handle_submit_live_answer(data):
    """Handle real-time answer submission via MVP API"""
    try:
        session_id = str(data.get('session_id', ''))
        question_id = str(data.get('question_id', ''))
        selected_answer = data.get('selected_answer')
        response_time = data.get('response_time', 0)
        
        # Use MVP API's submit logic to maintain consistency
        from api.live_quiz_api import _get_session, _leaderboard_payload, _compute_points
        from time import time
        
        s = _get_session(session_id)
        uid = int(current_user.get_id())
        p = s['participants'].get(uid)
        
        if p is None:
            emit('live_quiz_error', {'message': 'You must join the session first'})
            return
        
        # Initialize answered questions tracking if not exists
        if 'answered_questions' not in s:
            s['answered_questions'] = {}
        if uid not in s['answered_questions']:
            s['answered_questions'][uid] = set()
        
        # Check if already answered this question
        if question_id in s['answered_questions'][uid]:
            print(f'[SUBMIT ANSWER] ⚠️ User {uid} already answered question {question_id} in session {session_id}')
            emit('live_quiz_error', {'message': 'Already answered this question'})
            return
        
        # Mark question as answered
        print(f'[SUBMIT ANSWER] ✅ User {uid} answering question {question_id} in session {session_id}')
        s['answered_questions'][uid].add(question_id)
        
        # Get question metadata from session
        meta = s['questions'].get(question_id, {})
        correct_answer = meta.get('correct_answer')
        explanation = meta.get('explanation')
        
        # Check if answer is correct
        if selected_answer is None or selected_answer == '':
            is_correct = False
        else:
            is_correct = (correct_answer is not None and 
                          str(selected_answer).strip() == str(correct_answer).strip())
        
        # Compute Slido-like points
        points = _compute_points(is_correct, response_time)
        
        # Update participant stats IN MEMORY
        p['total_answered'] += 1
        p['total_time_sec'] += response_time
        p['last_answer_at'] = time()
        
        if is_correct:
            p['total_correct'] += 1
            p['total_score'] += points
        
        print(f'[SUBMIT ANSWER] Score update: {p["total_score"]} ({"+" + str(points) if is_correct else "0"} points)')
        
        # 🔥 CRITICAL FIX: Update database participant scores
        from user.models.live_quiz import LiveQuizParticipant, LiveQuizResponse
        db_participant = LiveQuizParticipant.query.filter_by(
            session_id=int(session_id),
            user_id=uid
        ).first()
        
        if db_participant:
            db_participant.total_score = p['total_score']
            db_participant.total_correct = p['total_correct']
            db_participant.total_answered = p['total_answered']
            db_participant.total_time = p['total_time_sec']
            db_participant.average_response_time = p['total_time_sec'] / p['total_answered'] if p['total_answered'] > 0 else 0.0
            
            # Save response record
            response = LiveQuizResponse(
                participant_id=db_participant.id,
                session_id=int(session_id),
                question_id=int(question_id),
                selected_answer=str(selected_answer),
                is_correct=is_correct,
                response_time=response_time,
                points_awarded=points if is_correct else 0
            )
            db.session.add(response)
            db.session.commit()
            
            print(f'[SUBMIT ANSWER] ✅ Database updated - User {uid} now has {db_participant.total_score} total points')
        else:
            print(f'[SUBMIT ANSWER] ⚠️ WARNING: No database participant found for user {uid}')
        
        # Get updated leaderboard
        leaderboard = _leaderboard_payload(s, current_uid=uid)
        
        # Broadcast to all participants in this quiz
        room = f'live_quiz_{session_id}'
        
        # Send answer result to the participant
        emit('answer_result', {
            'is_correct': is_correct,
            'points_awarded': points,
            'total_score': p['total_score'],
            'correct_answer': correct_answer,
            'explanation': explanation
        })
        
        # Broadcast leaderboard update to all participants
        emit('leaderboard_update', {
            'leaderboard': leaderboard,
            'answered_count': sum(1 for u in s['answered_questions'] if question_id in s['answered_questions'].get(u, set())),
            'session_id': session_id
        }, room=room)
        
        print(f"[OK] {current_user.username} submitted answer for question {question_id}")
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Error submitting live answer: {str(e)}")
        import traceback
        traceback.print_exc()
        emit('live_quiz_error', {'message': str(e)})


@socketio.on('instructor_start_quiz')
@instructor_required
def handle_instructor_start_quiz(data):
    """Instructor starts a live quiz - MVP FIX"""
    try:
        session_id = data.get('session_id')
        
        from user.models.live_quiz import LiveQuizSession
        
        session = LiveQuizSession.query.get(session_id)
        if not session:
            emit('live_quiz_error', {'message': 'Session not found'})
            return
        
        if session.status != 'waiting':
            emit('live_quiz_error', {'message': 'Quiz already started or completed'})
            return
        
        print(f"\n{'='*80}")
        print(f"[MVP REALTIME] Instructor starting session {session_id}")
        print(f"[MVP REALTIME] Session title: {session.title}")
        print(f"[MVP REALTIME] Module ID: {session.module_id}")
        print(f"[MVP REALTIME] Lesson ID: {session.lesson_id}")
        print(f"{'='*80}\n")
        
        # Update session status
        session.status = 'active'
        session.started_at = datetime.utcnow()
        session.current_question_index = 0
        db.session.commit()
        
        # Broadcast to quiz participants (students who already joined)
        room = f'live_quiz_{session_id}'
        emit('quiz_started', {
            'session_id': session_id,
            'started_at': session.started_at.isoformat(),
            'current_question_index': 0
        }, room=room)
        
        print(f"[MVP REALTIME] ✅ Broadcast 'quiz_started' to room: {room}")
        
        # CRITICAL: Broadcast to ALL students viewing the module page (not just joined)
        module_room = f'module_{session.module_id}'
        
        broadcast_data = {
            'session_id': session_id,
            'status': 'active',
            'class_id': session.class_id,
            'module_id': session.module_id,
            'lesson_id': session.lesson_id,
            'title': session.title,
            'session_code': session.session_code,
            'started_at': session.started_at.isoformat()
        }
        
        print(f"\n{'='*80}")
        print(f"[MVP REALTIME] 🚀 Broadcasting to module room: {module_room}")
        print(f"[MVP REALTIME] Event: live_quiz_session_status_changed")
        print(f"[MVP REALTIME] Data: {broadcast_data}")
        print(f"{'='*80}\n")
        
        emit('live_quiz_session_status_changed', broadcast_data, room=module_room, broadcast=True)
        
        print(f"[MVP REALTIME] ✅ Broadcast complete - All students on module {session.module_id} should see LIVE button")
        
        # Start automatic timer for first question
        from flask import current_app
        _start_question_timer(session_id, app=current_app._get_current_object())
        
        # Confirm to instructor
        emit('quiz_start_confirmed', {
            'success': True,
            'session_id': session_id,
            'status': 'active',
            'current_question_index': 0
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Error starting quiz: {str(e)}")
        import traceback
        traceback.print_exc()
        emit('live_quiz_error', {'message': str(e)})


def auto_advance_question(session_id, question_duration=30, leaderboard_duration=5, app=None):
    """Automatically advance to the next question when the timer expires."""
    time.sleep(question_duration)  # Wait for the active question timer to finish
    
    from user.models.live_quiz import LiveQuizSession, LiveQuizParticipant
    from user.routes.live_quiz_routes import get_session_leaderboard
    
    if app is None:
        print(f"[AUTO-ADVANCE] No app context available for session {session_id}, aborting auto-advance")
        if session_id in _active_timers:
            _active_timers.pop(session_id, None)
        return
    
    with app.app_context():
        try:
            session = LiveQuizSession.query.get(session_id)
            if not session or session.status != 'active':
                print(f"[AUTO-ADVANCE] Session {session_id} is no longer active. Cancelling timer.")
                if session_id in _active_timers:
                    del _active_timers[session_id]
                return
            
            room = f'live_quiz_{session_id}'
            current_q_index = session.current_question_index
            question_number = current_q_index + 1
            
            print(f"[AUTO-ADVANCE] Timer expired for session {session_id} (Question #{question_number})")
            
            # Capture leaderboard snapshot after the question completes
            leaderboard_snapshot = get_session_leaderboard(session_id)

            total_questions = 0
            try:
                total_questions = session._get_total_questions() or 0
            except Exception as total_questions_error:
                print(f"[AUTO-ADVANCE] Unable to determine total questions for session {session_id}: {total_questions_error}")
                total_questions = 0
            is_last_question = total_questions > 0 and question_number >= total_questions
            
            socketio.emit('timer_expired', {
                'session_id': session_id,
                'question_index': current_q_index,
                'timestamp': datetime.utcnow().isoformat(),
                'leaderboard': leaderboard_snapshot
            }, room=room, namespace='/')
            print(f"[AUTO-ADVANCE] Broadcast timer_expired for Q{question_number}")
            
            # Allow a short window for the answer reveal UI
            answer_reveal_delay = 3
            time.sleep(answer_reveal_delay)
            
            if is_last_question:
                print(f"[AUTO-ADVANCE] Session {session_id} reached final question. Completing quiz.")
                completion_time = datetime.utcnow()
                session.status = 'completed'
                session.ended_at = completion_time

                completed_count = 0
                try:
                    participants = LiveQuizParticipant.query.filter_by(session_id=session_id).all()
                    for participant in participants:
                        if not participant.completed_at:
                            participant.completed_at = completion_time
                            completed_count += 1
                except Exception as participant_error:
                    print(f"[AUTO-ADVANCE] Warning: Unable to mark participants as completed for session {session_id}: {participant_error}")

                db.session.commit()
                print(f"[AUTO-ADVANCE] Marked session {session_id} completed. Participants updated: {completed_count}")

                socketio.emit('quiz_ended', {
                    'session_id': session_id,
                    'ended_at': completion_time.isoformat(),
                    'leaderboard': leaderboard_snapshot
                }, room=room, namespace='/')
                module_room = f'module_{session.module_id}'
                socketio.emit('live_quiz_session_status_changed', {
                    'session_id': session_id,
                    'status': 'completed',
                    'class_id': session.class_id,
                    'module_id': session.module_id,
                    'lesson_id': session.lesson_id,
                    'ended_at': completion_time.isoformat()
                }, room=module_room, namespace='/', broadcast=True)

                if session_id in _active_timers:
                    _active_timers.pop(session_id, None)
                print(f"[AUTO-ADVANCE] Completed session {session_id}. No further timers scheduled.")
                return

            # Determine if we should show a leaderboard break (every 5th question)
            show_leaderboard_break = (question_number % 5 == 0)
            
            # Advance to the next question index
            session.current_question_index += 1
            db.session.commit()
            next_question_index = session.current_question_index
            print(f"[AUTO-ADVANCE] Advanced session {session_id} to question index {next_question_index}")
            
            # Broadcast next question payload
            socketio.emit('next_question', {
                'session_id': session_id,
                'question_index': next_question_index,
                'timestamp': datetime.utcnow().isoformat(),
                'leaderboard': leaderboard_snapshot,
                'show_leaderboard_break': show_leaderboard_break,
                'break_duration': leaderboard_duration if show_leaderboard_break else 0
            }, room=room, namespace='/')
            print(f"[AUTO-ADVANCE] Emitted next_question (break={show_leaderboard_break}) for session {session_id}")
            
            # Schedule next timer (delay start if we are showing a leaderboard break)
            delay_before_start = leaderboard_duration if show_leaderboard_break else 0
            _start_question_timer(session_id, question_duration, leaderboard_duration, app, delay_before_start=delay_before_start)
            
        except Exception as e:
            print(f"[AUTO-ADVANCE ERROR] {str(e)}")
            import traceback
            traceback.print_exc()
            if session_id in _active_timers:
                del _active_timers[session_id]


def _start_question_timer(session_id, question_duration=30, leaderboard_duration=5, app=None, delay_before_start=0):
    """Start automatic timer for current question"""
    # Cancel any existing timer for this session
    if session_id in _active_timers:
        _active_timers[session_id].cancel()
    
    # Get app instance if not provided
    if app is None:
        from flask import current_app
        app = current_app._get_current_object()
    
    def _begin_timer():
        timer = threading.Timer(question_duration, auto_advance_question, args=(session_id, question_duration, leaderboard_duration, app))
        timer.daemon = True
        timer.start()
        _active_timers[session_id] = timer
        print(f"[AUTO-TIMER] Started {question_duration}s timer for session {session_id}")
    
    if delay_before_start and delay_before_start > 0:
        delay_timer = threading.Timer(delay_before_start, _begin_timer)
        delay_timer.daemon = True
        delay_timer.start()
        _active_timers[session_id] = delay_timer
        print(f"[AUTO-TIMER] Delaying timer start by {delay_before_start}s for session {session_id}")
    else:
        _begin_timer()


def _cancel_question_timer(session_id):
    """Cancel automatic timer for a session"""
    if session_id in _active_timers:
        _active_timers[session_id].cancel()
        del _active_timers[session_id]
        print(f"[AUTO-TIMER] Cancelled timer for session {session_id}")


@socketio.on('instructor_next_question')
@instructor_required
def handle_instructor_next_question(data):
    """Instructor manually advances to next question - NOW DEPRECATED (auto-advance handles this)"""
    try:
        session_id = data.get('session_id')
        
        from user.models.live_quiz import LiveQuizSession
        
        session = LiveQuizSession.query.get(session_id)
        if not session:
            emit('live_quiz_error', {'message': 'Session not found'})
            return
        
        if session.status != 'active':
            emit('live_quiz_error', {'message': 'Quiz is not active'})
            return
        
        print(f"[MVP LiveQuiz] Instructor manually advancing session {session_id} from Q{session.current_question_index}")
        
        # Cancel auto-timer since instructor is manually advancing
        _cancel_question_timer(session_id)
        
        # Advance to next question
        session.current_question_index += 1
        db.session.commit()
        
        # Get updated leaderboard after previous question
        from user.routes.live_quiz_routes import get_session_leaderboard
        leaderboard = get_session_leaderboard(session_id)
        
        # Check if leaderboard break
        show_leaderboard_break = (session.current_question_index % 5 == 0) and (session.current_question_index > 0)
        
        # Broadcast to all participants in the room
        room = f'live_quiz_{session_id}'
        socketio.emit('next_question', {
            'question_index': session.current_question_index,
            'timestamp': datetime.utcnow().isoformat(),
            'leaderboard': leaderboard,
            'show_leaderboard_break': show_leaderboard_break
        }, room=room)
        
        print(f"[MVP LiveQuiz] Broadcast next_question to room {room} - Now showing Q{session.current_question_index + 1}")
        
        # Restart auto-timer for new question
        from flask import current_app
        _start_question_timer(session_id, app=current_app._get_current_object())
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Error advancing question: {str(e)}")
        import traceback
        traceback.print_exc()
        emit('live_quiz_error', {'message': str(e)})


@socketio.on('instructor_end_quiz')
@instructor_required
def handle_instructor_end_quiz(data):
    """Instructor ends a live quiz"""
    try:
        session_id = data.get('session_id')
        
        from user.models.live_quiz import LiveQuizSession, LiveQuizParticipant
        
        session = LiveQuizSession.query.get(session_id)
        if not session:
            emit('live_quiz_error', {'message': 'Session not found'})
            return
        
        # Cancel automatic timer
        _cancel_question_timer(session_id)
        
        # Update session status
        session.status = 'completed'
        session.ended_at = datetime.utcnow()
        
        # CRITICAL: Mark all participants as completed for gradebook integration
        participants = LiveQuizParticipant.query.filter_by(session_id=session_id).all()
        completed_count = 0
        for participant in participants:
            if not participant.completed_at:  # Only set if not already completed
                participant.completed_at = datetime.utcnow()
                completed_count += 1
        
        db.session.commit()
        print(f"[GRADEBOOK] Marked {completed_count} participants as completed for session {session_id}")
        
        # Get final leaderboard
        from user.routes.live_quiz_routes import get_session_leaderboard
        leaderboard = get_session_leaderboard(session_id)
        
        # Broadcast to all participants in quiz room
        room = f'live_quiz_{session_id}'
        emit('quiz_ended', {
            'session_id': session_id,
            'ended_at': session.ended_at.isoformat(),
            'leaderboard': leaderboard
        }, room=room)
        
        # REALTIME UPDATE: Broadcast to module room to hide "Join Quiz" button
        module_room = f'module_{session.module_id}'
        emit('live_quiz_session_status_changed', {
            'session_id': session_id,
            'status': 'completed',
            'class_id': session.class_id,
            'module_id': session.module_id,
            'lesson_id': session.lesson_id,
            'ended_at': session.ended_at.isoformat()
        }, room=module_room, broadcast=True)
        
        print(f"[OK] Instructor ended live quiz {session_id}")
        print(f"[REALTIME] Broadcast session end to module room: {module_room}")
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Error ending quiz: {str(e)}")
        emit('live_quiz_error', {'message': str(e)})


@socketio.on('leave_live_quiz')
@authenticated_only
def handle_leave_live_quiz(data):
    """Handle user leaving a live quiz"""
    try:
        session_id = data.get('session_id')
        
        if not session_id:
            return
        
        room = f'live_quiz_{session_id}'
        leave_room(room)
        
        try:
            from user.models.live_quiz import LiveQuizParticipant
            participant = LiveQuizParticipant.query.filter_by(
                session_id=session_id,
                user_id=current_user.id
            ).first()
            if participant and participant.is_active:
                participant.is_active = False
                db.session.commit()
                print(f"[OK] Marked {current_user.username} inactive for live quiz {session_id}")
        except Exception as inner_err:
            db.session.rollback()
            print(f"[WARN] Could not mark participant inactive: {inner_err}")

        print(f"[OK] {current_user.username} left live quiz {session_id}")
        
    except Exception as e:
        print(f"[ERROR] Error leaving live quiz: {str(e)}")
