from flask import Blueprint, jsonify, request, session
from instructor.models.question import Question
from instructor.models.question_group import QuestionGroup
from instructor.controllers.question_controller import QuestionController
from instructor.controllers.question_group_controller import QuestionGroupController
from instructor.models.topology import Topology
from instructor.controllers.topology_controller import TopologyController
from instructor.models.class_model import Class, class_students  # Import class_students from class_model
from __init__ import db  # Import db from main app
from user.models.user import User as UserModel  # Import User model directly
from user.models.score import Score as UserScore  # Use the regular Score model for all scoring
from user.constants.linkup import (
    LINKUP_FOUNDATION_TOTAL,
    LINKUP_FOUNDATION_SET,
    canonicalize_completed_ids,
    calculate_linkup_counts,
    normalize_linkup_id,
)
# Static content imports removed - using database-driven content
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

@api_blueprint.route('/class/<int:class_id>', methods=['GET'])
def get_class_details(class_id):
    """API endpoint to get details of a specific class by ID"""
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "User not logged in"}), 401
    
    try:
        user_id = session['user_id']
        
        # Check if the user is enrolled in this class
        enrollment = db.session.query(class_students).filter(
            class_students.c.class_id == class_id,
            class_students.c.user_id == user_id
        ).first()
        
        if not enrollment:
            return jsonify({"status": "error", "message": "You are not enrolled in this class"}), 403
        
        # Get the class details
        cls = Class.query.get_or_404(class_id)
        
        # Count total students in this class
        student_count = db.session.query(class_students).filter(
            class_students.c.class_id == cls.id
        ).count()
        
        # Format for response
        class_data = {
            'id': cls.id,
            'name': cls.name,
            'section': cls.section,
            'description': cls.description,
            'start_date': cls.start_date.isoformat() if cls.start_date else None,
            'end_date': cls.end_date.isoformat() if cls.end_date else None,
            'enrollment_count': student_count,
            'code': cls.code
        }
        
        return jsonify(class_data)
    except Exception as e:
        import traceback
        print(f"Error fetching class details: {str(e)}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"Error fetching class details: {str(e)}"}), 500

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
        from instructor.models.essay_response import EssayResponse
        
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

@api_blueprint.route('/questions/lesson/<int:lesson_id>', methods=['GET'])
def get_questions_by_lesson(lesson_id):
    """Get questions for a specific lesson based on module characteristics"""
    try:
        from user.models import Lesson, Module, Question, StandardQuestion
        
        # Get the lesson and its module
        lesson = Lesson.query.get(lesson_id)
        if not lesson:
            return jsonify({"error": "Lesson not found"}), 404
            
        module = Module.query.get(lesson.module_id)
        if not module:
            return jsonify({"error": "Module not found"}), 404
        
        # Determine question category based on module characteristics
        question_category = None
        
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
        else:
            # Fallback to networking if no module found
            question_category = 'networking'
        
        # Get questions from both tables with category filter
        questions_1 = Question.query.filter_by(category=question_category).all()
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
        
        return jsonify({
            "lesson_id": lesson_id,
            "module_title": module.title,
            "question_category": question_category,
            "questions": all_questions
        })
        
    except Exception as e:
        import traceback
        print(f"Error in get_questions_by_lesson: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500

@api_blueprint.route('/questions/module/<int:module_id>', methods=['GET'])
def get_questions_by_module(module_id):
    """Get questions assigned to a specific module via Quiz"""
    try:
        from instructor.models.module import Module
        from instructor.models.question_group import QuestionGroup
        
        # Get the module
        module = Module.query.get(module_id)
        if not module:
            return jsonify({"error": "Module not found"}), 404
        
        # Get all Quiz assigned to this module
        question_groups = module.question_groups.all()
        
        # Collect all questions from assigned Quiz
        all_questions = []
        total_groups = len(question_groups)
        
        for qg in question_groups:
            if hasattr(qg, 'questions') and qg.questions:
                for q in qg.questions:
                    question_dict = {
                        'id': q.id,
                        'question': q.question,
                        'answer': q.answer,
                        'category': getattr(q, 'category', ''),
                        'difficulty': getattr(q, 'difficulty', 'medium'),
                        'numb': getattr(q, 'numb', 0),
                        'question_group_id': qg.id,
                        'question_group_name': qg.name,
                        'source_table': 'question'
                    }
                    
                    # Add options if they exist
                    if hasattr(q, 'option1') and q.option1:
                        question_dict['options'] = [
                            q.option1,
                            q.option2 if hasattr(q, 'option2') and q.option2 else '',
                            q.option3 if hasattr(q, 'option3') and q.option3 else '',
                            q.option4 if hasattr(q, 'option4') and q.option4 else ''
                        ]
                        # Filter out empty options
                        question_dict['options'] = [opt for opt in question_dict['options'] if opt.strip()]
                    
                    all_questions.append(question_dict)
        
        # Sort questions by question number if available
        all_questions.sort(key=lambda x: (x.get('question_group_name', ''), x.get('numb', 0)))
        
        return jsonify({
            "module_id": module_id,
            "module_title": module.title,
            "total_question_groups": total_groups,
            "total_questions": len(all_questions),
            "questions": all_questions
        })
        
    except Exception as e:
        import traceback
        print(f"Error in get_questions_by_module: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500

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

@api_blueprint.route('/networking1/save-score', methods=['POST'])
def save_networking1_score():
    """API endpoint to save Networking 1 quiz score"""
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "User not logged in"}), 401
    
    try:
        data = request.json
        user_id = session['user_id']
        
        # Import score model
        from user.models.score import Score
        from user.models.user import UserModel
        
        # Create score entry
        score = Score(
            user_id=user_id,
            score=data.get('score', 0),
            category='networking1',
            total_questions=data.get('total_questions', 5),
            correct_answers=data.get('correct_answers', 0)
        )
        
        db.session.add(score)
        db.session.commit()
        
        # Update user's total score
        user = UserModel.query.get(user_id)
        if user:
            user.update_total_score()
            db.session.commit()
        
        return jsonify({
            "status": "success", 
            "message": "Score saved successfully",
            "score": data.get('score', 0)
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error saving networking1 score: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@api_blueprint.route('/networking1/lessons', methods=['GET'])
def get_networking1_lessons():
    """API endpoint to get Networking 1 lesson content from database"""
    try:
        # Use database content instead of static content
        return jsonify({"status": "success", "lessons": [], "message": "Using database-driven content"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@api_blueprint.route('/networking2/lessons', methods=['GET']) 
def get_networking2_lessons():
    """API endpoint to get Networking 2 lesson content from database"""
    try:
        # Use database content instead of static content
        return jsonify({"status": "success", "lessons": [], "message": "Using database-driven content"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@api_blueprint.route('/networking1/lesson/<lesson_id>', methods=['GET'])
def get_networking1_lesson(lesson_id):
    """API endpoint to get a specific Networking 1 lesson from database"""
    try:
        # Use database content instead of static content
        return jsonify({"error": "Lesson content now managed through database. Please use dynamic class routes."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/networking2/lesson/<lesson_id>', methods=['GET'])
def get_networking2_lesson(lesson_id):
    """API endpoint to get a specific Networking 2 lesson from database"""
    try:
        # Use database content instead of static content
        return jsonify({"error": "Lesson content now managed through database. Please use dynamic class routes."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Additional API endpoints for frontend compatibility
@api_blueprint.route('/networking/lesson/<lesson_id>', methods=['GET'])
def get_networking_lesson(lesson_id):
    """API endpoint to get a specific Networking 1 lesson (alternative URL pattern)"""
    try:
        # Use database content instead of static content
        return jsonify({"error": "Lesson content now managed through database. Please use dynamic class routes."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/networking/track-progress', methods=['POST'])
def track_networking_progress():
    """API endpoint to track networking progress"""
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "User not logged in"}), 401
    
    try:
        data = request.get_json()
        lesson_id = data.get('lessonId')
        completed = data.get('completed', False)
        
        # For now, just return success - you can implement actual progress tracking later
        return jsonify({
            "status": "success", 
            "message": "Progress tracked successfully",
            "lesson_id": lesson_id,
            "completed": completed
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@api_blueprint.route('/networking2/progress', methods=['POST'])
def track_networking2_progress():
    """API endpoint to track networking 2 progress"""
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "User not logged in"}), 401
    
    try:
        data = request.get_json()
        lesson_id = data.get('lessonId')
        completed = data.get('completed', False)
        
        # For now, just return success - you can implement actual progress tracking later
        return jsonify({
            "status": "success", 
            "message": "Progress tracked successfully",
            "lesson_id": lesson_id,
            "completed": completed
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================================================
# CHALLENGE PROGRESS API ROUTES - MVP
# Save/Load/Clear game state for resumable challenges
# ============================================================================

@api_blueprint.route('/challenge/save-progress', methods=['POST'])
def save_challenge_progress():
    """
    Save challenge progress to database
    Request body: {challenge_type: str, state_data: dict, is_completed: bool}
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'User not logged in'}), 401
    
    try:
        from user.models.challenge_progress import ChallengeProgress
        
        data = request.get_json()
        user_id = session['user_id']
        challenge_type = data.get('challenge_type')
        state_data = data.get('state_data')
        is_completed = data.get('is_completed', False)
        
        # Validation
        if not challenge_type:
            return jsonify({'success': False, 'error': 'Missing challenge_type'}), 400
        
        if not state_data or not isinstance(state_data, dict):
            return jsonify({'success': False, 'error': 'Missing or invalid state_data'}), 400
        
        # Save progress using model method
        progress = ChallengeProgress.save_progress(
            user_id=user_id,
            challenge_type=challenge_type,
            state_data=state_data,
            is_completed=is_completed
        )
        
        return jsonify({
            'success': True,
            'message': 'Progress saved successfully',
            'progress': progress.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error clearing challenge progress: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_blueprint.route('/challenge/completed-list/<challenge_type>', methods=['GET'])
def get_completed_challenges(challenge_type):
    """
    Get list of all completed challenges for a specific challenge type
    Uses ChallengeScore table for unified tracking
    Returns: {success: bool, completed_challenges: list}
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'User not logged in'}), 401
    
    try:
        from user.models.challenge_score import ChallengeScore
        
        user_id = session['user_id']
        print(f"[API] [OK] Fetching completed challenges for user {user_id}, type: {challenge_type}")
        
        # Map 'linkup' to 'troubleshooting' (same challenge, different names)
        mapped_type = 'troubleshooting' if challenge_type == 'linkup' else challenge_type
        
        # Get score record for this challenge type
        score_record = ChallengeScore.query.filter_by(
            user_id=user_id,
            challenge_type=mapped_type
        ).first()
        
        completed_payload = []
        linkup_counts = None
        
        if score_record:
            print(f"[API] 📊 ChallengeScore record found - Score: {score_record.best_score}, Completed: {score_record.is_completed}")
            metadata = score_record.challenge_metadata or {}
            if mapped_type == 'troubleshooting':
                raw_completed = metadata.get('completed_challenges', [])
                completed_payload = canonicalize_completed_ids(raw_completed)
                linkup_counts = metadata.get('challenge_counts')
                if not isinstance(linkup_counts, dict):
                    linkup_counts = calculate_linkup_counts(completed_payload)
                print(
                    f"[API] [OK] Canonical Link Up completions: {len(completed_payload)}/{LINKUP_FOUNDATION_TOTAL}"
                )
            else:
                if metadata:
                    print(f"[API] 📦 Metadata keys: {list(metadata.keys())}")
                if score_record.is_completed:
                    entry = {
                        'challenge_type': challenge_type,
                        'score': score_record.best_score,
                        'completed_at': score_record.last_completed_at.isoformat() if score_record.last_completed_at else None
                    }
                    completed_payload.append(entry)
        else:
            print(f"[API] ℹ️ No ChallengeScore record found for challenge_type: {mapped_type}")
        
        print(f"[API] 📤 Returning {len(completed_payload)} completed entries")
        
        response_payload = {
            'success': True,
            'completed_challenges': completed_payload,
            'total_completed': len(completed_payload)
        }

        if mapped_type == 'troubleshooting':
            linkup_counts = linkup_counts or calculate_linkup_counts(completed_payload)
            response_payload['challenge_counts'] = linkup_counts
            response_payload['foundation_total'] = LINKUP_FOUNDATION_TOTAL
            response_payload['is_complete'] = linkup_counts.get('foundation', 0) >= LINKUP_FOUNDATION_TOTAL

        return jsonify(response_payload), 200
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[API] [ERROR] ERROR in get_completed_challenges:")
        print(f"[API] Error type: {type(e).__name__}")
        print(f"[API] Error message: {str(e)}")
        print(f"[API] Full traceback:")
        print(error_trace)
        
        # Return a safe error response
        return jsonify({
            'success': False, 
            'error': str(e),
            'error_type': type(e).__name__,
            'completed_challenges': [],
            'total_completed': 0
        }), 500


@api_blueprint.route('/challenge/load-progress/<challenge_type>', methods=['GET'])
def load_challenge_progress(challenge_type):
    """
    Load saved challenge progress for the current user
    Returns: {success: bool, has_progress: bool, state_data: dict, last_updated: str, is_completed: bool}
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'User not logged in'}), 401
    
    try:
        from user.models.challenge_progress import ChallengeProgress
        
        user_id = session['user_id']
        
        # Load progress using model method
        progress = ChallengeProgress.load_progress(
            user_id=user_id,
            challenge_type=challenge_type
        )
        
        if progress:
            return jsonify({
                'success': True,
                'has_progress': True,
                'state_data': progress.state_data,
                'last_updated': progress.last_updated.isoformat(),
                'is_completed': progress.is_completed,
                'created_at': progress.created_at.isoformat() if progress.created_at else None
            })
        else:
            return jsonify({
                'success': True,
                'has_progress': False
            })
            
    except Exception as e:
        print(f"Error loading challenge progress: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_blueprint.route('/challenge/clear-progress/<challenge_type>', methods=['DELETE'])
def clear_challenge_progress(challenge_type):
    """
    Clear saved challenge progress for the current user
    Returns: {success: bool, message: str}
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'User not logged in'}), 401
    
    try:
        from user.models.challenge_progress import ChallengeProgress
        
        user_id = session['user_id']
        
        # Clear progress using model method
        cleared = ChallengeProgress.clear_progress(
            user_id=user_id,
            challenge_type=challenge_type
        )
        
        if cleared:
            return jsonify({
                'success': True,
                'message': f'Progress cleared for {challenge_type}'
            })
        else:
            return jsonify({
                'success': True,
                'message': 'No progress found to clear'
            })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error clearing challenge progress: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_blueprint.route('/linkup/foundation/complete', methods=['POST'])
def save_foundation_completion():
    """
    Save Link Up! Foundation module completion
    Request body: {module_id: str, score: int, time_spent: int}
    
    This fixes the bug where Foundation completions were only saved to localStorage
    and never synced to the backend database.
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'User not logged in'}), 401
    
    try:
        from user.models.challenge_score import ChallengeScore
        from sqlalchemy.orm.attributes import flag_modified
        from datetime import datetime
        
        data = request.get_json()
        user_id = session['user_id']
        module_id = data.get('module_id')
        score = data.get('score', 100)  # Foundation modules are pass/fail
        time_spent = data.get('time_spent', 0)
        
        # Validation
        if not module_id:
            return jsonify({'success': False, 'error': 'Missing module_id'}), 400
        canonical_module = normalize_linkup_id(module_id)
        if not canonical_module or canonical_module not in LINKUP_FOUNDATION_SET:
            return jsonify({'success': False, 'error': 'Invalid foundation module id'}), 400
        
        print(f"[Link Up Foundation] User {user_id} completed: {canonical_module}")
        
        # Get or create troubleshooting challenge score
        challenge_score = ChallengeScore.query.filter_by(
            user_id=user_id,
            challenge_type='troubleshooting'
        ).first()
        
        if not challenge_score:
            # Create new record
            challenge_score = ChallengeScore(
                user_id=user_id,
                challenge_type='troubleshooting',
                best_score=0.0,
                latest_score=0.0,
                total_attempts=0,
                total_score=0.0,
                average_score=0.0,
                is_completed=False,
                challenge_metadata={}
            )
            db.session.add(challenge_score)
        
        # Get existing completed_challenges array
        if challenge_score.challenge_metadata is None:
            challenge_score.challenge_metadata = {}
        
        existing_completed = challenge_score.challenge_metadata.get('completed_challenges', [])
        already_completed = canonical_module in existing_completed
        merged_completed = canonicalize_completed_ids(
            existing_completed if already_completed else existing_completed + [canonical_module]
        )
        challenge_score.challenge_metadata['completed_challenges'] = merged_completed
        challenge_score.challenge_metadata['challenge_counts'] = calculate_linkup_counts(merged_completed)

        if not already_completed:
            if 'foundation_modules' not in challenge_score.challenge_metadata:
                challenge_score.challenge_metadata['foundation_modules'] = {}

            challenge_score.challenge_metadata['foundation_modules'][canonical_module] = {
                'completed_at': datetime.utcnow().isoformat(),
                'score': score,
                'time_spent': time_spent
            }

            flag_modified(challenge_score, 'challenge_metadata')

            foundation_completed = challenge_score.challenge_metadata['challenge_counts']['foundation']
            progress_percentage = (foundation_completed / LINKUP_FOUNDATION_TOTAL) * 100.0 if LINKUP_FOUNDATION_TOTAL else 0.0

            if progress_percentage > challenge_score.best_score:
                challenge_score.best_score = progress_percentage
                challenge_score.latest_score = progress_percentage

            if foundation_completed >= LINKUP_FOUNDATION_TOTAL:
                challenge_score.is_completed = True
                if not challenge_score.first_completed_at:
                    challenge_score.first_completed_at = datetime.utcnow()
                challenge_score.last_completed_at = datetime.utcnow()

            db.session.commit()

            print(
                f"[Link Up Foundation] Progress: {foundation_completed}/{LINKUP_FOUNDATION_TOTAL} "
                f"({progress_percentage:.1f}%)"
            )

            return jsonify({
                'success': True,
                'message': f'Foundation module {canonical_module} saved',
                'total_completed': foundation_completed,
                'progress_percentage': progress_percentage,
                'all_complete': foundation_completed >= LINKUP_FOUNDATION_TOTAL
            }), 200

        print(f"[Link Up Foundation] Module {canonical_module} already completed")
        foundation_completed = challenge_score.challenge_metadata.get('challenge_counts', {}).get('foundation', 0)
        progress_percentage = (foundation_completed / LINKUP_FOUNDATION_TOTAL) * 100.0 if LINKUP_FOUNDATION_TOTAL else 0.0
        return jsonify({
            'success': True,
            'message': 'Module already completed',
            'total_completed': foundation_completed,
            'progress_percentage': progress_percentage
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Failed to save Foundation completion: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500