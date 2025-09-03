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
            
            # Convert attempts to dict safely
            recent_attempts_data = []
            for attempt in recent_attempts:
                try:
                    recent_attempts_data.append(attempt.to_dict())
                except Exception as e:
                    current_app.logger.warning(f"Error converting attempt to dict: {e}")
                    continue
            
            # Performance metrics - calculate completion rate directly in SQL
            avg_completion_rate = db.session.query(
                db.func.avg(
                    db.case(
                        (Simulation.total_attempts > 0, 
                         (Simulation.successful_completions * 100.0) / Simulation.total_attempts),
                        else_=0.0
                    )
                )
            ).filter(Simulation.is_published == True).scalar() or 0
            
            return {
                'simulations': stats,
                'learning_paths': {
                    'total_paths': total_paths,
                    'published_paths': published_paths
                },
                'recent_attempts': recent_attempts_data,
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
                'protocols': template_data.get('protocols', []),
                # Carry optional CLI rules authored in the troubleshooting editor
                'cli_rules': template_data.get('cli_rules', {}) if isinstance(template_data, dict) else {},
                # Also persist new nested authoring blocks without requiring migrations
                'collab': template_data.get('collab', {}) if isinstance(template_data, dict) else {},
                'tutorial': template_data.get('tutorial', {}) if isinstance(template_data, dict) else {},
                'achievements': template_data.get('achievements', {}) if isinstance(template_data, dict) else {},
                'scoring': template_data.get('scoring', {}) if isinstance(template_data, dict) else {}
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

    def _sanitize_html(self, html: str) -> str:
        """Basic HTML sanitizer to strip script tags and dangerous attributes.
        Note: Prefer bleach if available; keeping lightweight and dependency-free here.
        """
        try:
            if not html:
                return ''
            import re
            # Remove script/style tags and their content
            html = re.sub(r'<\s*(script|style)[^>]*>.*?<\s*/\s*\1\s*>', '', html, flags=re.I | re.S)
            # Remove on* event handler attributes (onclick, onload, etc.)
            html = re.sub(r'on[a-zA-Z]+\s*=\s*("[^"]*"|\'[^\']*\'|[^\s>]+)', '', html, flags=re.I)
            # Remove javascript: URLs
            html = re.sub(r'href\s*=\s*("|\')\s*javascript:[^\1]*\1', 'href="#"', html, flags=re.I)
            html = re.sub(r'src\s*=\s*("|\')\s*javascript:[^\1]*\1', '', html, flags=re.I)
            return html
        except Exception:
            return html or ''

    def _validate_enums(self, difficulty: str, sim_type: str):
        allowed_difficulties = {'Easy', 'Medium', 'Hard', 'Beginner', 'Intermediate', 'Advanced', 'Expert'}
        allowed_types = {'Standard', 'Guided', 'Assessment'}
        if difficulty not in allowed_difficulties:
            return False, f"Invalid difficulty: {difficulty}"
        if sim_type and sim_type not in allowed_types:
            # allow arbitrary but recommend allowed types; don't block if other strings exist
            pass
        return True, None

    def create_simulation_from_payload(self, payload, admin_user_id):
        """Create simulation from flat JSON payload per admin editor UI.
        Expected keys: title, description (HTML), difficulty, type, estimated_duration, max_score, is_active,
        learning_objectives (list[str]), step_definitions (list[{title, description, media?}])
        """
        try:
            required = ['title', 'difficulty', 'type']
            for k in required:
                if not payload.get(k):
                    return {'error': f'Missing required field: {k}'}

            title = str(payload.get('title')).strip()
            description = self._sanitize_html(payload.get('description', '') or '')
            difficulty = str(payload.get('difficulty')).strip()
            sim_type = str(payload.get('type')).strip()
            ok, err = self._validate_enums(difficulty, sim_type)
            if not ok:
                return {'error': err}

            try:
                est = int(payload.get('estimated_duration') or 30)
                if est < 1: est = 1
            except Exception:
                est = 30
            try:
                max_score = int(payload.get('max_score') or 100)
                if max_score < 1: max_score = 1
            except Exception:
                max_score = 100
            is_active = bool(payload.get('is_active', True))

            # Objectives
            objectives = payload.get('learning_objectives') or []
            if not isinstance(objectives, list):
                objectives = []
            objectives = [str(o) for o in objectives if str(o).strip()]

            # Steps
            raw_steps = payload.get('step_definitions') or []
            steps = []
            if isinstance(raw_steps, list):
                for i, s in enumerate(raw_steps):
                    try:
                        title_s = str(s.get('title', '')).strip()
                        if not title_s:
                            continue
                        desc_s = self._sanitize_html(s.get('description', '') or '')
                        step_obj = {
                            'title': title_s,
                            'description': desc_s,
                            'order': i + 1
                        }
                        # Preserve optional fields (type, media, etc.)
                        if s.get('type'):
                            step_obj['type'] = str(s.get('type'))
                        media = s.get('media')
                        if media:
                            step_obj['media'] = str(media)
                        steps.append(step_obj)
                    except Exception:
                        continue

            # Optional validation rules
            validation_rules = payload.get('validation_rules')
            if isinstance(validation_rules, dict):
                # lightly sanitize strings
                for key, rule in list(validation_rules.items()):
                    if not isinstance(rule, dict):
                        continue
                    for rk in ['expected_answer', 'validation_type', 'hint', 'success_message', 'error_message']:
                        if rk in rule and isinstance(rule[rk], str):
                            rule[rk] = rule[rk].strip()

            # Optional simulation config (devices, protocols, topology)
            simulation_config = payload.get('simulation_config') or {}
            if not isinstance(simulation_config, dict):
                simulation_config = {}

            # Optional tags
            tags = payload.get('tags') or []
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(',') if t.strip()]
            elif isinstance(tags, list):
                tags = [str(t).strip() for t in tags if str(t).strip()]
            else:
                tags = []

            simulation = Simulation(
                title=title,
                description=description,
                simulation_type=sim_type,
                category='General',
                difficulty=difficulty,
                learning_objectives=objectives,
                estimated_duration=est,
                step_definitions=steps,
                validation_rules=validation_rules if isinstance(validation_rules, dict) else {},
                simulation_config=simulation_config,
                base_score=max_score,  # treat as total base for now
                time_bonus=0,
                perfect_completion_bonus=0,
                tags=tags,
                is_active=is_active,
                is_published=False,
                created_by=admin_user_id,
            )
            db.session.add(simulation)
            db.session.commit()
            return {
                'success': True,
                'simulation': simulation.to_dict(include_steps=True),
                'simulation_id': simulation.id
            }
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating simulation from payload: {str(e)}")
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
            
            # Map incoming fields and sanitize
            if 'title' in update_data:
                simulation.title = str(update_data['title']).strip()
            if 'description' in update_data:
                simulation.description = self._sanitize_html(update_data.get('description') or '')
            if 'difficulty' in update_data:
                diff = str(update_data['difficulty']).strip()
                ok, err = self._validate_enums(diff, update_data.get('type') or simulation.simulation_type)
                if not ok:
                    return {'error': err}
                simulation.difficulty = diff
            if 'type' in update_data:
                simulation.simulation_type = str(update_data['type']).strip()
            if 'estimated_duration' in update_data:
                try:
                    est = int(update_data['estimated_duration'])
                    simulation.estimated_duration = max(1, est)
                except Exception:
                    pass
            if 'max_score' in update_data:
                try:
                    ms = int(update_data['max_score'])
                    simulation.base_score = max(1, ms)
                    simulation.time_bonus = 0
                    simulation.perfect_completion_bonus = 0
                except Exception:
                    pass
            if 'is_active' in update_data:
                simulation.is_active = bool(update_data['is_active'])
            if 'is_published' in update_data:
                simulation.is_published = bool(update_data['is_published'])
            if 'learning_objectives' in update_data:
                lo = update_data.get('learning_objectives') or []
                if isinstance(lo, list):
                    simulation.learning_objectives = [str(o) for o in lo if str(o).strip()]
            if 'step_definitions' in update_data:
                sd = update_data.get('step_definitions') or []
                if isinstance(sd, list):
                    cleaned = []
                    for i, s in enumerate(sd):
                        try:
                            t = str(s.get('title', '')).strip()
                            if not t: continue
                            d = self._sanitize_html(s.get('description', '') or '')
                            obj = {'title': t, 'description': d, 'order': i+1}
                            if s.get('type'):
                                obj['type'] = str(s.get('type')).strip()
                            if s.get('media'):
                                obj['media'] = str(s['media'])
                            cleaned.append(obj)
                        except Exception:
                            continue
                    simulation.step_definitions = cleaned
            # Optional validation rules update with enhanced validation support
            if 'validation_rules' in update_data and isinstance(update_data['validation_rules'], dict):
                vr = update_data['validation_rules']
                # sanitize standard validation rules
                for key, rule in list(vr.items()):
                    if not isinstance(rule, dict):
                        continue
                    for rk in ['expected_answer', 'validation_type', 'hint', 'success_message', 'error_message']:
                        if rk in rule and isinstance(rule[rk], str):
                            rule[rk] = rule[rk].strip()
                
                # Handle enhanced validation state requirements
                if 'enhanced_validation_states' in vr:
                    enhanced_states = vr['enhanced_validation_states']
                    if isinstance(enhanced_states, dict):
                        # Sanitize validation state requirements
                        for state_name in ['CONFIGURED', 'CONNECTED', 'VALIDATED', 'WORKING']:
                            if state_name in enhanced_states:
                                state_config = enhanced_states[state_name]
                                if isinstance(state_config, dict):
                                    # Sanitize requirements for each state
                                    if 'requirements' in state_config and isinstance(state_config['requirements'], list):
                                        cleaned_reqs = []
                                        for req in state_config['requirements']:
                                            if isinstance(req, str):
                                                cleaned_reqs.append(req.strip())
                                        state_config['requirements'] = cleaned_reqs
                                    
                                    # Sanitize validation criteria
                                    if 'validation_criteria' in state_config and isinstance(state_config['validation_criteria'], dict):
                                        criteria = state_config['validation_criteria']
                                        for key in ['min_devices_configured', 'min_connections_validated', 'min_tests_passed']:
                                            if key in criteria:
                                                try:
                                                    criteria[key] = int(criteria[key])
                                                except (ValueError, TypeError):
                                                    criteria[key] = 0
                
                simulation.validation_rules = vr
            # Optional simulation config update with enhanced validation support
            if 'simulation_config' in update_data and isinstance(update_data['simulation_config'], dict):
                config = update_data['simulation_config']
                
                # Handle enhanced validation configuration
                if 'enhanced_validation' in config:
                    enhanced_config = config['enhanced_validation']
                    # Validate and sanitize enhanced validation config
                    if isinstance(enhanced_config, dict):
                        # Sanitize configuration requirements
                        if 'configuration_requirements' in enhanced_config:
                            config_req = enhanced_config['configuration_requirements']
                            if isinstance(config_req, dict):
                                # Ensure boolean values for requirement flags
                                for key in ['require_ip_assignment', 'require_device_modes', 'require_cable_configuration']:
                                    if key in config_req:
                                        config_req[key] = bool(config_req[key])
                        
                        # Sanitize physical validation rules
                        if 'physical_validation' in enhanced_config:
                            phys_val = enhanced_config['physical_validation']
                            if isinstance(phys_val, dict):
                                # Ensure boolean values for validation flags
                                for key in ['enforce_compatible_connections', 'validate_device_capabilities', 'check_cable_types']:
                                    if key in phys_val:
                                        phys_val[key] = bool(phys_val[key])
                                        
                                # Sanitize connection rules
                                if 'connection_rules' in phys_val and isinstance(phys_val['connection_rules'], list):
                                    cleaned_rules = []
                                    for rule in phys_val['connection_rules']:
                                        if isinstance(rule, dict) and 'from_type' in rule and 'to_type' in rule:
                                            cleaned_rule = {
                                                'from_type': str(rule['from_type']).strip(),
                                                'to_type': str(rule['to_type']).strip(),
                                                'allowed_cables': rule.get('allowed_cables', []),
                                                'description': str(rule.get('description', '')).strip()
                                            }
                                            cleaned_rules.append(cleaned_rule)
                                    phys_val['connection_rules'] = cleaned_rules
                        
                        # Sanitize connectivity test configuration
                        if 'connectivity_tests' in enhanced_config:
                            conn_tests = enhanced_config['connectivity_tests']
                            if isinstance(conn_tests, dict):
                                # Ensure boolean values for test flags
                                for key in ['require_ping_tests', 'require_route_validation', 'require_connectivity_matrix']:
                                    if key in conn_tests:
                                        conn_tests[key] = bool(conn_tests[key])
                                        
                                # Sanitize required test cases
                                if 'required_tests' in conn_tests and isinstance(conn_tests['required_tests'], list):
                                    cleaned_tests = []
                                    for test in conn_tests['required_tests']:
                                        if isinstance(test, dict) and 'source' in test and 'target' in test:
                                            cleaned_test = {
                                                'source': str(test['source']).strip(),
                                                'target': str(test['target']).strip(),
                                                'test_type': str(test.get('test_type', 'ping')).strip(),
                                                'expected_result': test.get('expected_result', True),
                                                'description': str(test.get('description', '')).strip()
                                            }
                                            cleaned_tests.append(cleaned_test)
                                    conn_tests['required_tests'] = cleaned_tests
                
                simulation.simulation_config = config
            # Optional tags update
            if 'tags' in update_data:
                tags = update_data.get('tags') or []
                if isinstance(tags, str):
                    tags = [t.strip() for t in tags.split(',') if t.strip()]
                elif isinstance(tags, list):
                    tags = [str(t).strip() for t in tags if str(t).strip()]
                else:
                    tags = []
                simulation.tags = tags
            
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
    
    def create_simulation(self, simulation_data):
        """Create a new simulation with basic data"""
        try:
            # Validate required fields
            required_fields = ['title', 'description', 'simulation_type']
            for field in required_fields:
                if field not in simulation_data or not simulation_data[field]:
                    return {'error': f'Missing required field: {field}'}
            
            # Create new simulation
            simulation = Simulation(
                title=simulation_data['title'],
                description=simulation_data['description'],
                simulation_type=simulation_data['simulation_type'],
                category=simulation_data.get('category', 'General'),
                difficulty=simulation_data.get('difficulty', 'Beginner'),
                learning_objectives=simulation_data.get('learning_objectives', []),
                estimated_duration=simulation_data.get('estimated_duration', 30),
                tags=simulation_data.get('tags', []),
                step_definitions=simulation_data.get('step_definitions', []),
                created_by=simulation_data.get('created_by', 1),
                is_active=simulation_data.get('is_active', True),
                is_published=simulation_data.get('is_published', False),
                total_attempts=0,
                successful_completions=0,
                average_score=0.0
            )
            
            db.session.add(simulation)
            db.session.commit()
            
            return {
                'success': True,
                'simulation_id': simulation.id,
                'simulation': simulation.to_dict(),
                'message': 'Simulation created successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating simulation: {str(e)}")
            return {'error': f'Failed to create simulation: {str(e)}'}

    def toggle_simulation_status(self, simulation_id, is_published):
        """Toggle simulation publish status"""
        try:
            simulation = Simulation.query.get(simulation_id)
            if not simulation:
                return {'error': 'Simulation not found'}
            
            simulation.is_published = is_published
            db.session.commit()
            
            return {
                'success': True,
                'simulation_id': simulation_id,
                'is_published': is_published,
                'message': f'Simulation {"published" if is_published else "unpublished"} successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error toggling simulation status: {str(e)}")
            return {'error': f'Failed to update simulation status: {str(e)}'}

    def duplicate_simulation(self, simulation_id):
        """Create a copy of an existing simulation"""
        try:
            original = Simulation.query.get(simulation_id)
            if not original:
                return {'error': 'Simulation not found'}
            
            # Create duplicate with modified title
            duplicate = Simulation(
                title=f"{original.title} (Copy)",
                description=original.description,
                simulation_type=original.simulation_type,
                category=original.category,
                difficulty=original.difficulty,
                learning_objectives=original.learning_objectives.copy() if original.learning_objectives else [],
                estimated_duration=original.estimated_duration,
                tags=original.tags.copy() if original.tags else [],
                step_definitions=original.step_definitions.copy() if original.step_definitions else [],
                created_by=original.created_by,
                is_active=True,
                is_published=False,  # Duplicates start as unpublished
                total_attempts=0,
                successful_completions=0,
                average_score=0.0
            )
            
            db.session.add(duplicate)
            db.session.commit()
            
            return {
                'success': True,
                'original_id': simulation_id,
                'duplicate_id': duplicate.id,
                'duplicate': duplicate.to_dict(),
                'message': 'Simulation duplicated successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error duplicating simulation: {str(e)}")
            return {'error': f'Failed to duplicate simulation: {str(e)}'}

    def delete_simulation(self, simulation_id):
        """Delete a simulation (soft delete by setting is_active to False)"""
        try:
            simulation = Simulation.query.get(simulation_id)
            if not simulation:
                return {'error': 'Simulation not found'}
            
            # Soft delete - just mark as inactive
            simulation.is_active = False
            simulation.is_published = False
            db.session.commit()
            
            return {
                'success': True,
                'simulation_id': simulation_id,
                'message': 'Simulation deleted successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting simulation: {str(e)}")
            return {'error': f'Failed to delete simulation: {str(e)}'}
