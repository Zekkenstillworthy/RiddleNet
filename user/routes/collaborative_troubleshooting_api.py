"""
API routes for collaborative troubleshooting lobby management
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from services.troubleshooting_lobbies import lobby_manager

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

@collaborative_troubleshooting_api_bp.route('/lobby', methods=['POST'])
@login_required
def create_lobby():
    """Create a new collaborative troubleshooting lobby"""
    try:
        data = request.get_json()
        
        lobby_config = {
            'name': data.get('name', f"{current_user.username}'s Session"),
            'scenario_type': data.get('scenario_type', 'easy'),
            'scenario_id': data.get('scenario_id', 'network'),
            'max_participants': data.get('max_participants', 6)
        }
        
        lobby = lobby_manager.create_lobby(
            creator_id=str(current_user.id),
            creator_name=current_user.username,
            lobby_config=lobby_config
        )
        
        return jsonify({
            'success': True,
            'lobby': lobby.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@collaborative_troubleshooting_api_bp.route('/lobby/<lobby_id>/join', methods=['POST'])
@login_required
def join_lobby(lobby_id):
    """Join an existing lobby"""
    try:
        result = lobby_manager.join_lobby(
            lobby_id=lobby_id,
            user_id=str(current_user.id),
            user_info={'username': current_user.username}
        )
        
        if result['success']:
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
