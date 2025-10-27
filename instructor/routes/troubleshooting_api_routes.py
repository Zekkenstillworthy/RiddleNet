# filepath: c:\Users\gilbe\Documents\Flask_Main_Official_2 - Copy\admin\routes\troubleshooting_api_routes.py
from flask import Blueprint, request, jsonify
from instructor.controllers.troubleshooting_controller import TroubleshootingController
from instructor.utils.instructor_auth import instructor_login_required
from flask_cors import cross_origin

# Create the troubleshooting API blueprint
troubleshooting_api_bp = Blueprint('troubleshooting_api', __name__, url_prefix='/api/admin/troubleshooting')

# Initialize controller
controller = TroubleshootingController()

@troubleshooting_api_bp.route('/list', methods=['GET'])
@instructor_login_required
@cross_origin()
def list_troubleshootings():
    """Get all troubleshooting scenarios with pagination support"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    difficulty = request.args.get('difficulty', '')
    
    return controller.list_troubleshootings(page, per_page, search, difficulty)

# Add a temporary test route that bypasses authentication for debugging
@troubleshooting_api_bp.route('/test', methods=['GET'])
@cross_origin()
def test_troubleshootings():
    """Test route to check troubleshooting API without authentication"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        difficulty = request.args.get('difficulty', '')
        
        return controller.list_troubleshootings(page, per_page, search, difficulty)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": str(e.__traceback__)}), 500

@troubleshooting_api_bp.route('/<int:troubleshooting_id>', methods=['GET'])
@instructor_login_required
@cross_origin()
def get_troubleshooting(troubleshooting_id):
    """Get details of a specific troubleshooting scenario"""
    return controller.get_troubleshooting(troubleshooting_id)

@troubleshooting_api_bp.route('/', methods=['POST'])
@instructor_login_required
@cross_origin()
def create_troubleshooting():
    """Create a new troubleshooting scenario"""
    return controller.create_troubleshooting()

@troubleshooting_api_bp.route('/<int:troubleshooting_id>', methods=['PUT'])
@instructor_login_required
@cross_origin()
def update_troubleshooting(troubleshooting_id):
    """Update an existing troubleshooting scenario"""
    return controller.update_troubleshooting(troubleshooting_id)

@troubleshooting_api_bp.route('/<int:troubleshooting_id>', methods=['DELETE'])
@instructor_login_required
@cross_origin()
def delete_troubleshooting(troubleshooting_id):
    """Delete a troubleshooting scenario"""
    return controller.delete_troubleshooting(troubleshooting_id)

@troubleshooting_api_bp.route('/stats', methods=['GET'])
@instructor_login_required
@cross_origin()
def get_troubleshooting_stats():
    """Get statistics about troubleshooting scenarios usage"""
    return controller.get_troubleshooting_stats()

@troubleshooting_api_bp.route('/preview', methods=['POST'])
@instructor_login_required
@cross_origin()
def preview_troubleshooting():
    """Preview a troubleshooting scenario before saving"""
    return controller.preview_troubleshooting()

@troubleshooting_api_bp.route('/<int:troubleshooting_id>/toggle-status', methods=['POST'])
@instructor_login_required
@cross_origin()
def toggle_troubleshooting_status(troubleshooting_id):
    """Toggle the active status of a troubleshooting scenario"""
    action = request.json.get('action', 'activate' if not request.json.get('is_active', True) else 'deactivate')
    return controller.toggle_troubleshooting_status(troubleshooting_id, action)
