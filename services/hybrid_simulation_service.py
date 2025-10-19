"""
Database Simulation Service - Provides Database-Only Simulations
==================================================================

This service provides access to database simulations created via Simulation Builder.
All static content has been removed - simulations are now fully database-driven.
"""

from instructor.models.simulation import Simulation
from instructor.models.module import Module, Lesson
from instructor.models.class_model import Class
from flask import current_app
import json

class HybridSimulationService:
    """Service that provides database simulations (static content removed)"""
    
    @staticmethod
    def get_all_simulations_for_class(class_id, user_id=None):
        """Get all database simulations available to a class"""
        try:
            # Get class information
            class_obj = Class.query.get(class_id)
            if not class_obj:
                return {"database": [], "learning_paths": []}
            
            # Get database simulations assigned to this class
            database_sims = HybridSimulationService._get_database_simulations_for_class(class_id)
            
            # Get learning paths assigned to this class
            learning_paths = HybridSimulationService._get_learning_paths_for_class(class_id)
            
            # Add progression status if user_id provided
            if user_id:
                database_sims = HybridSimulationService._add_progression_status(database_sims, user_id, "database")
                learning_paths = HybridSimulationService._add_learning_path_progression(learning_paths, user_id)
            
            return {
                "database": database_sims,
                "learning_paths": learning_paths,
                "total_count": len(database_sims) + sum(len(lp.get('simulations', [])) for lp in learning_paths)
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting simulations for class {class_id}: {str(e)}")
            return {"static": [], "database": [], "learning_paths": []}
    
    @staticmethod
    def _get_static_simulations_for_class(class_obj):
        """Get static simulations based on class networking level"""
        static_sims = []
        
        # Determine networking level from class name/description
        networking_level = HybridSimulationService._determine_networking_level(class_obj)
        
        if networking_level in [1, "both"]:
            # Add Networking 1 simulations - now using database content only
            # Static content integration removed during refactoring
            pass
        
        if networking_level in [2, "both"]:
            # Add Networking 2 simulations - now using database content only  
            # Static content integration removed during refactoring
            pass
        
        return static_sims
    
    @staticmethod
    def _get_database_simulations_for_class(class_id):
        """Get database simulations assigned to a specific class"""
        try:
            # Get simulations directly assigned to class
            assigned_sims = Simulation.query.filter(
                Simulation.is_published == True,
                Simulation.is_active == True
            ).all()
            
            # Convert to unified format
            database_sims = []
            for sim in assigned_sims:
                database_sims.append({
                    'id': sim.id,
                    'title': sim.title,
                    'description': sim.description,
                    'type': 'database',
                    'category': sim.category,
                    'difficulty': sim.difficulty,
                    'estimated_duration': sim.estimated_duration,
                    'url': f'/dynamic/simulation/{sim.id}',
                    'static_url': None,
                    'step_definitions': sim.step_definitions,
                    'learning_objectives': sim.learning_objectives,
                    'is_locked': False  # Will be updated with progression status
                })
            
            return database_sims
            
        except Exception as e:
            current_app.logger.error(f"Error getting database simulations: {str(e)}")
            return []
    
    @staticmethod
    def _get_learning_paths_for_class(class_id):
        """Get learning paths with their simulations for a class - Learning Paths feature removed"""
        # Learning Paths feature has been completely removed from the system
        return []
    
    @staticmethod
    def _determine_networking_level(class_obj):
        """Determine networking level from class information"""
        # Simple heuristic - in real implementation, this could be a class field
        class_name = class_obj.name.lower()
        class_description = (class_obj.description or "").lower()
        
        if "networking 1" in class_name or "networking 1" in class_description:
            return 1
        elif "networking 2" in class_name or "networking 2" in class_description:
            return 2
        elif "advanced" in class_name or "routing" in class_description:
            return 2
        else:
            return "both"  # Show both levels for general classes
    
    @staticmethod
    def _convert_static_to_unified_format(content_module, course_type):
        """Convert static content to unified simulation format"""
        unified_sims = []
        
        try:
            # Get lessons from the content module
            lessons = getattr(content_module, 'lessons', {})
            
            for lesson_key, lesson_data in lessons.items():
                sim_data = {
                    'id': f"static_{course_type.lower().replace(' ', '_')}_{lesson_key}",
                    'title': lesson_data.get('title', f'{course_type} - {lesson_key}'),
                    'description': lesson_data.get('description', ''),
                    'type': 'static',
                    'category': course_type,
                    'difficulty': 'Beginner' if course_type == 'Networking 1' else 'Intermediate',
                    'estimated_duration': 45,  # Default duration
                    'url': f'/dynamic/simulation/static/{lesson_key}',  # New unified route
                    'static_url': HybridSimulationService._get_static_url(course_type, lesson_key),
                    'content': lesson_data.get('content', ''),
                    'is_locked': False  # Will be updated with progression status
                }
                
                unified_sims.append(sim_data)
                
        except Exception as e:
            current_app.logger.error(f"Error converting static content {course_type}: {str(e)}")
        
        return unified_sims
    
    @staticmethod
    def _get_static_url(course_type, lesson_key):
        """Get the original static URL for backwards compatibility"""
        if course_type == "Networking 1":
            # Map lesson keys to static routes
            static_mapping = {
                "1.1": "/networking1-components-simulation",
                "1.2": "/networking1-osi-simulation", 
                "1.3": "/networking1-tcpip-simulation",
                "1.4": "/networking1-ethernet-simulation",
                "1.5": "/networking1-application-simulation",
                "1.6": "/networking1-datalink-simulation"
            }
            return static_mapping.get(lesson_key, f"/networking1-{lesson_key}-simulation")
        elif course_type == "Networking 2":
            static_mapping = {
                "2.1": "/networking2-routing-fundamentals-simulation",
                "2.2": "/networking2-dynamic-routing-simulation",
                "2.3": "/networking2-rip-simulation",
                "2.4": "/networking2-eigrp-simulation",
                "2.5": "/networking2-ospf-simulation",
                "2.6": "/networking2-security-simulation",
                "2.7": "/networking2-vlan-simulation",
                "2.8": "/networking2-routing-simulation",
                "2.9": "/networking2-wireless-simulation",
                "2.10": "/networking2-management-simulation",
                "2.11": "/networking2-vpn-simulation",
                "2.12": "/networking2-troubleshooting-simulation",
                "2.13": "/networking2-qos-simulation"
            }
            return static_mapping.get(lesson_key, f"/networking2-{lesson_key}-simulation")
        
        return None
    
    @staticmethod
    def get_combined_networking1_content():
        """Get all Networking 1 simulations - DATABASE FIRST, then static as fallback"""
        try:
            # Get database simulations first - filter by simulation_type or category
            database_sims = Simulation.query.filter(
                (Simulation.simulation_type.like('%Networking 1%')) |
                (Simulation.category.like('%networking 1%')) |
                (Simulation.category.like('%Networking%')),
                Simulation.is_published == True,
                Simulation.is_active == True
            ).all()
            
            # Convert database simulations to unified format
            unified_sims = []
            for sim in database_sims:
                try:
                    step_count = 0
                    if sim.step_definitions:
                        if isinstance(sim.step_definitions, list):
                            step_count = len(sim.step_definitions)
                        elif isinstance(sim.step_definitions, str):
                            try:
                                parsed_steps = json.loads(sim.step_definitions)
                                step_count = len(parsed_steps) if isinstance(parsed_steps, list) else 1
                            except:
                                step_count = 1
                    
                    unified_sims.append({
                        'id': sim.id,
                        'title': sim.title,
                        'description': sim.description or 'Interactive networking simulation',
                        'type': 'database',
                        'category': sim.category or 'Networking',
                        'difficulty': sim.difficulty or 'Beginner',
                        'estimated_duration': sim.estimated_duration or 45,
                        'url': f'/dynamic/simulation/{sim.id}',
                        'step_count': step_count,
                        'is_interactive': bool(sim.step_definitions),
                        'is_locked': False,
                        'source': 'database'
                    })
                except Exception as e:
                    current_app.logger.warning(f"Error processing simulation {sim.id}: {str(e)}")
                    continue
            
            # Static content removed during refactoring - database-only approach
            return unified_sims
            
        except Exception as e:
            current_app.logger.error(f"Error getting combined networking1 content: {str(e)}")
            # Return empty list as fallback
            return []
    
    @staticmethod
    def get_combined_networking2_content():
        """Get all Networking 2 simulations - DATABASE FIRST, then static as fallback"""
        try:
            # Get database simulations first - filter by simulation_type or category
            database_sims = Simulation.query.filter(
                (Simulation.simulation_type.like('%Networking 2%')) |
                (Simulation.category.like('%networking 2%')) |
                (Simulation.category.like('%Routing%')) |
                (Simulation.category.like('%Dynamic%')) |
                (Simulation.category.like('%VLAN%')),
                Simulation.is_published == True,
                Simulation.is_active == True
            ).all()
            
            # Convert database simulations to unified format
            unified_sims = []
            for sim in database_sims:
                try:
                    step_count = 0
                    if sim.step_definitions:
                        if isinstance(sim.step_definitions, list):
                            step_count = len(sim.step_definitions)
                        elif isinstance(sim.step_definitions, str):
                            try:
                                parsed_steps = json.loads(sim.step_definitions)
                                step_count = len(parsed_steps) if isinstance(parsed_steps, list) else 1
                            except:
                                step_count = 1
                    
                    unified_sims.append({
                        'id': sim.id,
                        'title': sim.title,
                        'description': sim.description or 'Advanced networking simulation',
                        'type': 'database',
                        'category': sim.category or 'Networking',
                        'difficulty': sim.difficulty or 'Intermediate',
                        'estimated_duration': sim.estimated_duration or 60,
                        'url': f'/dynamic/simulation/{sim.id}',
                        'step_count': step_count,
                        'is_interactive': bool(sim.step_definitions),
                        'is_locked': False,
                        'source': 'database'
                    })
                except Exception as e:
                    current_app.logger.warning(f"Error processing simulation {sim.id}: {str(e)}")
                    continue
            
            # Static content removed during refactoring - database-only approach
            return unified_sims
            
        except Exception as e:
            current_app.logger.error(f"Error getting combined networking2 content: {str(e)}")
            # Return empty list as fallback
            return []
    
    @staticmethod
    @staticmethod
    def get_simulation_by_name(simulation_name, networking_type="1"):
        """Get a specific simulation by name for individual routes"""
        try:
            # Try database first
            service = HybridSimulationService()
            if networking_type == "1":
                all_sims = service.get_combined_networking1_content()
            else:
                all_sims = service.get_combined_networking2_content()
            
            # Look for simulation by name (fuzzy matching)
            simulation_name_clean = simulation_name.lower().replace('-', ' ').replace('_', ' ')
            
            for sim in all_sims:
                sim_title_clean = sim['title'].lower().replace('-', ' ').replace('_', ' ')
                if simulation_name_clean in sim_title_clean or sim_title_clean in simulation_name_clean:
                    return sim
                    
            # If not found, try exact key matching for static content
            if networking_type == "1":
                static_keys = [
                    'components', 'osi', 'tcpip', 'ethernet', 'application', 'datalink'
                ]
            else:
                static_keys = [
                    'routing_fundamentals', 'dynamic_routing', 'rip', 'eigrp', 'ospf',
                    'security', 'vlan', 'routing', 'wireless', 'management', 'vpn',
                    'troubleshooting', 'qos'
                ]
            
            if simulation_name in static_keys:
                # Return static simulation data
                return {
                    'id': f'static_{simulation_name}',
                    'title': simulation_name.replace('_', ' ').title(),
                    'description': f'Interactive {simulation_name} simulation',
                    'type': 'static',
                    'category': f'Networking {networking_type}',
                    'url': f'/networking{networking_type}-{simulation_name}-simulation',
                    'is_interactive': True,
                    'source': 'static'
                }
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error getting simulation by name {simulation_name}: {str(e)}")
            return None
            database_sims = Simulation.query.filter_by(
                simulation_type='Networking 2',
                is_published=True,
                is_active=True
            ).all()
            
            # Convert database simulations to unified format
            unified_sims = []
            for sim in database_sims:
                unified_sims.append({
                    'id': sim.id,
                    'title': sim.title,
                    'description': sim.description or '',
                    'type': 'database',
                    'category': sim.category or 'General',
                    'difficulty': sim.difficulty or 'Intermediate',
                    'estimated_duration': sim.estimated_duration or 45,
                    'url': f'/dynamic/simulation/{sim.id}',
                    'step_count': len(sim.step_definitions) if sim.step_definitions and isinstance(sim.step_definitions, list) else (len(json.loads(sim.step_definitions)) if sim.step_definitions else 0),
                    'is_interactive': bool(sim.step_definitions),
                    'is_locked': False
                })
            
            # If no database simulations, fallback to static content
            if not unified_sims:
                static_sims = HybridSimulationService._convert_static_to_unified_format(
                    networking2_updated_content, "Networking 2"
                )
                unified_sims.extend(static_sims)
            
            return unified_sims
            
        except Exception as e:
            current_app.logger.error(f"Error getting combined networking2 content: {str(e)}")
            # Return empty list as fallback
            return []
    
    @staticmethod
    def _add_progression_status(simulations, user_id, sim_type):
        """Add progression/lock status to simulations"""
        # TODO: Implement actual progression logic
        # For now, return simulations as-is (unlocked)
        return simulations
    
    @staticmethod
    def _add_learning_path_progression(learning_paths, user_id):
        """Add progression status to learning path simulations"""
        # TODO: Implement sequential unlock logic
        # For now, return paths as-is (unlocked)
        return learning_paths

# Make service available globally
hybrid_simulation_service = HybridSimulationService()
