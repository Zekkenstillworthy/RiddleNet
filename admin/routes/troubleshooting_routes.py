from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from admin.controllers.troubleshooting_controller import TroubleshootingController
from flask_cors import cross_origin
from admin.models.troubleshooting_progress import TroubleshootingProgress
from admin import db
from datetime import datetime

# Create the troubleshooting blueprint 
troubleshooting_bp = Blueprint('troubleshooting', __name__, url_prefix='/admin/troubleshooting')

# Initialize controller
controller = TroubleshootingController()

@troubleshooting_bp.route('/', methods=['GET'])
@cross_origin()
def get_all_troubleshooting():
    """Get all troubleshooting scenarios"""
    return controller.get_all_troubleshooting()

@troubleshooting_bp.route('/<int:troubleshooting_id>', methods=['GET'])
@cross_origin()
def get_troubleshooting(troubleshooting_id):
    """Get a specific troubleshooting scenario by ID"""
    return controller.get_troubleshooting(troubleshooting_id)

@troubleshooting_bp.route('/', methods=['POST'])
@login_required
def create_troubleshooting():
    """Create a new troubleshooting scenario"""
    return controller.create_troubleshooting()

@troubleshooting_bp.route('/<int:troubleshooting_id>', methods=['PUT'])
@login_required
def update_troubleshooting(troubleshooting_id):
    """Update an existing troubleshooting scenario"""
    return controller.update_troubleshooting(troubleshooting_id)

@troubleshooting_bp.route('/<int:troubleshooting_id>', methods=['DELETE'])
@login_required
def delete_troubleshooting(troubleshooting_id):
    """Delete a troubleshooting scenario"""
    return controller.delete_troubleshooting(troubleshooting_id)
    
@troubleshooting_bp.route('/<int:troubleshooting_id>/preview', methods=['GET'])
@login_required
def preview_troubleshooting(troubleshooting_id):
    """Preview a troubleshooting scenario"""
    return jsonify(controller.preview_troubleshooting(troubleshooting_id))

@troubleshooting_bp.route('/<int:troubleshooting_id>/validate', methods=['POST'])
@cross_origin()
def validate_solution(troubleshooting_id):
    """Validate a user's solution to a troubleshooting scenario"""
    data = request.json
    user_solution = data.get('solution')
    time_taken = data.get('time_taken')
    hints_used = data.get('hints_used', 0)
    
    result = controller.validate_solution(troubleshooting_id, user_solution, time_taken, hints_used)
    
    # If the user is logged in and the solution is correct, record their progress
    if 'is_correct' in result and result['is_correct'] and current_user.is_authenticated:
        try:
            # Check if there's an existing progress record
            progress = TroubleshootingProgress.query.filter_by(
                user_id=current_user.id,
                troubleshooting_id=troubleshooting_id
            ).first()
            
            if progress:
                # Update existing progress
                progress.is_completed = True
                progress.completion_time = datetime.utcnow()
                progress.score = result['score']
                progress.attempts = progress.attempts + 1
                progress.hints_used = hints_used
                progress.user_solution = user_solution
            else:
                # Create new progress record
                progress = TroubleshootingProgress(
                    user_id=current_user.id,
                    troubleshooting_id=troubleshooting_id,
                    is_completed=True,
                    completion_time=datetime.utcnow(),
                    score=result['score'],
                    attempts=1,
                    hints_used=hints_used,
                    user_solution=user_solution
                )
                db.session.add(progress)
                
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error recording troubleshooting progress: {str(e)}")
    
    return jsonify(result)
