from flask import Blueprint, render_template, request, jsonify, session
from datetime import datetime
import json

# Create blueprint for advanced simulation template
advanced_simulation_bp = Blueprint('advanced_simulation', __name__, 
                                 template_folder='../templates', 
                                 url_prefix='/advanced-simulation')

@advanced_simulation_bp.route('/')
def advanced_simulation():
    """Advanced simulation template following all troubleshoot.html patterns"""
    try:
        # Create test user for demo purposes
        test_user = type('User', (), {
            'username': 'advanced_user',
            'email': 'advanced@example.com',
            'id': 1
        })()
        
        # Advanced simulation data with comprehensive features
        simulation_data = {
            'id': 'advanced-sim-001',
            'title': 'Advanced Network Simulation',
            'description': 'Complete simulation environment with all troubleshoot.html features implemented',
            'simulation_type': 'Advanced',
            'category': 'Networking',
            'difficulty': 'Comprehensive',
            'estimated_duration': '45-60 minutes',
            'learning_objectives': [
                'Master complete simulation interface patterns',
                'Practice with advanced interactive tools',
                'Understand comprehensive performance tracking',
                'Experience full collaborative features',
                'Learn complex scenario management'
            ],
            'scenarios': [
                {
                    'id': 'basic-network',
                    'title': 'Basic Network Setup',
                    'difficulty': 'easy',
                    'description': 'Learn fundamental networking concepts',
                    'duration': '10-15 min',
                    'objectives': [
                        'Understand basic network components',
                        'Practice device placement',
                        'Learn connection basics'
                    ]
                },
                {
                    'id': 'troubleshooting',
                    'title': 'Network Troubleshooting',
                    'difficulty': 'medium',
                    'description': 'Diagnose and fix network issues',
                    'duration': '20-30 min',
                    'objectives': [
                        'Identify network problems',
                        'Apply troubleshooting methodology',
                        'Implement solutions'
                    ]
                },
                {
                    'id': 'advanced-topology',
                    'title': 'Advanced Network Design',
                    'difficulty': 'hard',
                    'description': 'Design complex enterprise networks',
                    'duration': '45-60 min',
                    'objectives': [
                        'Design scalable networks',
                        'Implement security best practices',
                        'Optimize performance'
                    ]
                }
            ],
            'device_library': [
                {
                    'category': 'Network Devices',
                    'devices': [
                        {'type': 'router', 'name': 'Router', 'icon': 'fa-route'},
                        {'type': 'switch', 'name': 'Switch', 'icon': 'fa-sitemap'},
                        {'type': 'pc', 'name': 'PC', 'icon': 'fa-desktop'},
                        {'type': 'server', 'name': 'Server', 'icon': 'fa-server'}
                    ]
                },
                {
                    'category': 'Connections',
                    'devices': [
                        {'type': 'ethernet', 'name': 'Ethernet', 'icon': 'fa-ethernet'},
                        {'type': 'fiber', 'name': 'Fiber', 'icon': 'fa-wifi'},
                        {'type': 'wireless', 'name': 'Wireless', 'icon': 'fa-broadcast-tower'}
                    ]
                }
            ],
            'tutorial_levels': {
                'easy': {
                    'guidance': 'Step-by-step instructions with highlights',
                    'hints': 'Frequent helpful hints with visual cues',
                    'validation': 'Real-time feedback and corrections',
                    'complexity': 'Basic concepts with guided practice'
                },
                'medium': {
                    'guidance': 'General direction with checkpoints',
                    'hints': 'Contextual hints available on request',
                    'validation': 'Checkpoint validation with feedback',
                    'complexity': 'Applied knowledge with some independence'
                },
                'hard': {
                    'guidance': 'Minimal guidance with final objectives',
                    'hints': 'Limited hints available on request',
                    'validation': 'Final validation with comprehensive review',
                    'complexity': 'Complex problem solving with minimal support'
                }
            },
            'achievement_system': [
                {
                    'id': 'first-device',
                    'name': 'First Device',
                    'description': 'Place your first device on the canvas',
                    'icon': 'fa-star',
                    'points': 10
                },
                {
                    'id': 'connection-master',
                    'name': 'Connection Master',
                    'description': 'Create 3 successful connections',
                    'icon': 'fa-link',
                    'points': 25
                },
                {
                    'id': 'speed-demon',
                    'name': 'Speed Demon',
                    'description': 'Complete actions at 10+ per minute',
                    'icon': 'fa-bolt',
                    'points': 50
                }
            ],
            'performance_metrics': {
                'tracking_enabled': True,
                'metrics': ['score', 'accuracy', 'speed', 'efficiency', 'hints_used', 'time_elapsed'],
                'scoring_system': {
                    'device_placed': 10,
                    'device_moved': 5,
                    'connection_created': 15,
                    'scenario_completed': 50,
                    'achievement_unlocked': 25
                }
            }
        }
        
        return render_template('user/advanced_simulation_template.html',
                             simulation=simulation_data,
                             user=test_user,
                             title="Advanced Simulation Template",
                             show_sidebar=True)
                             
    except Exception as e:
        print(f"Error loading advanced simulation template: {str(e)}")
        test_user = type('User', (), {
            'username': 'advanced_user',
            'email': 'advanced@example.com', 
            'id': 1
        })()
        
        return render_template('user/advanced_simulation_template.html',
                             simulation=None,
                             user=test_user,
                             title="Advanced Simulation Template",
                             show_sidebar=True,
                             error="Failed to load simulation data")

