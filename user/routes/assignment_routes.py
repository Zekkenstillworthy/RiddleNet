"""
User Assignment Routes
Student-facing routes for viewing and submitting assignments
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user

from __init__ import db
from admin.models.class_content import ClassAssignment
from admin.models.assignment_submission import AssignmentSubmission
from admin.models.class_model import Class, class_students
from user.models.user import User
from utils.auth_utils import flexible_login_required, get_current_user_context

user_assignment_bp = Blueprint('user_assignments', __name__, url_prefix='/assignments')

@user_assignment_bp.route('/')
@flexible_login_required
def assignment_list():
    """Display all assignments for the current user's enrolled classes"""
    try:
        user_context = get_current_user_context()
        print(f"[ASSIGNMENTS] assignment_list entered. user_context={user_context}")
        if not user_context['is_authenticated']:
            print("[ASSIGNMENTS] assignment_list: user not authenticated -> redirect to login")
            flash('Please log in to view your assignments', 'info')
            return redirect(url_for('user.login'))
        
        user_id = user_context['user_id']
        
        # Get user's enrolled classes
        enrollments = db.session.query(class_students).filter(
            class_students.c.user_id == user_id
        ).all()
        class_ids = [enrollment.class_id for enrollment in enrollments]
        print(f"[ASSIGNMENTS] assignment_list: user_id={user_id}, class_ids={class_ids}")
        
        if not class_ids:
            print("[ASSIGNMENTS] assignment_list: no enrolled classes -> render no_classes page")
            return render_template('user/assignments/no_classes.html')
        
        # Get all assignments for enrolled classes
        assignments = ClassAssignment.query.filter(
            ClassAssignment.class_id.in_(class_ids),
            ClassAssignment.is_published == True
        ).order_by(ClassAssignment.due_date.asc(), ClassAssignment.created_at.desc()).all()
        print(f"[ASSIGNMENTS] assignment_list: fetched {len(assignments)} assignments for classes {class_ids}")
        
        # Get submission status for each assignment
        assignment_data = []
        for assignment in assignments:
            submission = AssignmentSubmission.query.filter_by(
                assignment_id=assignment.id,
                student_id=user_id
            ).first()
            status = get_assignment_status(assignment, submission)
            print(f"[ASSIGNMENTS] assignment_list: assignment_id={assignment.id}, title='{assignment.title}', submission_id={getattr(submission, 'id', None)}, status={status}")
            assignment_data.append({
                'assignment': assignment,
                'submission': submission,
                'status': status
            })
        
        return render_template('user/assignments/assignment_list.html', 
                               assignments=assignment_data)
        
    except Exception as e:
        # Do not fallback to dashboard; print error for debugging
        print(f"[ASSIGNMENTS][ERROR] assignment_list failed: {e}")
        import traceback; traceback.print_exc()
        return f"Error loading assignments: {e}", 500

@user_assignment_bp.route('/<int:assignment_id>')
@flexible_login_required
def view_assignment(assignment_id):
    """View a specific assignment and submission status"""
    try:
        user_context = get_current_user_context()
        print(f"[ASSIGNMENTS] view_assignment entered. assignment_id={assignment_id}, user_context={user_context}")
        if not user_context['is_authenticated']:
            print("[ASSIGNMENTS] view_assignment: user not authenticated -> redirect to login")
            flash('Please log in to view this assignment', 'info')
            return redirect(url_for('user.login'))
        
        user_id = user_context['user_id']
        assignment = ClassAssignment.query.get_or_404(assignment_id)
        
        # Check if user is enrolled in the class
        enrollment = db.session.query(class_students).filter(
            class_students.c.user_id == user_id,
            class_students.c.class_id == assignment.class_id
        ).first()
        print(f"[ASSIGNMENTS] view_assignment: enrollment_found={bool(enrollment)} for user_id={user_id}, class_id={assignment.class_id}")
        
        if not enrollment:
            flash('You are not enrolled in this class', 'error')
            return redirect(url_for('user_assignments.assignment_list'))
        
        if not assignment.is_published:
            print(f"[ASSIGNMENTS] view_assignment: assignment_id={assignment_id} not published")
            flash('This assignment is not yet published', 'error')
            return redirect(url_for('user_assignments.assignment_list'))
        
        # Get existing submission
        submission = AssignmentSubmission.query.filter_by(
            assignment_id=assignment_id,
            student_id=user_id
        ).first()
        print(f"[ASSIGNMENTS] view_assignment: submission_id={getattr(submission, 'id', None)}")
        
        # Determine if user can submit
        can_submit = assignment.is_published and (
            not submission or assignment.allow_resubmission
        )
        print(f"[ASSIGNMENTS] view_assignment: can_submit={can_submit}, allow_resubmission={assignment.allow_resubmission}")
        
        # Check if late submission
        from datetime import datetime
        is_past_due = assignment.due_date and datetime.utcnow() > assignment.due_date
        print(f"[ASSIGNMENTS] view_assignment: is_past_due={bool(is_past_due)}, due_date={assignment.due_date}")
        
        return render_template('user/assignments/assignment_detail.html',
                               assignment=assignment,
                               submission=submission,
                               can_submit=can_submit,
                               is_past_due=is_past_due,
                               status=get_assignment_status(assignment, submission))
        
    except Exception as e:
        print(f"[ASSIGNMENTS][ERROR] view_assignment failed: {e}")
        import traceback; traceback.print_exc()
        return f"Error loading assignment: {e}", 500

