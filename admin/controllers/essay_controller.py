from flask import Blueprint, render_template, redire        return render_template('admin/essays.html',
                             step='classes',
                             classes_data=classes_data,
                             pagination=classes_pagination,
                             active_page='essays',
                             current_filters={})rl_for, request, flash, jsonify
from admin.models.essay_response import EssayResponse
from admin.models.user import AdminUser
from admin.models.activity_log import ActivityLog
from admin.models.class_model import Class
from user.models.user import User  # Import the correct User model
from admin import db
from sqlalchemy import func
from datetime import datetime
from flask_login import login_required, current_user

essay_bp = Blueprint('essay', __name__)

@essay_bp.route('/essays')
@login_required
def index():
    """Display classes, students, and essay responses with pagination"""
    # Get current step from query parameters
    step = request.args.get('step', 'classes')  # classes, students, essays
    class_id = request.args.get('class_id', type=int)
    student_id = request.args.get('student_id', type=int)
    
    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Fixed to 10 items per page
    
    if step == 'classes':
        # Step 1: Show classes with pagination
        classes_pagination = Class.query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get statistics for each class
        classes_data = []
        total_students = 0
        total_essays = 0
        total_pending = 0
        
        for class_obj in classes_pagination.items:
            student_count = class_obj.students.count()
            essay_count = 0
            pending_count = 0
            graded_count = 0
            total_scores = 0
            
            # Count essays from students in this class
            for student in class_obj.students:
                student_essays = EssayResponse.query.filter_by(user_id=student.id).all()
                essay_count += len(student_essays)
                for essay in student_essays:
                    if not essay.is_graded:
                        pending_count += 1
                    else:
                        graded_count += 1
                        if essay.graded_score:
                            total_scores += essay.graded_score
            
            # Calculate completion rate
            completion_rate = (graded_count / essay_count * 100) if essay_count > 0 else 0
            
            classes_data.append({
                'id': class_obj.id,
                'name': class_obj.name,
                'section': class_obj.section,
                'code': class_obj.code,
                'student_count': student_count,
                'essay_count': essay_count,
                'pending_count': pending_count,
                'completion_rate': round(completion_rate, 1)
            })
            
            total_students += student_count
            total_essays += essay_count
            total_pending += pending_count
        
        # Overall stats for dashboard
        stats = {
            'total_classes': classes_pagination.total,
            'total_students': total_students,
            'total_essays': total_essays,
            'completion_rate': round((total_essays - total_pending) / total_essays * 100, 1) if total_essays > 0 else 0
        }
        
        return render_template('admin/essays_enhanced.html',
                             step='classes',
                             classes_data=classes_data,
                             pagination=classes_pagination,
                             stats=stats,
                             active_page='essays',
                             current_filters={
                                 'reviewed': 'all',
                                 'category': 'all', 
                                 'sort_by': 'newest'
                             })
    
    elif step == 'students' and class_id:
        # Step 2: Show students in selected class with pagination
        selected_class = Class.query.get_or_404(class_id)
        
        # Get students with pagination
        students_query = selected_class.students
        students_pagination = students_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get essay statistics for each student
        students_data = []
        total_essays = 0
        total_pending = 0
        total_scores = 0
        scored_essays = 0
        
        for student in students_pagination.items:
            essays = EssayResponse.query.filter_by(user_id=student.id).all()
            essay_count = len(essays)
            pending_count = len([e for e in essays if not e.is_graded])
            graded_count = essay_count - pending_count
            
            # Calculate student's average score and completion rate
            student_scores = [e.graded_score for e in essays if e.graded_score is not None]
            average_score = sum(student_scores) / len(student_scores) if student_scores else 0
            completion_rate = (graded_count / essay_count * 100) if essay_count > 0 else 0
            
            students_data.append({
                'id': student.id,
                'username': student.username,
                'email': student.email,
                'essay_count': essay_count,
                'pending_count': pending_count,
                'average_score': round(average_score, 1),
                'completion_rate': round(completion_rate, 1)
            })
            
            total_essays += essay_count
            total_pending += pending_count
            if student_scores:
                total_scores += sum(student_scores)
                scored_essays += len(student_scores)
        
        # Overall stats for this class
        stats = {
            'total_students': students_pagination.total,
            'total_essays': total_essays,
            'pending_reviews': total_pending,
            'average_score': round(total_scores / scored_essays, 1) if scored_essays > 0 else 0
        }
        
        return render_template('admin/essays_enhanced.html',
                             step='students',
                             selected_class=selected_class,
                             students_data=students_data,
                             pagination=students_pagination,
                             stats=stats,
                             active_page='essays',
                             current_filters={
                                 'reviewed': 'all',
                                 'category': 'all', 
                                 'sort_by': 'newest'
                             })
    
    elif step == 'essays' and class_id and student_id:
        # Step 3: Show essays from selected student with pagination and filters
        selected_class = Class.query.get_or_404(class_id)
        selected_student = User.query.get_or_404(student_id)
        
        # Verify student is in the class
        if selected_student not in selected_class.students:
            flash('Student is not enrolled in the selected class.', 'error')
            return redirect(url_for('essay.index', step='students', class_id=class_id))
        
        # Get filter parameters
        reviewed = request.args.get('reviewed', '')
        category = request.args.get('category', '')
        sort_by = request.args.get('sort_by', 'newest')
        
        # Base query for student's essays
        query = EssayResponse.query.filter_by(user_id=student_id)
        
        # Apply filters
        if reviewed == 'true':
            query = query.filter(EssayResponse.is_graded == True)
        elif reviewed == 'false':
            query = query.filter(EssayResponse.is_graded == False)
        
        if category and category != '':
            query = query.filter(EssayResponse.category == category)
        
        # Apply sorting
        if sort_by == 'newest':
            query = query.order_by(EssayResponse.submission_date.desc())
        elif sort_by == 'oldest':
            query = query.order_by(EssayResponse.submission_date)
        elif sort_by == 'grade_high':
            query = query.order_by(EssayResponse.graded_score.desc().nullslast())
        elif sort_by == 'grade_low':
            query = query.order_by(EssayResponse.graded_score.asc().nullsfirst())
        
        # Get paginated essays
        essays_pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Calculate stats for this student
        all_essays = EssayResponse.query.filter_by(user_id=student_id).all()
        total_essays = len(all_essays)
        graded_essays = [e for e in all_essays if e.is_graded]
        pending_essays = [e for e in all_essays if not e.is_graded]
        
        graded_scores = [e.graded_score for e in graded_essays if e.graded_score is not None]
        average_grade = sum(graded_scores) / len(graded_scores) if graded_scores else 0
        
        stats = {
            'total_essays': total_essays,
            'pending_count': len(pending_essays),
            'reviewed_count': len(graded_essays),
            'average_grade': round(average_grade, 1)
        }
        
        return render_template('admin/essays_enhanced.html',
                             step='essays',
                             selected_class=selected_class,
                             selected_student=selected_student,
                             essays_pagination=essays_pagination,
                             stats=stats,
                             active_page='essays',
                             current_filters={
                                 'class_id': class_id,
                                 'student_id': student_id,
                                 'reviewed': reviewed,
                                 'category': category,
                                 'sort_by': sort_by
                             })
    
    else:
        # Default: redirect to classes view
        return redirect(url_for('essay.index', step='classes'))

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
