"""
Enhanced User Routes - Hybrid Static + Database Integration
=========================================================

These routes replace the existing user routes to provide:
1. Combined static + database simulation loading
2. Unified troubleshoot.html template for all simulations  
3. Sequential progression logic
4. Learning path integration

FIXES CRITICAL GAPS:
- Users now see database simulations alongside static ones
- All simulations render through unified template
- Learning paths appear as modules in classes
"""

from flask import Blueprint, render_template, request, jsonify, abort, redirect, url_for, current_app
from flask_login import login_required, current_user
from services.hybrid_simulation_service import hybrid_simulation_service
from admin.models.simulation import Simulation
from admin.models.learning_path import LearningPath
from admin.models.class_model import Class
# Static content imports removed - using database-driven content

# Create blueprint for enhanced routes
enhanced_user_bp = Blueprint('enhanced_user', __name__)

@enhanced_user_bp.route('/networking1-simulations')
@login_required
def enhanced_networking1_simulations():
    """Enhanced networking1 simulations page - shows static + database content"""
    try:
        # Get user's class (simplified - in real implementation, handle multiple classes)
        user_class_id = getattr(current_user, 'class_id', 7)  # Default to class 7
        
        # Get all simulations for this class
        all_simulations = hybrid_simulation_service.get_all_simulations_for_class(
            user_class_id, current_user.id
        )
        
        # Filter for Networking 1 content
        networking1_content = {
            'static': [sim for sim in all_simulations['static'] if 'Networking 1' in sim.get('category', '')],
            'database': [sim for sim in all_simulations['database'] if 'networking 1' in sim.get('category', '').lower()],
            'learning_paths': [lp for lp in all_simulations['learning_paths'] if 'Networking 1' in lp.get('course_level', '')]
        }
        
        return render_template('user/simulations.html', 
                             content=networking1_content,
                             course_title="Networking 1 Simulations",
                             course_type="networking1")
                             
    except Exception as e:
        current_app.logger.error(f"Error in enhanced_networking1_simulations: {str(e)}")
        # Fallback to original static content
        return redirect(url_for('user.networking1_simulations'))

@enhanced_user_bp.route('/networking2-simulations')
@login_required  
def enhanced_networking2_simulations():
    """Enhanced networking2 simulations page - shows static + database content"""
    try:
        # Get user's class
        user_class_id = getattr(current_user, 'class_id', 9)  # Default to class 9
        
        # Get all simulations for this class
        all_simulations = hybrid_simulation_service.get_all_simulations_for_class(
            user_class_id, current_user.id
        )
        
        # Filter for Networking 2 content
        networking2_content = {
            'static': [sim for sim in all_simulations['static'] if 'Networking 2' in sim.get('category', '')],
            'database': [sim for sim in all_simulations['database'] if 'networking 2' in sim.get('category', '').lower()],
            'learning_paths': [lp for lp in all_simulations['learning_paths'] if 'Networking 2' in lp.get('course_level', '')]
        }
        
        return render_template('user/simulations.html',
                             content=networking2_content, 
                             course_title="Networking 2 Simulations",
                             course_type="networking2")
                             
    except Exception as e:
        current_app.logger.error(f"Error in enhanced_networking2_simulations: {str(e)}")
        # Fallback to original static content
        return redirect(url_for('user.networking2_simulations'))

@enhanced_user_bp.route('/class/<int:class_id>/enhanced')
@login_required
def enhanced_class_detail(class_id):
    """Enhanced class detail page with static + database + learning path modules"""
    try:
        # Get class information
        class_obj = Class.query.get_or_404(class_id)
        
        # Get all content for this class
        all_content = hybrid_simulation_service.get_all_simulations_for_class(
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
@enhanced_user_bp.route('/simulation/static/<lesson_key>')  
@login_required
def unified_simulation_runner(simulation_id=None, lesson_key=None):
    """Unified simulation runner - handles both static and database simulations"""
    try:
        if lesson_key:
            # Handle static simulation
            simulation_data = _get_static_simulation_data(lesson_key)
        else:
            # Handle database simulation
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
    """Organize all content types into module structure"""
    modules = []
    
    # Add static content as modules
    if all_content['static']:
        networking1_sims = [sim for sim in all_content['static'] if 'Networking 1' in sim.get('category', '')]
        networking2_sims = [sim for sim in all_content['static'] if 'Networking 2' in sim.get('category', '')]
        
        if networking1_sims:
            modules.append({
                'id': 'static_networking1',
                'title': 'Networking Fundamentals',
                'type': 'static',
                'simulations': networking1_sims,
                'progress': _calculate_module_progress(networking1_sims)
            })
            
        if networking2_sims:
            modules.append({
                'id': 'static_networking2', 
                'title': 'Advanced Networking',
                'type': 'static',
                'simulations': networking2_sims,
                'progress': _calculate_module_progress(networking2_sims)
            })
    
    # Add learning paths as modules
    for learning_path in all_content['learning_paths']:
        modules.append({
            'id': f"learning_path_{learning_path['id']}",
            'title': learning_path['title'],
            'type': 'learning_path',
            'description': learning_path['description'],
            'simulations': learning_path['simulations'],
            'progress': _calculate_module_progress(learning_path['simulations']),
            'estimated_duration': learning_path.get('estimated_total_duration', 0)
        })
    
    # Add standalone database simulations as a module
    if all_content['database']:
        modules.append({
            'id': 'database_simulations',
            'title': 'Additional Simulations', 
            'type': 'database',
            'simulations': all_content['database'],
            'progress': _calculate_module_progress(all_content['database'])
        })
    
    return modules

def _calculate_module_progress(simulations):
    """Calculate progress percentage for a module"""
    if not simulations:
        return 0
    
    # TODO: Implement actual progress calculation based on user completion
    # For now, return 0 (not started)
    return 0

def _get_static_simulation_data(lesson_key):
    """Get static simulation data for unified rendering - now returns None as static content removed"""
    # Static content modules removed during refactoring
    # All content now comes from database
    return None
    
    # Convert to unified format for troubleshoot.html
    return {
        'id': f"static_{lesson_key}",
        'title': lesson_data.get('title', f'{course_type} - {lesson_key}'),
        'description': lesson_data.get('description', ''),
        'type': 'static',
        'content': lesson_data.get('content', ''),
        'step_definitions': _convert_static_content_to_steps(lesson_data),
        'learning_objectives': lesson_data.get('learning_objectives', []),
        'is_static': True
    }

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

def _convert_static_content_to_steps(lesson_data):
    """Convert static lesson content to step definitions for troubleshoot.html"""
    content = lesson_data.get('content', '')
    
    # Create basic step structure from content
    steps = [
        {
            'step_number': 1,
            'title': 'Overview',
            'instruction': lesson_data.get('description', ''),
            'type': 'reading',
            'content': content[:500] + '...' if len(content) > 500 else content
        },
        {
            'step_number': 2, 
            'title': 'Interactive Exercise',
            'instruction': 'Complete the simulation exercise',
            'type': 'simulation',
            'content': content
        }
    ]
    
    return steps
