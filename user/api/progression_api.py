"""
Progression API Routes - Handle progression and unlock mechanics
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from services.progression_service import progression_service

progression_api = Blueprint('progression_api', __name__)

@progression_api.route('/api/progression/simulation/<int:simulation_id>/unlock-status')
@login_required
def check_simulation_unlock_status(simulation_id):
    """Check if a simulation is unlocked for the current user"""
    try:        
        is_unlocked = progression_service.is_simulation_unlocked(
            current_user.id, 
            simulation_id, 
            None  # Learning paths removed
        )
        
        is_completed = progression_service.is_simulation_completed(
            current_user.id, 
            simulation_id
        )
        
        return jsonify({
            'success': True,
            'unlocked': is_unlocked,
            'completed': is_completed
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@progression_api.route('/api/progression/learning-path/<int:path_id>/progress')
@login_required
def get_learning_path_progress(path_id):
    """Get user's progress in a learning path - REMOVED"""
    return jsonify({
        'success': False,
        'error': 'Learning Paths feature has been removed'
    }), 404

@progression_api.route('/api/progression/simulation/<int:simulation_id>/complete', methods=['POST'])
@login_required
def mark_simulation_complete(simulation_id):
    """Mark a simulation as completed"""
    try:
        data = request.get_json() or {}
        score = data.get('score', 0)
        
        attempt = progression_service.mark_simulation_completed(
            current_user.id,
            simulation_id,
            score
        )
        
        if attempt:
            return jsonify({
                'success': True,
                'message': 'Simulation marked as completed',
                'attempt_id': attempt.id
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to mark simulation as completed'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@progression_api.route('/api/progression/learning-path/<int:path_id>/next')
@login_required
def get_next_simulation(path_id):
    """Get the next unlocked simulation in a learning path - REMOVED"""
    return jsonify({
        'success': False,
        'error': 'Learning Paths feature has been removed'
    }), 404

@progression_api.route('/api/progression/user/achievements')
@login_required
def get_user_achievements():
    """Get achievements for the current user"""
    try:
        achievements = progression_service.get_user_achievements(current_user.id)
        
        return jsonify({
            'success': True,
            'achievements': achievements
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
