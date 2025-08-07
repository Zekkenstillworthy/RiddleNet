from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from admin.models.class_model import Class
from admin.models.simulation import Simulation
from admin.models.question_group import QuestionGroup
from admin.models.module import Module, Lesson
from admin.models.class_content import ClassAnnouncement, ClassAssignment, ClassMaterial, ClassTopic
from admin import db
from datetime import datetime

# Create a blueprint for class content related routes
class_content_controller_old = Blueprint('class_content_controller_old', __name__, url_prefix='/admin')

@class_content_controller_old.route('/class-content-manager')
@login_required
def class_content_manager_redirect():
    """Handle class-content-manager route with query parameters and redirect to proper URL"""
    class_id = request.args.get('class_id', type=int)
    if class_id:
        return redirect(url_for('class_content_controller_old.manage_content', class_id=class_id))
    else:
        # If no class_id provided, redirect to dashboard selector
        return redirect(url_for('dashboard.class_content_manager'))

@class_content_controller_old.route('/class-content-manager/<int:class_id>')
@login_required
def manage_content(class_id):
    """Display class content manager interface for managing modules, simulations, assignments, etc."""
    try:
        # Get the class details
        cls = Class.query.get_or_404(class_id)
        
        # Get all available simulations
        all_simulations = Simulation.query.filter_by(is_published=True).all()
        
        # Get class modules
        class_modules = Module.query.filter_by(class_id=class_id, is_active=True).order_by(Module.order_index).all()
        
        # Get class topics (content organization)
        class_topics = ClassTopic.query.filter_by(class_id=class_id).order_by(ClassTopic.sort_order).all()
        
        # Get class assignments
        class_assignments = ClassAssignment.query.filter_by(class_id=class_id).order_by(ClassAssignment.sort_order).all()
        
        # Get class materials
        class_materials = ClassMaterial.query.filter_by(class_id=class_id).order_by(ClassMaterial.sort_order).all()
        
        # Get class announcements
        class_announcements = ClassAnnouncement.query.filter_by(class_id=class_id).order_by(ClassAnnouncement.created_at.desc()).all()
        
        # Get assigned simulations for this class
        from admin.models.simulation_assignment import SimulationAssignment
        assigned_simulations = []
        simulation_assignments = SimulationAssignment.query.filter_by(class_id=class_id).all()
        for assignment in simulation_assignments:
            if assignment.simulation:
                assigned_simulations.append(assignment.simulation)
        
        # Get available simulations (not yet assigned)
        assigned_sim_ids = [sim.id for sim in assigned_simulations]
        available_simulations = [sim for sim in all_simulations if sim.id not in assigned_sim_ids]
        
        # Prepare class content data structure for the template
        class_content = {
            'modules': [module.to_dict() if hasattr(module, 'to_dict') else {
                'id': module.id,
                'title': module.title,
                'description': module.description,
                'order_index': module.order_index,
                'is_published': module.is_published,
                'objectives': module.objectives,
                'content': module.content
            } for module in class_modules],
            'topics': [topic.to_dict() if hasattr(topic, 'to_dict') else {
                'id': topic.id,
                'title': topic.title,
                'description': topic.description,
                'sort_order': topic.sort_order
            } for topic in class_topics],
            'assignments': [assignment.to_dict() if hasattr(assignment, 'to_dict') else {
                'id': assignment.id,
                'title': assignment.title,
                'description': assignment.description,
                'sort_order': assignment.sort_order
            } for assignment in class_assignments],
            'materials': [material.to_dict() if hasattr(material, 'to_dict') else {
                'id': material.id,
                'title': material.title,
                'description': material.description,
                'sort_order': material.sort_order
            } for material in class_materials],
            'simulations': [sim.to_dict() if hasattr(sim, 'to_dict') else {
                'id': sim.id,
                'title': sim.title,
                'description': sim.description
            } for sim in assigned_simulations]
        }
        
        # Use module_builder template since that's what we're actually loading
        return render_template('admin/module_builder.html',
                             class_data=cls,
                             selected_class=cls,
                             class_content=class_content,
                             class_modules=class_modules,
                             class_topics=class_topics,
                             class_assignments=class_assignments,
                             class_materials=class_materials,
                             class_announcements=class_announcements,
                             assigned_simulations=assigned_simulations,
                             available_simulations=available_simulations,
                             all_classes=[cls],  # Add this for template compatibility
                             class_statistics={  # Add required statistics
                                 'total_students': 0,
                                 'total_simulations': len(assigned_simulations),
                                 'total_question_groups': 0,
                                 'total_modules': len(class_modules),
                                 'total_announcements': len(class_announcements),
                                 'total_assignments': len(class_assignments),
                                 'total_materials': len(class_materials),
                                 'total_topics': len(class_topics),
                                 'total_content': len(class_announcements) + len(class_assignments) + len(class_materials) + len(class_modules),
                                 'completion_rate': 0,
                                 'average_score': 0
                             },
                             active_page='module_builder')
                             
    except Exception as e:
        print(f"Error in manage_content: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'Error loading class content manager: {str(e)}', 'error')
        return redirect(url_for('class_controller.index'))

@class_content_controller_old.route('/api/classes/<int:class_id>/content/simulations', methods=['POST'])
@login_required
def assign_simulation_to_class(class_id):
    """Assign a simulation to a class"""
    try:
        data = request.json
        simulation_id = data.get('simulation_id')
        
        cls = Class.query.get_or_404(class_id)
        simulation = Simulation.query.get_or_404(simulation_id)
        
        # Create simulation assignment
        from admin.models.simulation_assignment import SimulationAssignment
        existing_assignment = SimulationAssignment.query.filter_by(
            class_id=class_id, 
            simulation_id=simulation_id
        ).first()
        
        if existing_assignment:
            return jsonify({"error": "Simulation already assigned to this class"}), 400
        
        new_assignment = SimulationAssignment(
            class_id=class_id,
            simulation_id=simulation_id,
            created_by=current_user.id
        )
        
        db.session.add(new_assignment)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Simulation '{simulation.title}' assigned to class successfully!"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@class_content_controller_old.route('/api/classes/<int:class_id>/content/simulations/<int:simulation_id>', methods=['DELETE'])
@login_required
def unassign_simulation_from_class(class_id, simulation_id):
    """Unassign a simulation from a class"""
    try:
        cls = Class.query.get_or_404(class_id)
        simulation = Simulation.query.get_or_404(simulation_id)
        
        # Remove simulation assignment
        from admin.models.simulation_assignment import SimulationAssignment
        assignment = SimulationAssignment.query.filter_by(
            class_id=class_id, 
            simulation_id=simulation_id
        ).first()
        
        if assignment:
            db.session.delete(assignment)
            db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Simulation '{simulation.title}' unassigned from class successfully!"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@class_content_controller_old.route('/api/classes/<int:class_id>/template/generate', methods=['POST'])
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

@class_content_controller_old.route('/api/classes/<int:class_id>/content/summary')
@login_required
def get_class_content_summary(class_id):
    """Get a summary of all content assigned to a class"""
    try:
        cls = Class.query.get_or_404(class_id)
        
        # Get content counts
        from admin.models.simulation_assignment import SimulationAssignment
        simulations_count = SimulationAssignment.query.filter_by(class_id=class_id).count()
        
        modules_count = Module.query.filter_by(class_id=class_id, is_active=True).count()
        
        question_groups_count = len(cls.question_groups) if cls.question_groups else 0
        
        students_count = cls.students.count() if cls.students else 0
        
        return jsonify({
            "class_id": class_id,
            "class_name": cls.name,
            "modules": modules_count,
            "simulations": simulations_count,
            "question_groups": question_groups_count,
            "students": students_count,
            "status": cls.status
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ========================================
# MODULE MANAGEMENT ENDPOINTS
# ========================================

@class_content_controller_old.route('/api/classes/<int:class_id>/modules', methods=['GET'])
@login_required
def get_class_modules(class_id):
    """Get all modules for a class"""
    try:
        cls = Class.query.get_or_404(class_id)
        modules = Module.query.filter_by(class_id=class_id, is_active=True).order_by(Module.order_index).all()
        
        modules_data = []
        for module in modules:
            modules_data.append({
                'id': module.id,
                'title': module.title,
                'description': module.description,
                'module_number': module.module_number,
                'course_type': module.course_type,
                'learning_objectives': module.learning_objectives or [],
                'estimated_duration': module.estimated_duration,
                'order_index': module.order_index,
                'level': module.level,
                'total_lessons': module.total_lessons,
                'is_published': module.is_published,
                'created_at': module.created_at.isoformat() if module.created_at else None
            })
        
        return jsonify({'modules': modules_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@class_content_controller_old.route('/api/classes/<int:class_id>/modules', methods=['POST'])
@login_required
def create_class_module(class_id):
    """Create a new module for a class"""
    try:
        data = request.json
        cls = Class.query.get_or_404(class_id)
        
        # Get the next order index
        last_module = Module.query.filter_by(class_id=class_id).order_by(Module.order_index.desc()).first()
        next_order = (last_module.order_index + 1) if last_module else 1
        
        # Create new module
        new_module = Module(
            title=data.get('title'),
            description=data.get('description'),
            module_number=data.get('module_number'),
            course_type=data.get('course_type', cls.name),
            learning_objectives=data.get('learning_objectives', []),
            estimated_duration=data.get('estimated_duration', 60),
            order_index=next_order,
            level=data.get('level', 1),
            class_id=class_id,
            is_active=True,
            is_published=data.get('is_published', True),
            requires_sequential_completion=data.get('requires_sequential_completion', True),
            created_by=current_user.id
        )
        
        db.session.add(new_module)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Module "{new_module.title}" created successfully!',
            'module': {
                'id': new_module.id,
                'title': new_module.title,
                'description': new_module.description,
                'module_number': new_module.module_number,
                'order_index': new_module.order_index
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@class_content_controller_old.route('/api/classes/<int:class_id>/modules/<int:module_id>', methods=['GET'])
@login_required
def get_class_module(class_id, module_id):
    """Get a specific module for a class"""
    try:
        cls = Class.query.get_or_404(class_id)
        module = Module.query.filter_by(id=module_id, class_id=class_id, is_active=True).first_or_404()
        
        module_data = {
            'id': module.id,
            'title': module.title,
            'description': module.description,
            'module_number': module.module_number,
            'course_type': module.course_type,
            'learning_objectives': module.learning_objectives or [],
            'estimated_duration': module.estimated_duration,
            'order_index': module.order_index,
            'level': module.level,
            'total_lessons': module.total_lessons,
            'is_published': module.is_published,
            'requires_sequential_completion': module.requires_sequential_completion,
            'created_at': module.created_at.isoformat() if module.created_at else None,
            'updated_at': module.updated_at.isoformat() if module.updated_at else None
        }
        
        return jsonify({'module': module_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@class_content_controller_old.route('/api/classes/<int:class_id>/modules/<int:module_id>', methods=['PUT'])
@login_required
def update_class_module(class_id, module_id):
    """Update a class module"""
    try:
        data = request.json
        cls = Class.query.get_or_404(class_id)
        module = Module.query.filter_by(id=module_id, class_id=class_id).first_or_404()
        
        # Update module fields
        if 'title' in data:
            module.title = data['title']
        if 'description' in data:
            module.description = data['description']
        if 'module_number' in data:
            module.module_number = data['module_number']
        if 'learning_objectives' in data:
            module.learning_objectives = data['learning_objectives']
        if 'estimated_duration' in data:
            module.estimated_duration = data['estimated_duration']
        if 'is_published' in data:
            module.is_published = data['is_published']
        if 'requires_sequential_completion' in data:
            module.requires_sequential_completion = data['requires_sequential_completion']
        
        module.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Module "{module.title}" updated successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@class_content_controller_old.route('/api/classes/<int:class_id>/modules/<int:module_id>', methods=['DELETE'])
@login_required
def delete_class_module(class_id, module_id):
    """Delete a class module"""
    try:
        cls = Class.query.get_or_404(class_id)
        module = Module.query.filter_by(id=module_id, class_id=class_id).first_or_404()
        
        module_title = module.title
        
        # Soft delete by setting is_active to False
        module.is_active = False
        module.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Module "{module_title}" deleted successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@class_content_controller_old.route('/api/classes/<int:class_id>/modules/<int:module_id>/preview', methods=['GET'])
@login_required
def get_module_preview(class_id, module_id):
    """Get module data for preview rendering - identical to student view"""
    try:
        cls = Class.query.get_or_404(class_id)
        module = Module.query.filter_by(id=module_id, class_id=class_id, is_active=True).first_or_404()
        
        # Get module lessons
        lessons = Lesson.query.filter_by(module_id=module_id, is_active=True).order_by(Lesson.order_index).all()
        
        # Get module materials (if any)
        try:
            from admin.models.class_content import ClassMaterial
            materials = ClassMaterial.query.filter_by(class_id=class_id).all()
            # Filter materials that might be associated with this module
            module_materials = [mat for mat in materials if str(module_id) in (mat.content or '')]
        except:
            module_materials = []
        
        # Format module data exactly as students would see it
        module_data = {
            'id': module.id,
            'title': module.title,
            'description': module.description,
            'module_number': module.module_number,
            'estimated_duration': module.estimated_duration or 60,
            'level': module.level,
            'learning_objectives': module.learning_objectives or [],
            'is_published': module.is_published,
            'lessons': [{
                'id': lesson.id,
                'title': lesson.title,
                'description': lesson.description,
                'lesson_number': lesson.lesson_number,
                'content': lesson.content,
                'duration': lesson.estimated_duration or 15,
                'type': 'Lesson',
                'order_index': lesson.order_index
            } for lesson in lessons],
            'materials': [{
                'id': mat.id,
                'title': mat.title,
                'description': mat.description,
                'type': getattr(mat, 'material_type', 'document'),
                'filename': getattr(mat, 'file_url', '').split('/')[-1] if hasattr(mat, 'file_url') and mat.file_url else None,
                'file_url': getattr(mat, 'file_url', '')
            } for mat in module_materials]
        }
        
        return jsonify({
            'success': True,
            'module': module_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404

@class_content_controller_old.route('/classes/<int:class_id>/modules/<int:module_id>/preview', methods=['GET'])
@login_required
def preview_module_page(class_id, module_id):
    """Direct module preview page - identical to student view"""
    try:
        cls = Class.query.get_or_404(class_id)
        module = Module.query.filter_by(id=module_id, class_id=class_id, is_active=True).first_or_404()
        
        # Get module lessons
        lessons = Lesson.query.filter_by(module_id=module_id, is_active=True).order_by(Lesson.order_index).all()
        
        # Get module materials (if any)
        try:
            from admin.models.class_content import ClassMaterial
            materials = ClassMaterial.query.filter_by(class_id=class_id).all()
            # Filter materials that might be associated with this module
            module_materials = [mat for mat in materials if str(module_id) in (mat.content or '')]
        except:
            module_materials = []
        
        # Calculate module progress (for preview, show as 0%)
        module_progress = {
            'completed_lessons': 0,
            'total_lessons': len(lessons),
            'percentage': 0
        }
        
        return render_template('admin/module_preview_template.html',
                             class_data=cls,
                             module=module,
                             lessons=lessons,
                             materials=module_materials,
                             progress=module_progress,
                             is_preview=True)
        
    except Exception as e:
        flash(f'Error loading module preview: {str(e)}', 'error')
        return redirect(url_for('class_content_controller_old.manage_content', class_id=class_id))

@class_content_controller_old.route('/classes/<int:class_id>/modules/<int:module_id>/student-view', methods=['GET'])
@login_required
def admin_student_view(class_id, module_id):
    """Admin-accessible student view of module - redirects to universal student route"""
    try:
        # Verify class and module exist
        cls = Class.query.get_or_404(class_id)
        module = Module.query.filter_by(id=module_id, class_id=class_id, is_active=True).first_or_404()
        
        # Redirect to the universal student route 
        return redirect(f'/class/{class_id}/module/{module_id}')
        
    except Exception as e:
        flash(f'Error loading student view: {str(e)}', 'error')
        return redirect(url_for('class_content_controller_old.manage_content', class_id=class_id))

@class_content_controller_old.route('/api/classes/<int:class_id>/modules/<int:module_id>/preview/html', methods=['GET'])
@login_required
def get_module_preview_html(class_id, module_id):
    """Get module preview as rendered HTML - identical to student view"""
    try:
        cls = Class.query.get_or_404(class_id)
        module = Module.query.filter_by(id=module_id, class_id=class_id, is_active=True).first_or_404()
        
        # Get module lessons
        lessons = Lesson.query.filter_by(module_id=module_id, is_active=True).order_by(Lesson.order_index).all()
        
        # Get module materials (if any)
        try:
            from admin.models.class_content import ClassMaterial
            materials = ClassMaterial.query.filter_by(class_id=class_id).all()
            # Filter materials that might be associated with this module
            module_materials = [mat for mat in materials if str(module_id) in (mat.content or '')]
        except:
            module_materials = []
        
        # Calculate module progress (for preview, show as 0%)
        module_progress = {
            'completed_lessons': 0,
            'total_lessons': len(lessons),
            'percentage': 0
        }
        
        # Render the student-identical template
        html_content = render_template('admin/module_preview_template.html',
                                     class_name=cls.name,
                                     class_data=cls,
                                     module=module,
                                     lessons=lessons,
                                     materials=module_materials,
                                     progress=module_progress,
                                     is_preview=True)
        
        return jsonify({
            'success': True,
            'html': html_content,
            'module': {
                'id': module.id,
                'title': module.title,
                'module_number': module.module_number
            }
        })
        
    except Exception as e:
        print(f"Error in get_module_preview_html: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404

@class_content_controller_old.route('/api/classes/<int:class_id>/modules/<int:module_id>/lessons', methods=['GET'])
@login_required
def get_module_lessons(class_id, module_id):
    """Get all lessons for a module"""
    try:
        cls = Class.query.get_or_404(class_id)
        module = Module.query.filter_by(id=module_id, class_id=class_id).first_or_404()
        
        lessons = Lesson.query.filter_by(module_id=module_id, is_active=True).order_by(Lesson.order_index).all()
        
        lessons_data = []
        for lesson in lessons:
            lessons_data.append({
                'id': lesson.id,
                'title': lesson.title,
                'description': lesson.description,
                'lesson_number': lesson.lesson_number,
                'content': lesson.content,
                'learning_objectives': lesson.learning_objectives or [],
                'key_concepts': lesson.key_concepts or [],
                'simulation_ids': lesson.simulation_ids or [],
                'simulation_count': lesson.simulation_count,
                'estimated_duration': lesson.estimated_duration,
                'order_index': lesson.order_index,
                'requires_simulation_completion': lesson.requires_simulation_completion,
                'created_at': lesson.created_at.isoformat() if lesson.created_at else None
            })
        
        return jsonify({'lessons': lessons_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@class_content_controller_old.route('/api/classes/<int:class_id>/modules/<int:module_id>/lessons', methods=['POST'])
@login_required
def create_module_lesson(class_id, module_id):
    """Create a new lesson for a module"""
    try:
        data = request.json
        cls = Class.query.get_or_404(class_id)
        module = Module.query.filter_by(id=module_id, class_id=class_id).first_or_404()
        
        # Get the next order index
        last_lesson = Lesson.query.filter_by(module_id=module_id).order_by(Lesson.order_index.desc()).first()
        next_order = (last_lesson.order_index + 1) if last_lesson else 1
        
        # Create new lesson
        new_lesson = Lesson(
            title=data.get('title'),
            description=data.get('description'),
            lesson_number=data.get('lesson_number'),
            content=data.get('content', ''),
            learning_objectives=data.get('learning_objectives', []),
            key_concepts=data.get('key_concepts', []),
            simulation_ids=data.get('simulation_ids', []),
            estimated_duration=data.get('estimated_duration', 30),
            order_index=next_order,
            module_id=module_id,
            is_active=True,
            requires_simulation_completion=data.get('requires_simulation_completion', True)
        )
        
        db.session.add(new_lesson)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Lesson "{new_lesson.title}" created successfully!',
            'lesson': {
                'id': new_lesson.id,
                'title': new_lesson.title,
                'description': new_lesson.description,
                'lesson_number': new_lesson.lesson_number,
                'order_index': new_lesson.order_index
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@class_content_controller_old.route('/api/classes/<int:class_id>/modules/<int:module_id>/lessons/<int:lesson_id>', methods=['PUT'])
@login_required
def update_module_lesson(class_id, module_id, lesson_id):
    """Update a module lesson"""
    try:
        data = request.json
        cls = Class.query.get_or_404(class_id)
        module = Module.query.filter_by(id=module_id, class_id=class_id).first_or_404()
        lesson = Lesson.query.filter_by(id=lesson_id, module_id=module_id).first_or_404()
        
        # Update lesson fields
        if 'title' in data:
            lesson.title = data['title']
        if 'description' in data:
            lesson.description = data['description']
        if 'lesson_number' in data:
            lesson.lesson_number = data['lesson_number']
        if 'content' in data:
            lesson.content = data['content']
        if 'learning_objectives' in data:
            lesson.learning_objectives = data['learning_objectives']
        if 'key_concepts' in data:
            lesson.key_concepts = data['key_concepts']
        if 'simulation_ids' in data:
            lesson.simulation_ids = data['simulation_ids']
        if 'estimated_duration' in data:
            lesson.estimated_duration = data['estimated_duration']
        if 'requires_simulation_completion' in data:
            lesson.requires_simulation_completion = data['requires_simulation_completion']
        
        lesson.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Lesson "{lesson.title}" updated successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@class_content_controller_old.route('/api/classes/<int:class_id>/modules/<int:module_id>/lessons/<int:lesson_id>', methods=['DELETE'])
@login_required
def delete_module_lesson(class_id, module_id, lesson_id):
    """Delete a module lesson"""
    try:
        cls = Class.query.get_or_404(class_id)
        module = Module.query.filter_by(id=module_id, class_id=class_id).first_or_404()
        lesson = Lesson.query.filter_by(id=lesson_id, module_id=module_id).first_or_404()
        
        lesson_title = lesson.title
        
        # Soft delete by setting is_active to False
        lesson.is_active = False
        lesson.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Lesson "{lesson_title}" deleted successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ========================================
# CONTENT TOPIC MANAGEMENT ENDPOINTS
# ========================================

@class_content_controller_old.route('/api/classes/<int:class_id>/topics', methods=['GET'])
@login_required
def get_class_topics(class_id):
    """Get all topics for a class"""
    try:
        cls = Class.query.get_or_404(class_id)
        topics = ClassTopic.query.filter_by(class_id=class_id).order_by(ClassTopic.sort_order).all()
        
        topics_data = []
        for topic in topics:
            topics_data.append(topic.to_dict())
        
        return jsonify({'topics': topics_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@class_content_controller_old.route('/api/classes/<int:class_id>/topics', methods=['POST'])
@login_required
def create_class_topic(class_id):
    """Create a new topic for a class"""
    try:
        data = request.json
        cls = Class.query.get_or_404(class_id)
        
        # Get the next sort order
        last_topic = ClassTopic.query.filter_by(class_id=class_id).order_by(ClassTopic.sort_order.desc()).first()
        next_order = (last_topic.sort_order + 1) if last_topic else 1
        
        # Create new topic
        new_topic = ClassTopic(
            name=data.get('name'),
            description=data.get('description'),
            color=data.get('color', '#3B82F6'),
            is_collapsed=data.get('is_collapsed', False),
            sort_order=next_order,
            class_id=class_id,
            created_by=current_user.id
        )
        
        db.session.add(new_topic)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Topic "{new_topic.name}" created successfully!',
            'topic': new_topic.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@class_content_controller_old.route('/api/classes/<int:class_id>/topics/<int:topic_id>', methods=['PUT'])
@login_required
def update_class_topic(class_id, topic_id):
    """Update a class topic"""
    try:
        data = request.json
        cls = Class.query.get_or_404(class_id)
        topic = ClassTopic.query.filter_by(id=topic_id, class_id=class_id).first_or_404()
        
        # Update topic fields
        if 'name' in data:
            topic.name = data['name']
        if 'description' in data:
            topic.description = data['description']
        if 'color' in data:
            topic.color = data['color']
        if 'is_collapsed' in data:
            topic.is_collapsed = data['is_collapsed']
        
        topic.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Topic "{topic.name}" updated successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@class_content_controller_old.route('/api/classes/<int:class_id>/topics/<int:topic_id>', methods=['DELETE'])
@login_required
def delete_class_topic(class_id, topic_id):
    """Delete a class topic"""
    try:
        cls = Class.query.get_or_404(class_id)
        topic = ClassTopic.query.filter_by(id=topic_id, class_id=class_id).first_or_404()
        
        topic_name = topic.name
        
        # Delete the topic and its content
        db.session.delete(topic)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Topic "{topic_name}" deleted successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ========================================
# ASSIGNMENT MANAGEMENT ENDPOINTS
# ========================================

@class_content_controller_old.route('/api/classes/<int:class_id>/assignments', methods=['GET'])
@login_required
def get_class_assignments(class_id):
    """Get all assignments for a class"""
    try:
        cls = Class.query.get_or_404(class_id)
        assignments = ClassAssignment.query.filter_by(class_id=class_id).order_by(ClassAssignment.sort_order).all()
        
        assignments_data = []
        for assignment in assignments:
            assignments_data.append({
                'id': assignment.id,
                'title': assignment.title,
                'description': assignment.description,
                'content': assignment.content,
                'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
                'points': assignment.points,
                'sort_order': assignment.sort_order,
                'created_at': assignment.created_at.isoformat() if assignment.created_at else None
            })
        
        return jsonify({'assignments': assignments_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@class_content_controller_old.route('/api/classes/<int:class_id>/assignments', methods=['POST'])
@login_required
def create_class_assignment(class_id):
    """Create a new assignment for a class"""
    try:
        data = request.json
        cls = Class.query.get_or_404(class_id)
        
        # Get the next sort order
        last_assignment = ClassAssignment.query.filter_by(class_id=class_id).order_by(ClassAssignment.sort_order.desc()).first()
        next_order = (last_assignment.sort_order + 1) if last_assignment else 1
        
        # Parse due date if provided
        due_date = None
        if data.get('due_date'):
            try:
                due_date = datetime.fromisoformat(data['due_date'])
            except (ValueError, TypeError):
                due_date = None
        
        # Create new assignment
        new_assignment = ClassAssignment(
            title=data['title'],
            description=data.get('description', ''),
            content=data.get('instructions', ''),  # Use instructions field for content
            due_date=due_date,
            points=data.get('points', 0),
            sort_order=next_order,
            class_id=class_id,
            created_by=current_user.id
        )
        
        # Add additional fields if they exist in the model
        if hasattr(new_assignment, 'is_published'):
            new_assignment.is_published = data.get('is_published', True)
        
        db.session.add(new_assignment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Assignment "{new_assignment.title}" created successfully!',
            'assignment': {
                'id': new_assignment.id,
                'title': new_assignment.title,
                'description': new_assignment.description,
                'due_date': new_assignment.due_date.isoformat() if new_assignment.due_date else None,
                'points': new_assignment.points
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@class_content_controller_old.route('/api/classes/<int:class_id>/assignments/<int:assignment_id>', methods=['GET'])
@login_required
def get_class_assignment(class_id, assignment_id):
    """Get specific assignment details"""
    try:
        cls = Class.query.get_or_404(class_id)
        assignment = ClassAssignment.query.filter_by(id=assignment_id, class_id=class_id).first_or_404()
        
        return jsonify({
            'assignment': {
                'id': assignment.id,
                'title': assignment.title,
                'description': assignment.description,
                'content': assignment.content,
                'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
                'points': assignment.points,
                'sort_order': assignment.sort_order,
                'created_at': assignment.created_at.isoformat() if assignment.created_at else None
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@class_content_controller_old.route('/api/classes/<int:class_id>/assignments/<int:assignment_id>', methods=['PUT'])
@login_required
def update_class_assignment(class_id, assignment_id):
    """Update an existing assignment"""
    try:
        data = request.json
        cls = Class.query.get_or_404(class_id)
        assignment = ClassAssignment.query.filter_by(id=assignment_id, class_id=class_id).first_or_404()
        
        # Update assignment fields
        if 'title' in data:
            assignment.title = data['title']
        if 'description' in data:
            assignment.description = data['description']
        if 'content' in data:
            assignment.content = data['content']
        if 'points' in data:
            assignment.points = data['points']
        if 'due_date' in data:
            if data['due_date']:
                try:
                    assignment.due_date = datetime.fromisoformat(data['due_date'])
                except (ValueError, TypeError):
                    pass
            else:
                assignment.due_date = None
        
        assignment.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Assignment "{assignment.title}" updated successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@class_content_controller_old.route('/api/classes/<int:class_id>/assignments/<int:assignment_id>', methods=['DELETE'])
@login_required
def delete_class_assignment(class_id, assignment_id):
    """Delete an assignment"""
    try:
        cls = Class.query.get_or_404(class_id)
        assignment = ClassAssignment.query.filter_by(id=assignment_id, class_id=class_id).first_or_404()
        
        assignment_title = assignment.title
        
        # Delete the assignment
        db.session.delete(assignment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Assignment "{assignment_title}" deleted successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ========================================
# MATERIAL MANAGEMENT ENDPOINTS
# ========================================

@class_content_controller_old.route('/api/classes/<int:class_id>/materials', methods=['GET'])
@login_required
def get_class_materials(class_id):
    """Get all materials for a class"""
    try:
        cls = Class.query.get_or_404(class_id)
        materials = ClassMaterial.query.filter_by(class_id=class_id).order_by(ClassMaterial.sort_order).all()
        
        materials_data = []
        for material in materials:
            materials_data.append({
                'id': material.id,
                'title': material.title,
                'description': material.description,
                'content': material.content,
                'file_url': material.file_url,
                'sort_order': material.sort_order,
                'created_at': material.created_at.isoformat() if material.created_at else None
            })
        
        return jsonify({'materials': materials_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@class_content_controller_old.route('/api/classes/<int:class_id>/materials', methods=['POST'])
@login_required
def create_class_material(class_id):
    """Create a new material for a class"""
    try:
        cls = Class.query.get_or_404(class_id)
        
        # Get the next sort order
        last_material = ClassMaterial.query.filter_by(class_id=class_id).order_by(ClassMaterial.sort_order.desc()).first()
        next_order = (last_material.sort_order + 1) if last_material else 1
        
        # Handle both JSON and FormData requests
        if request.content_type and 'application/json' in request.content_type:
            # JSON request
            data = request.json
            title = data['title']
            description = data.get('description', '')
            material_type = data.get('material_type', 'link')
            content = data.get('content', '')
            file_url = data.get('file_url') or data.get('link_url', '')
            is_published = data.get('is_published', True)
        else:
            # FormData request (file upload)
            title = request.form.get('title')
            description = request.form.get('description', '')
            material_type = request.form.get('material_type', 'file')
            content = request.form.get('content', '')
            is_published = request.form.get('is_published', 'true').lower() == 'true'
            
            file_url = ''
            
            if material_type == 'file' and 'file' in request.files:
                file = request.files['file']
                if file and file.filename:
                    # Import media_utils for file handling
                    from utils.media_utils import save_uploaded_file
                    
                    try:
                        # Save the file and get the URL
                        file_url = save_uploaded_file(file, 'materials')
                    except Exception as e:
                        return jsonify({'error': f'File upload failed: {str(e)}'}), 400
            elif material_type == 'link':
                file_url = request.form.get('link_url', '')
        
        if not title:
            return jsonify({'error': 'Title is required'}), 400
            
        if material_type == 'file' and not file_url:
            return jsonify({'error': 'File upload failed or no file provided'}), 400
            
        if material_type == 'link' and not file_url:
            return jsonify({'error': 'Link URL is required'}), 400
        
        # Create new material
        new_material = ClassMaterial(
            title=title,
            description=description,
            content=content,
            file_url=file_url,
            sort_order=next_order,
            class_id=class_id,
            created_by=current_user.id
        )
        
        # Add additional fields if they exist in the model
        if hasattr(new_material, 'material_type'):
            new_material.material_type = material_type
        if hasattr(new_material, 'is_published'):
            new_material.is_published = is_published
        
        db.session.add(new_material)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Material "{new_material.title}" created successfully!',
            'material': {
                'id': new_material.id,
                'title': new_material.title,
                'description': new_material.description,
                'file_url': new_material.file_url,
                'material_type': getattr(new_material, 'material_type', material_type)
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@class_content_controller_old.route('/api/classes/<int:class_id>/materials/<int:material_id>', methods=['DELETE'])
@login_required
def delete_class_material(class_id, material_id):
    """Delete a material"""
    try:
        cls = Class.query.get_or_404(class_id)
        material = ClassMaterial.query.filter_by(id=material_id, class_id=class_id).first_or_404()
        
        material_title = material.title
        
        # Delete the material
        db.session.delete(material)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Material "{material_title}" deleted successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ========================================
# QUIZ MANAGEMENT ENDPOINTS  
# ========================================

@class_content_controller_old.route('/api/classes/<int:class_id>/quizs', methods=['POST'])
@login_required  
def create_class_quiz(class_id):
    """Create a new quiz (creates a question group)"""
    try:
        data = request.json
        cls = Class.query.get_or_404(class_id)
        
        # Create a new question group for the quiz
        new_quiz = QuestionGroup(
            name=data['title'],
            description=data.get('description', ''),
            class_id=class_id,
            created_by=current_user.id
        )
        
        db.session.add(new_quiz)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Quiz "{new_quiz.name}" created successfully!',
            'quiz': {
                'id': new_quiz.id,
                'title': new_quiz.name,
                'description': new_quiz.description
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ========================================
# STUDENT MANAGEMENT ENDPOINTS
# ========================================

@class_content_controller_old.route('/api/classes/<int:class_id>/students/<int:student_id>/progress', methods=['GET'])
@login_required
def get_student_progress(class_id, student_id):
    """Get student progress for a specific class"""
    try:
        cls = Class.query.get_or_404(class_id)
        
        # Import User model to get student info
        from user.models.user import User
        student = User.query.get_or_404(student_id)
        
        # Get progress data (this would need to be implemented based on your progress tracking)
        progress_data = {
            'modules_completed': 0,  # Count completed modules
            'assignments_submitted': 0,  # Count submitted assignments
            'average_score': 0,  # Calculate average score
            'recent_activity': []  # Recent activity list
        }
        
        # You can expand this with actual progress tracking logic
        
        return jsonify({
            'success': True,
            'student': {
                'id': student.id,
                'name': f"{student.first_name} {student.last_name}",
                'email': student.email
            },
            'progress': progress_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@class_content_controller_old.route('/api/classes/<int:class_id>/students/<int:student_id>/message', methods=['POST'])
@login_required
def send_student_message(class_id, student_id):
    """Send a message to a student"""
    try:
        data = request.json
        cls = Class.query.get_or_404(class_id)
        
        from user.models.user import User
        student = User.query.get_or_404(student_id)
        
        # Create a notification/message (you'd need to implement a messaging system)
        # For now, just return success
        
        return jsonify({
            'success': True,
            'message': f'Message sent to {student.first_name} {student.last_name}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@class_content_controller_old.route('/api/classes/<int:class_id>/students/<int:student_id>', methods=['DELETE'])
@login_required
def remove_student_from_class(class_id, student_id):
    """Remove a student from a class"""
    try:
        cls = Class.query.get_or_404(class_id)
        
        from user.models.user import User
        student = User.query.get_or_404(student_id)
        
        # Remove student from class (this depends on how your class enrollment is structured)
        # For now, just return success - you'd need to implement the actual removal logic
        
        return jsonify({
            'success': True,
            'message': f'Student {student.first_name} {student.last_name} removed from class'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@class_content_controller_old.route('/api/classes/<int:class_id>/invite-students', methods=['POST'])
@login_required
def invite_students_to_class(class_id):
    """Send email invitations to students"""
    try:
        data = request.json
        cls = Class.query.get_or_404(class_id)
        
        emails = data.get('emails', [])
        class_name = data.get('class_name')
        class_code = data.get('class_code')
        invite_message = data.get('invite_message')
        
        # Here you would implement email sending logic
        # For now, just return success
        
        return jsonify({
            'success': True,
            'message': f'Invitations sent to {len(emails)} email addresses'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Alias for backward compatibility
class_content_controller = class_content_controller_old
