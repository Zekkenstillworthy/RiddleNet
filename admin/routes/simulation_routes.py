from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from admin.controllers.simulation_controller import SimulationController
# Learning controller removed - Learning Paths feature disabled
from admin.services.assignment_service import assignment_service
from socket_events import emit_new_simulation_available, emit_assignment_created
from utils.render_utils import render_safe_template
from utils.permission_decorators import teacher_required, require_class_id_in_json
import json

# Create blueprint with unique name to avoid conflicts
admin_simulation_bp = Blueprint('admin_simulation', __name__, url_prefix='/admin/simulation')

# Initialize controllers
simulation_controller = SimulationController()
# learning_controller removed - Learning Paths feature disabled

class TroubleshootingSimulation:
    """Helper class to create troubleshooting-compatible simulation objects"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self):
        """Convert to dictionary for template usage"""
        return {key: getattr(self, key, None) for key in dir(self) 
                if not key.startswith('_') and not callable(getattr(self, key))}

# Dashboard route removed - direct simulation access only

# List route removed - direct simulation access only

# Selector route removed - direct simulation access only

@admin_simulation_bp.route('/edit/new')
@login_required
@teacher_required
def new_simulation_troubleshooting_editor():
    """Create new simulation using troubleshooting editor"""
    try:
        # Use the enhanced troubleshooting editor template with no simulation data
        return render_safe_template(
            'admin/troubleshooting/edit_simulation.html',
            simulation=None
        )
    except Exception as e:
        flash(f'Error loading editor: {str(e)}', 'error')
        return redirect('/admin/classes')

@admin_simulation_bp.route('/edit/<int:simulation_id>')
@login_required
@teacher_required
def edit_simulation(simulation_id):
    """Edit existing simulation with enhanced troubleshooting editor"""
    try:
        simulation_data = simulation_controller.get_simulation_by_id(simulation_id, include_steps=True)
        if 'error' in simulation_data:
            flash(simulation_data['error'], 'error')
            return redirect('/admin/classes')
        
        # Convert simulation data to troubleshooting format if needed
        simulation = simulation_data['simulation']

        # Some legacy paths may return JSON strings; normalize to dict
        if isinstance(simulation, str):
            try:
                loaded = json.loads(simulation)
                simulation = loaded if isinstance(loaded, dict) else {}
            except Exception:
                simulation = {}
        elif not isinstance(simulation, dict):
            simulation = {}

        # Normalize potential JSON string fields to dict/list
        sim_config = simulation.get('simulation_config') if isinstance(simulation, dict) else None
        if isinstance(sim_config, str):
            try:
                sim_config = json.loads(sim_config)
            except Exception:
                sim_config = {}
        elif not isinstance(sim_config, dict):
            sim_config = {}

        step_defs = simulation.get('step_definitions') if isinstance(simulation, dict) else None
        if isinstance(step_defs, str):
            try:
                step_defs = json.loads(step_defs)
            except Exception:
                step_defs = []
        elif not isinstance(step_defs, list):
            step_defs = []

        # Normalize hints field (may be stored as JSON string)
        hints = simulation.get('hints', []) if isinstance(simulation, dict) else []
        if isinstance(hints, str):
            try:
                hints = json.loads(hints)
            except Exception:
                hints = []
        if not isinstance(hints, list):
            hints = []

        # Ensure nested optional dict blocks are dicts (not strings)
        def ensure_dict(d, key):
            val = d.get(key, {}) if isinstance(d, dict) else {}
            if isinstance(val, str):
                try:
                    return json.loads(val) or {}
                except Exception:
                    return {}
            return val if isinstance(val, dict) else {}
        
        # Log types for diagnostics
        try:
            current_app.logger.info(
                f"[edit_simulation] ID={simulation_id} types: sim={type(simulation)}, sim_config={type(sim_config)}, steps={type(step_defs)}, hints={type(hints)}"
            )
        except Exception:
            pass

        # Create a troubleshooting-compatible simulation object
        troubleshooting_sim = TroubleshootingSimulation(
            id=simulation.get('id'),
            title=simulation.get('title', 'Untitled Simulation'),
            description=simulation.get('description', ''),
            difficulty=simulation.get('difficulty', 'medium'),
            problem_type=simulation.get('simulation_type', 'network'),
            scenario=simulation.get('description', ''),
            solution=simulation.get('solution_steps', ''),
            time_limit=simulation.get('estimated_duration', 15),
            base_score=simulation.get('base_score', 50),
            time_bonus=simulation.get('time_bonus', 10),
            hints=hints,
            initial_topology=ensure_dict(sim_config, 'network_topology'),
            solution_topology=ensure_dict(sim_config, 'solution_topology') or ensure_dict(sim_config, 'network_topology'),
            cli_rules=ensure_dict(sim_config, 'cli_rules'),
            # New nested blocks for enhanced authoring
            collab=ensure_dict(sim_config, 'collab'),
            tutorial=ensure_dict(sim_config, 'tutorial'),
            achievements=ensure_dict(sim_config, 'achievements'),
            scoring=ensure_dict(sim_config, 'scoring'),
            required_steps=step_defs,
            created_at=simulation.get('created_at'),
            updated_at=simulation.get('updated_at'),
            is_active=simulation.get('is_active', True)
        )
        
        # Use the enhanced troubleshooting editor template
        return render_safe_template(
            'admin/troubleshooting/edit_simulation.html',
            simulation=troubleshooting_sim
        )
    except Exception as e:
        flash(f'Error loading simulation: {str(e)}', 'error')
        return redirect('/admin/classes')

@admin_simulation_bp.route('/edit/<int:simulation_id>/save', methods=['POST'])
@login_required
@teacher_required
def save_simulation_from_troubleshooting_editor(simulation_id):
    """Save simulation changes from troubleshooting editor"""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        # Convert troubleshooting editor data back to simulation format
        update_data = {
            'title': data.get('title'),
            'description': data.get('description'),
            'difficulty': data.get('difficulty'),
            'type': data.get('problem_type', 'network'),
            'estimated_duration': data.get('time_limit', 15),
            'base_score': data.get('base_score', 50),
            'time_bonus': data.get('time_bonus', 10),
            'hints': data.get('hints', []),
            'step_definitions': data.get('required_steps', []),
            'solution_steps': data.get('solution'),
            'simulation_config': {
                'network_topology': data.get('initial_topology', {}),
                'devices': data.get('devices', []),
                'solution_topology': data.get('solution_topology', {}),
                # Persist CLI rules authored in the editor without requiring a DB migration
                'cli_rules': data.get('cli_rules', {}),
                # New nested authoring blocks
                'collab': data.get('collab', {}),
                'tutorial': data.get('tutorial', {}),
                'achievements': data.get('achievements', {}),
                'scoring': data.get('scoring', {})
            }
        }

        # Update the simulation
        result = simulation_controller.update_simulation(simulation_id, update_data)

        if result.get('success'):
            return jsonify({
                'success': True,
                'message': 'Simulation updated successfully',
                'simulation_id': simulation_id
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('error', 'Error updating simulation')
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error saving simulation: {str(e)}'
        }), 500

@admin_simulation_bp.route('/edit/<int:simulation_id>/validation/config', methods=['GET'])
@login_required
@teacher_required
def get_enhanced_validation_config(simulation_id):
    """Get enhanced validation configuration for a simulation"""
    from admin.controllers.modern_simulation_controller import modern_simulation_controller
    
    result = modern_simulation_controller.get_enhanced_validation_config(simulation_id)
    
    if 'error' in result:
        return jsonify({'success': False, 'message': result['error']}), 404
    
    return jsonify(result)


@admin_simulation_bp.route('/edit/<int:simulation_id>/validation/config', methods=['POST'])
@login_required
@teacher_required
def save_enhanced_validation_config(simulation_id):
    """Save enhanced validation configuration for a simulation"""
    from admin.controllers.modern_simulation_controller import modern_simulation_controller
    
    data = request.json
    if not data:
        return jsonify({'success': False, 'message': 'No validation data provided'}), 400
    
    result = modern_simulation_controller.save_enhanced_validation_config(simulation_id, data)
    
    if 'error' in result:
        return jsonify({'success': False, 'message': result['error']}), 500
    
    return jsonify(result)


@admin_simulation_bp.route('/edit/<int:simulation_id>/validation/state', methods=['POST'])
@login_required
@teacher_required
def validate_simulation_state(simulation_id):
    """Validate current simulation state"""
    from admin.controllers.modern_simulation_controller import modern_simulation_controller
    
    data = request.json
    if not data:
        return jsonify({'success': False, 'message': 'No topology data provided'}), 400
    
    result = modern_simulation_controller.validate_simulation_state(simulation_id, data)
    
    if 'error' in result:
        return jsonify({'success': False, 'message': result['error']}), 500
    
    return jsonify(result)


@admin_simulation_bp.route('/edit/<int:simulation_id>/validation/tests', methods=['POST'])
@login_required
@teacher_required
def run_connectivity_tests(simulation_id):
    """Run connectivity tests for a simulation"""
    from admin.controllers.modern_simulation_controller import modern_simulation_controller
    
    data = request.json
    if not data:
        return jsonify({'success': False, 'message': 'No test data provided'}), 400
    
    topology_data = data.get('topology', {})
    test_config = data.get('test_config', {})
    
    result = modern_simulation_controller.run_connectivity_tests(simulation_id, topology_data, test_config)
    
    if 'error' in result:
        return jsonify({'success': False, 'message': result['error']}), 500
    
    return jsonify(result)


@admin_simulation_bp.route('/edit/save', methods=['POST'])
@login_required
@teacher_required
def create_simulation_from_troubleshooting_editor():
    """Create new simulation from troubleshooting editor"""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        # Convert troubleshooting editor data to simulation format
        simulation_data = {
            'basic': {
                'title': data.get('title', 'New Simulation'),
                'description': data.get('description', ''),
                'difficulty': data.get('difficulty', 'medium'),
                'simulation_type': data.get('problem_type', 'network'),
                'category': data.get('problem_type', 'network'),
                'duration': data.get('time_limit', 15)
            },
            'objectives': [
                'Complete the troubleshooting scenario',
                'Apply networking knowledge',
                'Demonstrate problem-solving skills'
            ],
            'steps': data.get('required_steps', []),
            'scoring': {
                'timeBonus': data.get('time_bonus', 10),
                'perfectBonus': data.get('base_score', 50),
                'tags': '',
                'isActive': True,
                'isPublished': False
            },
            'template': {
                'selectedTemplate': 'troubleshooting-template',
                'networkTopology': data.get('initial_topology', {}),
                'devices': data.get('devices', []),
                'protocols': [],
                # Carry CLI rules through the builder payload
                'cli_rules': data.get('cli_rules', {}),
                # Carry new nested authoring blocks as well
                'collab': data.get('collab', {}),
                'tutorial': data.get('tutorial', {}),
                'achievements': data.get('achievements', {}),
                'scoring': data.get('scoring', {})
            }
        }

        # Create the simulation
        result = simulation_controller.create_simulation_from_builder(simulation_data, current_user.id)

        if result.get('success'):
            return jsonify({
                'success': True,
                'message': 'Simulation created successfully',
                'simulation_id': result.get('simulation', {}).get('id')
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('error', 'Error creating simulation')
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating simulation: {str(e)}'
        }), 500

@admin_simulation_bp.route('/<int:simulation_id>')
@login_required
@teacher_required
def view_simulation(simulation_id):
    """Preview simulation"""
    try:
        simulation_data = simulation_controller.get_simulation_by_id(simulation_id, include_steps=True)
        if 'error' in simulation_data:
            flash(simulation_data['error'], 'error')
            return redirect('/admin/classes')
        
        return render_template(
            'admin/simulation_preview.html',
            simulation=simulation_data['simulation']
        )
    except Exception as e:
        flash(f'Error loading simulation: {str(e)}', 'error')
        return redirect('/admin/classes')

@admin_simulation_bp.route('/analytics/<int:simulation_id>')
@login_required
@teacher_required
def simulation_analytics(simulation_id):
    """Detailed analytics for a specific simulation"""
    try:
        analytics_data = simulation_controller.get_simulation_analytics(simulation_id)
        if 'error' in analytics_data:
            flash(analytics_data['error'], 'error')
            return redirect('/admin/classes')
        
        return render_template(
            'admin/simulation_analytics.html',
            analytics=analytics_data
        )
    except Exception as e:
        flash(f'Error loading analytics: {str(e)}', 'error')
        return redirect('/admin/classes')

# API Routes for AJAX/Frontend Integration

@admin_simulation_bp.route('/api', methods=['POST'])
@login_required
@teacher_required
def create_simulation_api():
    """Create simulation from builder interface"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        # Accept both flat payloads and builder format, delegate to controller
        result = simulation_controller.create_simulation_from_payload(data, current_user.id)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 201
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@admin_simulation_bp.route('/api/templates/<simulation_type>')
@login_required
@teacher_required
def get_simulation_templates(simulation_type):
    """Get templates for specific simulation type"""
    try:
        templates = simulation_controller.get_simulation_templates(simulation_type)
        return jsonify(templates)
    except Exception as e:
        return jsonify({'error': f'Failed to load templates: {str(e)}'}), 500

