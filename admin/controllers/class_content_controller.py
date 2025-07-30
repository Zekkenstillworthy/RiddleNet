from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from admin.models.class_model import Class
from admin.models.simulation import Simulation
from admin.models.learning_path import LearningPath
from admin.models.question_group import QuestionGroup
from admin import db
from datetime import datetime

# Create a blueprint for class content related routes
class_content_controller = Blueprint('class_content_controller', __name__, url_prefix='/admin')

@class_content_controller.route('/class/<int:class_id>/content')
@login_required
def class_content_editor(class_id):
    """Display class content editor for managing simulations, learning paths, etc."""
    try:
        # Get the class details
        cls = Class.query.get_or_404(class_id)
        
        # Get all available simulations
        all_simulations = Simulation.query.filter_by(is_published=True).all()
        
        # Get all available learning paths
        all_learning_paths = LearningPath.query.all()
        
        # Get assigned content for this class (you may need to create relationships for this)
        # For now, we'll get based on naming conventions or categories
        assigned_simulations = []
        assigned_learning_paths = []
        
        # Filter simulations based on class name/level
        class_level = cls.name.lower()
        for sim in all_simulations:
            if class_level in sim.category.lower() if sim.category else False:
                assigned_simulations.append(sim)
        
        # Filter learning paths based on class name/level
        for lp in all_learning_paths:
            if class_level in lp.course_level.lower() if hasattr(lp, 'course_level') and lp.course_level else False:
                assigned_learning_paths.append(lp)
        
        # Get available content (not yet assigned)
        available_simulations = [sim for sim in all_simulations if sim not in assigned_simulations]
        available_learning_paths = [lp for lp in all_learning_paths if lp not in assigned_learning_paths]
        
        return render_template('admin/class_content_editor.html',
                             class_data=cls,
                             assigned_simulations=assigned_simulations,
                             available_simulations=available_simulations,
                             assigned_learning_paths=assigned_learning_paths,
                             available_learning_paths=available_learning_paths,
                             active_page='classes')
                             
    except Exception as e:
        flash(f'Error loading class content editor: {str(e)}', 'error')
        return redirect(url_for('class_controller.index'))

@class_content_controller.route('/api/classes/<int:class_id>/content/simulations', methods=['POST'])
@login_required
def assign_simulation_to_class(class_id):
    """Assign a simulation to a class"""
    try:
        data = request.json
        simulation_id = data.get('simulation_id')
        
        cls = Class.query.get_or_404(class_id)
        simulation = Simulation.query.get_or_404(simulation_id)
        
        # Update simulation category to include class name
        if cls.name.lower() not in simulation.category.lower():
            simulation.category = f"{simulation.category}, {cls.name}"
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Simulation '{simulation.title}' assigned to class successfully!"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@class_content_controller.route('/api/classes/<int:class_id>/content/simulations/<int:simulation_id>', methods=['DELETE'])
@login_required
def unassign_simulation_from_class(class_id, simulation_id):
    """Unassign a simulation from a class"""
    try:
        cls = Class.query.get_or_404(class_id)
        simulation = Simulation.query.get_or_404(simulation_id)
        
        # Remove class name from simulation category
        if cls.name in simulation.category:
            simulation.category = simulation.category.replace(f", {cls.name}", "").replace(cls.name, "").strip()
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Simulation '{simulation.title}' unassigned from class successfully!"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@class_content_controller.route('/api/classes/<int:class_id>/content/learning-paths', methods=['POST'])
@login_required
def assign_learning_path_to_class(class_id):
    """Assign a learning path to a class"""
    try:
        data = request.json
        learning_path_id = data.get('learning_path_id')
        
        cls = Class.query.get_or_404(class_id)
        learning_path = LearningPath.query.get_or_404(learning_path_id)
        
        # Update learning path course level to include class name
        if hasattr(learning_path, 'course_level'):
            if cls.name.lower() not in learning_path.course_level.lower():
                learning_path.course_level = f"{learning_path.course_level}, {cls.name}"
        else:
            learning_path.course_level = cls.name
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Learning path '{learning_path.title}' assigned to class successfully!"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@class_content_controller.route('/api/classes/<int:class_id>/content/learning-paths/<int:path_id>', methods=['DELETE'])
@login_required
def unassign_learning_path_from_class(class_id, path_id):
    """Unassign a learning path from a class"""
    try:
        cls = Class.query.get_or_404(class_id)
        learning_path = LearningPath.query.get_or_404(path_id)
        
        # Remove class name from learning path course level
        if hasattr(learning_path, 'course_level') and cls.name in learning_path.course_level:
            learning_path.course_level = learning_path.course_level.replace(f", {cls.name}", "").replace(cls.name, "").strip()
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Learning path '{learning_path.title}' unassigned from class successfully!"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@class_content_controller.route('/api/classes/<int:class_id>/template/generate', methods=['POST'])
@login_required
def generate_class_template(class_id):
    """Generate or regenerate class template"""
    try:
        cls = Class.query.get_or_404(class_id)
        
        # Import the template generator
        from admin.services.enhanced_class_template_generator import enhanced_template_generator
        
        # Generate the template
        result = enhanced_template_generator.generate_class_template(cls)
        
        if result.get('success'):
            return jsonify({
                "success": True,
                "message": f"Class template generated successfully for {cls.name}!",
                "template_path": result.get('template_path'),
                "route_registered": result.get('route_registered', False)
            })
        else:
            return jsonify({
                "error": result.get('error', 'Failed to generate template')
            }), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@class_content_controller.route('/api/classes/<int:class_id>/content/summary')
@login_required
def get_class_content_summary(class_id):
    """Get a summary of all content assigned to a class"""
    try:
        cls = Class.query.get_or_404(class_id)
        
        # Get content counts
        simulations_count = Simulation.query.filter(
            Simulation.category.contains(cls.name),
            Simulation.is_published == True
        ).count()
        
        learning_paths_count = LearningPath.query.filter(
            LearningPath.course_level.contains(cls.name) if hasattr(LearningPath, 'course_level') else False
        ).count()
        
        question_groups_count = len(cls.question_groups) if cls.question_groups else 0
        
        students_count = cls.students.count() if cls.students else 0
        
        return jsonify({
            "class_id": class_id,
            "class_name": cls.name,
            "simulations": simulations_count,
            "learning_paths": learning_paths_count,
            "question_groups": question_groups_count,
            "students": students_count,
            "status": cls.status
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
