from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from instructor.models.module import Module, Lesson
from instructor.models.class_model import Class
from utils.auth_decorators import instructor_required
from __init__ import db
from datetime import datetime
import logging

# Create blueprint for enhanced module management
enhanced_module_bp = Blueprint('enhanced_module', __name__, template_folder='../templates', url_prefix='/admin')

@enhanced_module_bp.route('/classes/<int:class_id>/modules/<int:module_id>/edit', methods=['GET'])
@login_required
@instructor_required
def edit_module(class_id, module_id):
    """Show module editing form"""
    try:
        # Get the module
        module = Module.query.filter_by(id=module_id, class_id=class_id).first_or_404()
        
        # Get the class
        class_obj = Class.query.get_or_404(class_id)
        
        # Get all modules for the class
        class_modules = Module.query.filter_by(class_id=class_id, is_active=True).order_by(Module.order_index.asc()).all()
        
        # Get lessons for the module - handle dynamic relationship properly
        lessons = module.lessons.filter_by(is_active=True).order_by(Lesson.order_index.asc()).all()
        
        return render_template('instructor/modules/edit_module.html', 
                             module=module, 
                             class_obj=class_obj,
                             class_modules=class_modules,
                             lessons=lessons)
        
    except Exception as e:
        print(f"[ERROR] DEBUG Exception: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# DEBUG endpoint for testing actual delete (remove in production)
@enhanced_module_bp.route('/api/debug/modules/<int:module_id>/delete-now', methods=['GET'])
def debug_delete_module_now(module_id):
    """Debug endpoint to actually delete a module without auth"""
    try:
        print(f"[FIX] DEBUG: Actually deleting module {module_id}")
        module = Module.query.get(module_id)
        if not module:
            return jsonify({'success': False, 'message': f'Module {module_id} not found'}), 404
            
        print(f"[OK] Found module to delete: {module.title} (is_active: {module.is_active})")
        
        # Perform soft delete
        module.is_active = False
        module.updated_at = datetime.utcnow()
        
        db.session.commit()
        print(f"[OK] Module soft-deleted successfully: {module.id}")
        
        return jsonify({
            'success': True,
            'message': f'Module {module_id} soft-deleted successfully',
            'module': {
                'id': module.id,
                'title': module.title,
                'is_active': module.is_active,
                'class_id': module.class_id
            }
        })
        
    except Exception as e:
        print(f"[ERROR] DEBUG DELETE Exception: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@enhanced_module_bp.route('/modules/<int:module_id>/edit', methods=['GET'])
@login_required
@instructor_required
def edit_module_simple(module_id):
    """Simple edit module route"""
    try:
        module = Module.query.get_or_404(module_id)
        
        # Get the class for additional context
        class_obj = Class.query.get(module.class_id) if module.class_id else None
        
        # Get all modules for the class if class exists
        class_modules = []
        if class_obj:
            class_modules = Module.query.filter_by(class_id=class_obj.id, is_active=True).order_by(Module.order_index.asc()).all()
        
        # Get lessons for the module - handle dynamic relationship properly
        lessons = module.lessons.filter_by(is_active=True).order_by(Lesson.order_index.asc()).all()
        
        return render_template('instructor/modules/edit_module.html', 
                             module=module,
                             class_obj=class_obj,
                             class_modules=class_modules,
                             lessons=lessons)
    except Exception as e:
        flash(f'Error accessing module: {str(e)}', 'error')
        return redirect(url_for('dashboard.index'))

@enhanced_module_bp.route('/modules/<int:module_id>', methods=['GET'])
@login_required
@instructor_required
def view_module_simple(module_id):
    """Simple module view route - finds class ID from module and redirects to preview"""
    # Find the module to get the class_id
    module = Module.query.get_or_404(module_id)
    class_id = module.class_id
    # Redirect to module preview
    return redirect(url_for('class_content_controller_old.preview_module_page', class_id=class_id, module_id=module_id))

@enhanced_module_bp.route('/classes/<int:class_id>/modules/<int:module_id>/edit', methods=['POST'])
@login_required
@instructor_required
def update_module(class_id, module_id):
    """Update module details"""
    logging.debug(f'UPDATE MODULE: class_id={class_id}, module_id={module_id}, user={getattr(current_user, "id", None)}')
    try:
        # Get the module
        module = Module.query.filter_by(id=module_id, class_id=class_id).first_or_404()
        
        # Log form data for debugging
        logging.debug(f'Form data received: {dict(request.form)}')
        
        # Update module fields
        module.title = request.form.get('title', '').strip()
        module.description = request.form.get('description', '').strip()
        module.learning_objectives = request.form.get('learning_objectives', '').strip()
        module.order_index = int(request.form.get('order_index', module.order_index))
        
        # Handle estimated_duration
        try:
            module.estimated_duration = int(request.form.get('estimated_duration', module.estimated_duration or 60))
        except (ValueError, TypeError):
            module.estimated_duration = 60  # Default fallback
        
        # Handle active status - check for both possible field names
        is_active_value = request.form.get('is_active') or request.form.get('active_module')
        module.is_active = bool(is_active_value)
        
        # Handle published status independently
        is_published_value = request.form.get('is_published')
        module.is_published = bool(is_published_value)
        
        # Log the changes
        logging.debug(f'Module update - is_active: {module.is_active}, is_published: {module.is_published}, estimated_duration: {module.estimated_duration}')
        
        module.updated_at = datetime.utcnow()
        
        # Commit changes
        db.session.commit()
        logging.debug(f'Module updated successfully: id={module.id}, is_active={module.is_active}')
        
        flash('Module updated successfully!', 'success')
        return redirect(url_for('dashboard.class_content_manager') + f'?class_id={class_id}&module_id={module_id}')
        
    except ValueError as e:
        logging.error(f'UPDATE MODULE ValueError: {e}')
        flash(f'Invalid input: {str(e)}', 'error')
        return redirect(url_for('dashboard.class_content_manager') + f'?class_id={class_id}')
    except Exception as e:
        logging.error(f'UPDATE MODULE Exception: {e}')
        db.session.rollback()
        flash(f'Error updating module: {str(e)}', 'error')
        return redirect(url_for('dashboard.class_content_manager') + f'?class_id={class_id}')

@enhanced_module_bp.route('/classes/<int:class_id>/modules/new')
@login_required
@instructor_required  
def new_module_redirect(class_id):
    """Redirect /new to /create for compatibility"""
    return redirect(url_for('enhanced_module.create_module_form', class_id=class_id))

@enhanced_module_bp.route('/classes/<int:class_id>/modules/create', methods=['GET'])
@login_required
@instructor_required
def create_module_form(class_id):
    """Show create module form"""
    class_obj = Class.query.get_or_404(class_id)
    
    # Get next order index
    max_order = db.session.query(db.func.max(Module.order_index)).filter_by(class_id=class_id).scalar() or 0
    next_order = max_order + 1
    
    return render_template('instructor/modules/create_module.html', 
                         class_obj=class_obj, 
                         next_order=next_order)

@enhanced_module_bp.route('/classes/<int:class_id>/modules/create', methods=['POST'])
@login_required
@instructor_required
def create_module(class_id):
    """Create new module"""
    logging.debug(f'CREATE MODULE: class_id={class_id}, user={getattr(current_user, "id", None)}')
    try:
        # Verify class exists
        class_obj = Class.query.get_or_404(class_id)

        # Ownership check: only creator or super_admin can create content for this class
        if not (hasattr(current_user, 'role') and current_user.role == 'super_admin') and class_obj.created_by != getattr(current_user, 'id', None):
            return jsonify({'error': 'Permission denied'}), 403
        
        # Get form data with enhanced fields
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        learning_objectives = request.form.get('learning_objectives', '').strip()
        module_content = request.form.get('content', '').strip()  # Get content for lessons, not module
        estimated_duration = int(request.form.get('estimated_duration', 60))
        order_index = int(request.form.get('order_index', 1))
        is_active = bool(request.form.get('is_active'))
        is_published = bool(request.form.get('is_published'))
        requires_sequential_completion = bool(request.form.get('requires_sequential_completion'))
        
        # Validate required fields
        if not title:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json':
                return jsonify({'success': False, 'error': 'Module title is required'}), 400
            flash('Module title is required', 'error')
            return redirect(url_for('enhanced_module.create_module_form', class_id=class_id))
        
        # Process materials list
        materials = request.form.getlist('materials[]')
        materials = [m.strip() for m in materials if m.strip()]
        
        # Calculate the correct module number based on active modules count
        active_modules_count = Module.query.filter_by(class_id=class_id, is_active=True).count()
        next_module_number = active_modules_count + 1
        
        # Create new module - NOTE: Module model doesn't have 'content' field
        module = Module(
            title=title,
            description=description,
            module_number=str(next_module_number),  # Sequential module number
            course_type=class_obj.name or 'General Course',  # Use class name as course type
            learning_objectives=learning_objectives.split('\n') if learning_objectives else [],
            estimated_duration=estimated_duration,
            class_id=class_id,
            order_index=order_index,
            is_active=is_active,
            created_by=current_user.id,  # Set the current user as creator
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add additional fields if they exist in the model
        if hasattr(module, 'is_published'):
            module.is_published = is_published
        if hasattr(module, 'requires_sequential_completion'):
            module.requires_sequential_completion = requires_sequential_completion
        # Note: required_materials field doesn't exist in the Module model
        
        db.session.add(module)
        
        # Use sequence synchronization to prevent duplicate key errors
        try:
            from utils.sequence_sync import commit_with_sequence_retry
            print(f"[FIX] Committing module with sequence retry...")
            commit_with_sequence_retry('modules', 'id')
        except ImportError:
            # Fallback if sequence_sync is not available
            print(f"[WARNING]  sequence_sync not available, using regular commit")
            db.session.commit()
        except Exception as seq_error:
            print(f"[ERROR] Error creating module: {seq_error}")
            raise
            
        logging.debug(f'Module created: id={module.id}')
        
        # Process lesson data if any
        lesson_titles = request.form.getlist('lesson_titles[]')
        lesson_descriptions = request.form.getlist('lesson_descriptions[]') 
        lesson_durations = request.form.getlist('lesson_durations[]')
        lesson_types = request.form.getlist('lesson_types[]')
        
        # Create lessons if provided
        if lesson_titles and any(title.strip() for title in lesson_titles):
            for i, lesson_title in enumerate(lesson_titles):
                if lesson_title.strip():
                    lesson_description = lesson_descriptions[i] if i < len(lesson_descriptions) else ''
                    lesson_duration = int(lesson_durations[i]) if i < len(lesson_durations) and lesson_durations[i].isdigit() else 30
                    lesson_type = lesson_types[i] if i < len(lesson_types) else 'lecture'
                    
                    # Use module content for the first lesson if no specific lessons were created
                    lesson_content = module_content if i == 0 and module_content and len([t for t in lesson_titles if t.strip()]) == 1 else f"<p>Content for {lesson_title}</p>"
                    
                    lesson = Lesson(
                        title=lesson_title.strip(),
                        description=lesson_description.strip(),
                        lesson_number=str(i + 1),
                        content=lesson_content,
                        estimated_duration=lesson_duration,
                        order_index=i + 1,
                        module_id=module.id,
                        is_active=True
                    )
                    
                    # Add lesson type if the field exists
                    if hasattr(lesson, 'lesson_type'):
                        lesson.lesson_type = lesson_type
                    
                    db.session.add(lesson)
        elif module_content:
            # If no lessons were provided but content was, create a default lesson
            default_lesson = Lesson(
                title=f"{title} - Main Content",
                description="Main lesson content for this module",
                lesson_number="1",
                content=module_content,
                estimated_duration=estimated_duration,
                order_index=1,
                module_id=module.id,
                is_active=True
            )
            db.session.add(default_lesson)
        
        # Commit lessons with sequence sync
        if 'lesson_titles' in locals() and any(title.strip() for title in lesson_titles):
            try:
                from utils.sequence_sync import commit_with_sequence_retry
                print(f"[FIX] Committing lessons with sequence retry...")
                commit_with_sequence_retry('lessons', 'id')
            except ImportError:
                print(f"[WARNING]  sequence_sync not available for lessons, using regular commit")
                db.session.commit()
            except Exception as lesson_error:
                print(f"[ERROR] Error creating lessons: {lesson_error}")
                raise
        else:
            db.session.commit()
        
        # Emit WebSocket event for real-time updates
        try:
            from socket_manager import socketio
            module_data = {
                'id': module.id,
                'title': module.title,
                'description': module.description,
                'order_index': module.order_index,
                'class_id': module.class_id,
                'created_by': getattr(current_user, 'username', 'Unknown'),
                'created_at': module.created_at.isoformat() if module.created_at else None
            }
            
            print(f"📡 Emitting module_created event for module {module.id}")
            
            # Emit to admin room
            socketio.emit('module_created_broadcast', {
                'module': module_data,
                'class_id': class_id,
                'created_by': getattr(current_user, 'username', 'Unknown'),
                'timestamp': datetime.utcnow().isoformat()
            }, room='admin_room')
            
            # Emit to module builder room
            socketio.emit('module_created_broadcast', {
                'module': module_data,
                'class_id': class_id,
                'created_by': getattr(current_user, 'username', 'Unknown'),
                'timestamp': datetime.utcnow().isoformat()
            }, room='module_builder')
            
            # Emit to class-specific room
            socketio.emit('module_created_broadcast', {
                'module': module_data,
                'class_id': class_id,
                'created_by': getattr(current_user, 'username', 'Unknown'),
                'timestamp': datetime.utcnow().isoformat()
            }, room=f'class_{class_id}')
            
            print(f"[OK] WebSocket events emitted successfully for new module {module.id}")
            
        except Exception as ws_error:
            print(f"[WARNING] WebSocket emit failed (non-critical): {ws_error}")
            logging.warning(f'WebSocket emit failed for module creation: {ws_error}')
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json':
            return jsonify({
                'success': True,
                'message': 'Module created successfully!',
                'module': {
                    'id': module.id,
                    'title': module.title,
                    'description': module.description,
                    'order_index': module.order_index,
                    'class_id': module.class_id
                }
            }), 200
        
        flash('Module created successfully!', 'success')
        return redirect(url_for('dashboard.class_content_manager') + f'?class_id={class_id}&module_id={module.id}')
        
    except ValueError as e:
        logging.error(f'CREATE MODULE ValueError: {e}')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json':
            return jsonify({'success': False, 'error': f'Invalid input: {str(e)}'}), 400
        flash(f'Invalid input: {str(e)}', 'error')
        return redirect(url_for('enhanced_module.create_module_form', class_id=class_id))
    except Exception as e:
        logging.error(f'CREATE MODULE Exception: {e}')
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json':
            return jsonify({'success': False, 'error': f'Error creating module: {str(e)}'}), 500
        flash(f'Error creating module: {str(e)}', 'error')
        return redirect(url_for('enhanced_module.create_module_form', class_id=class_id))

@enhanced_module_bp.route('/classes/<int:class_id>/modules/<int:module_id>/delete', methods=['POST'])
@login_required
@instructor_required
def delete_module(class_id, module_id):
    """Soft delete module"""
    logging.debug(f'DELETE MODULE: class_id={class_id}, module_id={module_id}, user={getattr(current_user, "id", None)}')
    try:
        module = Module.query.filter_by(id=module_id, class_id=class_id).first_or_404()
        
        # Soft delete
        module.is_active = False
        module.updated_at = datetime.utcnow()
        
        db.session.commit()
        logging.debug(f'Module soft-deleted: id={module.id}')
        
        # Renumber remaining modules sequentially
        renumber_modules(class_id)
        
        flash('Module deleted successfully!', 'success')
        return redirect(url_for('dashboard.class_content_manager') + f'?class_id={class_id}')
        
    except Exception as e:
        logging.error(f'DELETE MODULE Exception: {e}')
        db.session.rollback()
        flash(f'Error deleting module: {str(e)}', 'error')
        return redirect(url_for('dashboard.class_content_manager') + f'?class_id={class_id}')

# API Routes for AJAX operations
@enhanced_module_bp.route('/api/classes/<int:class_id>/modules/renumber', methods=['POST'])
@login_required
@instructor_required
def renumber_modules_api(class_id):
    """API endpoint to renumber all modules in a class"""
    try:
        # Verify class exists
        class_obj = Class.query.get_or_404(class_id)
        
        # Renumber all modules
        renumber_modules(class_id)
        
        return jsonify({
            'success': True, 
            'message': 'Modules renumbered successfully'
        })
        
    except Exception as e:
        logging.error(f'RENUMBER MODULES Exception: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@enhanced_module_bp.route('/api/classes/<int:class_id>/modules/<int:module_id>/reorder', methods=['POST'])
@login_required
@instructor_required
def reorder_module(class_id, module_id):
    """Update module order"""
    try:
        module = Module.query.filter_by(id=module_id, class_id=class_id).first_or_404()
        new_order = request.json.get('order_index')
        
        if new_order is not None:
            module.order_index = int(new_order)
            module.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Renumber all modules sequentially after reordering
            renumber_modules(class_id)
            
            return jsonify({'success': True, 'message': 'Module order updated'})
        
        return jsonify({'success': False, 'message': 'Invalid order index'}), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


def renumber_modules(class_id):
    """Renumber all modules in a class sequentially based on order_index"""
    try:
        # Get all active modules for the class, ordered by order_index
        modules = Module.query.filter_by(
            class_id=class_id, 
            is_active=True
        ).order_by(Module.order_index.asc()).all()
        
        # Renumber them sequentially
        for index, module in enumerate(modules, start=1):
            module.module_number = str(index)
        
        db.session.commit()
        print(f"[OK] Renumbered {len(modules)} modules for class {class_id}")
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Error renumbering modules: {e}")
        raise

@enhanced_module_bp.route('/api/classes/<int:class_id>/modules/<int:module_id>/toggle', methods=['POST'])
@login_required
@instructor_required
def toggle_module_active(class_id, module_id):
    """Toggle module active status"""
    try:
        module = Module.query.filter_by(id=module_id, class_id=class_id).first_or_404()
        
        module.is_active = not module.is_active
        module.updated_at = datetime.utcnow()
        db.session.commit()
        
        status = "activated" if module.is_active else "deactivated"
        return jsonify({'success': True, 'message': f'Module {status}', 'is_active': module.is_active})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# API endpoints for class content manager
@enhanced_module_bp.route('/api/classes/<int:class_id>/modules', methods=['GET'])
@login_required
@instructor_required
def get_class_modules_api(class_id):
    """Get all modules for a class (API endpoint)"""
    logging.debug(f'GET MODULES: class_id={class_id}, user={getattr(current_user, "id", None)}')
    try:
        # Verify class exists
        class_obj = Class.query.get_or_404(class_id)
        
        # Get modules with lesson count
        modules = db.session.query(Module).filter_by(class_id=class_id, is_active=True).order_by(Module.order_index).all()
        
        modules_data = []
        for module in modules:
            lessons_count = Lesson.query.filter_by(module_id=module.id, is_active=True).count()
            modules_data.append({
                'id': module.id,
                'title': module.title,
                'description': module.description,
                'order_index': module.order_index,
                'estimated_duration': module.estimated_duration,
                'is_active': module.is_active,
                'lessons_count': lessons_count,
                'created_at': module.created_at.isoformat() if module.created_at else None,
                'updated_at': module.updated_at.isoformat() if module.updated_at else None
            })
        
        return jsonify(modules_data)
        
    except Exception as e:
        logging.error(f'GET MODULES Exception: {e}')
        return jsonify({'error': str(e)}), 500

@enhanced_module_bp.route('/api/classes/<int:class_id>/modules/<int:module_id>', methods=['GET'])
@login_required
@instructor_required
def get_module_details_api(class_id, module_id):
    """Get detailed module information (API endpoint)"""
    logging.debug(f'GET MODULE DETAILS: class_id={class_id}, module_id={module_id}, user={getattr(current_user, "id", None)}')
    try:
        # Get the module
        module = Module.query.filter_by(id=module_id, class_id=class_id).first_or_404()
        
        # Get lessons for this module
        lessons = Lesson.query.filter_by(module_id=module_id, is_active=True).order_by(Lesson.order_index).all()
        
        lessons_data = []
        for lesson in lessons:
            lessons_data.append({
                'id': lesson.id,
                'title': lesson.title,
                'description': lesson.description,
                'duration': lesson.duration,
                'is_active': lesson.is_active,
                'order_index': lesson.order_index
            })
        
        module_data = {
            'id': module.id,
            'title': module.title,
            'description': module.description,
            'learning_objectives': module.learning_objectives,
            'order_index': module.order_index,
            'estimated_duration': module.estimated_duration,
            'is_active': module.is_active,
            'lessons': lessons_data,
            'created_at': module.created_at.isoformat() if module.created_at else None,
            'updated_at': module.updated_at.isoformat() if module.updated_at else None
        }
        
        return jsonify(module_data)
        
    except Exception as e:
        logging.error(f'GET MODULE DETAILS Exception: {e}')
        return jsonify({'error': str(e)}), 500

@enhanced_module_bp.route('/api/classes/<int:class_id>/modules/<int:module_id>', methods=['POST'])
@login_required
@instructor_required
def update_module_api(class_id, module_id):
    """Update module via API (for AJAX requests)"""
    logging.debug(f'UPDATE MODULE API: class_id={class_id}, module_id={module_id}, user={getattr(current_user, "id", None)}')
    try:
        # Get the module
        module = Module.query.filter_by(id=module_id, class_id=class_id).first_or_404()
        
        data = request.get_json()
        
        # Update module fields
        if 'title' in data:
            module.title = data['title'].strip()
        if 'description' in data:
            module.description = data['description'].strip()
        if 'learning_objectives' in data:
            module.learning_objectives = data['learning_objectives'].strip()
        if 'order_index' in data:
            module.order_index = int(data['order_index'])
        if 'estimated_duration' in data:
            module.estimated_duration = int(data['estimated_duration'])
        if 'is_active' in data:
            module.is_active = bool(data['is_active'])
            
        module.updated_at = datetime.utcnow()
        
        # Commit changes
        db.session.commit()
        logging.debug(f'Module updated via API: id={module.id}')
        
        # Emit WebSocket event for real-time updates
        try:
            from socket_manager import socketio
            module_data = {
                'id': module.id,
                'title': module.title,
                'description': module.description,
                'learning_objectives': module.learning_objectives,
                'order_index': module.order_index,
                'estimated_duration': module.estimated_duration,
                'is_active': module.is_active,
                'class_id': module.class_id,
                'updated_by': getattr(current_user, 'username', 'Unknown'),
                'updated_at': module.updated_at.isoformat() if module.updated_at else None
            }
            
            print(f"📡 Emitting module_updated event for module {module.id}")
            
            # Emit to admin room
            socketio.emit('module_updated_broadcast', {
                'module': module_data,
                'class_id': class_id,
                'updated_by': getattr(current_user, 'username', 'Unknown'),
                'timestamp': datetime.utcnow().isoformat()
            }, room='admin_room')
            
            # Emit to module builder room
            socketio.emit('module_updated_broadcast', {
                'module': module_data,
                'class_id': class_id,
                'updated_by': getattr(current_user, 'username', 'Unknown'),
                'timestamp': datetime.utcnow().isoformat()
            }, room='module_builder')
            
            # Emit to class-specific room
            socketio.emit('module_updated_broadcast', {
                'module': module_data,
                'class_id': class_id,
                'updated_by': getattr(current_user, 'username', 'Unknown'),
                'timestamp': datetime.utcnow().isoformat()
            }, room=f'class_{class_id}')
            
            print(f"[OK] WebSocket events emitted successfully for updated module {module.id}")
            
        except Exception as ws_error:
            print(f"[WARNING] WebSocket emit failed (non-critical): {ws_error}")
            logging.warning(f'WebSocket emit failed for module update: {ws_error}')
        
        return jsonify({'success': True, 'message': 'Module updated successfully'})
        
    except ValueError as e:
        logging.error(f'UPDATE MODULE API ValueError: {e}')
        return jsonify({'success': False, 'message': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        logging.error(f'UPDATE MODULE API Exception: {e}')
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error updating module: {str(e)}'}), 500

@enhanced_module_bp.route('/api/classes/<int:class_id>/modules/<int:module_id>', methods=['DELETE'])
@login_required
@instructor_required
def delete_module_api(class_id, module_id):
    """Delete module via API (for AJAX requests) with real-time WebSocket updates"""
    try:
        print(f"[FIX] DELETE MODULE API: class_id={class_id}, module_id={module_id}, user={getattr(current_user, 'id', None)}")
        logging.debug(f'DELETE MODULE API: class_id={class_id}, module_id={module_id}, user={getattr(current_user, "id", None)}')
        
        module = Module.query.filter_by(id=module_id, class_id=class_id).first_or_404()
        print(f"[OK] Found module: {module.title}")
        
        # Store module data for WebSocket emit
        module_data = {
            'id': module.id,
            'title': module.title,
            'class_id': module.class_id,
            'deleted_at': datetime.utcnow().isoformat(),
            'deleted_by': getattr(current_user, 'username', 'Unknown')
        }
        
        # Soft delete by setting is_active to False
        module.is_active = False
        module.updated_at = datetime.utcnow()
        
        db.session.commit()
        print(f"[OK] Module soft-deleted successfully: {module.id}")
        logging.debug(f'Module soft-deleted via API: id={module.id}')
        
        # Emit WebSocket event for real-time updates
        try:
            from socket_manager import socketio
            print(f"📡 Emitting module_deleted event to admin_room and class_{class_id}")
            
            # Emit to admin room for admin interfaces
            socketio.emit('module_deleted', module_data, room='admin_room')
            
            # Emit to class-specific room for any user interfaces
            socketio.emit('module_deleted', module_data, room=f'class_{class_id}')
            
            # Emit to module builder room for real-time UI updates
            socketio.emit('module_deleted', module_data, room='module_builder')
            
            print(f"[OK] WebSocket events emitted successfully for module {module_id}")
            
        except Exception as ws_error:
            print(f"[WARNING] WebSocket emit failed (non-critical): {ws_error}")
            logging.warning(f'WebSocket emit failed for module deletion: {ws_error}')
        
        return jsonify({'success': True, 'message': 'Module deleted successfully', 'module': module_data})
        
    except Exception as e:
        print(f"[ERROR] DELETE MODULE API Exception: {e}")
        logging.error(f'DELETE MODULE API Exception: {e}')
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error deleting module: {str(e)}'}), 500

# DEBUG endpoint for testing (remove in production)
@enhanced_module_bp.route('/api/debug/modules/<int:module_id>/test-delete', methods=['GET'])
def debug_test_delete_module(module_id):
    """Debug endpoint to test delete functionality without auth"""
    try:
        print(f"[FIX] DEBUG: Testing delete functionality for module {module_id}")
        module = Module.query.get(module_id)
        if not module:
            return jsonify({'success': False, 'message': f'Module {module_id} not found'}), 404
            
        print(f"[OK] Found module: {module.title} (is_active: {module.is_active})")
        return jsonify({
            'success': True, 
            'message': f'Module {module_id} exists and can be deleted',
            'module': {
                'id': module.id,
                'title': module.title,
                'is_active': module.is_active,
                'class_id': module.class_id
            }
        })
        
    except Exception as e:
        print(f"[ERROR] DEBUG Exception: {e}")
        return jsonify({'success': False, 'message': f'Debug error: {str(e)}'}), 500
