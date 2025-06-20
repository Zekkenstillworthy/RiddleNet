from flask import current_app
from admin.models.learning_path import LearningPath, LearningPathSimulation, UserLearningProgress
from admin.models.simulation import Simulation
from admin.models import db
from datetime import datetime

class LearningPathController:
    """Controller for managing learning paths"""
    
    def get_all_learning_paths(self):
        """Get all learning paths"""
        try:
            learning_paths = LearningPath.query.all()
            return [path.to_dict() for path in learning_paths]
        except Exception as e:
            current_app.logger.error(f"Error getting learning paths: {str(e)}")
            return {'error': 'Failed to get learning paths'}
    
    def get_learning_path_by_id(self, path_id):
        """Get learning path by ID"""
        try:
            learning_path = LearningPath.query.get(path_id)
            if not learning_path:
                return {'error': 'Learning path not found'}
            
            return learning_path.to_dict()
        except Exception as e:
            current_app.logger.error(f"Error getting learning path: {str(e)}")
            return {'error': 'Failed to get learning path'}
    
    def create_learning_path(self, path_data, admin_user_id):
        """Create a new learning path"""
        try:
            learning_path = LearningPath(
                title=path_data['title'],
                description=path_data['description'],
                course_level=path_data['course_level'],
                created_by=admin_user_id,
                is_active=path_data.get('is_active', True),
                is_published=path_data.get('is_published', False),
                total_duration=path_data.get('total_duration', 0),
                difficulty=path_data.get('difficulty', 'beginner')
            )
            
            db.session.add(learning_path)
            db.session.commit()
            
            return {'success': True, 'learning_path': learning_path.to_dict()}
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating learning path: {str(e)}")
            return {'error': 'Failed to create learning path'}
    
    def update_learning_path(self, path_id, path_data, admin_user_id):
        """Update an existing learning path"""
        try:
            learning_path = LearningPath.query.get(path_id)
            if not learning_path:
                return {'error': 'Learning path not found'}
            
            # Update fields
            learning_path.title = path_data.get('title', learning_path.title)
            learning_path.description = path_data.get('description', learning_path.description)
            learning_path.course_level = path_data.get('course_level', learning_path.course_level)
            learning_path.is_active = path_data.get('is_active', learning_path.is_active)
            learning_path.is_published = path_data.get('is_published', learning_path.is_published)
            learning_path.total_duration = path_data.get('total_duration', learning_path.total_duration)
            learning_path.difficulty = path_data.get('difficulty', learning_path.difficulty)
            learning_path.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return {'success': True, 'learning_path': learning_path.to_dict()}
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating learning path: {str(e)}")
            return {'error': 'Failed to update learning path'}
    
    def delete_learning_path(self, path_id):
        """Delete a learning path"""
        try:
            learning_path = LearningPath.query.get(path_id)
            if not learning_path:
                return {'error': 'Learning path not found'}
            
            db.session.delete(learning_path)
            db.session.commit()
            
            return {'success': True, 'message': 'Learning path deleted successfully'}
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting learning path: {str(e)}")
            return {'error': 'Failed to delete learning path'}
    
    def _add_simulations_to_path(self, path_id, simulation_associations):
        """Add simulations to a learning path"""
        try:
            # Remove existing associations
            LearningPathSimulation.query.filter_by(learning_path_id=path_id).delete()
            db.session.commit()
            
            # Add new associations
            for assoc in simulation_associations:
                path_sim = LearningPathSimulation(
                    learning_path_id=path_id,
                    simulation_id=assoc['simulation_id'],
                    order_index=assoc['order_index'],
                    is_required=assoc.get('is_required', True),
                    unlock_criteria=assoc.get('unlock_criteria', {})
                )
                db.session.add(path_sim)
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding simulations to path: {str(e)}")
            return False
    
    def create_learning_path_with_simulations(self, path_data, simulation_ids, admin_user_id):
        """Create a learning path and associate simulations"""
        try:
            # Create the learning path
            path_result = self.create_learning_path(path_data, admin_user_id)
            if 'error' in path_result:
                return path_result
            
            path_id = path_result['learning_path']['id']
            
            # Associate simulations with order and requirements
            simulation_associations = []
            for i, sim_data in enumerate(simulation_ids):
                simulation_id = sim_data.get('id') if isinstance(sim_data, dict) else sim_data
                
                # Verify simulation exists
                simulation = Simulation.query.get(simulation_id)
                if not simulation:
                    continue
                    
                association = {
                    'simulation_id': simulation_id,
                    'order_index': sim_data.get('order', i) if isinstance(sim_data, dict) else i,
                    'is_required': sim_data.get('required', True) if isinstance(sim_data, dict) else True,
                    'unlock_criteria': sim_data.get('unlock_criteria') if isinstance(sim_data, dict) else None
                }
                simulation_associations.append(association)
            
            # Add simulations to path
            self._add_simulations_to_path(path_id, simulation_associations)
            
            # Return updated learning path with simulations
            return self.get_learning_path_by_id(path_id)
            
        except Exception as e:
            current_app.logger.error(f"Error creating learning path with simulations: {str(e)}")
            return {'error': 'Failed to create learning path with simulations'}

    def get_simulation_recommendations(self, user_id, completed_simulation_id):
        """Get recommended simulations based on user progress"""
        try:
            completed_simulation = Simulation.query.get(completed_simulation_id)
            if not completed_simulation:
                return []
            
            # Get user's learning path progress
            user_progress = UserLearningProgress.query.filter_by(
                user_id=user_id,
                status='completed'
            ).all()
            
            completed_sim_ids = [p.simulation_id for p in user_progress]
            
            # Find simulations in the same category or type
            similar_simulations = Simulation.query.filter(
                Simulation.id.notin_(completed_sim_ids),
                Simulation.is_active == True,
                Simulation.is_published == True,
                db.or_(
                    Simulation.simulation_type == completed_simulation.simulation_type,
                    Simulation.category == completed_simulation.category
                )
            ).limit(3).all()
            
            recommendations = []
            for sim in similar_simulations:
                recommendations.append({
                    'id': sim.id,
                    'title': sim.title,
                    'description': sim.description[:100] + '...',
                    'difficulty': sim.difficulty,
                    'estimated_duration': sim.estimated_duration
                })
            
            return recommendations
            
        except Exception as e:
            current_app.logger.error(f"Error getting recommendations: {str(e)}")
            return []
