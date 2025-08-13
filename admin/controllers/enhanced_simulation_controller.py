from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from admin import db
from admin.models.simulation import Simulation, SimulationAttempt
from admin.models.class_model import Class
from admin.models.module import Module, Lesson
from utils.auth_decorators import admin_required
from utils.render_utils import render_safe_template
from datetime import datetime
import json
from admin.controllers.simulation_controller import SimulationController

# Create blueprint for enhanced simulation management
admin_simulation_bp = Blueprint('admin_simulation', __name__, template_folder='../templates', url_prefix='/admin/simulations')

# Initialize simulation controller
simulation_controller = SimulationController()

@admin_simulation_bp.route('/manage')
@login_required
@admin_required
def manage_simulations():
    """Display simulation management interface"""
    try:
        # Get all simulations with analytics
        result = simulation_controller.get_all_simulations(include_inactive=False)
        simulations = result.get('simulations', [])
        
        return render_safe_template('admin/simulations/manage.html',
                                   simulations=simulations)
    except Exception as e:
        current_app.logger.error(f"Error loading simulations management: {str(e)}")
        flash('Error loading simulations', 'error')
        return redirect(url_for('dashboard.index'))

@admin_simulation_bp.route('/create')
@login_required
@admin_required
def create_simulation():
    """Display simulation builder interface"""
    return render_safe_template('admin/simulations/create.html')

@admin_simulation_bp.route('/create', methods=['POST'])
@login_required
@admin_required
def create_simulation_post():
    """Handle simulation creation from builder"""
    try:
        # Extract form data
        basic_data = {
            'title': request.form.get('title'),
            'type': request.form.get('simulation_type'),
            'category': request.form.get('category'),
            'difficulty': request.form.get('difficulty'),
            'description': request.form.get('description'),
            'duration': request.form.get('duration', 30)
        }
        
        # Extract objectives
        objectives = [obj.strip() for obj in request.form.getlist('objectives[]') if obj.strip()]
        
        # Extract steps data
        steps = []
        step_index = 1
        while f'steps[{step_index}][title]' in request.form:
            step_data = {
                'title': request.form.get(f'steps[{step_index}][title]'),
                'type': request.form.get(f'steps[{step_index}][type]'),
                'description': request.form.get(f'steps[{step_index}][description]'),
                'validation': {
                    'expectedAnswer': request.form.get(f'steps[{step_index}][answer]', ''),
                    'score': int(request.form.get(f'steps[{step_index}][points]', 10))
                },
                'hint': request.form.get(f'steps[{step_index}][hint]', '')
            }
            
            # Add type-specific fields
            step_type = step_data['type']
            if step_type == 'question':
                step_data['questionText'] = request.form.get(f'steps[{step_index}][question]', '')
                step_data['questionType'] = request.form.get(f'steps[{step_index}][questionType]', 'text')
            elif step_type == 'configuration':
                step_data['deviceType'] = request.form.get(f'steps[{step_index}][deviceType]', '')
                step_data['expectedCommands'] = request.form.get(f'steps[{step_index}][commands]', '')
            elif step_type == 'troubleshooting':
                step_data['problemScenario'] = request.form.get(f'steps[{step_index}][scenario]', '')
                step_data['troubleshootingSteps'] = request.form.get(f'steps[{step_index}][troubleshooting]', '')
            
            steps.append(step_data)
            step_index += 1
        
        # Extract scoring data
        scoring_data = {
            'timeBonus': int(request.form.get('time_bonus', 20)),
            'perfectBonus': int(request.form.get('perfect_bonus', 30)),
            'tags': request.form.get('tags', ''),
            'isActive': bool(request.form.get('is_active')),
            'isPublished': bool(request.form.get('is_published'))
        }
        
        # Template data (if selected)
        template_data = {
            'selectedTemplate': request.form.get('selected_template', ''),
            'networkTopology': {},
            'devices': [],
            'protocols': []
        }
        
        # Build the complete builder data
        builder_data = {
            'basic': basic_data,
            'objectives': objectives,
            'steps': steps,
            'scoring': scoring_data,
            'template': template_data
        }
        
        # Create the simulation using the controller
        result = simulation_controller.create_simulation_from_builder(builder_data, current_user.id)
        
        if result.get('success'):
            flash('Simulation created successfully!', 'success')
            return jsonify({'success': True, 'redirect': url_for('admin_simulation.manage_simulations')})
        else:
            return jsonify({'success': False, 'message': result.get('error', 'Unknown error occurred')})
            
    except Exception as e:
        current_app.logger.error(f"Error creating simulation: {str(e)}")
        return jsonify({'success': False, 'message': f'Error creating simulation: {str(e)}'})

