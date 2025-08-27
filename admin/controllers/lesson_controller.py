"""


Lesson Controller for Admin Interface
Provides comprehensive lesson management functionality
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from admin import db
from admin.models.module import Module, Lesson, LessonProgress
from admin.models.class_model import Class
from admin.models.simulation import Simulation
from utils.render_utils import render_safe_template
from datetime import datetime
import json

lesson_bp = Blueprint('lesson', __name__, url_prefix='/admin')

@lesson_bp.route('/lessons')
@login_required
def index():
    """Display enhanced lesson content editor interface with module preview styling"""
    print(f"DEBUG LESSON_INDEX: Enhanced lessons content editor route called")
    try:
        print(f"DEBUG LESSON_INDEX: Querying for all active lessons")
        # Get all lessons with their module and class information
        lessons = db.session.query(Lesson)\
            .join(Module)\
            .join(Class)\
            .filter(Lesson.is_active == True)\
            .order_by(Class.name, Module.module_number, Lesson.order_index)\
            .all()
        
        print(f"DEBUG LESSON_INDEX: Found {len(lessons)} lessons")
        
        # Get class filter options (filter by ownership)
        if hasattr(current_user, 'role') and current_user.role == 'super_admin':
            classes = Class.query.filter_by(status='active').order_by(Class.name).all()
        else:
            classes = Class.query.filter_by(status='active', created_by=getattr(current_user, 'id', None)).order_by(Class.name).all()
        print(f"DEBUG LESSON_INDEX: Found {len(classes)} active classes")
        
        # Get selected lesson for editing
        selected_lesson_id = request.args.get('selected_lesson_id', type=int) or request.args.get('lesson_id', type=int)
        selected_lesson = None
        
        if selected_lesson_id:
            selected_lesson = Lesson.query.get(selected_lesson_id)
            print(f"DEBUG LESSON_INDEX: Selected lesson: {selected_lesson.title if selected_lesson else 'Not found'}")
        
        # Get filter parameters (keeping for backward compatibility)
        class_filter = request.args.get('class_id', type=int)
        module_filter = request.args.get('module_id', type=int)
        print(f"DEBUG LESSON_INDEX: Filters - class_id: {class_filter}, module_id: {module_filter}")
        
        if class_filter:
            lessons = [l for l in lessons if l.module.class_id == class_filter]
            print(f"DEBUG LESSON_INDEX: Filtered by class, now {len(lessons)} lessons")
        if module_filter:
            lessons = [l for l in lessons if l.module_id == module_filter]
            print(f"DEBUG LESSON_INDEX: Filtered by module, now {len(lessons)} lessons")
        
        # Get media files for selected lesson if exists
        lesson_media = []
        if selected_lesson:
            try:
                # Get lesson media files from database
                lesson_media = db.session.execute(
                    "SELECT * FROM lesson_media_files WHERE lesson_id = ? AND upload_status = 'completed' ORDER BY created_at DESC",
                    (selected_lesson.id,)
                ).fetchall()
                print(f"DEBUG LESSON_INDEX: Found {len(lesson_media)} media files for lesson")
            except:
                print(f"DEBUG LESSON_INDEX: No media files table found, using empty list")
        
        print(f"DEBUG LESSON_INDEX: Rendering enhanced lessons content editor template")
        return render_safe_template('admin/lessons/enhanced_editor.html',
                                   lessons=lessons,
                                   classes=classes,
                                   selected_lesson=selected_lesson,
                                   lesson_media=lesson_media,
                                   class_filter=class_filter,
                                   module_filter=module_filter)
    except Exception as e:
        print(f"DEBUG LESSON_INDEX: ERROR in enhanced lesson content editor: {str(e)}")
        import traceback
        print(f"DEBUG LESSON_INDEX: Traceback: {traceback.format_exc()}")
        current_app.logger.error(f"Error in enhanced lesson content editor: {str(e)}")
        flash('Error loading lesson editor', 'error')
        return redirect(url_for('dashboard.index'))

@lesson_bp.route('/lessons/<int:lesson_id>')
@login_required
def view_lesson(lesson_id):
    """View lesson details"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        
        # Get lesson statistics
        total_students = lesson.module.class_obj.students.count()
        completed_count = LessonProgress.query.filter_by(
            lesson_id=lesson_id, is_completed=True
        ).count()
        
        # Get recent student progress
        recent_progress = db.session.query(LessonProgress)\
            .join(LessonProgress.user)\
            .filter(LessonProgress.lesson_id == lesson_id)\
            .order_by(LessonProgress.last_accessed.desc())\
            .limit(10).all()
        
        # Get lesson simulations
        lesson_simulations = []
        if lesson.simulation_ids:
            lesson_simulations = Simulation.query.filter(
                Simulation.id.in_(lesson.simulation_ids),
                Simulation.is_active == True
            ).all()
        
        stats = {
            'total_students': total_students,
            'completed_count': completed_count,
            'completion_rate': round((completed_count / total_students * 100) if total_students > 0 else 0, 1),
            'average_time': 0  # Calculate from progress data
        }
        
        if recent_progress:
            total_time = sum(p.total_time_spent for p in recent_progress if p.total_time_spent)
            stats['average_time'] = round(total_time / len(recent_progress) / 60, 1) if total_time > 0 else 0
        
        return render_safe_template('admin/lessons/detail.html',
                                   lesson=lesson,
                                   stats=stats,
                                   recent_progress=recent_progress,
                                   simulations=lesson_simulations)
    except Exception as e:
        current_app.logger.error(f"Error viewing lesson {lesson_id}: {str(e)}")
        flash('Error loading lesson details', 'error')
        return redirect(url_for('lesson.index'))

