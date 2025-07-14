from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from admin.models.essay_response import EssayResponse
from admin.models.user import AdminUser
from admin.models.activity_log import ActivityLog
from user.models.user import User  # Import the correct User model
from admin import db
from sqlalchemy import func
from datetime import datetime
from flask_login import login_required, current_user

essay_bp = Blueprint('essay', __name__)

@essay_bp.route('/essays')
@login_required
def index():
    """Display all essay responses with filters"""
    # Get filter parameters
    reviewed = request.args.get('reviewed', 'all')
    category = request.args.get('category', 'all')
    sort_by = request.args.get('sort_by', 'newest')
    
    # Base query
    query = EssayResponse.query
    
    # Apply filters
    if reviewed != 'all':
        is_reviewed = (reviewed == 'yes')
        query = query.filter(EssayResponse.is_graded == is_reviewed)
    
    if category != 'all':
        query = query.filter(EssayResponse.category == category)
    
    # Apply sorting
    if sort_by == 'newest':
        query = query.order_by(EssayResponse.submission_date.desc())
    elif sort_by == 'oldest':
        query = query.order_by(EssayResponse.submission_date)
    
    # Execute query
    essays = query.all()
    
    return render_template('admin/essays.html', 
                           essays=essays, 
                           active_page='essays',
                           current_filters={
                               'reviewed': reviewed,
                               'category': category,
                               'sort_by': sort_by
                           })

@essay_bp.route('/users')
@login_required
def users():
    """Display users with their essay responses"""
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Get all users
    users = User.query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get essay statistics for each user
    users_data = []
    users_with_essays = 0
    total_essays = 0
    pending_essays = 0
    
    for user in users.items:
        # Get all essays for this user
        essays = EssayResponse.query.filter_by(user_id=user.id).all()
        essay_count = len(essays)
        
        # Count as a user with essays if they have at least one essay
        if essay_count > 0:
            users_with_essays += 1
            total_essays += essay_count
            
            # Count pending essays
            pending_count = sum(1 for essay in essays if not essay.is_graded)
            pending_essays += pending_count
            
            # Get the date of the most recent essay
            last_essay = max([essay.submission_date for essay in essays]) if essays else None
            
            users_data.append({
                'user': user,
                'essay_count': essay_count,
                'pending_count': pending_count,
                'last_essay': last_essay
            })
        else:
            users_data.append({
                'user': user,
                'essay_count': 0,
                'pending_count': 0,
                'last_essay': None
            })
    
    return render_template('admin/user_essays.html',
                          users_data=users_data,
                          users=users.items,
                          pagination=users,
                          users_with_essays=users_with_essays,
                          total_essays=total_essays,
                          pending_essays=pending_essays,
                          active_page='users')

@essay_bp.route('/<int:essay_id>')
@login_required
def view(essay_id):
    """View a single essay response with review options"""
    essay = EssayResponse.query.get_or_404(essay_id)
    user = User.query.get(essay.user_id) if essay.user_id else None
    
    return render_template('admin/essay_detail.html', 
                           essay=essay, 
                           user=user,
                           active_page='essays')

@essay_bp.route('/<int:essay_id>/review', methods=['POST'])
@login_required
def review(essay_id):
    """Review an essay response"""
    essay = EssayResponse.query.get_or_404(essay_id)
    
    # Get review data from form
    feedback = request.form.get('feedback', '')
    grade = request.form.get('grade')
    
    if grade:
        try:
            grade = float(grade)
        except ValueError:
            flash('Invalid grade value', 'danger')
            return redirect(url_for('essay.view', essay_id=essay_id))
    
    # Update the essay response
    essay.feedback = feedback
    essay.graded_score = grade  # Changed from grade to graded_score
    essay.is_graded = True      # Changed from reviewed to is_graded
    db.session.commit()
    
    # Log the activity
    ActivityLog.log_activity(
        user_id=1,  # Admin user ID
        action_type='review',
        message=f'Reviewed essay response #{essay_id}',
        related_entity_type='essay',
        related_entity_id=essay_id
    )
    
    flash('Essay reviewed successfully', 'success')
    return redirect(url_for('essay.index'))