@admin_simulation_bp.route('/<int:simulation_id>')
@login_required
@admin_required
def view_simulation(simulation_id):
    """View simulation details and analytics"""
    try:
        result = simulation_controller.get_simulation_analytics(simulation_id)
        
        if 'error' in result:
            flash(result['error'], 'error')
            return redirect(url_for('admin_simulation.manage_simulations'))
        
        return render_safe_template('admin/simulations/view.html',
                                   simulation_data=result)
    except Exception as e:
        current_app.logger.error(f"Error viewing simulation {simulation_id}: {str(e)}")
        flash('Error loading simulation details', 'error')
        return redirect(url_for('admin_simulation.manage_simulations'))

@admin_simulation_bp.route('/<int:simulation_id>/edit')
@login_required
@admin_required
def edit_simulation(simulation_id):
    """Edit simulation interface"""
    try:
        result = simulation_controller.get_simulation_by_id(simulation_id, include_steps=True)
        
        if 'error' in result:
            flash(result['error'], 'error')
            return redirect(url_for('admin_simulation.manage_simulations'))
        
        return render_safe_template('admin/simulations/edit.html',
                                   simulation=result['simulation'])
    except Exception as e:
        current_app.logger.error(f"Error loading simulation {simulation_id} for editing: {str(e)}")
        flash('Error loading simulation for editing', 'error')
        return redirect(url_for('admin_simulation.manage_simulations'))

