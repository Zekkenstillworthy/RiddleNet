from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from __init__ import db
from instructor.models.rubric import Rubric, RubricCriterion
from instructor.models.class_content import ClassAssignment
from utils.permission_decorators import teacher_required

rubric_bp = Blueprint('rubric', __name__, url_prefix='/admin/rubrics')


@rubric_bp.route('/assignment/<int:assignment_id>', methods=['GET'])
@login_required
def get_rubric_for_assignment(assignment_id):
    rubric = Rubric.query.filter_by(assignment_id=assignment_id).first()
    return jsonify({'success': True, 'rubric': rubric.to_dict() if rubric else None})


@rubric_bp.route('/assignment/<int:assignment_id>', methods=['POST'])
@login_required
@teacher_required
def create_or_update_assignment_rubric(assignment_id):
    data = request.json or {}
    assignment = ClassAssignment.query.get_or_404(assignment_id)
    rubric = Rubric.query.filter_by(assignment_id=assignment_id).first()
    if not rubric:
        rubric = Rubric(
            name=data.get('name') or f"Rubric for {assignment.title}",
            description=data.get('description'),
            assignment_id=assignment_id,
            created_by=getattr(current_user, 'id', None),
        )
        db.session.add(rubric)
        db.session.flush()
    else:
        if 'name' in data:
            rubric.name = data['name']
        if 'description' in data:
            rubric.description = data['description']

    # Replace criteria if provided
    criteria = data.get('criteria')
    if isinstance(criteria, list):
        # delete existing
        RubricCriterion.query.filter_by(rubric_id=rubric.id).delete()
        order = 1
        for c in criteria:
            rc = RubricCriterion(
                rubric_id=rubric.id,
                title=str(c.get('title') or f'Criterion {order}')[:255],
                description=c.get('description'),
                max_points=float(c.get('max_points', 0)),
                weight=float(c.get('weight', 1.0)),
                order_index=int(c.get('order_index') or order)
            )
            order += 1
            db.session.add(rc)

    db.session.commit()
    return jsonify({'success': True, 'rubric': rubric.to_dict()})
