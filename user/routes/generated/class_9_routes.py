"""
Auto-generated routes for Class: Networking 2 (ID: 9)
Generated on: 2025-07-06 19:10:24
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from user.models.user import User
from admin.models.class_model import Class
from admin.models.question_group import QuestionGroup
from utils.auth_utils import flexible_login_required, get_current_user_context

# Create blueprint for this class
class_9_bp = Blueprint(
    'class_9', 
    __name__, 
    url_prefix='/class/9'
)

# Main class route
@class_9_bp.route('/')
@flexible_login_required
def class_home():
    """Main class page"""
    user_context = get_current_user_context()
    user_id = user_context['user_id'] if user_context['is_authenticated'] else None
    
    if not user_id:
        return redirect(url_for('user.index', message='You need to log in first!'))
    
    # Get user model for template compatibility
    user = User.query.get(user_id)
    
    # Get class data
    class_obj = Class.query.get_or_404(9)  # Networking 2 class
    
    # Get question groups for assessments using the many-to-many relationship
    question_groups = class_obj.question_groups.all() if class_obj else []
    question_groups_data = []
    for qg in question_groups:
        question_groups_data.append({
            'id': qg.id,
            'name': qg.name,
            'description': qg.description,
            'question_count': len(qg.questions) if qg.questions else 0
        })
    
    # Prepare class data for the standardized template
    class_data = {
        'id': 9,
        'name': 'Networking 2',
        'description': 'Advanced Network Management & Security',
        'code': class_obj.code if class_obj else 'NET202',
        'section': 'Advanced Network Management & Security'
    }
    
    # Networking 2 static simulations
    static_simulations = [
        {
            'title': 'Routing Fundamentals',
            'description': 'Basic routing concepts and static routing',
            'url': '/networking2-routing-fundamentals-simulation',
            'icon': 'fas fa-route'
        },
        {
            'title': 'Dynamic Routing Protocols',
            'description': 'Understanding RIP, OSPF, EIGRP protocols',
            'url': '/networking2-dynamic-routing-simulation',
            'icon': 'fas fa-share-alt'
        },
        {
            'title': 'VLAN Configuration',
            'description': 'Virtual LAN setup and inter-VLAN routing',
            'url': '/networking2-vlan-simulation',
            'icon': 'fas fa-network-wired'
        },
        {
            'title': 'Network Security',
            'description': 'Firewalls, ACLs, and security implementation',
            'url': '/networking2-security-simulation',
            'icon': 'fas fa-shield-alt'
        }
    ]
    
    return render_template(
        'user/user_class_standardized.html',
        user=user,
        user_context={'is_admin': False, 'is_authenticated': True},
        class_data=class_data,
        static_simulations=static_simulations,
        static_modules=[],
        class_progress={'completion': 25, 'modules': 8, 'hours': 24, 'score': 87},
        simulations=[],
        learning_paths=[],
        modules=[],
        lessons=[],
        question_groups=question_groups_data,
        recent_activities=[],
        achievements=[],
        overall_progress=25
    )

@class_9_bp.route('/assessment/<int:assessment_id>')
@flexible_login_required
def assessment_detail(assessment_id):
    """Assessment page for quiz/question group"""
    try:
        print(f"🔍 Assessment request for ID: {assessment_id}")  # Debug
        
        # Get user context first
        user_context = get_current_user_context()
        user_id = user_context['user_id'] if user_context['is_authenticated'] else None
        
        qg = QuestionGroup.query.get_or_404(assessment_id)
        print(f"✅ Found question group: {qg.name}")  # Debug
        
        # Check if question group has questions
        if not qg.questions or len(qg.questions) == 0:
            flash('This assessment has no questions available yet.', 'warning')
            return redirect(url_for('class_9.class_home'))
        
        print(f"✅ Question group has {len(qg.questions)} questions")  # Debug
        
        # Format questions for the quiz interface
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
        
        # Get user data for session - ensure no undefined values
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

        # Ensure user_context is properly formatted for JSON serialization  
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
                             class_info={
                                 'id': 9,
                                 'name': 'Networking 2',
                                 'code': 'QKA5AN'
                             },
                             user_data=user_data,
                             user_context=safe_user_context)
        
    except Exception as e:
        print(f"❌ Assessment Error: {str(e)}")  # Debug logging
        error_message = str(e)
        
        # Provide more specific error messages
        if "404" in error_message or "not found" in error_message.lower():
            flash('Assessment not found. Please try again or contact support.', 'error')
        elif "no questions" in error_message.lower():
            flash('This assessment has no questions available yet.', 'warning')  
        else:
            flash(f'Error loading assessment: {error_message}', 'error')
            
        return redirect(url_for('class_9.class_home'))