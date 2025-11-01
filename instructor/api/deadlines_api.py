"""
Deadlines API Blueprint
API for deadline management and statistics in Deadlines tab
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime
from __init__ import db
from instructor.models.class_model import Class, class_students
from instructor.models.assignment_submission import AssignmentSubmission
from instructor.models.class_content import ClassAssignment
from instructor.models.deadline_policy import (
    DeadlinePolicy, 
    StudentDeadlineExtension, 
    AssignmentAvailabilityWindow
)

deadlines_api = Blueprint('deadlines_api', __name__)


@deadlines_api.route('/instructor/api/deadlines/<int:class_id>', methods=['GET'])
@login_required
def get_class_deadlines(class_id):
    """
    Fetch deadline data for Deadlines tab
    Returns statistics and policies for deadline management
    """
    try:
        # Verify instructor owns this class
        cls = Class.query.get_or_404(class_id)
        if cls.created_by != current_user.id:
            # Check if super_admin
            if not (hasattr(current_user, 'role') and current_user.role == 'super_admin'):
                return jsonify({"error": "Unauthorized"}), 403
        
        # Get all assignments for this class
        # Method 1: Direct class assignments
        direct_assignments = ClassAssignment.query.filter_by(
            class_id=class_id,
            is_published=True
        ).all()
        print(f"[Deadlines API] Direct assignments for class {class_id}: {len(direct_assignments)}")

        # Method 2: Assignments through modules (where content is organized)
        from instructor.models.module import Module
        from user.models.user import User as StudentUser
        from instructor.models.user import InstructorUser

        # First check what modules exist
        modules = Module.query.filter_by(class_id=class_id).all()
        print(f"[Deadlines API] Modules for class {class_id}: {len(modules)}")
        for module in modules:
            module_assigns = ClassAssignment.query.filter_by(module_id=module.id).all()
            print(
                f"  Module {module.id}: {module.title} (published={module.is_published})"
            )
            print(f"    Assignments in module: {len(module_assigns)}")

        module_assignments = db.session.query(ClassAssignment).join(
            Module, ClassAssignment.module_id == Module.id
        ).filter(
            Module.class_id == class_id,
            ClassAssignment.is_published == True
        ).all()
        print(
            f"[Deadlines API] Module assignments (published only): {len(module_assignments)}"
        )

        # Combine both and remove duplicates
        assignment_dict = {}
        for assignment in direct_assignments + module_assignments:
            assignment_dict[assignment.id] = assignment
        assignments = list(assignment_dict.values())
        print(f"[Deadlines API] Total unique assignments: {len(assignments)}")

        assignment_lookup = {a.id: a for a in assignments}
        assignment_ids = [a.id for a in assignments]

        # Build assignment response payload with submission and extension counts
        assignments_data = []
        total_submissions = 0
        total_late = 0

        for assignment in assignments:
            submissions_count = AssignmentSubmission.query.filter_by(
                assignment_id=assignment.id
            ).filter(
                AssignmentSubmission.status != 'draft'
            ).count()

            late_count = AssignmentSubmission.query.filter_by(
                assignment_id=assignment.id,
                is_late=True
            ).count()

            active_extension_count = StudentDeadlineExtension.query.filter_by(
                assignment_id=assignment.id,
                is_active=True
            ).count()

            assignments_data.append({
                "id": assignment.id,
                "title": assignment.title,
                "due_date": assignment.due_date.isoformat() if assignment.due_date else None,
                "assignment_type": assignment.assignment_type,
                "module_id": assignment.module_id,
                "submissions_count": submissions_count,
                "late_count": late_count,
                "extensions_count": active_extension_count,
                "allow_late_submissions": assignment.allow_late_submissions,
                "late_penalty_per_day": assignment.late_penalty_per_day,
                "points": assignment.points
            })

            total_submissions += submissions_count
            total_late += late_count

        on_time_rate = 0.0
        if total_submissions > 0:
            on_time_rate = round(
                ((total_submissions - total_late) / total_submissions) * 100,
                2
            )

        # Build extension payload for the UI
        extensions_data = []
        if assignment_ids:
            extensions = StudentDeadlineExtension.query.filter(
                StudentDeadlineExtension.assignment_id.in_(assignment_ids)
            ).all()
        else:
            extensions = []

        for ext in extensions:
            student = StudentUser.query.get(ext.student_id)
            assignment_ref = assignment_lookup.get(ext.assignment_id)
            approver = InstructorUser.query.get(ext.approved_by) if ext.approved_by else None

            student_name_parts = [
                getattr(student, "first_name", None) if student else None,
                getattr(student, "last_name", None) if student else None
            ]
            student_name = " ".join(part for part in student_name_parts if part)
            if not student_name and student:
                student_name = getattr(student, "username", "Unknown Student")
            if not student_name:
                student_name = "Unknown Student"

            granted_by_parts = [
                getattr(approver, "first_name", None) if approver else None,
                getattr(approver, "last_name", None) if approver else None
            ]
            granted_by_name = " ".join(part for part in granted_by_parts if part)
            if not granted_by_name and approver:
                granted_by_name = getattr(approver, "username", "Instructor")
            if not granted_by_name:
                granted_by_name = "Instructor"

            extensions_data.append({
                "id": ext.id,
                "assignment_id": ext.assignment_id,
                "assignment_title": assignment_ref.title if assignment_ref else "Unknown Assignment",
                "student_id": ext.student_id,
                "student_name": student_name,
                "student_email": getattr(student, "email", None) if student else None,
                "original_due_date": ext.original_due_date.isoformat() if ext.original_due_date else None,
                "extended_due_date": ext.extended_due_date.isoformat() if ext.extended_due_date else None,
                "extension_hours": ext.extension_hours,
                "reason": ext.reason,
                "approval_notes": ext.approval_notes,
                "waive_late_penalty": ext.waive_late_penalty,
                "custom_penalty_rate": ext.custom_penalty_rate,
                "is_active": ext.is_active,
                "used": ext.used,
                "granted_by": granted_by_name,
                "granted_by_id": ext.approved_by,
                "granted_by_name": granted_by_name,
                "granted_at": ext.created_at.isoformat() if ext.created_at else None
            })
        
        # ========== CALCULATE STATISTICS ==========
        
        # Late submissions count
        late_submissions = db.session.query(func.count(AssignmentSubmission.id)).filter(
            AssignmentSubmission.assignment_id.in_(assignment_ids),
            AssignmentSubmission.is_late == True
        ).scalar() or 0
        
        # Active extensions count
        active_extensions = db.session.query(func.count(StudentDeadlineExtension.id)).filter(
            StudentDeadlineExtension.assignment_id.in_(assignment_ids),
            StudentDeadlineExtension.is_active == True
        ).scalar() or 0
        
        # Average late penalty
        avg_penalty = db.session.query(
            func.avg(AssignmentSubmission.late_penalty_applied)
        ).filter(
            AssignmentSubmission.assignment_id.in_(assignment_ids),
            AssignmentSubmission.is_late == True
        ).scalar() or 0.0
        
        # ========== GET DEADLINE POLICIES ==========
        # Get all policies created by this instructor (not just those in use)
        # Check if super_admin to show all policies, otherwise filter by creator
        if hasattr(current_user, 'role') and current_user.role == 'super_admin':
            policies = DeadlinePolicy.query.all()
        else:
            policies = DeadlinePolicy.query.filter_by(created_by=current_user.id).all()
        
        policies_data = []
        for policy in policies:
            policy_dict = policy.to_dict()
            # Count how many assignments use this policy
            assignments_count = db.session.query(func.count(AssignmentAvailabilityWindow.id)).filter(
                AssignmentAvailabilityWindow.deadline_policy_id == policy.id,
                AssignmentAvailabilityWindow.assignment_id.in_(assignment_ids)
            ).scalar() or 0
            policy_dict['assignments_count'] = assignments_count
            policies_data.append(policy_dict)
        
        # ========== GET UPCOMING DEADLINES ==========
        upcoming_deadlines = []
        now = datetime.utcnow()
        
        for assignment in assignments:
            if assignment.due_date and assignment.due_date > now:
                # Get submission count
                submission_count = AssignmentSubmission.query.filter_by(
                    assignment_id=assignment.id
                ).filter(
                    AssignmentSubmission.status != 'draft'
                ).count()
                
                # Get students in class
                student_count = db.session.query(func.count(class_students.c.user_id)).filter(
                    class_students.c.class_id == class_id
                ).scalar() or 0
                
                upcoming_deadlines.append({
                    "assignment_id": assignment.id,
                    "assignment_title": assignment.title,
                    "due_date": assignment.due_date.isoformat(),
                    "submitted_count": submission_count,
                    "total_students": student_count,
                    "completion_rate": round((submission_count / student_count * 100), 2) if student_count > 0 else 0
                })
        
        # Sort by due date
        upcoming_deadlines.sort(key=lambda x: x['due_date'])
        
        # ========== GET LATE SUBMISSIONS DETAIL ==========
        late_submissions_detail = []
        late_subs = db.session.query(
            AssignmentSubmission, ClassAssignment
        ).join(
            ClassAssignment, AssignmentSubmission.assignment_id == ClassAssignment.id
        ).filter(
            ClassAssignment.class_id == class_id,
            AssignmentSubmission.is_late == True
        ).limit(20).all()  # Limit to 20 most recent
        
        for sub, assignment in late_subs:
            # Get student info
            student = StudentUser.query.get(sub.student_id)
            
            if student:
                late_submissions_detail.append({
                    "submission_id": sub.id,
                    "assignment_title": assignment.title,
                    "student_name": " ".join(
                        part for part in [
                            getattr(student, "first_name", None),
                            getattr(student, "last_name", None)
                        ] if part
                    ) or getattr(student, "username", "Unknown Student"),
                    "student_email": getattr(student, "email", None),
                    "submitted_at": sub.submitted_at.isoformat() if sub.submitted_at else None,
                    "due_date": assignment.due_date.isoformat() if assignment.due_date else None,
                    "penalty_applied": sub.late_penalty_applied,
                    "grade": sub.grade
                })
        
        return jsonify({
            "statistics": {
                "late_submissions": late_submissions,
                "active_extensions": active_extensions,
                "avg_late_penalty": round(avg_penalty, 2),
                "on_time_rate": on_time_rate
            },
            "assignments": assignments_data,
            "extensions": extensions_data,
            "policies": policies_data,
            "upcoming_deadlines": upcoming_deadlines[:10],  # Top 10 upcoming
            "late_submissions_detail": late_submissions_detail
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@deadlines_api.route('/instructor/api/deadlines/<int:class_id>/extensions', methods=['GET'])
@login_required
def get_deadline_extensions(class_id):
    """
    Get all active deadline extensions for a class
    """
    try:
        # Verify instructor owns this class
        cls = Class.query.get_or_404(class_id)
        if cls.created_by != current_user.id:
            if not (hasattr(current_user, 'role') and current_user.role == 'super_admin'):
                return jsonify({"error": "Unauthorized"}), 403
        
        # Get assignments for this class
        assignments = ClassAssignment.query.filter_by(class_id=class_id).all()
        assignment_ids = [a.id for a in assignments]
        
        # Get extensions
        extensions = StudentDeadlineExtension.query.filter(
            StudentDeadlineExtension.assignment_id.in_(assignment_ids)
        ).all()
        
        from user.models.user import User as StudentUser
        from instructor.models.user import InstructorUser

        extensions_data = []
        for ext in extensions:
            student = StudentUser.query.get(ext.student_id)
            assignment = ClassAssignment.query.get(ext.assignment_id)
            approver = InstructorUser.query.get(ext.approved_by) if ext.approved_by else None

            if not assignment:
                continue

            student_name_parts = [
                getattr(student, "first_name", None) if student else None,
                getattr(student, "last_name", None) if student else None
            ]
            student_name = " ".join(part for part in student_name_parts if part)
            if not student_name and student:
                student_name = getattr(student, "username", "Unknown Student")
            if not student_name:
                student_name = "Unknown Student"

            granted_by_parts = [
                getattr(approver, "first_name", None) if approver else None,
                getattr(approver, "last_name", None) if approver else None
            ]
            granted_by_name = " ".join(part for part in granted_by_parts if part)
            if not granted_by_name and approver:
                granted_by_name = getattr(approver, "username", "Instructor")
            if not granted_by_name:
                granted_by_name = "Instructor"

            extensions_data.append({
                "id": ext.id,
                "assignment_id": ext.assignment_id,
                "assignment_title": assignment.title,
                "student_id": ext.student_id,
                "student_name": student_name,
                "student_email": getattr(student, "email", None) if student else None,
                "original_due_date": ext.original_due_date.isoformat() if ext.original_due_date else None,
                "extended_due_date": ext.extended_due_date.isoformat() if ext.extended_due_date else None,
                "extension_hours": ext.extension_hours,
                "reason": ext.reason,
                "approval_notes": ext.approval_notes,
                "waive_late_penalty": ext.waive_late_penalty,
                "custom_penalty_rate": ext.custom_penalty_rate,
                "is_active": ext.is_active,
                "used": ext.used,
                "granted_by": ext.approved_by,
                "granted_by_name": granted_by_name,
                "granted_at": ext.created_at.isoformat() if ext.created_at else None
            })
        
        return jsonify({"extensions": extensions_data})
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