@advanced_simulation_bp.route('/api/progress', methods=['POST'])
def update_progress():
    """Enhanced progress tracking API with comprehensive metrics"""
    try:
        data = request.get_json()
        
        # Extract progress data with validation
        action = data.get('action', '')
        step = data.get('step', 1)
        score = data.get('score', 0)
        progress = data.get('progress', 0)
        metrics = data.get('metrics', {})
        
        # Validate action types
        valid_actions = [
            'device_placed', 'device_moved', 'connection_created', 
            'mode_changed', 'scenario_selected', 'tutorial_completed',
            'settings_changed', 'achievement_unlocked'
        ]
        
        if action not in valid_actions:
            return jsonify({
                'success': False,
                'error': 'Invalid action type'
            }), 400
        
        # Calculate score based on action
        score_mapping = {
            'device_placed': 10,
            'device_moved': 5,
            'connection_created': 15,
            'mode_changed': 2,
            'scenario_selected': 5,
            'tutorial_completed': 100,
            'achievement_unlocked': 25
        }
        
        calculated_score = score_mapping.get(action, 0)
        
        # Store progress in session (in production, save to database)
        if 'simulation_progress' not in session:
            session['simulation_progress'] = {
                'total_score': 0,
                'actions_completed': [],
                'current_step': 1,
                'start_time': datetime.now().isoformat(),
                'metrics': {
                    'accuracy': 100,
                    'speed': 0,
                    'efficiency': 'A+',
                    'hints_used': 0
                }
            }
        
        # Update progress
        session['simulation_progress']['total_score'] += calculated_score
        session['simulation_progress']['actions_completed'].append({
            'action': action,
            'timestamp': datetime.now().isoformat(),
            'score': calculated_score,
            'step': step
        })
        
        # Update metrics if provided
        if metrics:
            session['simulation_progress']['metrics'].update(metrics)
        
        # Calculate progress percentage
        total_actions = len(session['simulation_progress']['actions_completed'])
        progress_percentage = min((total_actions / 20) * 100, 100)  # Assume 20 actions for 100%
        
        response_data = {
            'success': True,
            'action': action,
            'score_gained': calculated_score,
            'total_score': session['simulation_progress']['total_score'],
            'progress_percentage': progress_percentage,
            'current_step': session['simulation_progress']['current_step'],
            'metrics': session['simulation_progress']['metrics'],
            'message': f'Progress updated: {action}'
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error updating progress: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update progress'
        }), 500

