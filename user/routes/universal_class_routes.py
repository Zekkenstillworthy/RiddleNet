"""
Universal Dynamic Class Route Handler
Handles all class detail pages using a single dynamic template
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from user.models.user import User
from user.models.score import Score  # Import Score to ensure SQLAlchemy relationship works
from instructor.models.class_model import Class
from instructor.models.module import Module, Lesson, LessonProgress
from instructor.models.simulation import Simulation, SimulationAttempt
from instructor.models.question_group import QuestionGroup
from instructor.models.simulation import Simulation
from instructor.models.simulation_assignment import SimulationAssignment
from instructor.models.module import Module, Lesson
from instructor.models.class_content import ClassAnnouncement, ClassAssignment, ClassMaterial
from instructor.models.assignment_submission import AssignmentSubmission
# ClassTopic removed - content now organized under Modules
from utils.auth_utils import flexible_login_required, get_current_user_context
from __init__ import db
from sqlalchemy import and_
import json, ast

# Create blueprint for universal class handling
universal_class_bp = Blueprint('universal_class', __name__, url_prefix='/class')

@universal_class_bp.route('/<int:class_id>')
@flexible_login_required
def dynamic_class_detail(class_id):
    """
    Universal dynamic class detail page - handles ALL classes
    
    This route dynamically generates class pages using a single template:
    - Pulls all content from database (modules, simulations, assessments)
    - Supports custom styling per class (colors, CSS)
    - Instructor can create new classes without needing new templates
    - All content is database-driven and configurable
    """
    print(f"🚀 ROUTE HIT: /class/{class_id} - dynamic_class_detail called")
    try:
        # QUICK REDIRECT: For classes 6 and 7, send users directly to first module's first lesson
        if class_id in [6, 7]:
            try:
                first_module = Module.query.filter_by(class_id=class_id, is_active=True).order_by(Module.order_index.asc()).first()
                if first_module:
                    first_lesson = Lesson.query.filter_by(module_id=first_module.id, is_active=True).order_by(Lesson.order_index.asc()).first()
                    if first_lesson:
                        return redirect(url_for('universal_class.module_detail', class_id=class_id, module_id=first_module.id) + f'?lesson_id={first_lesson.id}')
            except Exception as redirect_err:
                print(f"Redirect logic for class {class_id} failed: {redirect_err}")
        
        # Get user context
        user_context = get_current_user_context()
        user_id = user_context['user_id'] if user_context['is_authenticated'] else None
        
        # Get class data from database
        class_obj = Class.query.get_or_404(class_id)
        
        # Get user model for template compatibility
        user = User.query.get(user_id) if user_id else None
        
        # Prepare class data for template
        class_data = {
            'id': class_obj.id,
            'name': class_obj.name,
            'description': class_obj.description,
            'code': class_obj.code,
            'section': class_obj.section,
            'primary_color': getattr(class_obj, 'primary_color', '#3B82F6'),
            'secondary_color': getattr(class_obj, 'secondary_color', '#8B5CF6'),
            'accent_color': getattr(class_obj, 'accent_color', '#10B981'),
            'background_color': getattr(class_obj, 'background_color', 'transparent'),
            'background_image': getattr(class_obj, 'background_image', None),
            'custom_css': getattr(class_obj, 'custom_css', '')
        }
        
        # Get class modules from database (using Module model)
        class_modules = []
        modules = Module.query.filter_by(class_id=class_id, is_active=True).order_by(Module.order_index).all()
        # Normalizer to ensure objective/concept fields become lists
        def _normalize_list_field(raw_value):
            try:
                if not raw_value:
                    return []
                if isinstance(raw_value, list):
                    return raw_value
                if isinstance(raw_value, (set, tuple)):
                    return list(raw_value)
                if isinstance(raw_value, str):
                    s = raw_value.strip()
                    # Try JSON / literal list
                    if (s.startswith('[') and s.endswith(']')):
                        try:
                            parsed = json.loads(s)
                            if isinstance(parsed, list):
                                return parsed
                        except Exception:
                            try:
                                parsed = ast.literal_eval(s)
                                if isinstance(parsed, list):
                                    return parsed
                            except Exception:
                                pass
                    # Fallback split on newlines first then commas
                    delimiter = '\n' if '\n' in s else ','
                    parts = [p.strip().strip('"').strip("'") for p in s.split(delimiter) if p.strip()]
                    # Remove stray brackets
                    cleaned = [p.lstrip('[').rstrip(']') for p in parts if p not in ['[',']']]
                    return [c for c in cleaned if c]
                return [str(raw_value)]
            except Exception as norm_err:
                print(f"_normalize_list_field (class view) error: {norm_err}")
                return []

        for module in modules:
            # Get module lessons
            lessons = Lesson.query.filter_by(module_id=module.id, is_active=True).order_by(Lesson.order_index).all()
            
            # Safely get module progress with error handling
            try:
                module_progress = module.get_user_progress(user_id) if user_id else None
                completion_percentage = module_progress['progress_percentage'] if module_progress else 0
            except Exception as e:
                print(f"Error getting module progress for module {module.id}: {e}")
                completion_percentage = 0
            
            # Safely get lesson data with error handling
            lesson_data = []
            for lesson in lessons:
                try:
                    lesson_data.append({
                        'id': lesson.id,
                        'title': lesson.title,
                        'description': lesson.description,
                        'lesson_number': lesson.lesson_number,
                        'content': lesson.content,
                        'learning_objectives': _normalize_list_field(getattr(lesson, 'learning_objectives', None)),
                        'key_concepts': _normalize_list_field(getattr(lesson, 'key_concepts', None)),
                        'estimated_duration': lesson.estimated_duration,
                        'is_active': lesson.is_active,
                        'simulation_ids': lesson.simulation_ids or [],
                        'simulation_count': lesson.simulation_count,
                        'order_index': lesson.order_index
                    })
                except Exception as e:
                    print(f"Error getting lesson data for lesson {lesson.id}: {e}")
                    lesson_data.append({
                        'id': lesson.id,
                        'title': lesson.title,
                        'description': lesson.description or '',
                        'lesson_number': getattr(lesson, 'lesson_number', ''),
                        'estimated_duration': getattr(lesson, 'estimated_duration', 30),
                        'learning_objectives': [],
                        'key_concepts': []
                    })
            
            class_modules.append({
                'id': module.id,
                'title': module.title,
                'name': module.title,  # For compatibility
                'description': module.description,
                'module_number': module.module_number,
                'course_type': module.course_type,
                'learning_objectives': module.learning_objectives or [],
                'estimated_duration': module.estimated_duration,
                'type': 'module',
                'lessons': lesson_data,
                'total_lessons': len(lessons),
                'completion_percentage': completion_percentage,
                'is_unlocked': True  # Default to unlocked to avoid database issues
            })
        
        # If no modules exist, create a default module structure
        if not class_modules:
            # Create a placeholder module to hold unorganized content
            class_modules.append({
                'id': 0,
                'title': 'General Content',
                'name': 'General Content',  # For compatibility
                'description': 'Content not yet organized into modules',
                'type': 'general',
                'completion_percentage': 0  # TODO: Calculate from user progress
            })
        
        # Get class simulations from database
        class_simulations = []
        simulation_assignments = SimulationAssignment.query.filter_by(class_id=class_id).all()
        for assignment in simulation_assignments:
            if assignment.simulation:
                class_simulations.append({
                    'id': assignment.simulation.id,
                    'title': assignment.simulation.title,
                    'name': assignment.simulation.title,  # For compatibility
                    'description': assignment.simulation.description,
                    'icon': getattr(assignment.simulation, 'icon', 'fas fa-play'),
                    'type': 'simulation'
                })
        
                # Note: Simulations don't have class_id directly - they're linked through SimulationAssignment
        # The simulation_assignments query above already gets all assigned simulations
        
        # Get Quiz (assessments) for this class
        question_groups = class_obj.question_groups.all() if class_obj else []
        question_groups_data = []
        for qg in question_groups:
            questions = []
            if hasattr(qg, 'questions') and qg.questions:
                for q in qg.questions:
                    questions.append({
                        'id': q.id,
                        'question': q.question,
                        'type': getattr(q, 'type', 'multiple_choice'),
                        'options': getattr(q, 'options', []),
                        'difficulty': getattr(q, 'difficulty', 'medium')
                    })
            
            question_groups_data.append({
                'id': qg.id,
                'name': qg.name,
                'description': qg.description,
                'category': getattr(qg, 'category', 'General'),  # Default to 'General' if no category field
                'questions': questions
            })
        
        # Calculate class progress (mock data for now)
        class_progress = {
            'completion': 0,  # TODO: Calculate from user progress
            'modules': len([m for m in class_modules]),
            'hours': 0,  # TODO: Calculate from time tracking
            'score': 0   # TODO: Calculate from assessment scores
        }
        
        # Get class assignments
        class_assignments = []
        assignments = ClassAssignment.query.filter_by(class_id=class_id, is_published=True).order_by(ClassAssignment.due_date).all()
        now = datetime.now()
        
        # DEBUG: Print assignment info
        print(f"[DEBUG] DEBUG: Class {class_id} assignments query:")
        print(f"   - Found {len(assignments)} published assignments")
        print(f"   - User ID: {user_id}")
        print(f"   - User authenticated: {user_context['is_authenticated']}")
        
        for assignment in assignments:
            print(f"   - Assignment: {assignment.title} (ID: {assignment.id})")
            
            # Get submission status for this user
            submission = None
            status = 'not_submitted'
            
            if user_id:
                submission = AssignmentSubmission.query.filter_by(
                    assignment_id=assignment.id,
                    student_id=user_id
                ).first()
                
                if submission:
                    if submission.grade is not None:
                        status = 'graded'
                    else:
                        status = 'submitted'
                elif assignment.due_date and assignment.due_date < now:
                    status = 'overdue'
            
            class_assignments.append({
                'assignment': assignment,
                'submission': submission,
                'status': status
            })
        
        print(f"   - Final class_assignments count: {len(class_assignments)}")
        
        # Calculate actual progress if user is authenticated
        if user_id:
            # TODO: Implement progress calculation from database
            # This would involve checking user's completion status for modules,
            # simulation attempts, and assessment scores
            pass
        
        return render_template('user/dynamic_class_universal.html',
                             user_context=user_context,
                             user=user,
                             class_data=class_data,
                             class_modules=class_modules,
                             class_simulations=class_simulations,
                             question_groups=question_groups_data,
                             class_progress=class_progress,
                             class_assignments=class_assignments,
                             now=datetime.now())
                             
    except Exception as e:
        print(f"Error in dynamic_class_detail: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return a basic error template or redirect
        return render_template('user/dynamic_class_universal.html',
                             user_context=get_current_user_context(),
                             class_data={'name': 'Class Not Found', 'id': class_id},
                             class_modules=[],
                             class_simulations=[],
                             question_groups=[],
                             class_progress={'completion': 0, 'modules': 0, 'hours': 0, 'score': 0})

@universal_class_bp.route('/<int:class_id>/simulation/<int:simulation_id>')
@flexible_login_required
def simulation_detail(class_id, simulation_id):
    """Handle simulation pages"""
    # Redirect to simulation runner
    return redirect(url_for('user.simulation_runner', simulation_id=simulation_id))

@universal_class_bp.route('/<int:class_id>/assessment/<int:assessment_id>')
@flexible_login_required
def assessment_detail(class_id, assessment_id):
    """Handle assessment pages"""
    # For now, redirect to main class page with assessments tab
    return redirect(url_for('universal_class.dynamic_class_detail', class_id=class_id) + '#assessments-tab')

# API endpoints for dynamic content
@universal_class_bp.route('/<int:class_id>/api/progress')
@flexible_login_required
def api_get_progress(class_id):
    """Get user progress for the class"""
    user_context = get_current_user_context()
    user_id = user_context['user_id'] if user_context['is_authenticated'] else None
    
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # TODO: Implement progress calculation from database
    progress = {
        'modules_completed': 0,
        'simulations_completed': 0,
        'assessments_completed': 0,
        'overall_progress': 0,
        'time_spent': 0,
        'average_score': 0
    }
    
    return jsonify(progress)

@universal_class_bp.route('/<int:class_id>/api/content')
@flexible_login_required
def api_get_content(class_id):
    """Get all content for the class"""
    try:
        class_obj = Class.query.get_or_404(class_id)
        
        # Get modules (replacing topics)
        modules_query = Module.query.filter_by(class_id=class_id, is_active=True).order_by(Module.order_index).all()
        modules = [{'id': m.id, 'name': m.title, 'description': m.description} for m in modules_query]
        
        # Get simulations
        simulation_assignments = SimulationAssignment.query.filter_by(class_id=class_id).all()
        simulations = []
        for assignment in simulation_assignments:
            if assignment.simulation:
                simulations.append({
                    'id': assignment.simulation.id,
                    'title': assignment.simulation.title,
                    'description': assignment.simulation.description
                })
        
        # Get assessments
        question_groups = class_obj.question_groups.all()
        assessments = [{'id': qg.id, 'name': qg.name, 'description': qg.description} for qg in question_groups]
        
        return jsonify({
            'modules': modules,
            'simulations': simulations,
            'assessments': assessments
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@universal_class_bp.route('/<int:class_id>/module/<int:module_id>')
@flexible_login_required
def module_detail(class_id, module_id):
    """Student view of a specific module"""
    try:
        # Get user context
        user_context = get_current_user_context()
        user_id = user_context['user_id'] if user_context['is_authenticated'] else None
        
        if not user_id:
            return redirect(url_for('user.index', message='You need to log in first!'))
        
        # Get user model
        user = User.query.get(user_id)
        
        # Get the module and class
        module = Module.query.filter_by(id=module_id, class_id=class_id, is_active=True).first()
        if not module:
            return redirect(url_for('universal_class.dynamic_class_detail', class_id=class_id))
        
        class_obj = Class.query.get_or_404(class_id)
        
        # Get ALL class modules for sidebar navigation
        all_class_modules = Module.query.filter_by(class_id=class_id, is_active=True).order_by(Module.order_index).all()
        class_modules_data = []
        for mod in all_class_modules:
            try:
                # Safely get module progress
                module_progress = mod.get_user_progress(user_id) if user_id else None
                completion_percentage = module_progress['progress_percentage'] if module_progress else 0
            except Exception as e:
                print(f"Error getting module progress for module {mod.id}: {e}")
                completion_percentage = 0
            
            # Get lessons for this module
            module_lessons = Lesson.query.filter_by(module_id=mod.id, is_active=True).order_by(Lesson.order_index).all()
            lessons_data = []
            for lesson in module_lessons:
                lessons_data.append({
                    'id': lesson.id,
                    'title': lesson.title,
                    'lesson_number': lesson.lesson_number,
                    'order_index': lesson.order_index,
                    'estimated_duration': lesson.estimated_duration or 30
                })
            
            class_modules_data.append({
                'id': mod.id,
                'title': mod.title,
                'module_number': mod.module_number,
                'estimated_duration': mod.estimated_duration,
                'total_lessons': mod.total_lessons,
                'completion_percentage': completion_percentage,
                'lessons': lessons_data  # Add actual lesson data
            })
        
        # Get module lessons
        lessons = Lesson.query.filter_by(module_id=module_id, is_active=True).order_by(Lesson.order_index).all()
        
        # Get simulations related to this module
        module_simulations = []
        module_simulation_assignments = []  # Cache assignments for later lesson-level usage
        seen_simulation_ids = set()  # Track unique simulation IDs to prevent duplicates
        try:
            # Get simulations assigned directly to this module
            # First, get assignments with module_id matching this module
            module_simulation_assignments = SimulationAssignment.query.filter_by(
                module_id=module_id,
                class_id=class_id,
                is_active=True,
                is_published=True
            ).all()
            
            print(f"[DEBUG] Found {len(module_simulation_assignments)} assignments for module {module_id}")
            
            for assignment in module_simulation_assignments:
                # Ensure assignment is actually available now and simulation is usable
                if not assignment.is_available:
                    print(f"[DEBUG] Skipping assignment {assignment.id} - not available")
                    continue
                    
                if assignment.simulation and getattr(assignment.simulation, 'is_active', True) and assignment.simulation.is_published:
                    # Skip if we've already added this simulation
                    if assignment.simulation.id in seen_simulation_ids:
                        print(f"[DEBUG] Skipping simulation {assignment.simulation.id} - already added")
                        continue
                    
                    # Add to seen set and append to list
                    seen_simulation_ids.add(assignment.simulation.id)
                    print(f"[DEBUG] Adding simulation: {assignment.simulation.title} (ID: {assignment.simulation.id})")
                    module_simulations.append({
                        'id': assignment.simulation.id,
                        'title': assignment.simulation.title,
                        'description': assignment.simulation.description,
                        'difficulty': assignment.simulation.difficulty,
                        'estimated_duration': assignment.simulation.estimated_duration
                    })
                        
            print(f"Found {len(module_simulations)} unique simulations for module {module_id}")
        except Exception as e:
            print(f"Error getting module simulations: {e}")
            import traceback
            traceback.print_exc()
            module_simulations = []
        
        # Get assignments for this class/module
        assignments = ClassAssignment.query.filter_by(
            class_id=class_id, 
            is_published=True
        ).order_by(ClassAssignment.due_date.asc()).all()
        
        # Get user's submissions for these assignments
        assignment_submissions = {}
        if user_id:
            from instructor.models.assignment_submission import AssignmentSubmission
            submissions = AssignmentSubmission.query.filter_by(student_id=user_id).all()
            assignment_submissions = {sub.assignment_id: sub for sub in submissions}
        
        # Prepare assignment data with submission status
        assignment_data = []
        for assignment in assignments:
            submission = assignment_submissions.get(assignment.id)
            status = 'not_submitted'
            if submission:
                if submission.status == 'graded':
                    status = 'graded'
                elif submission.status == 'resubmitted':
                    status = 'resubmitted'
                else:
                    status = 'submitted'
            elif assignment.due_date and assignment.due_date < datetime.utcnow():
                status = 'overdue'
            
            # Convert assignment to dictionary for JSON serialization
            assignment_dict = {
                'id': assignment.id,
                'title': assignment.title,
                'description': assignment.description,
                'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
                'points': assignment.points,
                'assignment_type': assignment.assignment_type,
                'is_published': assignment.is_published,
                'created_at': assignment.created_at.isoformat() if assignment.created_at else None
            }
            
            submission_dict = None
            if submission:
                submission_dict = {
                    'id': submission.id,
                    'status': submission.status,
                    'submitted_at': submission.submitted_at.isoformat() if submission.submitted_at else None,
                    'grade': submission.grade,
                    'feedback': submission.feedback
                }
            
            assignment_data.append({
                'assignment': assignment_dict,
                'submission': submission_dict,
                'status': status
            })
        
        # Get module materials (if any)
        module_materials = []
        try:
            module_materials = ClassMaterial.query.filter_by(class_id=class_id).all()
            # Filter materials that might be associated with this module
            module_materials = [mat for mat in module_materials if str(module_id) in (mat.content or '')]
        except:
            module_materials = []
        
        # Calculate module progress (for now, show as 0%)
        module_progress = {
            'completed_lessons': 0,
            'total_lessons': len(lessons),
            'percentage': 0
        }
        
        # Get active lesson for embedded lesson content
        active_lesson = None
        active_lesson_progress = None
        previous_lesson = None
        next_lesson = None
        simulation_progress = {}
        lesson_simulations = []
        
        if lessons:
            # Default to first lesson or use query param
            lesson_id_param = request.args.get('lesson_id', type=int)
            if lesson_id_param:
                active_lesson = next((l for l in lessons if l.id == lesson_id_param), lessons[0])
            else:
                active_lesson = lessons[0]
            
            if active_lesson:
                # Get or create lesson progress
                active_lesson_progress = LessonProgress.query.filter_by(
                    user_id=user_id,
                    lesson_id=active_lesson.id
                ).first()
                
                if not active_lesson_progress:
                    active_lesson_progress = LessonProgress(
                        user_id=user_id,
                        lesson_id=active_lesson.id,
                        started_at=datetime.utcnow()
                    )
                    db.session.add(active_lesson_progress)
                    db.session.commit()

                # Normalize learning_objectives & key_concepts to lists (handle strings / JSON / None)
                def _normalize_list_field(raw_value):
                    if not raw_value:
                        return []
                    if isinstance(raw_value, list):
                        return raw_value
                    if isinstance(raw_value, str):
                        import json, ast
                        s = raw_value.strip()
                        # Try to parse as JSON first (handles proper JSON arrays and strings)
                        try:
                            parsed = json.loads(s)
                            if isinstance(parsed, list):
                                return parsed
                            if isinstance(parsed, str):  # A single quoted string
                                return [parsed]
                        except Exception:
                            pass
                        
                        # Try Python literal evaluation
                        try:
                            parsed = ast.literal_eval(s)
                            if isinstance(parsed, list):
                                return parsed
                        except Exception:
                            pass
                        
                        # If not JSON/Python literal, split on commas or newlines
                        if '\n' in s:
                            return [p.strip() for p in s.split('\n') if p.strip()]
                        else:
                            return [p.strip() for p in s.split(',') if p.strip()]
                    # Any other type -> wrap
                    return [str(raw_value)]

                try:
                    raw_objectives = getattr(active_lesson, 'learning_objectives', [])
                    active_lesson.learning_objectives = _normalize_list_field(raw_objectives)
                except Exception as nerr:
                    print(f"Normalization error (learning_objectives) for lesson {active_lesson.id}: {nerr}")
                    import traceback
                    traceback.print_exc()
                    active_lesson.learning_objectives = []
                try:
                    raw_concepts = getattr(active_lesson, 'key_concepts', [])
                    active_lesson.key_concepts = _normalize_list_field(raw_concepts)
                except Exception as nerr:
                    print(f"Normalization error (key_concepts) for lesson {active_lesson.id}: {nerr}")
                    active_lesson.key_concepts = []
                
                # Get previous and next lessons
                current_index = lessons.index(active_lesson)
                if current_index > 0:
                    previous_lesson = lessons[current_index - 1]
                if current_index < len(lessons) - 1:
                    next_lesson = lessons[current_index + 1]
                
                # Get lesson-specific simulations
                seen_lesson_simulation_ids = set()

                def add_simulation_to_lesson(sim_obj):
                    """Attach a simulation to the active lesson response with progress metadata."""
                    if not sim_obj:
                        return
                    if sim_obj.id in seen_lesson_simulation_ids:
                        return
                    if not getattr(sim_obj, 'is_active', True):
                        return
                    if hasattr(sim_obj, 'is_published') and not sim_obj.is_published:
                        return

                    user_sim_progress = SimulationAttempt.query.filter_by(
                        user_id=user_id,
                        simulation_id=sim_obj.id,
                        is_completed=True
                    ).first()
                    simulation_progress[sim_obj.id] = {
                        'completed': user_sim_progress is not None,
                        'score': user_sim_progress.total_score if user_sim_progress else 0,
                        'attempts': SimulationAttempt.query.filter_by(
                            user_id=user_id,
                            simulation_id=sim_obj.id
                        ).count()
                    }

                    lesson_simulations.append({
                        'id': sim_obj.id,
                        'title': sim_obj.title,
                        'description': sim_obj.description,
                        'difficulty': getattr(sim_obj, 'difficulty', None),
                        'estimated_duration': getattr(sim_obj, 'estimated_duration', None),
                        'simulation_type': getattr(sim_obj, 'simulation_type', 'Interactive'),
                        'icon': getattr(sim_obj, 'icon', 'network-wired')
                    })
                    seen_lesson_simulation_ids.add(sim_obj.id)

                if hasattr(active_lesson, 'simulation_ids') and active_lesson.simulation_ids:
                    from instructor.models.simulation import Simulation
                    # Safely normalize simulation_ids (may be stored as list, JSON string, python repr, or comma-separated)
                    raw_ids = active_lesson.simulation_ids
                    normalized_ids = []
                    try:
                        if isinstance(raw_ids, (list, tuple, set)):
                            normalized_ids = [int(x) for x in raw_ids if str(x).isdigit()]
                        elif isinstance(raw_ids, int):
                            normalized_ids = [raw_ids]
                        elif isinstance(raw_ids, str):
                            import json, ast, re
                            s = raw_ids.strip()
                            if s:
                                parsed = None
                                # Try JSON first
                                try:
                                    parsed = json.loads(s)
                                except Exception:
                                    # Try ast.literal_eval for python-style list
                                    try:
                                        parsed = ast.literal_eval(s)
                                    except Exception:
                                        parsed = None
                                if isinstance(parsed, int):
                                    normalized_ids = [parsed]
                                elif isinstance(parsed, (list, tuple, set)):
                                    normalized_ids = [int(x) for x in parsed if str(x).isdigit()]
                                else:
                                    # Fallback: split on commas / whitespace, strip brackets
                                    s_clean = re.sub(r'[\[\]\s]+', ' ', s)
                                    candidates = [c for token in s_clean.split(' ') for c in token.split(',')]
                                    normalized_ids = [int(x) for x in candidates if x.isdigit()]
                    except Exception as parse_err:
                        print(f"[WARNING] Failed to parse simulation_ids '{raw_ids}': {parse_err}")
                        normalized_ids = []

                    # Deduplicate & preserve order
                    seen = set()
                    ordered_ids = []
                    for _id in normalized_ids:
                        if _id not in seen:
                            seen.add(_id)
                            ordered_ids.append(_id)

                    if ordered_ids:
                        lesson_simulations_objs = Simulation.query.filter(
                            Simulation.id.in_(ordered_ids),
                            Simulation.is_active == True,
                            Simulation.is_published == True
                        ).all()

                        for sim in lesson_simulations_objs:
                            add_simulation_to_lesson(sim)

                # Merge in simulations sourced from assignments when not explicitly listed on the lesson
                if module_simulation_assignments:
                    lesson_title_lower = (active_lesson.title or '').lower()
                    lesson_number_lower = (active_lesson.lesson_number or '').lower() if active_lesson.lesson_number else ''

                    for assignment in module_simulation_assignments:
                        if not assignment.is_available:
                            continue
                        sim_obj = assignment.simulation
                        if not sim_obj:
                            continue

                        matches_lesson = False
                        # Direct module linkage takes priority
                        if assignment.module_id == module_id:
                            matches_lesson = True

                        # Lesson-specific assignments (by title/number match)
                        if not matches_lesson and assignment.assignment_type == 'lesson':
                            lesson_name_lower = (assignment.lesson_name or '').lower()
                            if lesson_name_lower:
                                if lesson_title_lower and lesson_title_lower in lesson_name_lower:
                                    matches_lesson = True
                                elif lesson_number_lower and lesson_number_lower in lesson_name_lower:
                                    matches_lesson = True

                        if matches_lesson:
                            add_simulation_to_lesson(sim_obj)
        
        # Get questions assigned to this module/lesson via Quiz associations
        lesson_questions = []
        try:
            assigned_question_groups = []
            seen_question_group_ids = set()

            if module:
                try:
                    module_question_groups = module.question_groups.filter(QuestionGroup.is_active == True).all()
                except Exception:
                    module_question_groups = list(module.question_groups) if hasattr(module, 'question_groups') else []

                for qg in module_question_groups:
                    if not qg or getattr(qg, 'id', None) is None:
                        continue
                    if qg.id in seen_question_group_ids:
                        continue
                    if hasattr(qg, 'is_active') and not qg.is_active:
                        continue
                    assigned_question_groups.append(qg)
                    seen_question_group_ids.add(qg.id)

            # Include quiz-type class assignments that belong to this module
            for assignment in assignments:
                if not getattr(assignment, 'question_group_id', None):
                    continue
                if assignment.module_id and module and assignment.module_id != module.id:
                    continue
                qg = getattr(assignment, 'question_group', None)
                if not qg or getattr(qg, 'id', None) is None:
                    continue
                if qg.id in seen_question_group_ids:
                    continue
                if hasattr(qg, 'is_active') and not qg.is_active:
                    continue
                assigned_question_groups.append(qg)
                seen_question_group_ids.add(qg.id)

            for qg in assigned_question_groups:
                questions_in_group = getattr(qg, 'questions', []) or []
                for question in questions_in_group:
                    if not question:
                        continue
                    if hasattr(question, 'to_dict'):
                        question_dict = question.to_dict()
                    else:
                        options = []
                        if hasattr(question, 'options'):
                            try:
                                options = list(question.options)
                            except Exception:
                                options = []
                        question_dict = {
                            'id': getattr(question, 'id', None),
                            'question': getattr(question, 'question', ''),
                            'answer': getattr(question, 'answer', ''),
                            'options': options,
                            'explanation': getattr(question, 'explanation', None),
                            'numb': getattr(question, 'numb', None),
                            'category': getattr(question, 'category', None)
                        }

                    question_dict['question_group_id'] = qg.id
                    question_dict['question_group_name'] = getattr(qg, 'name', '')
                    lesson_questions.append(question_dict)

            lesson_questions.sort(key=lambda x: (
                (x.get('question_group_name') or '').lower(),
                x.get('numb', 0) if x.get('numb') is not None else 0,
                x.get('id', 0) if x.get('id') is not None else 0
            ))

            print(
                f"Found {len(lesson_questions)} assigned questions for module {module_id} "
                f"(lesson {active_lesson.id if active_lesson else 'n/a'})"
            )

        except Exception as e:
            print(f"Error fetching lesson questions: {e}")
            lesson_questions = []
        
        # Get active live quiz sessions for this module/lesson
        live_quiz_sessions = []
        try:
            from user.models.live_quiz import LiveQuizSession
            
            # Find active quiz sessions for this module
            active_sessions = LiveQuizSession.query.filter_by(
                class_id=class_id,
                module_id=module_id,
                status='active'
            ).all()
            
            # Also check for waiting sessions
            waiting_sessions = LiveQuizSession.query.filter_by(
                class_id=class_id,
                module_id=module_id,
                status='waiting'
            ).all()
            
            all_sessions = active_sessions + waiting_sessions
            
            for session in all_sessions:
                live_quiz_sessions.append(session.to_dict())
            
            # Enhanced logging for debugging production issues
            print(f"[LiveQuiz] Class {class_id}, Module {module_id}: Found {len(live_quiz_sessions)} sessions")
            if live_quiz_sessions:
                for session in live_quiz_sessions:
                    print(f"  ✅ Session #{session.get('id')}: {session.get('title')} ({session.get('status')}) - Code: {session.get('session_code')}")
            else:
                # Check if ANY sessions exist for this class (debugging)
                total_class_sessions = LiveQuizSession.query.filter_by(class_id=class_id).count()
                total_module_sessions = LiveQuizSession.query.filter_by(class_id=class_id, module_id=module_id).count()
                print(f"  ⚠️  No active/waiting sessions found")
                print(f"  ℹ️  Total sessions for class {class_id}: {total_class_sessions}")
                print(f"  ℹ️  Total sessions for this module: {total_module_sessions}")
                
                # Show what sessions DO exist for this module (if any)
                all_module_sessions = LiveQuizSession.query.filter_by(
                    class_id=class_id, 
                    module_id=module_id
                ).all()
                if all_module_sessions:
                    print(f"  📝 Existing sessions (all statuses):")
                    for s in all_module_sessions:
                        print(f"     - Session #{s.id}: {s.title} (status: {s.status})")
            
        except Exception as e:
            print(f"[LiveQuiz] Error fetching live quiz sessions: {e}")
            import traceback
            traceback.print_exc()
            live_quiz_sessions = []

        # Render using the module detail template with sidebar navigation
        return render_template('user/module_detail.html',
                             user=user,
                             user_context=user_context,
                             class_data=class_obj,
                             class_obj=class_obj,  # For lesson template compatibility
                             class_modules=class_modules_data,
                             module=module,
                             module_simulations=module_simulations,
                             lessons=lessons,
                             assignments=assignment_data,
                             materials=module_materials,
                             progress=module_progress,
                             # Lesson-specific data
                             lesson=active_lesson,
                             lesson_simulations=lesson_simulations,
                             lesson_progress=active_lesson_progress,
                             previous_lesson=previous_lesson,
                             next_lesson=next_lesson,
                             simulation_progress=simulation_progress,
                             # Questions data
                             lesson_questions=lesson_questions,
                             live_quiz_sessions=live_quiz_sessions,
                             is_student_view=True,
                             now=datetime.now())
    
    except Exception as e:
        print(f"Error in module_detail: {str(e)}")
        import traceback
        traceback.print_exc()
        return redirect(url_for('universal_class.dynamic_class_detail', class_id=class_id))

@universal_class_bp.route('/<int:class_id>/api/first-lesson')
@flexible_login_required
def api_get_first_lesson(class_id):
    """Get the first lesson of the first module for a class"""
    try:
        # Get the class
        class_obj = Class.query.get_or_404(class_id)
        
        # Get the first module (ordered by order_index)
        first_module = Module.query.filter_by(
            class_id=class_id, 
            is_active=True
        ).order_by(Module.order_index.asc()).first()
        
        if not first_module:
            return jsonify({'error': 'No modules found'}), 404
        
        # Get the first lesson of the first module
        first_lesson = Lesson.query.filter_by(
            module_id=first_module.id,
            is_active=True
        ).order_by(Lesson.order_index.asc()).first()
        
        if not first_lesson:
            return jsonify({'error': 'No lessons found'}), 404
        
        return jsonify({
            'class_id': class_id,
            'module_id': first_module.id,
            'lesson_id': first_lesson.id,
            'url': f'/class/{class_id}/module/{first_module.id}?lesson_id={first_lesson.id}'
        })
        
    except Exception as e:
        print(f"Error getting first lesson for class {class_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@universal_class_bp.route('/api/assignments/<int:assignment_id>')
@flexible_login_required
def api_get_assignment(assignment_id):
    """Get assignment data for dynamic loading"""
    try:
        # Get user context
        user_context = get_current_user_context()
        user_id = user_context['user_id'] if user_context['is_authenticated'] else None
        
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        # Get the assignment
        assignment = ClassAssignment.query.get_or_404(assignment_id)
        
        # Check if user is enrolled in the class
        # TODO: Add enrollment check if needed
        
        # Get user's submission if exists
        submission = AssignmentSubmission.query.filter_by(
            assignment_id=assignment_id,
            student_id=user_id
        ).first()
        
        # Determine submission status
        status = 'not_submitted'
        now = datetime.now()
        
        if submission:
            if submission.grade is not None:
                status = 'graded'
            elif submission.status == 'resubmitted':
                status = 'resubmitted'
            else:
                status = 'submitted'
        elif assignment.due_date and assignment.due_date < now:
            status = 'overdue'
        
        # Prepare assignment data
        assignment_data = {
            'id': assignment.id,
            'title': assignment.title,
            'description': assignment.description,
            'instructions': assignment.instructions,
            'due_date': assignment.due_date.strftime('%B %d, %Y at %I:%M %p') if assignment.due_date else None,
            'due_date_iso': assignment.due_date.isoformat() if assignment.due_date else None,
            'points': assignment.points,
            'assignment_type': assignment.assignment_type,
            'allow_file_uploads': assignment.allow_file_uploads,
            'allowed_file_types': assignment.allowed_file_types,
            'max_file_size_mb': assignment.max_file_size_mb,
            'max_files': assignment.max_files,
            'allow_text_submission': assignment.allow_text_submission,
            'allow_late_submissions': assignment.allow_late_submissions,
            'late_penalty_per_day': assignment.late_penalty_per_day,
            'allow_resubmission': assignment.allow_resubmission,
            'status': status,
            'submission': None
        }
        
        # Add submission data if exists
        if submission:
            # Safely include attachments if relationship is present
            try:
                attachments = [att.to_dict() for att in getattr(submission, 'attachments', [])]
            except Exception:
                attachments = []

            assignment_data['submission'] = {
                'id': submission.id,
                'submitted_at': submission.submitted_at.strftime('%B %d, %Y at %I:%M %p') if submission.submitted_at else None,
                'grade': submission.grade,
                'feedback': submission.feedback,
                'status': submission.status,
                'submission_text': getattr(submission, 'submission_text', None),
                'attachments': attachments
            }
        
        return jsonify(assignment_data)
        
    except Exception as e:
        print(f"Error getting assignment {assignment_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500