@admin_simulation_bp.route('/api/topologies', methods=['GET'])
@login_required
@teacher_required
def get_available_topologies():
    """Get available topologies for simulation creation"""
    try:
        from admin.models.topology import Topology
        
        # Get all active topologies from database
        topologies = Topology.query.filter_by(is_active=True).all()
        
        topology_list = []
        for topology in topologies:
            topology_list.append({
                'id': topology.id,
                'title': topology.title,
                'description': topology.description,
                'topology_type': topology.topology_type,
                'difficulty': topology.difficulty,
                'device_requirements': topology.device_requirements,
                'scoring_metrics': topology.scoring_metrics,
                'base_score': topology.base_score
            })
        
        # If no topologies in database, provide default options
        if not topology_list:
            default_topologies = [
                {
                    'id': 'point-to-point',
                    'title': 'Point-to-Point',
                    'description': 'Direct connection between two devices',
                    'topology_type': 'point-to-point',
                    'difficulty': 'easy',
                    'device_requirements': {'pc': 2, 'router': 0, 'switch': 0},
                    'scoring_metrics': {'time_efficiency': 10, 'config_process': 25, 'design_layout': 20, 'completeness': 20, 'correctness': 25},
                    'base_score': 10
                },
                {
                    'id': 'star',
                    'title': 'Star Topology',
                    'description': 'Central hub connecting multiple devices',
                    'topology_type': 'star',
                    'difficulty': 'medium',
                    'device_requirements': {'pc': 3, 'router': 0, 'switch': 1},
                    'scoring_metrics': {'time_efficiency': 10, 'config_process': 25, 'design_layout': 20, 'completeness': 20, 'correctness': 25},
                    'base_score': 15
                },
                {
                    'id': 'mesh',
                    'title': 'Mesh Topology',
                    'description': 'Every device connected to every other device',
                    'topology_type': 'mesh',
                    'difficulty': 'hard',
                    'device_requirements': {'pc': 0, 'router': 4, 'switch': 0},
                    'scoring_metrics': {'time_efficiency': 10, 'config_process': 25, 'design_layout': 20, 'completeness': 20, 'correctness': 25},
                    'base_score': 25
                },
                {
                    'id': 'bus',
                    'title': 'Bus Topology',
                    'description': 'All devices connected to a single communication line',
                    'topology_type': 'bus',
                    'difficulty': 'medium',
                    'device_requirements': {'pc': 4, 'router': 0, 'switch': 0},
                    'scoring_metrics': {'time_efficiency': 10, 'config_process': 25, 'design_layout': 20, 'completeness': 20, 'correctness': 25},
                    'base_score': 15
                },
                {
                    'id': 'ring',
                    'title': 'Ring Topology',
                    'description': 'Devices connected in a circular fashion',
                    'topology_type': 'ring',
                    'difficulty': 'medium',
                    'device_requirements': {'pc': 0, 'router': 0, 'switch': 4},
                    'scoring_metrics': {'time_efficiency': 10, 'config_process': 25, 'design_layout': 20, 'completeness': 20, 'correctness': 25},
                    'base_score': 15
                },
                {
                    'id': 'tree',
                    'title': 'Tree Topology',
                    'description': 'Hierarchical structure with branches',
                    'topology_type': 'tree',
                    'difficulty': 'hard',
                    'device_requirements': {'pc': 4, 'router': 1, 'switch': 2},
                    'scoring_metrics': {'time_efficiency': 10, 'config_process': 25, 'design_layout': 20, 'completeness': 20, 'correctness': 25},
                    'base_score': 20
                },
                {
                    'id': 'hybrid',
                    'title': 'Hybrid Topology',
                    'description': 'Combination of multiple topology types',
                    'topology_type': 'hybrid',
                    'difficulty': 'hard',
                    'device_requirements': {'pc': 3, 'router': 1, 'switch': 2, 'server': 1},
                    'scoring_metrics': {'time_efficiency': 10, 'config_process': 25, 'design_layout': 20, 'completeness': 20, 'correctness': 25},
                    'base_score': 30
                }
            ]
            topology_list = default_topologies
        
        return jsonify({
            'success': True,
            'topologies': topology_list
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get topologies: {str(e)}'}), 500

@admin_simulation_bp.route('/api/validate-step', methods=['POST'])
@login_required
@teacher_required
def validate_simulation_step():
    """Real-time validation for simulation steps during creation"""
    try:
        data = request.get_json()
        
        # Mock validation for builder interface
        validation_result = {
            'isValid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        step_type = data.get('type')
        step_content = data.get('content', {})
        
        # Validate based on step type
        if step_type == 'configuration':
            if not step_content.get('device_type'):
                validation_result['errors'].append('Device type is required for configuration steps')
                validation_result['isValid'] = False
            
            if not step_content.get('commands'):
                validation_result['errors'].append('Configuration commands are required')
                validation_result['isValid'] = False
        
        elif step_type == 'question':
            if not step_content.get('question_text'):
                validation_result['errors'].append('Question text is required')
                validation_result['isValid'] = False
            
            if step_content.get('question_type') == 'multiple_choice' and not step_content.get('options'):
                validation_result['warnings'].append('Multiple choice questions should have options')
        
        return jsonify(validation_result)
        
    except Exception as e:
        return jsonify({'error': f'Validation error: {str(e)}'}), 500

@admin_simulation_bp.route('/api/list', methods=['GET'])
@login_required
@teacher_required
def get_simulations_api():
    """Get simulations list for API consumption"""
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        result = simulation_controller.get_all_simulations(include_inactive=include_inactive)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Failed to get simulations: {str(e)}'}), 500

@admin_simulation_bp.route('/api/<int:simulation_id>', methods=['GET'])
@login_required
@teacher_required
def get_simulation_api(simulation_id):
    """Get simulation by ID"""
    try:
        include_steps = request.args.get('include_steps', 'true').lower() == 'true'
        result = simulation_controller.get_simulation_by_id(simulation_id, include_steps=include_steps)
        
        if 'error' in result:
            return jsonify(result), 404
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Failed to get simulation: {str(e)}'}), 500

@admin_simulation_bp.route('/api/<int:simulation_id>', methods=['PUT'])
@login_required
@teacher_required
def update_simulation_api(simulation_id):
    """Update simulation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        result = simulation_controller.update_simulation(simulation_id, data)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Failed to update simulation: {str(e)}'}), 500

@admin_simulation_bp.route('/api/<int:simulation_id>/publish', methods=['POST'])
@login_required
@teacher_required
def publish_simulation_api(simulation_id):
    """Publish simulation"""
    try:
        result = simulation_controller.toggle_simulation_status(simulation_id, True)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify({'success': True, 'message': 'Simulation published successfully'})
    except Exception as e:
        return jsonify({'error': f'Failed to publish simulation: {str(e)}'}), 500

@admin_simulation_bp.route('/api/<int:simulation_id>/unpublish', methods=['POST'])
@login_required
@teacher_required
def unpublish_simulation_api(simulation_id):
    """Unpublish simulation"""
    try:
        result = simulation_controller.toggle_simulation_status(simulation_id, False)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify({'success': True, 'message': 'Simulation unpublished successfully'})
    except Exception as e:
        return jsonify({'error': f'Failed to unpublish simulation: {str(e)}'}), 500

@admin_simulation_bp.route('/api/<int:simulation_id>/duplicate', methods=['POST'])
@login_required
@teacher_required
def duplicate_simulation_api(simulation_id):
    """Duplicate simulation"""
    try:
        result = simulation_controller.duplicate_simulation(simulation_id)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Failed to duplicate simulation: {str(e)}'}), 500

@admin_simulation_bp.route('/api/<int:simulation_id>', methods=['DELETE'])
@login_required
@teacher_required
def delete_simulation_api(simulation_id):
    """Delete simulation"""
    try:
        result = simulation_controller.delete_simulation(simulation_id)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Failed to delete simulation: {str(e)}'}), 500

@admin_simulation_bp.route('/api/search', methods=['GET'])
@login_required
@teacher_required
def search_simulations_api():
    """Search simulations with filters"""
    try:
        query_params = {
            'query': request.args.get('query', ''),
            'type': request.args.get('type'),
            'difficulty': request.args.get('difficulty'),
            'category': request.args.get('category')
        }
        
        result = simulation_controller.search_simulations(query_params)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@admin_simulation_bp.route('/api/<int:simulation_id>/analytics', methods=['GET'])
@login_required
@teacher_required
def get_simulation_analytics_api(simulation_id):
    """Get simulation analytics"""
    try:
        result = simulation_controller.get_simulation_analytics(simulation_id)
        
        if 'error' in result:
            return jsonify(result), 404
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Failed to get analytics: {str(e)}'}), 500

@admin_simulation_bp.route('/api/<int:simulation_id>/validate/<int:step_index>', methods=['POST'])
@login_required
@teacher_required
def validate_step_response(simulation_id, step_index):
    """Validate a specific step response (for testing simulations)"""
    try:
        data = request.get_json()
        if not data or 'response' not in data:
            return jsonify({'valid': False, 'message': 'No response provided'}), 400
        
        result = simulation_controller.validate_simulation_step(
            simulation_id, 
            step_index, 
            data['response']
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Validation failed: {str(e)}'}), 500

# Learning Path Integration Routes - DISABLED (Feature Removed)

@admin_simulation_bp.route('/api/learning-paths', methods=['GET'])
@login_required
def get_learning_paths_api():
    """Get all learning paths - DISABLED"""
    return jsonify({'learning_paths': [], 'message': 'Learning Paths feature has been removed'})

@admin_simulation_bp.route('/api/learning-paths', methods=['POST'])
@login_required
def create_learning_path_api():
    """Create a new learning path - DISABLED"""
    return jsonify({'error': 'Learning Paths feature has been removed'}), 410

@admin_simulation_bp.route('/api/learning-paths/<int:path_id>/simulations', methods=['POST'])
@login_required
def add_simulation_to_path_api(path_id):
    """Add simulation to learning path - DISABLED"""
    return jsonify({'error': 'Learning Paths feature has been removed'}), 410

# Error Handlers
@admin_simulation_bp.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404

@admin_simulation_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ===== WEEK 2 ENHANCEMENT: ASSIGNMENT API ENDPOINTS =====

@admin_simulation_bp.route('/api/assignments/lesson', methods=['POST'])
@login_required
@teacher_required
@require_class_id_in_json
def create_lesson_assignment():
    """Create a lesson-based assignment"""
    try:
        data = request.get_json()
        
        assignment = assignment_service.create_lesson_assignment(
            simulation_id=data['simulation_id'],
            class_id=data['class_id'],
            lesson_name=data['lesson_name'],
            due_date=data.get('due_date'),
            max_attempts=data.get('max_attempts', 3)
        )
        
        return jsonify({
            'success': True,
            'assignment_id': assignment.id,
            'message': 'Lesson assignment created successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to create lesson assignment: {str(e)}'}), 500

@admin_simulation_bp.route('/api/assignments/category', methods=['POST'])
@login_required
@teacher_required
def create_category_auto_assignment():
    """Create automatic assignments for all simulations in a category"""
    try:
        data = request.get_json()
        
        assignments = assignment_service.create_category_auto_assignment(
            category=data['category'],
            class_ids=data['class_ids']
        )
        
        return jsonify({
            'success': True,
            'assignments_created': len(assignments),
            'message': f'Created {len(assignments)} auto-assignments for {data["category"]} category'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to create category assignments: {str(e)}'}), 500

@admin_simulation_bp.route('/api/assignments/explicit', methods=['POST'])
@login_required
@teacher_required
@require_class_id_in_json
def create_explicit_assignment():
    """Create an explicit assignment with custom settings"""
    try:
        data = request.get_json() or {}

        # Required fields
        simulation_id = data.get('simulation_id')
        class_id = data.get('class_id')
        if not simulation_id:
            return jsonify({'error': 'simulation_id is required'}), 400

        # Title is optional from the UI; generate a sensible default if missing
        title = data.get('title')
        if not title:
            try:
                # Lazy import to avoid circulars
                from admin.models.simulation import Simulation
                sim = Simulation.query.get(simulation_id)
                if sim and getattr(sim, 'title', None):
                    title = f"Assignment: {sim.title}"
                else:
                    title = f"Assignment for Simulation {simulation_id}"
            except Exception:
                # Fallback if model lookup fails for any reason
                title = f"Assignment for Simulation {simulation_id}"

        assignment = assignment_service.create_explicit_assignment(
            simulation_id=simulation_id,
            class_id=class_id,
            title=title,
            description=data.get('description', ''),
            due_date=data.get('due_date'),
            max_attempts=data.get('max_attempts', 3)
        )
        
        return jsonify({
            'success': True,
            'assignment_id': assignment.id,
            'message': 'Explicit assignment created successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to create explicit assignment: {str(e)}'}), 500

@admin_simulation_bp.route('/api/assignments/auto-assign/<int:simulation_id>', methods=['POST'])
@login_required
@teacher_required
def auto_assign_simulation(simulation_id):
    """Automatically assign a simulation to relevant classes"""
    try:
        assignments = assignment_service.auto_assign_new_simulation(simulation_id)
        
        return jsonify({
            'success': True,
            'assignments_created': len(assignments),
            'class_ids': [a.class_id for a in assignments],
            'message': f'Auto-assigned simulation to {len(assignments)} classes'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to auto-assign simulation: {str(e)}'}), 500

@admin_simulation_bp.route('/api/assignments/class/<int:class_id>')
@login_required
@teacher_required
def get_class_assignments(class_id):
    """Get all assignments for a specific class"""
    try:
        assignment_type = request.args.get('type')
        assignments = assignment_service.get_assignments_for_class(class_id, assignment_type)
        
        return jsonify({
            'success': True,
            'class_id': class_id,
            'assignments': assignments,
            'total': len(assignments)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get class assignments: {str(e)}'}), 500

@admin_simulation_bp.route('/api/assignments/enable-auto/<int:class_id>', methods=['POST'])
@login_required
@teacher_required
def enable_category_auto_assignment(class_id):
    """Enable automatic assignment for a category in a class"""
    try:
        data = request.get_json()
        category = data['category']
        
        success = assignment_service.enable_category_auto_assignment(class_id, category)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Auto-assignment enabled for {category} in class {class_id}'
            })
        else:
            return jsonify({'error': 'Failed to enable auto-assignment'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to enable auto-assignment: {str(e)}'}), 500

@admin_simulation_bp.route('/api/assignments/statistics/<int:class_id>')
@login_required
@teacher_required
def get_assignment_statistics(class_id):
    """Get comprehensive assignment statistics for a class"""
    try:
        stats = assignment_service.get_assignment_statistics(class_id)
        
        return jsonify({
            'success': True,
            'class_id': class_id,
            'statistics': stats
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get assignment statistics: {str(e)}'}), 500

# Enhanced simulation creation with auto-assignment
@admin_simulation_bp.route('/api/create-with-auto-assign', methods=['POST'])
@login_required
@teacher_required
def create_simulation_with_auto_assign():
    """Create simulation and automatically assign to relevant classes"""
    try:
        data = request.get_json()

        # Create the simulation first
        result = simulation_controller.create_simulation(data)

        if 'error' in result:
            return jsonify(result), 400

        simulation_id = result['simulation_id']

        # Auto-assign to relevant classes
        assignments = assignment_service.auto_assign_new_simulation(simulation_id)

        # Send real-time notification
        emit_new_simulation_available(
            simulation_id,
            data.get('category', 'general'),
            [a.class_id for a in assignments]
        )

        return jsonify({
            'success': True,
            'simulation_id': simulation_id,
            'assignments_created': len(assignments),
            'message': f'Simulation created and assigned to {len(assignments)} classes'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to create simulation with auto-assignment: {str(e)}'}), 500

@admin_simulation_bp.route('/api/quick-create', methods=['POST'])
@login_required
@teacher_required
def quick_create_simulation():
    """Quick create simulation with minimal setup"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Build simulation data from quick form
        simulation_data = {
            'basic': {
                'title': data.get('title'),
                'simulation_type': data.get('simulation_type'),
                'difficulty': data.get('difficulty'),
                'description': data.get('description', ''),
                'category': data.get('simulation_type', 'general'),
                'tags': '',
                'estimated_duration': 30,
                'isActive': True,
                'isPublished': data.get('is_published', False)
            },
            'objectives': [
                f"Complete {data.get('simulation_type', 'networking')} exercise",
                "Apply learned concepts in practice",
                "Demonstrate understanding through hands-on work"
            ],
            'template': {
                'selectedTemplate': 'basic-template',
                'networkTopology': 'simple'
            },
            'steps': [
                {
                    'title': 'Introduction',
                    'type': 'instruction',
                    'description': f"Welcome to the {data.get('title', 'simulation')} exercise.",
                    'content': data.get('description', ''),
                    'validation': {'score': 0}
                },
                {
                    'title': 'Complete Task',
                    'type': 'question',
                    'description': 'Complete the assigned networking task.',
                    'questionText': f"Complete the {data.get('simulation_type', 'networking')} configuration as instructed.",
                    'questionType': 'text',
                    'validation': {
                        'expectedAnswer': '',
                        'score': 100
                    },
                    'hint': 'Follow the step-by-step instructions provided.'
                }
            ],
            'scoring': {
                'timeBonus': 10,
                'perfectBonus': 20,
                'totalPoints': 100
            }
        }

        # Create the simulation
        result = simulation_controller.create_simulation_from_builder(simulation_data, current_user.id)

        if 'error' in result:
            return jsonify(result), 400

        # Auto-assign to specified class if requested
        if data.get('auto_assign') and data.get('class_id'):
            try:
                assignment = assignment_service.create_explicit_assignment(
                    simulation_id=result['simulation']['id'],
                    class_id=data['class_id'],
                    title=f"Assignment: {data.get('title')}",
                    description=data.get('description', ''),
                    max_attempts=3
                )

                # Send notification
                emit_assignment_created(
                    assignment.id,
                    assignment.class_id,
                    assignment.simulation_id
                )

            except Exception as e:
                # Log but don't fail the creation
                print(f"Warning: Failed to auto-assign simulation: {e}")

        return jsonify({
            'success': True,
            'simulation': result['simulation'],
            'message': 'Simulation created successfully!'
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to create simulation: {str(e)}'}), 500