@advanced_simulation_bp.route('/api/hint', methods=['POST'])
def get_hint():
    """Enhanced contextual hint system with difficulty adaptation"""
    try:
        data = request.get_json()
        current_step = data.get('step', 1)
        scenario = data.get('scenario', 'basic-network')
        difficulty = data.get('difficulty', 'easy')
        hints_used = data.get('hints_used', 0)
        
        # Check hint limit based on difficulty
        hint_limits = {'easy': 5, 'medium': 3, 'hard': 1}
        max_hints = hint_limits.get(difficulty, 3)
        
        if hints_used >= max_hints:
            return jsonify({
                'success': False,
                'message': f'No more hints available for {difficulty} level',
                'hints_remaining': 0
            })
        
        # Contextual hints based on scenario and step
        hint_database = {
            'basic-network': {
                1: "Start by selecting a router from the device palette at the bottom of the screen.",
                2: "Click anywhere on the canvas to place your selected device.",
                3: "Try adding a switch next - it helps connect multiple devices.",
                4: "Use the draw mode to create connections between your devices.",
                5: "Check the performance panel on the right to track your progress."
            },
            'troubleshooting': {
                1: "Look for devices that appear disconnected or have error indicators.",
                2: "Use the select mode to examine device properties and configurations.",
                3: "Check connection paths and look for breaks or misconfigurations.",
                4: "Consider network topology best practices when fixing issues.",
                5: "Verify all connections are properly established before completing."
            },
            'advanced-topology': {
                1: "Plan your network hierarchy before placing devices.",
                2: "Consider redundancy and failover paths in your design.",
                3: "Implement proper segmentation for security and performance.",
                4: "Use appropriate device types for different network layers.",
                5: "Optimize traffic flow and minimize bottlenecks."
            }
        }
        
        # Get appropriate hint
        scenario_hints = hint_database.get(scenario, hint_database['basic-network'])
        hint_text = scenario_hints.get(current_step, "Keep exploring the simulation tools and features!")
        
        # Adjust hint detail based on difficulty
        if difficulty == 'hard':
            hint_text = hint_text.split('.')[0] + '.'  # Make hints shorter for hard mode
        elif difficulty == 'easy':
            hint_text += " Need more help? Check the help button for detailed instructions."
        
        # Track hint usage in session
        if 'simulation_progress' not in session:
            session['simulation_progress'] = {'metrics': {'hints_used': 0}}
        
        session['simulation_progress']['metrics']['hints_used'] = hints_used + 1
        
        return jsonify({
            'success': True,
            'hint': hint_text,
            'hints_used': hints_used + 1,
            'hints_remaining': max_hints - (hints_used + 1),
            'step': current_step,
            'scenario': scenario
        })
        
    except Exception as e:
        print(f"Error providing hint: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to provide hint'
        }), 500

@advanced_simulation_bp.route('/api/validate', methods=['POST'])
def validate_action():
    """Comprehensive action validation with real-time feedback"""
    try:
        data = request.get_json()
        
        action_type = data.get('action_type', '')
        device_type = data.get('device_type', '')
        position = data.get('position', {})
        connection_data = data.get('connection', {})
        scenario = data.get('scenario', 'basic-network')
        
        validation_result = {
            'valid': True,
            'message': 'Action completed successfully',
            'score': 0,
            'feedback': '',
            'suggestions': []
        }
        
        # Validate device placement
        if action_type == 'device_placement':
            if not device_type:
                validation_result.update({
                    'valid': False,
                    'message': 'No device type specified',
                    'feedback': 'Please select a device from the palette first.'
                })
            elif not position:
                validation_result.update({
                    'valid': False,
                    'message': 'Invalid position',
                    'feedback': 'Please click on a valid location on the canvas.'
                })
            else:
                # Check for overlapping devices (simplified)
                x, y = position.get('x', 0), position.get('y', 0)
                if x < 50 or y < 50:  # Too close to edges
                    validation_result.update({
                        'message': 'Device placed near edge',
                        'feedback': 'Consider placing devices away from canvas edges for better organization.',
                        'suggestions': ['Move device towards center', 'Leave space for connections']
                    })
                
                validation_result['score'] = 10
        
        # Validate connections
        elif action_type == 'connection_creation':
            from_device = connection_data.get('from')
            to_device = connection_data.get('to')
            
            if not from_device or not to_device:
                validation_result.update({
                    'valid': False,
                    'message': 'Invalid connection endpoints',
                    'feedback': 'Connections must be between two different devices.'
                })
            elif from_device == to_device:
                validation_result.update({
                    'valid': False,
                    'message': 'Cannot connect device to itself',
                    'feedback': 'Please select two different devices for the connection.'
                })
            else:
                validation_result['score'] = 15
                validation_result['feedback'] = 'Connection established successfully!'
        
        # Validate mode changes
        elif action_type == 'mode_change':
            mode = data.get('mode', '')
            valid_modes = ['select', 'draw', 'connect']
            
            if mode not in valid_modes:
                validation_result.update({
                    'valid': False,
                    'message': 'Invalid mode',
                    'feedback': f'Valid modes are: {", ".join(valid_modes)}'
                })
            else:
                validation_result['score'] = 2
                validation_result['feedback'] = f'Switched to {mode} mode'
        
        # Scenario-specific validation
        if scenario == 'troubleshooting':
            validation_result['suggestions'].append('Look for network issues to resolve')
        elif scenario == 'advanced-topology':
            validation_result['suggestions'].extend([
                'Consider network hierarchy',
                'Plan for redundancy',
                'Optimize traffic flow'
            ])
        
        return jsonify(validation_result)
        
    except Exception as e:
        print(f"Error validating action: {str(e)}")
        return jsonify({
            'valid': False,
            'message': 'Validation failed',
            'error': 'Server error during validation'
        }), 500

