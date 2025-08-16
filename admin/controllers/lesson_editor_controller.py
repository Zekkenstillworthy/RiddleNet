"""
Advanced Lesson Editor API Controller
Provides comprehensive lesson editing functionality with rich media support
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from admin import db
from admin.models.module import Module, Lesson, LessonProgress
from admin.models.class_model import Class
from admin.models.simulation import Simulation
from utils.render_utils import render_safe_template
from datetime import datetime
import json
import os
import uuid
import mimetypes
from PIL import Image
import ffmpeg

lesson_editor_bp = Blueprint('lesson_editor', __name__, url_prefix='/admin/lessons')

# Configuration
UPLOAD_FOLDER = 'static/uploads/lessons'
ALLOWED_EXTENSIONS = {
    'images': {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'},
    'videos': {'mp4', 'webm', 'mov', 'avi', 'mkv'},
    'audio': {'mp3', 'wav', 'ogg', 'aac', 'm4a'},
    'documents': {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt'}
}
MAX_FILE_SIZES = {
    'images': 10 * 1024 * 1024,  # 10MB
    'videos': 500 * 1024 * 1024,  # 500MB
    'audio': 50 * 1024 * 1024,   # 50MB
    'documents': 100 * 1024 * 1024  # 100MB
}

def allowed_file(filename, file_type):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS.get(file_type, set())

def get_file_type(filename):
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return file_type
    return 'unknown'

@lesson_editor_bp.route('/<int:lesson_id>/editor')
@login_required
def advanced_editor(lesson_id):
    """Advanced lesson editor interface"""
    print(f"DEBUG LESSON_EDITOR: advanced_editor called with lesson_id={lesson_id}")
    try:
        print(f"DEBUG LESSON_EDITOR: Querying for lesson with id={lesson_id}")
        lesson = Lesson.query.get_or_404(lesson_id)
        print(f"DEBUG LESSON_EDITOR: Found lesson: {lesson.title if lesson else 'None'}")
        
        class_obj = lesson.module.class_obj
        module = lesson.module
        print(f"DEBUG LESSON_EDITOR: Associated with class: {class_obj.name}, module: {module.title}")
        
        # Get lesson content blocks
        print(f"DEBUG LESSON_EDITOR: Getting content blocks for lesson")
        content_blocks = get_lesson_content_blocks(lesson_id)
        print(f"DEBUG LESSON_EDITOR: Found {len(content_blocks)} content blocks")
        
        # Get lesson templates
        print(f"DEBUG LESSON_EDITOR: Getting lesson templates")
        templates = get_lesson_templates()
        print(f"DEBUG LESSON_EDITOR: Found {len(templates)} templates")
        
        # Get available simulations
        print(f"DEBUG LESSON_EDITOR: Getting available simulations")
        simulations = Simulation.query.filter(
            Simulation.is_active == True,
            Simulation.is_published == True
        ).order_by(Simulation.title).all()
        print(f"DEBUG LESSON_EDITOR: Found {len(simulations)} simulations")
        
        # Get lesson media files
        print(f"DEBUG LESSON_EDITOR: Getting media files for lesson")
        media_files = get_lesson_media_files(lesson_id)
        print(f"DEBUG LESSON_EDITOR: Found {len(media_files)} media files")
        
        print(f"DEBUG LESSON_EDITOR: Rendering advanced editor template")
        return render_safe_template('admin/lessons/advanced_editor.html',
                                   lesson=lesson,
                                   class_obj=class_obj,
                                   module=module,
                                   content_blocks=content_blocks,
                                   templates=templates,
                                   simulations=simulations,
                                   media_files=media_files)
                                   
    except Exception as e:
        print(f"DEBUG LESSON_EDITOR: ERROR in advanced_editor: {str(e)}")
        import traceback
        print(f"DEBUG LESSON_EDITOR: Traceback: {traceback.format_exc()}")
        current_app.logger.error(f"Error loading advanced editor: {str(e)}")
        flash('Error loading lesson editor', 'error')
        return redirect(url_for('lesson.index'))

@lesson_editor_bp.route('/<int:lesson_id>/content-blocks')
@login_required
def get_content_blocks(lesson_id):
    """Get lesson content blocks as JSON"""
    try:
        blocks = get_lesson_content_blocks(lesson_id)
        return jsonify({
            'success': True,
            'blocks': blocks
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lesson_editor_bp.route('/<int:lesson_id>/content-blocks', methods=['POST'])
@login_required
def save_content_blocks(lesson_id):
    """Save lesson content blocks"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        blocks_data = request.json.get('blocks', [])
        
        # Delete existing blocks
        db.session.execute("DELETE FROM lesson_content_blocks WHERE lesson_id = ?", (lesson_id,))
        
        # Insert new blocks
        for i, block in enumerate(blocks_data):
            db.session.execute(
                """INSERT INTO lesson_content_blocks 
                   (lesson_id, block_type, content_data, display_order, is_active) 
                   VALUES (?, ?, ?, ?, ?)""",
                (lesson_id, block.get('type'), json.dumps(block.get('content', {})), i, True)
            )
        
        # Update lesson metadata
        lesson.content_format = 'blocks'
        lesson.has_media_content = any(block.get('type') in ['image', 'video', 'audio'] for block in blocks_data)
        lesson.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Content blocks saved successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@lesson_editor_bp.route('/<int:lesson_id>/media', methods=['POST'])
