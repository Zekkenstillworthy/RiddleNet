"""
Advanced Lesson Editor Controller
Provides rich multimedia content management and real-time preview capabilities
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from __init__ import db
from utils.render_utils import render_safe_template
from datetime import datetime
import json
import os
import uuid
import mimetypes

advanced_lesson_bp = Blueprint('advanced_lesson', __name__, url_prefix='/admin')

# Content block types configuration
CONTENT_BLOCK_TYPES = {
    'text': {
        'name': 'Text Block',
        'icon': 'text_fields',
        'description': 'Rich text content with formatting'
    },
    'image': {
        'name': 'Image',
        'icon': 'image',
        'description': 'Images, diagrams, and visual content'
    },
    'video': {
        'name': 'Video',
        'icon': 'play_circle',
        'description': 'Video content and embeds'
    },
    'audio': {
        'name': 'Audio',
        'icon': 'audiotrack',
        'description': 'Audio recordings and podcasts'
    },
    'file': {
        'name': 'File Download',
        'icon': 'download',
        'description': 'Downloadable files and documents'
    },
    'quiz': {
        'name': 'Knowledge Check',
        'icon': 'quiz',
        'description': 'Interactive questions and assessments'
    },
    'simulation': {
        'name': 'Simulation',
        'icon': 'science',
        'description': 'Interactive simulations and labs'
    },
    'objectives': {
        'name': 'Learning Objectives',
        'icon': 'checklist',
        'description': 'Structured learning objectives'
    },
    'summary': {
        'name': 'Summary',
        'icon': 'summarize',
        'description': 'Key takeaways and conclusions'
    }
}

# File upload configuration
UPLOAD_FOLDER = 'static/uploads/lessons'
ALLOWED_EXTENSIONS = {
    'image': {'jpg', 'jpeg', 'png', 'gif', 'svg', 'webp'},
    'video': {'mp4', 'webm', 'mov', 'avi'},
    'audio': {'mp3', 'wav', 'ogg', 'aac', 'm4a'},
    'document': {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt'}
}

MAX_FILE_SIZES = {
    'image': 10 * 1024 * 1024,    # 10MB
    'video': 500 * 1024 * 1024,   # 500MB
    'audio': 50 * 1024 * 1024,    # 50MB
    'document': 100 * 1024 * 1024  # 100MB
}

def allowed_file(filename, file_type):
    """Check if file extension is allowed for the given type"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS.get(file_type, set())

def get_file_type(filename):
    """Determine file type based on extension"""
    if not filename or '.' not in filename:
        return 'document'
    
    extension = filename.rsplit('.', 1)[1].lower()
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if extension in extensions:
            return file_type
    return 'document'

@advanced_lesson_bp.route('/lessons/<int:lesson_id>/advanced-editor')
@login_required
def advanced_editor(lesson_id):
    """Advanced lesson editor interface"""
    try:
        # Import models at runtime to avoid circular imports
        from instructor.models.module import Module, Lesson, LessonProgress
        from instructor.models.class_model import Class
        from instructor.models.simulation import Simulation
        
        lesson = Lesson.query.get_or_404(lesson_id)
        class_obj = lesson.module.class_obj
        module = lesson.module
        
        # Get existing content blocks
        content_blocks = db.session.execute(
            "SELECT * FROM lesson_content_blocks WHERE lesson_id = ? ORDER BY display_order",
            (lesson_id,)
        ).fetchall()
        
        # Get lesson media files
        media_files = db.session.execute(
            "SELECT * FROM lesson_media_files WHERE lesson_id = ? ORDER BY created_at DESC",
            (lesson_id,)
        ).fetchall()
        
        # Get available templates
        templates = db.session.execute(
            "SELECT * FROM lesson_templates WHERE is_public = 1 ORDER BY usage_count DESC"
        ).fetchall()
        
        # Get available simulations
        simulations = Simulation.query.filter(
            Simulation.is_active == True,
            Simulation.is_published == True
        ).order_by(Simulation.title).all()
        
        return render_safe_template('instructor/lessons/advanced_editor.html',
                                   class_obj=class_obj,
                                   module=module,
                                   lesson=lesson,
                                   content_blocks=content_blocks,
                                   media_files=media_files,
                                   templates=templates,
                                   simulations=simulations,
                                   block_types=CONTENT_BLOCK_TYPES)
    except Exception as e:
        current_app.logger.error(f"Error loading advanced editor: {str(e)}")
        flash('Error loading advanced editor', 'error')
        return redirect(url_for('lesson.index'))

