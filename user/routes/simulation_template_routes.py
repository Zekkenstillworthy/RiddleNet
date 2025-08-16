from flask import Blueprint, render_template, request, jsonify, session
from datetime import datetime
import json

# Create blueprint for simulation template
simulation_template_bp = Blueprint('simulation_template', __name__, 
                                 template_folder='../templates', 
                                 url_prefix='/simulation-template')

@simulation_template_bp.route('/')
def simulation_template():
    """Main simulation template page following troubleshoot.html patterns"""
    try:
        # Sample simulation data - replace with actual data from database
        simulation_data = {
            'id': 'template-001',
            'title': 'Interactive Simulation Template',
            'description': 'A comprehensive template following troubleshoot.html patterns',
            'simulation_type': 'Template',
            'category': 'Educational',
            'difficulty': 'Medium',
            'estimated_duration': '15-30 minutes',
            'learning_objectives': [
                'Understand simulation interface patterns',
                'Practice with interactive tools',
                'Learn performance tracking features',
                'Master collaborative elements'
            ],
            'step_definitions': [
                {
                    'step': 1,
                    'title': 'Getting Started',
                    'description': 'Select your preferred difficulty level and scenario',
                    'validation': 'scenario_selected'
                },
                {
                    'step': 2,
                    'title': 'Tool Selection',
                    'description': 'Choose appropriate tools from the device palette',
                    'validation': 'tool_selected'
                },
                {
                    'step': 3,
                    'title': 'Interactive Mode',
                    'description': 'Switch between select, draw, and connect modes',
                    'validation': 'mode_changed'
                },
                {
                    'step': 4,
                    'title': 'Canvas Interaction',
                    'description': 'Interact with the canvas using selected tools',
                    'validation': 'canvas_interaction'
                },
                {
                    'step': 5,
                    'title': 'Performance Review',
                    'description': 'Review your performance metrics and achievements',
                    'validation': 'performance_reviewed'
                }
            ],
            'validation_rules': {
                'scenario_selected': {
                    'type': 'user_action',
                    'required': True,
                    'points': 10
                },
                'tool_selected': {
                    'type': 'user_action', 
                    'required': True,
                    'points': 15
                },
                'mode_changed': {
                    'type': 'user_action',
                    'required': True,
                    'points': 20
                },
                'canvas_interaction': {
                    'type': 'user_action',
                    'required': True,
                    'points': 25
                },
                'performance_reviewed': {
                    'type': 'user_action',
                    'required': False,
                    'points': 10
                }
            },
            'scoring_config': {
                'total_points': 80,
                'passing_score': 60,
                'time_bonus': True,
                'accuracy_bonus': True
            }
        }
        
        return render_template('user/simulation_template.html', 
                             simulation=simulation_data,
                             user={'username': 'demo_user', 'id': 1})
                             
    except Exception as e:
        print(f"Error loading simulation template: {str(e)}")
        return render_template('user/simulation_template.html',
                             simulation=None,
                             user={'username': 'demo_user', 'id': 1},
                             error="Failed to load simulation data")

