"""
API routes for collaborative troubleshooting lobby management
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from services.troubleshooting_lobbies import lobby_manager
from admin.models.class_model import Class
from admin.models.activity_log import ActivityLog

# Create blueprint for collaborative troubleshooting API
collaborative_troubleshooting_api_bp = Blueprint(
    'collaborative_troubleshooting_api', 
    __name__, 
    url_prefix='/api/troubleshooting/collaborative'
)

@collaborative_troubleshooting_api_bp.route('/lobbies', methods=['GET'])
@login_required
def get_public_lobbies():
    """Get available public lobbies"""
    try:
        lobbies = lobby_manager.get_public_lobbies()
        # Filter by class membership when lobby is class-scoped
        try:
            user_classes = getattr(current_user, 'enrolled_classes', None)
            class_ids = [c.id for c in user_classes.all()] if user_classes is not None and hasattr(user_classes, 'all') else []
            lobbies = [l for l in lobbies if (l.get('class_id') is None or l.get('class_id') in class_ids)]
        except Exception:
            # If we cannot resolve classes, return unfiltered
            pass
        return jsonify({
            'success': True,
            'lobbies': lobbies
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@collaborative_troubleshooting_api_bp.route('/lobby/<lobby_id>', methods=['GET'])
@login_required
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
            'lobby': lobby.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@collaborative_troubleshooting_api_bp.route('/my-lobby', methods=['GET'])
@login_required
def get_my_lobby():
    """Get current user's lobby"""
    try:
        lobby = lobby_manager.get_user_lobby(str(current_user.id))
        if not lobby:
            return jsonify({
                'success': False,
                'error': 'Not in any lobby'
            })
        
        return jsonify({
            'success': True,
            'lobby': lobby.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# REMOVED: User lobby creation - only admins can create lobbies now
# @collaborative_troubleshooting_api_bp.route('/lobby', methods=['POST'])
# @login_required
# def create_lobby():
#     """Create a new collaborative troubleshooting lobby - DISABLED FOR USERS"""
#     return jsonify({
#         'success': False,
#         'error': 'Lobby creation is restricted to administrators only. Please contact your teacher to create collaboration sessions.'
#     }), 403

@collaborative_troubleshooting_api_bp.route('/lobby/<lobby_id>/join', methods=['POST'])
@login_required
def join_lobby(lobby_id):
    """Join an existing lobby"""
    try:
        # Enforce class scoping if lobby has class_id
        lobby = lobby_manager.get_lobby_by_id(lobby_id)
        if not lobby:
            return jsonify({'success': False, 'error': 'Lobby not found'}), 404
        if lobby.class_id:
            # Validate current_user is enrolled in class
            user_classes = getattr(current_user, 'enrolled_classes', None)
            is_member = False
            try:
                if user_classes is not None and user_classes.filter_by(id=lobby.class_id).first():
                    is_member = True
            except Exception:
                # Fallback: query Class and check association if available
                cls = Class.query.get(lobby.class_id)
                if cls and hasattr(cls, 'students'):
                    try:
                        is_member = current_user in cls.students
                    except Exception:
                        is_member = False
            if not is_member:
                return jsonify({'success': False, 'error': 'Class membership required to join this session'}), 403

        result = lobby_manager.join_lobby(
            lobby_id=lobby_id,
            user_id=str(current_user.id),
            user_info={'username': current_user.username}
        )
        
        if result['success']:
            ActivityLog.log_activity(
                user_id=current_user.id,
                action_type='lobby_join',
                message=f"Joined lobby {lobby_id}",
                related_entity_type='lobby',
                related_entity_id=None
            )
            return jsonify({
                'success': True,
                'lobby': result['lobby'].to_dict()
            })
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@collaborative_troubleshooting_api_bp.route('/lobby/leave', methods=['POST'])
@login_required
def leave_lobby():
    """Leave current lobby"""
    try:
        success = lobby_manager.leave_lobby(str(current_user.id))
        if success:
            ActivityLog.log_activity(
                user_id=current_user.id,
                action_type='lobby_leave',
                message=f"Left current lobby",
                related_entity_type='lobby',
                related_entity_id=None
            )
        
        return jsonify({
            'success': success
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@collaborative_troubleshooting_api_bp.route('/stats', methods=['GET'])
@login_required
def get_lobby_stats():
    """Get lobby system statistics"""
    try:
        stats = lobby_manager.get_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@collaborative_troubleshooting_api_bp.route('/lobby/<lobby_id>/close', methods=['POST'])
@login_required
def close_lobby(lobby_id):
    """Close a lobby (owner/moderator)"""
    try:
        lobby = lobby_manager.get_lobby_by_id(lobby_id)
        if not lobby:
            return jsonify({'success': False, 'error': 'Lobby not found'}), 404
        role = lobby.participants.get(str(current_user.id), {}).get('role')
        if role not in ('creator', 'moderator'):
            return jsonify({'success': False, 'error': 'Moderator or owner permissions required'}), 403
        ok = lobby_manager.close_lobby(lobby_id)
        if ok:
            ActivityLog.log_activity(current_user.id, 'lobby_close', f"Closed lobby {lobby_id}", 'lobby', None)
        return jsonify({'success': ok}), (200 if ok else 400)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@collaborative_troubleshooting_api_bp.route('/lobby/<lobby_id>/lock', methods=['POST'])
@login_required
def lock_lobby(lobby_id):
    """Lock or unlock a lobby (owner/moderator)"""
    try:
        lobby = lobby_manager.get_lobby_by_id(lobby_id)
        if not lobby:
            return jsonify({'success': False, 'error': 'Lobby not found'}), 404
        data = request.get_json() or {}
        locked = bool(data.get('locked', True))
        result = lobby.set_locked(str(current_user.id), locked)
        if result.get('success'):
            ActivityLog.log_activity(current_user.id, 'lobby_lock', f"Set lock={locked} on lobby {lobby_id}", 'lobby', None)
        return jsonify(result), (200 if result.get('success') else 403)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@collaborative_troubleshooting_api_bp.route('/lobby/<lobby_id>/kick', methods=['POST'])
@login_required
def kick_user(lobby_id):
    """Kick a user from a lobby (owner/moderator)"""
    try:
        lobby = lobby_manager.get_lobby_by_id(lobby_id)
        if not lobby:
            return jsonify({'success': False, 'error': 'Lobby not found'}), 404
        data = request.get_json() or {}
        target_user_id = str(data.get('user_id'))
        if not target_user_id:
            return jsonify({'success': False, 'error': 'Missing user_id'}), 400
        result = lobby.kick_participant(target_user_id, str(current_user.id))
        if result.get('success'):
            ActivityLog.log_activity(current_user.id, 'lobby_kick', f"Kicked user {target_user_id} from lobby {lobby_id}", 'lobby', None)
        return jsonify(result), (200 if result.get('success') else 403)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@collaborative_troubleshooting_api_bp.route('/lobby/<lobby_id>/assign-moderator', methods=['POST'])
@login_required
def assign_moderator(lobby_id):
    """Assign moderator role to a participant (owner only)"""
    try:
        lobby = lobby_manager.get_lobby_by_id(lobby_id)
        if not lobby:
            return jsonify({'success': False, 'error': 'Lobby not found'}), 404
        data = request.get_json() or {}
        target_user_id = str(data.get('user_id'))
        if not target_user_id:
            return jsonify({'success': False, 'error': 'Missing user_id'}), 400
        result = lobby.assign_moderator(target_user_id, str(current_user.id))
        if result.get('success'):
            ActivityLog.log_activity(current_user.id, 'lobby_assign_mod', f"Assigned moderator to {target_user_id} in lobby {lobby_id}", 'lobby', None)
        return jsonify(result), (200 if result.get('success') else 403)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@collaborative_troubleshooting_api_bp.route('/lobby/<lobby_id>/revoke-moderator', methods=['POST'])
@login_required
def revoke_moderator(lobby_id):
    """Revoke moderator role from a participant (owner only)"""
    try:
        lobby = lobby_manager.get_lobby_by_id(lobby_id)
        if not lobby:
            return jsonify({'success': False, 'error': 'Lobby not found'}), 404
        data = request.get_json() or {}
        target_user_id = str(data.get('user_id'))
        if not target_user_id:
            return jsonify({'success': False, 'error': 'Missing user_id'}), 400
        result = lobby.revoke_moderator(target_user_id, str(current_user.id))
        if result.get('success'):
            ActivityLog.log_activity(current_user.id, 'lobby_revoke_mod', f"Revoked moderator from {target_user_id} in lobby {lobby_id}", 'lobby', None)
        return jsonify(result), (200 if result.get('success') else 403)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