@user_assignment_bp.route('/<int:assignment_id>/api/details')
@flexible_login_required
def api_assignment_details(assignment_id):
    """API endpoint to get assignment details for modal display"""
    try:
        user_context = get_current_user_context()
        print(f"[ASSIGNMENTS] api_assignment_details entered. assignment_id={assignment_id}")
        print(f"[ASSIGNMENTS] User context: {user_context}")
        if not user_context['is_authenticated']:
            print(f"[ASSIGNMENTS] User not authenticated")
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_id = user_context['user_id']
        assignment = ClassAssignment.query.get_or_404(assignment_id)
        
        # Check if user is enrolled in the class
        enrollment = db.session.query(class_students).filter(
            class_students.c.user_id == user_id,
            class_students.c.class_id == assignment.class_id
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'You are not enrolled in this class'}), 403
        
        # Get existing submission
        submission = AssignmentSubmission.query.filter_by(
            assignment_id=assignment_id,
            student_id=user_id
        ).first()
        
        # Check if late submission
        from datetime import datetime
        is_past_due = assignment.due_date and datetime.utcnow() > assignment.due_date
        
        # Format assignment data for frontend
        assignment_data = {
            'id': assignment.id,
            'title': assignment.title,
            'description': assignment.description,
            'instructions': assignment.instructions,
            'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
            'points': assignment.points,
            'allow_text_submission': assignment.allow_text_submission,
            'allow_file_uploads': assignment.allow_file_uploads,
            'allowed_file_types': assignment.allowed_file_types,
            'max_files': assignment.max_files,
            'max_file_size_mb': assignment.max_file_size_mb,
            'allow_resubmission': assignment.allow_resubmission,
            'allow_late_submissions': assignment.allow_late_submissions,
            'is_published': assignment.is_published,
            'class_name': assignment.class_obj.name,
            'is_past_due': is_past_due
        }
        
        submission_data = None
        if submission:
            submission_data = {
                'id': submission.id,
                'submission_text': submission.submission_text,
                'submitted_at': submission.submitted_at.isoformat() if submission.submitted_at else None,
                'status': submission.status,
                'grade': submission.grade,
                'feedback': submission.feedback,
                'is_late': submission.is_late
            }
        
        return jsonify({
            'success': True,
            'assignment': assignment_data,
            'submission': submission_data,
            'can_submit': assignment.is_published and (not submission or assignment.allow_resubmission),
            'is_past_due': is_past_due
        })
        
    except Exception as e:
        print(f"[ASSIGNMENTS][ERROR] api_assignment_details failed: {e}")
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@user_assignment_bp.route('/<int:assignment_id>/submit')
@flexible_login_required
def submit_assignment_form(assignment_id):
    """Display the assignment submission form"""
    try:
        user_context = get_current_user_context()
        print(f"[ASSIGNMENTS] submit_assignment_form entered. assignment_id={assignment_id}, user_context={user_context}")
        if not user_context['is_authenticated']:
            print("[ASSIGNMENTS] submit_assignment_form: user not authenticated -> redirect to login")
            flash('Please log in to submit this assignment', 'info')
            return redirect(url_for('user.login'))
        
        user_id = user_context['user_id']
        assignment = ClassAssignment.query.get_or_404(assignment_id)
        
        # Check if user is enrolled in the class
        enrollment = db.session.query(class_students).filter(
            class_students.c.user_id == user_id,
            class_students.c.class_id == assignment.class_id
        ).first()
        print(f"[ASSIGNMENTS] submit_assignment_form: enrollment_found={bool(enrollment)} for user_id={user_id}, class_id={assignment.class_id}")
        
        if not enrollment:
            flash('You are not enrolled in this class', 'error')
            return redirect(url_for('user_assignments.assignment_list'))
        
        if not assignment.is_published:
            print(f"[ASSIGNMENTS] submit_assignment_form: assignment_id={assignment_id} not published")
            flash('This assignment is not yet published', 'error')
            return redirect(url_for('user_assignments.assignment_list'))
        
        # Get existing submission
        submission = AssignmentSubmission.query.filter_by(
            assignment_id=assignment_id,
            student_id=user_id
        ).first()
        print(f"[ASSIGNMENTS] submit_assignment_form: existing_submission_id={getattr(submission, 'id', None)}")
        
        # Check if submission is allowed
        if submission and not assignment.allow_resubmission:
            print("[ASSIGNMENTS] submit_assignment_form: resubmission not allowed, redirecting to view_assignment")
            flash('You have already submitted this assignment and resubmission is not allowed', 'warning')
            return redirect(url_for('user_assignments.view_assignment', assignment_id=assignment_id))
        
        # Check if late submission is allowed
        from datetime import datetime
        is_past_due = assignment.due_date and datetime.utcnow() > assignment.due_date
        print(f"[ASSIGNMENTS] submit_assignment_form: is_past_due={bool(is_past_due)}, allow_late={assignment.allow_late_submissions}")
        if is_past_due and not assignment.allow_late_submissions:
            print("[ASSIGNMENTS] submit_assignment_form: late submissions not allowed -> redirect to view page")
            flash('This assignment is past due and late submissions are not allowed', 'error')
            return redirect(url_for('user_assignments.view_assignment', assignment_id=assignment_id))
        
        print(f"[ASSIGNMENTS] submit_assignment_form: rendering submission form for assignment_id={assignment_id}")
        return render_template('user/assignments/submit_assignment.html',
                               assignment=assignment,
                               existing_submission=submission,
                               is_past_due=is_past_due)
        
    except Exception as e:
        print(f"[ASSIGNMENTS][ERROR] submit_assignment_form failed: {e}")
        import traceback; traceback.print_exc()
        return f"Error loading submission form: {e}", 500

