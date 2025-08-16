from flask import Blueprint, render_template, request, jsonify, session, current_app
from datetime import datetime, timedelta
import json
import os

# Create blueprint for advanced simulation management
advanced_simulation_management_bp = Blueprint('advanced_simulation_management', __name__, 
                                            url_prefix='/admin/advanced-simulation')

@advanced_simulation_management_bp.route('/dashboard')
def simulation_dashboard():
    """Advanced simulation management dashboard"""
    try:
        # Get simulation statistics
        stats = {
            'total_simulations': 25,
            'active_users': 12,
            'completion_rate': 85.4,
            'average_score': 89.2,
            'total_achievements_unlocked': 156,
            'recent_activity': [
                {
                    'user': 'student_001',
                    'action': 'Completed Advanced Topology scenario',
                    'timestamp': '2024-01-15 10:30:00',
                    'score': 450
                },
                {
                    'user': 'student_002', 
                    'action': 'Unlocked Network Architect achievement',
                    'timestamp': '2024-01-15 10:25:00',
                    'score': 100
                },
                {
                    'user': 'student_003',
                    'action': 'Started Troubleshooting scenario',
                    'timestamp': '2024-01-15 10:20:00',
                    'score': 0
                }
            ]
        }
        
        return render_template('admin/advanced_simulation_dashboard.html',
                             stats=stats,
                             title="Advanced Simulation Dashboard")
                             
    except Exception as e:
        print(f"Error loading simulation dashboard: {str(e)}")
        return render_template('admin/advanced_simulation_dashboard.html',
                             stats={},
                             title="Advanced Simulation Dashboard",
                             error="Failed to load dashboard data")