@simulation_template_bp.route('/api/progress', methods=['POST'])
def update_progress():
    """Update simulation progress via API"""
    try:
        data = request.get_json()
        
        # Extract progress data
        action = data.get('action')
        step = data.get('step', 1)
        score = data.get('score', 0)
        progress = data.get('progress', 0)
        
        # In a real implementation, save to database
        # For now, return success response with updated data
        
        response_data = {
            'success': True,
            'message': f'Progress updated: {action}',
            'data': {
                'current_score': score,
                'current_progress': progress,
                'current_step': step,
                'timestamp': datetime.utcnow().isoformat()
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@simulation_template_bp.route('/api/hint', methods=['POST'])
def get_hint():
    """Get contextual hints for current simulation state"""
    try:
        data = request.get_json()
        current_step = data.get('step', 1)
        current_mode = data.get('mode', 'select')
        difficulty = data.get('difficulty', 'medium')
        
        # Generate hints based on current state
        hints = {
            1: {
                'easy': "Click on a scenario card to get started. Begin with 'Beginner Challenge' for guided experience.",
                'medium': "Select a scenario that matches your skill level. Each has different complexity.",
                'hard': "Choose your challenge wisely. Advanced scenarios provide minimal guidance."
            },
            2: {
                'easy': "Look at the center section of the bottom palette. Click on any tool icon to select it.",
                'medium': "Tools in the center palette have different functions. Hover to see descriptions.",
                'hard': "Select appropriate tools based on your scenario requirements."
            },
            3: {
                'easy': "Try clicking the 'Select', 'Draw', or 'Connect' buttons in the left section of the palette.",
                'medium': "Each mode changes how you interact with the canvas. Experiment with different modes.",
                'hard': "Mode selection determines interaction behavior. Choose based on your current task."
            },
            4: {
                'easy': "Click anywhere on the canvas to interact. The action depends on your selected mode and tool.",
                'medium': "Canvas interactions are tracked. Your performance metrics update in real-time.",
                'hard': "Efficient canvas usage improves your score. Plan your actions carefully."
            },
            5: {
                'easy': "Check the performance sidebar on the right to see your progress and scores.",
                'medium': "Performance metrics help you understand your learning progress and efficiency.",
                'hard': "Use performance data to optimize your approach for future simulations."
            }
        }
        
        hint_text = hints.get(current_step, {}).get(difficulty, "Continue working through the simulation steps.")
        
        return jsonify({
            'success': True,
            'hint': hint_text,
            'step': current_step,
            'difficulty': difficulty
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@simulation_template_bp.route('/api/validate', methods=['POST'])
def validate_action():
    """Validate user actions against simulation rules"""
    try:
        data = request.get_json()
        action_type = data.get('action_type')
        action_data = data.get('action_data', {})
        
        # Validation logic based on action type
        validation_results = {
            'scenario_selected': {
                'valid': True,
                'points': 10,
                'message': 'Scenario selected successfully!'
            },
            'tool_selected': {
                'valid': True,
                'points': 15,
                'message': 'Tool selected! Ready for interaction.'
            },
            'mode_changed': {
                'valid': True,
                'points': 20,
                'message': 'Mode switched successfully!'
            },
            'canvas_interaction': {
                'valid': True,
                'points': 25,
                'message': 'Great interaction with the canvas!'
            },
            'performance_reviewed': {
                'valid': True,
                'points': 10,
                'message': 'Performance review completed.'
            }
        }
        
        result = validation_results.get(action_type, {
            'valid': False,
            'points': 0,
            'message': 'Unknown action type'
        })
        
        return jsonify({
            'success': True,
            'validation': result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@simulation_template_bp.route('/api/achievements', methods=['GET'])
def get_achievements():
    """Get available achievements for the simulation"""
    try:
        achievements = [
            {
                'id': 'first_steps',
                'name': 'First Steps',
                'description': 'Complete your first simulation scenario',
                'icon': 'fas fa-baby',
                'points': 50,
                'unlocked': False
            },
            {
                'id': 'tool_master',
                'name': 'Tool Master', 
                'description': 'Use all available tools in a single session',
                'icon': 'fas fa-tools',
                'points': 100,
                'unlocked': False
            },
            {
                'id': 'speed_demon',
                'name': 'Speed Demon',
                'description': 'Complete a scenario in under 5 minutes',
                'icon': 'fas fa-tachometer-alt',
                'points': 150,
                'unlocked': False
            },
            {
                'id': 'perfectionist',
                'name': 'Perfectionist',
                'description': 'Complete a scenario with 100% accuracy',
                'icon': 'fas fa-star',
                'points': 200,
                'unlocked': False
            },
            {
                'id': 'explorer',
                'name': 'Explorer',
                'description': 'Try all three difficulty levels',
                'icon': 'fas fa-compass',
                'points': 175,
                'unlocked': False
            }
        ]
        
        return jsonify({
            'success': True,
            'achievements': achievements
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
