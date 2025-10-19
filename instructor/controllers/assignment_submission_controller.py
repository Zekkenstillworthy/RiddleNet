"""
Assignment Submission Controller
Handles student assignment submissions, file uploads, and grading
"""

import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_login import login_required, current_user

from __init__ import db
from instructor.models.class_content import ClassAssignment
from instructor.models.assignment_submission import AssignmentSubmission, SubmissionAttachment, AssignmentSubmissionHistory
from instructor.models.rubric import Rubric, RubricCriterion, RubricAssessment
from user.models.user import User

assignment_submission_bp = Blueprint('assignment_submission', __name__)

# Allowed file extensions and their MIME types
ALLOWED_EXTENSIONS = {
    'pdf': 'application/pdf',
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'txt': 'text/plain',
    'rtf': 'application/rtf',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'zip': 'application/zip',
    'rar': 'application/x-rar-compressed'
}

def allowed_file(filename, allowed_types=None):
    """Check if file extension is allowed"""
    if not filename or '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    
    if allowed_types:
        allowed_list = [t.strip().lower() for t in allowed_types.split(',')]
        return ext in allowed_list
    
    return ext in ALLOWED_EXTENSIONS

def get_file_size_mb(file_size_bytes):
    """Convert file size from bytes to MB"""
    return file_size_bytes / (1024 * 1024)

