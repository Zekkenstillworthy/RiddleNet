"""
Admin API routes for collaboration lobby management
Only admins/teachers can create and manage collaboration lobbies
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from services.troubleshooting_lobbies import lobby_manager
from admin.models.class_model import Class
from admin.models.activity_log import ActivityLog
from admin.models.simulation import Simulation
from utils.permission_decorators import admin_required, teacher_required
import json

# Create blueprint for admin collaboration API
admin_collaboration_api_bp = Blueprint(
    'admin_collaboration_api', 
    __name__, 
    url_prefix='/admin/api/collaboration'
)

@admin_collaboration_api_bp.route('/lobby', methods=['POST'])
@login_required
@teacher_required
def create_admin_lobby():
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
def get_admin_lobbies():
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
            classes_data.append({
                'id': cls.id,
                'name': cls.name,
                'code': cls.code,
                'section': cls.section
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