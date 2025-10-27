"""
Device Count Synchronization API
Ensures consistent device counts between admin edit and dynamic simulation pages
"""

from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from instructor.controllers.simulation_controller import SimulationController
from instructor.models.simulation import Simulation
from __init__ import db
import json
from datetime import datetime

# Create blueprint
device_sync_bp = Blueprint('device_sync', __name__, url_prefix='/instructor/api/device-sync')

simulation_controller = SimulationController()

@device_sync_bp.route('/simulation/<int:simulation_id>/canonical-count', methods=['GET'])
@login_required
def get_canonical_device_count(simulation_id):
    """Get the canonical device count from both simulation config and user progress data"""
    try:
        # Get simulation from database
        simulation = Simulation.query.get_or_404(simulation_id)
        
        simulation_config = simulation.simulation_config or {}
        if isinstance(simulation_config, str):
            try:
                simulation_config = json.loads(simulation_config)
            except Exception:
                simulation_config = {}
        
        # Get device count from network_topology (admin source)
        network_topology = simulation_config.get('network_topology', {})
        database_device_count = len(network_topology.get('devices', []))
        
        # Get device count from the most recent user attempt (dynamic source)
        from instructor.models.simulation import SimulationAttempt
        latest_attempt = SimulationAttempt.query.filter_by(
            simulation_id=simulation_id,
            is_completed=False
        ).order_by(SimulationAttempt.started_at.desc()).first()
        
        user_progress_device_count = 0
        if latest_attempt and latest_attempt.session_data:
            progress_data = latest_attempt.session_data
            if isinstance(progress_data, str):
                try:
                    progress_data = json.loads(progress_data)
                except Exception:
                    progress_data = {}
            
            # Check for devices in progress data (this is what the dynamic page shows)
            if 'networkDevices' in progress_data:
                user_progress_device_count = len(progress_data.get('networkDevices', []))
            elif 'devices' in progress_data:
                user_progress_device_count = len(progress_data.get('devices', []))
        
        # Additional fallback sources
        fallback_device_count = len(simulation_config.get('devices', []))
        
        # The canonical count should be the user progress data if available (since that's what dynamic page shows)
        # Otherwise fall back to database config
        canonical_count = user_progress_device_count if user_progress_device_count > 0 else max(database_device_count, fallback_device_count)
        
        return jsonify({
            'success': True,
            'simulation_id': simulation_id,
            'canonical_device_count': canonical_count,
            'sources': {
                'network_topology_devices': database_device_count,
                'user_progress_devices': user_progress_device_count,
                'simulation_config_devices': fallback_device_count
            },
            'canonical_source': 'user_progress' if user_progress_device_count > 0 else 'database_config',
            'metadata': {
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'database_canonical'
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting canonical device count for simulation {simulation_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@device_sync_bp.route('/simulation/<int:simulation_id>/sync-devices', methods=['POST'])
@login_required
def sync_device_count(simulation_id):
    """Sync device count from dynamic simulation to admin edit"""
    try:
        data = request.get_json() or {}
        
        dynamic_device_count = data.get('device_count', 0)
        dynamic_devices = data.get('devices', [])
        source_page = data.get('source_page', 'unknown')
        
        if dynamic_device_count <= 0:
            return jsonify({
                'success': False,
                'error': 'Invalid device count provided'
            }), 400
        
        # Get simulation from database
        simulation = Simulation.query.get_or_404(simulation_id)
        
        simulation_config = simulation.simulation_config or {}
        if isinstance(simulation_config, str):
            try:
                simulation_config = json.loads(simulation_config)
            except Exception:
                simulation_config = {}
        
        # Update the network_topology with dynamic simulation data
        if 'network_topology' not in simulation_config:
            simulation_config['network_topology'] = {}
        
        # Update device count and devices if provided
        if dynamic_devices:
            simulation_config['network_topology']['devices'] = dynamic_devices
        
        # Ensure simulation config is updated with the new device data
        simulation.simulation_config = simulation_config
        simulation.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log the sync operation
        current_app.logger.info(
            f"Device count synced for simulation {simulation_id}: "
            f"{dynamic_device_count} devices from {source_page}"
        )
        
        return jsonify({
            'success': True,
            'simulation_id': simulation_id,
            'updated_device_count': dynamic_device_count,
            'source_page': source_page,
            'message': f'Device count synced successfully: {dynamic_device_count} devices',
            'metadata': {
                'timestamp': datetime.utcnow().isoformat(),
                'updated_by': current_user.username if current_user.is_authenticated else 'system'
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error syncing device count for simulation {simulation_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@device_sync_bp.route('/simulation/<int:simulation_id>/device-consistency-check', methods=['GET'])
@login_required 
def device_consistency_check(simulation_id):
    """Check device count consistency between admin and dynamic simulation"""
    try:
        simulation = Simulation.query.get_or_404(simulation_id)
        
        simulation_config = simulation.simulation_config or {}
        if isinstance(simulation_config, str):
            try:
                simulation_config = json.loads(simulation_config)
            except Exception:
                simulation_config = {}
        
        # Get device counts from different sources
        network_topology_count = len(simulation_config.get('network_topology', {}).get('devices', []))
        simulation_devices_count = len(simulation_config.get('devices', []))
        
        # Get device count from the most recent user attempt (what dynamic page actually shows)
        from instructor.models.simulation import SimulationAttempt
        latest_attempt = SimulationAttempt.query.filter_by(
            simulation_id=simulation_id,
            is_completed=False
        ).order_by(SimulationAttempt.started_at.desc()).first()
        
        user_progress_count = 0
        if latest_attempt and latest_attempt.session_data:
            progress_data = latest_attempt.session_data
            if isinstance(progress_data, str):
                try:
                    progress_data = json.loads(progress_data)
                except Exception:
                    progress_data = {}
            
            # Check for devices in progress data (this is what the dynamic page shows)
            if 'networkDevices' in progress_data:
                user_progress_count = len(progress_data.get('networkDevices', []))
            elif 'devices' in progress_data:
                user_progress_count = len(progress_data.get('devices', []))
        
        # The canonical count is the user progress (what dynamic shows) if available
        canonical_count = user_progress_count if user_progress_count > 0 else max(network_topology_count, simulation_devices_count)
        
        # Check consistency: admin should match what dynamic actually shows
        is_consistent = (network_topology_count == canonical_count) or (network_topology_count == 0 and canonical_count > 0)
        discrepancy = abs(canonical_count - network_topology_count)
        
        return jsonify({
            'success': True,
            'simulation_id': simulation_id,
            'consistency_check': {
                'is_consistent': is_consistent,
                'network_topology_devices': network_topology_count,
                'simulation_config_devices': simulation_devices_count,
                'user_progress_devices': user_progress_count,
                'canonical_count': canonical_count,
                'discrepancy': discrepancy
            },
            'recommendations': {
                'action_needed': not is_consistent,
                'suggested_action': 'Sync device counts using sync-devices endpoint' if not is_consistent else 'No action needed'
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error checking device consistency for simulation {simulation_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
