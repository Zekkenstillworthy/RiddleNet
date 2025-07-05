from __init__ import db
from user.models.performance_feedback import PerformanceFeedback, FeedbackSession
from socket_manager import socketio
from flask_socketio import emit
import uuid
import json
from datetime import datetime

class FeedbackService:
    """
    Service for managing real-time performance feedback during troubleshooting scenarios
    """
    
    def __init__(self):
        self.active_sessions = {}  # session_id -> FeedbackSession
        self.feedback_rules = self.load_feedback_rules()
    
    def load_feedback_rules(self):
        """Load feedback rules for different scenarios and actions"""
        return {
            'device_placement': {
                'correct_placement': {
                    'type': 'success',
                    'message': 'Great! Device placed correctly.',
                    'score': 10,
                    'icon': 'fas fa-check-circle',
                    'color': '#4CAF50'
                },
                'incorrect_placement': {
                    'type': 'error',
                    'message': 'Device placement is incorrect. Check the network topology requirements.',
                    'score': -5,
                    'icon': 'fas fa-times-circle',
                    'color': '#f44336'
                },
                'duplicate_placement': {
                    'type': 'warning',
                    'message': 'Device already exists in this location.',
                    'score': 0,
                    'icon': 'fas fa-exclamation-triangle',
                    'color': '#FF9800'
                }
            },
            'connection_creation': {
                'valid_connection': {
                    'type': 'success',
                    'message': 'Connection established successfully!',
                    'score': 15,
                    'icon': 'fas fa-link',
                    'color': '#4CAF50'
                },
                'invalid_connection': {
                    'type': 'error',
                    'message': 'Invalid connection. Check device compatibility.',
                    'score': -5,
                    'icon': 'fas fa-unlink',
                    'color': '#f44336'
                },
                'redundant_connection': {
                    'type': 'warning',
                    'message': 'Connection already exists between these devices.',
                    'score': 0,
                    'icon': 'fas fa-exclamation-triangle',
                    'color': '#FF9800'
                }
            },
            'cli_command': {
                'correct_command': {
                    'type': 'success',
                    'message': 'Command executed successfully!',
                    'score': 20,
                    'icon': 'fas fa-terminal',
                    'color': '#4CAF50'
                },
                'incorrect_command': {
                    'type': 'error',
                    'message': 'Command failed. Check syntax and parameters.',
                    'score': -3,
                    'icon': 'fas fa-times-circle',
                    'color': '#f44336'
                },
                'helpful_command': {
                    'type': 'success',
                    'message': 'Good troubleshooting approach!',
                    'score': 10,
                    'icon': 'fas fa-lightbulb',
                    'color': '#2196F3'
                }
            },
            'configuration': {
                'correct_config': {
                    'type': 'success',
                    'message': 'Configuration applied correctly!',
                    'score': 25,
                    'icon': 'fas fa-cogs',
                    'color': '#4CAF50'
                },
                'incorrect_config': {
                    'type': 'error',
                    'message': 'Configuration error. Review the requirements.',
                    'score': -5,
                    'icon': 'fas fa-exclamation-triangle',
                    'color': '#f44336'
                },
                'partial_config': {
                    'type': 'warning',
                    'message': 'Configuration partially correct. Continue with remaining settings.',
                    'score': 10,
                    'icon': 'fas fa-cog',
                    'color': '#FF9800'
                }
            }
        }
    
    def start_session(self, user_id, scenario_id, lobby_id=None):
        """Start a new feedback session"""
        import uuid
        session_id = str(uuid.uuid4())
        
        # Create session record
        session = FeedbackSession(
            session_id=session_id,
            user_id=user_id,
            scenario_id=scenario_id,
            lobby_id=lobby_id,
            is_collaborative=lobby_id is not None
        )
        
        db.session.add(session)
        db.session.commit()
        
        # Track active session
        self.active_sessions[session_id] = session
        
        return {
            'session_id': session_id,
            'user_id': user_id,
            'scenario_id': scenario_id,
            'lobby_id': lobby_id,
            'start_time': session.start_time.isoformat()
        }
    
    def generate_hint(self, session_id, user_id, current_step, scenario_context=None):
        """Generate contextual hints based on current progress and common mistakes"""
        hints = {
            'device_placement': [
                "Start by placing the central networking device (router or switch) first.",
                "Consider the physical layout - devices should be placed logically based on their function.",
                "Remember that routers connect different networks, while switches connect devices within the same network.",
                "Check if you have all required device types for this scenario."
            ],
            'connection_creation': [
                "Use Ethernet cables to connect devices to switches.",
                "Serial cables are typically used for router-to-router connections.",
                "Make sure you're connecting the right interfaces (FastEthernet, Serial, etc.).",
                "Each connection should serve a purpose in your network topology."
            ],
            'configuration': [
                "Start with basic interface configuration (IP addresses, subnet masks).",
                "Remember to enable interfaces with the 'no shutdown' command.",
                "Configure routing protocols if devices are in different networks.",
                "Test connectivity with ping commands after configuration."
            ],
            'general': [
                "Read the scenario requirements carefully.",
                "Think about the logical flow of network traffic.",
                "Consider both Layer 2 (switching) and Layer 3 (routing) requirements.",
                "Don't forget to save your configuration changes."
            ]
        }
        
        # Get user's recent actions to provide more specific hints
        recent_feedback = PerformanceFeedback.query.filter_by(
            session_id=session_id, 
            user_id=user_id
        ).order_by(PerformanceFeedback.action_timestamp.desc()).limit(5).all()
        
        # Analyze recent errors for specific guidance
        recent_errors = [f for f in recent_feedback if f.feedback_type == 'error']
        
        if recent_errors:
            error_types = [e.action_type for e in recent_errors]
            most_common_error = max(set(error_types), key=error_types.count)
            
            # Provide specific hint for the most common error
            specific_hints = hints.get(most_common_error, hints['general'])
        else:
            # Provide hints for current step
            specific_hints = hints.get(current_step, hints['general'])
        
        # Select a random hint from the appropriate category
        import random
        selected_hint = random.choice(specific_hints)
        
        return {
            'message': selected_hint,
            'hint_type': current_step,
            'category': 'contextual',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def validate_complete_solution(self, session_id, user_id, solution_data, requirements):
        """Validate complete solution against scenario requirements"""
        score = 0
        feedback_details = []
        max_score = 100
        
        # Validate device placement (30 points)
        devices = solution_data.get('devices', [])
        required_devices = requirements.get('devices', [])
        
        device_score = 0
        if len(devices) >= len(required_devices):
            device_score = 20
            # Check device types
            device_types = [d.get('type', '') for d in devices]
            required_types = [d.get('type', '') for d in required_devices]
            
            type_matches = sum(1 for req_type in required_types if req_type in device_types)
            device_score += (type_matches / len(required_types)) * 10
            
        score += device_score
        feedback_details.append(f"Device placement: {device_score}/30 points")
        
        # Validate connections (25 points)
        connections = solution_data.get('connections', [])
        required_connections = requirements.get('connections', [])
        
        connection_score = 0
        if connections:
            # Basic connectivity check
            connection_score = min(len(connections) / max(len(required_connections), 1) * 25, 25)
        
        score += connection_score
        feedback_details.append(f"Network connections: {connection_score}/25 points")
        
        # Validate configuration (35 points)
        configurations = solution_data.get('configurations', {})
        required_configs = requirements.get('configurations', {})
        
        config_score = 0
        if configurations:
            # Check IP addressing
            ip_score = self._validate_ip_addressing(configurations, required_configs)
            config_score += ip_score
            
            # Check routing configuration
            routing_score = self._validate_routing_config(configurations, required_configs)
            config_score += routing_score
        
        score += config_score
        feedback_details.append(f"Configuration: {config_score}/35 points")
        
        # Connectivity test (10 points)
        connectivity_score = self._validate_connectivity(solution_data, requirements)
        score += connectivity_score
        feedback_details.append(f"Connectivity test: {connectivity_score}/10 points")
        
        # Generate detailed feedback message
        completion_percentage = (score / max_score) * 100
        
        if completion_percentage >= 90:
            overall_feedback = "Excellent work! Your solution demonstrates mastery of networking concepts."
        elif completion_percentage >= 75:
            overall_feedback = "Good solution! A few minor improvements could make it even better."
        elif completion_percentage >= 60:
            overall_feedback = "Your solution addresses most requirements but needs some refinement."
        else:
            overall_feedback = "Your solution needs significant improvements. Review the requirements carefully."
        
        return {
            'score': completion_percentage,
            'detailed_feedback': overall_feedback,
            'breakdown': feedback_details,
            'areas_for_improvement': self._identify_improvement_areas(solution_data, requirements, score),
            'completion_percentage': completion_percentage,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _validate_ip_addressing(self, configurations, required_configs):
        """Validate IP addressing configuration"""
        score = 0
        
        # Check if IP addresses are configured
        for device_id, config in configurations.items():
            if 'interfaces' in config:
                for interface, settings in config['interfaces'].items():
                    if 'ip_address' in settings and 'subnet_mask' in settings:
                        score += 2  # Points for proper IP configuration
        
        return min(score, 15)  # Max 15 points for IP addressing
    
    def _validate_routing_config(self, configurations, required_configs):
        """Validate routing configuration"""
        score = 0
        
        # Check for routing protocols or static routes
        for device_id, config in configurations.items():
            if 'routing' in config:
                if config['routing'].get('protocol') or config['routing'].get('static_routes'):
                    score += 10  # Points for routing configuration
        
        return min(score, 20)  # Max 20 points for routing
    
    def _validate_connectivity(self, solution_data, requirements):
        """Validate end-to-end connectivity"""
        # Simple connectivity validation based on solution completeness
        devices = solution_data.get('devices', [])
        connections = solution_data.get('connections', [])
        configurations = solution_data.get('configurations', {})
        
        if devices and connections and configurations:
            return 10  # Full connectivity score
        elif devices and connections:
            return 6   # Partial connectivity
        elif devices:
            return 3   # Basic setup
        
        return 0
    
    def _identify_improvement_areas(self, solution_data, requirements, current_score):
        """Identify specific areas where the solution can be improved"""
        areas = []
        
        devices = solution_data.get('devices', [])
        connections = solution_data.get('connections', [])
        configurations = solution_data.get('configurations', {})
        
        required_devices = requirements.get('devices', [])
        required_connections = requirements.get('connections', [])
        
        if len(devices) < len(required_devices):
            areas.append("Add missing network devices as specified in requirements")
        
        if len(connections) < len(required_connections):
            areas.append("Create additional network connections for proper topology")
        
        if not configurations:
            areas.append("Configure device interfaces with appropriate IP addresses")
        
        if current_score < 60:
            areas.append("Review scenario requirements and ensure all components are addressed")
        
        return areas
    
    def get_session_progress(self, session_id):
        """Get detailed progress information for a session"""
        if session_id not in self.active_sessions:
            # Try to get from database
            session = FeedbackSession.query.filter_by(session_id=session_id).first()
            if not session:
                return None
        else:
            session = self.active_sessions[session_id]
        
        # Get all feedback for this session
        feedback_entries = PerformanceFeedback.query.filter_by(session_id=session_id).all()
        
        # Calculate progress metrics
        total_actions = len(feedback_entries)
        successful_actions = len([f for f in feedback_entries if f.feedback_type == 'success'])
        error_actions = len([f for f in feedback_entries if f.feedback_type == 'error'])
        warning_actions = len([f for f in feedback_entries if f.feedback_type == 'warning'])
        
        current_score = sum(f.feedback_score for f in feedback_entries)
        
        # Get latest progress percentage
        latest_progress = 0
        if feedback_entries:
            latest_feedback = max(feedback_entries, key=lambda x: x.action_timestamp)
            latest_progress = latest_feedback.scenario_progress or 0
        
        return {
            'session_id': session_id,
            'total_actions': total_actions,
            'successful_actions': successful_actions,
            'error_actions': error_actions,
            'warning_actions': warning_actions,
            'current_score': current_score,
            'progress_percentage': latest_progress,
            'success_rate': (successful_actions / total_actions * 100) if total_actions > 0 else 0,
            'session_duration': self._calculate_session_duration(session),
            'action_breakdown': self._get_action_breakdown(feedback_entries),
            'recent_actions': [f.to_dict() for f in feedback_entries[-5:]]  # Last 5 actions
        }
    
    def _calculate_session_duration(self, session):
        """Calculate session duration in minutes"""
        if session.end_time:
            duration = (session.end_time - session.start_time).total_seconds()
        else:
            duration = (datetime.utcnow() - session.start_time).total_seconds()
        
        return round(duration / 60, 2)  # Return in minutes
    
    def end_session(self, session_id):
        """End a feedback session and calculate final metrics"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.end_time = datetime.utcnow()
            session.total_duration = (session.end_time - session.start_time).total_seconds()
            session.is_completed = True
            
            # Update aggregated metrics
            session.update_metrics()
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            return session.to_dict()
        return None
    
    def validate_action(self, action_type, action_data, scenario_context=None):
        """Validate an action and determine appropriate feedback"""
        if action_type == 'device_placement':
            return self._validate_device_placement(action_data, scenario_context)
        elif action_type == 'connection_creation':
            return self._validate_connection_creation(action_data, scenario_context)
        elif action_type == 'cli_command':
            return self._validate_cli_command(action_data, scenario_context)
        elif action_type == 'configuration':
            return self._validate_configuration(action_data, scenario_context)
        else:
            return self._default_validation(action_type, action_data)
    
    def _validate_device_placement(self, action_data, scenario_context):
        """Validate device placement actions"""
        device_type = action_data.get('device_type')
        position = action_data.get('position', {})
        existing_devices = scenario_context.get('devices', []) if scenario_context else []
        
        # Check for duplicate placement
        for device in existing_devices:
            if (device.get('x', 0) == position.get('x', 0) and 
                device.get('y', 0) == position.get('y', 0)):
                return 'duplicate_placement'
        
        # Check if placement follows network topology rules
        if scenario_context and 'required_topology' in scenario_context:
            required_devices = scenario_context['required_topology'].get('devices', [])
            if device_type in [d['type'] for d in required_devices]:
                return 'correct_placement'
            else:
                return 'incorrect_placement'
        
        # Default to correct if no specific rules
        return 'correct_placement'
    
    def _validate_connection_creation(self, action_data, scenario_context):
        """Validate connection creation actions"""
        device1_id = action_data.get('device1_id')
        device2_id = action_data.get('device2_id')
        connection_type = action_data.get('connection_type', 'ethernet')
        
        # Check for existing connections
        existing_connections = scenario_context.get('connections', []) if scenario_context else []
        for conn in existing_connections:
            if ((conn.get('device1_id') == device1_id and conn.get('device2_id') == device2_id) or
                (conn.get('device1_id') == device2_id and conn.get('device2_id') == device1_id)):
                return 'redundant_connection'
        
        # Validate connection compatibility
        if scenario_context and 'devices' in scenario_context:
            devices = scenario_context['devices']
            device1 = next((d for d in devices if d.get('id') == device1_id), None)
            device2 = next((d for d in devices if d.get('id') == device2_id), None)
            
            if device1 and device2:
                # Check if devices can be connected
                if self._can_connect_devices(device1, device2, connection_type):
                    return 'valid_connection'
                else:
                    return 'invalid_connection'
        
        return 'valid_connection'
    
    def _validate_cli_command(self, action_data, scenario_context):
        """Validate CLI command execution"""
        command = action_data.get('command', '').strip().lower()
        device_id = action_data.get('device_id')
        expected_output = action_data.get('expected_output', '')
        
        # Define helpful commands
        helpful_commands = [
            'ping', 'ipconfig', 'show ip route', 'show running-config',
            'traceroute', 'nslookup', 'arp', 'netstat'
        ]
        
        # Check if command is in helpful list
        if any(cmd in command for cmd in helpful_commands):
            return 'helpful_command'
        
        # Check against expected commands for scenario
        if scenario_context and 'expected_commands' in scenario_context:
            expected_commands = scenario_context['expected_commands']
            if command in expected_commands:
                return 'correct_command'
        
        # Check for common mistake patterns
        if command.startswith('config') and 'terminal' not in command:
            return 'incorrect_command'
        
        return 'correct_command'
    
    def _validate_configuration(self, action_data, scenario_context):
        """Validate device configuration actions"""
        device_id = action_data.get('device_id')
        config_type = action_data.get('config_type')
        config_value = action_data.get('config_value')
        
        if scenario_context and 'expected_configs' in scenario_context:
            expected_configs = scenario_context['expected_configs']
            device_configs = expected_configs.get(device_id, {})
            
            if config_type in device_configs:
                if device_configs[config_type] == config_value:
                    return 'correct_config'
                else:
                    return 'incorrect_config'
        
        return 'partial_config'
    
    def _can_connect_devices(self, device1, device2, connection_type):
        """Check if two devices can be connected with the given connection type"""
        # Define connection compatibility rules
        compatibility_rules = {
            'ethernet': ['router', 'switch', 'pc', 'server'],
            'serial': ['router', 'router'],
            'console': ['pc', 'router', 'switch'],
            'fiber': ['switch', 'router']
        }
        
        device1_type = device1.get('type', '').lower()
        device2_type = device2.get('type', '').lower()
        
        compatible_types = compatibility_rules.get(connection_type, [])
        
        return device1_type in compatible_types and device2_type in compatible_types
    
    def _default_validation(self, action_type, action_data):
        """Default validation for unknown action types"""
        return 'correct_placement'  # Default to success
    
    def record_feedback(self, session_id, user_id, action_type, action_data, scenario_context=None):
        """Record feedback for a user action"""
        
        # Validate the action
        validation_result = self.validate_action(action_type, action_data, scenario_context)
        
        # Get feedback configuration
        feedback_config = self.feedback_rules.get(action_type, {}).get(validation_result, {})
        
        if not feedback_config:
            # Fallback feedback
            feedback_config = {
                'type': 'success',
                'message': 'Action completed.',
                'score': 5,
                'icon': 'fas fa-check',
                'color': '#4CAF50'
            }
        
        # Calculate progress
        progress = self._calculate_progress(session_id, action_type, validation_result)
        
        # Create feedback record
        feedback = PerformanceFeedback.create_feedback(
            user_id=user_id,
            session_id=session_id,
            scenario_id=action_data.get('scenario_id', 'unknown'),
            action_type=action_type,
            feedback_type=feedback_config['type'],
            feedback_message=feedback_config['message'],
            feedback_score=feedback_config['score'],
            action_details=action_data,
            device_id=action_data.get('device_id'),
            connection_ids=action_data.get('connection_ids', []),
            cli_command=action_data.get('command'),
            scenario_progress=progress,
            response_time=action_data.get('response_time'),
            lobby_id=action_data.get('lobby_id')
        )
        
        # Prepare real-time feedback data
        feedback_data = {
            'feedback_id': feedback.id,
            'type': feedback_config['type'],
            'message': feedback_config['message'],
            'score': feedback_config['score'],
            'icon': feedback_config['icon'],
            'color': feedback_config['color'],
            'progress': progress,
            'action_type': action_type,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Update session if active
        if session_id in self.active_sessions:
            self.active_sessions[session_id].update_metrics()
        
        return feedback_data
    
    def _calculate_progress(self, session_id, action_type, validation_result):
        """Calculate scenario progress based on completed actions"""
        # Get all feedback for this session
        feedback_count = PerformanceFeedback.query.filter_by(
            session_id=session_id,
            feedback_type='success'
        ).count()
        
        # Define progress weights for different action types
        progress_weights = {
            'device_placement': 10,
            'connection_creation': 15,
            'cli_command': 20,
            'configuration': 25
        }
        
        # Calculate progress based on successful actions
        if validation_result in ['correct_placement', 'valid_connection', 'correct_command', 'correct_config']:
            weight = progress_weights.get(action_type, 5)
            return min(feedback_count * weight, 100.0)
        
        return 0.0
    
    def get_session_analytics(self, session_id):
        """Get analytics for a specific session"""
        session = FeedbackSession.query.filter_by(session_id=session_id).first()
        if not session:
            return None
        
        # Get all feedback for this session
        feedback_entries = PerformanceFeedback.query.filter_by(session_id=session_id).all()
        
        analytics = {
            'session': session.to_dict(),
            'feedback_timeline': [f.to_dict() for f in feedback_entries],
            'action_breakdown': self._get_action_breakdown(feedback_entries),
            'performance_trends': self._get_performance_trends(feedback_entries),
            'recommendations': self._generate_recommendations(feedback_entries)
        }
        
        return analytics
    
    def _get_action_breakdown(self, feedback_entries):
        """Get breakdown of actions by type and result"""
        breakdown = {}
        
        for feedback in feedback_entries:
            action_type = feedback.action_type
            feedback_type = feedback.feedback_type
            
            if action_type not in breakdown:
                breakdown[action_type] = {'success': 0, 'error': 0, 'warning': 0}
            
            breakdown[action_type][feedback_type] += 1
        
        return breakdown
    
    def _get_performance_trends(self, feedback_entries):
        """Get performance trends over time"""
        trends = []
        cumulative_score = 0
        
        for feedback in feedback_entries:
            cumulative_score += feedback.feedback_score
            trends.append({
                'timestamp': feedback.action_timestamp.isoformat(),
                'cumulative_score': cumulative_score,
                'action_type': feedback.action_type,
                'feedback_type': feedback.feedback_type,
                'progress': feedback.scenario_progress
            })
        
        return trends
    
    def _generate_recommendations(self, feedback_entries):
        """Generate learning recommendations based on performance"""
        recommendations = []
        
        # Analyze common mistakes
        error_actions = [f for f in feedback_entries if f.feedback_type == 'error']
        if error_actions:
            error_types = {}
            for error in error_actions:
                action_type = error.action_type
                error_types[action_type] = error_types.get(action_type, 0) + 1
            
            # Find most common error type
            most_common_error = max(error_types.items(), key=lambda x: x[1])
            
            recommendations.append({
                'type': 'improvement',
                'message': f'Focus on improving {most_common_error[0].replace("_", " ")} skills',
                'priority': 'high'
            })
        
        # Check CLI command usage
        cli_commands = [f for f in feedback_entries if f.action_type == 'cli_command']
        if len(cli_commands) < 3:
            recommendations.append({
                'type': 'suggestion',
                'message': 'Try using more CLI commands for better troubleshooting',
                'priority': 'medium'
            })
        
        # Check configuration completeness
        config_actions = [f for f in feedback_entries if f.action_type == 'configuration']
        successful_configs = [f for f in config_actions if f.feedback_type == 'success']
        
        if len(config_actions) > 0 and len(successful_configs) / len(config_actions) < 0.5:
            recommendations.append({
                'type': 'improvement',
                'message': 'Review device configuration procedures',
                'priority': 'high'
            })
        
        return recommendations

# Global feedback service instance
feedback_service = FeedbackService()

