"""
Auto-generated routes for Class: Networking 1 (ID: 7)
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from user.models.user import User
from admin.models.class_model import Class
from admin.models.question_group import QuestionGroup
from utils.auth_utils import flexible_login_required, get_current_user_context

# Create blueprint for this class
class_7_bp = Blueprint('class_7', __name__, url_prefix='/class/7')

@class_7_bp.route('/')
@flexible_login_required
def class_home():
    """Main class page"""
    user_context = get_current_user_context()
    user_id = user_context['user_id'] if user_context['is_authenticated'] else None
    
    if not user_id:
        return redirect(url_for('user.index', message='You need to log in first!'))
    
    user = User.query.get(user_id)
    class_obj = Class.query.get(7)
    
    if not class_obj:
        flash('Class not found', 'error')
        return redirect(url_for('user.index'))
    
    # Get question groups for assessments
    question_groups = class_obj.question_groups.all() if class_obj else []
    question_groups_data = []
    for qg in question_groups:
        question_groups_data.append({
            'id': qg.id,
            'name': qg.name,
            'description': qg.description,
            'question_count': len(qg.questions) if qg.questions else 0
        })
    
    # Temporary fix: Add hardcoded question group if none exist in database
    if len(question_groups_data) == 0:
        question_groups_data = [
            {
                'id': 1,
                'name': 'Networking 1 Assessment',
                'description': 'Basic networking concepts and fundamentals',
                'question_count': 5
            }
        ]
    
    # Class data
    class_data = {
        'id': 7,
        'name': 'Networking 1',
        'description': 'Computer Network Fundamentals',
        'code': class_obj.code if class_obj else 'NET101',
        'section': 'Computer Network Fundamentals'
    }
    
    # Static simulations
    static_simulations = [
        {
            'title': 'Network Components Lab',
            'description': 'Explore network hardware components',
            'url': '/user/networking1/components-simulation',
            'icon': 'fas fa-puzzle-piece'
        },
        {
            'title': 'OSI Model Explorer',
            'description': 'Interactive OSI model learning',
            'url': '/user/networking1/osi-simulation',
            'icon': 'fas fa-layer-group'
        }
    ]
    
    return render_template('user/user_class_standardized.html',
                         user_context=user_context,
                         user=user,
                         class_data=class_data,
                         static_simulations=static_simulations,
                         static_modules=[],
                         question_groups=question_groups_data,
                         class_progress={'completion': 35, 'modules': 6, 'hours': 18, 'score': 92},
                         simulations=[], learning_paths=[], modules=[], lessons=[],
                         recent_activities=[], achievements=[], overall_progress=25)

@class_7_bp.route('/assessment/<int:assessment_id>')
@flexible_login_required
def assessment_detail(assessment_id):
    """Assessment page for quiz/question group"""
    try:
        user_context = get_current_user_context()
        user_id = user_context['user_id'] if user_context['is_authenticated'] else None
        
        # Handle hardcoded assessment ID 1 for Networking 1
        if assessment_id == 1:
            # Create hardcoded sample questions for Networking 1
            sample_questions = [
                {
                    'id': 1,
                    'question': 'What does OSI stand for in networking?',
                    'options': ['Open Systems Integration', 'Open Systems Interconnection', 'Operating Systems Interface', 'Online Systems Integration'],
                    'correct': 1,
                    'type': 'multiple_choice',
                    'difficulty': 'easy',
                    'category': 'osi_model'
                },
                {
                    'id': 2,
                    'question': 'Which layer of the OSI model is responsible for routing packets between different networks?',
                    'options': ['Physical Layer', 'Data Link Layer', 'Network Layer', 'Transport Layer'],
                    'correct': 2,
                    'type': 'multiple_choice',
                    'difficulty': 'medium',
                    'category': 'osi_model'
                },
                {
                    'id': 3,
                    'question': 'What is the default subnet mask for a Class C network?',
                    'options': ['255.0.0.0', '255.255.0.0', '255.255.255.0', '255.255.255.255'],
                    'correct': 2,
                    'type': 'multiple_choice',
                    'difficulty': 'medium',
                    'category': 'subnetting'
                },
                {
                    'id': 4,
                    'question': 'Which device operates at the Data Link layer of the OSI model?',
                    'options': ['Router', 'Switch', 'Hub', 'Repeater'],
                    'correct': 1,
                    'type': 'multiple_choice',
                    'difficulty': 'medium',
                    'category': 'network_devices'
                },
                {
                    'id': 5,
                    'question': 'What is the purpose of a subnet mask?',
                    'options': ['To hide network traffic', 'To divide IP addresses into network and host portions', 'To encrypt network data', 'To filter network packets'],
                    'correct': 1,
                    'type': 'multiple_choice',
                    'difficulty': 'medium',
                    'category': 'subnetting'
                }
            ]
            
            assessment_data = {
                'id': 1,
                'name': 'Networking 1 Assessment',
                'description': 'Test your knowledge of basic networking concepts and fundamentals',
                'questions': sample_questions,
                'total_questions': len(sample_questions),
                'estimated_time': len(sample_questions) * 2
            }
            
        else:
            # Try to get from database for other assessment IDs
            qg = QuestionGroup.query.get_or_404(assessment_id)
            
            questions = []
            for q in qg.questions:
                question_data = {
                    'id': q.id,
                    'question': q.question,
                    'options': q.options if hasattr(q, 'options') and q.options else [],
                    'type': getattr(q, 'type', 'multiple_choice'),
                    'difficulty': getattr(q, 'difficulty', 'medium'),
                    'category': q.category
                }
                questions.append(question_data)
            
            assessment_data = {
                'id': qg.id,
                'name': qg.name,
                'description': qg.description,
                'questions': questions,
                'total_questions': len(questions),
                'estimated_time': len(questions) * 2
            }
        
        user_data = {}
        if user_id:
            user = User.query.get(user_id)
            if user:
                user_data = {
                    'id': user.id,
                    'username': user.username,
                    'first_name': getattr(user, 'first_name', ''),
                    'last_name': getattr(user, 'last_name', ''),
                    'profile_picture': getattr(user, 'profile_picture', None)
                }

        # Ensure user_context is properly formatted
        safe_user_context = {}
        if user_context and hasattr(user_context, 'get'):
            safe_user_context = {
                'is_authenticated': user_context.get('is_authenticated', False),
                'user_id': user_context.get('user_id'),
                'username': user_context.get('username', ''),
                'role': user_context.get('role', 'user')
            }

        return render_template('user/quiz_interface.html', 
                             assessment=assessment_data,
                             class_info={'id': 7, 'name': 'Networking 1', 'code': '5BNCGY'},
                             user_data=user_data,
                             user_context=safe_user_context)
    except Exception as e:
        flash(f'Error loading assessment: {str(e)}', 'error')
        return redirect(url_for('class_7.class_home')) 