@admin_simulation_bp.route('/<int:simulation_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_simulation_post(simulation_id):
    """Handle simulation updates"""
    try:
        update_data = {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'difficulty': request.form.get('difficulty'),
            'estimated_duration': int(request.form.get('duration', 30)),
            'tags': request.form.get('tags', '').split(',') if request.form.get('tags') else [],
            'is_active': bool(request.form.get('is_active')),
            'is_published': bool(request.form.get('is_published'))
        }
        
        # Extract objectives
        objectives = [obj.strip() for obj in request.form.getlist('objectives[]') if obj.strip()]
        update_data['learning_objectives'] = objectives
        
        result = simulation_controller.update_simulation(simulation_id, update_data)
        
        if result.get('success'):
            flash('Simulation updated successfully!', 'success')
            return redirect(url_for('admin_simulation.view_simulation', simulation_id=simulation_id))
        else:
            flash(result.get('error', 'Error updating simulation'), 'error')
            return redirect(url_for('admin_simulation.edit_simulation', simulation_id=simulation_id))
            
    except Exception as e:
        current_app.logger.error(f"Error updating simulation {simulation_id}: {str(e)}")
        flash('Error updating simulation', 'error')
        return redirect(url_for('admin_simulation.edit_simulation', simulation_id=simulation_id))

@admin_simulation_bp.route('/<int:simulation_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_simulation(simulation_id):
    """Delete (deactivate) simulation"""
    try:
        result = simulation_controller.delete_simulation(simulation_id)
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"Error deleting simulation {simulation_id}: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@admin_simulation_bp.route('/<int:simulation_id>/duplicate', methods=['POST'])
@login_required
@admin_required
def duplicate_simulation(simulation_id):
    """Create a copy of an existing simulation"""
    try:
        # Get the original simulation
        original_result = simulation_controller.get_simulation_by_id(simulation_id, include_steps=True)
        
        if 'error' in original_result:
            return jsonify({'success': False, 'message': original_result['error']})
        
        original = original_result['simulation']
        
        # Prepare duplicate data
        builder_data = {
            'basic': {
                'title': f"Copy of {original['title']}",
                'type': original['simulation_type'],
                'category': original['category'],
                'difficulty': original['difficulty'],
                'description': original['description'],
                'duration': original['estimated_duration']
            },
            'objectives': original.get('learning_objectives', []),
            'steps': original.get('step_definitions', []),
            'scoring': {
                'timeBonus': original.get('time_bonus', 20),
                'perfectBonus': original.get('perfect_completion_bonus', 30),
                'tags': ','.join(original.get('tags', [])),
                'isActive': False,  # Start as inactive
                'isPublished': False  # Start as unpublished
            },
            'template': {
                'selectedTemplate': '',
                'networkTopology': original.get('simulation_config', {}).get('network_topology', {}),
                'devices': original.get('simulation_config', {}).get('devices', []),
                'protocols': original.get('simulation_config', {}).get('protocols', [])
            }
        }
        
        # Create the duplicate
        result = simulation_controller.create_simulation_from_builder(builder_data, current_user.id)
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error duplicating simulation {simulation_id}: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@admin_simulation_bp.route('/templates/<simulation_type>')
@login_required
@admin_required
def get_templates(simulation_type):
    """Get templates for a specific simulation type"""
    try:
        templates = simulation_controller.get_simulation_templates(simulation_type)
        return jsonify(templates)
    except Exception as e:
        current_app.logger.error(f"Error getting templates for {simulation_type}: {str(e)}")
        return jsonify({})

@admin_simulation_bp.route('/search')
@login_required
@admin_required
def search_simulations():
    """Search simulations with filters"""
    try:
        query_params = {
            'query': request.args.get('q', ''),
            'type': request.args.get('type'),
            'difficulty': request.args.get('difficulty'),
            'category': request.args.get('category')
        }
        
        result = simulation_controller.search_simulations(query_params)
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error searching simulations: {str(e)}")
        return jsonify({'error': str(e)})

@admin_simulation_bp.route('/dashboard-stats')
@login_required
@admin_required
def dashboard_stats():
    """Get dashboard statistics for simulations"""
    try:
        stats = simulation_controller.get_dashboard_data()
        return jsonify(stats)
    except Exception as e:
        current_app.logger.error(f"Error getting dashboard stats: {str(e)}")
        return jsonify({'error': str(e)})

# Integration routes for connecting simulations to lessons
@admin_simulation_bp.route('/assign-to-lesson', methods=['POST'])
@login_required
@admin_required
def assign_simulation_to_lesson():
    """Assign a simulation to a lesson"""
    try:
        data = request.json
        lesson_id = data.get('lesson_id')
        simulation_id = data.get('simulation_id')
        
        if not lesson_id or not simulation_id:
            return jsonify({'success': False, 'message': 'Missing lesson_id or simulation_id'})
        
        # Get the lesson
        lesson = Lesson.query.get(lesson_id)
        if not lesson:
            return jsonify({'success': False, 'message': 'Lesson not found'})
        
        # Verify simulation exists
        simulation = Simulation.query.get(simulation_id)
        if not simulation:
            return jsonify({'success': False, 'message': 'Simulation not found'})
        
        # Add simulation to lesson's simulation_ids list
        if not lesson.simulation_ids:
            lesson.simulation_ids = []
        
        if simulation_id not in lesson.simulation_ids:
            lesson.simulation_ids.append(simulation_id)
            lesson.updated_at = datetime.utcnow()
            
            # Mark lesson as modified for SQLAlchemy
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(lesson, 'simulation_ids')
            
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Simulation assigned to lesson successfully'})
        else:
            return jsonify({'success': False, 'message': 'Simulation already assigned to this lesson'})
            
    except Exception as e:
        current_app.logger.error(f"Error assigning simulation to lesson: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@admin_simulation_bp.route('/remove-from-lesson', methods=['POST'])
@login_required
@admin_required
def remove_simulation_from_lesson():
    """Remove a simulation from a lesson"""
    try:
        data = request.json
        lesson_id = data.get('lesson_id')
        simulation_id = data.get('simulation_id')
        
        if not lesson_id or not simulation_id:
            return jsonify({'success': False, 'message': 'Missing lesson_id or simulation_id'})
        
        # Get the lesson
        lesson = Lesson.query.get(lesson_id)
        if not lesson:
            return jsonify({'success': False, 'message': 'Lesson not found'})
        
        # Remove simulation from lesson's simulation_ids list
        if lesson.simulation_ids and simulation_id in lesson.simulation_ids:
            lesson.simulation_ids.remove(simulation_id)
            lesson.updated_at = datetime.utcnow()
            
            # Mark lesson as modified for SQLAlchemy
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(lesson, 'simulation_ids')
            
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Simulation removed from lesson successfully'})
        else:
            return jsonify({'success': False, 'message': 'Simulation not assigned to this lesson'})
            
    except Exception as e:
        current_app.logger.error(f"Error removing simulation from lesson: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@admin_simulation_bp.route('/available-for-lesson/<int:lesson_id>')
@login_required
@admin_required
def available_simulations_for_lesson(lesson_id):
    """Get simulations available for assignment to a lesson"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        
        # Get all published and active simulations
        available_simulations = Simulation.query.filter_by(
            is_active=True, 
            is_published=True
        ).order_by(Simulation.title).all()
        
        # Format for response
        simulations_data = []
        for sim in available_simulations:
            is_assigned = lesson.simulation_ids and sim.id in lesson.simulation_ids
            simulations_data.append({
                'id': sim.id,
                'title': sim.title,
                'simulation_type': sim.simulation_type,
                'difficulty': sim.difficulty,
                'estimated_duration': sim.estimated_duration,
                'is_assigned': is_assigned
            })
        
        return jsonify({
            'success': True,
            'simulations': simulations_data,
            'lesson': {
                'id': lesson.id,
                'title': lesson.title,
                'assigned_simulations': lesson.simulation_ids or []
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting available simulations for lesson {lesson_id}: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})