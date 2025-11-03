from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response, make_response
from flask_login import login_required, current_user
from utils.auth_decorators import instructor_required
from instructor.models.class_model import Class
from instructor.models.question_group import QuestionGroup
from user.models.user import User  # Import User model for the relationship
from user.models.score import Score  # Import Score model for performance data
from __init__ import db
from datetime import datetime
import json
import random
import string
import csv
import io
from instructor.services.class_template_generator import ClassTemplateGenerator
from instructor.services.enhanced_class_template_generator import enhanced_template_generator
from instructor.services.dynamic_route_registry import route_registry

# Create a blueprint for class related routes
class_controller = Blueprint('class_controller', __name__, url_prefix='/admin')

# Initialize the template generators
template_generator = ClassTemplateGenerator()
enhanced_generator = enhanced_template_generator

@class_controller.route('/classes')
@instructor_required
def index():
    """Display the class management page"""
    print("=" * 80)
    print("[DEBUG] CLASS CONTROLLER INDEX: Route accessed at /instructor/classes")
    print(f"[DEBUG] Current user: {current_user.username if current_user.is_authenticated else 'Not authenticated'}")
    print(f"[DEBUG] User type: {type(current_user)}")
    from flask import session, request
    print(f"[DEBUG] Auth namespace: {session.get('auth_namespace', 'unknown')}")
    print(f"[DEBUG] Referrer: {request.referrer}")
    print("=" * 80)
    
    # Show only classes owned by this admin unless super_admin
    from instructor.models.class_model import Class
    try:
        if hasattr(current_user, 'role') and current_user.role == 'super_admin':
            classes = Class.query.order_by(Class.name).all()
        else:
            classes = Class.query.filter_by(created_by=getattr(current_user, 'id', None)).order_by(Class.name).all()
    except Exception:
        # Fallback - show nothing if there's a DB issue
        classes = []

    return render_template('instructor/class.html', active_page='all_classes', classes=classes)

@class_controller.route('/class/<int:class_id>/content-manager')
@instructor_required
def content_manager(class_id):
    """Redirect to the class content manager"""
    # Import here to avoid circular imports
    from instructor.controllers.class_content_controller import class_content_controller_old

    # Ownership check: allow if creator or super_admin
    cls = Class.query.get_or_404(class_id)
    if not (hasattr(current_user, 'role') and current_user.role == 'super_admin') and cls.created_by != getattr(current_user, 'id', None):
        flash('You do not have permission to access that class', 'error')
        return redirect(url_for('class_controller.index'))

    return redirect(url_for('class_content_controller_old.manage_content', class_id=class_id))