@login_required
def upload_media(lesson_id):
    """Upload media files for lesson"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        # Determine file type
        file_type = get_file_type(file.filename)
        if file_type == 'unknown':
            return jsonify({'error': 'File type not supported'}), 400
            
        if not allowed_file(file.filename, file_type):
            return jsonify({'error': f'File type not allowed for {file_type}'}), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZES.get(file_type, 10 * 1024 * 1024):
            return jsonify({'error': f'File too large. Maximum size for {file_type}: {MAX_FILE_SIZES.get(file_type, 10) // (1024*1024)}MB'}), 400
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{original_filename}"
        
        # Create upload directory if it doesn't exist
        lesson_upload_dir = os.path.join(UPLOAD_FOLDER, str(lesson_id))
        os.makedirs(lesson_upload_dir, exist_ok=True)
        
        file_path = os.path.join(lesson_upload_dir, unique_filename)
        file.save(file_path)
        
        # Process file based on type
        thumbnail_path = None
        mime_type = mimetypes.guess_type(original_filename)[0]
        
        if file_type == 'images':
            thumbnail_path = create_image_thumbnail(file_path, lesson_upload_dir)
        elif file_type == 'videos':
            thumbnail_path = create_video_thumbnail(file_path, lesson_upload_dir)
        
        # Save file information to database
        media_file = {
            'lesson_id': lesson_id,
            'original_filename': original_filename,
            'stored_filename': unique_filename,
            'file_path': file_path,
            'file_size': file_size,
            'mime_type': mime_type,
            'media_type': file_type,
            'thumbnail_path': thumbnail_path,
            'is_processed': True,
            'upload_status': 'completed'
        }
        
        db.session.execute(
            """INSERT INTO lesson_media_files 
               (lesson_id, original_filename, stored_filename, file_path, file_size, 
                mime_type, media_type, thumbnail_path, is_processed, upload_status) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (media_file['lesson_id'], media_file['original_filename'], media_file['stored_filename'],
             media_file['file_path'], media_file['file_size'], media_file['mime_type'],
             media_file['media_type'], media_file['thumbnail_path'], 
             media_file['is_processed'], media_file['upload_status'])
        )
        db.session.commit()
        
        # Return file information
        file_url = f"/static/uploads/lessons/{lesson_id}/{unique_filename}"
        thumbnail_url = f"/static/uploads/lessons/{lesson_id}/thumbnails/{os.path.basename(thumbnail_path)}" if thumbnail_path else None
        
        return jsonify({
            'success': True,
            'file': {
                'id': db.session.execute("SELECT last_insert_rowid()").fetchone()[0],
                'filename': original_filename,
                'url': file_url,
                'thumbnail_url': thumbnail_url,
                'type': file_type,
                'size': file_size,
                'mime_type': mime_type
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error uploading media: {str(e)}")
        return jsonify({'error': str(e)}), 500

@lesson_editor_bp.route('/<int:lesson_id>/preview')
@login_required
def preview_lesson(lesson_id):
    """Generate student preview of lesson"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        content_blocks = get_lesson_content_blocks(lesson_id)
        media_files = get_lesson_media_files(lesson_id)
        
        return render_safe_template('admin/lessons/preview.html',
                                   lesson=lesson,
                                   content_blocks=content_blocks,
                                   media_files=media_files)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lesson_editor_bp.route('/templates')
@login_required
def get_templates():
    """Get available lesson templates"""
    try:
        templates = get_lesson_templates()
        return jsonify({
            'success': True,
            'templates': templates
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lesson_editor_bp.route('/templates/<int:template_id>/apply', methods=['POST'])
@login_required
def apply_template(template_id):
    """Apply a template to a lesson"""
    try:
        lesson_id = request.json.get('lesson_id')
        if not lesson_id:
            return jsonify({'error': 'lesson_id required'}), 400
            
        lesson = Lesson.query.get_or_404(lesson_id)
        template = get_lesson_template(template_id)
        
        if not template:
            return jsonify({'error': 'Template not found'}), 404
            
        # Parse template data
        template_data = json.loads(template.get('template_data', '{}'))
        blocks = template_data.get('blocks', [])
        
        # Clear existing blocks and apply template
        db.session.execute("DELETE FROM lesson_content_blocks WHERE lesson_id = ?", (lesson_id,))
        
        for i, block in enumerate(blocks):
            db.session.execute(
                """INSERT INTO lesson_content_blocks 
                   (lesson_id, block_type, content_data, display_order, is_active) 
                   VALUES (?, ?, ?, ?, ?)""",
                (lesson_id, block.get('type'), json.dumps(block), i, True)
            )
        
        # Update template usage count
        db.session.execute(
            "UPDATE lesson_templates SET usage_count = usage_count + 1 WHERE id = ?",
            (template_id,)
        )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Template applied successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Helper functions
def get_lesson_content_blocks(lesson_id):
    """Get content blocks for a lesson"""
    try:
        result = db.session.execute(
            """SELECT id, block_type, content_data, display_order, is_active 
               FROM lesson_content_blocks 
               WHERE lesson_id = ? AND is_active = 1 
               ORDER BY display_order""",
            (lesson_id,)
        ).fetchall()
        
        blocks = []
        for row in result:
            content_data = json.loads(row[2]) if row[2] else {}
            blocks.append({
                'id': row[0],
                'type': row[1],
                'content': content_data,
                'order': row[3],
                'active': row[4]
            })
        return blocks
    except Exception:
        return []

def get_lesson_media_files(lesson_id):
    """Get media files for a lesson"""
    try:
        result = db.session.execute(
            """SELECT id, original_filename, stored_filename, file_path, file_size,
                      mime_type, media_type, thumbnail_path, upload_status
               FROM lesson_media_files 
               WHERE lesson_id = ? 
               ORDER BY created_at DESC""",
            (lesson_id,)
        ).fetchall()
        
        files = []
        for row in result:
            stored_filename = row[2] or ''
            # Build browser-friendly URLs under /static/
            base_url = f"/static/uploads/lessons/{lesson_id}"
            file_url = f"{base_url}/{stored_filename}" if stored_filename else None
            thumb = row[7]
            # If thumbnail_path is stored as filesystem path, derive URL
            thumbnail_url = None
            if thumb:
                # Normalize to forward slashes and strip leading static if present
                thumb_name = os.path.basename(str(thumb))
                thumbnail_url = f"{base_url}/thumbnails/{thumb_name}"

            files.append({
                'id': row[0],
                'filename': row[1],
                'stored_filename': stored_filename,
                'path': row[3],
                'url': file_url,
                'size': row[4],
                'mime_type': row[5],
                'type': row[6],
                'thumbnail': row[7],
                'thumbnail_url': thumbnail_url,
                'status': row[8]
            })
        return files
    except Exception:
        return []

def get_lesson_templates():
    """Get available lesson templates"""
    try:
        result = db.session.execute(
            """SELECT id, name, description, template_data, category, usage_count
               FROM lesson_templates 
               WHERE is_public = 1 
               ORDER BY usage_count DESC, name"""
        ).fetchall()
        
        templates = []
        for row in result:
            templates.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'template_data': row[3],
                'category': row[4],
                'usage_count': row[5]
            })
        return templates
    except Exception:
        return []

def get_lesson_template(template_id):
    """Get a specific lesson template"""
    try:
        result = db.session.execute(
            """SELECT id, name, description, template_data, category, usage_count
               FROM lesson_templates 
               WHERE id = ? AND is_public = 1""",
            (template_id,)
        ).fetchone()
        
        if result:
            return {
                'id': result[0],
                'name': result[1],
                'description': result[2],
                'template_data': result[3],
                'category': result[4],
                'usage_count': result[5]
            }
        return None
    except Exception:
        return None

def create_image_thumbnail(image_path, upload_dir):
    """Create thumbnail for uploaded image"""
    try:
        thumbnail_dir = os.path.join(upload_dir, 'thumbnails')
        os.makedirs(thumbnail_dir, exist_ok=True)
        
        with Image.open(image_path) as img:
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            thumbnail_filename = f"thumb_{os.path.basename(image_path)}"
            thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)
            img.save(thumbnail_path, quality=85)
            return thumbnail_path
    except Exception as e:
        current_app.logger.error(f"Error creating image thumbnail: {str(e)}")
        return None

def create_video_thumbnail(video_path, upload_dir):
    """Create thumbnail for uploaded video"""
    try:
        thumbnail_dir = os.path.join(upload_dir, 'thumbnails')
        os.makedirs(thumbnail_dir, exist_ok=True)
        
        thumbnail_filename = f"thumb_{os.path.splitext(os.path.basename(video_path))[0]}.jpg"
        thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)
        
        # Use ffmpeg to extract thumbnail from video
        (
            ffmpeg
            .input(video_path, ss=1)  # Extract frame at 1 second
            .output(thumbnail_path, vframes=1, format='image2', vcodec='mjpeg')
            .overwrite_output()
            .run(quiet=True)
        )
        
        return thumbnail_path
    except Exception as e:
        current_app.logger.error(f"Error creating video thumbnail: {str(e)}")
        return None
