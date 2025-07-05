from flask import Blueprint, jsonify, request, current_app
from user.models import db, User, TopologyProgress
from flask_jwt_extended import jwt_required, get_jwt_identity
import datetime

topology_progress_bp = Blueprint('topology_progress', __name__, url_prefix='/api/topology')

@topology_progress_bp.route('/progress', methods=['POST'])
@jwt_required(optional=True)
def save_topology_progress():
    """Save user's topology progress"""
    try:
        data = request.json
        user_id = get_jwt_identity()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
        
        # Check if we have a user ID (user is logged in)
        if not user_id:
            # For anonymous users, we just acknowledge but don't save
            return jsonify({
                'status': 'success',
                'message': 'Progress acknowledged (anonymous user)'
            })
        
        # Get required fields
        topology_type = data.get('topology_type')
        completed = data.get('completed', False)
        score = data.get('score', 0)
        
        if not topology_type:
            return jsonify({
                'status': 'error',
                'message': 'Topology type is required'
            }), 400
            
        # Check if there's already a progress record for this user and topology
        progress = TopologyProgress.query.filter_by(
            user_id=user_id,
            topology_type=topology_type
        ).first()
        
        if progress:
            # Update existing record if new score is higher
            if score > progress.highest_score:
                progress.highest_score = score
                progress.completion_count += 1 if completed else 0
                progress.last_attempt = datetime.utcnow()
        else:
            # Create new progress record
            progress = TopologyProgress(
                user_id=user_id,
                topology_type=topology_type,
                highest_score=score,
                completion_count=1 if completed else 0,
                last_attempt=datetime.utcnow()
            )
            db.session.add(progress)
            
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Progress saved successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error saving topology progress: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500

@topology_progress_bp.route('/progress/<topology_type>', methods=['GET'])
@jwt_required(optional=True)
def get_topology_progress(topology_type):
    """Get user's progress for a specific topology type"""
    try:
        user_id = get_jwt_identity()
        
        if not user_id:
            # For anonymous users, return empty progress
            return jsonify({
                'status': 'success',
                'progress': None,
                'message': 'No user authenticated'
            })
            
        progress = TopologyProgress.query.filter_by(
            user_id=user_id,
            topology_type=topology_type
        ).first()
        
        if not progress:
            return jsonify({
                'status': 'success',
                'progress': None,
                'message': 'No progress found'
            })
            
        return jsonify({
            'status': 'success',
            'progress': {
                'topology_type': progress.topology_type,
                'highest_score': progress.highest_score,
                'completion_count': progress.completion_count,
                'last_attempt': progress.last_attempt.isoformat() if progress.last_attempt else None
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving topology progress: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500

@topology_progress_bp.route('/progress', methods=['GET'])
@jwt_required()
def get_all_topology_progress():
    """Get all topology progress for the current user"""
    try:
        user_id = get_jwt_identity()
            
        progress_records = TopologyProgress.query.filter_by(user_id=user_id).all()
        
        progress_list = [{
            'topology_type': p.topology_type,
            'highest_score': p.highest_score,
            'completion_count': p.completion_count,
            'last_attempt': p.last_attempt.isoformat() if p.last_attempt else None
        } for p in progress_records]
            
        return jsonify({
            'status': 'success',
            'progress': progress_list
        })
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving all topology progress: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500

