"""
Gamified Topology Routes
=======================

Enhanced routes for the gamified topology simulation system with:
- Difficulty-based scenarios
- Progress tracking
- Achievement system
- Leaderboards
- Interactive tutorials
"""

from flask import Blueprint, render_template, request, jsonify, session
from flask_login import current_user
from datetime import datetime
import json

from utils.auth_decorators import user_login_required
from services.gamified_topology_service import GamifiedTopologyService
from user.models.topology_progress import TopologyProgress
from admin.models.topology import Topology
from admin import db

# Create the blueprint
gamified_topology_bp = Blueprint('gamified_topology', __name__, url_prefix='/topology')

# Initialize the service
topology_service = GamifiedTopologyService()


@gamified_topology_bp.route('/')
@user_login_required
def topology_simulation():
    """Main topology simulation page with gamified interface"""
    try:
        user_id = current_user.id
        
        # Get all available scenarios with user progress
        scenarios = topology_service.get_available_scenarios(user_id)
        
        # Get user's overall progress
        user_progress = topology_service.get_user_progress(user_id)
        
        # Get recent activity
        recent_progress = TopologyProgress.query.filter_by(user_id=user_id)\
            .order_by(TopologyProgress.updated_at.desc()).limit(5).all()
        
        # Format recent activity for display
        recent_activity = []
        for progress in recent_progress:
            if progress.last_completed:
                recent_activity.append({
                    'topology_type': progress.topology_type,
                    'difficulty': progress.difficulty,
                    'score': progress.best_score,
                    'completed_at': progress.last_completed.strftime('%Y-%m-%d %H:%M'),
                    'attempt_count': progress.completion_count
                })
        
        return render_template(
            'user/gamified_topology.html',
            scenarios=scenarios,
            user_progress=user_progress,
            recent_activity=recent_activity,
            achievements=topology_service.ACHIEVEMENTS
        )
        
    except Exception as e:
        current_app.logger.error(f"Error loading topology simulation: {str(e)}")
        return render_template(
            'user/gamified_topology.html',
            scenarios=[],
            user_progress={},
            recent_activity=[],
            achievements={},
            error="Failed to load topology simulation"
        )


@gamified_topology_bp.route('/api/scenarios')
@user_login_required
def get_scenarios():
    """API endpoint to get all available scenarios"""
    try:
        user_id = current_user.id
        scenarios = topology_service.get_available_scenarios(user_id)
        
        return jsonify({
            'success': True,
            'scenarios': scenarios
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@gamified_topology_bp.route('/api/scenario/<scenario_id>/start', methods=['POST'])
@user_login_required
def start_scenario(scenario_id):
    """Start a specific topology scenario"""
    try:
        user_id = current_user.id
        
        # Parse scenario ID (format: topology_type_difficulty)
        parts = scenario_id.split('_')
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'error': 'Invalid scenario ID format'
            }), 400
        
        topology_type = '_'.join(parts[:-1])  # Handle multi-word topology types
        difficulty = parts[-1]
        
        # Start the scenario
        result = topology_service.start_scenario(user_id, topology_type, difficulty)
        
        return jsonify({
            'success': True,
            'scenario': result
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to start scenario: {str(e)}'
        }), 500


@gamified_topology_bp.route('/api/scenario/<scenario_id>/validate', methods=['POST'])
@user_login_required
def validate_scenario(scenario_id):
    """Validate a topology scenario submission"""
    try:
        user_id = current_user.id
        data = request.get_json()
        
        # Parse scenario ID
        parts = scenario_id.split('_')
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'error': 'Invalid scenario ID format'
            }), 400
        
        topology_type = '_'.join(parts[:-1])
        difficulty = parts[-1]
        
        # Extract validation data
        devices = data.get('devices', [])
        connections = data.get('connections', [])
        completion_time = data.get('completion_time')  # in seconds
        start_time = data.get('start_time')
        
        # Calculate completion time if not provided
        if not completion_time and start_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                completion_time = int((datetime.utcnow() - start_dt).total_seconds())
            except:
                completion_time = None
        
        # Validate the topology
        result = topology_service.validate_topology(
            user_id, topology_type, difficulty, devices, connections, completion_time
        )
        
        return jsonify({
            'success': True,
            'validation': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Validation failed: {str(e)}'
        }), 500


