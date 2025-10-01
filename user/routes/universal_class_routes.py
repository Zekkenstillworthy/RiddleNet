"""
Universal Dynamic Class Route Handler
Handles all class detail pages using a single dynamic template
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from user.models.user import User
from user.models.score import Score  # Import Score to ensure SQLAlchemy relationship works
from admin.models.class_model import Class
from admin.models.module import Module, Lesson, LessonProgress
from admin.models.simulation import Simulation, SimulationAttempt
from admin.models.question_group import QuestionGroup
from admin.models.question import Question, StandardQuestion
from admin.models.simulation import Simulation
from admin.models.simulation_assignment import SimulationAssignment
from admin.models.module import Module, Lesson
from admin.models.class_content import ClassAnnouncement, ClassAssignment, ClassMaterial
from admin.models.assignment_submission import AssignmentSubmission
# ClassTopic removed - content now organized under Modules
from utils.auth_utils import flexible_login_required, get_current_user_context
from admin import db
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
    - Admin can create new classes without needing new templates
    - All content is database-driven and configurable
    """
    print(f"🚀 ROUTE HIT: /class/{class_id} - dynamic_class_detail called")
    try:
        # QUICK REDIRECT: For legacy class 7, send users directly to first module's first lesson
        if class_id == 7:
            try:
                first_module = Module.query.filter_by(class_id=class_id, is_active=True, is_published=True).order_by(Module.order_index.asc()).first()
                if first_module:
                    first_lesson = Lesson.query.filter_by(module_id=first_module.id, is_active=True).order_by(Lesson.order_index.asc()).first()
                    if first_lesson:
                        return redirect(url_for('universal_class.module_detail', class_id=class_id, module_id=first_module.id) + f'?lesson_id={first_lesson.id}')
            except Exception as redirect_err:
                print(f"Redirect logic for class 7 failed: {redirect_err}")
        
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
        modules = Module.query.filter_by(class_id=class_id, is_active=True, is_published=True).order_by(Module.order_index).all()
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
        print(f"🔍 DEBUG: Class {class_id} assignments query:")
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
        all_class_modules = Module.query.filter_by(class_id=class_id, is_active=True, is_published=True).order_by(Module.order_index).all()
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
        seen_simulation_ids = set()  # Track unique simulation IDs to prevent duplicates
        try:
            # Get simulations assigned to this class that might be related to this module
            # Only consider assignments that are active and published
            simulation_assignments = SimulationAssignment.query.filter_by(
                class_id=class_id,
                is_active=True,
                is_published=True
            ).all()
            for assignment in simulation_assignments:
                # Ensure assignment is actually available now and simulation is usable
                if not assignment.is_available:
                    continue
                if assignment.simulation and getattr(assignment.simulation, 'is_active', True) and assignment.simulation.is_published:
                    # Skip if we've already added this simulation
                    if assignment.simulation.id in seen_simulation_ids:
                        continue
                        
                    # Check if simulation is related to this module (by title, category, or type)
                    module_title_lower = module.title.lower()
                    sim_title_lower = assignment.simulation.title.lower()
                    sim_description_lower = (assignment.simulation.description or '').lower()
                    
                    # Simple matching logic - you can enhance this based on your needs
                    if (str(module_id) in sim_title_lower or 
                        any(word in sim_title_lower for word in module_title_lower.split()) or
                        any(word in sim_description_lower for word in module_title_lower.split())):
                        
                        # Add to seen set and append to list
                        seen_simulation_ids.add(assignment.simulation.id)
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
            module_simulations = []
        
        # Get assignments for this class/module
        assignments = ClassAssignment.query.filter_by(
            class_id=class_id, 
            is_published=True
        ).order_by(ClassAssignment.due_date.asc()).all()
        
        # Get user's submissions for these assignments
        assignment_submissions = {}
        if user_id:
            from admin.models.assignment_submission import AssignmentSubmission
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
            
            assignment_data.append({
                'assignment': assignment,
                'submission': submission,
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
                        # If it looks like JSON list
                        if (s.startswith('[') and s.endswith(']')) or (s.startswith('"') and s.endswith('"')):
                            try:
                                parsed = json.loads(s)
                                if isinstance(parsed, list):
                                    return parsed
                                if isinstance(parsed, str):  # A single quoted string
                                    return [parsed]
                            except Exception:
                                try:
                                    parsed = ast.literal_eval(s)
                                    if isinstance(parsed, list):
                                        return parsed
                                except Exception:
                                    pass
                        # Fallback: split on commas
                        return [p.strip() for p in s.split(',') if p.strip()]
                    # Any other type -> wrap
                    return [str(raw_value)]

                try:
                    active_lesson.learning_objectives = _normalize_list_field(getattr(active_lesson, 'learning_objectives', []))
                except Exception as nerr:
                    print(f"Normalization error (learning_objectives) for lesson {active_lesson.id}: {nerr}")
                    active_lesson.learning_objectives = []
                try:
                    active_lesson.key_concepts = _normalize_list_field(getattr(active_lesson, 'key_concepts', []))
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
                if hasattr(active_lesson, 'simulation_ids') and active_lesson.simulation_ids:
                    from admin.models.simulation import Simulation
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
                        print(f"⚠️ Failed to parse simulation_ids '{raw_ids}': {parse_err}")
                        normalized_ids = []

                    # Deduplicate & preserve order
                    seen = set()
                    ordered_ids = []
                    for _id in normalized_ids:
                        if _id not in seen:
                            seen.add(_id)
                            ordered_ids.append(_id)

                    if ordered_ids:
                        lesson_simulations = Simulation.query.filter(
                            Simulation.id.in_(ordered_ids),
                            Simulation.is_active == True,
                            Simulation.is_published == True
                        ).all()
                    else:
                        lesson_simulations = []
                    
                    # Get simulation progress for each lesson simulation
                    for sim in lesson_simulations:
                        user_sim_progress = SimulationAttempt.query.filter_by(
                            user_id=user_id,
                            simulation_id=sim.id,
                            is_completed=True
                        ).first()
                        simulation_progress[sim.id] = {
                            'completed': user_sim_progress is not None,
                            'score': user_sim_progress.total_score if user_sim_progress else 0,
                            'attempts': SimulationAttempt.query.filter_by(
                                user_id=user_id,
                                simulation_id=sim.id
                            ).count()
                        }
        
        # Get questions from database with module-specific filtering
        lesson_questions = []
        try:
            # Determine question category based on module characteristics
            question_category = None
            
            # Module-based category mapping logic
            if module:
                module_title_lower = module.title.lower()
                course_type_lower = module.course_type.lower()
                
                # Networking modules get networking questions
                if ('network' in module_title_lower or 
                    'networking' in course_type_lower or 
                    'tcp' in module_title_lower or 
                    'osi' in module_title_lower or
                    'ethernet' in module_title_lower or
                    'routing' in module_title_lower):
                    question_category = 'networking'
                # Default to riddle questions for other modules
                else:
                    question_category = 'riddle'
                
                print(f"Module '{module.title}' mapped to question category: '{question_category}'")
            else:
                # Fallback to networking if no module found
                question_category = 'networking'
            
            # Get questions from the 'question' table (Question model) with category filter
            questions_1 = Question.query.filter_by(category=question_category).all()
            # Get questions from the 'questions' table (StandardQuestion model) with category filter
            questions_2 = StandardQuestion.query.filter_by(category=question_category).all()
            
            # Combine questions and convert to dict format
            all_questions = []
            for q in questions_1:
                question_dict = q.to_dict()
                question_dict['source_table'] = 'question'
                all_questions.append(question_dict)
            for q in questions_2:
                question_dict = q.to_dict()
                question_dict['source_table'] = 'questions'
                all_questions.append(question_dict)
            
            # Sort by question number if available
            all_questions.sort(key=lambda x: x.get('numb', 0))
            lesson_questions = all_questions
            
            print(f"Found {len(lesson_questions)} questions for category '{question_category}' in module {module_id}")
            
        except Exception as e:
            print(f"Error fetching questions: {e}")
            lesson_questions = []

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
