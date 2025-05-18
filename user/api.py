from flask import Blueprint, jsonify, request, session
from admin.models.question import Question
from admin.models.question_group import QuestionGroup
from admin.controllers.question_controller import QuestionController
from admin.controllers.question_group_controller import QuestionGroupController
from admin.models.topology import Topology
from admin.controllers.topology_controller import TopologyController
from admin.models.score import AdminScore  # Updated to use the renamed model directly
from admin.models.class_model import Class
from user.models import db, User as UserModel  # Rename to avoid conflicts
from user.models import Score as UserScore  # Use a clear name for the user's Score model
from user.models.association_tables import class_students
import json
from datetime import datetime

api_blueprint = Blueprint('api', __name__)
question_controller = QuestionController()
question_group_controller = QuestionGroupController()
topology_controller = TopologyController()

@api_blueprint.route('/classes', methods=['GET'])
def get_classes():
    """API endpoint to get the classes that the current user is enrolled in"""
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "User not logged in"}), 401
    
    try:
        user_id = session['user_id']
        
        # Find all classes the user is enrolled in using the association table
        enrolled_classes = db.session.query(Class).join(
            class_students, 
            Class.id == class_students.c.class_id
        ).filter(
            class_students.c.user_id == user_id
        ).all()
        
        # Format classes for response
        classes_data = []
        for cls in enrolled_classes:
            # Count total students in this class
            student_count = db.session.query(class_students).filter(
                class_students.c.class_id == cls.id
            ).count()
            
            # Format for response
            classes_data.append({
                'id': cls.id,
                'name': cls.name,
                'section': cls.section,
                'description': cls.description,
                'startDate': cls.start_date.isoformat() if cls.start_date else None,
                'endDate': cls.end_date.isoformat() if cls.end_date else None,
                'studentCount': student_count
            })
        
        return jsonify({"status": "success", "classes": classes_data})
    except Exception as e:
        import traceback
        print(f"Error fetching classes: {str(e)}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"Error fetching classes: {str(e)}"}), 500

@api_blueprint.route('/save_essay', methods=['POST'])
def save_essay():
    """Save an essay response for the current user"""
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "User not logged in."}), 403
    
    data = request.get_json()
    question_text = data.get('question')
    question_id = data.get('questionId')
    response_text = data.get('answer')
    category = data.get('category', 'riddle')
    
    if not response_text or not question_text:
        return jsonify({"status": "error", "message": "Missing question or response"}), 400
    
    try:
        from admin.models.essay_response import EssayResponse
        
        new_response = EssayResponse(
            user_id=session['user_id'],
            question_id=question_id,
            question_text=question_text,
            response_text=response_text,
            category=category
        )
        db.session.add(new_response)
        db.session.commit()
        
        return jsonify({"status": "success", "message": "Essay submitted for review"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error saving essay: {str(e)}")
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500

@api_blueprint.route('/questions', methods=['GET'])
def get_questions():
    """Get all questions, with optional category filter"""
    try:
        category = request.args.get('category')
        if category:
            questions = question_controller.get_questions_by_category(category)
        else:   
            questions = question_controller.get_all_questions()
        
        # Convert to JSON-serializable format
        result = []
        for question in questions:
            question_data = {
                'id': question.id,
                'numb': question.numb,
                'question': question.question,
                'answer': question.answer,
                'options': question.options,
                'explanation': question.explanation,
                'category': question.category
            }
            result.append(question_data)
        
        return jsonify(result)
    except Exception as e:
        import traceback
        print(f"Error in get_questions: {str(e)}")
        traceback.print_exc()
        return jsonify([]), 500

@api_blueprint.route('/topology/types', methods=['GET'])
def get_topology_types():
    """Get available topology types for the topology UI"""
    try:
        # Return all available topology types
        topology_types = db.session.query(Topology.topology_type).distinct().all()
        topology_types = [t[0] for t in topology_types]
        
        # If no types in the database yet, return the default ones
        if not topology_types:
            topology_types = [
                'point-to-point', 'mesh', 'star', 'bus', 'ring', 'tree', 'hybrid'
            ]
        
        return jsonify({
            "status": "success",
            "topology_types": topology_types
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@api_blueprint.route('/topology/list', methods=['GET'])
def get_topologies():
    """Get all active topologies for the user UI"""
    try:
        # Get all active topologies
        topologies = Topology.query.filter_by(is_active=True).all()
        
        # Format for response
        topology_data = []
        for topology in topologies:
            topology_data.append({
                'id': topology.id,
                'title': topology.title,
                'description': topology.description,
                'difficulty': topology.difficulty,
                'topology_type': topology.topology_type
            })
        
        return jsonify({
            "status": "success",
            "topologies": topology_data
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@api_blueprint.route('/join-class', methods=['POST'])
def join_class():
    """API endpoint to join a class using a class code"""
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "User not logged in"}), 401
    
    try:
        data = request.get_json()
        class_code = data.get('code')
        
        if not class_code:
            return jsonify({"status": "error", "message": "Class code is required"}), 400
        
        # Find the class with this code
        class_obj = Class.query.filter_by(code=class_code).first()
        
        if not class_obj:
            return jsonify({"status": "error", "message": "Invalid class code. Please try again."}), 404
        
        user_id = session['user_id']
        
        # Check if user is already enrolled in this class
        enrollment = db.session.query(class_students).filter(
            class_students.c.class_id == class_obj.id,
            class_students.c.user_id == user_id
        ).first()
        
        if enrollment:
            return jsonify({"status": "error", "message": "You are already enrolled in this class"}), 400
        
        # Check if class has reached max students (if specified)
        if class_obj.max_students:
            current_student_count = db.session.query(class_students).filter(
                class_students.c.class_id == class_obj.id
            ).count()
            
            if current_student_count >= class_obj.max_students:
                return jsonify({"status": "error", "message": "This class has reached its maximum enrollment"}), 400
        
        # Enroll the user in the class
        stmt = class_students.insert().values(user_id=user_id, class_id=class_obj.id)
        db.session.execute(stmt)
        db.session.commit()
        
        return jsonify({
            "status": "success", 
            "message": f"Successfully joined {class_obj.name}"
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"Error joining class: {str(e)}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"Error joining class: {str(e)}"}), 500

@api_blueprint.route('/leave-class/<int:class_id>', methods=['POST'])
def leave_class(class_id):
    """API endpoint to leave a class"""
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "User not logged in"}), 401
    
    try:
        user_id = session['user_id']
        
        # Check if user is enrolled in this class
        enrollment = db.session.query(class_students).filter(
            class_students.c.class_id == class_id,
            class_students.c.user_id == user_id
        ).first()
        
        if not enrollment:
            return jsonify({"status": "error", "message": "You are not enrolled in this class"}), 400
        
        # Remove the user from the class
        stmt = class_students.delete().where(
            class_students.c.class_id == class_id,
            class_students.c.user_id == user_id
        )
        db.session.execute(stmt)
        db.session.commit()
        
        return jsonify({
            "status": "success", 
            "message": "Successfully left the class"
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"Error leaving class: {str(e)}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"Error leaving class: {str(e)}"}), 500