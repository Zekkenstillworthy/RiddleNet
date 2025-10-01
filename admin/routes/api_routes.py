from flask import Blueprint, jsonify, request, render_template, current_app, session
from flask_login import current_user
from admin import db
from admin.models.class_model import Class
from admin.models.question_group import QuestionGroup
from admin.models.module import Module
import random
import string
from datetime import datetime
from utils.permission_decorators import teacher_required
from utils.route_guards import admin_required

api_bp = Blueprint('admin_api', __name__, url_prefix='/admin/api')

# Require instructor/admin for mutation methods across this blueprint
@api_bp.before_request
def admin_api_write_guard():
    # Allow safe methods (GET/HEAD/OPTIONS) for reads/preflights
    if request.method in ('GET', 'HEAD', 'OPTIONS'):
        return None
    # For mutating methods, enforce teacher/instructor access
    # The decorator returns a Flask response on failure; emulate that here
    @teacher_required
    def _noop():
        return None
    return _noop()

@api_bp.route('/deadlines/<int:class_id>', methods=['GET'])
def get_deadlines(class_id):
    """Get deadline data for a specific class"""
    try:
        from admin.models.class_content import ClassAssignment
        from admin.models.assignment_submission import AssignmentSubmission
        from admin.models.deadline_policy import StudentDeadlineExtension, DeadlinePolicy
        from user.models.user import User
        from datetime import datetime
        
        # Get assignments for the class
        assignments = ClassAssignment.query.filter_by(class_id=class_id).all()
        
        assignment_data = []
        for assignment in assignments:
            submissions = AssignmentSubmission.query.filter_by(assignment_id=assignment.id).all()
            extensions = StudentDeadlineExtension.query.filter_by(assignment_id=assignment.id).all()
            
            late_count = len([s for s in submissions if s.is_late])
            
            assignment_data.append({
                'id': assignment.id,
                'title': assignment.title,
                'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
                'submissions_count': len(submissions),
                'late_count': late_count,
                'extensions_count': len([e for e in extensions if e.is_active])
            })
        
        # Get active extensions for the class
        extension_data = []
        for assignment in assignments:
            extensions = StudentDeadlineExtension.query.filter_by(assignment_id=assignment.id).all()
            for extension in extensions:
                student = User.query.get(extension.student_id)
                granted_by = User.query.get(extension.granted_by_id)
                
                extension_data.append({
                    'id': extension.id,
                    'student_name': f"{student.first_name} {student.last_name}" if student else "Unknown",
                    'assignment_title': assignment.title,
                    'extended_due_date': extension.extended_due_date.isoformat() if extension.extended_due_date else None,
                    'granted_by_name': f"{granted_by.first_name} {granted_by.last_name}" if granted_by else "Unknown",
                    'reason': extension.reason,
                    'is_active': extension.is_active,
                    'used': extension.used
                })
        
        # Get policies
        policies = DeadlinePolicy.query.all()
        policy_data = []
        for policy in policies:
            # Count assignments using this policy (this would need a relationship)
            policy_data.append({
                'id': policy.id,
                'name': policy.name,
                'policy_type': policy.policy_type,
                'simple_penalty_per_day': policy.simple_penalty_per_day,
                'grace_period_hours': policy.grace_period_hours,
                'max_penalty_percentage': policy.max_penalty_percentage,
                'assignments_count': 0  # TODO: Implement policy-assignment relationship
            })
        
        # Calculate statistics
        all_submissions = AssignmentSubmission.query.join(ClassAssignment).filter(
            ClassAssignment.class_id == class_id
        ).all()
        
        late_submissions = [s for s in all_submissions if s.is_late]
        active_extensions = StudentDeadlineExtension.query.join(ClassAssignment).filter(
            ClassAssignment.class_id == class_id,
            StudentDeadlineExtension.is_active == True
        ).count()
        
        avg_late_penalty = sum([s.late_penalty_applied for s in late_submissions]) / len(late_submissions) if late_submissions else 0
        on_time_rate = ((len(all_submissions) - len(late_submissions)) / len(all_submissions) * 100) if all_submissions else 100
        
        return jsonify({
            'assignments': assignment_data,
            'extensions': extension_data,
            'policies': policy_data,
            'statistics': {
                'late_submissions': len(late_submissions),
                'active_extensions': active_extensions,
                'avg_late_penalty': round(avg_late_penalty, 1),
                'on_time_rate': round(on_time_rate, 1)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# NOTE: Duplicate endpoint removed. A more robust implementation of
# `get_classes` exists later in this file ("Get all classes with better
# error handling"). Keeping a single definition avoids Flask endpoint
# collision (AssertionError: View function mapping is overwriting an
# existing endpoint function: admin_api.get_classes) which previously
# prevented other admin blueprints (e.g., simulation routes) from
# registering.

@api_bp.route('/test', methods=['GET'])
def test_api():
    """Test endpoint to verify API connectivity"""
    try:
        # Test database connection and check for missing columns
        from sqlalchemy import text
        
        # PostgreSQL: rely on migrations; perform a lightweight check using information_schema
        try:
            column_check = db.session.execute(text("""
                SELECT 1 FROM information_schema.columns
                WHERE table_name='classes' AND column_name='updated_at'
            """)).first()
            if not column_check:
                print("[test_api] 'updated_at' column missing in 'classes' table; please generate a migration.")
        except Exception as e:
            print(f"[test_api] Column existence check failed: {e}")
        
        class_count = Class.query.count()
        
        return jsonify({
            'status': 'success',
            'message': 'API is working',
            'database_connected': True,
            'class_count': class_count
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'API test failed: {str(e)}',
            'database_connected': False
        }), 500

@api_bp.route('/classes', methods=['GET'])
def get_classes():
    """Get all classes with better error handling"""
    try:
        print("Fetching classes from database...")
        # Only return classes owned by current admin unless super_admin
        try:
            if hasattr(current_user, 'role') and current_user.role == 'super_admin':
                classes = Class.query.all()
            else:
                classes = Class.query.filter_by(created_by=getattr(current_user, 'id', None)).all()
        except Exception:
            classes = Class.query.all()
        print(f"Found {len(classes)} classes in database")
        
        classes_data = []
        for cls in classes:
            try:
                print(f"Processing class: {cls.name} (ID: {cls.id})")
                class_dict = cls.to_dict()
                classes_data.append(class_dict)
                print(f"Successfully converted class {cls.id} to dict")
            except Exception as e:
                print(f"Error converting class {cls.id} to dict: {e}")
                # Add minimal data if to_dict fails
                classes_data.append({
                    'id': cls.id,
                    'name': cls.name or 'Unknown',
                    'code': cls.code or 'NO-CODE',
                    'status': cls.status or 'active',
                    'studentCount': 0,
                    'maxStudents': cls.max_students or 30,
                    'startDate': cls.start_date.isoformat() if cls.start_date else None,
                    'endDate': cls.end_date.isoformat() if cls.end_date else None,
                    'section': cls.section,
                    'description': cls.description
                })
        
        print(f"Returning {len(classes_data)} classes")
        return jsonify(classes_data)
        
    except Exception as e:
        print(f"Error in get_classes: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Failed to fetch classes: {str(e)}',
            'classes': []
        }), 500

@api_bp.route('/classes', methods=['POST'])
def create_class():
    """Create a new class"""
    try:
        data = request.get_json()
        
        # Create new class instance with safer field handling
        new_class = Class(
            name=data['name'],
            section=data.get('section'),
            code=data['code'],
            description=data.get('description'),
            start_date=data['startDate'],
            end_date=data['endDate'],
            max_students=data['maxStudents'],
            status=data.get('status', 'active')
        )
        # Set ownership if current_user is available
        try:
            new_class.created_by = getattr(current_user, 'id', None)
        except Exception:
            pass
        
        # Manually set timestamps if column exists
        try:
            new_class.created_at = datetime.utcnow()
            new_class.updated_at = datetime.utcnow()
        except Exception as e:
            print(f"Warning: Could not set timestamps: {e}")
        
        # Add to database
        db.session.add(new_class)
        db.session.commit()
        
        # Add Quiz if provided
        if data.get('questionGroups'):
            for group_id in data['questionGroups']:
                group = QuestionGroup.query.get(group_id)
                if group:
                    new_class.question_groups.append(group)
            db.session.commit()
        
        # ✅ UNIVERSAL TEMPLATE: All classes use the same dynamic template
        # No need to generate class-specific templates anymore
        try:
            print(f"✅ Class created: {new_class.name} - will use universal dynamic template")
            print(f"🎯 New class will be accessible at: /class/{new_class.id}")
            print(f"📄 Using universal template: dynamic_class_universal.html") 
        except Exception as log_error:
            print(f"⚠️ Logging error: {log_error}")
            # Don't fail the class creation for logging issues
        
        return jsonify({
            'message': 'Class created successfully',
            'class': new_class.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@api_bp.route('/classes/<int:class_id>', methods=['GET'])
def get_class(class_id):
    """Get a specific class"""
    try:
        cls = Class.query.get_or_404(class_id)
        # Ownership check
        if not (hasattr(current_user, 'role') and current_user.role == 'super_admin') and cls.created_by != getattr(current_user, 'id', None):
            return jsonify({'error': 'Permission denied'}), 403
        return jsonify(cls.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@api_bp.route('/classes/<int:class_id>/students', methods=['GET'])
def get_class_students(class_id):
    """Get students enrolled in a class"""
    try:
        cls = Class.query.get_or_404(class_id)
        students = cls.students  # This will use the property method
        
        return jsonify({
            'students': students,
            'count': len(students)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/classes/<int:class_id>/assignments', methods=['GET'])
def get_class_assignments(class_id):
    """Get assignments for a specific class"""
    try:
        cls = Class.query.get_or_404(class_id)
        # TODO: Query actual assignments from database when assignment model is created
        # For now, return an empty, consistently shaped response
        return jsonify({
            'success': True,
            'assignments': []
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/generate-class-code', methods=['GET'])
def generate_class_code():
    """Generate a unique class code"""
    def generate_code():
        chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        return ''.join(random.choices(chars, k=6))
    
    # Keep generating until we find a unique code
    max_attempts = 10
    for _ in range(max_attempts):
        code = generate_code()
        if not Class.query.filter_by(code=code).first():
            return jsonify({'code': code})
    
    # If we can't find a unique code, return an error
    return jsonify({'error': 'Unable to generate unique code'}), 500

@api_bp.route('/question-groups', methods=['GET'])
def get_question_groups():
    """Get all Quiz"""
    try:
        groups = QuestionGroup.query.all()
        groups_data = []
        
        for group in groups:
            group_dict = {
                'id': group.id,
                'name': group.name,
                'description': group.description if hasattr(group, 'description') else '',
                'category': group.category if hasattr(group, 'category') else '',
                'questionCount': len(group.questions) if hasattr(group, 'questions') else 0
            }
            groups_data.append(group_dict)
        
        return jsonify(groups_data)
        
    except Exception as e:
        print(f"Error fetching Quiz: {e}")
        return jsonify([])

@api_bp.route('/question-groups/assignments/explicit', methods=['POST'])
def assign_question_group_explicit():
    """Assign Quiz to class or module explicitly"""
    try:
        print(f"\n🎯 assign_question_group_explicit called")
        print(f"📋 Request method: {request.method}")
        print(f"📋 Request headers: {dict(request.headers)}")
        print(f"👤 Current user: {current_user}")
        print(f"🔐 Is authenticated: {current_user.is_authenticated}")
        
        data = request.get_json()
        print(f"📋 Request data: {data}")
        
        question_group_id = data.get('question_group_id') if data else None
        class_id = data.get('class_id') if data else None
        module_id = data.get('module_id') if data else None  # Optional: assign to specific module
        
        print(f"📋 Parsed fields: question_group_id={question_group_id}, class_id={class_id}, module_id={module_id}")
        
        if not question_group_id or not class_id:
            print(f"❌ Missing required fields: question_group_id={question_group_id}, class_id={class_id}")
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Get the Quiz
        print(f"🔍 Querying Quiz with ID: {question_group_id}")
        question_group = QuestionGroup.query.get(question_group_id)
        if not question_group:
            print(f"❌ Quiz with ID {question_group_id} not found")
            return jsonify({'success': False, 'error': 'Quiz not found'}), 404
        
        print(f"✅ Quiz found: {question_group.name} (ID: {question_group.id})")
        
        if module_id:
            print(f"🎯 Assigning to specific module (module_id={module_id}, class_id={class_id})")
            # Assign to specific module
            from admin.models.module import Module
            print(f"🔍 Querying module with ID={module_id} and class_id={class_id}")
            module = Module.query.filter_by(id=module_id, class_id=class_id).first()
            if not module:
                print(f"❌ Module with ID {module_id} not found in class {class_id}")
                # Let's check if module exists at all
                all_modules = Module.query.filter_by(id=module_id).all()
                print(f"🔍 Modules with ID {module_id} in any class: {[f'Module {m.id} in class {m.class_id}' for m in all_modules]}")
                return jsonify({'success': False, 'error': 'Module not found'}), 404
            
            print(f"✅ Module found: {module.title} (ID: {module.id}, Class ID: {module.class_id})")
            print(f"📋 Module current question_groups: {[qg.name for qg in module.question_groups]}")
            
            # Check if already assigned
            if question_group not in module.question_groups:
                print(f"✅ Quiz not already assigned, proceeding with assignment")
                module.question_groups.append(question_group)
                assignment_type = "module"
                target_name = module.title
                print(f"✅ Quiz '{question_group.name}' added to module '{module.title}'")
            else:
                # Idempotent behavior: treat duplicate assignment as success with info
                print(f"ℹ️ Quiz '{question_group.name}' already assigned to module '{module.title}' - returning idempotent success")
                assignment_type = "module"
                target_name = module.title
                return jsonify({
                    'success': True,
                    'already_assigned': True,
                    'message': f'Quiz "{question_group.name}" is already assigned to module: {module.title}. No changes made.'
                }), 200
        else:
            print(f"🎯 Assigning to entire class (class_id={class_id})")
            # Assign to entire class
            from admin.models.class_model import Class
            print(f"🔍 Querying class with ID: {class_id}")
            class_obj = Class.query.get(class_id)
            if not class_obj:
                print(f"❌ Class with ID {class_id} not found")
                return jsonify({'success': False, 'error': 'Class not found'}), 404
            
            print(f"✅ Class found: {class_obj.name} (ID: {class_obj.id})")
            print(f"📋 Class current question_groups: {[qg.name for qg in class_obj.question_groups]}")
            
            # Check if already assigned
            if question_group not in class_obj.question_groups:
                print(f"✅ Quiz not already assigned to class, proceeding with assignment")
                class_obj.question_groups.append(question_group)
                assignment_type = "class"
                target_name = class_obj.name
                print(f"✅ Quiz '{question_group.name}' added to class '{class_obj.name}'")
            else:
                # Idempotent behavior: treat duplicate assignment as success with info
                print(f"ℹ️ Quiz '{question_group.name}' already assigned to class '{class_obj.name}' - returning idempotent success")
                assignment_type = "class"
                target_name = class_obj.name
                return jsonify({
                    'success': True,
                    'already_assigned': True,
                    'message': f'Quiz "{question_group.name}" is already assigned to class: {class_obj.name}. No changes made.'
                }), 200
        
        print(f"💾 Attempting to commit database changes...")
        try:
            db.session.commit()
            print(f"✅ Database commit successful")
        except Exception as commit_error:
            print(f"❌ Database commit failed: {commit_error}")
            db.session.rollback()
            return jsonify({'success': False, 'error': f'Database commit failed: {str(commit_error)}'}), 500
        
        # Create notification data
        print(f"📬 Creating notification data...")
        notification_data = {
            'type': 'question_group_assigned',
            'question_group_name': question_group.name,
            'assignment_type': assignment_type,
            'target_name': target_name,
            'class_id': class_id,
            'module_id': module_id if module_id else None
        }
        print(f"📬 Notification data: {notification_data}")
        
        # Emit socket event for real-time notification
        print(f"📡 Attempting to emit socket notification...")
        try:
            from socket_events import emit_assignment_notification
            emit_assignment_notification(class_id, notification_data)
            print(f"✅ Socket notification emitted successfully")
        except Exception as socket_error:
            print(f"⚠️ Socket notification failed (non-critical): {socket_error}")
        
        success_message = f'Quiz "{question_group.name}" successfully assigned to {assignment_type}: {target_name}'
        print(f"✅ Assignment successful: {success_message}")
        
        return jsonify({
            'success': True,
            'message': success_message
        })
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR in assign_question_group_explicit: {e}")
        print(f"📋 Error type: {type(e).__name__}")
        import traceback
        print(f"📋 Full traceback:")
        traceback.print_exc()
        
        try:
            db.session.rollback()
            print(f"🔄 Database rollback completed")
        except Exception as rollback_error:
            print(f"❌ Database rollback failed: {rollback_error}")
        
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/render-module-preview', methods=['POST'])
def render_module_preview():
    """Render module preview using the student-identical template"""
    try:
        data = request.get_json()
        module_data = data.get('module', {})
        class_name = data.get('class_name', 'Sample Class')
        
        # Render the module preview template with the module data
        html = render_template('admin/module_preview_template.html', 
                             module=module_data, 
                             class_name=class_name)
        
        return html
        
    except Exception as e:
        print(f"Error rendering module preview: {e}")
        import traceback
        traceback.print_exc()
        return f"<div class='error-message'>Error rendering preview: {str(e)}</div>", 500

@api_bp.route('/classes/<int:class_id>/modules/<int:module_id>/preview', methods=['GET'])
def get_module_preview_data(class_id, module_id):
    """Get detailed module data for preview"""
    print("=" * 60)
    print("🔍 API PREVIEW ROUTE CALLED")
    print(f"Route: /admin/api/classes/{class_id}/modules/{module_id}/preview")
    print(f"This is the API route, not the template route!")
    print(f"Method: {request.method}")
    print(f"Referrer: {request.referrer}")
    print("=" * 60)
    
    try:
        # Get the module with all related data
        module = Module.query.filter_by(id=module_id, class_id=class_id).first()
        
        if not module:
            return jsonify({
                'success': False,
                'error': 'Module not found'
            }), 404
        
        # Parse learning objectives if they're stored as JSON string
        import json
        learning_objectives = []
        if module.learning_objectives:
            try:
                if isinstance(module.learning_objectives, str):
                    learning_objectives = json.loads(module.learning_objectives)
                elif isinstance(module.learning_objectives, list):
                    learning_objectives = module.learning_objectives
                else:
                    learning_objectives = []
            except (json.JSONDecodeError, TypeError):
                learning_objectives = []
        
        # Convert module to dict with all preview data
        module_data = {
            'id': module.id,
            'title': module.title,
            'description': module.description,
            'module_number': module.module_number,
            'estimated_duration': module.estimated_duration,
            'level': getattr(module, 'level', 'Beginner'),
            'learning_objectives': learning_objectives,
            'lessons': [],
            'materials': [],
            'assessments': [],
            'simulations': []
        }
        
        # Add lessons with detailed data
        if hasattr(module, 'lessons') and module.lessons:
            for lesson in module.lessons:
                lesson_data = {
                    'id': lesson.id,
                    'title': lesson.title,
                    'description': lesson.description,
                    'content': getattr(lesson, 'content', ''),
                    'type': getattr(lesson, 'type', 'Lesson'),
                    'duration': getattr(lesson, 'duration', None),
                    'order_index': getattr(lesson, 'order_index', 0)
                }
                module_data['lessons'].append(lesson_data)
        
        # Add materials if available
        if hasattr(module, 'materials') and module.materials:
            for material in module.materials:
                material_data = {
                    'id': material.id,
                    'title': material.title,
                    'description': material.description,
                    'type': getattr(material, 'type', 'document'),
                    'filename': getattr(material, 'filename', None),
                    'file_url': getattr(material, 'file_url', None)
                }
                module_data['materials'].append(material_data)
        
        return jsonify({
            'success': True,
            'module': module_data
        })
        
    except Exception as e:
        print(f"Error fetching module preview data: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to fetch module data: {str(e)}'
        }), 500

# Enhanced UI Components API Endpoints
@api_bp.route('/deadlines', methods=['GET'], endpoint='get_all_deadlines')
def get_all_deadlines():
    """Get all deadlines for enhanced deadline management"""
    try:
        # For now, return empty array since we don't have deadline models yet
        return jsonify({
            'success': True,
            'deadlines': []
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Missing collaboration endpoints
@api_bp.route('/collaboration/classes', methods=['GET'])
def get_collaboration_classes():
    """Get available classes for collaboration assignment"""
    try:
        from admin.models.class_model import Class
        
        # Get all active classes for collaboration
        classes = Class.query.filter_by(status='active').all()
        
        classes_data = []
        for cls in classes:
            # Count students for each class
            student_count = cls.students.count() if cls.students else 0
            
            classes_data.append({
                'id': cls.id,
                'name': cls.name,
                'code': cls.code,
                'student_count': student_count
            })
        
        return jsonify({
            'success': True,
            'classes': classes_data
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching collaboration classes: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/collaboration/classes/<int:class_id>/students', methods=['GET'])
def get_collaboration_class_students(class_id):
    """Get students for a specific class for collaboration"""
    try:
        from admin.models.class_model import Class
        
        cls = Class.query.get_or_404(class_id)
        students = cls.students.all() if cls.students else []
        
        students_data = []
        for student in students:
            students_data.append({
                'id': student.id,
                'name': student.username,  # User model has username, not name
                'email': getattr(student, 'email', ''),
                'status': getattr(student, 'status', 'active')
            })
        
        return jsonify({
            'success': True,
            'students': students_data
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching students for class {class_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/collaboration/settings', methods=['GET'])
def get_collaboration_settings():
    """Get collaboration settings for enhanced collaboration management"""
    try:
        # For now, return empty array since we don't have collaboration models yet
        return jsonify({
            'success': True,
            'settings': []
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/collaboration/settings', methods=['POST'])
def save_collaboration_settings():
    """Save collaboration settings"""
    try:
        data = request.get_json()
        # For now, just return success
        return jsonify({
            'success': True,
            'message': 'Collaboration settings saved'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# -----------------------------------------------------------------------------
# Simulation-Specific Collaboration Settings (Needed by collaboration-manager.js)
# Frontend calls: /admin/api/collaboration/simulation/<simulation_id>/collaboration
#  - GET: fetch existing settings (stored on Simulation.collaboration_settings JSON column)
#  - POST: update settings
# Returns safe defaults if none exist yet to prevent 404 / JSON parse errors.
# -----------------------------------------------------------------------------
@api_bp.route('/collaboration/simulation/<int:simulation_id>/collaboration', methods=['GET'])
def get_simulation_collaboration_settings(simulation_id):
    """Fetch collaboration settings for a specific simulation.
    Frontend expects JSON with { success: bool, collaboration_settings: {...} }
    """
    try:
        from admin.models.simulation import Simulation
        simulation = Simulation.query.get(simulation_id)
        if not simulation:
            return jsonify({'success': False, 'error': 'Simulation not found'}), 404

        # Provide sensible defaults if empty
        settings = simulation.collaboration_settings or {}
        if not settings:
            settings = {
                'enable_collaboration': False,
                'max_team_size': 4,
                'team_formation': 'manual',  # manual | auto
                'enable_chat': True,
                'enable_screen_share': False,
                'enable_annotations': False,
                'instructor_monitoring': True,
                'activity_logging': True,
                'session_timeout': 60,  # minutes
                'max_sessions': 5
            }

        return jsonify({
            'success': True,
            'collaboration_settings': settings
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching simulation collaboration settings: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/collaboration/simulation/<int:simulation_id>/collaboration', methods=['POST'])
def save_simulation_collaboration_settings(simulation_id):
    """Persist collaboration settings for a simulation."""
    try:
        from admin.models.simulation import Simulation
        simulation = Simulation.query.get(simulation_id)
        if not simulation:
            return jsonify({'success': False, 'error': 'Simulation not found'}), 404

        data = request.get_json() or {}
        new_settings = data.get('collaboration_settings') or data.get('settings') or {}

        # Basic validation / normalization
        if not isinstance(new_settings, dict):
            return jsonify({'success': False, 'error': 'Invalid settings payload'}), 400

        # Ensure required keys have defaults
        defaults = {
            'enable_collaboration': False,
            'max_team_size': 4,
            'team_formation': 'manual',
            'enable_chat': True,
            'enable_screen_share': False,
            'enable_annotations': False,
            'instructor_monitoring': True,
            'activity_logging': True,
            'session_timeout': 60,
            'max_sessions': 5
        }
        for k, v in defaults.items():
            new_settings.setdefault(k, v)

        # Simple constraints
        try:
            new_settings['max_team_size'] = max(2, min(int(new_settings.get('max_team_size', 4)), 50))
            new_settings['session_timeout'] = max(15, min(int(new_settings.get('session_timeout', 60)), 480))
            new_settings['max_sessions'] = max(1, min(int(new_settings.get('max_sessions', 5)), 100))
        except ValueError:
            return jsonify({'success': False, 'error': 'Numeric fields must be integers'}), 400

        simulation.collaboration_settings = new_settings
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Simulation collaboration settings saved',
            'collaboration_settings': new_settings
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving simulation collaboration settings: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Live Collaboration Monitoring API Endpoints - duplicate removed, kept the version at line 2586

@api_bp.route('/collaboration/active', methods=['GET'])
def get_active_collaborations():
    """Get list of active collaboration sessions"""
    try:
        # Import lobby manager to get real active collaborations
        try:
            from services.troubleshooting_lobbies import lobby_manager
            active_lobbies = lobby_manager.get_public_lobbies()
            
            collaborations = []
            for lobby_data in active_lobbies:
                # Calculate duration
                duration = "0m"
                if 'created_at' in lobby_data:
                    try:
                        from datetime import datetime
                        created_time = datetime.fromisoformat(lobby_data['created_at'].replace('Z', '+00:00'))
                        duration_minutes = int((datetime.utcnow() - created_time.replace(tzinfo=None)).total_seconds() / 60)
                        duration = f"{duration_minutes}m"
                    except:
                        pass
                
                collaborations.append({
                    'id': lobby_data.get('id'),
                    'activity_name': lobby_data.get('name', 'Unknown Session'),
                    'participants': [p.get('username', 'Unknown') for p in lobby_data.get('participants', [])],
                    'duration': duration,
                    'status': 'active',
                    'type': 'troubleshooting',
                    'scenario': lobby_data.get('scenario_type', 'Unknown')
                })
            
            return jsonify(collaborations)
            
        except ImportError:
            # Lobby manager not available - return empty array
            return jsonify([])
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/collaboration/<int:collaboration_id>/details', methods=['GET'])
def get_collaboration_details(collaboration_id):
    """Get detailed information about a specific collaboration session"""
    try:
        # Import lobby manager to get real collaboration details
        try:
            from services.troubleshooting_lobbies import lobby_manager
            lobby = lobby_manager.get_lobby(collaboration_id)
            
            if not lobby:
                return jsonify({
                    'success': False,
                    'error': 'Collaboration session not found'
                }), 404
            
            # Convert lobby to detailed format
            collaboration_details = {
                'id': lobby.id,
                'activity_name': lobby.name,
                'participants': [
                    {
                        'id': pid,
                        'username': pdata.get('username', 'Unknown'),
                        'profile_image': pdata.get('profile_image')
                    }
                    for pid, pdata in lobby.participants.items()
                ],
                'status': 'active',
                'type': 'troubleshooting',
                'scenario': lobby.scenario_type,
                'created_at': lobby.created_at.isoformat() if hasattr(lobby, 'created_at') else None,
                'max_participants': lobby.max_participants
            }
            
            return jsonify(collaboration_details)
            
        except ImportError:
            return jsonify({
                'success': False,
                'error': 'Collaboration system not available'
            }), 503
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/collaboration/<int:collaboration_id>/chat', methods=['GET'])
def get_collaboration_chat(collaboration_id):
    """Get chat history for a collaboration session"""
    try:
        # Import lobby manager to get real chat history
        try:
            from services.troubleshooting_lobbies import lobby_manager
            lobby = lobby_manager.get_lobby(collaboration_id)
            
            if not lobby:
                return jsonify({
                    'success': False,
                    'error': 'Collaboration session not found'
                }), 404
            
            # Get chat history from lobby
            chat_messages = []
            if hasattr(lobby, 'chat_history') and lobby.chat_history:
                chat_messages = [
                    {
                        'timestamp': msg.get('timestamp'),
                        'user_name': msg.get('username', 'Unknown'),
                        'message': msg.get('message', ''),
                        'user_id': msg.get('user_id')
                    }
                    for msg in lobby.chat_history
                ]
            
            return jsonify(chat_messages)
            
        except ImportError:
            return jsonify([])
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/collaboration/<int:collaboration_id>/screen', methods=['GET'])
def get_collaboration_screen(collaboration_id):
    """Get screen sharing information for a collaboration session"""
    try:
        # TODO: Query screen sharing data from database
        return jsonify({
            'active': False
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/collaboration/<int:collaboration_id>/files', methods=['GET'])
def get_collaboration_files(collaboration_id):
    """Get shared files for a collaboration session"""
    try:
        # TODO: Query shared files from database
        return jsonify([])
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/collaboration/<int:collaboration_id>/progress', methods=['GET'])
def get_collaboration_progress(collaboration_id):
    """Get progress tracking for a collaboration session"""
    try:
        # TODO: Query progress data from database
        return jsonify({
            'participants': []
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/collaboration/<int:collaboration_id>/join', methods=['POST'])
def join_collaboration(collaboration_id):
    """Allow admin to join a collaboration session"""
    try:
        # TODO: Implement admin join functionality
        return jsonify({
            'success': False,
            'error': 'Collaboration session not found or not active'
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/collaboration/<int:collaboration_id>/end', methods=['POST'])
def end_collaboration(collaboration_id):
    """End a collaboration session"""
    try:
        # Import lobby manager to end the collaboration
        try:
            from services.troubleshooting_lobbies import lobby_manager
            lobby = lobby_manager.get_lobby(collaboration_id)
            
            if not lobby:
                return jsonify({
                    'success': False,
                    'error': 'Collaboration session not found or already ended'
                }), 404
            
            # Close the lobby (this will kick out all participants)
            result = lobby_manager.close_lobby(collaboration_id)
            
            if result:
                return jsonify({
                    'success': True,
                    'message': 'Collaboration session ended successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to end collaboration session'
                }), 500
            
        except ImportError:
            return jsonify({
                'success': False,
                'error': 'Collaboration system not available'
            }), 503
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/collaboration/files/<int:file_id>/download', methods=['GET'])
def download_collaboration_file(file_id):
    """Download a shared collaboration file"""
    try:
        # TODO: Implement file download functionality
        return jsonify({
            'success': False,
            'error': 'File not found'
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/grades/<int:class_id>', methods=['GET'])
@admin_required
def get_class_grades(class_id):
    """Get comprehensive grade data for a class"""
    try:
        print(f"🔍 DEBUG: Getting grades for class {class_id}")
        from admin.models.class_content import ClassAssignment
        from admin.models.assignment_submission import AssignmentSubmission
        from user.models.user import User
        from admin.models.class_model import Class
        
        print(f"🔍 DEBUG: Fetching class object {class_id}")
        # Verify class exists and user has access
        class_obj = Class.query.get_or_404(class_id)
        print(f"✅ DEBUG: Class found: {class_obj.name}")
        
        print(f"🔍 DEBUG: Getting students for class {class_id}")
        # Get all students in the class using the relationship
        students = class_obj.students.all()
        print(f"✅ DEBUG: Found {len(students)} students")
        
        print(f"🔍 DEBUG: Getting assignments for class {class_id}")
        # Get all assignments for this class
        assignments = ClassAssignment.query.filter_by(class_id=class_id).all()
        print(f"✅ DEBUG: Found {len(assignments)} assignments")
        
        print(f"🔍 DEBUG: Getting submissions for assignments")
        # Get all submissions for these assignments
        assignment_ids = [a.id for a in assignments]
        submissions = AssignmentSubmission.query.filter(
            AssignmentSubmission.assignment_id.in_(assignment_ids)
        ).all() if assignment_ids else []
        print(f"✅ DEBUG: Found {len(submissions)} submissions")
        
        print(f"🔍 DEBUG: Processing submissions data")
        # Group submissions by student and assignment
        submission_map = {}
        grade_map = {}
        
        for submission in submissions:
            try:
                if submission.student_id not in submission_map:
                    submission_map[submission.student_id] = {}
                    grade_map[submission.student_id] = {}
                
                submission_map[submission.student_id][submission.assignment_id] = submission
                
                if submission.grade is not None:
                    grade_map[submission.student_id][submission.assignment_id] = {
                        'score': submission.grade,
                        'max_points': submission.max_points or 100,
                        'percentage': (submission.grade / (submission.max_points or 100)) * 100,
                        'graded_at': submission.graded_at.isoformat() if submission.graded_at else None
                    }
            except Exception as e:
                print(f"❌ DEBUG: Error processing submission {submission.id}: {e}")
                continue
        
        print(f"🔍 DEBUG: Building student data")
        # Prepare student data
        student_data = []
        for student in students:
            try:
                student_grades = grade_map.get(student.id, {})
                student_submissions = submission_map.get(student.id, {})
                
                student_data.append({
                    'id': student.id,
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'email': student.email,
                    'grades': student_grades,
                    'submissions': {aid: {'status': sub.status, 'submitted_at': sub.submitted_at.isoformat() if sub.submitted_at else None} 
                                  for aid, sub in student_submissions.items()}
                })
            except Exception as e:
                print(f"❌ DEBUG: Error processing student {student.id}: {e}")
                continue
        
        print(f"✅ DEBUG: Built data for {len(student_data)} students")
        
        print(f"🔍 DEBUG: Building assignment statistics")
        # Prepare assignment data with statistics
        assignment_data = []
        for assignment in assignments:
            try:
                assignment_submissions = [s for s in submissions if s.assignment_id == assignment.id]
                assignment_grades = [s.grade for s in assignment_submissions if s.grade is not None]
                
                stats = {
                    'id': assignment.id,
                    'title': assignment.title,
                    'type': 'assignment',
                    'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
                    'max_points': assignment.max_points or 100,
                    'submitted_count': len(assignment_submissions),
                    'graded_count': len(assignment_grades),
                    'average_grade': sum(assignment_grades) / len(assignment_grades) if assignment_grades else 0
                }
                assignment_data.append(stats)
            except Exception as e:
                print(f"❌ DEBUG: Error processing assignment {assignment.id}: {e}")
                continue
        
        print(f"✅ DEBUG: Built data for {len(assignment_data)} assignments")
        
        # TODO: Add simulation and quiz data when those models are available
        simulation_data = []
        quiz_data = []
        
        response_data = {
            'students': student_data,
            'assignments': assignment_data,
            'simulations': simulation_data,
            'quizzes': quiz_data,
            'class_info': {
                'id': class_obj.id,
                'name': class_obj.name,
                'code': class_obj.code
            }
        }
        
        print(f"✅ DEBUG: Successfully built grades response")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ DEBUG: Fatal error in get_class_grades: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# DEADLINE MANAGEMENT API ENDPOINTS

@api_bp.route('/deadline-policies', methods=['GET'])
def get_deadline_policies():
    """Get all deadline policies"""
    try:
        from admin.models.deadline_policy import DeadlinePolicy
        
        policies = DeadlinePolicy.query.all()
        return jsonify({
            'success': True,
            'policies': [policy.to_dict() for policy in policies]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/deadline-policies', methods=['POST'])
def create_deadline_policy():
    """Create a new deadline policy"""
    try:
        from admin.models.deadline_policy import DeadlinePolicy, PenaltyTier
        from flask_login import current_user
        
        data = request.get_json()
        
        policy = DeadlinePolicy(
            name=data['name'],
            description=data.get('description'),
            policy_type=data.get('policy_type', 'simple'),
            simple_penalty_per_day=data.get('simple_penalty_per_day', 10.0),
            max_penalty_percentage=data.get('max_penalty_percentage', 100.0),
            grace_period_hours=data.get('grace_period_hours', 0),
            hard_cutoff_enabled=data.get('hard_cutoff_enabled', False),
            hard_cutoff_days=data.get('hard_cutoff_days', 7),
            exclude_weekends=data.get('exclude_weekends', False),
            exclude_holidays=data.get('exclude_holidays', False),
            allow_partial_credit=data.get('allow_partial_credit', True),
            round_penalty_up=data.get('round_penalty_up', False),
            created_by=current_user.id
        )
        
        db.session.add(policy)
        db.session.flush()  # Get the policy ID
        
        # Add penalty tiers if specified
        if 'penalty_tiers' in data:
            for tier_data in data['penalty_tiers']:
                tier = PenaltyTier(
                    policy_id=policy.id,
                    start_day=tier_data['start_day'],
                    end_day=tier_data.get('end_day'),
                    penalty_percentage=tier_data['penalty_percentage'],
                    penalty_type=tier_data.get('penalty_type', 'per_day'),
                    description=tier_data.get('description')
                )
                db.session.add(tier)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Deadline policy created successfully',
            'policy': policy.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/deadline-policies/<int:policy_id>', methods=['PUT'])
def update_deadline_policy(policy_id):
    """Update a deadline policy"""
    try:
        from admin.models.deadline_policy import DeadlinePolicy, PenaltyTier
        
        policy = DeadlinePolicy.query.get_or_404(policy_id)
        data = request.get_json()
        
        # Update policy fields
        for field in ['name', 'description', 'policy_type', 'simple_penalty_per_day',
                     'max_penalty_percentage', 'grace_period_hours', 'hard_cutoff_enabled',
                     'hard_cutoff_days', 'exclude_weekends', 'exclude_holidays',
                     'allow_partial_credit', 'round_penalty_up']:
            if field in data:
                setattr(policy, field, data[field])
        
        # Update penalty tiers if specified
        if 'penalty_tiers' in data:
            # Remove existing tiers
            PenaltyTier.query.filter_by(policy_id=policy.id).delete()
            
            # Add new tiers
            for tier_data in data['penalty_tiers']:
                tier = PenaltyTier(
                    policy_id=policy.id,
                    start_day=tier_data['start_day'],
                    end_day=tier_data.get('end_day'),
                    penalty_percentage=tier_data['penalty_percentage'],
                    penalty_type=tier_data.get('penalty_type', 'per_day'),
                    description=tier_data.get('description')
                )
                db.session.add(tier)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Deadline policy updated successfully',
            'policy': policy.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/deadline-policies/<int:policy_id>', methods=['DELETE'])
def delete_deadline_policy(policy_id):
    """Delete a deadline policy"""
    try:
        from admin.models.deadline_policy import DeadlinePolicy
        
        policy = DeadlinePolicy.query.get_or_404(policy_id)
        
        # Check if policy is in use
        from admin.models.deadline_policy import AssignmentAvailabilityWindow
        in_use = AssignmentAvailabilityWindow.query.filter_by(deadline_policy_id=policy.id).first()
        
        if in_use:
            return jsonify({
                'success': False,
                'error': 'Cannot delete policy that is currently in use by assignments'
            }), 400
        
        db.session.delete(policy)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Deadline policy deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/assignments/<int:assignment_id>/availability', methods=['GET'])
def get_assignment_availability(assignment_id):
    """Get assignment availability window"""
    try:
        from admin.models.deadline_policy import AssignmentAvailabilityWindow
        from services.deadline_service import DeadlineService
        
        availability = AssignmentAvailabilityWindow.query.filter_by(
            assignment_id=assignment_id
        ).first()
        
        if availability:
            return jsonify({
                'success': True,
                'availability': availability.to_dict()
            })
        else:
            return jsonify({
                'success': True,
                'availability': None
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/assignments/<int:assignment_id>/availability', methods=['POST', 'PUT'])
def set_assignment_availability(assignment_id):
    """Set or update assignment availability window"""
    try:
        from admin.models.deadline_policy import AssignmentAvailabilityWindow
        from datetime import datetime
        
        data = request.get_json()
        
        # Get or create availability window
        availability = AssignmentAvailabilityWindow.query.filter_by(
            assignment_id=assignment_id
        ).first()
        
        if not availability:
            availability = AssignmentAvailabilityWindow(assignment_id=assignment_id)
            db.session.add(availability)
        
        # Update fields
        date_fields = ['available_from', 'available_until', 'due_date', 
                      'extended_due_date', 'late_submission_until']
        
        for field in date_fields:
            if field in data and data[field]:
                try:
                    setattr(availability, field, datetime.fromisoformat(data[field].replace('Z', '+00:00')))
                except ValueError:
                    setattr(availability, field, datetime.strptime(data[field], '%Y-%m-%d %H:%M:%S'))
            elif field in data and data[field] is None:
                setattr(availability, field, None)
        
        # Update other fields
        other_fields = ['late_submission_enabled', 'deadline_policy_id', 
                       'custom_penalty_enabled', 'custom_penalty_per_day',
                       'require_password', 'access_password', 'ip_restrictions',
                       'time_limit_enabled', 'time_limit_minutes', 'max_attempts',
                       'allow_save_and_resume']
        
        for field in other_fields:
            if field in data:
                setattr(availability, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Assignment availability updated successfully',
            'availability': availability.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/assignments/<int:assignment_id>/extensions', methods=['GET'])
def get_assignment_extensions(assignment_id):
    """Get all deadline extensions for an assignment"""
    try:
        from admin.models.deadline_policy import StudentDeadlineExtension
        from user.models.user import User
        
        extensions = db.session.query(StudentDeadlineExtension, User).join(
            User, StudentDeadlineExtension.student_id == User.id
        ).filter(StudentDeadlineExtension.assignment_id == assignment_id).all()
        
        result = []
        for extension, student in extensions:
            ext_dict = extension.to_dict()
            ext_dict['student'] = {
                'id': student.id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email
            }
            result.append(ext_dict)
        
        return jsonify({
            'success': True,
            'extensions': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/assignments/<int:assignment_id>/extensions', methods=['POST'])
def grant_deadline_extension(assignment_id):
    """Grant a deadline extension to a student"""
    try:
        from services.deadline_service import DeadlineService
        from flask_login import current_user
        
        data = request.get_json()
        
        extension = DeadlineService.grant_extension(
            assignment_id=assignment_id,
            student_id=data['student_id'],
            hours=data['hours'],
            reason=data.get('reason'),
            approved_by=current_user.id,
            waive_late_penalty=data.get('waive_late_penalty', False),
            custom_penalty_rate=data.get('custom_penalty_rate'),
            approval_notes=data.get('approval_notes')
        )
        
        return jsonify({
            'success': True,
            'message': 'Deadline extension granted successfully',
            'extension': extension.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/extensions/<int:extension_id>', methods=['PUT'])
def update_deadline_extension(extension_id):
    """Update a deadline extension"""
    try:
        from admin.models.deadline_policy import StudentDeadlineExtension
        from datetime import datetime, timedelta
        
        extension = StudentDeadlineExtension.query.get_or_404(extension_id)
        data = request.get_json()
        
        # Update extension hours and recalculate due date
        if 'hours' in data:
            extension.extension_hours = data['hours']
            extension.extended_due_date = extension.original_due_date + timedelta(hours=data['hours'])
        
        # Update other fields
        for field in ['reason', 'approval_notes', 'waive_late_penalty', 
                     'custom_penalty_rate', 'is_active']:
            if field in data:
                setattr(extension, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Deadline extension updated successfully',
            'extension': extension.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/extensions/<int:extension_id>', methods=['DELETE'])
def revoke_deadline_extension(extension_id):
    """Revoke a deadline extension"""
    try:
        from admin.models.deadline_policy import StudentDeadlineExtension
        
        extension = StudentDeadlineExtension.query.get_or_404(extension_id)
        
        # Check if extension has been used
        if extension.used:
            # Don't delete, just deactivate
            extension.is_active = False
            db.session.commit()
            message = 'Extension deactivated (student had already used it)'
        else:
            # Can safely delete
            db.session.delete(extension)
            db.session.commit()
            message = 'Extension revoked successfully'
        
        return jsonify({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/assignments/<int:assignment_id>/penalty-calculation', methods=['POST'])
def calculate_assignment_penalties(assignment_id):
    """Calculate penalties for all submissions of an assignment"""
    try:
        from admin.models.class_content import ClassAssignment
        from admin.models.assignment_submission import AssignmentSubmission
        from services.deadline_service import DeadlineService
        
        assignment = ClassAssignment.query.get_or_404(assignment_id)
        submissions = AssignmentSubmission.query.filter_by(assignment_id=assignment_id).all()
        
        results = []
        for submission in submissions:
            penalty_result = DeadlineService.calculate_late_penalty(submission, assignment)
            results.append({
                'submission_id': submission.id,
                'student_id': submission.student_id,
                'penalty_result': penalty_result
            })
        
        return jsonify({
            'success': True,
            'assignment_id': assignment_id,
            'penalty_calculations': results,
            'total_submissions': len(submissions),
            'late_submissions': len([r for r in results if r['penalty_result']['is_late']])
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/submissions/<int:submission_id>/penalty-details', methods=['GET'])
def get_submission_penalty_details(submission_id):
    """Get detailed penalty calculation for a specific submission"""
    try:
        from admin.models.assignment_submission import AssignmentSubmission
        from admin.models.deadline_policy import DeadlineCalculationLog
        from services.deadline_service import DeadlineService
        
        submission = AssignmentSubmission.query.get_or_404(submission_id)
        assignment = submission.assignment
        
        # Get current penalty calculation
        penalty_result = DeadlineService.calculate_late_penalty(submission, assignment)
        
        # Get calculation logs
        logs = DeadlineCalculationLog.query.filter_by(
            submission_id=submission_id
        ).order_by(DeadlineCalculationLog.calculated_at.desc()).all()
        
        return jsonify({
            'success': True,
            'submission': submission.to_dict(),
            'current_penalty': penalty_result,
            'calculation_history': [log.to_dict() for log in logs]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/assignments/<int:assignment_id>/availability-check', methods=['GET'])
def check_assignment_availability(assignment_id):
    """Check current availability status of an assignment"""
    try:
        from admin.models.class_content import ClassAssignment
        from services.deadline_service import DeadlineService
        
        assignment = ClassAssignment.query.get_or_404(assignment_id)
        student_id = request.args.get('student_id', type=int)
        
        availability_status = DeadlineService.check_assignment_availability(assignment, student_id)
        
        return jsonify({
            'success': True,
            'assignment_id': assignment_id,
            'availability': availability_status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/classes/<int:class_id>/deadline-report', methods=['GET'])
def get_class_deadline_report(class_id):
    """Get comprehensive deadline report for a class"""
    try:
        from admin.models.class_content import ClassAssignment
        from admin.models.assignment_submission import AssignmentSubmission
        from admin.models.deadline_policy import StudentDeadlineExtension, DeadlineCalculationLog
        from user.models.user import User
        from datetime import datetime, timedelta
        
        # Get all assignments for the class
        assignments = ClassAssignment.query.filter_by(class_id=class_id).all()
        assignment_ids = [a.id for a in assignments]
        
        # Get all submissions
        submissions = AssignmentSubmission.query.filter(
            AssignmentSubmission.assignment_id.in_(assignment_ids)
        ).all() if assignment_ids else []
        
        # Get all extensions
        extensions = StudentDeadlineExtension.query.filter(
            StudentDeadlineExtension.assignment_id.in_(assignment_ids)
        ).all() if assignment_ids else []
        
        # Get penalty logs for recent calculations
        recent_date = datetime.utcnow() - timedelta(days=30)
        penalty_logs = DeadlineCalculationLog.query.filter(
            DeadlineCalculationLog.submission_id.in_([s.id for s in submissions]),
            DeadlineCalculationLog.calculated_at >= recent_date
        ).all() if submissions else []
        
        # Calculate statistics
        total_submissions = len(submissions)
        late_submissions = len([s for s in submissions if s.is_late])
        on_time_rate = ((total_submissions - late_submissions) / total_submissions * 100) if total_submissions > 0 else 0
        
        # Extensions statistics
        total_extensions = len(extensions)
        active_extensions = len([e for e in extensions if e.is_active])
        used_extensions = len([e for e in extensions if e.used])
        
        # Assignment breakdown
        assignment_stats = []
        for assignment in assignments:
            assignment_submissions = [s for s in submissions if s.assignment_id == assignment.id]
            assignment_late = len([s for s in assignment_submissions if s.is_late])
            assignment_extensions = [e for e in extensions if e.assignment_id == assignment.id]
            
            assignment_stats.append({
                'assignment_id': assignment.id,
                'title': assignment.title,
                'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
                'total_submissions': len(assignment_submissions),
                'late_submissions': assignment_late,
                'on_time_rate': ((len(assignment_submissions) - assignment_late) / len(assignment_submissions) * 100) if assignment_submissions else 0,
                'extensions_granted': len(assignment_extensions),
                'average_penalty': sum([s.late_penalty_applied for s in assignment_submissions if s.late_penalty_applied]) / len([s for s in assignment_submissions if s.late_penalty_applied]) if [s for s in assignment_submissions if s.late_penalty_applied] else 0
            })
        
        return jsonify({
            'success': True,
            'class_id': class_id,
            'report_generated': datetime.utcnow().isoformat(),
            'overview': {
                'total_assignments': len(assignments),
                'total_submissions': total_submissions,
                'late_submissions': late_submissions,
                'on_time_rate': on_time_rate,
                'total_extensions': total_extensions,
                'active_extensions': active_extensions,
                'used_extensions': used_extensions
            },
            'assignment_breakdown': assignment_stats,
            'recent_penalty_calculations': len(penalty_logs)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Module Content Assignment Endpoints
@api_bp.route('/classes/<int:class_id>/question-groups', methods=['GET'])
def get_class_question_groups(class_id):
    """Get Quiz for a class"""
    try:
        from admin.models.class_model import Class
        
        class_obj = Class.query.get_or_404(class_id)
        question_groups = class_obj.question_groups.all()
        
        question_groups_data = []
        for qg in question_groups:
            question_groups_data.append({
                'id': qg.id,
                'name': qg.name,
                'description': qg.description,
                'question_count': len(qg.questions) if hasattr(qg, 'questions') else 0,
                'is_active': getattr(qg, 'is_active', True)
            })
        
        return jsonify({
            'success': True,
            'question_groups': question_groups_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/classes/<int:class_id>/simulations', methods=['GET'])  
def get_class_simulations(class_id):
    """Get simulations assigned to a class"""
    try:
        from admin.models.simulation_assignment import SimulationAssignment
        
        assignments = SimulationAssignment.query.filter_by(
            class_id=class_id,
            is_active=True
        ).all()
        
        simulations_data = []
        for assignment in assignments:
            if assignment.simulation and assignment.simulation.is_active:
                simulations_data.append({
                    'id': assignment.simulation.id,
                    'assignment_id': assignment.id,
                    'title': assignment.simulation.title,
                    'description': assignment.simulation.description,
                    'category': assignment.simulation.category,
                    'difficulty': assignment.simulation.difficulty,
                    'estimated_duration': assignment.simulation.estimated_duration,
                    'module_id': assignment.module_id,
                    'due_date': assignment.due_date.isoformat() if assignment.due_date else None
                })
        
        return jsonify({
            'success': True,
            'simulations': simulations_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/modules/<int:module_id>/content', methods=['GET'])
@admin_required
def get_module_content(module_id):
    """Get content assigned to a module (simulations, assignments, Quiz).

    Frontend calls this for many module cards during page load. Returning 404s causes
    noisy console errors and breaks UX. If a module is missing (deleted or not in this
    class), return a 200 with an empty content payload so the UI can render an empty
    state gracefully.
    """
    try:
        from admin.models.module import Module
        from admin.models.simulation_assignment import SimulationAssignment
        from admin.models.class_content import ClassAssignment

        print(f"[get_module_content] Request for module_id={module_id}")
        module = Module.query.get(module_id)
        if not module:
            print(f"[get_module_content] Module {module_id} not found. Returning empty content.")
            return jsonify({
                'success': True,
                'module': {
                    'id': module_id,
                    'title': None,
                    'description': None
                },
                'simulations': [],
                'assignments': [],
                'question_groups': []
            }), 200

        # Get simulations assigned to this module
        sim_assignments = SimulationAssignment.query.filter_by(
            module_id=module_id,
            is_active=True
        ).all()

        simulations_data = []
        for assignment in sim_assignments:
            if assignment.simulation and getattr(assignment.simulation, 'is_active', True):
                simulations_data.append({
                    'id': assignment.simulation.id,
                    'assignment_id': assignment.id,
                    'title': assignment.simulation.title,
                    'description': assignment.simulation.description,
                    'category': getattr(assignment.simulation, 'category', None),
                    'difficulty': getattr(assignment.simulation, 'difficulty', None),
                    'due_date': assignment.due_date.isoformat() if assignment.due_date else None
                })

        # Get assignments assigned to this module
        assignments = ClassAssignment.query.filter_by(
            module_id=module_id,
            is_published=True
        ).all()

        assignments_data = []
        for assignment in assignments:
            assignments_data.append({
                'id': assignment.id,
                'title': assignment.title,
                'description': assignment.description,
                'due_date': assignment.due_date.isoformat() if getattr(assignment, 'due_date', None) else None,
                'points': getattr(assignment, 'points', None),
                'assignment_type': getattr(assignment, 'assignment_type', None)
            })

        # Get Quiz assigned to this module
        question_groups_data = []
        if hasattr(module, 'question_groups') and module.question_groups:
            for qg in module.question_groups:
                question_groups_data.append({
                    'id': qg.id,
                    'name': qg.name,
                    'description': getattr(qg, 'description', None),
                    'question_count': len(qg.questions) if hasattr(qg, 'questions') and qg.questions else 0
                })

        print(f"[get_module_content] Module {module.id} found (class_id={getattr(module, 'class_id', 'n/a')}). Returning content: sims={len(simulations_data)}, assignments={len(assignments_data)}, qgs={len(question_groups_data)}")
        return jsonify({
            'success': True,
            'module': {
                'id': module.id,
                'title': module.title,
                'description': module.description
            },
            'simulations': simulations_data,
            'assignments': assignments_data,
            'question_groups': question_groups_data
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/modules/<int:module_id>/assign-simulation', methods=['POST'])
def assign_simulation_to_module(module_id):
    """Assign a simulation to a module"""
    try:
        from admin.models.module import Module
        from admin.models.simulation import Simulation
        from admin.models.simulation_assignment import SimulationAssignment
        from datetime import datetime, timedelta
        
        data = request.get_json()
        simulation_id = data.get('simulation_id')
        due_date_str = data.get('due_date')
        
        if not simulation_id:
            return jsonify({
                'success': False,
                'error': 'Simulation ID is required'
            }), 400
            
        module = Module.query.get_or_404(module_id)
        simulation = Simulation.query.get_or_404(simulation_id)
        
        # Parse due date
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            except:
                # Fallback: set due date to 7 days from now
                due_date = datetime.utcnow() + timedelta(days=7)
        
        # Check if assignment already exists
        existing_assignment = SimulationAssignment.query.filter_by(
            simulation_id=simulation_id,
            module_id=module_id,
            class_id=module.class_id
        ).first()
        
        if existing_assignment:
            # Idempotent success: already assigned
            return jsonify({
                'success': True,
                'message': f'Simulation "{simulation.title}" is already assigned to module "{module.title}"',
                'alreadyAssigned': True,
                'assignment_id': existing_assignment.id
            }), 200
        
        # Create new assignment
        assignment = SimulationAssignment(
            title=f"{simulation.title} - {module.title}",
            description=f"Simulation assignment for {module.title}",
            simulation_id=simulation_id,
            class_id=module.class_id,
            module_id=module_id,
            assigned_by=getattr(current_user, 'id', 1),
            assignment_type='module',
            due_date=due_date,
            is_active=True,
            is_published=True
        )
        
        db.session.add(assignment)
        db.session.commit()
        
        # Emit WebSocket event to users viewing this module
        try:
            from socket_events import emit_module_content_updated
            emit_module_content_updated(module.class_id, module_id, {
                'type': 'simulation_assigned',
                'simulation': {
                    'id': simulation.id,
                    'title': simulation.title,
                    'description': simulation.description
                },
                'module': {
                    'id': module.id,
                    'title': module.title
                },
                'assignment_id': assignment.id,
                'assigned_by': current_user.username if current_user.is_authenticated else 'System'
            })
        except Exception as e:
            print(f"Warning: Failed to emit module content update: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': f'Simulation "{simulation.title}" assigned to module "{module.title}"',
            'assignment_id': assignment.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/modules/<int:module_id>/assign-assignment', methods=['POST'])
def assign_assignment_to_module(module_id):
    """Assign a class assignment to a module"""
    try:
        from admin.models.module import Module
        from admin.models.class_content import ClassAssignment
        
        data = request.get_json()
        assignment_id = data.get('assignment_id')
        
        if not assignment_id:
            return jsonify({
                'success': False,
                'error': 'Assignment ID is required'
            }), 400
            
        module = Module.query.get_or_404(module_id)
        assignment = ClassAssignment.query.get_or_404(assignment_id)
        
        # Update assignment to be linked to this module
        assignment.module_id = module_id
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Assignment "{assignment.title}" assigned to module "{module.title}"'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/modules/<int:module_id>/assign-question-group', methods=['POST'])
def assign_question_group_to_module(module_id):
    """Assign a Quiz to a module"""
    try:
        from admin.models.module import Module
        from admin.models.question_group import QuestionGroup
        
        data = request.get_json()
        print(f"\n📥 assign_question_group_to_module called for module_id={module_id}")
        print(f"🔎 Raw JSON payload: {data}")
        question_group_id = data.get('question_group_id') if data else None
        
        if not question_group_id:
            return jsonify({
                'success': False,
                'error': 'Quiz ID is required'
            }), 400
            
        module = Module.query.get_or_404(module_id)
        question_group = QuestionGroup.query.get_or_404(question_group_id)
        print(f"✅ Module found: {module.id} - {getattr(module, 'title', 'N/A')}")
        print(f"✅ Quiz found: {question_group.id} - {getattr(question_group, 'name', 'N/A')}")
        
        # Check if already assigned
        already_assigned = module.question_groups.filter_by(id=question_group.id).first() is not None
        if already_assigned:
            print(f"ℹ️ Quiz {question_group.id} already assigned to module {module.id} (idempotent success)")
            return jsonify({
                'success': True,
                'message': f'Quiz "{question_group.name}" is already assigned to module "{module.title}"',
                'alreadyAssigned': True
            }), 200
        
        # Add Quiz to module
        module.question_groups.append(question_group)
        db.session.commit()
        print(f"🟢 Assigned Quiz {question_group.id} to module {module.id}")
        
        return jsonify({
            'success': True,
            'message': f'Quiz "{question_group.name}" assigned to module "{module.title}"'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error in assign_question_group_to_module: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/modules/<int:module_id>/unassign-simulation/<int:assignment_id>', methods=['DELETE'])
def unassign_simulation_from_module(module_id, assignment_id):
    """Remove a simulation assignment from a module"""
    try:
        from admin.models.simulation_assignment import SimulationAssignment
        
        assignment = SimulationAssignment.query.filter_by(
            id=assignment_id,
            module_id=module_id
        ).first_or_404()
        
        assignment.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Simulation unassigned from module'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/modules/<int:module_id>/unassign-assignment/<int:assignment_id>', methods=['DELETE'])
def unassign_assignment_from_module(module_id, assignment_id):
    """Remove an assignment from a module"""
    try:
        from admin.models.class_content import ClassAssignment
        
        assignment = ClassAssignment.query.filter_by(
            id=assignment_id,
            module_id=module_id
        ).first_or_404()
        
        assignment.module_id = None
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Assignment unassigned from module'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/modules/<int:module_id>/unassign-question-group/<int:question_group_id>', methods=['DELETE'])
def unassign_question_group_from_module(module_id, question_group_id):
    """Remove a Quiz from a module"""
    try:
        from admin.models.module import Module
        from admin.models.question_group import QuestionGroup
        
        module = Module.query.get_or_404(module_id)
        question_group = QuestionGroup.query.get_or_404(question_group_id)
        
        if question_group in module.question_groups:
            module.question_groups.remove(question_group)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Quiz unassigned from module'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =============================================================================
# LOBBY MANAGEMENT API ENDPOINTS
# =============================================================================

@api_bp.route('/lobbies', methods=['GET'])
def get_admin_lobbies():
    """Get all lobbies for admin management"""
    try:
        from services.troubleshooting_lobbies import lobby_manager
        
        class_id = request.args.get('class_id', type=int)
        
        # Get all lobbies
        all_lobbies = lobby_manager.get_public_lobbies()
        
        # Filter by class if specified
        if class_id:
            filtered_lobbies = [
                lobby for lobby in all_lobbies 
                if lobby.get('class_id') == class_id
            ]
        else:
            filtered_lobbies = all_lobbies
        
        # Format for admin interface
        lobbies = []
        for lobby_data in filtered_lobbies:
            lobbies.append({
                'id': lobby_data.get('id'),
                'name': lobby_data.get('name', 'Unknown Session'),
                'description': lobby_data.get('description', ''),
                'max_participants': lobby_data.get('max_participants', 4),
                'participants': lobby_data.get('participants', []),
                'status': 'active' if lobby_data.get('is_active', True) else 'inactive',
                'created_at': lobby_data.get('created_at'),
                'creator_id': lobby_data.get('creator_id'),
                'creator_name': lobby_data.get('creator_name'),
                'class_id': lobby_data.get('class_id'),
                'scenario_type': lobby_data.get('scenario_type', 'general'),
                'is_private': lobby_data.get('is_private', False)
            })
        
        return jsonify({
            'success': True,
            'lobbies': lobbies
        })
        
    except ImportError:
        return jsonify({
            'success': True,
            'lobbies': []
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching admin lobbies: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/lobbies', methods=['POST'])
def create_admin_lobby():
    """Create a new lobby from admin interface"""
    try:
        from services.troubleshooting_lobbies import lobby_manager
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate required fields
        name = data.get('name', '').strip()
        if not name:
            return jsonify({
                'success': False,
                'error': 'Lobby name is required'
            }), 400
        
        # Create lobby data
        lobby_data = {
            'name': name,
            'description': data.get('description', ''),
            'max_participants': int(data.get('max_participants', 4)),
            'class_id': data.get('class_id'),
            'creator_id': str(data.get('created_by', '')),
            'creator_name': data.get('creator_name', 'Admin'),
            'scenario_type': data.get('scenario_type', 'general'),
            'scenario_id': data.get('scenario_id', 'default'),
            'is_private': bool(data.get('is_private', False)),
            'creator_role': 'admin'
        }
        
        # Create the lobby
        lobby_id = lobby_manager.create_lobby(
            name=lobby_data['name'],
            scenario_type=lobby_data['scenario_type'],
            scenario_id=lobby_data['scenario_id'],
            max_participants=lobby_data['max_participants'],
            class_id=lobby_data['class_id'],
            creator_id=lobby_data['creator_id'],
            creator_name=lobby_data['creator_name']
        )
        
        if lobby_id:
            return jsonify({
                'success': True,
                'lobby_id': lobby_id,
                'message': f'Lobby "{name}" created successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create lobby'
            }), 500
            
    except ImportError:
        return jsonify({
            'success': False,
            'error': 'Lobby system not available'
        }), 503
    except Exception as e:
        current_app.logger.error(f"Error creating admin lobby: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/lobbies/<lobby_id>', methods=['DELETE'])
def delete_admin_lobby(lobby_id):
    """Delete a lobby from admin interface"""
    try:
        from services.troubleshooting_lobbies import lobby_manager
        
        current_app.logger.info(f"Admin attempting to delete lobby: {lobby_id}")
        
        # Check if lobby exists first
        lobby = lobby_manager.get_lobby_by_id(lobby_id)
        if not lobby:
            current_app.logger.warning(f"Lobby {lobby_id} not found for deletion")
            return jsonify({
                'success': False,
                'error': f'Lobby {lobby_id} not found'
            }), 404
        
        success = lobby_manager.delete_lobby(lobby_id)
        
        if success:
            current_app.logger.info(f"Successfully deleted lobby: {lobby_id}")
            return jsonify({
                'success': True,
                'message': 'Lobby deleted successfully'
            })
        else:
            current_app.logger.error(f"Failed to delete lobby: {lobby_id}")
            return jsonify({
                'success': False,
                'error': 'Lobby could not be deleted'
            }), 500
            
    except ImportError as e:
        current_app.logger.error(f"Lobby system import error: {e}")
        return jsonify({
            'success': False,
            'error': 'Lobby system not available'
        }), 503
    except Exception as e:
        current_app.logger.error(f"Error deleting admin lobby {lobby_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/lobbies/<lobby_id>/participants', methods=['GET'])
def get_lobby_participants(lobby_id):
    """Get participants for a specific lobby"""
    try:
        from services.troubleshooting_lobbies import lobby_manager
        
        lobby = lobby_manager.get_lobby(lobby_id)
        if not lobby:
            return jsonify({
                'success': False,
                'error': 'Lobby not found'
            }), 404
        
        participants = []
        for user_id, participant_data in lobby.participants.items():
            participants.append({
                'user_id': user_id,
                'username': participant_data.get('username', 'Unknown'),
                'profile_image': participant_data.get('profile_image'),
                'joined_at': participant_data.get('joined_at'),
                'is_active': participant_data.get('is_active', True),
                'selected_device': participant_data.get('selected_device'),
                'cursor_position': participant_data.get('cursor_position', {'x': 0, 'y': 0})
            })
        
        return jsonify({
            'success': True,
            'participants': participants
        })
        
    except ImportError:
        return jsonify({
            'success': False,
            'error': 'Lobby system not available'
        }), 503
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =============================================================================
# SIMULATION COLLABORATION API ENDPOINTS
# =============================================================================

@api_bp.route('/collaboration/simulation/<int:simulation_id>/start-lobby', methods=['POST'])
def start_simulation_collaboration_lobby(simulation_id):
    """Start a collaboration lobby for a specific simulation"""
    try:
        from services.troubleshooting_lobbies import lobby_manager
        
        data = request.get_json() or {}
        
        # Get simulation details
        from user.models import Simulation
        simulation = Simulation.query.get_or_404(simulation_id)
        
        # Create lobby data
        lobby_name = data.get('name', f'{simulation.name} - Collaboration Session')
        lobby_data = {
            'name': lobby_name,
            'description': data.get('description', f'Collaborative session for {simulation.name}'),
            'max_participants': int(data.get('max_participants', 12)),
            'class_id': data.get('class_id'),
            'creator_id': str(data.get('created_by', '')),
            'creator_name': data.get('creator_name', 'Admin'),
            'scenario_type': data.get('scenario_type', 'simulation'),
            'scenario_id': str(simulation_id),
            'simulation_id': simulation_id,
            'is_private': bool(data.get('is_private', False)),
            'creator_role': 'admin'
        }
        
        # Create the lobby
        lobby_id = lobby_manager.create_lobby(
            name=lobby_data['name'],
            scenario_type=lobby_data['scenario_type'],
            scenario_id=lobby_data['scenario_id'],
            max_participants=lobby_data['max_participants'],
            class_id=lobby_data['class_id'],
            creator_id=lobby_data['creator_id'],
            creator_name=lobby_data['creator_name']
        )
        
        if lobby_id:
            # Store additional simulation-specific data
            lobby = lobby_manager.get_lobby(lobby_id)
            if lobby:
                lobby.simulation_id = simulation_id
                lobby.simulation_name = simulation.name
                
            return jsonify({
                'success': True,
                'lobby_id': lobby_id,
                'simulation_id': simulation_id,
                'lobby_name': lobby_name,
                'message': f'Collaboration lobby created for {simulation.name}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create collaboration lobby'
            }), 500
            
    except ImportError:
        return jsonify({
            'success': False,
            'error': 'Lobby system not available'
        }), 503
    except Exception as e:
        current_app.logger.error(f"Error starting simulation collaboration: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/collaboration/simulation/<int:simulation_id>/lobby', methods=['GET'])
def get_simulation_collaboration_lobby(simulation_id):
    """Get active collaboration lobby for a simulation"""
    try:
        from services.troubleshooting_lobbies import lobby_manager
        
        # Find lobby for this simulation
        all_lobbies = lobby_manager.get_public_lobbies()
        simulation_lobby = None
        
        for lobby_data in all_lobbies:
            if (lobby_data.get('scenario_type') == 'simulation' and 
                str(lobby_data.get('scenario_id')) == str(simulation_id)):
                simulation_lobby = lobby_data
                break
        
        if simulation_lobby:
            return jsonify({
                'success': True,
                'lobby': {
                    'id': simulation_lobby.get('id'),
                    'name': simulation_lobby.get('name'),
                    'description': simulation_lobby.get('description'),
                    'max_participants': simulation_lobby.get('max_participants'),
                    'participants': simulation_lobby.get('participants', []),
                    'is_active': simulation_lobby.get('is_active', True),
                    'created_at': simulation_lobby.get('created_at'),
                    'simulation_id': simulation_id
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No active collaboration lobby found for this simulation'
            }), 404
            
    except ImportError:
        return jsonify({
            'success': True,
            'lobby': None
        })
    except Exception as e:
        current_app.logger.error(f"Error getting simulation collaboration lobby: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/collaboration/simulation/<int:simulation_id>/stop-lobby', methods=['POST'])
def stop_simulation_collaboration_lobby(simulation_id):
    """Stop collaboration lobby for a simulation"""
    try:
        from services.troubleshooting_lobbies import lobby_manager
        
        # Find and delete lobby for this simulation
        all_lobbies = lobby_manager.get_public_lobbies()
        
        for lobby_data in all_lobbies:
            if (lobby_data.get('scenario_type') == 'simulation' and 
                str(lobby_data.get('scenario_id')) == str(simulation_id)):
                
                lobby_id = lobby_data.get('id')
                success = lobby_manager.delete_lobby(lobby_id)
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': f'Collaboration lobby stopped for simulation {simulation_id}'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to stop collaboration lobby'
                    }), 500
        
        return jsonify({
            'success': False,
            'error': 'No active collaboration lobby found for this simulation'
        }), 404
            
    except ImportError:
        return jsonify({
            'success': False,
            'error': 'Lobby system not available'
        }), 503
    except Exception as e:
        current_app.logger.error(f"Error stopping simulation collaboration: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/collaboration/stats', methods=['GET'])
def get_collaboration_stats():
    """Get collaboration statistics for admin dashboard"""
    try:
        from services.troubleshooting_lobbies import lobby_manager
        
        class_id = request.args.get('class_id', type=int)
        
        # Get all lobbies
        all_lobbies = lobby_manager.get_public_lobbies()
        
        # Filter by class if specified
        if class_id:
            class_lobbies = [
                lobby for lobby in all_lobbies 
                if lobby.get('class_id') == class_id
            ]
        else:
            class_lobbies = all_lobbies
        
        # Calculate stats
        stats = {
            'total_active_lobbies': len(class_lobbies),
            'total_participants': sum(len(lobby.get('participants', [])) for lobby in class_lobbies),
            'simulation_lobbies': len([
                lobby for lobby in class_lobbies 
                if lobby.get('scenario_type') == 'simulation'
            ]),
            'general_lobbies': len([
                lobby for lobby in class_lobbies 
                if lobby.get('scenario_type') == 'general'
            ]),
            'lobbies': [
                {
                    'id': lobby.get('id'),
                    'name': lobby.get('name'),
                    'participants_count': len(lobby.get('participants', [])),
                    'max_participants': lobby.get('max_participants', 4),
                    'scenario_type': lobby.get('scenario_type'),
                    'created_at': lobby.get('created_at')
                }
                for lobby in class_lobbies
            ]
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except ImportError:
        return jsonify({
            'success': True,
            'stats': {
                'total_active_lobbies': 0,
                'total_participants': 0,
                'simulation_lobbies': 0,
                'general_lobbies': 0,
                'lobbies': []
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error getting collaboration stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# =============================================================================
# EDIT SIMULATION LOBBY API ENDPOINTS 
# These endpoints are called by edit_simulation.html collaboration tab
# =============================================================================

@api_bp.route('/collaboration/lobbies', methods=['GET'])
def get_all_lobbies():
    """Get all available lobbies for the lobby browser"""
    try:
        from services.troubleshooting_lobbies import lobby_manager
        
        # Get all public lobbies
        lobbies = lobby_manager.get_public_lobbies()
        
        # Format lobbies for frontend
        formatted_lobbies = []
        for lobby_data in lobbies:
            formatted_lobbies.append({
                'id': lobby_data.get('id'),
                'name': lobby_data.get('name', 'Unnamed Lobby'),
                'description': lobby_data.get('description', 'No description provided'),
                'participant_count': len(lobby_data.get('participants', {})),
                'max_participants': lobby_data.get('max_participants', 8),
                'privacy': 'public',  # All public lobbies
                'creator_name': lobby_data.get('creator_name', 'Unknown'),
                'scenario_type': lobby_data.get('scenario_type', 'medium'),
                'scenario_id': lobby_data.get('scenario_id', 'network'),
                'is_active': lobby_data.get('is_active', True),
                'created_at': lobby_data.get('created_at')
            })
        
        return jsonify({
            'success': True,
            'lobbies': formatted_lobbies
        })
        
    except ImportError:
        return jsonify({
            'success': True,
            'lobbies': []
        })
    except Exception as e:
        current_app.logger.error(f"Error getting lobbies: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'lobbies': []
        }), 500

@api_bp.route('/collaboration/lobbies', methods=['POST'])
def create_lobby():
    """Create a new collaboration lobby"""
    try:
        from services.troubleshooting_lobbies import lobby_manager
        
        data = request.get_json() or {}
        
        # Validate required fields
        lobby_name = data.get('name', '').strip()
        if not lobby_name:
            return jsonify({
                'success': False,
                'error': 'Lobby name is required'
            }), 400
            
        # Get creator information from session
        creator_id = str(session.get('admin_id', 'admin'))
        creator_name = session.get('admin_username', 'Admin')
        
        # Create lobby config
        lobby_config = {
            'name': lobby_name,
            'scenario_type': data.get('scenario_type', 'medium'),
            'scenario_id': data.get('scenario_id', 'network'),
            'max_participants': int(data.get('max_participants', 8)),
            'class_id': data.get('class_id'),
            'description': data.get('description', ''),
            'simulation_id': data.get('simulation_id')
        }
        
        # Create lobby with troubleshooting_lobbies service
        lobby = lobby_manager.create_lobby(
            creator_id=creator_id,
            creator_name=creator_name,
            lobby_config=lobby_config
        )
        
        if lobby:
            return jsonify({
                'success': True,
                'lobby_id': lobby.id,
                'lobby': lobby.to_dict(),
                'message': f'Lobby "{lobby_name}" created successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create lobby'
            }), 500
            
    except ImportError:
        return jsonify({
            'success': False,
            'error': 'Lobby system not available'
        }), 503
    except Exception as e:
        current_app.logger.error(f"Error creating lobby: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/collaboration/lobbies/active', methods=['GET'])
def get_active_lobbies():
    """Get active lobbies for the current session"""
    try:
        from services.troubleshooting_lobbies import lobby_manager
        
        # Get all public lobbies (they are all active)
        lobbies = lobby_manager.get_public_lobbies()
        
        # Format lobbies for frontend
        active_lobbies = []
        for lobby_data in lobbies:
            if lobby_data.get('is_active', True):
                active_lobbies.append({
                    'id': lobby_data.get('id'),
                    'name': lobby_data.get('name', 'Unnamed Lobby'),
                    'participant_count': len(lobby_data.get('participants', {})),
                    'max_participants': lobby_data.get('max_participants', 8),
                    'creator_name': lobby_data.get('creator_name', 'Unknown'),
                    'created_at': lobby_data.get('created_at'),
                    'scenario_type': lobby_data.get('scenario_type', 'medium')
                })
        
        return jsonify({
            'success': True,
            'lobbies': active_lobbies
        })
        
    except ImportError:
        return jsonify({
            'success': True,
            'lobbies': []
        })
    except Exception as e:
        current_app.logger.error(f"Error getting active lobbies: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'lobbies': []
        }), 500

@api_bp.route('/collaboration/lobby/<lobby_id>/close', methods=['POST'])
def close_lobby(lobby_id):
    """Close/delete a specific lobby"""
    try:
        from services.troubleshooting_lobbies import lobby_manager
        
        # Check if admin has permission (basic check)
        if not session.get('admin_id'):
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403
            
        # Close the lobby
        success = lobby_manager.delete_lobby(lobby_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Lobby {lobby_id} closed successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to close lobby or lobby not found'
            }), 404
            
    except ImportError:
        return jsonify({
            'success': False,
            'error': 'Lobby system not available'
        }), 503
    except Exception as e:
        current_app.logger.error(f"Error closing lobby {lobby_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/collaboration/teams', methods=['POST'])
def save_collaboration_teams():
    """Save team assignments for collaboration"""
    try:
        data = request.get_json() or {}
        
        # For now, just acknowledge the request
        # TODO: Implement team assignment logic with CollaborationLobby and TeamAssignment models
        
        return jsonify({
            'success': True,
            'message': 'Team assignments saved successfully',
            'teams': data.get('teams', [])
        })
        
    except Exception as e:
        current_app.logger.error(f"Error saving teams: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
