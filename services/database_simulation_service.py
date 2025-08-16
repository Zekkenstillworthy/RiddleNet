"""
Database Simulation Service - Provides Database-Only Simulations
==================================================================

This service provides access to database simulations created via Simulation Builder.
All static content has been removed - simulations are now fully database-driven.
"""

from admin.models.simulation import Simulation
from admin.models.class_model import Class
from flask import current_app
import json

class DatabaseSimulationService:
    """Service that provides database simulations only"""
    
    @staticmethod
    def get_all_simulations_for_class(class_id, user_id=None):
        """Get all database simulations available to a class"""
        try:
            # Get class information
            class_obj = Class.query.get(class_id)
            if not class_obj:
                return {"database": [], "learning_paths": []}
            
            # Get database simulations assigned to this class
            database_sims = DatabaseSimulationService._get_database_simulations_for_class(class_id)
            
            # Get learning paths assigned to this class
            learning_paths = DatabaseSimulationService._get_learning_paths_for_class(class_id)
            
            # Add progression status if user_id provided
            if user_id:
                database_sims = DatabaseSimulationService._add_progression_status(database_sims, user_id, "database")
                learning_paths = DatabaseSimulationService._add_learning_path_progression(learning_paths, user_id)
            
            return {
                "database": database_sims,
                "learning_paths": learning_paths,
                "total_count": len(database_sims) + sum(len(lp.get('simulations', [])) for lp in learning_paths)
            }
        except Exception as e:
            print(f"Error in get_all_simulations_for_class: {e}")
            return {"database": [], "learning_paths": []}

    @staticmethod
    def get_combined_networking1_content():
        """Get all networking 1 content - now database only"""
        try:
            # Get database simulations for Networking 1
            database_sims = Simulation.query.filter(
                Simulation.simulation_type.ilike('%networking 1%'),
                Simulation.is_active == True,
                Simulation.is_published == True
            ).all()
            
            return [DatabaseSimulationService._convert_simulation_to_unified_format(sim) for sim in database_sims]
        except Exception as e:
            print(f"Error getting networking1 content: {e}")
            return []

    @staticmethod
    def get_combined_networking2_content():
        """Get all networking 2 content - now database only"""
        try:
            # Get database simulations for Networking 2
            database_sims = Simulation.query.filter(
                Simulation.simulation_type.ilike('%networking 2%'),
                Simulation.is_active == True,
                Simulation.is_published == True
            ).all()
            
            return [DatabaseSimulationService._convert_simulation_to_unified_format(sim) for sim in database_sims]
        except Exception as e:
            print(f"Error getting networking2 content: {e}")
            return []

    @staticmethod
    def _get_database_simulations_for_class(class_id):
        """Get database simulations assigned to this class"""
        try:
            from admin.models.simulation_assignment import SimulationAssignment
            
            assignments = SimulationAssignment.query.filter_by(class_id=class_id).all()
            simulations = []
            
            for assignment in assignments:
                if assignment.simulation and assignment.simulation.is_active:
                    simulations.append(DatabaseSimulationService._convert_simulation_to_unified_format(assignment.simulation))
            
            return simulations
        except Exception as e:
            print(f"Error getting database simulations: {e}")
            return []

    @staticmethod
    def _get_learning_paths_for_class(class_id):
        """Get learning paths assigned to this class"""
        try:
            # Learning paths functionality can be implemented here when needed
            return []
        except Exception as e:
            print(f"Error getting learning paths: {e}")
            return []

    @staticmethod
    def _convert_simulation_to_unified_format(simulation):
        """Convert a database simulation to unified format"""
        return {
            'id': simulation.id,
            'title': simulation.title,
            'description': simulation.description,
            'type': 'database',
            'category': simulation.simulation_type,
            'difficulty': getattr(simulation, 'difficulty', 'medium'),
            'estimated_time': getattr(simulation, 'estimated_time', 30),
            'url': f'/dynamic/simulation/{simulation.id}',
            'icon': getattr(simulation, 'icon', 'fas fa-network-wired'),
            'is_published': simulation.is_published,
            'created_at': simulation.created_at.isoformat() if simulation.created_at else None
        }

    @staticmethod
    def _add_progression_status(simulations, user_id, sim_type):
        """Add progression status to simulations"""
        # TODO: Implement progression tracking
        for sim in simulations:
            sim['progress'] = {
                'completed': False,
                'score': 0,
                'attempts': 0,
                'last_attempt': None
            }
        return simulations

    @staticmethod
    def _add_learning_path_progression(learning_paths, user_id):
        """Add progression status to learning paths"""
        # TODO: Implement learning path progression tracking
        for path in learning_paths:
            path['progress'] = {
                'completed_simulations': 0,
                'total_simulations': len(path.get('simulations', [])),
                'completion_percentage': 0
            }
        return learning_paths

# Backward compatibility alias
HybridSimulationService = DatabaseSimulationService
