from flask import Blueprint, jsonify, request
from instructor.models.topology import Topology
from __init__ import db
from flask_cors import cross_origin

# Create blueprint for API endpoints
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/topology/config/<topology_type>', methods=['GET'])
@cross_origin()
def get_topology_config(topology_type):
    """Endpoint to get topology configuration including scoring metrics and device requirements"""
    try:
        # First try to get from database
        topology = db.session.query(Topology).filter_by(topology_type=topology_type).first()
        
        if topology:
            return jsonify({
                'topology_type': topology.topology_type,
                'base_score': topology.base_score,
                'time_bonus': topology.time_bonus,
                'perfect_match_bonus': topology.perfect_match_bonus,
                'scoring_metrics': topology.scoring_metrics,
                'device_requirements': topology.device_requirements
            })
        
        # Fallback to default configuration if not in database
        default_scoring = {
            'time_efficiency': 10,
            'config_process': 25,
            'design_layout': 20,
            'completeness': 20,
            'correctness': 25
        }
        
        default_requirements = {
            'point-to-point': {'pc': 2, 'router': 0, 'switch': 0, 'server': 0},
            'star': {'pc': 3, 'router': 0, 'switch': 1, 'server': 0},
            'mesh': {'pc': 0, 'router': 4, 'switch': 0, 'server': 0},
            'bus': {'pc': 4, 'router': 0, 'switch': 0, 'server': 0},
            'ring': {'pc': 0, 'router': 0, 'switch': 4, 'server': 0},
            'tree': {'pc': 4, 'router': 1, 'switch': 2, 'server': 0},
            'hybrid': {'pc': 3, 'router': 1, 'switch': 2, 'server': 1}
        }
        
        return jsonify({
            'topology_type': topology_type,
            'base_score': 10,
            'time_bonus': 5,
            'perfect_match_bonus': 5,
            'scoring_metrics': default_scoring,
            'device_requirements': default_requirements.get(topology_type, {'pc': 2, 'router': 0, 'switch': 0, 'server': 0})
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/topology/types', methods=['GET'])
@cross_origin()
def get_topology_types():
    """Get all available topology types"""
    try:
        # For a real app, you would get these from your database
        topology_types = ['point-to-point', 'mesh', 'star', 'bus', 'ring', 'tree', 'hybrid']
        return jsonify({
            'status': 'success',
            'topology_types': topology_types
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
