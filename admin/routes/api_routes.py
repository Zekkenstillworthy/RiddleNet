from flask import Blueprint, jsonify, request, render_template
from admin import db
from admin.models.class_model import Class
from admin.models.question_group import QuestionGroup
from admin.models.module import Module
import random
import string
from datetime import datetime

api_bp = Blueprint('admin_api', __name__, url_prefix='/admin/api')

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
@api_bp.route('/deadlines', methods=['GET'])
def get_deadlines():
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