@user_assignment_bp.route('/<int:assignment_id>/api/submit', methods=['POST'])
@flexible_login_required
def api_submit_assignment(assignment_id):
    """API endpoint for submitting assignments via AJAX"""
    try:
        user_context = get_current_user_context()
        print(f"[ASSIGNMENTS] api_submit_assignment entered. assignment_id={assignment_id}")
        if not user_context['is_authenticated']:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_id = user_context['user_id']
        assignment = ClassAssignment.query.get_or_404(assignment_id)
        
        # Check if user is enrolled in the class
        enrollment = db.session.query(class_students).filter(
            class_students.c.user_id == user_id,
            class_students.c.class_id == assignment.class_id
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'You are not enrolled in this class'}), 403
        
        if not assignment.is_published:
            return jsonify({'error': 'Assignment is not published'}), 400
        
        # Get submission data
        submission_text = request.form.get('submission_text', '')
        
        # Validate that we have either text or files (basic validation)
        files = request.files.getlist('files')
        if not submission_text and not files:
            return jsonify({'error': 'Please provide either text submission or file attachments'}), 400
        
        # Check if text submission is allowed
        if submission_text and not assignment.allow_text_submission:
            return jsonify({'error': 'Text submissions not allowed for this assignment'}), 400
        
        # Check if file uploads are allowed
        if files and not assignment.allow_file_uploads:
            return jsonify({'error': 'File uploads not allowed for this assignment'}), 400
        
        # Get existing submission
        existing_submission = AssignmentSubmission.query.filter_by(
            assignment_id=assignment_id,
            student_id=user_id
        ).first()
        
        if existing_submission and not assignment.allow_resubmission:
            return jsonify({'error': 'Resubmission not allowed for this assignment'}), 400
        
        # Check if late submission is allowed
        from datetime import datetime
        is_past_due = assignment.due_date and datetime.utcnow() > assignment.due_date
        if is_past_due and not assignment.allow_late_submissions:
            return jsonify({'error': 'Late submissions not allowed for this assignment'}), 400
        
        # Create or update submission (simplified - redirect to admin controller for full implementation)
        # For now, just create a basic text submission
        if existing_submission:
            existing_submission.submission_text = submission_text
            existing_submission.submitted_at = datetime.utcnow()
            existing_submission.status = 'resubmitted'
        else:
            submission = AssignmentSubmission(
                assignment_id=assignment_id,
                student_id=user_id,
                submission_text=submission_text,
                max_points=assignment.points,
                is_late=is_past_due,
                status='submitted'
            )
            db.session.add(submission)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Assignment submitted successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"[ASSIGNMENTS][ERROR] api_submit_assignment failed: {e}")
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def get_assignment_status(assignment, submission):
    """Get the status of an assignment for a student"""
    from datetime import datetime
    
    if not submission:
        if assignment.due_date and datetime.utcnow() > assignment.due_date:
            return 'overdue'
        return 'not_submitted'
    
    if submission.status == 'graded':
        return 'graded'
    elif submission.status == 'resubmitted':
        return 'resubmitted'
    else:
        return 'submitted'