"""
Grades API Blueprint
Unified API for aggregating grades from all submission types
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import func
from __init__ import db
from instructor.models.class_model import Class, class_students
from instructor.models.assignment_submission import AssignmentSubmission
from instructor.models.class_content import ClassAssignment
from instructor.models.simulation_progress import SimulationProgress
from instructor.models.simulation_assignment import SimulationAssignment
from instructor.models.essay_response import EssayResponse
from instructor.models.question_group import QuestionGroup
from user.models.live_quiz import LiveQuizSession, LiveQuizParticipant
from user.models.user import User

grades_api = Blueprint('grades_api', __name__)


@grades_api.route('/instructor/api/grades/<int:class_id>', methods=['GET'])
@login_required
def get_class_grades(class_id):
    """
    Unified grades API for Grades tab
    Aggregates data from:
    - assignment_submissions
    - simulation_progress
    - live_quiz_participants
    - essay_response
    """
    print(f"🔍 [GRADES API] Called get_class_grades for class_id={class_id}, user={current_user.id if current_user.is_authenticated else 'Anonymous'}")
    
    try:
        # Verify instructor owns this class
        cls = Class.query.get_or_404(class_id)
        print(f"✅ [GRADES API] Class found: {cls.name}, created_by={cls.created_by}")
        if cls.created_by != current_user.id:
            # Check if super_admin
            if not (hasattr(current_user, 'role') and current_user.role == 'super_admin'):
                return jsonify({"error": "Unauthorized"}), 403
        
        # Get all students in class
        students = db.session.query(User).join(
            class_students, User.id == class_students.c.user_id
        ).filter(class_students.c.class_id == class_id).all()
        
        # ========== AGGREGATE ASSIGNMENTS ==========
        assignments = []
        assignment_list = ClassAssignment.query.filter_by(
            class_id=class_id,
            is_published=True
        ).all()
        
        for assignment in assignment_list:
            # Get all submissions for this assignment
            submissions = AssignmentSubmission.query.filter_by(
                assignment_id=assignment.id
            ).all()
            
            submitted_count = len([s for s in submissions if s.status not in ['draft', None]])
            graded_count = len([s for s in submissions if s.grade is not None])
            
            # Calculate average grade
            graded_submissions = [s for s in submissions if s.grade is not None]
            avg_grade = 0
            if graded_submissions:
                total = sum([s.grade for s in graded_submissions])
                avg_grade = (total / len(graded_submissions))
            
            assignments.append({
                "id": f"assignment_{assignment.id}",
                "title": assignment.title,
                "type": "assignment",
                "due_date": assignment.due_date.isoformat() if assignment.due_date else None,
                "max_points": assignment.points or 100,
                "submitted_count": submitted_count,
                "graded_count": graded_count,
                "average_grade": round(avg_grade, 2)
            })
        
        # ========== AGGREGATE SIMULATIONS ==========
        simulations = []
        simulation_assignments = SimulationAssignment.query.filter_by(
            class_id=class_id,
            is_active=True
        ).all()
        
        for sim_assignment in simulation_assignments:
            if not sim_assignment.simulation:
                continue
                
            # Get all progress records for this simulation
            progress_records = SimulationProgress.query.filter_by(
                simulation_id=sim_assignment.simulation_id
            ).join(
                class_students,
                SimulationProgress.user_id == class_students.c.user_id
            ).filter(
                class_students.c.class_id == class_id
            ).all()
            
            completed_count = len([p for p in progress_records if p.status == 'completed'])
            
            # Calculate average score
            scored_records = [p for p in progress_records if p.score is not None]
            avg_score = 0
            if scored_records:
                avg_score = sum([p.score for p in scored_records]) / len(scored_records)
            
            simulations.append({
                "id": f"simulation_{sim_assignment.simulation_id}",
                "title": sim_assignment.simulation.title if sim_assignment.simulation else "Unknown",
                "type": "simulation",
                "due_date": sim_assignment.due_date.isoformat() if sim_assignment.due_date else None,
                "max_points": 100,
                "submitted_count": len(progress_records),
                "graded_count": completed_count,
                "average_grade": round(avg_score, 2)
            })
        
        # ========== AGGREGATE LIVE QUIZZES ==========
        quizzes = []
        live_quiz_sessions = LiveQuizSession.query.filter_by(
            class_id=class_id
        ).all()

        # Pre-compute question counts per session's question_group to avoid repeated lookups
        group_ids = {s.question_group_id for s in live_quiz_sessions if getattr(s, 'question_group_id', None)}
        question_groups = []
        question_counts = {}
        if group_ids:
            question_groups = QuestionGroup.query.filter(QuestionGroup.id.in_(group_ids)).all()
            for qg in question_groups:
                # Safely get question count; default to 0 if relationship not loaded
                count = len(getattr(qg, 'questions', []) or [])
                question_counts[qg.id] = count
        
        for session in live_quiz_sessions:
            # Get participants from this class
            participants = db.session.query(LiveQuizParticipant).filter(
                LiveQuizParticipant.session_id == session.id
            ).join(
                class_students,
                LiveQuizParticipant.user_id == class_students.c.user_id
            ).filter(
                class_students.c.class_id == class_id
            ).all()
            
            completed_count = len([p for p in participants if p.completed_at is not None])
            
            # Calculate average score as percentage
            avg_score = 0
            if participants:
                # Normalize using actual number of questions in the session's question group
                # Scoring awards up to 1000 points per correct answer (see LiveQuizResponse.calculate_points)
                q_count = question_counts.get(getattr(session, 'question_group_id', None), 0)
                max_possible_points = (q_count or 0) * 1000
                # Convert each participant's score to percentage, then average
                percentage_scores = []
                for p in participants:
                    total_score = getattr(p, 'total_score', 0) or 0
                    percentage = min(100, (total_score / max_possible_points) * 100) if max_possible_points > 0 else 0
                    percentage_scores.append(percentage)
                avg_score = sum(percentage_scores) / len(percentage_scores) if percentage_scores else 0
            
            quizzes.append({
                "id": f"quiz_{session.id}",
                "title": session.title,
                "type": "quiz",
                "due_date": session.ended_at.isoformat() if session.ended_at else None,
                "max_points": 100,
                "submitted_count": len(participants),
                "graded_count": completed_count,
                "average_grade": round(avg_score, 2)
            })
        
        # ========== AGGREGATE ESSAYS ==========
        essays = []
        # Get essay responses for students in this class
        essay_responses = db.session.query(EssayResponse).join(
            class_students, EssayResponse.user_id == class_students.c.user_id
        ).filter(
            class_students.c.class_id == class_id
        ).all()
        
        # Group essays by question
        from collections import defaultdict
        essays_by_question = defaultdict(list)
        for essay in essay_responses:
            essays_by_question[essay.question_id].append(essay)
        
        for question_id, essay_list in essays_by_question.items():
            graded_count = len([e for e in essay_list if e.is_graded])
            
            # Calculate average score
            graded_essays = [e for e in essay_list if e.graded_score is not None]
            avg_score = 0
            if graded_essays:
                avg_score = sum([e.graded_score for e in graded_essays]) / len(graded_essays)
            
            # Get question title
            question_title = f"Essay Question {question_id}"
            if essay_list and essay_list[0].question_text:
                question_title = essay_list[0].question_text[:50] + "..."
            
            essays.append({
                "id": f"essay_{question_id}",
                "title": question_title,
                "type": "essay",
                "due_date": None,
                "max_points": 100,
                "submitted_count": len(essay_list),
                "graded_count": graded_count,
                "average_grade": round(avg_score, 2)
            })
        
        # ========== BUILD STUDENT GRADES MAP ==========
        students_data = []
        for student in students:
            grades = {}
            submissions = {}
            
            # Add assignment grades
            for assignment in assignment_list:
                sub = AssignmentSubmission.query.filter_by(
                    assignment_id=assignment.id,
                    student_id=student.id
                ).first()
                
                if sub:
                    key = f"assignment_{assignment.id}"
                    if sub.grade is not None:
                        grades[key] = {"score": sub.grade}
                    submissions[key] = {
                        "submitted_at": sub.submitted_at.isoformat() if sub.submitted_at else None,
                        "status": sub.status
                    }
            
            # Add simulation grades
            for sim_assignment in simulation_assignments:
                progress = SimulationProgress.query.filter_by(
                    simulation_id=sim_assignment.simulation_id,
                    user_id=student.id
                ).first()
                
                if progress:
                    key = f"simulation_{sim_assignment.simulation_id}"
                    if progress.score is not None:
                        grades[key] = {"score": progress.score}
                    submissions[key] = {
                        "submitted_at": progress.updated_at.isoformat() if progress.updated_at else None,
                        "status": progress.status
                    }
            
            # Add live quiz grades
            for session in live_quiz_sessions:
                participant = LiveQuizParticipant.query.filter_by(
                    session_id=session.id,
                    user_id=student.id
                ).first()
                
                if participant:
                    key = f"quiz_{session.id}"
                    # Normalize quiz score to percentage (0-100)
                    # Use actual number of questions from the session's question group and 1000 pts/question
                    q_count = question_counts.get(getattr(session, 'question_group_id', None), 0)
                    max_possible_points = (q_count or 0) * 1000
                    total_score = getattr(participant, 'total_score', 0) or 0
                    percentage_score = min(100, (total_score / max_possible_points) * 100) if max_possible_points > 0 else 0
                    grades[key] = {"score": round(percentage_score, 2)}
                    submissions[key] = {
                        "submitted_at": participant.completed_at.isoformat() if participant.completed_at else None,
                        "status": "completed" if participant.completed_at else "in_progress"
                    }
            
            # Add essay grades
            student_essays = [e for e in essay_responses if e.user_id == student.id]
            for essay in student_essays:
                key = f"essay_{essay.question_id}"
                if essay.graded_score is not None:
                    grades[key] = {"score": essay.graded_score}
                submissions[key] = {
                    "submitted_at": essay.submission_date.isoformat() if essay.submission_date else None,
                    "status": "graded" if essay.is_graded else "pending"
                }
            
            students_data.append({
                "id": student.id,
                "username": student.username,
                "email": student.email or "",
                "grades": grades,
                "submissions": submissions
            })
        
        return jsonify({
            "students": students_data,
            "assignments": assignments,
            "simulations": simulations,
            "quizzes": quizzes,
            "essays": essays
        })
    
    except Exception as e:
        import traceback
        print(f"❌ [GRADES API] ERROR in get_class_grades for class_id={class_id}:")
        print(f"❌ [GRADES API] Error type: {type(e).__name__}")
        print(f"❌ [GRADES API] Error message: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