@class_controller.route('/api/classes/<int:class_id>/export/csv', methods=['GET'])
@login_required
def export_class_csv(class_id):
    """Export class data including students and performance to CSV"""
    try:
        cls = Class.query.get_or_404(class_id)
        # Ownership check
        if not (hasattr(current_user, 'role') and current_user.role == 'super_admin') and cls.created_by != getattr(current_user, 'id', None):
            return jsonify({'error': 'Permission denied'}), 403
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write class information header
        writer.writerow(['Class Report - ' + cls.name])
        writer.writerow(['Generated on:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])  # Empty row
        
        # Class details section
        writer.writerow(['Class Information'])
        writer.writerow(['Class Name', cls.name])
        writer.writerow(['Section', cls.section or 'N/A'])
        writer.writerow(['Class Code', cls.code])
        writer.writerow(['Description', cls.description or 'N/A'])
        writer.writerow(['Start Date', cls.start_date.strftime('%Y-%m-%d') if cls.start_date else 'N/A'])
        writer.writerow(['End Date', cls.end_date.strftime('%Y-%m-%d') if cls.end_date else 'N/A'])
        writer.writerow(['Max Students', cls.max_students])
        writer.writerow(['Current Students', cls.students.count() if cls.students else 0])
        writer.writerow(['Status', cls.status])
        writer.writerow([])  # Empty row
        
        # Quiz section
        writer.writerow(['Assigned Quiz'])
        writer.writerow(['Group ID', 'Group Name', 'Question Count'])
        if cls.question_groups:
            for group in cls.question_groups:
                question_count = len(group.questions) if hasattr(group, 'questions') and group.questions else 0
                writer.writerow([group.id, group.name, question_count])
        else:
            writer.writerow(['N/A', 'No Quiz assigned', '0'])
        writer.writerow([])  # Empty row
        
        # Students section
        writer.writerow(['Enrolled Students'])
        writer.writerow(['Student ID', 'Username', 'Email', 'Total Scores', 'Average Score', 'Best Score'])
        
        if cls.students:
            for student in cls.students.all():
                # Get student's scores for this class or related assessments
                student_scores = Score.query.filter_by(user_id=student.id).all()
                
                total_scores = len(student_scores)
                if student_scores:
                    scores_values = [score.score for score in student_scores if score.score is not None]
                    avg_score = sum(scores_values) / len(scores_values) if scores_values else 0
                    best_score = max(scores_values) if scores_values else 0
                else:
                    avg_score = 0
                    best_score = 0
                
                writer.writerow([
                    student.id,
                    student.username,
                    student.email if hasattr(student, 'email') else 'N/A',
                    total_scores,
                    f"{avg_score:.1f}%" if avg_score > 0 else "N/A",
                    f"{best_score:.1f}%" if best_score > 0 else "N/A"
                ])
        else:
            writer.writerow(['N/A', 'No students enrolled', 'N/A', 'N/A', 'N/A', 'N/A'])
        
        # Performance summary
        writer.writerow([])
        writer.writerow(['Performance Summary'])
        if cls.students:
            all_scores = []
            for student in cls.students.all():
                student_scores = Score.query.filter_by(user_id=student.id).all()
                for score in student_scores:
                    if score.score is not None:
                        all_scores.append(score.score)
            
            if all_scores:
                writer.writerow(['Class Average', f"{sum(all_scores) / len(all_scores):.1f}%"])
                writer.writerow(['Highest Score', f"{max(all_scores):.1f}%"])
                writer.writerow(['Lowest Score', f"{min(all_scores):.1f}%"])
                writer.writerow(['Total Assessments Taken', len(all_scores)])
            else:
                writer.writerow(['Class Average', 'No scores recorded'])
        else:
            writer.writerow(['Class Average', 'No students enrolled'])
        
        # Prepare the response
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename=class_{cls.code}_{cls.name}_report.csv'
        response.headers['Content-Type'] = 'text/csv'
        
        return response
        
    except Exception as e:
        return jsonify({"error": f"Failed to export class data: {str(e)}"}), 500

@class_controller.route('/api/classes/<int:class_id>/export/pdf', methods=['GET'])
@login_required
def export_class_pdf(class_id):
    """Export class data to PDF (placeholder for now)"""
    try:
        cls = Class.query.get_or_404(class_id)
        
        # For now, return a message indicating PDF functionality is coming soon
        # In a full implementation, you would use libraries like reportlab or weasyprint
        return jsonify({
            "message": "PDF export functionality is coming soon!",
            "suggestion": "Please use CSV export for now",
            "classInfo": {
                "name": cls.name,
                "code": cls.code,
                "students": cls.students.count() if cls.students else 0
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to export PDF: {str(e)}"}), 500

@class_controller.route('/api/classes', methods=['GET'])
@login_required
def get_classes():
    """API endpoint to retrieve all classes"""
    try:
        # Only return classes owned by current admin unless super_admin
        if hasattr(current_user, 'role') and current_user.role == 'super_admin':
            classes = Class.query.all()
        else:
            classes = Class.query.filter_by(created_by=getattr(current_user, 'id', None)).all()
        
        # Convert classes to dictionary format for JSON response
        result = []
        for cls in classes:
            # Safely get student count
            try:
                student_count = cls.students.count() if hasattr(cls, 'students') and cls.students else 0
            except Exception:
                student_count = 0
            
            result.append({
                'id': cls.id,
                'name': cls.name or '',
                'section': cls.section or '',
                'code': cls.code or '',
                'students': student_count,
                'maxStudents': cls.max_students or 0,
                'startDate': cls.start_date.isoformat() if cls.start_date else None,
                'endDate': cls.end_date.isoformat() if cls.end_date else None,
                'status': cls.status or 'inactive'
            })
            
        return jsonify(result)
    except Exception as e:
        print(f"Error fetching classes: {e}")
        # Return empty list instead of error to prevent frontend crash
        return jsonify([])
    

@class_controller.route('/api/classes', methods=['POST'])
@login_required
def create_class():
    """API endpoint to create a new class"""
    try:
        data = request.json
        
        # Check if code already exists
        existing_class = Class.query.filter_by(code=data.get('code')).first()
        if existing_class:
            return jsonify({
                "error": f"Class code '{data.get('code')}' already exists. Please use a different code."
            }), 400
        
        # Parse dates (frontend sends YYYY-MM-DD format)
        start_date = datetime.strptime(data.get('startDate'), '%Y-%m-%d').date() if data.get('startDate') else None
        end_date = datetime.strptime(data.get('endDate'), '%Y-%m-%d').date() if data.get('endDate') else None
        
        # Create new class
        new_class = Class(
            name=data.get('name'),
            section=data.get('section'),
            code=data.get('code'),
            description=data.get('description'),
            start_date=start_date,
            end_date=end_date,
            max_students=data.get('maxStudents'),
            status=data.get('status', 'active'),
            created_by=getattr(current_user, 'id', None)
        )
        
        # Add Quiz if provided
        if 'questionGroups' in data and data['questionGroups']:
            question_groups = QuestionGroup.query.filter(
                QuestionGroup.id.in_(data['questionGroups'])
            ).all()
            for qg in question_groups:
                new_class.question_groups.append(qg)
        
        # Save to database
        db.session.add(new_class)
        db.session.commit()
        
        # CHECK TEMPLATE CONFIGURATION
        from instructor.config.class_template_config import should_use_universal_template, get_template_config
        
        config = get_template_config()
        
        if should_use_universal_template():
            # UNIVERSAL TEMPLATE SYSTEM - No need to generate class-specific templates
            # All classes now use the dynamic universal template (dynamic_class_universal.html)
            try:
                print(f"[OK] Class {new_class.id} created - using universal template system")
                print(f"   Template: {config['universal_template']}")
                print(f"   Route: /class/{new_class.id} (handled by universal_class_routes.py)")
                print(f"   Mode: Universal template only (configured)")
                
                # Optional: Create dashboard integration for admin features only
                try:
                    integration_info = enhanced_generator.create_class_dashboard_integration(new_class)
                except Exception as e:
                    print(f"   Dashboard integration skipped: {e}")
                
                flash(f"Class created successfully! Using universal dynamic template system.", 'success')
            except Exception as e:
                flash(f"Class created successfully! Universal template system active.", 'success')
        else:
            # LEGACY SYSTEM - Generate class-specific templates (if configured)
            try:
                print(f"[WARNING] Class {new_class.id} created - using legacy template generation")
                generation_result = enhanced_generator.generate_all_class_resources(new_class.id)
                route_registry.register_class_routes(new_class.id)
                integration_info = enhanced_generator.create_class_dashboard_integration(new_class)
                
                flash(f"Class created successfully! Class-specific template generated: {generation_result['template']}", 'success')
            except Exception as e:
                flash(f"Class created but template generation failed: {str(e)}", 'warning')
        
        return jsonify({
            "success": True, 
            "message": "Class created successfully with universal dynamic template!",
            "classId": new_class.id,
            "templateSystem": "universal",
            "templateFile": "dynamic_class_universal.html",
            "dashboardUrl": f"/class/{new_class.id}/",
            "universalFeatures": True
        }), 201
    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        if "UNIQUE constraint failed: classes.code" in error_msg:
            error_msg = f"Class code '{data.get('code')}' already exists. Please use a different code."
        return jsonify({"error": error_msg}), 500

@class_controller.route('/api/classes/<int:class_id>', methods=['GET'])
@login_required
def get_class(class_id):
    """API endpoint to retrieve a specific class details"""
    try:
        cls = Class.query.get_or_404(class_id)
        # Ownership check
        if not (hasattr(current_user, 'role') and current_user.role == 'super_admin') and cls.created_by != getattr(current_user, 'id', None):
            return jsonify({'error': 'Permission denied'}), 403
        class_data = cls.to_dict()
        # Ensure studentCount is correctly provided
        if 'studentCount' not in class_data or class_data['studentCount'] is None:
            class_data['studentCount'] = cls.students.count() if cls.students else 0
        return jsonify(class_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@class_controller.route('/api/classes/<int:class_id>', methods=['PUT'])
@login_required
def update_class(class_id):
    """API endpoint to update a class"""
    try:
        cls = Class.query.get_or_404(class_id)
        data = request.json
        
        # Check if code is being changed and verify it's unique
        if 'code' in data and data['code'] != cls.code:
            existing_class = Class.query.filter_by(code=data['code']).first()
            if existing_class and existing_class.id != class_id:
                return jsonify({
                    "error": f"Class code '{data['code']}' already exists. Please use a different code."
                }), 400
        
        # Update fields if provided
        if 'name' in data:
            cls.name = data['name']
        if 'section' in data:
            cls.section = data['section']
        if 'code' in data:
            cls.code = data['code']
        if 'description' in data:
            cls.description = data['description']
        if 'startDate' in data:
            cls.start_date = datetime.strptime(data['startDate'], '%Y-%m-%d').date() if data['startDate'] else None
        if 'endDate' in data:
            cls.end_date = datetime.strptime(data['endDate'], '%Y-%m-%d').date() if data['endDate'] else None
        if 'maxStudents' in data:
            cls.max_students = data['maxStudents']
        if 'status' in data:
            cls.status = data['status']
            
        # Set updated_at explicitly
        cls.updated_at = datetime.utcnow()
            
        # Update Quiz if provided
        if 'questionGroups' in data:
            # Clear existing Quiz
            cls.question_groups.clear()
            # Add new Quiz
            question_groups = QuestionGroup.query.filter(
                QuestionGroup.id.in_(data['questionGroups'])
            ).all()
            for qg in question_groups:
                cls.question_groups.append(qg)
        
        db.session.commit()
        
        # Also update template if Quiz changed
        try:
            if 'questionGroups' in data:
                generation_result = template_generator.regenerate_class_resources(class_id)
                flash(f"Class updated and template regenerated!", 'success')
        except Exception as e:
            print(f"Warning: Could not regenerate template: {e}")
        
        return jsonify({"success": True, "message": "Class updated successfully!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@class_controller.route('/api/classes/<int:class_id>/regenerate-template', methods=['POST'])
@login_required
def regenerate_class_template(class_id):
    """API endpoint to regenerate template for a class - respects configuration"""
    try:
        class_obj = Class.query.get_or_404(class_id)
        
        # CHECK TEMPLATE CONFIGURATION
        from instructor.config.class_template_config import should_use_universal_template, get_template_config
        
        config = get_template_config()
        
        if should_use_universal_template():
            # UNIVERSAL TEMPLATE SYSTEM - No regeneration needed
            # All classes use dynamic_class_universal.html which adapts automatically
            print(f"[OK] Class {class_id} template refresh requested")
            print(f"   Using universal template: {config['universal_template']}")
            print(f"   No regeneration needed - template adapts dynamically")
            print(f"   Mode: Universal template only (configured)")
            
            # Optional: Update dashboard integration for admin features
            try:
                integration_info = enhanced_generator.create_class_dashboard_integration(class_obj)
            except Exception as e:
                integration_info = {"status": "universal_system_active"}
            
            return jsonify({
                "success": True, 
                "message": "Using universal template system - no regeneration needed!",
                "templateSystem": "universal",
                "templateFile": config['universal_template'],
                "universalFeatures": True,
                "dashboardUrl": f"/class/{class_id}/",
                "note": "All classes automatically use the dynamic universal template"
            })
        else:
            # LEGACY SYSTEM - Regenerate class-specific templates
            print(f"[WARNING] Class {class_id} using legacy template regeneration")
            generation_result = enhanced_generator.regenerate_class_resources(class_id)
            route_registry.refresh_class_routes(class_id)
            integration_info = enhanced_generator.create_class_dashboard_integration(class_obj)
            
            return jsonify({
                "success": True, 
                "message": "Class-specific template regenerated successfully!",
                "template": generation_result['template'],
                "routes": generation_result['routes'],
                "enhancedFeatures": True,
                "dashboardUrl": f"/class/{class_id}/",
                "staticIntegrations": integration_info.get('static_integrations', [])
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@class_controller.route('/api/classes/<int:class_id>', methods=['DELETE'])
@login_required
def delete_class(class_id):
    """API endpoint to delete a class"""
    try:
        cls = Class.query.get_or_404(class_id)
        
        # Clean up generated resources
        try:
            template_generator.cleanup_class_resources(class_id)
        except Exception as e:
            print(f"Warning: Could not clean up class resources: {e}")
        
        db.session.delete(cls)
        db.session.commit()
        
        return jsonify({"success": True, "message": "Class and its resources deleted successfully!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@class_controller.route('/api/generate-class-code', methods=['GET'])
@login_required
def generate_class_code():
    """API endpoint to generate a unique class code"""
    try:
        # Generate a random 6-character code (letters and numbers)
        chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'  # Removed confusing characters like 0, O, 1, I
        
        # Keep generating until we find a unique code
        max_attempts = 100  # Prevent infinite loop
        attempts = 0
        code = None
        
        while attempts < max_attempts:
            code = ''.join(random.choice(chars) for _ in range(6))
            
            # Check if code already exists in database
            try:
                existing = Class.query.filter_by(code=code).first()
                if not existing:
                    break
            except Exception as db_error:
                print(f"Database error checking code: {db_error}")
                # If DB check fails, just return the generated code
                break
            attempts += 1
                
        if attempts >= max_attempts:
            return jsonify({"error": "Unable to generate unique code"}), 500
                
        return jsonify({"code": code})
    except Exception as e:
        print(f"Error generating class code: {e}")
        # Return a fallback code
        fallback_code = ''.join(random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(6))
        return jsonify({"code": fallback_code})

@class_controller.route('/student-classes')
@login_required
def student_classes():
    """Display the student class enrollment management page"""
    return render_template('instructor/student_classes.html', active_page='student_classes')

@class_controller.route('/api/student/classes', methods=['GET'])
@login_required
def get_student_classes():
    """API endpoint to retrieve all classes that the current instructor user can view"""
    try:
        # Only return classes owned by current admin unless super_admin
        if hasattr(current_user, 'role') and current_user.role == 'super_admin':
            classes = Class.query.all()
        else:
            classes = Class.query.filter_by(created_by=getattr(current_user, 'id', None)).all()
        
        # Convert classes to dictionary format for JSON response
        result = []
        for cls in classes:
            result.append({
                'id': cls.id,
                'name': cls.name,
                'section': cls.section,
                'code': cls.code,
                'description': cls.description,
                'startDate': cls.start_date.isoformat() if cls.start_date else None,
                'endDate': cls.end_date.isoformat() if cls.end_date else None,
                'status': cls.status,
                'studentCount': cls.students.count() if cls.students else 0,
                'maxStudents': cls.max_students
            })
            
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@class_controller.route('/api/classes/<int:class_id>/students', methods=['GET'])
@login_required
def get_class_students(class_id):
    """API endpoint to retrieve all students enrolled in a specific class"""
    try:
        cls = Class.query.get_or_404(class_id)
        students = []
        
        # Use .all() to get actual student objects from dynamic relationship
        for student in cls.students.all():
            students.append({
                'id': student.id,
                'username': student.username,
                'email': student.email if hasattr(student, 'email') else None,
                # Join date and status would be in the association table, but we don't have direct access
                # so returning placeholders
                'joinDate': None,
                'status': 'active'
            })
            
        return jsonify({
            'classId': cls.id,
            'className': cls.name,
            'students': students
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@class_controller.route('/api/classes/<int:class_id>/students/<int:student_id>', methods=['DELETE'])
@login_required
def remove_student_from_class(class_id, student_id):
    """API endpoint to remove a student from a class"""
    try:
        cls = Class.query.get_or_404(class_id)
        
        # Find the student - using the imported User model
        student = User.query.get_or_404(student_id)
        
        # Check if student is enrolled using the dynamic relationship
        if not cls.students.filter_by(id=student_id).first():
            return jsonify({"error": "Student is not enrolled in this class"}), 400
        
        # Remove the student from the class using the association table
        cls.students.remove(student)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Student {student.username} removed from class successfully!"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@class_controller.route('/class/<int:class_id>/overview')
@login_required
def class_overview(class_id):
    """Display class overview and content editing page for admin"""
    try:
        print(f"Loading class overview for class ID: {class_id}")
        
        # Get the class details
        cls = Class.query.get_or_404(class_id)
        print(f"Found class: {cls.name}")
        
        # Get enrolled students
        students = cls.students.all() if cls.students else []
        print(f"Found {len(students)} students")
        
        # Get Quiz assigned to this class
        question_groups = cls.question_groups.all() if cls.question_groups else []
        print(f"Found {len(question_groups)} Quiz")
        
        # Get class performance data
        performance_data = []
        if students:
            for student in students:
                student_scores = Score.query.filter_by(user_id=student.id).all()
                if student_scores:
                    scores_values = [score.score for score in student_scores if score.score is not None]
                    avg_score = sum(scores_values) / len(scores_values) if scores_values else 0
                    best_score = max(scores_values) if scores_values else 0
                    total_assessments = len(scores_values)
                else:
                    avg_score = 0
                    best_score = 0
                    total_assessments = 0
                
                performance_data.append({
                    'student': student,
                    'avg_score': avg_score,
                    'best_score': best_score,
                    'total_assessments': total_assessments
                })
        
        # Get available Quiz for assignment
        all_question_groups = QuestionGroup.query.all()
        available_question_groups = [qg for qg in all_question_groups if qg not in question_groups]
        
        print(f"Rendering template with class data")
        return render_template('instructor/class_overview.html',
                             class_data=cls,
                             students=students,
                             question_groups=question_groups,
                             available_question_groups=available_question_groups,
                             performance_data=performance_data,
                             active_page='classes')
                             
    except Exception as e:
        error_msg = f'Error loading class overview for class {class_id}: {str(e)}'
        print(error_msg)
        import traceback
        traceback.print_exc()
        
        # Add error to flash messages
        flash(error_msg, 'error')
        
        # Return JSON response if it's an AJAX request
        if request.is_json or 'application/json' in request.headers.get('Accept', ''):
            return jsonify({"error": error_msg}), 500
            
        return redirect(url_for('class_controller.index'))

@class_controller.route('/api/classes/<int:class_id>/question-groups', methods=['POST'])
@login_required
def add_question_group_to_class(class_id):
    """Add a Quiz to a class"""
    try:
        data = request.json
        question_group_id = data.get('question_group_id')
        
        cls = Class.query.get_or_404(class_id)
        question_group = QuestionGroup.query.get_or_404(question_group_id)
        
        # Check if already assigned (idempotent)
        if question_group in cls.question_groups:
            return jsonify({
                "success": True,
                "already_assigned": True,
                "message": f"Quiz '{question_group.name}' is already assigned to this class. No changes made."
            }), 200
        
        # Add the Quiz to the class
        cls.question_groups.append(question_group)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Quiz '{question_group.name}' added to class successfully!"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@class_controller.route('/api/classes/<int:class_id>/question-groups/<int:group_id>', methods=['DELETE'])
@login_required
def remove_question_group_from_class(class_id, group_id):
    """Remove a Quiz from a class"""
    try:
        cls = Class.query.get_or_404(class_id)
        question_group = QuestionGroup.query.get_or_404(group_id)
        
        # Check if assigned
        if question_group not in cls.question_groups:
            return jsonify({"error": "Quiz is not assigned to this class"}), 400
        
        # Remove the Quiz from the class
        cls.question_groups.remove(question_group)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Quiz '{question_group.name}' removed from class successfully!"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@class_controller.route('/api/classes/<int:class_id>/students', methods=['POST'])
@login_required
def add_student_to_class_by_username(class_id):
    """Add a student to a class by username"""
    try:
        data = request.json
        username = data.get('username')
        
        if not username:
            return jsonify({"error": "Username is required"}), 400
        
        cls = Class.query.get_or_404(class_id)
        student = User.query.filter_by(username=username).first()
        
        if not student:
            return jsonify({"error": f"Student with username '{username}' not found"}), 404
        
        # Check if already enrolled
        if student in cls.students:
            return jsonify({"error": f"Student '{username}' is already enrolled in this class"}), 400
        
        # Add the student to the class
        cls.students.append(student)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Student '{username}' added to class successfully!"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
