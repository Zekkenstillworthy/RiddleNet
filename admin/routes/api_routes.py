from flask import Blueprint, jsonify, request, render_template
from flask_login import current_user
from admin import db
from admin.models.class_model import Class
from admin.models.question_group import QuestionGroup
from admin.models.module import Module
import random
import string
from datetime import datetime

api_bp = Blueprint('admin_api', __name__, url_prefix='/admin/api')

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
        
        # Check if updated_at column exists in classes table
        try:
            result = db.session.execute(text("PRAGMA table_info(classes)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'updated_at' not in columns:
                print("Missing updated_at column in classes table. Adding it...")
                # Add the missing column
                db.session.execute(text("ALTER TABLE classes ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
                db.session.commit()
                print("Successfully added updated_at column to classes table")
        except Exception as e:
            print(f"Error checking/adding updated_at column: {e}")
        
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
        
        # Add question groups if provided
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
        # For now, return empty array
        return jsonify([])
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
    """Get all question groups"""
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
        print(f"Error fetching question groups: {e}")
        return jsonify([])

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
        
        # Convert module to dict with all preview data
        module_data = {
            'id': module.id,
            'title': module.title,
            'description': module.description,
            'module_number': module.module_number,
            'estimated_duration': module.estimated_duration,
            'level': getattr(module, 'level', 'Beginner'),
            'learning_objectives': module.learning_objectives or [],
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

# Live Collaboration Monitoring API Endpoints
@api_bp.route('/collaboration/stats', methods=['GET'])
def get_collaboration_stats():
    """Get real-time collaboration statistics"""
    try:
        # Import lobby manager to get real stats
        try:
            from services.troubleshooting_lobbies import lobby_manager
            active_lobbies = lobby_manager.get_public_lobbies()
            
            active_groups = len(active_lobbies)
            total_participants = sum(len(lobby.get('participants', [])) for lobby in active_lobbies)
            
            # Calculate average duration
            avg_duration = "0m"
            if active_lobbies:
                durations = []
                for lobby_data in active_lobbies:
                    if 'created_at' in lobby_data:
                        try:
                            from datetime import datetime
                            created_time = datetime.fromisoformat(lobby_data['created_at'].replace('Z', '+00:00'))
                            duration_minutes = int((datetime.utcnow() - created_time.replace(tzinfo=None)).total_seconds() / 60)
                            durations.append(duration_minutes)
                        except:
                            pass
                if durations:
                    avg_duration = f"{int(sum(durations) / len(durations))}m"
                    
            return jsonify({
                'success': True,
                'activeGroups': active_groups,
                'totalParticipants': total_participants,
                'avgDuration': avg_duration
            })
            
        except ImportError:
            # Lobby manager not available - return zero stats
            return jsonify({
                'success': True,
                'activeGroups': 0,
                'totalParticipants': 0,
                'avgDuration': '0m'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
def get_class_grades(class_id):
    """Get comprehensive grade data for a class"""
    try:
        from admin.models.class_content import ClassAssignment
        from admin.models.assignment_submission import AssignmentSubmission
        from user.models.user import User
        from admin.models.class_model import Class
        
        # Verify class exists and user has access
        class_obj = Class.query.get_or_404(class_id)
        
        # Get all students in the class
        students = User.query.filter_by(role='student').join(
            User.enrolled_classes
        ).filter_by(id=class_id).all()
        
        # Get all assignments for this class
        assignments = ClassAssignment.query.filter_by(class_id=class_id).all()
        
        # Get all submissions for these assignments
        assignment_ids = [a.id for a in assignments]
        submissions = AssignmentSubmission.query.filter(
            AssignmentSubmission.assignment_id.in_(assignment_ids)
        ).all() if assignment_ids else []
        
        # Group submissions by student and assignment
        submission_map = {}
        grade_map = {}
        
        for submission in submissions:
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
        
        # Prepare student data
        student_data = []
        for student in students:
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
        
        # Prepare assignment data with statistics
        assignment_data = []
        for assignment in assignments:
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
        
        return jsonify(response_data)
        
    except Exception as e:
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
