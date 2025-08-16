from flask import current_app, request, jsonify
from admin import db
from admin.models.simulation import Simulation, SimulationAttempt
# Learning Path models removed - feature deprecated
# from admin.models.learning_path import LearningPath, UserLearningProgress
from datetime import datetime
import json

class SimulationController:
    """
    Enhanced Simulation Controller for Admin Simulation Management
    Supports step-by-step simulation creation, validation, and analytics
    """
    
    def get_dashboard_data(self):
        """Get comprehensive dashboard data for admin"""
        try:
            # Basic statistics
            stats = Simulation.get_dashboard_stats()
            
            # Learning paths statistics
            # Learning paths feature removed - returning 0 counts
            total_paths = 0
            published_paths = 0
            
            # Recent activity
            recent_attempts = SimulationAttempt.query.order_by(
                SimulationAttempt.started_at.desc()
            ).limit(10).all()
            
            # Performance metrics
            avg_completion_rate = db.session.query(
                db.func.avg(Simulation.completion_rate)
            ).filter(Simulation.is_published == True).scalar() or 0
            
            return {
                'simulations': stats,
                'learning_paths': {
                    'total_paths': total_paths,
                    'published_paths': published_paths
                },
                'recent_attempts': [attempt.to_dict() for attempt in recent_attempts],
                'metrics': {
                    'average_completion_rate': round(avg_completion_rate, 2),
                    'total_user_attempts': SimulationAttempt.query.count()
                }
            }
        except Exception as e:
            current_app.logger.error(f"Error getting dashboard data: {str(e)}")
            return {'error': 'Failed to load dashboard data'}
    
    def create_simulation_from_builder(self, builder_data, admin_user_id):
        """Create simulation from the enhanced builder interface"""
        try:
            # Validate required fields
            required_fields = ['title', 'simulation_type', 'difficulty', 'description']
            for field in required_fields:
                if not builder_data.get('basic', {}).get(field):
                    return {'error': f'Missing required field: {field}'}
            
            basic_data = builder_data.get('basic', {})
            objectives = builder_data.get('objectives', [])
            steps = builder_data.get('steps', [])
            scoring = builder_data.get('scoring', {})
            template_data = builder_data.get('template', {})
            
            # Process step definitions with enhanced validation
            step_definitions = []
            validation_rules = {}
            total_score = 0
            
            for i, step in enumerate(steps):
                step_def = {
                    'title': step.get('title', ''),
                    'type': step.get('type', 'instruction'),
                    'description': step.get('description', ''),
                    'order': i + 1,
                    'content': self._process_step_content(step)
                }
                
                # Add step-specific properties
                if step['type'] == 'question':
                    step_def.update({
                        'question_text': step.get('questionText', ''),
                        'question_type': step.get('questionType', 'text'),
                        'options': step.get('options', [])
                    })
                elif step['type'] == 'configuration':
                    step_def.update({
                        'device_type': step.get('deviceType', ''),
                        'configuration_task': step.get('configTask', ''),
                        'expected_commands': step.get('expectedCommands', '')
                    })
                elif step['type'] == 'troubleshooting':
                    step_def.update({
                        'problem_scenario': step.get('problemScenario', ''),
                        'troubleshooting_steps': step.get('troubleshootingSteps', '')
                    })
                
                step_definitions.append(step_def)
                
                # Create validation rules
                validation_rules[str(i)] = {
                    'type': step['type'],
                    'expected_answer': step.get('validation', {}).get('expectedAnswer', ''),
                    'score': step.get('validation', {}).get('score', 10),
                    'validation_type': self._determine_validation_type(step['type']),
                    'success_message': 'Correct! Well done.',
                    'error_message': 'Incorrect. Please review and try again.',
                    'hint': step.get('hint', '')
                }
                
                total_score += step.get('validation', {}).get('score', 10)
            
            # Create simulation configuration
            simulation_config = {
                'template_used': template_data.get('selectedTemplate'),
                'network_topology': template_data.get('networkTopology', {}),
                'devices': template_data.get('devices', []),
                'protocols': template_data.get('protocols', [])
            }
            
            # Create the simulation
            simulation = Simulation(
                title=basic_data['title'],
                description=basic_data['description'],
                simulation_type=basic_data['type'],
                category=basic_data.get('category', 'General'),
                difficulty=basic_data['difficulty'],
                learning_objectives=objectives,
                estimated_duration=int(basic_data.get('duration', 30)),
                step_definitions=step_definitions,
                validation_rules=validation_rules,
                simulation_config=simulation_config,
                base_score=total_score,
                time_bonus=int(scoring.get('timeBonus', 20)),
                perfect_completion_bonus=int(scoring.get('perfectBonus', 30)),
                tags=scoring.get('tags', '').split(',') if scoring.get('tags') else [],
                is_active=scoring.get('isActive', True),
                is_published=scoring.get('isPublished', False),
                created_by=admin_user_id,
                initial_state={},
                expected_outcomes={}
            )
            
            db.session.add(simulation)
            db.session.commit()
            
            current_app.logger.info(f"Simulation created successfully: {simulation.id}")
            
            return {
                'success': True,
                'simulation': simulation.to_dict(include_steps=True),
                'message': 'Simulation created successfully!'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating simulation: {str(e)}")
            return {'error': f'Failed to create simulation: {str(e)}'}
    
    def _process_step_content(self, step):
        """Process step content based on type"""
        content = {}
        
        if step['type'] == 'network_diagram':
            content['show_diagram'] = step.get('showDiagram', True)
            content['network_task'] = step.get('networkTask', '')
        elif step['type'] == 'configuration':
            content['device_configuration'] = {
                'device_type': step.get('deviceType', ''),
                'commands': step.get('expectedCommands', '').split('\n') if step.get('expectedCommands') else []
            }
        elif step['type'] == 'troubleshooting':
            content['troubleshooting_scenario'] = {
                'problem_description': step.get('problemScenario', ''),
                'expected_steps': step.get('troubleshootingSteps', '').split('\n') if step.get('troubleshootingSteps') else []
            }
        
        return content
    
    def _determine_validation_type(self, step_type):
        """Determine validation type based on step type"""
        validation_types = {
            'question': 'exact_match',
            'configuration': 'contains',
            'troubleshooting': 'contains',
            'network_diagram': 'contains',
            'instruction': 'manual'
        }
        return validation_types.get(step_type, 'exact_match')
    
    def validate_simulation_step(self, simulation_id, step_index, user_response):
        """Validate a user's response to a specific simulation step"""
        try:
            simulation = Simulation.query.get(simulation_id)
            if not simulation:
                return {'valid': False, 'message': 'Simulation not found'}
            
            # Use the simulation's built-in validation method
            result = simulation.validate_step_response(step_index, user_response)
            
            # Log validation attempt
            current_app.logger.info(f"Step validation - Simulation: {simulation_id}, Step: {step_index}, Valid: {result['valid']}")
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error validating step: {str(e)}")
            return {'valid': False, 'message': 'Validation error occurred'}
    
    def get_simulation_templates(self, simulation_type):
        """Get templates for specific simulation type"""
        templates = {
            'Networking 1': {
                'basic_subnetting': {
                    'name': 'Basic IPv4 Subnetting',
                    'description': 'Learn fundamental subnetting concepts and calculations',
                    'default_config': {
                        'protocols': ['IPv4', 'CIDR'],
                        'scenarios': ['Calculate subnet masks', 'Determine network ranges', 'Assign IP addresses'],
                        'difficulty': 'Beginner',
                        'estimated_duration': 45
                    },
                    'step_templates': [
                        {
                            'title': 'Understanding CIDR Notation',
                            'type': 'instruction',
                            'description': 'Learn about CIDR notation and subnet masks'
                        },
                        {
                            'title': 'Calculate Subnet Mask',
                            'type': 'question',
                            'description': 'Calculate the subnet mask for a given CIDR notation'
                        }
                    ]
                },
                'vlan_configuration': {
                    'name': 'VLAN Configuration',
                    'description': 'Configure VLANs on Cisco switches',
                    'default_config': {
                        'protocols': ['802.1Q', 'VTP'],
                        'scenarios': ['Create VLANs', 'Assign switch ports', 'Configure trunk ports'],
                        'difficulty': 'Intermediate',
                        'estimated_duration': 60
                    },
                    'step_templates': [
                        {
                            'title': 'Create VLAN',
                            'type': 'configuration',
                            'description': 'Create a new VLAN with specified ID and name'
                        },
                        {
                            'title': 'Assign Port to VLAN',
                            'type': 'configuration',
                            'description': 'Assign switch port to the created VLAN'
                        }
                    ]
                }
            },
            'Networking 2': {
                'ospf_routing': {
                    'name': 'OSPF Dynamic Routing',
                    'description': 'Configure OSPF routing protocol',
                    'default_config': {
                        'protocols': ['OSPF', 'IPv4'],
                        'scenarios': ['Configure OSPF areas', 'Set router IDs', 'Verify adjacencies'],
                        'difficulty': 'Advanced',
                        'estimated_duration': 90
                    },
                    'step_templates': [
                        {
                            'title': 'Enable OSPF Process',
                            'type': 'configuration',
                            'description': 'Enable OSPF routing process on the router'
                        },
                        {
                            'title': 'Configure Network Statements',
                            'type': 'configuration',
                            'description': 'Add network statements to advertise connected networks'
                        }
                    ]
                },
                'bgp_routing': {
                    'name': 'BGP Routing Configuration',
                    'description': 'Configure BGP for inter-AS routing',
                    'default_config': {
                        'protocols': ['BGP', 'AS Numbers'],
                        'scenarios': ['eBGP configuration', 'Route filtering', 'Path selection'],
                        'difficulty': 'Expert',
                        'estimated_duration': 120
                    },
                    'step_templates': [
                        {
                            'title': 'Configure BGP Process',
                            'type': 'configuration',
                            'description': 'Configure BGP process with AS number'
                        },
                        {
                            'title': 'Add BGP Neighbor',
                            'type': 'configuration',
                            'description': 'Add eBGP neighbor configuration'
                        }
                    ]
                }
            },
            'Troubleshooting': {
                'network_connectivity': {
                    'name': 'Network Connectivity Issues',
                    'description': 'Troubleshoot common network connectivity problems',
                    'default_config': {
                        'protocols': ['ICMP', 'ARP', 'DNS'],
                        'scenarios': ['Ping failures', 'DNS resolution issues', 'Default gateway problems'],
                        'difficulty': 'Intermediate',
                        'estimated_duration': 45
                    },
                    'step_templates': [
                        {
                            'title': 'Identify the Problem',
                            'type': 'troubleshooting',
                            'description': 'Analyze the network connectivity issue'
                        },
                        {
                            'title': 'Test Connectivity',
                            'type': 'troubleshooting',
                            'description': 'Use ping and traceroute to test connectivity'
                        }
                    ]
                }
            }
        }
        
        return templates.get(simulation_type, {})
    
    def get_all_simulations(self, include_inactive=False):
        """Get all simulations with optional filtering"""
        try:
            query = Simulation.query
            
            if not include_inactive:
                query = query.filter_by(is_active=True)
            
            simulations = query.order_by(Simulation.created_at.desc()).all()
            
            # If no simulations exist, create sample data
            if not simulations:
                print("🔄 No simulations found, creating sample data...")
                self._create_sample_simulations()
                simulations = query.order_by(Simulation.created_at.desc()).all()
            
            return {
                'simulations': [sim.to_dict(include_analytics=True) for sim in simulations],
                'total_count': len(simulations)
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting simulations: {str(e)}")
            return {'error': 'Failed to retrieve simulations'}
    
    def get_simulation_by_id(self, simulation_id, include_steps=True):
        """Get simulation by ID with optional step details"""
        try:
            simulation = Simulation.query.get(simulation_id)
            if not simulation:
                return {'error': 'Simulation not found'}
            
            return {
                'simulation': simulation.to_dict(include_steps=include_steps, include_analytics=True)
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting simulation {simulation_id}: {str(e)}")
            return {'error': 'Failed to retrieve simulation'}
    
    def update_simulation(self, simulation_id, update_data):
        """Update existing simulation"""
        try:
            simulation = Simulation.query.get(simulation_id)
            if not simulation:
                return {'error': 'Simulation not found'}
            
            # Update allowed fields
            allowed_fields = [
                'title', 'description', 'difficulty', 'learning_objectives',
                'estimated_duration', 'tags', 'is_active', 'is_published'
            ]
            
            for field in allowed_fields:
                if field in update_data:
                    setattr(simulation, field, update_data[field])
            
            simulation.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'success': True,
                'simulation': simulation.to_dict(),
                'message': 'Simulation updated successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating simulation {simulation_id}: {str(e)}")
            return {'error': 'Failed to update simulation'}
    
    def delete_simulation(self, simulation_id):
        """Soft delete simulation (mark as inactive)"""
        try:
            simulation = Simulation.query.get(simulation_id)
            if not simulation:
                return {'error': 'Simulation not found'}
            
            simulation.is_active = False
            simulation.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Simulation deleted successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting simulation {simulation_id}: {str(e)}")
            return {'error': 'Failed to delete simulation'}
    
    def search_simulations(self, query_params):
        """Search simulations with advanced filters"""
        try:
            query = query_params.get('query', '')
            simulation_type = query_params.get('type')
            difficulty = query_params.get('difficulty')
            category = query_params.get('category')
            
            simulations = Simulation.search_simulations(
                query=query,
                simulation_type=simulation_type,
                difficulty=difficulty,
                category=category
            )
            
            return {
                'simulations': [sim.to_dict() for sim in simulations],
                'total_count': len(simulations),
                'search_params': query_params
            }
            
        except Exception as e:
            current_app.logger.error(f"Error searching simulations: {str(e)}")
            return {'error': 'Failed to search simulations'}
    
    def _create_sample_simulations(self):
        """Create sample simulations for testing"""
        try:
            sample_simulations = [
                {
                    'title': 'Basic IPv4 Subnetting',
                    'description': 'Learn fundamental subnetting concepts with hands-on practice calculating subnet masks and network ranges.',
                    'simulation_type': 'Networking 1',
                    'category': 'Subnetting',
                    'difficulty': 'Beginner',
                    'learning_objectives': ['Understand CIDR notation', 'Calculate subnet masks', 'Determine network ranges'],
                    'estimated_duration': 30,
                    'is_published': True,
                    'tags': ['ipv4', 'subnetting', 'networking', 'basics'],
                    'step_definitions': [
                        {
                            'title': 'Understanding CIDR Notation',
                            'type': 'instruction',
                            'description': 'Learn about CIDR notation and subnet masks',
                            'order': 1
                        },
                        {
                            'title': 'Calculate Subnet Mask',
                            'type': 'question',
                            'description': 'Calculate the subnet mask for /24 network',
                            'order': 2
                        }
                    ]
                },
                {
                    'title': 'VLAN Configuration',
                    'description': 'Configure VLANs on Cisco switches including VLAN creation, port assignment, and trunk configuration.',
                    'simulation_type': 'Networking 1', 
                    'category': 'Switching',
                    'difficulty': 'Intermediate',
                    'learning_objectives': ['Create VLANs', 'Configure switch ports', 'Setup trunk ports'],
                    'estimated_duration': 45,
                    'is_published': True,
                    'tags': ['vlan', 'switching', 'cisco', 'configuration'],
                    'step_definitions': [
                        {
                            'title': 'Create VLAN',
                            'type': 'configuration',
                            'description': 'Create a new VLAN with ID 10',
                            'order': 1
                        }
                    ]
                },
                {
                    'title': 'OSPF Routing Protocol',
                    'description': 'Configure OSPF dynamic routing protocol with multiple areas and verify neighbor adjacencies.',
                    'simulation_type': 'Networking 2',
                    'category': 'Routing',
                    'difficulty': 'Advanced',
                    'learning_objectives': ['Configure OSPF areas', 'Set router IDs', 'Verify OSPF adjacencies'],
                    'estimated_duration': 60,
                    'is_published': True,
                    'tags': ['ospf', 'routing', 'dynamic', 'protocol'],
                    'step_definitions': [
                        {
                            'title': 'Enable OSPF Process',
                            'type': 'configuration',
                            'description': 'Enable OSPF routing process on router',
                            'order': 1
                        }
                    ]
                },
                {
                    'title': 'Network Troubleshooting',
                    'description': 'Diagnose and fix common network connectivity issues using systematic troubleshooting methodology.',
                    'simulation_type': 'Troubleshooting',
                    'category': 'Troubleshooting',
                    'difficulty': 'Intermediate',
                    'learning_objectives': ['Identify network problems', 'Use troubleshooting tools', 'Implement solutions'],
                    'estimated_duration': 40,
                    'is_published': False,  # Draft simulation
                    'tags': ['troubleshooting', 'connectivity', 'ping', 'traceroute'],
                    'step_definitions': [
                        {
                            'title': 'Identify Problem',
                            'type': 'troubleshooting',
                            'description': 'Analyze connectivity issue symptoms',
                            'order': 1
                        }
                    ]
                }
            ]
            
            for sim_data in sample_simulations:
                simulation = Simulation(
                    title=sim_data['title'],
                    description=sim_data['description'],
                    simulation_type=sim_data['simulation_type'],
                    category=sim_data['category'],
                    difficulty=sim_data['difficulty'],
                    learning_objectives=sim_data['learning_objectives'],
                    estimated_duration=sim_data['estimated_duration'],
                    is_published=sim_data['is_published'],
                    tags=sim_data['tags'],
                    step_definitions=sim_data['step_definitions'],
                    created_by=1,  # Assume admin user ID 1
                    is_active=True,
                    total_attempts=0,
                    successful_completions=0,
                    average_score=0.0
                )
                db.session.add(simulation)
            
            db.session.commit()
            print("✅ Sample simulations created successfully")
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating sample simulations: {str(e)}")
            print(f"❌ Error creating sample simulations: {str(e)}")
    
    def get_simulation_analytics(self, simulation_id):
        """Get detailed analytics for a specific simulation"""
        try:
            simulation = Simulation.query.get(simulation_id)
            if not simulation:
                return {'error': 'Simulation not found'}
            
            # Get attempt data
            attempts = SimulationAttempt.query.filter_by(simulation_id=simulation_id).all()
            
            # Calculate analytics
            total_attempts = len(attempts)
            completed_attempts = [a for a in attempts if a.is_completed]
            
            analytics = {
                'basic_stats': simulation.to_dict(include_analytics=True),
                'attempt_details': {
                    'total_attempts': total_attempts,
                    'completed_attempts': len(completed_attempts),
                    'completion_rate': (len(completed_attempts) / total_attempts * 100) if total_attempts > 0 else 0,
                    'average_score': sum(a.total_score for a in completed_attempts) / len(completed_attempts) if completed_attempts else 0,
                    'average_duration': sum(a.time_spent_seconds for a in completed_attempts) / len(completed_attempts) if completed_attempts else 0
                },
                'step_analytics': self._calculate_step_analytics(attempts, simulation),
                'user_performance': [a.to_dict() for a in attempts[-10:]]  # Last 10 attempts
            }
            
            return analytics
            
        except Exception as e:
            current_app.logger.error(f"Error getting analytics for simulation {simulation_id}: {str(e)}")
            return {'error': 'Failed to get simulation analytics'}
    
    def _calculate_step_analytics(self, attempts, simulation):
        """Calculate analytics for each step"""
        step_analytics = {}
        
        for i, step in enumerate(simulation.step_definitions):
            step_attempts = [a for a in attempts if str(i) in a.step_responses]
            step_scores = [a.step_scores.get(str(i), 0) for a in step_attempts]
            
            step_analytics[i] = {
                'step_title': step.get('title', f'Step {i+1}'),
                'attempt_count': len(step_attempts),
                'success_count': len([s for s in step_scores if s > 0]),
                'success_rate': (len([s for s in step_scores if s > 0]) / len(step_attempts) * 100) if step_attempts else 0,
                'average_score': sum(step_scores) / len(step_scores) if step_scores else 0
            }
        
        return step_analytics
