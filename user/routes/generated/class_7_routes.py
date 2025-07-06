
"""
Auto-generated routes for Class: Networking 1 (ID: 7)
Generated on: 2025-07-07 00:56:55
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from user.models.user import User
from admin.models.class_model import Class
from admin.models.question_group import QuestionGroup
from utils.auth_utils import flexible_login_required, get_current_user_context

# Create blueprint for this class
class_7_bp = Blueprint(
    'class_7', 
    __name__, 
    url_prefix='/class/7'
)

@class_7_bp.route('/')
@flexible_login_required
def class_home():
    """Main class page"""
    user_context = get_current_user_context()
    user_id = user_context['user_id'] if user_context['is_authenticated'] else None
    
    if not user_id:
        return redirect(url_for('user.index', message='You need to log in first!'))
    
    # Get user model for template compatibility
    from user.models.user import User
    user = User.query.get(user_id)
    
    # Import NetworkingProgress model for progress tracking
    try:
        from user.models.networking_progress import NetworkingProgress
        # Get user's progress for all networking lessons
        progress = NetworkingProgress.query.filter_by(user_id=user_id).all()
        
        # Format progress data for the template
        progress_data = {}
        for item in progress:
            if item.module_id not in progress_data:
                progress_data[item.module_id] = {
                    "lessons": {},
                    "completed_count": 0,
                    "total_lessons": 0
                }
            
            progress_data[item.module_id]["lessons"][item.lesson_id] = {
                "completed": item.completed,
                "progress": item.progress_percent
            }
            
            # Update module completion stats
            progress_data[item.module_id]["total_lessons"] += 1
            if item.completed:
                progress_data[item.module_id]["completed_count"] += 1
        
        # Calculate overall module progress percentages
        for module_id, module_data in progress_data.items():
            if module_data["total_lessons"] > 0:
                module_data["progress_percent"] = int((module_data["completed_count"] / module_data["total_lessons"]) * 100)
            else:
                module_data["progress_percent"] = 0
                
    except ImportError:
        # If progress model doesn't exist, use empty progress
        progress_data = {}
    
    return render_template(
        'user/learning_networking1.html',
        user=user,
        progress_data=progress_data
    )

@class_7_bp.route('/module/<int:module_id>')
@flexible_login_required
def module_detail(module_id):
    """Module detail page"""
    # Implementation for module detail
    pass

@class_7_bp.route('/lesson/<int:lesson_id>')
@flexible_login_required
def lesson_detail(lesson_id):
    """Lesson detail page"""
    # Implementation for lesson detail
    pass

@class_7_bp.route('/simulation/<simulation_id>')
@flexible_login_required
def simulation_detail(simulation_id):
    """Simulation page"""
    # Implementation for simulation
    pass

@class_7_bp.route('/assessment/<int:assessment_id>')
@flexible_login_required
def assessment_detail(assessment_id):
    """Assessment page"""
    # Implementation for assessment
    pass

@class_7_bp.route('/api/lesson/<int:lesson_id>')
@flexible_login_required
def api_get_lesson(lesson_id):
    """API endpoint to get lesson content"""
    # Get lesson content from question group
    qg = QuestionGroup.query.get_or_404(lesson_id)
    
    return jsonify({
        'id': qg.id,
        'name': qg.name,
        'description': qg.description,
        'content': format_lesson_content(qg),
        'questions': format_questions(qg.questions) if hasattr(qg, 'questions') else []
    })

@class_7_bp.route('/api/progress')
@flexible_login_required
def api_get_progress():
    """API endpoint to get user progress"""
    user_context = get_current_user_context()
    user_id = user_context['user_id']
    progress = get_user_progress(user_id, 7)
    
    return jsonify(progress)

@class_7_bp.route('/api/submit-answer', methods=['POST'])
@flexible_login_required
def api_submit_answer():
    """API endpoint to submit question answer"""
    data = request.json
    user_context = get_current_user_context()
    user_id = user_context['user_id']
    
    # Process answer submission
    result = process_answer_submission(user_id, data)
    
    return jsonify(result)

# Helper functions
def get_class_modules(class_id):
    """Get modules for the class"""
    class_obj = Class.query.get(class_id)
    modules = []
    
    for qg in class_obj.question_groups:
        modules.append({
            'id': qg.id,
            'name': qg.name,
            'description': qg.description,
            'category': qg.category,
            'lessons': get_lessons_for_group(qg)
        })
    
    return modules

def get_class_simulations(class_id):
    """Get simulations for the class"""
    # Implementation based on class type
    class_obj = Class.query.get(class_id)
    
    if 'networking' in class_obj.name.lower():
        return get_networking_simulations()
    elif 'security' in class_obj.name.lower():
        return get_security_simulations()
    else:
        return get_default_simulations()

def get_class_question_groups(class_id):
    """Get question groups for the class"""
    class_obj = Class.query.get(class_id)
    return [qg for qg in class_obj.question_groups]

def get_user_progress(user_id, class_id):
    """Get user progress for the class"""
    # Implementation for tracking user progress
    return {
        'modules_completed': 0,
        'simulations_completed': 0,
        'assessments_completed': 0,
        'overall_progress': 0
    }

def format_lesson_content(question_group):
    """Format question group into lesson content"""
    return {
        'title': question_group.name,
        'description': question_group.description,
        'type': 'questions',
        'content': question_group.description or "Interactive lesson content"
    }

def format_questions(questions):
    """Format questions for API response"""
    formatted = []
    for q in questions:
        formatted.append({
            'id': q.id,
            'question': q.question,
            'type': getattr(q, 'type', 'multiple_choice'),
            'options': getattr(q, 'options', []),
            'difficulty': getattr(q, 'difficulty', 'medium')
        })
    return formatted

def get_lessons_for_group(question_group):
    """Get lessons for a question group"""
    return [{
        'id': question_group.id,
        'name': question_group.name,
        'description': question_group.description,
        'type': 'questions',
        'estimated_time': len(getattr(question_group, 'questions', [])) * 2
    }]

def get_networking_simulations():
    """Get networking-specific simulations"""
    return [
        {
            'id': 'network_topology',
            'name': 'Network Topology Builder',
            'description': 'Build and configure network topologies',
            'icon': 'fas fa-network-wired'
        },
        {
            'id': 'routing_config',
            'name': 'Routing Configuration',
            'description': 'Configure static and dynamic routing',
            'icon': 'fas fa-route'
        }
    ]

def get_security_simulations():
    """Get security-specific simulations"""
    return [
        {
            'id': 'firewall_config',
            'name': 'Firewall Configuration',
            'description': 'Configure firewall rules and policies',
            'icon': 'fas fa-shield-alt'
        },
        {
            'id': 'intrusion_detection',
            'name': 'Intrusion Detection',
            'description': 'Set up and monitor IDS systems',
            'icon': 'fas fa-eye'
        }
    ]

def get_default_simulations():
    """Get default simulations"""
    return [
        {
            'id': 'general_lab',
            'name': 'Interactive Lab',
            'description': 'General purpose laboratory environment',
            'icon': 'fas fa-flask'
        }
    ]

def process_answer_submission(user_id, data):
    """Process answer submission and update progress"""
    # Implementation for processing answers
    return {
        'success': True,
        'score': 0,
        'feedback': 'Answer submitted successfully'
    }


# Simulation proxy routes for networking1

@class_7_bp.route('/simulation/components')
@flexible_login_required
def simulation_components():
    """Proxy to Network Components Builder simulation"""
    return redirect('/user/networking1/components-simulation')

@class_7_bp.route('/simulation/osi')
@flexible_login_required
def simulation_osi():
    """Proxy to OSI Model Explorer simulation"""
    return redirect('/user/networking1/osi-simulation')

@class_7_bp.route('/simulation/tcpip')
@flexible_login_required
def simulation_tcpip():
    """Proxy to TCP/IP Protocol Stack simulation"""
    return redirect('/user/networking1/tcpip-simulation')

@class_7_bp.route('/simulation/ethernet')
@flexible_login_required
def simulation_ethernet():
    """Proxy to Ethernet Frame Builder simulation"""
    return redirect('/user/networking1/ethernet-simulation')

@class_7_bp.route('/simulation/application')
@flexible_login_required
def simulation_application():
    """Proxy to Application Layer Protocols simulation"""
    return redirect('/user/networking1/application-simulation')
