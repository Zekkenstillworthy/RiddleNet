"""Instructor deadline management views."""

from datetime import datetime, timedelta
from types import SimpleNamespace

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from __init__ import db
from instructor.models.deadline_policy import (
    DeadlineCalculationLog,
    DeadlinePolicy,
    PenaltyTier,
    StudentDeadlineExtension,
)
from instructor.models.class_content import ClassAssignment
from instructor.services.deadline_service import DeadlineService
from user.models.user import User
from utils.auth_decorators import instructor_required


deadline_controller_bp = Blueprint("deadline_controller", __name__, url_prefix="/instructor")


def _safe_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_float(value, default):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_bool(value, default=False):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return default


def _hydrate_extension_students(extensions):
    student_ids = {ext.student_id for ext in extensions if ext.student_id}
    if not student_ids:
        return

    students = User.query.filter(User.id.in_(student_ids)).all()
    lookup = {student.id: student for student in students}

    for extension in extensions:
        student = lookup.get(extension.student_id)
        if not student:
            continue

        first_name = getattr(student, "first_name", None) or getattr(student, "username", "")
        last_name = getattr(student, "last_name", None) or ""
        extension.student = SimpleNamespace(
            first_name=first_name,
            last_name=last_name,
            username=getattr(student, "username", ""),
        )


def _collect_deadline_stats():
    total_policies = DeadlinePolicy.query.count()
    total_extensions = StudentDeadlineExtension.query.filter_by(is_active=True).count()

    cutoff = datetime.utcnow() - timedelta(days=30)
    recent_calculations = DeadlineCalculationLog.query.filter(
        DeadlineCalculationLog.calculated_at >= cutoff
    ).count()

    recent_extensions = (
        StudentDeadlineExtension.query.order_by(StudentDeadlineExtension.created_at.desc())
        .limit(5)
        .all()
    )
    _hydrate_extension_students(recent_extensions)

    policies = (
        DeadlinePolicy.query.order_by(DeadlinePolicy.created_at.desc())
        .limit(6)
        .all()
    )

    return {
        "total_policies": total_policies,
        "total_extensions": total_extensions,
        "recent_calculations": recent_calculations,
        "recent_extensions": recent_extensions,
        "policies": policies,
    }


@deadline_controller_bp.route("/deadline-management")
@login_required
@instructor_required
def deadline_management_dashboard():
    try:
        context = _collect_deadline_stats()
        return render_template("instructor/deadline_management.html", **context)
    except Exception as exc:
        current_app.logger.error("Failed to load deadline dashboard: %s", exc, exc_info=True)
        flash("Unable to load deadline dashboard right now.", "error")
        return redirect(url_for("class_controller.index"))


@deadline_controller_bp.route("/deadline-policies")
@login_required
@instructor_required
def deadline_policies():
    try:
        policies = DeadlinePolicy.query.order_by(DeadlinePolicy.created_at.desc()).all()
        return render_template("instructor/deadline_policies.html", policies=policies)
    except Exception as exc:
        current_app.logger.error("Failed to load deadline policies: %s", exc, exc_info=True)
        flash("Unable to load deadline policies.", "error")
        return redirect(url_for("deadline_controller.deadline_management_dashboard"))


@deadline_controller_bp.route("/deadline-policies/create", methods=["GET", "POST"])
@login_required
@instructor_required
def create_deadline_policy():
    if request.method == "GET":
        flash("Use the policy creation form within the dashboard to add new policies.", "info")
        return redirect(url_for("deadline_controller.deadline_policies"))

    payload = request.get_json(silent=True) or request.form.to_dict()
    try:
        policy = DeadlinePolicy(
            name=payload.get("name") or "Untitled Policy",
            description=payload.get("description"),
            policy_type=payload.get("policy_type", "simple"),
            simple_penalty_per_day=_safe_float(payload.get("simple_penalty_per_day"), 10.0),
            max_penalty_percentage=_safe_float(payload.get("max_penalty_percentage"), 100.0),
            grace_period_hours=_safe_int(payload.get("grace_period_hours"), 0),
            hard_cutoff_enabled=_safe_bool(payload.get("hard_cutoff_enabled")),
            hard_cutoff_days=_safe_int(payload.get("hard_cutoff_days"), 7),
            exclude_weekends=_safe_bool(payload.get("exclude_weekends")),
            exclude_holidays=_safe_bool(payload.get("exclude_holidays")),
            allow_partial_credit=_safe_bool(payload.get("allow_partial_credit"), True),
            round_penalty_up=_safe_bool(payload.get("round_penalty_up")),
            created_by=getattr(current_user, "id", None),
        )

        db.session.add(policy)
        db.session.flush()

        penalty_tiers = payload.get("penalty_tiers") or []
        for tier in penalty_tiers:
            policy.penalty_tiers.append(
                PenaltyTier(
                    policy_id=policy.id,
                    start_day=_safe_int(tier.get("start_day"), 1),
                    end_day=tier.get("end_day"),
                    penalty_percentage=_safe_float(tier.get("penalty_percentage"), 0.0),
                    penalty_type=tier.get("penalty_type", "per_day"),
                    description=tier.get("description"),
                )
            )

        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        current_app.logger.error("Failed to create deadline policy: %s", exc, exc_info=True)
        if request.is_json:
            return jsonify({"success": False, "error": str(exc)}), 500
        flash("Could not create deadline policy.", "error")
        return redirect(url_for("deadline_controller.deadline_policies"))

    if request.is_json:
        return jsonify({"success": True, "policy": policy.to_dict()})

    flash("Deadline policy created successfully.", "success")
    return redirect(url_for("deadline_controller.deadline_policies"))


