from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from utils.auth_decorators import instructor_required
from instructor.models.class_model import Class
from instructor.models.module import Module, Lesson
from __init__ import db

module_lesson_editor_bp = Blueprint('module_lesson_editor', __name__, url_prefix='/admin')

@module_lesson_editor_bp.route('/classes/<int:class_id>/modules/<int:module_id>/editor', methods=['GET'])
@login_required
@instructor_required
def edit_module_lessons(class_id, module_id):
    """
    Editable module lesson editor interface
    Combines module preview layout with lesson editing capabilities
    """
    try:
        # Get the class and module
        cls = Class.query.get_or_404(class_id)
        module = Module.query.filter_by(id=module_id, class_id=class_id, is_active=True).first_or_404()
        
        # Get module lessons
        lessons = Lesson.query.filter_by(module_id=module_id, is_active=True).order_by(Lesson.order_index).all()
        
        # Get selected lesson for editing
        selected_lesson_id = request.args.get('selected_lesson_id', type=int)
        selected_lesson = None
        if selected_lesson_id:
            selected_lesson = Lesson.query.get(selected_lesson_id)
        elif lessons:
            selected_lesson = lessons[0]  # Default to first lesson
        
        # Get media files for selected lesson if exists
        lesson_media = []
        if selected_lesson:
            try:
                # Get lesson media files from database
                lesson_media = db.session.execute(
                    "SELECT * FROM lesson_media_files WHERE lesson_id = ? AND upload_status = 'completed' ORDER BY created_at DESC",
                    (selected_lesson.id,)
                ).fetchall()
            except:
                lesson_media = []
        
        # Get module materials (if any)
        try:
            from instructor.models.class_content import ClassMaterial
            materials = ClassMaterial.query.filter_by(class_id=class_id).all()
            module_materials = [mat for mat in materials if str(module_id) in (mat.content or '')]
        except:
            module_materials = []
        
        # Calculate module progress
        module_progress = {
            'completed_lessons': 0,
            'total_lessons': len(lessons),
            'percentage': 0
        }
        
        # Get all class modules for navigation
        all_class_modules = Module.query.filter_by(class_id=class_id, is_active=True).order_by(Module.order_index).all()
        class_modules_data = []
        for mod in all_class_modules:
            class_modules_data.append({
                'id': mod.id,
                'title': mod.title,
                'module_number': mod.module_number,
                'estimated_duration': mod.estimated_duration,
                'total_lessons': getattr(mod, 'total_lessons', 0),
                'completion_percentage': 0
            })
        
        # Create module data
        module_data = {
            'id': module.id,
            'title': module.title,
            'description': module.description,
            'module_number': module.module_number,
            'estimated_duration': module.estimated_duration or 60,
            'level': getattr(module, 'level', 'Beginner'),
            'learning_objectives': module.learning_objectives or [],
            'is_published': module.is_published,
            'lessons': lessons,
            'class_id': module.class_id
        }
        
        return render_template('instructor/modules/lesson_editor.html',
                                  class_data=cls,
                                  module=module_data,
                                  lessons=lessons,
                                  selected_lesson=selected_lesson,
                                  lesson_media=lesson_media,
                                  materials=module_materials,
                                  progress=module_progress,
                                  class_modules=class_modules_data,
                                  is_editor=True)
        
    except Exception as e:
        flash(f'Error loading module lesson editor: {str(e)}', 'error')
        return redirect(url_for('class_content_controller_old.manage_content', class_id=class_id))

@module_lesson_editor_bp.route('/api/lessons/<int:lesson_id>/media', methods=['GET'])
@login_required
@instructor_required
def get_lesson_media(lesson_id):
    """Get media files for a specific lesson"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        
        # Get lesson media files
        media_files = db.session.execute(
            "SELECT * FROM lesson_media_files WHERE lesson_id = ? AND upload_status = 'completed' ORDER BY created_at DESC",
            (lesson_id,)
        ).fetchall()
        
        # Convert to list of dicts
        media_list = []
        for media in media_files:
            media_dict = dict(media._mapping) if hasattr(media, '_mapping') else dict(media)
            media_list.append(media_dict)
        
        return jsonify({
            'success': True,
            'media': media_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@module_lesson_editor_bp.route('/api/lessons/<int:lesson_id>/content', methods=['POST'])
@login_required
@instructor_required
def update_lesson_content(lesson_id):
    """Update lesson content"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        data = request.get_json()
        
        # Update lesson fields
        if 'title' in data:
            lesson.title = data['title']
        if 'description' in data:
            lesson.description = data['description']
        if 'content' in data:
            lesson.content = data['content']
        if 'learning_objectives' in data:
            lesson.learning_objectives = data['learning_objectives']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Lesson updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
