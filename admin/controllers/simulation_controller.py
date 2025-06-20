from flask import current_app, jsonify, request
from admin.models.simulation import Simulation
from admin.models import db
from datetime import datetime

class SimulationController:
    """Controller for managing simulations"""
    
    def get_all_simulations(self):
        """Get all simulations"""
        try:
            simulations = Simulation.query.all()
            return [simulation.to_dict() for simulation in simulations]
        except Exception as e:
            current_app.logger.error(f"Error getting simulations: {str(e)}")
            return {'error': 'Failed to get simulations'}
    
    def get_simulation_by_id(self, simulation_id):
        """Get simulation by ID"""
        try:
            simulation = Simulation.query.get(simulation_id)
            if not simulation:
                return {'error': 'Simulation not found'}
            
            return simulation.to_dict()
        except Exception as e:
            current_app.logger.error(f"Error getting simulation: {str(e)}")
            return {'error': 'Failed to get simulation'}
    
    def create_simulation(self, simulation_data, admin_user_id):
        """Create a new simulation"""
        try:
            simulation = Simulation(
                title=simulation_data['title'],
                description=simulation_data['description'],
                simulation_type=simulation_data['simulation_type'],
                category=simulation_data.get('category'),
                difficulty=simulation_data.get('difficulty'),
                learning_objectives=simulation_data.get('learning_objectives', []),
                estimated_duration=simulation_data.get('estimated_duration'),
                prerequisite_knowledge=simulation_data.get('prerequisite_knowledge', []),
                step_definitions=simulation_data.get('step_definitions', []),
                validation_rules=simulation_data.get('validation_rules', {}),
                simulation_config=simulation_data.get('simulation_config', {}),
                base_score=simulation_data.get('base_score', 100),
                time_bonus=simulation_data.get('time_bonus', 20),
                perfect_completion_bonus=simulation_data.get('perfect_completion_bonus', 10),
                initial_state=simulation_data.get('initial_state', {}),
                expected_outcomes=simulation_data.get('expected_outcomes', {}),
                created_by=admin_user_id,
                is_active=simulation_data.get('is_active', True),
                is_published=simulation_data.get('is_published', False),
                tags=simulation_data.get('tags', '')
            )
            
            db.session.add(simulation)
            db.session.commit()
            
            return {'success': True, 'simulation': simulation.to_dict()}
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating simulation: {str(e)}")
            return {'error': 'Failed to create simulation'}
    
    def update_simulation(self, simulation_id, simulation_data, admin_user_id):
        """Update an existing simulation"""
        try:
            simulation = Simulation.query.get(simulation_id)
            if not simulation:
                return {'error': 'Simulation not found'}
            
            # Update fields
            simulation.title = simulation_data.get('title', simulation.title)
            simulation.description = simulation_data.get('description', simulation.description)
            simulation.simulation_type = simulation_data.get('simulation_type', simulation.simulation_type)
            simulation.category = simulation_data.get('category', simulation.category)
            simulation.difficulty = simulation_data.get('difficulty', simulation.difficulty)
            simulation.learning_objectives = simulation_data.get('learning_objectives', simulation.learning_objectives)
            simulation.estimated_duration = simulation_data.get('estimated_duration', simulation.estimated_duration)
            simulation.prerequisite_knowledge = simulation_data.get('prerequisite_knowledge', simulation.prerequisite_knowledge)
            simulation.step_definitions = simulation_data.get('step_definitions', simulation.step_definitions)
            simulation.validation_rules = simulation_data.get('validation_rules', simulation.validation_rules)
            simulation.simulation_config = simulation_data.get('simulation_config', simulation.simulation_config)
            simulation.base_score = simulation_data.get('base_score', simulation.base_score)
            simulation.time_bonus = simulation_data.get('time_bonus', simulation.time_bonus)
            simulation.perfect_completion_bonus = simulation_data.get('perfect_completion_bonus', simulation.perfect_completion_bonus)
            simulation.initial_state = simulation_data.get('initial_state', simulation.initial_state)
            simulation.expected_outcomes = simulation_data.get('expected_outcomes', simulation.expected_outcomes)
            simulation.is_active = simulation_data.get('is_active', simulation.is_active)
            simulation.is_published = simulation_data.get('is_published', simulation.is_published)
            simulation.tags = simulation_data.get('tags', simulation.tags)
            simulation.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return {'success': True, 'simulation': simulation.to_dict()}
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating simulation: {str(e)}")
            return {'error': 'Failed to update simulation'}
    
    def delete_simulation(self, simulation_id):
        """Delete a simulation"""
        try:
            simulation = Simulation.query.get(simulation_id)
            if not simulation:
                return {'error': 'Simulation not found'}
            
            db.session.delete(simulation)
            db.session.commit()
            
            return {'success': True, 'message': 'Simulation deleted successfully'}
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting simulation: {str(e)}")
            return {'error': 'Failed to delete simulation'}
    
    def validate_simulation_step(self, simulation_id, step_index, user_response):
        """Validate a user's response to a specific simulation step"""
        try:
            simulation = Simulation.query.get(simulation_id)
            if not simulation:
                return {'valid': False, 'message': 'Simulation not found'}
            
            validation_rules = simulation.validation_rules
            if str(step_index) not in validation_rules:
                return {'valid': False, 'message': 'Step validation rules not found'}
            
            step_rule = validation_rules[str(step_index)]
            step_type = step_rule.get('type', 'text')
            expected_answer = step_rule.get('expected_answer', '')
            score = step_rule.get('score', 0)
            validation_type = step_rule.get('validation_type', 'exact_match')
            
            is_valid = False
            message = ''
            
            if validation_type == 'exact_match':
                is_valid = user_response.lower().strip() == expected_answer.lower().strip()
            elif validation_type == 'contains':
                is_valid = expected_answer.lower() in user_response.lower()
            elif validation_type == 'regex':
                import re
                is_valid = bool(re.match(expected_answer, user_response, re.IGNORECASE))
            elif validation_type == 'multiple_choice':
                is_valid = user_response == expected_answer
            
            if is_valid:
                message = step_rule.get('success_message', 'Correct! Well done.')
            else:
                message = step_rule.get('error_message', 'Incorrect. Please try again.')
                
            return {
                'valid': is_valid,
                'message': message,
                'score': score if is_valid else 0,
                'hint': step_rule.get('hint', '') if not is_valid else ''
            }
            
        except Exception as e:
            current_app.logger.error(f"Error validating step: {str(e)}")
            return {'valid': False, 'message': 'Validation error occurred'}

    def create_simulation_from_builder(self, builder_data, admin_user_id):
        """Create simulation from the builder interface"""
        try:
            # Process step definitions
            step_definitions = []
            for step in builder_data.get('step_definitions', []):
                step_def = {
                    'title': step['title'],
                    'type': step['type'],
                    'description': step['description'],
                    'order': step['order']
                }
                
                # Add type-specific properties
                if step['type'] == 'question':
                    step_def.update({
                        'question': step.get('questionText', ''),
                        'inputType': step.get('questionType', 'text'),
                        'options': step.get('options', []) if step.get('questionType') == 'multiple_choice' else None
                    })
                elif step['type'] == 'configuration':
                    step_def.update({
                        'deviceType': step.get('deviceType', ''),
                        'task': step.get('configTask', ''),
                        'expectedCommands': step.get('expectedCommands', '')
                    })
                elif step['type'] == 'network_diagram':
                    step_def.update({
                        'task': step.get('networkTask', ''),
                        'showDiagram': step.get('showDiagram', True)
                    })
                
                step_definitions.append(step_def)
            
            # Create validation rules
            validation_rules = {}
            for i, step in enumerate(builder_data.get('step_definitions', [])):
                validation_rules[str(i)] = {
                    'type': step['type'],
                    'expected_answer': step['validation']['expectedAnswer'],
                    'score': step['validation']['score'],
                    'validation_type': 'exact_match' if step['type'] == 'question' else 'contains'
                }
            
            # Create the simulation
            simulation_data = {
                'title': builder_data['title'],
                'description': builder_data['description'],
                'simulation_type': builder_data['simulation_type'],
                'category': builder_data['category'],
                'difficulty': builder_data['difficulty'],
                'learning_objectives': builder_data['learning_objectives'],
                'estimated_duration': builder_data['estimated_duration'],
                'step_definitions': step_definitions,
                'validation_rules': validation_rules,
                'base_score': builder_data['base_score'],
                'time_bonus': builder_data['time_bonus'],
                'perfect_completion_bonus': builder_data['perfect_completion_bonus'],
                'tags': builder_data['tags'],
                'is_active': builder_data['is_active'],
                'is_published': builder_data['is_published'],
                'simulation_config': builder_data.get('simulation_config', {}),
                'initial_state': builder_data.get('initial_state', {}),
                'expected_outcomes': builder_data.get('expected_outcomes', {})
            }
            
            return self.create_simulation(simulation_data, admin_user_id)
            
        except Exception as e:
            current_app.logger.error(f"Error creating simulation from builder: {str(e)}")
            return {'error': 'Failed to create simulation from builder data'}
