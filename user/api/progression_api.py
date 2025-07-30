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
        learning_path_id = request.args.get('learning_path_id', type=int)
        
        is_unlocked = progression_service.is_simulation_unlocked(
            current_user.id, 
            simulation_id, 
            learning_path_id
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
    """Get user's progress in a learning path"""
    try:
        progress = progression_service.get_user_progress_in_path(
            current_user.id, 
            path_id
        )
        
        return jsonify({
            'success': True,
            'progress': progress
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
    """Get the next unlocked simulation in a learning path"""
    try:
        next_sim = progression_service.get_next_unlocked_simulation(
            current_user.id, 
            path_id
        )
        
        if next_sim:
            return jsonify({
                'success': True,
                'simulation': {
                    'id': next_sim.id,
                    'title': next_sim.title,
                    'description': next_sim.description,
                    'url': f'/dynamic/simulation/{next_sim.id}'
                }
            })
        else:
            return jsonify({
                'success': True,
                'simulation': None,
                'message': 'No more simulations available'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