@lesson_bp.route('/classes/<int:class_id>/modules/<int:module_id>/lessons/new')
@login_required
def new_lesson(class_id, module_id):
    """Create new lesson form"""
    try:
        class_obj = Class.query.get_or_404(class_id)
        module = Module.query.filter_by(id=module_id, class_id=class_id).first_or_404()
        
        # Get available simulations for this class
        simulations = Simulation.query.filter(
            Simulation.is_active == True,
            Simulation.is_published == True
        ).order_by(Simulation.title).all()
        
        # Get next lesson number
        last_lesson = Lesson.query.filter_by(module_id=module_id)\
            .order_by(Lesson.order_index.desc()).first()
        next_number = f"{module.module_number}.{(last_lesson.order_index + 1) if last_lesson else 1}"
        
        return render_safe_template('admin/lessons/form.html',
                                   class_obj=class_obj,
                                   module=module,
                                   lesson=None,
                                   simulations=simulations,
                                   suggested_number=next_number,
                                   action='Create')
    except Exception as e:
        current_app.logger.error(f"Error creating lesson form: {str(e)}")
        flash('Error loading lesson form', 'error')
        return redirect(url_for('class_controller.class_overview', class_id=class_id))

@lesson_bp.route('/classes/<int:class_id>/modules/<int:module_id>/lessons', methods=['POST'])
@login_required
def create_lesson(class_id, module_id):
    """Create new lesson"""
    try:
        class_obj = Class.query.get_or_404(class_id)
        module = Module.query.filter_by(id=module_id, class_id=class_id).first_or_404()
        
        # Get form data
        data = request.form
        
        # Get next order index
        last_lesson = Lesson.query.filter_by(module_id=module_id)\
            .order_by(Lesson.order_index.desc()).first()
        next_order = (last_lesson.order_index + 1) if last_lesson else 1
        
        # Process simulation IDs
        simulation_ids = request.form.getlist('simulation_ids')
        simulation_ids = [int(sid) for sid in simulation_ids if sid]
        
        # Process learning objectives and key concepts
        objectives = [obj.strip() for obj in data.get('learning_objectives', '').split('\n') if obj.strip()]
        concepts = [concept.strip() for concept in data.get('key_concepts', '').split('\n') if concept.strip()]
        
        # Create lesson
        lesson = Lesson(
            title=data.get('title'),
            description=data.get('description'),
            lesson_number=data.get('lesson_number'),
            content=data.get('content', ''),
            learning_objectives=objectives,
            key_concepts=concepts,
            simulation_ids=simulation_ids,
            estimated_duration=int(data.get('estimated_duration', 30)),
            order_index=next_order,
            module_id=module_id,
            is_active=True,
            requires_simulation_completion=bool(data.get('requires_simulation_completion'))
        )
        
        db.session.add(lesson)
        db.session.commit()
        
        flash(f'Lesson "{lesson.title}" created successfully!', 'success')
        return redirect(url_for('class_controller.class_overview', class_id=class_id))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating lesson: {str(e)}")
        flash('Error creating lesson', 'error')
        return redirect(url_for('lesson.new_lesson', class_id=class_id, module_id=module_id))

