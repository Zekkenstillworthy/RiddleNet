from flask import Blueprint, jsonify, request
from admin.controllers.topology_controller import TopologyController
from admin.models.topology import Topology
from __init__ import db
from flask_login import login_required, current_user
from flask_cors import cross_origin

# Create the topology blueprint
topology_bp = Blueprint('topology', __name__, url_prefix='/admin/topology')

# Initialize the controller
controller = TopologyController()

@topology_bp.route('/', methods=['GET'])
@cross_origin()
def get_all_topologies():
    """Get all topology challenges"""
    print("GET topology/ endpoint called")
    return controller.get_all_topologies()

@topology_bp.route('/<int:topology_id>', methods=['GET'])
@cross_origin()
def get_topology(topology_id):
    """Get a specific topology challenge by ID"""
    print(f"GET topology/{topology_id} endpoint called")
    return controller.get_topology(topology_id)

@topology_bp.route('/', methods=['POST'])
@login_required
def create_topology():
    """Create a new topology challenge"""
    data = request.get_json()
    return controller.create_topology(data)

@topology_bp.route('/<int:topology_id>', methods=['PUT'])
@login_required
def update_topology(topology_id):
    """Update an existing topology challenge"""
    data = request.get_json()
    return controller.update_topology(topology_id, data)

@topology_bp.route('/<int:topology_id>', methods=['DELETE'])
@login_required
def delete_topology(topology_id):
    """Delete a topology challenge"""
    return controller.delete_topology(topology_id)

@topology_bp.route('/<int:topology_id>/preview', methods=['GET'])
@cross_origin()
def preview_topology(topology_id):
    """Get a topology in a format suitable for previewing"""
    print(f"GET topology/{topology_id}/preview endpoint called")
    return controller.preview_topology(topology_id)

@topology_bp.route('/<int:topology_id>/toggle-active', methods=['POST'])
@login_required
def toggle_active_status(topology_id):
    """Toggle the active status of a topology challenge"""
    return controller.toggle_active_status(topology_id)

@topology_bp.route('/features-guide', methods=['GET'])
@login_required
def topology_features_guide():
    """Render the topology features guide page"""
    from flask import render_template
    return render_template('admin/topology_features_guide.html')

@topology_bp.route('/types', methods=['GET'])
@cross_origin()
def get_topology_types():
    """Get all available topology types"""
    return controller.get_topology_types()

@topology_bp.route('/management', methods=['GET'])
@login_required
def topology_management():
    """Render the topology management page"""
    from flask import render_template
    return render_template('admin/topology_management.html')

@topology_bp.route('/debug/<int:topology_id>', methods=['GET'])
@cross_origin()
def debug_topology(topology_id):
    """Debug endpoint for troubleshooting"""
    try:
        topology = Topology.query.get(topology_id)
        if topology:
            return jsonify({
                "id": topology.id,
                "title": topology.title,
                "has_initial_config": topology._initial_config is not None,
                "has_expected_config": topology._expected_config is not None,
                "has_scoring_metrics": topology._scoring_metrics is not None,
                "has_device_requirements": topology._device_requirements is not None
            }), 200
        else:
            return jsonify({"error": f"Topology {topology_id} not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Error debugging topology: {str(e)}"}), 500

@topology_bp.route('/debug-json', methods=['POST'])
@cross_origin()
def debug_json():
    """Debug endpoint for testing JSON data handling"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        results = {}
        
        # Test each JSON field separately
        if 'initial_config' in data:
            try:
                test_topology = Topology()
                test_topology.initial_config = data['initial_config']
                results['initial_config'] = "OK"
            except Exception as e:
                results['initial_config'] = f"ERROR: {str(e)}"
                
        if 'expected_config' in data:
            try:
                test_topology = Topology()
                test_topology.expected_config = data['expected_config']
                results['expected_config'] = "OK"
            except Exception as e:
                results['expected_config'] = f"ERROR: {str(e)}"
                
        if 'scoring_metrics' in data:
            try:
                test_topology = Topology()
                test_topology.scoring_metrics = data['scoring_metrics']
                results['scoring_metrics'] = "OK"
            except Exception as e:
                results['scoring_metrics'] = f"ERROR: {str(e)}"
                
        if 'device_requirements' in data:
            try:
                test_topology = Topology()
                test_topology.device_requirements = data['device_requirements']
                results['device_requirements'] = "OK"
            except Exception as e:
                results['device_requirements'] = f"ERROR: {str(e)}"
                
        return jsonify({
            "message": "JSON debugging complete",
            "results": results
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error in debug-json endpoint: {str(e)}"}), 500