@advanced_simulation_bp.route('/api/achievements', methods=['GET'])
def get_achievements():
    """Enhanced achievement system with progress tracking"""
    try:
        # Get current progress from session
        progress = session.get('simulation_progress', {})
        actions_completed = progress.get('actions_completed', [])
        total_score = progress.get('total_score', 0)
        metrics = progress.get('metrics', {})
        
        # Define comprehensive achievement system
        achievements = [
            {
                'id': 'first-device',
                'name': 'First Device',
                'description': 'Place your first device on the canvas',
                'icon': 'fa-star',
                'points': 10,
                'unlocked': len([a for a in actions_completed if a['action'] == 'device_placed']) > 0,
                'progress': min(len([a for a in actions_completed if a['action'] == 'device_placed']), 1),
                'requirement': 1
            },
            {
                'id': 'connection-master',
                'name': 'Connection Master',
                'description': 'Create 3 successful connections',
                'icon': 'fa-link',
                'points': 25,
                'unlocked': len([a for a in actions_completed if a['action'] == 'connection_created']) >= 3,
                'progress': len([a for a in actions_completed if a['action'] == 'connection_created']),
                'requirement': 3
            },
            {
                'id': 'speed-demon',
                'name': 'Speed Demon',
                'description': 'Complete 10+ actions per minute',
                'icon': 'fa-bolt',
                'points': 50,
                'unlocked': metrics.get('speed', 0) >= 10,
                'progress': metrics.get('speed', 0),
                'requirement': 10
            },
            {
                'id': 'perfectionist',
                'name': 'Perfectionist',
                'description': 'Maintain 100% accuracy',
                'icon': 'fa-trophy',
                'points': 75,
                'unlocked': metrics.get('accuracy', 100) == 100 and len(actions_completed) >= 5,
                'progress': metrics.get('accuracy', 100),
                'requirement': 100
            },
            {
                'id': 'network-architect',
                'name': 'Network Architect',
                'description': 'Complete an advanced topology scenario',
                'icon': 'fa-building',
                'points': 100,
                'unlocked': any(a['action'] == 'scenario_completed' and 'advanced' in str(a) for a in actions_completed),
                'progress': len([a for a in actions_completed if a['action'] == 'scenario_completed']),
                'requirement': 1
            },
            {
                'id': 'efficiency-expert',
                'name': 'Efficiency Expert',
                'description': 'Achieve A+ efficiency rating',
                'icon': 'fa-award',
                'points': 60,
                'unlocked': metrics.get('efficiency', 'C') == 'A+',
                'progress': 1 if metrics.get('efficiency', 'C') == 'A+' else 0,
                'requirement': 1
            }
        ]
        
        # Calculate total achievement points
        unlocked_achievements = [a for a in achievements if a['unlocked']]
        total_achievement_points = sum(a['points'] for a in unlocked_achievements)
        possible_points = sum(a['points'] for a in achievements)
        
        return jsonify({
            'success': True,
            'achievements': achievements,
            'unlocked_count': len(unlocked_achievements),
            'total_count': len(achievements),
            'achievement_points': total_achievement_points,
            'possible_points': possible_points,
            'completion_percentage': round((len(unlocked_achievements) / len(achievements)) * 100, 1)
        })
        
    except Exception as e:
        print(f"Error getting achievements: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load achievements'
        }), 500