@advanced_simulation_management_bp.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get detailed simulation analytics"""
    try:
        time_range = request.args.get('range', '7d')
        
        # Calculate date range
        end_date = datetime.now()
        if time_range == '24h':
            start_date = end_date - timedelta(days=1)
        elif time_range == '7d':
            start_date = end_date - timedelta(days=7)
        elif time_range == '30d':
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=7)
        
        # Generate sample analytics data (in production, query from database)
        analytics = {
            'usage_metrics': {
                'total_sessions': 342,
                'unique_users': 89,
                'average_session_duration': '28.5 minutes',
                'bounce_rate': '12.3%',
                'completion_rate': '85.4%'
            },
            'performance_metrics': {
                'average_score': 89.2,
                'median_score': 92.0,
                'highest_score': 100.0,
                'lowest_score': 45.0,
                'score_distribution': {
                    '90-100': 45,
                    '80-89': 28,
                    '70-79': 12,
                    '60-69': 8,
                    'Below 60': 4
                }
            },
            'scenario_popularity': [
                {'scenario': 'Basic Network', 'attempts': 234, 'completion_rate': 92.3},
                {'scenario': 'Troubleshooting', 'attempts': 156, 'completion_rate': 78.8},
                {'scenario': 'Advanced Topology', 'attempts': 89, 'completion_rate': 65.2}
            ],
            'achievement_stats': [
                {'achievement': 'First Device', 'unlocked_by': 89, 'percentage': 100.0},
                {'achievement': 'Connection Master', 'unlocked_by': 67, 'percentage': 75.3},
                {'achievement': 'Speed Demon', 'unlocked_by': 34, 'percentage': 38.2},
                {'achievement': 'Network Architect', 'unlocked_by': 23, 'percentage': 25.8}
            ],
            'daily_usage': [
                {'date': '2024-01-10', 'sessions': 45, 'users': 23},
                {'date': '2024-01-11', 'sessions': 52, 'users': 28},
                {'date': '2024-01-12', 'sessions': 38, 'users': 19},
                {'date': '2024-01-13', 'sessions': 61, 'users': 31},
                {'date': '2024-01-14', 'sessions': 48, 'users': 25},
                {'date': '2024-01-15', 'sessions': 55, 'users': 29},
                {'date': '2024-01-16', 'sessions': 43, 'users': 22}
            ],
            'device_usage': [
                {'device': 'Router', 'placements': 456, 'success_rate': 94.2},
                {'device': 'Switch', 'placements': 389, 'success_rate': 91.8},
                {'device': 'PC', 'placements': 567, 'success_rate': 98.1},
                {'device': 'Server', 'placements': 234, 'success_rate': 87.6}
            ]
        }
        
        return jsonify({
            'success': True,
            'analytics': analytics,
            'time_range': time_range,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error getting analytics: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load analytics'
        }), 500

@advanced_simulation_management_bp.route('/api/user-progress/<user_id>', methods=['GET'])
def get_user_progress(user_id):
    """Get detailed user progress and performance"""
    try:
        # Generate sample user progress data (in production, query from database)
        user_progress = {
            'user_info': {
                'id': user_id,
                'username': f'student_{user_id}',
                'email': f'student_{user_id}@example.com',
                'enrollment_date': '2024-01-01',
                'last_active': '2024-01-15 10:30:00'
            },
            'overall_stats': {
                'total_sessions': 24,
                'total_time': '12 hours 35 minutes',
                'average_score': 87.3,
                'scenarios_completed': 15,
                'achievements_unlocked': 8,
                'current_streak': 5
            },
            'scenario_progress': [
                {
                    'scenario': 'Basic Network',
                    'attempts': 8,
                    'best_score': 95,
                    'average_score': 89.2,
                    'completion_rate': 100.0,
                    'last_attempt': '2024-01-12 14:30:00'
                },
                {
                    'scenario': 'Troubleshooting',
                    'attempts': 5,
                    'best_score': 87,
                    'average_score': 78.4,
                    'completion_rate': 80.0,
                    'last_attempt': '2024-01-14 16:45:00'
                },
                {
                    'scenario': 'Advanced Topology',
                    'attempts': 2,
                    'best_score': 72,
                    'average_score': 68.5,
                    'completion_rate': 50.0,
                    'last_attempt': '2024-01-15 10:30:00'
                }
            ],
            'achievements': [
                {
                    'name': 'First Device',
                    'unlocked_at': '2024-01-02 09:15:00',
                    'points': 10
                },
                {
                    'name': 'Connection Master',
                    'unlocked_at': '2024-01-03 11:22:00',
                    'points': 25
                },
                {
                    'name': 'Speed Demon',
                    'unlocked_at': '2024-01-05 15:30:00',
                    'points': 50
                }
            ],
            'learning_path': {
                'current_level': 'Intermediate',
                'progress_to_next': 65,
                'recommended_next': 'Advanced Network Security',
                'strengths': ['Device Placement', 'Basic Connectivity'],
                'areas_for_improvement': ['Complex Troubleshooting', 'Security Implementation']
            },
            'session_history': [
                {
                    'date': '2024-01-15',
                    'duration': '45 minutes',
                    'scenario': 'Advanced Topology',
                    'score': 72,
                    'achievements': 0
                },
                {
                    'date': '2024-01-14',
                    'duration': '32 minutes',
                    'scenario': 'Troubleshooting',
                    'score': 87,
                    'achievements': 1
                },
                {
                    'date': '2024-01-12',
                    'duration': '28 minutes',
                    'scenario': 'Basic Network',
                    'score': 95,
                    'achievements': 0
                }
            ]
        }
        
        return jsonify({
            'success': True,
            'user_progress': user_progress
        })
        
    except Exception as e:
        print(f"Error getting user progress: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load user progress'
        }), 500

@advanced_simulation_management_bp.route('/api/scenario-config', methods=['GET', 'POST'])
def manage_scenario_config():
    """Manage scenario configurations"""
    if request.method == 'GET':
        try:
            # Get all scenario configurations
            scenario_configs = {
                'basic-network': {
                    'enabled': True,
                    'max_duration': 15,
                    'hint_limit': 5,
                    'passing_score': 70,
                    'difficulty_settings': {
                        'device_limit': 10,
                        'connection_limit': 8,
                        'tutorial_enabled': True
                    }
                },
                'troubleshooting': {
                    'enabled': True,
                    'max_duration': 30,
                    'hint_limit': 3,
                    'passing_score': 80,
                    'difficulty_settings': {
                        'device_limit': 15,
                        'connection_limit': 12,
                        'tutorial_enabled': False
                    }
                },
                'advanced-topology': {
                    'enabled': True,
                    'max_duration': 60,
                    'hint_limit': 1,
                    'passing_score': 85,
                    'difficulty_settings': {
                        'device_limit': 20,
                        'connection_limit': 18,
                        'tutorial_enabled': False
                    }
                }
            }
            
            return jsonify({
                'success': True,
                'scenarios': scenario_configs
            })
            
        except Exception as e:
            print(f"Error getting scenario configs: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Failed to load scenario configurations'
            }), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            scenario_id = data.get('scenario_id')
            config = data.get('config', {})
            
            if not scenario_id:
                return jsonify({
                    'success': False,
                    'error': 'Scenario ID required'
                }), 400
            
            # Validate configuration
            required_fields = ['enabled', 'max_duration', 'hint_limit', 'passing_score']
            for field in required_fields:
                if field not in config:
                    return jsonify({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }), 400
            
            # In production, save to database
            # For now, just validate and return success
            
            return jsonify({
                'success': True,
                'message': f'Configuration updated for scenario: {scenario_id}',
                'scenario_id': scenario_id,
                'config': config
            })
            
        except Exception as e:
            print(f"Error updating scenario config: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Failed to update scenario configuration'
            }), 500

@advanced_simulation_management_bp.route('/api/device-library', methods=['GET', 'POST'])
def manage_device_library():
    """Manage device library and configurations"""
    if request.method == 'GET':
        try:
            device_library = {
                'network_devices': [
                    {
                        'id': 'router',
                        'name': 'Router',
                        'icon': 'fa-route',
                        'category': 'Network Infrastructure',
                        'enabled': True,
                        'properties': {
                            'ports': 4,
                            'protocols': ['TCP', 'UDP', 'ICMP'],
                            'routing': True
                        }
                    },
                    {
                        'id': 'switch',
                        'name': 'Network Switch',
                        'icon': 'fa-sitemap',
                        'category': 'Network Infrastructure',
                        'enabled': True,
                        'properties': {
                            'ports': 24,
                            'protocols': ['Ethernet'],
                            'managed': True
                        }
                    },
                    {
                        'id': 'pc',
                        'name': 'Personal Computer',
                        'icon': 'fa-desktop',
                        'category': 'End Devices',
                        'enabled': True,
                        'properties': {
                            'os': 'Windows',
                            'network_card': True,
                            'applications': ['Browser', 'Email']
                        }
                    },
                    {
                        'id': 'server',
                        'name': 'Server',
                        'icon': 'fa-server',
                        'category': 'Infrastructure',
                        'enabled': True,
                        'properties': {
                            'os': 'Linux',
                            'services': ['Web', 'Database', 'Email'],
                            'redundancy': True
                        }
                    }
                ],
                'connection_types': [
                    {
                        'id': 'ethernet',
                        'name': 'Ethernet Cable',
                        'icon': 'fa-ethernet',
                        'category': 'Wired',
                        'enabled': True,
                        'properties': {
                            'speed': '1 Gbps',
                            'duplex': 'Full',
                            'distance': '100m'
                        }
                    },
                    {
                        'id': 'fiber',
                        'name': 'Fiber Optic',
                        'icon': 'fa-wifi',
                        'category': 'Wired',
                        'enabled': True,
                        'properties': {
                            'speed': '10 Gbps',
                            'distance': '40km',
                            'interference': 'Minimal'
                        }
                    }
                ]
            }
            
            return jsonify({
                'success': True,
                'device_library': device_library
            })
            
        except Exception as e:
            print(f"Error getting device library: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Failed to load device library'
            }), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            action = data.get('action')  # 'add', 'update', 'delete'
            device_data = data.get('device', {})
            
            if action == 'add':
                # Validate new device data
                required_fields = ['id', 'name', 'icon', 'category']
                for field in required_fields:
                    if field not in device_data:
                        return jsonify({
                            'success': False,
                            'error': f'Missing required field: {field}'
                        }), 400
                
                return jsonify({
                    'success': True,
                    'message': f'Device {device_data["name"]} added successfully',
                    'device': device_data
                })
                
            elif action == 'update':
                device_id = device_data.get('id')
                if not device_id:
                    return jsonify({
                        'success': False,
                        'error': 'Device ID required for update'
                    }), 400
                
                return jsonify({
                    'success': True,
                    'message': f'Device {device_id} updated successfully',
                    'device': device_data
                })
                
            elif action == 'delete':
                device_id = data.get('device_id')
                if not device_id:
                    return jsonify({
                        'success': False,
                        'error': 'Device ID required for deletion'
                    }), 400
                
                return jsonify({
                    'success': True,
                    'message': f'Device {device_id} deleted successfully'
                })
            
            else:
                return jsonify({
                    'success': False,
                    'error': 'Invalid action. Use add, update, or delete'
                }), 400
                
        except Exception as e:
            print(f"Error managing device library: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Failed to manage device library'
            }), 500

@advanced_simulation_management_bp.route('/api/export-data', methods=['POST'])
def export_simulation_data():
    """Export simulation data for analysis"""
    try:
        data = request.get_json()
        export_type = data.get('type', 'all')  # 'users', 'sessions', 'achievements', 'all'
        format_type = data.get('format', 'json')  # 'json', 'csv', 'xlsx'
        date_range = data.get('date_range', {})
        
        # Generate export data based on type
        export_data = {}
        
        if export_type in ['users', 'all']:
            export_data['users'] = [
                {
                    'id': 1,
                    'username': 'student_001',
                    'email': 'student001@example.com',
                    'total_sessions': 24,
                    'average_score': 87.3,
                    'achievements': 8,
                    'last_active': '2024-01-15 10:30:00'
                },
                {
                    'id': 2,
                    'username': 'student_002',
                    'email': 'student002@example.com',
                    'total_sessions': 18,
                    'average_score': 92.1,
                    'achievements': 12,
                    'last_active': '2024-01-15 09:45:00'
                }
            ]
        
        if export_type in ['sessions', 'all']:
            export_data['sessions'] = [
                {
                    'session_id': 'sess_001',
                    'user_id': 1,
                    'scenario': 'Basic Network',
                    'start_time': '2024-01-15 10:00:00',
                    'end_time': '2024-01-15 10:28:00',
                    'score': 95,
                    'achievements': 0,
                    'devices_used': 5,
                    'connections_made': 4
                },
                {
                    'session_id': 'sess_002',
                    'user_id': 2,
                    'scenario': 'Troubleshooting',
                    'start_time': '2024-01-15 09:15:00',
                    'end_time': '2024-01-15 09:47:00',
                    'score': 87,
                    'achievements': 1,
                    'devices_used': 7,
                    'connections_made': 6
                }
            ]
        
        if export_type in ['achievements', 'all']:
            export_data['achievements'] = [
                {
                    'achievement_id': 'first-device',
                    'user_id': 1,
                    'unlocked_at': '2024-01-02 09:15:00',
                    'points': 10
                },
                {
                    'achievement_id': 'connection-master',
                    'user_id': 1,
                    'unlocked_at': '2024-01-03 11:22:00',
                    'points': 25
                }
            ]
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'simulation_export_{export_type}_{timestamp}.{format_type}'
        
        return jsonify({
            'success': True,
            'export_data': export_data,
            'filename': filename,
            'format': format_type,
            'export_type': export_type,
            'record_count': sum(len(v) if isinstance(v, list) else 1 for v in export_data.values()),
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error exporting data: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to export simulation data'
        }), 500

@advanced_simulation_management_bp.route('/api/system-health', methods=['GET'])
def get_system_health():
    """Get system health and performance metrics"""
    try:
        # Generate system health data
        health_data = {
            'status': 'healthy',
            'uptime': '15 days, 8 hours, 23 minutes',
            'last_restart': '2024-01-01 00:00:00',
            'performance_metrics': {
                'cpu_usage': 23.4,
                'memory_usage': 45.7,
                'disk_usage': 67.2,
                'network_throughput': '145 Mbps',
                'response_time': '250ms',
                'error_rate': '0.02%'
            },
            'database_health': {
                'status': 'connected',
                'query_performance': 'optimal',
                'connections': 12,
                'max_connections': 100,
                'slow_queries': 0
            },
            'cache_health': {
                'status': 'active',
                'hit_rate': '94.2%',
                'memory_usage': '78%',
                'eviction_rate': 'low'
            },
            'active_sessions': {
                'total': 45,
                'simulation_sessions': 32,
                'admin_sessions': 3,
                'idle_sessions': 10
            },
            'recent_errors': [],
            'maintenance_schedule': {
                'next_backup': '2024-01-16 02:00:00',
                'next_update': '2024-01-20 01:00:00',
                'maintenance_window': 'Sunday 01:00-03:00 AM'
            }
        }
        
        return jsonify({
            'success': True,
            'health_data': health_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error getting system health: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get system health data'
        }), 500