@deadline_controller_bp.route("/deadline-policies/<int:policy_id>/edit")
@login_required
@instructor_required
def edit_deadline_policy(policy_id):
    flash("Detailed policy editing UI is coming soon. Please use the policy API for updates.", "info")
    return redirect(url_for("deadline_controller.deadline_policies"))


@deadline_controller_bp.route("/deadline-extensions")
@login_required
@instructor_required
def deadline_extensions():
    try:
        extensions = (
            StudentDeadlineExtension.query.order_by(StudentDeadlineExtension.created_at.desc())
            .limit(100)
            .all()
        )
        _hydrate_extension_students(extensions)
        return render_template("instructor/deadline_extensions.html", extensions=extensions)
    except Exception as exc:
        current_app.logger.error("Failed to load deadline extensions: %s", exc, exc_info=True)
        flash("Unable to load deadline extensions.", "error")
        return redirect(url_for("deadline_controller.deadline_management_dashboard"))


@deadline_controller_bp.route("/api/deadline-activity", methods=["GET"])
@login_required
@instructor_required
def deadline_activity_feed():
    activities = []

    extensions = (
        StudentDeadlineExtension.query.order_by(StudentDeadlineExtension.created_at.desc())
        .limit(5)
        .all()
    )
    _hydrate_extension_students(extensions)
    for extension in extensions:
        activities.append(
            {
                "type": "extension",
                "detail": f"Extension granted for assignment {extension.assignment_id}",
                "student": getattr(extension, "student", None).username if hasattr(extension, "student") else None,
                "timestamp": extension.created_at.isoformat() if extension.created_at else None,
            }
        )

    logs = (
        DeadlineCalculationLog.query.order_by(DeadlineCalculationLog.calculated_at.desc())
        .limit(5)
        .all()
    )
    for log in logs:
        activities.append(
            {
                "type": "calculation",
                "detail": f"Penalty calculated with method {log.calculation_method}",
                "timestamp": log.calculated_at.isoformat() if log.calculated_at else None,
                "penalty": log.applied_penalty_percentage,
            }
        )

    activities.sort(key=lambda item: item.get("timestamp") or "", reverse=True)
    return jsonify({"success": True, "activities": activities})


@deadline_controller_bp.route("/deadlines/<int:assignment_id>/preview", methods=["GET"])
@login_required
@instructor_required
def preview_deadline(assignment_id):
    assignment = ClassAssignment.query.get_or_404(assignment_id)
    availability = DeadlineService.check_assignment_availability(assignment)
    penalty_preview = {}

    submissions = getattr(assignment, "submissions", None)
    if submissions:
        submission = submissions[0]
        _, penalty_preview = DeadlineService.apply_penalty_to_grade(submission, submission.score or 0)

    return render_template(
        "instructor/partials/deadline_preview.html",
        assignment=assignment,
        availability=availability,
        penalty_preview=penalty_preview,
    )


@deadline_controller_bp.route("/assignment/<int:assignment_id>/deadline-settings", methods=["GET"])
@login_required
@instructor_required
def assignment_deadline_settings(assignment_id):
    """Get deadline settings for a specific assignment"""
    try:
        from instructor.models.deadline_policy import AssignmentAvailabilityWindow
        
        assignment = ClassAssignment.query.get_or_404(assignment_id)
        
        # Get availability window if exists
        availability = AssignmentAvailabilityWindow.query.filter_by(
            assignment_id=assignment_id
        ).first()
        
        # Get active extensions for this assignment
        extensions = StudentDeadlineExtension.query.filter_by(
            assignment_id=assignment_id,
            is_active=True
        ).all()
        _hydrate_extension_students(extensions)
        
        # Get deadline policy if assigned
        deadline_policy = None
        if hasattr(assignment, 'deadline_policy_id') and assignment.deadline_policy_id:
            deadline_policy = DeadlinePolicy.query.get(assignment.deadline_policy_id)
        
        # Get all available policies
        all_policies = DeadlinePolicy.query.order_by(DeadlinePolicy.name).all()
        
        # If accessed via AJAX, return JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'assignment': {
                    'id': assignment.id,
                    'title': assignment.title,
                    'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
                    'description': assignment.description
                },
                'availability': availability.to_dict() if availability else None,
                'extensions': [ext.to_dict() for ext in extensions],
                'deadline_policy': deadline_policy.to_dict() if deadline_policy else None,
                'available_policies': [p.to_dict() for p in all_policies]
            })
        
        # Otherwise render template (for backward compatibility)
        return render_template(
            "instructor/deadline_settings.html",
            assignment=assignment,
            availability=availability,
            extensions=extensions,
            deadline_policy=deadline_policy,
            available_policies=all_policies
        )
        
    except Exception as exc:
        current_app.logger.error("Failed to load deadline settings: %s", exc, exc_info=True)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': str(exc)}), 500
        flash("Unable to load deadline settings.", "error")
        return redirect(url_for("deadline_controller.deadline_management_dashboard"))