@assignment_submission_bp.route('/api/assignments/<int:assignment_id>/submissions', methods=['GET'])
@login_required
def get_assignment_submissions(assignment_id):
    """Get all submissions for an assignment (admin only)"""
    try:
        # Check if user is admin
        if not hasattr(current_user, 'role') or current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        assignment = ClassAssignment.query.get_or_404(assignment_id)
        submissions = AssignmentSubmission.query.filter_by(assignment_id=assignment_id).all()
        
        return jsonify({
            'success': True,
            'assignment': assignment.to_dict(),
            'submissions': [submission.to_dict() for submission in submissions]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assignment_submission_bp.route('/api/assignments/<int:assignment_id>/submit', methods=['POST'])
@login_required
def submit_assignment(assignment_id):
    """Submit an assignment with text and/or file attachments"""
    try:
        assignment = ClassAssignment.query.get_or_404(assignment_id)
        
        # Check if assignment accepts submissions
        if not assignment.is_published:
            return jsonify({'error': 'Assignment is not published'}), 400
        
        # Check for existing submission
        existing_submission = AssignmentSubmission.query.filter_by(
            assignment_id=assignment_id,
            student_id=current_user.id
        ).first()
        
        if existing_submission and not assignment.allow_resubmission:
            return jsonify({'error': 'Resubmission not allowed for this assignment'}), 400
        
        # Get submission data
        submission_text = request.form.get('submission_text', '')
        
        # Validate that we have either text or files
        files = request.files.getlist('files')
        if not submission_text and not files:
            return jsonify({'error': 'Please provide either text submission or file attachments'}), 400
        
        # Check if text submission is allowed
        if submission_text and not assignment.allow_text_submission:
            return jsonify({'error': 'Text submissions not allowed for this assignment'}), 400
        
        # Check if file uploads are allowed
        if files and not assignment.allow_file_uploads:
            return jsonify({'error': 'File uploads not allowed for this assignment'}), 400
        
        # Validate files
        if files:
            if len(files) > assignment.max_files:
                return jsonify({'error': f'Maximum {assignment.max_files} files allowed'}), 400
            
            for file in files:
                if file.filename == '':
                    continue
                
                if not allowed_file(file.filename, assignment.allowed_file_types):
                    return jsonify({'error': f'File type not allowed: {file.filename}'}), 400
                
                # Check file size (approximate, will be exact after saving)
                file.seek(0, 2)  # Seek to end
                file_size = file.tell()
                file.seek(0)  # Reset to beginning
                
                if get_file_size_mb(file_size) > assignment.max_file_size_mb:
                    return jsonify({'error': f'File too large: {file.filename} (max {assignment.max_file_size_mb}MB)'}), 400
        
        # Check if submission is late
        is_late = False
        if assignment.due_date and datetime.utcnow() > assignment.due_date:
            if not assignment.allow_late_submissions:
                return jsonify({'error': 'Late submissions not allowed for this assignment'}), 400
            is_late = True
        
        # Create or update submission
        if existing_submission:
            submission = existing_submission
            submission.submission_text = submission_text
            submission.submitted_at = datetime.utcnow()
            submission.status = 'resubmitted'
            
            # Remove old attachments
            for attachment in submission.attachments:
                try:
                    os.remove(os.path.join(current_app.root_path, attachment.file_path))
                except:
                    pass
                db.session.delete(attachment)
        else:
            submission = AssignmentSubmission(
                assignment_id=assignment_id,
                student_id=current_user.id,
                submission_text=submission_text,
                max_points=assignment.points,
                is_late=is_late,
                status='submitted'
            )
            db.session.add(submission)
        
        # Flush to get submission ID
        db.session.flush()
        
        # Handle file uploads
        uploaded_files = []
        if files:
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'assignments', 'submissions')
            os.makedirs(upload_dir, exist_ok=True)
            
            for file in files:
                if file.filename == '':
                    continue
                
                # Generate unique filename
                file_ext = file.filename.rsplit('.', 1)[1].lower()
                stored_filename = f"{uuid.uuid4()}.{file_ext}"
                file_path = os.path.join(upload_dir, stored_filename)
                
                # Save file
                file.save(file_path)
                
                # Get actual file size
                file_size = os.path.getsize(file_path)
                
                # Create attachment record
                attachment = SubmissionAttachment(
                    submission_id=submission.id,
                    original_filename=secure_filename(file.filename),
                    stored_filename=stored_filename,
                    file_path=f"static/uploads/assignments/submissions/{stored_filename}",
                    file_size=file_size,
                    mime_type=ALLOWED_EXTENSIONS.get(file_ext, 'application/octet-stream')
                )
                db.session.add(attachment)
                uploaded_files.append(attachment.original_filename)
        
        # Add history entry
        history = AssignmentSubmissionHistory(
            submission_id=submission.id,
            action='resubmitted' if existing_submission else 'submitted',
            changed_by=current_user.id,
            changed_by_type='student',
            notes=f"Submitted with {len(uploaded_files)} file(s)" if uploaded_files else "Text submission only"
        )
        db.session.add(history)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Assignment submitted successfully!',
            'submission': submission.to_dict(),
            'uploaded_files': uploaded_files
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@assignment_submission_bp.route('/api/submissions/<int:submission_id>', methods=['GET'])
@login_required
def get_submission(submission_id):
    """Get a specific submission"""
    try:
        submission = AssignmentSubmission.query.get_or_404(submission_id)
        
        # Check permissions
        if hasattr(current_user, 'role') and current_user.role == 'admin':
            # Admin can view any submission
            pass
        elif submission.student_id == current_user.id:
            # Student can view their own submission
            pass
        else:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'success': True,
            'submission': submission.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assignment_submission_bp.route('/api/submissions/<int:submission_id>/grade', methods=['POST'])
@login_required
def grade_submission(submission_id):
    """Grade a submission (admin only)"""
    try:
        # Check if user is admin
        if not hasattr(current_user, 'role') or current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        submission = AssignmentSubmission.query.get_or_404(submission_id)
        data = request.json or {}

        old_grade = submission.grade
        old_status = submission.status

        rubric_payload = data.get('rubric_assessments')
        total_grade = data.get('grade')
        feedback = data.get('feedback', '')

        # If rubric assessments are provided, compute total based on criteria
        if rubric_payload and isinstance(rubric_payload, list):
            # Clear existing rubric assessments for this submission
            try:
                RubricAssessment.query.filter_by(submission_id=submission.id).delete()
            except Exception:
                pass

            awarded_total = 0.0
            max_total = 0.0
            for item in rubric_payload:
                try:
                    criterion_id = int(item.get('criterion_id'))
                    awarded_points = float(item.get('awarded_points', 0.0))
                    feedback_item = item.get('feedback')
                except Exception:
                    continue
                criterion = RubricCriterion.query.get(criterion_id)
                if not criterion:
                    continue
                # clamp awarded points
                awarded_points = max(0.0, min(awarded_points, float(criterion.max_points)))
                assess = RubricAssessment(
                    submission_id=submission.id,
                    rubric_id=criterion.rubric_id,
                    criterion_id=criterion.id,
                    awarded_points=awarded_points,
                    feedback=feedback_item
                )
                db.session.add(assess)
                awarded_total += awarded_points
                max_total += float(criterion.max_points)
            # Scale to assignment max points
            if max_total > 0:
                scale = (submission.max_points or 100) / max_total
                total_grade = round(awarded_total * scale)

        # Update grade and feedback
        submission.grade = total_grade
        submission.feedback = feedback
        submission.status = 'graded'
        submission.graded_at = datetime.utcnow()
        submission.graded_by = current_user.id

        # Add history entry
        history = AssignmentSubmissionHistory(
            submission_id=submission.id,
            action='graded',
            old_grade=old_grade,
            new_grade=submission.grade,
            old_status=old_status,
            new_status='graded',
            changed_by=current_user.id,
            changed_by_type='admin',
            notes=f"Graded: {submission.grade}/{submission.max_points}"
        )
        db.session.add(history)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Submission graded successfully!',
            'submission': submission.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@assignment_submission_bp.route('/api/submissions/attachments/<int:attachment_id>/download')
@login_required
def download_attachment(attachment_id):
    """Download a submission attachment"""
    try:
        attachment = SubmissionAttachment.query.get_or_404(attachment_id)
        submission = attachment.submission
        
        # Check permissions
        if hasattr(current_user, 'role') and current_user.role == 'admin':
            # Admin can download any attachment
            pass
        elif submission.student_id == current_user.id:
            # Student can download their own attachments
            pass
        else:
            return jsonify({'error': 'Access denied'}), 403
        
        file_path = os.path.join(current_app.root_path, attachment.file_path)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=attachment.original_filename,
            mimetype=attachment.mime_type
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assignment_submission_bp.route('/api/students/<int:student_id>/assignments/<int:assignment_id>/submission', methods=['GET'])
@login_required
def get_student_submission(student_id, assignment_id):
    """Get a student's submission for a specific assignment"""
    try:
        # Check permissions
        if hasattr(current_user, 'role') and current_user.role == 'admin':
            # Admin can view any student's submission
            pass
        elif current_user.id == student_id:
            # Student can view their own submission
            pass
        else:
            return jsonify({'error': 'Access denied'}), 403
        
        assignment = ClassAssignment.query.get_or_404(assignment_id)
        submission = AssignmentSubmission.query.filter_by(
            assignment_id=assignment_id,
            student_id=student_id
        ).first()
        
        return jsonify({
            'success': True,
            'assignment': assignment.to_dict(),
            'submission': submission.to_dict() if submission else None,
            'can_submit': assignment.is_published and (
                not submission or assignment.allow_resubmission
            )
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500