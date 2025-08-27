"""
Modern Simulation Controller with Enhanced Validation
Handles enhanced validation across all simulation editors
"""

from flask import current_app, request, jsonify
from admin import db
from admin.models.simulation import Simulation
from admin.config.simulation_config import ValidationConfig
from datetime import datetime
import json


class ModernSimulationController:
    """Enhanced simulation controller with network validation"""
    
    def __init__(self):
        self.validation_config = ValidationConfig()
    
    def get_enhanced_validation_config(self, simulation_id):
        """Get enhanced validation configuration for a simulation"""
        try:
            simulation = Simulation.query.get(simulation_id)
            if not simulation:
                return {'error': 'Simulation not found'}
            
            # Get enhanced validation config from simulation_config
            sim_config = simulation.simulation_config or {}
            enhanced_config = sim_config.get('enhanced_validation', {})
            
            # Merge with defaults if incomplete
            default_config = ValidationConfig.get_default_config()['enhanced_validation']
            for key, value in default_config.items():
                if key not in enhanced_config:
                    enhanced_config[key] = value
            
            return {
                'success': True,
                'validation_config': enhanced_config,
                'device_requirements': ValidationConfig.DEVICE_CONFIG_REQUIREMENTS,
                'connection_rules': ValidationConfig.PHYSICAL_CONNECTION_RULES,
                'default_tests': ValidationConfig.DEFAULT_CONNECTIVITY_TESTS
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting validation config for simulation {simulation_id}: {str(e)}")
            return {'error': 'Failed to get validation configuration'}
    
    def save_enhanced_validation_config(self, simulation_id, validation_data):
        """Save enhanced validation configuration for a simulation"""
        try:
            simulation = Simulation.query.get(simulation_id)
            if not simulation:
                return {'error': 'Simulation not found'}
            
            # Get current simulation config
            sim_config = simulation.simulation_config or {}
            
            # Update enhanced validation section
            sim_config['enhanced_validation'] = validation_data
            
            # Save back to simulation
            simulation.simulation_config = sim_config
            simulation.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Enhanced validation configuration saved successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error saving validation config for simulation {simulation_id}: {str(e)}")
            return {'error': 'Failed to save validation configuration'}
    
    def validate_simulation_state(self, simulation_id, topology_data):
        """Validate current simulation state against enhanced validation rules"""
        try:
            simulation = Simulation.query.get(simulation_id)
            if not simulation:
                return {'error': 'Simulation not found'}
            
            # Get validation configuration
            config_result = self.get_enhanced_validation_config(simulation_id)
            if 'error' in config_result:
                return config_result
            
            validation_config = config_result['validation_config']
            
            # Initialize validation results
            validation_results = {
                'overall_state': ValidationConfig.VALIDATION_STATES['DISCONNECTED'],
                'configuration_valid': False,
                'physical_valid': False,
                'connectivity_valid': False,
                'errors': [],
                'warnings': [],
                'device_statuses': {},
                'connection_statuses': {},
                'test_results': {}
            }
            
            devices = topology_data.get('devices', [])
            connections = topology_data.get('connections', [])
            
            # 1. Configuration Validation
            config_results = self._validate_device_configurations(devices, validation_config)
            validation_results.update(config_results)
            
            # 2. Physical Connection Validation
            physical_results = self._validate_physical_connections(devices, connections, validation_config)
            validation_results.update(physical_results)
            
            # 3. Determine overall state
            overall_state = self._determine_validation_state(validation_results)
            validation_results['overall_state'] = overall_state
            
            return {
                'success': True,
                'validation_results': validation_results
            }
            
        except Exception as e:
            current_app.logger.error(f"Error validating simulation {simulation_id}: {str(e)}")
            return {'error': 'Failed to validate simulation state'}
    
    def run_connectivity_tests(self, simulation_id, topology_data, test_config):
        """Run connectivity tests for the simulation"""
        try:
            simulation = Simulation.query.get(simulation_id)
            if not simulation:
                return {'error': 'Simulation not found'}
            
            devices = topology_data.get('devices', [])
            connections = topology_data.get('connections', [])
            
            # Generate connectivity test results
            test_results = self._run_simulated_connectivity_tests(devices, connections, test_config)
            
            return {
                'success': True,
                'test_results': test_results
            }
            
        except Exception as e:
            current_app.logger.error(f"Error running connectivity tests for simulation {simulation_id}: {str(e)}")
            return {'error': 'Failed to run connectivity tests'}
    
    def _validate_device_configurations(self, devices, validation_config):
        """Validate device configurations"""
        results = {
            'configuration_valid': True,
            'device_statuses': {},
            'config_errors': []
        }
        
        config_requirements = validation_config.get('configuration_requirements', {})
        
        for device in devices:
            device_id = device.get('id')
            device_type = device.get('type')
            device_config = device.get('config', {})
            
            # Initialize device status
            device_status = {
                'configured': False,
                'missing_fields': [],
                'validation_errors': []
            }
            
            if config_requirements.get('require_ip_assignment', True):
                # Validate IP configuration
                is_valid, message = ValidationConfig.validate_device_config(device_type, device_config)
                if not is_valid:
                    device_status['validation_errors'].append(message)
                    results['configuration_valid'] = False
                    results['config_errors'].append(f"Device {device.get('name', device_id)}: {message}")
                else:
                    device_status['configured'] = True
            
            results['device_statuses'][device_id] = device_status
        
        return results
    
    def _validate_physical_connections(self, devices, connections, validation_config):
        """Validate physical connections"""
        results = {
            'physical_valid': True,
            'connection_statuses': {},
            'physical_errors': []
        }
        
        physical_validation = validation_config.get('physical_validation', {})
        
        # Create device lookup
        device_lookup = {device['id']: device for device in devices}
        
        for connection in connections:
            conn_id = f"{connection.get('source')}_{connection.get('target')}"
            source_device = device_lookup.get(connection.get('source'))
            target_device = device_lookup.get(connection.get('target'))
            cable_type = connection.get('cable_type', 'ethernet')
            
            connection_status = {
                'valid': False,
                'errors': []
            }
            
            if not source_device or not target_device:
                connection_status['errors'].append('Invalid device reference in connection')
                results['physical_valid'] = False
                results['physical_errors'].append(f"Connection {conn_id}: Invalid device reference")
            else:
                # Validate connection compatibility
                is_valid, message = ValidationConfig.validate_physical_connection(
                    source_device['type'], 
                    target_device['type'], 
                    cable_type
                )
                
                if not is_valid:
                    connection_status['errors'].append(message)
                    results['physical_valid'] = False
                    results['physical_errors'].append(f"Connection {conn_id}: {message}")
                else:
                    connection_status['valid'] = True
            
            results['connection_statuses'][conn_id] = connection_status
        
        return results
    
    def _determine_validation_state(self, validation_results):
        """Determine overall validation state based on results"""
        if not validation_results['configuration_valid']:
            return ValidationConfig.VALIDATION_STATES['DISCONNECTED']
        elif not validation_results['physical_valid']:
            return ValidationConfig.VALIDATION_STATES['CONFIGURED']
        elif not validation_results['connectivity_valid']:
            return ValidationConfig.VALIDATION_STATES['CONNECTED']
        else:
            return ValidationConfig.VALIDATION_STATES['WORKING']
    
    def _run_simulated_connectivity_tests(self, devices, connections, test_config):
        """Run simulated connectivity tests"""
        test_results = {}
        
        # Create network graph for reachability testing
        device_lookup = {device['id']: device for device in devices}
        adjacency = {}
        
        # Build adjacency list
        for device in devices:
            adjacency[device['id']] = []
        
        for connection in connections:
            source = connection.get('source')
            target = connection.get('target')
            if source and target:
                adjacency[source].append(target)
                adjacency[target].append(source)
        
        # Generate ping tests between end devices
        end_devices = [d for d in devices if d.get('type') in ['pc', 'server']]
        
        for i, source_device in enumerate(end_devices):
            for target_device in end_devices[i+1:]:
                test_id = f"ping_{source_device['id']}_{target_device['id']}"
                
                # Simple reachability test using BFS
                reachable = self._is_reachable(source_device['id'], target_device['id'], adjacency)
                
                test_results[test_id] = {
                    'type': 'ping',
                    'source': source_device['name'],
                    'target': target_device['name'],
                    'result': 'pass' if reachable else 'fail',
                    'message': 'Connectivity verified' if reachable else 'No connectivity path found',
                    'timestamp': datetime.utcnow().isoformat()
                }
        
        return test_results
    
    def _is_reachable(self, source, target, adjacency):
        """Check if target is reachable from source using BFS"""
        if source == target:
            return True
        
        visited = set()
        queue = [source]
        visited.add(source)
        
        while queue:
            current = queue.pop(0)
            for neighbor in adjacency.get(current, []):
                if neighbor == target:
                    return True
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return False


# Global instance
modern_simulation_controller = ModernSimulationController()