from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from instructor.controllers.troubleshooting_controller import TroubleshootingController
from flask_cors import cross_origin
from instructor.models.troubleshooting_progress import TroubleshootingProgress
from instructor.models.troubleshooting import Troubleshooting
from __init__ import db
from datetime import datetime
from utils.auth_decorators import instructor_required
from utils.render_utils import render_safe_template
import json

# Create the troubleshooting blueprint 
troubleshooting_bp = Blueprint('instructor_troubleshooting', __name__, url_prefix='/instructor/troubleshooting')

# Initialize controller
controller = TroubleshootingController()

@troubleshooting_bp.route('/', methods=['GET'])
@cross_origin()
def get_all_troubleshooting():
    """Get all troubleshooting scenarios"""
    return controller.get_all_troubleshooting()

@troubleshooting_bp.route('/<int:troubleshooting_id>', methods=['GET'])
@cross_origin()
def get_troubleshooting(troubleshooting_id):
    """Get a specific troubleshooting scenario by ID"""
    return controller.get_troubleshooting(troubleshooting_id)

@troubleshooting_bp.route('/', methods=['POST'])
@login_required
def create_troubleshooting():
    """Create a new troubleshooting scenario"""
    return controller.create_troubleshooting()

@troubleshooting_bp.route('/<int:troubleshooting_id>', methods=['PUT'])
@login_required
def update_troubleshooting(troubleshooting_id):
    """Update an existing troubleshooting scenario"""
    return controller.update_troubleshooting(troubleshooting_id)

@troubleshooting_bp.route('/<int:troubleshooting_id>', methods=['DELETE'])
@login_required
def delete_troubleshooting(troubleshooting_id):
    """Delete a troubleshooting scenario"""
    return controller.delete_troubleshooting(troubleshooting_id)
    
@troubleshooting_bp.route('/<int:troubleshooting_id>/preview', methods=['GET'])
@login_required
def preview_troubleshooting(troubleshooting_id):
    """Preview a troubleshooting scenario"""
    return jsonify(controller.preview_troubleshooting(troubleshooting_id))

@troubleshooting_bp.route('/<int:troubleshooting_id>/validate', methods=['POST'])
@cross_origin()
def validate_solution(troubleshooting_id):
    """Validate a user's solution to a troubleshooting scenario"""
    data = request.json
    user_solution = data.get('solution')
    time_taken = data.get('time_taken')
    hints_used = data.get('hints_used', 0)
    
    result = controller.validate_solution(troubleshooting_id, user_solution, time_taken, hints_used)
    
    # If the user is logged in and the solution is correct, record their progress
    if 'is_correct' in result and result['is_correct'] and current_user.is_authenticated:
        try:
            # Check if there's an existing progress record
            progress = TroubleshootingProgress.query.filter_by(
                user_id=current_user.id,
                troubleshooting_id=troubleshooting_id
            ).first()
            
            if progress:
                # Update existing progress
                progress.is_completed = True
                progress.completion_time = datetime.utcnow()
                progress.score = result['score']
                progress.attempts = progress.attempts + 1
                progress.hints_used = hints_used
                progress.user_solution = user_solution
            else:
                # Create new progress record
                progress = TroubleshootingProgress(
                    user_id=current_user.id,
                    troubleshooting_id=troubleshooting_id,
                    is_completed=True,
                    completion_time=datetime.utcnow(),
                    score=result['score'],
                    attempts=1,
                    hints_used=hints_used,
                    user_solution=user_solution
                )
                db.session.add(progress)
                
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error recording troubleshooting progress: {str(e)}")
    
    return jsonify(result)

# Admin Simulation Editor Routes
@troubleshooting_bp.route('/editor')
@login_required
@instructor_required
def simulation_editor_list():
    """Display list of troubleshooting simulations for editing"""
    try:
        simulations = Troubleshooting.query.filter_by(is_active=True).order_by(Troubleshooting.created_at.desc()).all()
        return render_safe_template('instructor/troubleshooting/editor_list.html', simulations=simulations)
    except Exception as e:
        flash(f'Error loading simulations: {str(e)}', 'error')
        return redirect(url_for('dashboard.index'))

