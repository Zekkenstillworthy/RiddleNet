from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from admin.models.class_model import Class
from admin.models.question_group import QuestionGroup
from user.models.user import User  # Import User model for the relationship
from admin import db
from datetime import datetime
import json
import random
import string
from admin.services.class_template_generator import ClassTemplateGenerator
from admin.services.enhanced_class_template_generator import enhanced_template_generator
from admin.services.dynamic_route_registry import route_registry

# Create a blueprint for class related routes
class_controller = Blueprint('class_controller', __name__, url_prefix='/admin')

# Initialize the template generators
template_generator = ClassTemplateGenerator()
enhanced_generator = enhanced_template_generator

@class_controller.route('/classes')
@login_required
def index():
    """Display the class management page"""
    # Add debug print to verify authentication status
    print(f"User authenticated: {current_user.is_authenticated}")
    print(f"Current user: {current_user}")
    
    return render_template('admin/class.html', active_page='classes')

@class_controller.route('/api/question-groups', methods=['GET'])
@login_required
def get_question_groups():
    """API endpoint to retrieve all question groups"""
    try:
        # Get all question groups from database
        groups = QuestionGroup.query.all()
        return jsonify([{
            'id': group.id,
            'name': group.name,
            'questionCount': len(group.questions) if hasattr(group, 'questions') and group.questions else 0
        } for group in groups])
    except Exception as e:
        print(f"Error fetching question groups: {e}")
        return jsonify({"error": "Failed to fetch question groups"}), 500

@class_controller.route('/api/classes', methods=['GET'])
@login_required
def get_classes():
    """API endpoint to retrieve all classes"""
    try:
        # Get all classes from database
        classes = Class.query.all()
        
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
            status=data.get('status', 'active')
        )
        
        # Add question groups if provided
        if 'questionGroups' in data and data['questionGroups']:
            question_groups = QuestionGroup.query.filter(
                QuestionGroup.id.in_(data['questionGroups'])
            ).all()
            for qg in question_groups:
                new_class.question_groups.append(qg)
        
        # Save to database
        db.session.add(new_class)
        db.session.commit()
        
        # Generate dynamic template and routes for the new class
        try:
            # Use enhanced generator for better static template integration
            generation_result = enhanced_generator.generate_all_class_resources(new_class.id)
            
            # Register routes dynamically
            route_registry.register_class_routes(new_class.id)
            
            # Create dashboard integration
            integration_info = enhanced_generator.create_class_dashboard_integration(new_class)
            
            flash(f"Class created successfully! Enhanced template generated: {generation_result['template']}", 'success')
        except Exception as e:
            flash(f"Class created but enhanced template generation failed: {str(e)}", 'warning')
        
        return jsonify({
            "success": True, 
            "message": "Class created successfully with enhanced dynamic template!",
            "classId": new_class.id,
            "templateGenerated": True,
            "enhancedFeatures": True,
            "dashboardUrl": f"/class/{new_class.id}/"
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
            
        # Update question groups if provided
        if 'questionGroups' in data:
            # Clear existing question groups
            cls.question_groups.clear()
            # Add new question groups
            question_groups = QuestionGroup.query.filter(
                QuestionGroup.id.in_(data['questionGroups'])
            ).all()
            for qg in question_groups:
                cls.question_groups.append(qg)
        
        db.session.commit()
        
        # Also update template if question groups changed
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
    """API endpoint to regenerate enhanced template for a class"""
    try:
        class_obj = Class.query.get_or_404(class_id)
        
        # Regenerate enhanced template and routes
        generation_result = enhanced_generator.regenerate_class_resources(class_id)
        
        # Refresh route registration
        route_registry.refresh_class_routes(class_id)
        
        # Update dashboard integration
        integration_info = enhanced_generator.create_class_dashboard_integration(class_obj)
        
        return jsonify({
            "success": True, 
            "message": "Enhanced template regenerated successfully!",
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
    return render_template('admin/student_classes.html', active_page='student_classes')

@class_controller.route('/api/student/classes', methods=['GET'])
@login_required
def get_student_classes():
    """API endpoint to retrieve all classes that the current admin user can view"""
    try:
        # Get all classes from database
        classes = Class.query.all()
        
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