@gamified_topology_bp.route('/api/progress')
@user_login_required
def get_user_progress():
    """Get comprehensive user progress data"""
    try:
        user_id = current_user.id
        progress_data = topology_service.get_user_progress(user_id)
        
        return jsonify({
            'success': True,
            'progress': progress_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@gamified_topology_bp.route('/api/leaderboard')
@user_login_required
def get_leaderboard():
    """Get leaderboard data"""
    try:
        topology_type = request.args.get('topology_type')
        difficulty = request.args.get('difficulty')
        limit = int(request.args.get('limit', 10))
        
        leaderboard = topology_service.get_leaderboard(topology_type, difficulty, limit)
        
        return jsonify({
            'success': True,
            'leaderboard': leaderboard
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@gamified_topology_bp.route('/api/achievements')
@user_login_required
def get_achievements():
    """Get available achievements and user's earned achievements"""
    try:
        user_id = current_user.id
        
        # Get all achievements
        all_achievements = topology_service.ACHIEVEMENTS
        
        # Get user's earned achievements
        earned_achievements = topology_service._get_user_achievements(user_id)
        earned_ids = [ach.get('id') for ach in earned_achievements if 'id' in ach]
        
        # Mark which achievements are earned
        achievements_with_status = {}
        for ach_id, achievement in all_achievements.items():
            achievements_with_status[ach_id] = {
                **achievement,
                'earned': ach_id in earned_ids
            }
        
        return jsonify({
            'success': True,
            'achievements': achievements_with_status,
            'earned_count': len(earned_achievements),
            'total_count': len(all_achievements)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@gamified_topology_bp.route('/api/scenarios/<scenario_id>/tutorial')
@user_login_required
def get_scenario_tutorial(scenario_id):
    """Get tutorial steps for a specific scenario"""
    try:
        # Parse scenario ID
        parts = scenario_id.split('_')
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'error': 'Invalid scenario ID format'
            }), 400
        
        topology_type = '_'.join(parts[:-1])
        difficulty = parts[-1]
        
        # Get scenario data
        if topology_type not in topology_service.topology_scenarios:
            return jsonify({
                'success': False,
                'error': 'Topology type not found'
            }), 404
        
        if difficulty not in topology_service.topology_scenarios[topology_type]:
            return jsonify({
                'success': False,
                'error': 'Difficulty not found'
            }), 404
        
        scenario = topology_service.topology_scenarios[topology_type][difficulty]
        
        return jsonify({
            'success': True,
            'tutorial': {
                'steps': scenario['tutorial_steps'],
                'estimated_time': scenario['time_limit'] // 60,  # Convert to minutes
                'difficulty': difficulty,
                'requirements': scenario['requirements']
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@gamified_topology_bp.route('/api/progress/mark-tutorial-complete', methods=['POST'])
@user_login_required
def mark_tutorial_complete():
    """Mark tutorial as completed for a scenario"""
    try:
        user_id = current_user.id
        data = request.get_json()
        scenario_id = data.get('scenario_id')
        
        if not scenario_id:
            return jsonify({
                'success': False,
                'error': 'Scenario ID required'
            }), 400
        
        # Parse scenario ID
        parts = scenario_id.split('_')
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'error': 'Invalid scenario ID format'
            }), 400
        
        topology_type = '_'.join(parts[:-1])
        difficulty = parts[-1]
        
        # Find or create progress record
        progress = TopologyProgress.query.filter_by(
            user_id=user_id,
            topology_type=topology_type,
            difficulty=difficulty
        ).first()
        
        if not progress:
            progress = TopologyProgress(
                user_id=user_id,
                topology_type=topology_type,
                difficulty=difficulty
            )
            db.session.add(progress)
        
        progress.tutorial_completed = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tutorial marked as completed'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@gamified_topology_bp.route('/api/hint', methods=['POST'])
@user_login_required
def get_hint():
    """Get a hint for the current scenario"""
    try:
        user_id = current_user.id
        data = request.get_json()
        scenario_id = data.get('scenario_id')
        current_step = data.get('current_step', 0)
        
        if not scenario_id:
            return jsonify({
                'success': False,
                'error': 'Scenario ID required'
            }), 400
        
        # Parse scenario ID
        parts = scenario_id.split('_')
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'error': 'Invalid scenario ID format'
            }), 400
        
        topology_type = '_'.join(parts[:-1])
        difficulty = parts[-1]
        
        # Get scenario
        scenario = topology_service.topology_scenarios.get(topology_type, {}).get(difficulty)
        if not scenario:
            return jsonify({
                'success': False,
                'error': 'Scenario not found'
            }), 404
        
        # Get hint based on current step
        tutorial_steps = scenario.get('tutorial_steps', [])
        if current_step < len(tutorial_steps):
            hint = tutorial_steps[current_step]
        else:
            # Generic hints based on topology type
            generic_hints = {
                'point-to-point': "Remember: point-to-point needs exactly 2 devices with 1 connection",
                'star': "Tip: One device should be in the center connected to all others",
                'mesh': "Hint: In a mesh, every device connects to every other device",
                'bus': "Remember: Bus topology forms a single line of connections",
                'ring': "Tip: Each device should have exactly 2 connections forming a circle",
                'tree': "Hint: Tree topology has a hierarchical structure with no loops",
                'hybrid': "Remember: Combine different topology patterns effectively"
            }
            hint = generic_hints.get(topology_type, "Check the requirements and try different approaches")
        
        # Track hint usage
        progress = TopologyProgress.query.filter_by(
            user_id=user_id,
            topology_type=topology_type,
            difficulty=difficulty
        ).first()
        
        if progress:
            progress.hints_used += 1
            db.session.commit()
        
        return jsonify({
            'success': True,
            'hint': hint,
            'hints_used': progress.hints_used if progress else 1
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@gamified_topology_bp.route('/api/reset-progress', methods=['POST'])
@user_login_required
def reset_user_progress():
    """Reset user's progress (for testing or fresh start)"""
    try:
        user_id = current_user.id
        data = request.get_json()
        confirm = data.get('confirm', False)
        
        if not confirm:
            return jsonify({
                'success': False,
                'error': 'Confirmation required to reset progress'
            }), 400
        
        # Delete all progress records for the user
        TopologyProgress.query.filter_by(user_id=user_id).delete()
        
        # Also delete topology scores
        from user.models import Score
        Score.query.filter_by(user_id=user_id, category='topology').delete()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Progress reset successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Error handlers
@gamified_topology_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404


@gamified_topology_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500