@advanced_simulation_bp.route('/api/scenario/<scenario_id>', methods=['GET'])
def get_scenario_details(scenario_id):
    """Get detailed scenario information and requirements"""
    try:
        scenarios = {
            'basic-network': {
                'id': 'basic-network',
                'title': 'Basic Network Setup',
                'difficulty': 'easy',
                'description': 'Learn fundamental networking concepts by building a simple network topology.',
                'duration': '10-15 minutes',
                'objectives': [
                    'Place network devices on the canvas',
                    'Create connections between devices',
                    'Understand basic network topology',
                    'Practice using simulation tools'
                ],
                'required_devices': ['router', 'switch', 'pc'],
                'required_connections': 2,
                'tutorial_enabled': True,
                'hints_available': 5,
                'scoring': {
                    'completion_points': 100,
                    'efficiency_bonus': 50,
                    'speed_bonus': 25
                }
            },
            'troubleshooting': {
                'id': 'troubleshooting',
                'title': 'Network Troubleshooting',
                'difficulty': 'medium',
                'description': 'Diagnose and fix common network issues in a corporate environment.',
                'duration': '20-30 minutes',
                'objectives': [
                    'Identify network connectivity issues',
                    'Analyze network topology problems',
                    'Apply systematic troubleshooting approach',
                    'Implement effective solutions'
                ],
                'required_devices': ['router', 'switch', 'pc', 'server'],
                'required_connections': 4,
                'tutorial_enabled': False,
                'hints_available': 3,
                'scoring': {
                    'completion_points': 200,
                    'efficiency_bonus': 100,
                    'accuracy_bonus': 75
                }
            },
            'advanced-topology': {
                'id': 'advanced-topology',
                'title': 'Advanced Network Design',
                'difficulty': 'hard',
                'description': 'Design a complex enterprise network with redundancy and security considerations.',
                'duration': '45-60 minutes',
                'objectives': [
                    'Design scalable network architecture',
                    'Implement redundancy and failover',
                    'Apply security best practices',
                    'Optimize network performance'
                ],
                'required_devices': ['router', 'switch', 'pc', 'server', 'firewall'],
                'required_connections': 8,
                'tutorial_enabled': False,
                'hints_available': 1,
                'scoring': {
                    'completion_points': 500,
                    'design_bonus': 200,
                    'security_bonus': 150,
                    'optimization_bonus': 100
                }
            }
        }
        
        scenario = scenarios.get(scenario_id)
        if not scenario:
            return jsonify({
                'success': False,
                'error': 'Scenario not found'
            }), 404
        
        return jsonify({
            'success': True,
            'scenario': scenario
        })
        
    except Exception as e:
        print(f"Error getting scenario details: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load scenario details'
        }), 500

@advanced_simulation_bp.route('/api/save', methods=['POST'])
def save_configuration():
    """Save current simulation state and configuration"""
    try:
        data = request.get_json()
        
        configuration = {
            'devices': data.get('devices', []),
            'connections': data.get('connections', []),
            'settings': data.get('settings', {}),
            'progress': session.get('simulation_progress', {}),
            'timestamp': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        # In production, save to database
        # For now, store in session
        session['saved_configuration'] = configuration
        
        return jsonify({
            'success': True,
            'message': 'Configuration saved successfully',
            'save_id': f"config_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'timestamp': configuration['timestamp']
        })
        
    except Exception as e:
        print(f"Error saving configuration: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to save configuration'
        }), 500

@advanced_simulation_bp.route('/api/load', methods=['GET'])
def load_configuration():
    """Load saved simulation configuration"""
    try:
        configuration = session.get('saved_configuration')
        
        if not configuration:
            return jsonify({
                'success': False,
                'error': 'No saved configuration found'
            }), 404
        
        return jsonify({
            'success': True,
            'configuration': configuration,
            'message': 'Configuration loaded successfully'
        })
        
    except Exception as e:
        print(f"Error loading configuration: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load configuration'
        }), 500
