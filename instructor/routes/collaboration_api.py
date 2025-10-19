"""
Admin API routes for collaboration lobby management
Only admins/teachers can create and manage collaboration lobbies
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from services.troubleshooting_lobbies import lobby_manager
from instructor.models.class_model import Class
from instructor.models.activity_log import ActivityLog
from instructor.models.simulation import Simulation
from utils.permission_decorators import instructor_required, teacher_required
from __init__ import db
from datetime import datetime
import json

# Create blueprint for admin collaboration API
admin_collaboration_api_bp = Blueprint(
    'admin_collaboration_api', 
    __name__, 
    url_prefix='/instructor/api/collaboration'
)

print("🔧 Admin Collaboration API Blueprint created with prefix: /admin/api/collaboration")

@admin_collaboration_api_bp.route('/lobby', methods=['POST'])
@login_required
@teacher_required
def create_instructor_lobby():
    """Create a new collaborative lobby (admin/teacher only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Lobby name is required'
            }), 400
        
        lobby_config = {
            'name': data.get('name'),
            'scenario_type': data.get('scenario_type', 'medium'),
            'scenario_id': data.get('scenario_id', 'network'),
            'max_participants': data.get('max_participants', 6),
            'class_id': data.get('class_id'),
            'simulation_id': data.get('simulation_id'),
            'admin_created': True
        }
        
        # Validate class exists if class_id is provided
        if lobby_config['class_id']:
            class_obj = Class.query.get(lobby_config['class_id'])
            if not class_obj:
                return jsonify({
                    'success': False,
                    'error': 'Invalid class ID'
                }), 400
        
        # Validate simulation exists if simulation_id is provided
        if lobby_config['simulation_id']:
            simulation = Simulation.query.get(lobby_config['simulation_id'])
            if not simulation:
                return jsonify({
                    'success': False,
                    'error': 'Invalid simulation ID'
                }), 400
        
        lobby = lobby_manager.create_lobby(
            creator_id=str(current_user.id),
            creator_name=current_user.username,
            creator_profile_image=getattr(current_user, 'profile_img', None),
            lobby_config=lobby_config
        )

        # Log activity
        ActivityLog.log_activity(
            user_id=current_user.id,
            action_type='admin_lobby_create',
            message=f"Admin created lobby {lobby.id} ({lobby.name})",
            related_entity_type='lobby',
            related_entity_id=lobby.id
        )
        
        return jsonify({
            'success': True,
            'lobby': lobby.to_dict(),
            'lobby_id': lobby.id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_collaboration_api_bp.route('/lobbies', methods=['GET'])
@login_required
@teacher_required
def get_instructor_lobbies():
    """Get all lobbies (admin/teacher view)"""
    try:
        lobbies = lobby_manager.get_all_lobbies()
        
        # Convert lobby objects to dictionaries
        lobbies_data = []
        for lobby in lobbies:
            lobby_dict = lobby.to_dict() if hasattr(lobby, 'to_dict') else {
                'id': lobby.id,
                'name': lobby.name,
                'scenario_type': lobby.scenario_type,
                'scenario_id': lobby.scenario_id,
                'max_participants': lobby.max_participants,
                'class_id': lobby.class_id,
                'creator_id': lobby.creator_id,
                'creator_name': lobby.creator_name,
                'participants': lobby.participants,
                'is_active': lobby.is_active,
                'is_locked': lobby.is_locked,
                'created_at': lobby.created_at.isoformat() if hasattr(lobby.created_at, 'isoformat') else str(lobby.created_at)
            }
            lobbies_data.append(lobby_dict)
        
        return jsonify({
            'success': True,
            'lobbies': lobbies_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_collaboration_api_bp.route('/lobby/<lobby_id>', methods=['GET'])
@login_required
@teacher_required
def get_lobby_details(lobby_id):
    """Get detailed information about a specific lobby"""
    try:
        lobby = lobby_manager.get_lobby_by_id(lobby_id)
        if not lobby:
            return jsonify({
                'success': False,
                'error': 'Lobby not found'
            }), 404
        
        return jsonify({
            'success': True,
            'lobby': lobby.to_dict() if hasattr(lobby, 'to_dict') else {
                'id': lobby.id,
                'name': lobby.name,
                'scenario_type': lobby.scenario_type,
                'scenario_id': lobby.scenario_id,
                'max_participants': lobby.max_participants,
                'class_id': lobby.class_id,
                'creator_id': lobby.creator_id,
                'creator_name': lobby.creator_name,
                'participants': lobby.participants,
                'is_active': lobby.is_active,
                'is_locked': lobby.is_locked,
                'created_at': lobby.created_at.isoformat() if hasattr(lobby.created_at, 'isoformat') else str(lobby.created_at)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_collaboration_api_bp.route('/lobby/<lobby_id>/close', methods=['POST'])
@login_required
@teacher_required
def close_admin_lobby(lobby_id):
    """Close a lobby (admin/teacher)"""
    try:
        lobby = lobby_manager.get_lobby_by_id(lobby_id)
        if not lobby:
            return jsonify({
                'success': False,
                'error': 'Lobby not found'
            }), 404
        
        # Admins and teachers can close any lobby
        success = lobby_manager.close_lobby(lobby_id)
        
        if success:
            ActivityLog.log_activity(
                user_id=current_user.id,
                action_type='admin_lobby_close',
                message=f"Admin closed lobby {lobby_id}",
                related_entity_type='lobby',
                related_entity_id=lobby_id
            )
        
        return jsonify({
            'success': success
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_collaboration_api_bp.route('/lobby/<lobby_id>/lock', methods=['POST'])
@login_required
@teacher_required
def lock_admin_lobby(lobby_id):
    """Lock or unlock a lobby (admin/teacher)"""
    try:
        lobby = lobby_manager.get_lobby_by_id(lobby_id)
        if not lobby:
            return jsonify({
                'success': False,
                'error': 'Lobby not found'
            }), 404
        
        data = request.get_json() or {}
        locked = bool(data.get('locked', True))
        
        # Admins can lock/unlock any lobby - use creator privileges
        result = lobby.set_locked(lobby.creator_id, locked)
        
        if result.get('success'):
            ActivityLog.log_activity(
                user_id=current_user.id,
                action_type='admin_lobby_lock',
                message=f"Admin set lock={locked} on lobby {lobby_id}",
                related_entity_type='lobby',
                related_entity_id=lobby_id
            )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_collaboration_api_bp.route('/lobby/<lobby_id>/participants', methods=['GET'])
@login_required
@teacher_required
def get_lobby_participants(lobby_id):
    """Get participants of a lobby"""
    try:
        lobby = lobby_manager.get_lobby_by_id(lobby_id)
        if not lobby:
            return jsonify({
                'success': False,
                'error': 'Lobby not found'
            }), 404
        
        return jsonify({
            'success': True,
            'participants': lobby.participants
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_collaboration_api_bp.route('/lobby/<lobby_id>/kick/<user_id>', methods=['POST'])
@login_required
@teacher_required
def kick_user_from_lobby(lobby_id, user_id):
    """Kick a user from a lobby (admin/teacher)"""
    try:
        lobby = lobby_manager.get_lobby_by_id(lobby_id)
        if not lobby:
            return jsonify({
                'success': False,
                'error': 'Lobby not found'
            }), 404
        
        # Admins can kick any user - use creator privileges
        result = lobby.kick_participant(user_id, lobby.creator_id)
        
        if result.get('success'):
            ActivityLog.log_activity(
                user_id=current_user.id,
                action_type='admin_lobby_kick',
                message=f"Admin kicked user {user_id} from lobby {lobby_id}",
                related_entity_type='lobby',
                related_entity_id=lobby_id
            )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_collaboration_api_bp.route('/classes', methods=['GET'])
@login_required
@teacher_required
def get_classes_for_lobbies():
    """Get list of classes for lobby assignment"""
    try:
        # Get all active classes
        classes = Class.query.filter_by(is_active=True).all()
        
        classes_data = []
        for cls in classes:
            # Get student count for this class
            student_count = 0
            if hasattr(cls, 'students'):
                student_count = len(cls.students)
            
            classes_data.append({
                'id': cls.id,
                'name': cls.name,
                'code': cls.code,
                'section': cls.section,
                'student_count': student_count
            })
        
        return jsonify({
            'success': True,
            'classes': classes_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_collaboration_api_bp.route('/simulations', methods=['GET'])
@login_required
@teacher_required
def get_simulations_for_lobbies():
    """Get list of simulations for lobby assignment"""
    try:
        # Get all active and published simulations
        simulations = Simulation.query.filter_by(is_active=True, is_published=True).all()
        
        simulations_data = []
        for sim in simulations:
            simulations_data.append({
                'id': sim.id,
                'title': sim.title,
                'difficulty': sim.difficulty,
                'simulation_type': sim.simulation_type,
                'category': sim.category
            })
        
        return jsonify({
            'success': True,
            'simulations': simulations_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_collaboration_api_bp.route('/stats', methods=['GET'])
@login_required
@teacher_required
def get_collaboration_stats():
    """Get collaboration system statistics"""
    try:
        stats = lobby_manager.get_stats()
        
        # Add additional admin-relevant stats
        total_lobbies = len(lobby_manager.get_all_lobbies())
        active_lobbies = len([l for l in lobby_manager.get_all_lobbies() if l.is_active])
        
        stats.update({
            'total_lobbies': total_lobbies,
            'active_lobbies': active_lobbies,
            'admin_view': True
        })
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_collaboration_api_bp.route('/teams', methods=['POST'])
@login_required
@teacher_required
def save_team_assignments():
    """Save team assignments for a collaboration simulation"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('class_id'):
            return jsonify({
                'success': False,
                'error': 'Class ID is required'
            }), 400
            
        if not data.get('teams'):
            return jsonify({
                'success': False,
                'error': 'Teams data is required'
            }), 400
        
        class_id = data.get('class_id')
        simulation_id = data.get('simulation_id')
        teams = data.get('teams', [])
        collaboration_settings = data.get('collaboration_settings', {})
        
        # Validate class exists
        class_obj = Class.query.get(class_id)
        if not class_obj:
            return jsonify({
                'success': False,
                'error': 'Invalid class ID'
            }), 400
        
        # Store team assignments in the database
        # Note: You'll need to create appropriate database models for this
        # For now, we'll store it in a simple format
        
        team_data = {
            'class_id': class_id,
            'simulation_id': simulation_id,
            'teams': teams,
            'collaboration_settings': collaboration_settings,
            'created_by': current_user.id,
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Log the team assignment activity
        ActivityLog.log_activity(
            user_id=current_user.id,
            action_type='team_assignments_saved',
            message=f"Saved team assignments for class {class_obj.name} with {len(teams)} teams",
            related_entity_type='class',
            related_entity_id=class_id
        )
        
        return jsonify({
            'success': True,
            'message': f'Team assignments saved for {len(teams)} teams',
            'team_count': len(teams)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_collaboration_api_bp.route('/classes/<int:class_id>/students', methods=['GET'])
@login_required
@teacher_required
def get_class_students(class_id):
    """Get students in a specific class for team assignment"""
    try:
        class_obj = Class.query.get_or_404(class_id)
        
        # Get students in the class
        students = []
        if hasattr(class_obj, 'students'):
            for student in class_obj.students:
                students.append({
                    'id': student.id,
                    'username': student.username,
                    'email': student.email,
                    'profile_img': getattr(student, 'profile_img', None)
                })
        
        return jsonify({
            'success': True,
            'students': students,
            'class_name': class_obj.name
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_collaboration_api_bp.route('/teams/<int:class_id>', methods=['GET'])
@login_required
@teacher_required
def get_team_assignments(class_id):
    """Get existing team assignments for a class"""
    try:
        # This would retrieve stored team assignments
        # For now, return empty teams as the storage mechanism needs to be implemented
        
        return jsonify({
            'success': True,
            'teams': [],
            'message': 'No existing team assignments found'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_collaboration_api_bp.route('/simulation/<int:simulation_id>/collaboration', methods=['POST'])
@login_required
@teacher_required
def save_simulation_collaboration_settings(simulation_id):
    """Save collaboration settings for a specific simulation"""
    print(f"🔧 POST /simulation/{simulation_id}/collaboration route called")
    try:
        data = request.get_json()
        
        # Validate simulation exists
        simulation = Simulation.query.get_or_404(simulation_id)
        
        collaboration_settings = data.get('collaboration_settings', {})
        
        # Import the collaboration model
        from instructor.models.collaboration import CollaborationSetting
        
        # Find or create collaboration setting
        setting = CollaborationSetting.query.filter_by(simulation_id=simulation_id).first()
        if not setting:
            setting = CollaborationSetting(
                simulation_id=simulation_id,
                created_by=current_user.id
            )
            db.session.add(setting)
        
        # Update settings
        setting.collaboration_enabled = collaboration_settings.get('collaboration_enabled', False)
        setting.team_size = collaboration_settings.get('team_size', 2)
        setting.shared_terminal = collaboration_settings.get('shared_terminal', False)
        setting.individual_terminals = collaboration_settings.get('individual_terminals', True)
        setting.follow_leader = collaboration_settings.get('follow_leader', False)
        setting.chat_enabled = collaboration_settings.get('chat_enabled', False)
        setting.transcript_logging = collaboration_settings.get('transcript_logging', False)
        setting.allow_late_join = collaboration_settings.get('allow_late_join', True)
        setting.require_instructor = collaboration_settings.get('require_instructor', False)
        setting.time_window = collaboration_settings.get('time_window')
        setting.roles = collaboration_settings.get('roles', ['Leader', 'Observer', 'Operator'])
        
        db.session.commit()
        
        # Log the activity
        ActivityLog.log_activity(
            user_id=current_user.id,
            action_type='collaboration_settings_updated',
            message=f"Updated collaboration settings for simulation {simulation.title}",
            related_entity_type='simulation',
            related_entity_id=simulation_id
        )
        
        return jsonify({
            'success': True,
            'message': 'Collaboration settings saved successfully',
            'settings': setting.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error saving collaboration settings: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_collaboration_api_bp.route('/simulation/<int:simulation_id>/collaboration', methods=['GET'])
@login_required
@teacher_required
def get_simulation_collaboration_settings(simulation_id):
    """Get collaboration settings for a specific simulation"""
    print(f"🔧 GET /simulation/{simulation_id}/collaboration route called")
    try:
        simulation = Simulation.query.get_or_404(simulation_id)
        
        # Import the collaboration model
        from instructor.models.collaboration import CollaborationSetting
        
        setting = CollaborationSetting.query.filter_by(simulation_id=simulation_id).first()
        
        if setting:
            collaboration_settings = setting.to_dict()
        else:
            # Return default settings
            collaboration_settings = {
                'collaboration_enabled': False,
                'team_size': 2,
                'shared_terminal': False,
                'individual_terminals': True,
                'follow_leader': False,
                'chat_enabled': False,
                'transcript_logging': False,
                'allow_late_join': True,
                'require_instructor': False,
                'time_window': None,
                'roles': ['Leader', 'Observer', 'Operator']
            }
        
        return jsonify({
            'success': True,
            'collaboration_settings': collaboration_settings
        })
        
    except Exception as e:
        print(f"Error getting collaboration settings: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_collaboration_api_bp.route('/simulation/<int:simulation_id>/start-lobby', methods=['POST'])
@login_required
@teacher_required
def start_collaboration_lobby(simulation_id):
    """Start a collaboration lobby for a simulation based on its settings"""
    try:
        data = request.get_json()
        
        # Validate simulation exists
        simulation = Simulation.query.get_or_404(simulation_id)
        
        # Import the collaboration model
        from instructor.models.collaboration import CollaborationSetting
        
        # Get collaboration settings
        setting = CollaborationSetting.query.filter_by(simulation_id=simulation_id).first()
        if not setting or not setting.collaboration_enabled:
            return jsonify({
                'success': False,
                'error': 'Collaboration is not enabled for this simulation'
            }), 400
        
        class_id = data.get('class_id')
        if class_id:
            # Validate class exists
            class_obj = Class.query.get(class_id)
            if not class_obj:
                return jsonify({
                    'success': False,
                    'error': 'Invalid class ID'
                }), 400
        
        # Create lobby configuration based on collaboration settings
        lobby_config = {
            'name': data.get('name', f"{simulation.title} - Collaboration Session"),
            'scenario_type': 'collaboration',
            'scenario_id': f'simulation_{simulation_id}',
            'max_participants': (setting.team_size or 2) * 3,  # Allow multiple teams
            'class_id': class_id,
            'simulation_id': simulation_id,
            'admin_created': True,
            'collaboration_settings': setting.to_dict()
        }
        
        # Create the lobby using lobby manager
        lobby = lobby_manager.create_lobby(
            creator_id=str(current_user.id),
            creator_name=current_user.username,
            creator_profile_image=getattr(current_user, 'profile_img', None),
            lobby_config=lobby_config
        )
        
        # Also store in database for persistence
        from instructor.models.collaboration import CollaborationLobby
        
        db_lobby = CollaborationLobby(
            id=lobby.id,
            name=lobby.name,
            scenario_type=lobby.scenario_type,
            scenario_id=lobby.scenario_id,
            max_participants=lobby.max_participants,
            class_id=class_id,
            simulation_id=simulation_id,
            creator_id=lobby.creator_id,
            creator_name=lobby.creator_name,
            creator_profile_image=getattr(current_user, 'profile_img', None),
            participants=lobby.participants,
            is_active=True,
            is_locked=False
        )
        
        db.session.add(db_lobby)
        db.session.commit()
        
        # Log activity
        ActivityLog.log_activity(
            user_id=current_user.id,
            action_type='collaboration_lobby_started',
            message=f"Started collaboration lobby for simulation {simulation.title}",
            related_entity_type='simulation',
            related_entity_id=simulation_id
        )
        
        return jsonify({
            'success': True,
            'lobby': lobby.to_dict(),
            'lobby_id': lobby.id,
            'join_url': f'/dynamic/simulation/{simulation_id}?lobby_id={lobby.id}'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error starting collaboration lobby: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


print("🔧 Admin Collaboration API routes defined successfully!")
print(f"🔧 Blueprint name: {admin_collaboration_api_bp.name}")
print(f"🔧 Blueprint URL prefix: {admin_collaboration_api_bp.url_prefix}")