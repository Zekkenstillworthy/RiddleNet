from flask import Blueprint, render_template, jsonify, request, session
from flask_login import current_user, login_required
import json
from admin.models.topology import Topology
from user.models.topology_progress import TopologyProgress
from __init__ import db

# Blueprint for topology-related routes
topology_bp = Blueprint('topology', __name__, url_prefix='/topology')

@topology_bp.route('/', methods=['GET'])
@login_required
def topology():
    """
    Render the topology page with data from the database
    """
    # Get all topology configurations from the database
    topology_data = {}
    topology_types = []
    
    try:
        # Query topology data from database
        topologies = Topology.query.all()
        
        for topology in topologies:
            # Extract topology type
            topology_types.append(topology.topology_type)
            
            # Parse JSON fields
            device_requirements = json.loads(topology.device_requirements) if topology.device_requirements else {}
            validation_rules = json.loads(topology.validation_rules) if topology.validation_rules else {}
            scoring_metrics = json.loads(topology.scoring_metrics) if topology.scoring_metrics else {}
            
            # Build configuration object
            topology_data[topology.topology_type] = {
                'title': topology.title,
                'description': topology.description,
                'difficulty': topology.difficulty,
                'base_score': topology.base_score,
                'device_requirements': device_requirements,
                'validation_rules': validation_rules,
                'scoring_metrics': scoring_metrics
            }
        
        # If no topologies found, use some defaults
        if not topology_types:
            topology_types = ['point-to-point', 'mesh', 'star', 'bus', 'ring', 'tree', 'hybrid']
            
        # Get user's completed topologies
        completed_topologies = []
        if current_user.is_authenticated:
            user_progress = TopologyProgress.query.filter_by(
                user_id=current_user.id, 
                completion_count__gt=0  # At least completed once
            ).all()
            
            completed_topologies = [progress.topology_type for progress in user_progress]
            
    except Exception as e:
        # Log the error but don't crash
        print(f"Error loading topology data: {str(e)}")
        
    return render_template(
        'user/topology.html',
        topology_data=topology_data,
        topology_types=topology_types,
        completed_topologies=completed_topologies
    )

@topology_bp.route('/progress', methods=['POST'])
@login_required
def save_topology_progress():
    """
    Save user's topology progress
    """
    data = request.json
    
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400
    
    try:
        topology_type = data.get('topology_type')
        completed = data.get('completed', False)
        score = data.get('score', 0)
        
        # Find existing progress or create new
        progress = TopologyProgress.query.filter_by(
            user_id=current_user.id,
            topology_type=topology_type
        ).first()
        
        if progress:
            # Update if score is higher
            if score > progress.highest_score:
                progress.highest_score = score
            
            if completed:
                progress.completion_count += 1
                
        else:
            # Create new record
            progress = TopologyProgress(
                user_id=current_user.id,
                topology_type=topology_type,
                highest_score=score,
                completion_count=1 if completed else 0
            )
            db.session.add(progress)
            
        db.session.commit()
        
        return jsonify({"status": "success", "message": "Progress saved"}), 200
        
    except Exception as e:
        print(f"Error saving topology progress: {str(e)}")
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