@lesson_bp.route('/lessons/<int:lesson_id>/edit')
@login_required
def edit_lesson(lesson_id):
    """Redirect to the lesson content editor interface"""
    try:
        # Ensure lesson exists (to return 404 if not)
        lesson = Lesson.query.get_or_404(lesson_id)
        # Redirect to main lesson editor with lesson selected
        return redirect(url_for('lesson.index', lesson_id=lesson_id))
    except Exception as e:
        current_app.logger.error(f"Error loading lesson editor for lesson {lesson_id}: {str(e)}")
        flash('Error loading lesson editor', 'error')
        return redirect(url_for('dashboard.index'))

@lesson_bp.route('/lessons/<int:lesson_id>', methods=['POST'])
@login_required
def update_lesson(lesson_id):
    """Update lesson"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        data = request.form
        
        # Update lesson fields
        lesson.title = data.get('title')
        lesson.description = data.get('description')
        lesson.lesson_number = data.get('lesson_number')
        lesson.content = data.get('content', '')
        lesson.estimated_duration = int(data.get('estimated_duration', 30))
        lesson.requires_simulation_completion = bool(data.get('requires_simulation_completion'))
        
        # Process simulation IDs
        simulation_ids = request.form.getlist('simulation_ids')
        lesson.simulation_ids = [int(sid) for sid in simulation_ids if sid]
        
        # Process learning objectives and key concepts
        objectives = [obj.strip() for obj in data.get('learning_objectives', '').split('\n') if obj.strip()]
        concepts = [concept.strip() for concept in data.get('key_concepts', '').split('\n') if concept.strip()]
        lesson.learning_objectives = objectives
        lesson.key_concepts = concepts
        
        lesson.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash(f'Lesson "{lesson.title}" updated successfully!', 'success')
        return redirect(url_for('lesson.view_lesson', lesson_id=lesson_id))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating lesson: {str(e)}")
        flash('Error updating lesson', 'error')
        return redirect(url_for('lesson.edit_lesson', lesson_id=lesson_id))

@lesson_bp.route('/lessons/<int:lesson_id>/delete', methods=['POST'])
@login_required
def delete_lesson(lesson_id):
    """Delete lesson"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        class_id = lesson.module.class_id
        lesson_title = lesson.title
        
        # Soft delete by setting is_active to False
        lesson.is_active = False
        lesson.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash(f'Lesson "{lesson_title}" deleted successfully!', 'success')
        return redirect(url_for('class_controller.class_overview', class_id=class_id))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting lesson: {str(e)}")
        flash('Error deleting lesson', 'error')
        return redirect(url_for('lesson.view_lesson', lesson_id=lesson_id))

