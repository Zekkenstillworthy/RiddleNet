from flask import Blueprint, request, jsonify
import json
from datetime import datetime
from flask_login import login_required, current_user
from utils.permission_decorators import teacher_required
from services.lab_service import LabService
# Removed unused service imports: PointEconomyService, OnboardingService, AntiCheatService
from admin.models.lab import Lab, LabSubmission
from admin.models.rubric import Rubric
from __init__ import db


lab_api = Blueprint('lab_api', __name__)


@lab_api.route('/admin/labs', methods=['POST'])
@login_required
@teacher_required
def create_lab():
    payload = request.get_json(force=True)
    lab = LabService.create_lab(owner_admin_id=getattr(current_user, 'id', None), title=payload.get('title', 'Untitled Lab'), description=payload.get('description'), class_id=payload.get('class_id'), rubric_id=payload.get('rubric_id'))
    return jsonify({'success': True, 'lab': lab.to_dict()})


@lab_api.route('/admin/labs/<int:lab_id>/topology', methods=['PUT'])
@login_required
@teacher_required
def upsert_topology(lab_id: int):
    payload = request.get_json(force=True)
    topo = LabService.upsert_topology(lab_id, payload.get('initial_config'), payload.get('expected_config'), payload.get('validations'))
    return jsonify({'success': True, 'topology_id': topo.id})


@lab_api.route('/admin/labs/<int:lab_id>/deadline', methods=['PUT'])
@login_required
@teacher_required
def set_deadline(lab_id: int):
    payload = request.get_json(force=True)
    from datetime import datetime
    due = payload.get('due_date')
    late_until = payload.get('late_allowed_until')
    parse = lambda s: datetime.fromisoformat(s) if s else None
    d = LabService.set_deadline(lab_id, parse(due), parse(late_until), float(payload.get('late_penalty_per_day', 10.0)))
    return jsonify({'success': True, 'deadline_id': d.id})


@lab_api.route('/admin/labs/<int:lab_id>/export', methods=['GET'])
@login_required
@teacher_required
def export_lab(lab_id: int):
    include_subs = request.args.get('include_submissions', '1') == '1'
    res = LabService.export_lab(lab_id, include_submissions=include_subs, created_by=getattr(current_user, 'id', None))
    return jsonify({'success': True, **res})


@lab_api.route('/admin/labs/import', methods=['POST'])
@login_required
@teacher_required
def import_lab():
    payload = request.get_json(force=True)
    data = payload.get('data')
    sha = payload.get('sha256')
    lab = LabService.import_lab(data, sha)
    return jsonify({'success': True, 'lab': lab.to_dict()})


# Student-facing minimal endpoints
@lab_api.route('/labs/<int:lab_id>/submit', methods=['POST'])
@login_required
def submit_lab(lab_id: int):
    payload = request.get_json(force=True)
    # deadline enforcement
    from admin.models.lab import LabDeadline
    d = LabDeadline.query.filter_by(lab_id=lab_id).first()
    now = datetime.utcnow()
    if d and d.due_date:
        cutoff = d.late_allowed_until or d.due_date
        if now > cutoff:
            # AntiCheatService removed - stub implementation for deadline checking
            # AntiCheatService.log_action(getattr(current_user, 'id', None), lab_id, 'deadline_circumvention', {'now': now.isoformat()}, flagged=True)
            return jsonify({'success': False, 'error': 'Submission window closed'}), 403
    sub = LabSubmission(lab_id=lab_id, student_id=getattr(current_user, 'id', None), data_json=json.dumps(payload.get('data', {})))
    db.session.add(sub)
    db.session.commit()
    # AntiCheatService removed - submissions no longer logged for anti-cheat
    # AntiCheatService.log_action(getattr(current_user, 'id', None), lab_id, 'submit', {'size': len(payload.get('data', {}))})
    # AntiCheatService.detect_rapid_submissions(getattr(current_user, 'id', None), lab_id)
    return jsonify({'success': True, 'submission_id': sub.id})


@lab_api.route('/labs/<int:lab_id>/grade/<int:submission_id>', methods=['POST'])
@login_required
@teacher_required
def grade_lab(lab_id: int, submission_id: int):
    payload = request.get_json(force=True)
    rub = None
    lab = Lab.query.get_or_404(lab_id)
    if lab.rubric_id:
        rub = Rubric.query.get(lab.rubric_id)
    sub = LabSubmission.query.get_or_404(submission_id)
    result = {'score': None}
    if rub:
        result = LabService.score_submission_with_rubric(sub, rub, payload.get('criterion_scores', {}), feedback=payload.get('feedback'))
    else:
        sub.score = payload.get('score', 0.0)
        sub.feedback = payload.get('feedback')
        db.session.commit()
        result['score'] = sub.score
    # award points equal to score (rounded)
    try:
        if sub.student_id and result.get('score') is not None:
            # PointEconomyService removed - points no longer awarded automatically
            # PointEconomyService.earn(sub.student_id, int(result['score']), reason='lab_grade')
            pass
    except Exception:
        pass
    return jsonify({'success': True, 'result': result})


@lab_api.route('/api/onboarding/steps', methods=['GET'])
def get_onboarding_steps():
    role = request.args.get('role', 'student')
    # OnboardingService removed - return empty steps
    return jsonify({'success': True, 'role': role, 'steps': []})


@lab_api.route('/labs/<int:lab_id>/validate', methods=['POST'])
@login_required
def validate_lab(lab_id: int):
    payload = request.get_json(force=True)
    result = LabService.validate_topology(lab_id, payload.get('data', {}))
    return jsonify({'success': True, 'validation': result})


@lab_api.route('/api/points/balance', methods=['GET'])
@login_required
def get_points_balance():
    # PointEconomyService removed - return default balance
    return jsonify({'success': True, 'balance': 0})


@lab_api.route('/api/points/spend', methods=['POST'])
@login_required
def spend_points():
    payload = request.get_json(force=True)
    # PointEconomyService removed - return success without spending
    return jsonify({'success': True, 'message': 'Points system disabled'}), 200
