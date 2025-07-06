from flask import Blueprint, jsonify, request
from admin import db
from admin.models.class_model import Class
from admin.models.question_group import QuestionGroup
import random
import string
from datetime import datetime

api_bp = Blueprint('api', __name__)

@api_bp.route('/admin/api/test', methods=['GET'])
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

@api_bp.route('/admin/api/classes', methods=['GET'])
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

@api_bp.route('/admin/api/classes', methods=['POST'])
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
        
        # 🚀 ENHANCED AUTOMATION: Generate class files automatically
        try:
            from admin.services.enhanced_class_template_generator import enhanced_template_generator
            from admin.services.dynamic_route_registry import route_registry
            
            print(f"🎯 Generating automated files for class: {new_class.name}")
            
            # Generate template and routes
            result = enhanced_template_generator.generate_all_class_resources(new_class)
            
            if result.get('success'):
                print(f"✅ Auto-generated files:")
                print(f"   - Template: {result.get('template_path')}")
                print(f"   - Routes: {result.get('routes_path')}")
                
                # Register routes dynamically
                route_registry.register_class_routes(new_class)
                print(f"✅ Routes registered for class {new_class.id}")
                
            else:
                print(f"⚠️  File generation had issues: {result.get('error', 'Unknown error')}")
                
        except Exception as auto_error:
            print(f"⚠️  Automation system error: {auto_error}")
            # Don't fail the class creation if automation fails
            import traceback
            traceback.print_exc()
        
        return jsonify({
            'message': 'Class created successfully',
            'class': new_class.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@api_bp.route('/admin/api/classes/<int:class_id>', methods=['GET'])
def get_class(class_id):
    """Get a specific class"""
    try:
        cls = Class.query.get_or_404(class_id)
        return jsonify(cls.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@api_bp.route('/admin/api/classes/<int:class_id>/students', methods=['GET'])
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

@api_bp.route('/admin/api/generate-class-code', methods=['GET'])
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

@api_bp.route('/admin/api/question-groups', methods=['GET'])
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