@advanced_lesson_bp.route('/lessons/<int:lesson_id>/content-blocks', methods=['GET'])
@login_required
def get_content_blocks(lesson_id):
    """Get lesson content blocks as JSON"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        
        blocks = db.session.execute(
            "SELECT * FROM lesson_content_blocks WHERE lesson_id = ? ORDER BY display_order",
            (lesson_id,)
        ).fetchall()
        
        content_blocks = []
        for block in blocks:
            content_data = json.loads(block[2]) if block[2] else {}
            content_blocks.append({
                'id': block[0],
                'type': block[1],
                'data': content_data,
                'order': block[3],
                'is_active': block[4]
            })
        
        return jsonify({
            'success': True,
            'blocks': content_blocks
        })
    except Exception as e:
        current_app.logger.error(f"Error getting content blocks: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@advanced_lesson_bp.route('/lessons/<int:lesson_id>/content-blocks', methods=['POST'])
@login_required
def save_content_blocks(lesson_id):
    """Save lesson content blocks"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        data = request.json
        
        if not data or 'blocks' not in data:
            return jsonify({'success': False, 'error': 'Invalid data format'}), 400
        
        # Delete existing blocks
        db.session.execute(
            "DELETE FROM lesson_content_blocks WHERE lesson_id = ?",
            (lesson_id,)
        )
        
        # Insert new blocks
        for index, block in enumerate(data['blocks']):
            db.session.execute(
                """INSERT INTO lesson_content_blocks 
                   (lesson_id, block_type, content_data, display_order, is_active) 
                   VALUES (?, ?, ?, ?, ?)""",
                (lesson_id, block['type'], json.dumps(block['data']), index, True)
            )
        
        # Update lesson metadata
        lesson.content_format = 'blocks'
        lesson.has_media_content = any(
            block['type'] in ['image', 'video', 'audio', 'file'] 
            for block in data['blocks']
        )
        lesson.interactive_elements_count = sum(
            1 for block in data['blocks'] 
            if block['type'] in ['quiz', 'simulation']
        )
        lesson.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Create version snapshot
        create_lesson_version(lesson_id, data['blocks'], "Content blocks updated")
        
        return jsonify({
            'success': True,
            'message': 'Content blocks saved successfully'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving content blocks: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@advanced_lesson_bp.route('/lessons/<int:lesson_id>/upload-media', methods=['POST'])
@login_required
def upload_media(lesson_id):
    """Upload media file for lesson"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Determine file type
        file_type = get_file_type(file.filename)
        
        if not allowed_file(file.filename, file_type):
            return jsonify({'success': False, 'error': 'File type not allowed'}), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZES.get(file_type, MAX_FILE_SIZES['document']):
            return jsonify({'success': False, 'error': 'File too large'}), 400
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        stored_filename = f"{unique_id}_{filename}"
        
        # Create upload directory if it doesn't exist
        upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, str(lesson_id))
        os.makedirs(upload_path, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_path, stored_filename)
        file.save(file_path)
        
        # Get relative path for database
        relative_path = f"{UPLOAD_FOLDER}/{lesson_id}/{stored_filename}"
        
        # Generate thumbnail for images and videos (simplified implementation)
        thumbnail_path = None
        if file_type == 'image':
            try:
                # For now, use the original image as thumbnail
                # TODO: Implement proper thumbnail generation
                thumbnail_path = relative_path
            except Exception as e:
                current_app.logger.warning(f"Could not generate thumbnail: {str(e)}")
        elif file_type == 'video':
            # TODO: Implement video thumbnail generation
            thumbnail_path = None
        
        # Save to database
        media_id = db.session.execute(
            """INSERT INTO lesson_media_files 
               (lesson_id, original_filename, stored_filename, file_path, file_size, 
                mime_type, media_type, thumbnail_path, upload_status) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (lesson_id, filename, stored_filename, relative_path, file_size,
             file.mimetype, file_type, thumbnail_path, 'completed')
        ).lastrowid
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'file': {
                'id': media_id,
                'filename': filename,
                'stored_filename': stored_filename,
                'file_path': relative_path,
                'file_size': file_size,
                'media_type': file_type,
                'thumbnail_path': thumbnail_path,
                'url': f"/{relative_path}"
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error uploading media: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@advanced_lesson_bp.route('/lessons/<int:lesson_id>/preview')
@login_required
def preview_lesson(lesson_id):
    """Generate student preview of the lesson"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        
        # Get content blocks
        blocks = db.session.execute(
            "SELECT * FROM lesson_content_blocks WHERE lesson_id = ? AND is_active = 1 ORDER BY display_order",
            (lesson_id,)
        ).fetchall()
        
        content_blocks = []
        for block in blocks:
            content_data = json.loads(block[2]) if block[2] else {}
            content_blocks.append({
                'id': block[0],
                'type': block[1],
                'data': content_data,
                'order': block[3]
            })
        
        # Get media files
        media_files = db.session.execute(
            "SELECT * FROM lesson_media_files WHERE lesson_id = ? AND upload_status = 'completed'",
            (lesson_id,)
        ).fetchall()
        
        media_dict = {}
        for media in media_files:
            media_dict[media[0]] = {
                'id': media[0],
                'filename': media[1],
                'url': f"/{media[3]}",
                'type': media[7],
                'thumbnail': f"/{media[8]}" if media[8] else None
            }
        
        return render_safe_template('instructor/lessons/preview.html',
                                   lesson=lesson,
                                   content_blocks=content_blocks,
                                   media_files=media_dict)
    except Exception as e:
        current_app.logger.error(f"Error generating preview: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@advanced_lesson_bp.route('/lessons/<int:lesson_id>/templates/<int:template_id>/apply', methods=['POST'])
@login_required
def apply_template(lesson_id, template_id):
    """Apply a lesson template to the current lesson"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        
        template = db.session.execute(
            "SELECT * FROM lesson_templates WHERE id = ?",
            (template_id,)
        ).fetchone()
        
        if not template:
            return jsonify({'success': False, 'error': 'Template not found'}), 404
        
        template_data = json.loads(template[2])  # template_data column
        
        # Clear existing blocks
        db.session.execute(
            "DELETE FROM lesson_content_blocks WHERE lesson_id = ?",
            (lesson_id,)
        )
        
        # Create blocks from template
        for index, block_template in enumerate(template_data.get('blocks', [])):
            db.session.execute(
                """INSERT INTO lesson_content_blocks 
                   (lesson_id, block_type, content_data, display_order, is_active) 
                   VALUES (?, ?, ?, ?, ?)""",
                (lesson_id, block_template['type'], json.dumps({
                    'title': block_template.get('title', ''),
                    'content': '',
                    'placeholder': f"Add {block_template['type']} content here..."
                }), index, True)
            )
        
        # Update template usage count
        db.session.execute(
            "UPDATE lesson_templates SET usage_count = usage_count + 1 WHERE id = ?",
            (template_id,)
        )
        
        lesson.content_format = 'blocks'
        lesson.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Template "{template[1]}" applied successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error applying template: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def create_lesson_version(lesson_id, content_blocks, change_summary):
    """Create a version snapshot of the lesson"""
    try:
        # Get current version number
        last_version = db.session.execute(
            "SELECT MAX(version_number) FROM lesson_versions WHERE lesson_id = ?",
            (lesson_id,)
        ).fetchone()
        
        version_number = (last_version[0] + 1) if last_version[0] else 1
        
        # Create version snapshot
        db.session.execute(
            """INSERT INTO lesson_versions 
               (lesson_id, version_number, content_snapshot, change_summary, created_by) 
               VALUES (?, ?, ?, ?, ?)""",
            (lesson_id, version_number, json.dumps(content_blocks), 
             change_summary, current_user.id)
        )
        
        db.session.commit()
        
    except Exception as e:
        current_app.logger.error(f"Error creating lesson version: {str(e)}")

@advanced_lesson_bp.route('/lessons/<int:lesson_id>/versions')
@login_required
def get_lesson_versions(lesson_id):
    """Get lesson version history"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        
        versions = db.session.execute(
            """SELECT lv.*, u.username 
               FROM lesson_versions lv 
               LEFT JOIN users u ON lv.created_by = u.id 
               WHERE lv.lesson_id = ? 
               ORDER BY lv.version_number DESC""",
            (lesson_id,)
        ).fetchall()
        
        version_list = []
        for version in versions:
            version_list.append({
                'id': version[0],
                'version_number': version[2],
                'change_summary': version[4],
                'created_by': version[7] or 'Unknown',
                'created_at': version[6]
            })
        
        return jsonify({
            'success': True,
            'versions': version_list
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting lesson versions: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@advanced_lesson_bp.route('/media/<int:media_id>/delete', methods=['DELETE'])
@login_required
def delete_media(media_id):
    """Delete uploaded media file"""
    try:
        media = db.session.execute(
            "SELECT * FROM lesson_media_files WHERE id = ?",
            (media_id,)
        ).fetchone()
        
        if not media:
            return jsonify({'success': False, 'error': 'Media file not found'}), 404
        
        # Delete physical file
        file_path = os.path.join(current_app.root_path, media[3])
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete thumbnail if exists
        if media[8]:  # thumbnail_path
            thumbnail_path = os.path.join(current_app.root_path, media[8])
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
        
        # Delete from database
        db.session.execute(
            "DELETE FROM lesson_media_files WHERE id = ?",
            (media_id,)
        )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Media file deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting media: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