@essay_bp.route('/<int:essay_id>/delete', methods=['POST'])
@login_required
def delete(essay_id):
    """Delete an essay response"""
    essay = EssayResponse.query.get_or_404(essay_id)
    
    # Delete the essay response
    db.session.delete(essay)
    db.session.commit()
    
    # Log the activity
    ActivityLog.log_activity(
        user_id=1,  # Admin user ID
        action_type='delete',
        message=f'Deleted essay response #{essay_id}',
        related_entity_type='essay',
        related_entity_id=essay_id
    )
    
    flash('Essay response deleted', 'success')
    return redirect(url_for('essay.index'))

# API Endpoints for AJAX functionality

@essay_bp.route('/api/users/<int:user_id>/essays')
@login_required
def get_user_essays(user_id):
    """API endpoint to get all essays for a specific user"""
    user = User.query.get_or_404(user_id)
    essays = EssayResponse.query.filter_by(user_id=user_id).order_by(EssayResponse.submission_date.desc()).all()
    
    # Format essay data for JSON response
    essays_data = []
    for essay in essays:
        essays_data.append({
            'id': essay.id,
            'question': essay.question_text,  # Changed from essay.question
            'answer': essay.response_text,    # Changed from essay.answer
            'category': essay.category,
            'submission_date': essay.submission_date.strftime('%Y-%m-%d %H:%M'),
            'is_graded': essay.is_graded,
            'graded_score': essay.graded_score
        })
    
    return jsonify({
        'user_id': user_id,
        'username': user.username,
        'essays': essays_data
    })

@essay_bp.route('/api/essays/<int:essay_id>/grade', methods=['POST'])
@login_required
def api_grade_essay(essay_id):
    """API endpoint to grade an essay"""
    essay = EssayResponse.query.get_or_404(essay_id)
    
    # Get grade from request
    data = request.json
    grade = data.get('grade')
    
    if grade is None:
        return jsonify({'error': 'Grade is required'}), 400
    
    try:
        grade = float(grade)
        if grade < 0 or grade > 100:
            return jsonify({'error': 'Grade must be between 0 and 100'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid grade value'}), 400
    
    # Update the essay
    essay.graded_score = grade
    essay.is_graded = True
    db.session.commit()
    
    # Log the activity
    ActivityLog.log_activity(
        user_id=current_user.id,
        action_type='grade',
        message=f'Graded essay response #{essay_id} with score {grade}',
        related_entity_type='essay',
        related_entity_id=essay_id
    )
    
    return jsonify({
        'success': True,
        'essay_id': essay_id,
        'grade': grade
    })

@essay_bp.route('/api/essays/<int:essay_id>')
@login_required
def api_get_essay(essay_id):
    """API endpoint to get essay details"""
    essay = EssayResponse.query.get_or_404(essay_id)
    
    return jsonify({
        'success': True,
        'essay': {
            'id': essay.id,
            'question_text': essay.question_text,
            'response_text': essay.response_text,
            'category': essay.category,
            'submission_date': essay.submission_date.strftime('%Y-%m-%d %H:%M'),
            'is_graded': essay.is_graded,
            'graded_score': essay.graded_score,
            'user_id': essay.user_id
        }
    })

@essay_bp.route('/<int:essay_id>/edit', methods=['POST'])
@login_required
def edit(essay_id):
    """Edit an essay response"""
    essay = EssayResponse.query.get_or_404(essay_id)
    
    # Update essay fields
    essay.question_text = request.form.get('question_text', essay.question_text)
    essay.response_text = request.form.get('response_text', essay.response_text)
    essay.category = request.form.get('category', essay.category)
    
    db.session.commit()
    
    # Log the activity
    ActivityLog.log_activity(
        user_id=current_user.id,
        action_type='edit',
        message=f'Edited essay response #{essay_id}',
        related_entity_type='essay',
        related_entity_id=essay_id
    )
    
    return jsonify({
        'success': True,
        'message': 'Essay updated successfully'
    })
