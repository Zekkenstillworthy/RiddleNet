"""
Simple Advanced Lesson Editor Controller
Minimal implementation to fix import issues
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from admin import db
from utils.render_utils import render_safe_template
from datetime import datetime
import json
import os

# Create blueprint
advanced_lesson_bp = Blueprint('advanced_lesson', __name__, url_prefix='/admin')

@advanced_lesson_bp.route('/lessons/<int:lesson_id>/advanced-editor')
@login_required
def advanced_editor(lesson_id):
    """Advanced lesson editor interface"""
    try:
        # Import models at runtime to avoid circular imports
        from admin.models.module import Module, Lesson, LessonProgress
        from admin.models.class_model import Class
        from admin.models.simulation import Simulation
        
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
        
        # Content block types configuration
        block_types = {
            'text': {'name': 'Text Block', 'icon': 'text_fields', 'description': 'Rich text content with formatting'},
            'image': {'name': 'Image', 'icon': 'image', 'description': 'Images, diagrams, and visual content'},
            'video': {'name': 'Video', 'icon': 'play_circle', 'description': 'Video content and embeds'},
            'audio': {'name': 'Audio', 'icon': 'audiotrack', 'description': 'Audio recordings and podcasts'},
            'file': {'name': 'File Download', 'icon': 'download', 'description': 'Downloadable files and documents'},
            'quiz': {'name': 'Knowledge Check', 'icon': 'quiz', 'description': 'Interactive questions and assessments'},
            'simulation': {'name': 'Simulation', 'icon': 'science', 'description': 'Interactive simulations and labs'},
            'objectives': {'name': 'Learning Objectives', 'icon': 'checklist', 'description': 'Structured learning objectives'},
            'summary': {'name': 'Summary', 'icon': 'summarize', 'description': 'Key takeaways and conclusions'}
        }
        
        return render_safe_template('admin/lessons/advanced_editor.html',
                                   class_obj=class_obj,
                                   module=module,
                                   lesson=lesson,
                                   content_blocks=content_blocks,
                                   media_files=media_files,
                                   templates=templates,
                                   simulations=simulations,
                                   block_types=block_types)
    except Exception as e:
        current_app.logger.error(f"Error loading advanced editor: {str(e)}")
        flash('Error loading advanced editor', 'error')
        return redirect(url_for('lesson.index'))

@advanced_lesson_bp.route('/lessons/<int:lesson_id>/content-blocks', methods=['GET'])
@login_required
def get_content_blocks(lesson_id):
    """Get lesson content blocks as JSON"""
    try:
        from admin.models.module import Lesson
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
        from admin.models.module import Lesson
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
        
        return jsonify({
            'success': True,
            'message': 'Content blocks saved successfully'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving content blocks: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@advanced_lesson_bp.route('/lessons/<int:lesson_id>/preview')
@login_required
def preview_lesson(lesson_id):
    """Generate student preview of the lesson"""
    try:
        from admin.models.module import Lesson
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
        
        return render_safe_template('admin/lessons/preview.html',
                                   lesson=lesson,
                                   content_blocks=content_blocks,
                                   media_files=media_dict)
    except Exception as e:
        current_app.logger.error(f"Error generating preview: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