@troubleshooting_bp.route('/editor/new')
@login_required
@instructor_required
def new_simulation_editor():
    """Create new troubleshooting simulation"""
    return render_safe_template('instructor/troubleshooting/edit_simulation.html', simulation=None)

@troubleshooting_bp.route('/editor/<int:simulation_id>')
@login_required
@instructor_required
def edit_simulation_editor(simulation_id):
    """Edit existing troubleshooting simulation"""
    try:
        simulation = Troubleshooting.query.get_or_404(simulation_id)
        return render_safe_template('instructor/troubleshooting/edit_simulation.html', simulation=simulation)
    except Exception as e:
        flash(f'Error loading simulation: {str(e)}', 'error')
        return redirect(url_for('instructor_troubleshooting.simulation_editor_list'))

@troubleshooting_bp.route('/editor/<int:simulation_id>/save', methods=['POST'])
@login_required
@instructor_required
def save_simulation_editor(simulation_id):
    """Save simulation changes from editor"""
    try:
        data = request.json
        simulation = Troubleshooting.query.get_or_404(simulation_id)
        
        # Update simulation properties
        simulation.title = data.get('title', simulation.title)
        simulation.description = data.get('description', simulation.description)
        simulation.difficulty = data.get('difficulty', simulation.difficulty)
        simulation.problem_type = data.get('problem_type', simulation.problem_type)
        simulation.scenario = data.get('scenario', simulation.scenario)
        simulation.solution = data.get('solution', simulation.solution)
        simulation.time_limit = data.get('time_limit', simulation.time_limit)
        simulation.base_score = data.get('base_score', simulation.base_score)
        simulation.time_bonus = data.get('time_bonus', simulation.time_bonus)
        simulation.hints = data.get('hints', [])
        simulation.initial_topology = data.get('initial_topology', {})
        simulation.solution_topology = data.get('solution_topology', {})
        simulation.required_steps = data.get('required_steps', [])
        simulation.updated_at = datetime.utcnow()
        
        # Handle collaboration settings
        collaboration_config = data.get('collaborationConfig', {})
        if collaboration_config:
            # Store collaboration settings as JSON if the model supports it
            if hasattr(simulation, 'collaboration_settings'):
                simulation.collaboration_settings = json.dumps(collaboration_config)
            # Alternatively, you might want to create a separate CollaborationSettings model
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Simulation updated successfully',
            'simulation_id': simulation.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error saving simulation: {str(e)}'
        }), 500

@troubleshooting_bp.route('/editor/save', methods=['POST'])
@login_required
@instructor_required
def create_simulation_editor():
    """Create new simulation from editor"""
    try:
        data = request.json
        
        simulation = Troubleshooting(
            title=data.get('title', 'New Simulation'),
            description=data.get('description', ''),
            difficulty=data.get('difficulty', 'medium'),
            problem_type=data.get('problem_type', 'network'),
            scenario=data.get('scenario', ''),
            solution=data.get('solution', ''),
            time_limit=data.get('time_limit', 15),
            base_score=data.get('base_score', 10),
            time_bonus=data.get('time_bonus', 5),
            hints=data.get('hints', []),
            initial_topology=data.get('initial_topology', {}),
            solution_topology=data.get('solution_topology', {}),
            required_steps=data.get('required_steps', []),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(simulation)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Simulation created successfully',
            'simulation_id': simulation.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating simulation: {str(e)}'
        }), 500

@troubleshooting_bp.route('/editor/<int:simulation_id>/duplicate', methods=['POST'])
@login_required
@instructor_required
def duplicate_simulation(simulation_id):
    """Duplicate an existing simulation"""
    try:
        original = Troubleshooting.query.get_or_404(simulation_id)
        
        # Create duplicate
        duplicate = Troubleshooting(
            title=f"Copy of {original.title}",
            description=original.description,
            difficulty=original.difficulty,
            problem_type=original.problem_type,
            scenario=original.scenario,
            solution=original.solution,
            time_limit=original.time_limit,
            base_score=original.base_score,
            time_bonus=original.time_bonus,
            hints=original.hints,
            initial_topology=original.initial_topology,
            solution_topology=original.solution_topology,
            required_steps=original.required_steps,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(duplicate)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Simulation duplicated successfully',
            'simulation_id': duplicate.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error duplicating simulation: {str(e)}'
        }), 500
