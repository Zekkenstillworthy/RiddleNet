"""
Enhanced User Routes - Database-Driven Content
==============================================

These routes provide database-driven simulation loading.
All static content has been removed in favor of dynamic, admin-configurable content.

Features:
- Database simulation loading
- Unified troubleshoot.html template for all simulations  
- Sequential progression logic
- Learning path integration
"""

from flask import Blueprint, render_template, request, jsonify, abort, redirect, url_for, current_app
from flask_login import login_required, current_user
from services.database_simulation_service import DatabaseSimulationService
from admin.models.simulation import Simulation
from admin.models.class_model import Class

# Create blueprint for enhanced routes
enhanced_user_bp = Blueprint('enhanced_user', __name__)

@enhanced_user_bp.route('/networking1-simulations')
@login_required
def enhanced_networking1_simulations():
    """Enhanced networking1 simulations page - shows database content only"""
    try:
        # Get user's class (simplified - in real implementation, handle multiple classes)
        user_class_id = getattr(current_user, 'class_id', 7)  # Default to class 7
        
        # Get all simulations for this class
        simulation_service = DatabaseSimulationService()
        all_simulations = simulation_service.get_all_simulations_for_class(
            user_class_id, current_user.id
        )
        
        # Filter for Networking 1 content
        networking1_content = {
            'database': [sim for sim in all_simulations['database'] if 'networking 1' in sim.get('category', '').lower()],
            'learning_paths': all_simulations.get('learning_paths', [])
        }
        
        return render_template('user/simulations.html', 
                             content=networking1_content,
                             course_title="Networking 1 Simulations",
                             course_type="networking1")
                             
    except Exception as e:
        current_app.logger.error(f"Error in enhanced_networking1_simulations: {str(e)}")
        # Fallback to main class view
        return redirect(url_for('user.dashboard'))

@enhanced_user_bp.route('/networking2-simulations')
@login_required  
def enhanced_networking2_simulations():
    """Enhanced networking2 simulations page - shows database content only"""
    try:
        # Get user's class
        user_class_id = getattr(current_user, 'class_id', 9)  # Default to class 9
        
        # Get all simulations for this class
        simulation_service = DatabaseSimulationService()
        all_simulations = simulation_service.get_all_simulations_for_class(
            user_class_id, current_user.id
        )
        
        # Filter for Networking 2 content
        networking2_content = {
            'database': [sim for sim in all_simulations['database'] if 'networking 2' in sim.get('category', '').lower()],
            'learning_paths': all_simulations.get('learning_paths', [])
        }
        
        return render_template('user/simulations.html',
                             content=networking2_content, 
                             course_title="Networking 2 Simulations",
                             course_type="networking2")
                             
    except Exception as e:
        current_app.logger.error(f"Error in enhanced_networking2_simulations: {str(e)}")
        # Fallback to main class view
        return redirect(url_for('user.dashboard'))

@enhanced_user_bp.route('/class/<int:class_id>/enhanced')
@login_required
def enhanced_class_detail(class_id):
    """Enhanced class detail page with database + learning path modules"""
    try:
        # Get class information
        class_obj = Class.query.get_or_404(class_id)
        
        # Get all content for this class
        simulation_service = DatabaseSimulationService()
        all_content = simulation_service.get_all_simulations_for_class(
            class_id, current_user.id
        )
        
        # Organize content into modules
        modules = _organize_content_into_modules(all_content, class_obj)
        
        return render_template('user/enhanced_class_detail.html',
                             class_obj=class_obj,
                             modules=modules,
                             total_simulations=all_content['total_count'])
                             
    except Exception as e:
        current_app.logger.error(f"Error in enhanced_class_detail: {str(e)}")
        abort(500)

@enhanced_user_bp.route('/simulation/<simulation_id>')
@login_required
def unified_simulation_runner(simulation_id=None):
    """Unified simulation runner - handles database simulations only"""
    try:
        # Handle database simulation only (static content removed)
        simulation_data = _get_database_simulation_data(simulation_id)
        
        if not simulation_data:
            abort(404)
        
        # Always render using troubleshoot.html template for consistency
        return render_template('user/troubleshoot.html',
                             simulation=simulation_data,
                             is_unified=True)
                             
    except Exception as e:
        current_app.logger.error(f"Error in unified_simulation_runner: {str(e)}")
        abort(500)

def _organize_content_into_modules(all_content, class_obj):
    """Organize database content into module structure"""
    modules = []
    
    # Add database simulations as modules (static content removed)
    if all_content['database']:
        modules.append({
            'id': 'database_simulations',
            'title': 'Course Simulations', 
            'type': 'database',
            'simulations': all_content['database'],
            'progress': _calculate_module_progress(all_content['database'])
        })
    
    # Add learning paths if available
    if all_content.get('learning_paths'):
        for path in all_content['learning_paths']:
            modules.append({
                'id': f'learning_path_{path["id"]}',
                'title': path['title'],
                'type': 'learning_path',
                'simulations': path.get('simulations', []),
                'progress': path.get('progress', 0)
            })
    
    return modules
    
    return modules

def _calculate_module_progress(simulations):
    """Calculate progress percentage for a module"""
    if not simulations:
        return 0
    
    # TODO: Implement actual progress calculation based on user completion
    # For now, return 0 (not started)
    return 0

def _get_database_simulation_data(simulation_id):
    """Get database simulation data for unified rendering"""
    try:
        simulation = Simulation.query.get(simulation_id)
        if not simulation or not simulation.is_published:
            return None
        
        return {
            'id': simulation.id,
            'title': simulation.title,
            'description': simulation.description,
            'type': 'database',
            'step_definitions': simulation.step_definitions,
            'learning_objectives': simulation.learning_objectives,
            'validation_rules': simulation.validation_rules,
            'simulation_config': simulation.simulation_config,
            'is_static': False
        }
        
    except Exception as e:
        current_app.logger.error(f"Error getting database simulation {simulation_id}: {str(e)}")
        return None
