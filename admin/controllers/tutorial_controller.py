from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from __init__ import db
from admin.models.tutorial_system import Tutorial, TutorialStep
from admin.models.simulation import Simulation
from utils.permission_decorators import teacher_required
from utils.media_utils import save_uploaded_file


tutorial_bp = Blueprint('tutorial', __name__, url_prefix='/admin/tutorials')


@tutorial_bp.route('/<int:simulation_id>', methods=['GET'])
@login_required
def get_tutorial(simulation_id):
    tutorial = Tutorial.query.filter_by(simulation_id=simulation_id).first()
    if not tutorial:
        # lazily create an empty tutorial shell
        tutorial = Tutorial(simulation_id=simulation_id, title='Tutorial', created_by=getattr(current_user, 'id', None))
        db.session.add(tutorial)
        db.session.commit()
    return jsonify({'success': True, 'tutorial': tutorial.to_dict()})


@tutorial_bp.route('/<int:simulation_id>/steps', methods=['POST'])
@login_required
@teacher_required
def add_step(simulation_id):
    tutorial = Tutorial.query.filter_by(simulation_id=simulation_id).first()
    if not tutorial:
        tutorial = Tutorial(simulation_id=simulation_id, title='Tutorial', created_by=getattr(current_user, 'id', None))
        db.session.add(tutorial)
        db.session.flush()

    data = request.json or {}
    order_index = data.get('order_index') or (len(tutorial.steps) + 1)
    step = TutorialStep(
        tutorial_id=tutorial.id,
        order_index=order_index,
        step_type=data.get('step_type', 'text'),
        content=data.get('content'),
        media_url=data.get('media_url'),
        caption=data.get('caption'),
    )
    db.session.add(step)
    db.session.commit()
    return jsonify({'success': True, 'step': step.to_dict()})


@tutorial_bp.route('/steps/<int:step_id>', methods=['PUT'])
@login_required
@teacher_required
def update_step(step_id):
    step = TutorialStep.query.get_or_404(step_id)
    data = request.json or {}
    if 'order_index' in data:
        step.order_index = int(data['order_index'])
    if 'step_type' in data:
        step.step_type = str(data['step_type'])
    if 'content' in data:
        step.content = data['content']
    if 'media_url' in data:
        step.media_url = data['media_url']
    if 'caption' in data:
        step.caption = data['caption']
    db.session.commit()
    return jsonify({'success': True, 'step': step.to_dict()})


@tutorial_bp.route('/steps/<int:step_id>', methods=['DELETE'])
@login_required
@teacher_required
def delete_step(step_id):
    step = TutorialStep.query.get_or_404(step_id)
    db.session.delete(step)
    db.session.commit()
    return jsonify({'success': True})


@tutorial_bp.route('/<int:simulation_id>/reorder', methods=['PATCH'])
@login_required
@teacher_required
def reorder_steps(simulation_id):
    tutorial = Tutorial.query.filter_by(simulation_id=simulation_id).first_or_404()
    payload = request.json or {}
    order = payload.get('order') or []  # list of step IDs in desired order
    id_to_step = {s.id: s for s in tutorial.steps}
    for idx, step_id in enumerate(order, start=1):
        step = id_to_step.get(step_id)
        if step:
            step.order_index = idx
    db.session.commit()
    return jsonify({'success': True, 'steps': [s.to_dict() for s in tutorial.steps]})


@tutorial_bp.route('/steps/<int:step_id>/media', methods=['POST'])
@login_required
@teacher_required
def upload_step_media(step_id):
    step = TutorialStep.query.get_or_404(step_id)
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    try:
        url = save_uploaded_file(file, 'tutorials')
    except Exception as e:
        return jsonify({'error': f'Upload failed: {e}'}), 400
    step.media_url = url
    db.session.commit()
    return jsonify({'success': True, 'step': step.to_dict()})