# API Routes for AJAX requests
@lesson_bp.route('/api/lessons/<int:lesson_id>')
@login_required
def api_get_lesson(lesson_id):
    """Get lesson data as JSON"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        
        return jsonify({
            'success': True,
            'lesson': lesson.to_dict(include_simulations=True)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lesson_bp.route('/api/lessons/<int:lesson_id>/progress')
@login_required
def api_lesson_progress(lesson_id):
    """Get lesson progress analytics"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        
        # Get all student progress for this lesson
        progress_data = db.session.query(LessonProgress)\
            .join(LessonProgress.user)\
            .filter(LessonProgress.lesson_id == lesson_id)\
            .all()
        
        total_students = lesson.module.class_obj.students.count()
        completed_count = len([p for p in progress_data if p.is_completed])
        
        analytics = {
            'total_students': total_students,
            'started_count': len(progress_data),
            'completed_count': completed_count,
            'completion_rate': round((completed_count / total_students * 100) if total_students > 0 else 0, 1),
            'average_time_minutes': 0,
            'average_progress': 0,
            'progress_distribution': {
                'not_started': total_students - len(progress_data),
                'in_progress': len(progress_data) - completed_count,
                'completed': completed_count
            }
        }
        
        if progress_data:
            total_time = sum(p.total_time_spent for p in progress_data if p.total_time_spent)
            total_progress = sum(p.progress_percentage for p in progress_data)
            
            analytics['average_time_minutes'] = round(total_time / len(progress_data) / 60, 1) if total_time > 0 else 0
            analytics['average_progress'] = round(total_progress / len(progress_data), 1)
        
        return jsonify({
            'success': True,
            'analytics': analytics
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lesson_bp.route('/api/modules/<int:module_id>/lessons/reorder', methods=['POST'])
@login_required
def api_reorder_lessons(module_id):
    """Reorder lessons within a module"""
    try:
        module = Module.query.get_or_404(module_id)
        data = request.json
        lesson_ids = data.get('lesson_ids', [])
        
        # Update order indices
        for index, lesson_id in enumerate(lesson_ids):
            lesson = Lesson.query.filter_by(id=lesson_id, module_id=module_id).first()
            if lesson:
                lesson.order_index = index + 1
                lesson.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Lesson order updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@lesson_bp.route('/api/lessons/<int:lesson_id>')
@login_required
def get_lesson_api(lesson_id):
    """Get lesson data for API"""
    print(f"DEBUG LESSON_API: get_lesson_api called with lesson_id={lesson_id}")
    try:
        print(f"DEBUG LESSON_API: Looking for lesson with id={lesson_id}")
        lesson = Lesson.query.get_or_404(lesson_id)
        print(f"DEBUG LESSON_API: Found lesson: {lesson.title if lesson else 'None'}")
        
        lesson_data = {
            'id': lesson.id,
            'title': lesson.title,
            'description': lesson.description,
            'lesson_number': lesson.lesson_number,
            'content': lesson.content,
            'estimated_duration': lesson.estimated_duration,
            'order_index': lesson.order_index,
            'learning_objectives': lesson.learning_objectives or [],
            'key_concepts': lesson.key_concepts or [],
            'requires_simulation_completion': lesson.requires_simulation_completion,
            'simulation_ids': lesson.simulation_ids or [],
            'module_id': lesson.module_id,
            'is_active': lesson.is_active
        }
        print(f"DEBUG LESSON_API: Returning lesson data for: {lesson.title}")
        return jsonify({'success': True, 'lesson': lesson_data})
    except Exception as e:
        print(f"DEBUG LESSON_API: ERROR in get_lesson_api: {str(e)}")
        import traceback
        print(f"DEBUG LESSON_API: Traceback: {traceback.format_exc()}")
        current_app.logger.error(f"Error getting lesson data: {str(e)}")
        return jsonify({'success': False, 'message': 'Error loading lesson data'})

@lesson_bp.route('/api/lessons/<int:lesson_id>/update', methods=['PUT'])
@login_required  
def update_lesson_api(lesson_id):
    """Update lesson via API"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        data = request.get_json()
        
        # Update lesson fields
        lesson.title = data.get('title', lesson.title)
        lesson.description = data.get('description', lesson.description)
        lesson.lesson_number = data.get('lesson_number', lesson.lesson_number)
        lesson.content = data.get('content', lesson.content)
        lesson.estimated_duration = data.get('estimated_duration', lesson.estimated_duration)
        lesson.order_index = data.get('order_index', lesson.order_index)
        lesson.requires_simulation_completion = data.get('requires_simulation_completion', lesson.requires_simulation_completion)
        
        # Update learning objectives and key concepts
        lesson.learning_objectives = data.get('learning_objectives', lesson.learning_objectives)
        lesson.key_concepts = data.get('key_concepts', lesson.key_concepts)
        
        lesson.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Lesson updated successfully',
            'lesson': {
                'id': lesson.id,
                'title': lesson.title,
                'lesson_number': lesson.lesson_number,
                'description': lesson.description
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating lesson via API: {str(e)}")
        return jsonify({'success': False, 'message': 'Error updating lesson'})

@lesson_bp.route('/api/lessons/<int:lesson_id>/media/upload', methods=['POST'])
@login_required
def upload_lesson_media(lesson_id):
    """Upload media files for a lesson"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        
        if 'files' not in request.files:
            return jsonify({'success': False, 'message': 'No files provided'})
        
        files = request.files.getlist('files')
        uploaded_files = []
        
        for file in files:
            if file and file.filename:
                # Generate secure filename
                import os
                import uuid
                from werkzeug.utils import secure_filename
                
                filename = secure_filename(file.filename)
                file_extension = os.path.splitext(filename)[1]
                unique_filename = f"{uuid.uuid4()}{file_extension}"
                
                # Determine file type
                file_type = 'document'
                if file.content_type.startswith('video/'):
                    file_type = 'video'
                elif file.content_type.startswith('image/'):
                    file_type = 'image'
                
                # Create upload directory if it doesn't exist
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'lessons', str(lesson_id))
                os.makedirs(upload_dir, exist_ok=True)
                
                # Save file
                file_path = os.path.join(upload_dir, unique_filename)
                file.save(file_path)
                
                # Create relative path for URL
                relative_path = f"static/uploads/lessons/{lesson_id}/{unique_filename}"
                
                # Store file info (in a real app, you'd save this to database)
                file_info = {
                    'id': str(uuid.uuid4()),
                    'filename': filename,
                    'unique_filename': unique_filename,
                    'file_type': file_type,
                    'size': os.path.getsize(file_path),
                    'url': f"/{relative_path}",
                    'upload_time': datetime.utcnow().isoformat()
                }
                
                uploaded_files.append(file_info)
        
        return jsonify({
            'success': True,
            'message': f'{len(uploaded_files)} files uploaded successfully',
            'files': uploaded_files
        })
        
    except Exception as e:
        current_app.logger.error(f"Error uploading media: {str(e)}")
        return jsonify({'success': False, 'message': f'Upload failed: {str(e)}'})

@lesson_bp.route('/api/lessons/<int:lesson_id>/media')
@login_required
def get_lesson_media(lesson_id):
    """Get all media files for a lesson"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        
        # In a real implementation, you'd query the database
        # For now, return empty arrays that can be populated via uploads
        media_files = {
            'videos': [],
            'images': [],
            'documents': []
        }
        
        return jsonify({
            'success': True,
            'media': media_files
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting lesson media: {str(e)}")
        return jsonify({'success': False, 'message': 'Error loading media files'})

@lesson_bp.route('/api/lessons/<int:lesson_id>/layout', methods=['PUT'])
@login_required
def update_lesson_layout(lesson_id):
    """Update lesson layout configuration via API"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        data = request.get_json()
        
        # Store layout configuration (you may want to add a layout_config field to the Lesson model)
        layout_config = {
            'layout_type': data.get('layout_type', 'single-column'),
            'blocks': data.get('blocks', []),
            'settings': data.get('settings', {
                'block_spacing': 20,
                'media_size': 'medium',
                'text_alignment': 'left'
            })
        }
        
        # For now, store in content field with a special marker
        # In production, you'd want a separate layout_config field
        current_content = lesson.content or ''
        layout_marker = '<!--LAYOUT_CONFIG:'
        
        if layout_marker in current_content:
            # Replace existing layout config
            start = current_content.find(layout_marker)
            end = current_content.find('-->', start) + 3
            current_content = current_content[:start] + current_content[end:]
        
        # Add new layout config at the beginning
        lesson.content = f"<!--LAYOUT_CONFIG:{json.dumps(layout_config)}-->\n{current_content}"
        lesson.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Lesson layout updated successfully',
            'layout_config': layout_config
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating lesson layout: {str(e)}")
        return jsonify({'success': False, 'message': 'Error updating layout'})

@lesson_bp.route('/api/lessons/<int:lesson_id>/layout', methods=['GET'])
@login_required
def get_lesson_layout(lesson_id):
    """Get lesson layout configuration via API"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        
        # Extract layout config from content
        layout_config = {
            'layout_type': 'single-column',
            'blocks': [],
            'settings': {
                'block_spacing': 20,
                'media_size': 'medium',
                'text_alignment': 'left'
            }
        }
        
        if lesson.content:
            layout_marker = '<!--LAYOUT_CONFIG:'
            if layout_marker in lesson.content:
                start = lesson.content.find(layout_marker) + len(layout_marker)
                end = lesson.content.find('-->', start)
                if end > start:
                    try:
                        config_data = lesson.content[start:end]
                        layout_config = json.loads(config_data)
                    except json.JSONDecodeError:
                        pass  # Use default config
        
        return jsonify({
            'success': True,
            'layout_config': layout_config
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting lesson layout: {str(e)}")
        return jsonify({'success': False, 'message': 'Error loading layout'})

@lesson_bp.route('/api/lessons/<int:lesson_id>/content', methods=['PUT'])
@login_required
def update_lesson_content_with_layout(lesson_id):
    """Update lesson content with layout information via API"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        data = request.get_json()
        
        # Update lesson content
        content = data.get('content', lesson.content)
        layout_config = data.get('layout_config')
        
        # If layout config is provided, store it
        if layout_config:
            layout_marker = '<!--LAYOUT_CONFIG:'
            
            if layout_marker in content:
                # Replace existing layout config
                start = content.find(layout_marker)
                end = content.find('-->', start) + 3
                content = content[:start] + content[end:]
            
            # Add new layout config at the beginning
            content = f"<!--LAYOUT_CONFIG:{json.dumps(layout_config)}-->\n{content}"
        
        lesson.content = content
        lesson.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Lesson content and layout updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating lesson content with layout: {str(e)}")
        return jsonify({'success': False, 'message': 'Error updating content'})

def update_lesson_content(lesson_id):
    """Update lesson content via API"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        data = request.get_json()
        
        # Update lesson content
        lesson.content = data.get('content', lesson.content)
        lesson.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Lesson content updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating lesson content: {str(e)}")
        return jsonify({'success': False, 'message': 'Error updating content'})
