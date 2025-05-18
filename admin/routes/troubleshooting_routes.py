from flask import Blueprint, request, jsonify
from flask_login import login_required
from admin.controllers.troubleshooting_controller import TroubleshootingController
from flask_cors import cross_origin

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
