from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from __init__ import db
from ..models.question_group import QuestionGroup
from ..models.question import Question

question_group_bp = Blueprint('question_group', __name__, url_prefix='/admin/groups')

class QuestionGroupController:
    @staticmethod
    @question_group_bp.route('/')
    @login_required
    def index():
        groups = QuestionGroup.query.order_by(QuestionGroup.name).all()
        return render_template(
            'instructor/questions.html',
            groups=groups,
            active_page='questions'
        )
    
    @staticmethod
    @question_group_bp.route('/add', methods=['GET', 'POST'])
    @login_required
    def add_group():
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description', '')
            
            if not name:
                flash('Group name is required', 'error')
                return render_template('instructor/add_question_group.html')
            
            new_group = QuestionGroup(
                name=name,
                description=description
            )
            
            try:
                db.session.add(new_group)
                db.session.commit()
                flash('Quiz created successfully', 'success')
                return redirect(url_for('question_group.index'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating Quiz: {str(e)}', 'error')
                
        return render_template('instructor/add_question_group.html')
    
    @staticmethod
    @question_group_bp.route('/edit/<int:group_id>', methods=['GET', 'POST'])
    @login_required
    def edit_group(group_id):
        group = QuestionGroup.query.get_or_404(group_id)
        
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description', '')
            
            if not name:
                flash('Group name is required', 'error')
                return render_template('instructor/edit_question_group.html', group=group)
            
            group.name = name
            group.description = description
            
            try:
                db.session.commit()
                flash('Quiz updated successfully', 'success')
                return redirect(url_for('question_group.index'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating Quiz: {str(e)}', 'error')
                
        return render_template('instructor/edit_question_group.html', group=group)
    
    @staticmethod
    @question_group_bp.route('/delete/<int:group_id>', methods=['POST'])
    @login_required
    def delete_group(group_id):
        group = QuestionGroup.query.get_or_404(group_id)
        
        try:
            db.session.delete(group)
            db.session.commit()
            flash('Quiz deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting Quiz: {str(e)}', 'error')
            
        return redirect(url_for('question_group.index'))

    @staticmethod
    @question_group_bp.route('/api/delete/<int:group_id>', methods=['DELETE', 'POST'])
    @login_required
    def delete_group_api(group_id):
        """API endpoint to delete a Quiz and return JSON response"""
        try:
            group = QuestionGroup.query.get_or_404(group_id)
            group_name = group.name
            
            db.session.delete(group)
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'message': f'Quiz "{group_name}" deleted successfully'
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False, 
                'message': f'Error deleting Quiz: {str(e)}'
            }), 500
    
    @staticmethod
    @question_group_bp.route('/<int:group_id>')
    @login_required
    def view_group(group_id):
        group = QuestionGroup.query.get_or_404(group_id)
        
        # Group questions by category for better organization
        categorized_questions = {}
        for question in group.questions:
            if question.category not in categorized_questions:
                categorized_questions[question.category] = []
            categorized_questions[question.category].append(question)
        
        return render_template(
            'instructor/group_questions.html',
            group=group,
            questions=group.questions,
            question_count=len(group.questions),
            categorized_questions=categorized_questions,
            active_page='question_groups'
        )
    
    @staticmethod
    @question_group_bp.route('/<int:group_id>/add_questions', methods=['GET', 'POST'])
    @login_required
    def add_questions_to_group(group_id):
        group = QuestionGroup.query.get_or_404(group_id)
        
        if request.method == 'POST':
            question_ids = request.form.getlist('question_ids')
            
            if not question_ids:
                flash('No questions selected', 'error')
                return redirect(url_for('question_group.add_questions_to_group', group_id=group.id))
            
            selected_questions = Question.query.filter(Question.id.in_(question_ids)).all()
            
            for question in selected_questions:
                if question not in group.questions:
                    group.questions.append(question)
            
            try:
                db.session.commit()
                flash(f'Added {len(selected_questions)} question(s) to the group', 'success')
                return redirect(url_for('question_group.view_group', group_id=group.id))
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding questions to group: {str(e)}', 'error')
        
        # Get available questions that are not already in the group
        current_question_ids = [q.id for q in group.questions]
        if current_question_ids:
            available_questions = Question.query.filter(~Question.id.in_(current_question_ids)).all()
        else:
            available_questions = Question.query.all()
        
        # Group questions by category
        categorized_questions = {}
        for question in available_questions:
            if question.category not in categorized_questions:
                categorized_questions[question.category] = []
            categorized_questions[question.category].append(question)
        
        return render_template(
            'instructor/add_questions_to_group.html',
            group=group,
            categorized_questions=categorized_questions,
            active_page='question_groups'
        )
    
    @staticmethod
    @question_group_bp.route('/<int:group_id>/remove_question/<int:question_id>', methods=['POST'])
    @login_required
    def remove_question_from_group(group_id, question_id):
        group = QuestionGroup.query.get_or_404(group_id)
        question = Question.query.get_or_404(question_id)
        
        if question in group.questions:
            group.questions.remove(question)
            
            try:
                db.session.commit()
                flash('Question removed from group successfully', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error removing question from group: {str(e)}', 'error')
                
        return redirect(url_for('question_group.view_group', group_id=group.id))
    
    @staticmethod
    def delete_group(group_id):
        """Delete a Quiz and count deleted questions"""
        group = QuestionGroup.query.get(group_id)
        if not group:
            return False, 0
            
        # Count questions in this group before deleting
        deletedQuestions = len(group.questions) if hasattr(group, 'questions') else 0
        
        try:
            db.session.delete(group)
            db.session.commit()
            return True, deletedQuestions
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting group: {str(e)}")
            return False, 0
    
    @staticmethod
    @question_group_bp.route('/api/<int:group_id>')
    @login_required 
    def view_group_api(group_id):
        """API endpoint to get group questions as JSON"""
        try:
            group = QuestionGroup.query.get_or_404(group_id)
            
            questions_data = []
            for question in group.questions:
                # Extract question type from explanation field
                question_type = 'Multiple Choice'  # Default
                if question.explanation and '[TYPE:' in question.explanation:
                    type_start = question.explanation.find('[TYPE:') + 6
                    type_end = question.explanation.find(']', type_start)
                    if type_end > type_start:
                        question_type = question.explanation[type_start:type_end].replace('_', ' ').title()
                        
                questions_data.append({
                    'id': question.id,
                    'numb': question.numb,
                    'question': question.question,
                    'category': question.category,
                    'type': question_type,
                    'answer': question.answer,
                    'options': question.options
                })
            
            return jsonify({
                'success': True,
                'questions': questions_data,
                'group': {
                    'id': group.id,
                    'name': group.name,
                    'description': group.description
                }
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error loading group: {str(e)}'
            }), 500

    @staticmethod
    @question_group_bp.route('/add-questions', methods=['POST'])
    @login_required
    def add_questions_to_group_ajax():
        """
        AJAX endpoint to add questions to a group
        Expects: group_id and question_ids[] in form data
        """
        try:
            group_id = request.form.get('group_id')
            question_ids = request.form.getlist('question_ids[]')
            
            if not group_id:
                return jsonify({
                    'success': False,
                    'message': 'Group ID is required'
                }), 400
            
            if not question_ids:
                return jsonify({
                    'success': False,
                    'message': 'No questions selected'
                }), 400
            
            # Get the group
            group = QuestionGroup.query.get_or_404(group_id)
            
            # Get the questions
            selected_questions = Question.query.filter(Question.id.in_(question_ids)).all()
            
            if not selected_questions:
                return jsonify({
                    'success': False,
                    'message': 'No valid questions found'
                }), 400
            
            # Add questions to group (avoid duplicates)
            added_count = 0
            for question in selected_questions:
                if question not in group.questions:
                    group.questions.append(question)
                    added_count += 1
            
            # Commit the changes
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Successfully added {added_count} question(s) to group "{group.name}"',
                'added_count': added_count,
                'group': {
                    'id': group.id,
                    'name': group.name,
                    'total_questions': len(group.questions)
                }
            })
            
        except Exception as e:
            db.session.rollback()
            print(f"Error adding questions to group: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error adding questions to group: {str(e)}'
            }), 500
