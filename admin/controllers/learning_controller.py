from flask import current_app
from admin import db
from admin.models.learning_path import LearningPath, LearningPathSimulation, UserLearningProgress
from admin.models.simulation import Simulation
from datetime import datetime
import json

class LearningPathController:
    """
    Learning Path Controller for managing structured learning experiences
    """
    
    def get_dashboard_data(self):
        """Get learning path dashboard data"""
        try:
            # Basic statistics
            total_paths = LearningPath.query.filter_by(is_active=True).count()
            published_paths = LearningPath.query.filter_by(is_active=True, is_published=True).count()
            
            # Recent paths
            recent_paths = LearningPath.query.filter_by(is_active=True)\
                .order_by(LearningPath.created_at.desc()).limit(5).all()
            
            # Popular paths (most enrollments)
            popular_paths = LearningPath.query.filter_by(is_active=True, is_published=True)\
                .order_by(LearningPath.total_enrollments.desc()).limit(5).all()
            
            # Get aggregate statistics
            total_enrollments = db.session.query(
                db.func.sum(LearningPath.total_enrollments)
            ).filter(LearningPath.is_active == True).scalar() or 0
            
            total_completions = db.session.query(
                db.func.sum(LearningPath.total_completions)
            ).filter(LearningPath.is_active == True).scalar() or 0
            
            return {
                'statistics': {
                    'total_paths': total_paths,
                    'published_paths': published_paths,
                    'total_enrollments': total_enrollments,
                    'total_completions': total_completions,
                    'average_completion_rate': (total_completions / total_enrollments * 100) if total_enrollments > 0 else 0
                },
                'recent_paths': [path.to_dict() for path in recent_paths],
                'popular_paths': [path.to_dict() for path in popular_paths]
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting learning path dashboard data: {str(e)}")
            return {'error': 'Failed to load dashboard data'}
    
    def create_learning_path(self, path_data, admin_user_id):
        """Create a new learning path"""
        try:
            # Validate required fields
            required_fields = ['title', 'description', 'course_level']
            for field in required_fields:
                if not path_data.get(field):
                    return {'error': f'Missing required field: {field}'}
            
            learning_path = LearningPath(
                title=path_data['title'],
                description=path_data['description'],
                course_level=path_data['course_level'],
                learning_objectives=path_data.get('learning_objectives', []),
                prerequisites=path_data.get('prerequisites', []),
                difficulty_level=path_data.get('difficulty_level', 'Beginner'),
                is_active=path_data.get('is_active', True),
                is_published=path_data.get('is_published', False),
                created_by=admin_user_id
            )
            
            db.session.add(learning_path)
            db.session.commit()
            
            current_app.logger.info(f"Learning path created successfully: {learning_path.id}")
            
            return {
                'success': True,
                'learning_path': learning_path.to_dict(),
                'message': 'Learning path created successfully!'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating learning path: {str(e)}")
            return {'error': f'Failed to create learning path: {str(e)}'}
    
    def create_learning_path_with_simulations(self, path_data, simulation_associations, admin_user_id):
        """Create learning path and associate simulations"""
        try:
            # Create the learning path first
            path_result = self.create_learning_path(path_data, admin_user_id)
            if 'error' in path_result:
                return path_result
            
            learning_path_id = path_result['learning_path']['id']
            
            # Add simulations to the path
            total_duration = 0
            for i, sim_data in enumerate(simulation_associations):
                simulation_id = sim_data.get('id') if isinstance(sim_data, dict) else sim_data
                
                # Verify simulation exists
                simulation = Simulation.query.get(simulation_id)
                if not simulation:
                    continue
                
                # Create association
                association = LearningPathSimulation(
                    learning_path_id=learning_path_id,
                    simulation_id=simulation_id,
                    order_index=sim_data.get('order', i) if isinstance(sim_data, dict) else i,
                    is_required=sim_data.get('required', True) if isinstance(sim_data, dict) else True,
                    unlock_criteria=sim_data.get('unlock_criteria', {}) if isinstance(sim_data, dict) else {}
                )
                
                db.session.add(association)
                total_duration += simulation.estimated_duration
            
            # Update learning path with total duration
            learning_path = LearningPath.query.get(learning_path_id)
            learning_path.estimated_total_duration = total_duration
            
            db.session.commit()
            
            return self.get_learning_path_by_id(learning_path_id)
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating learning path with simulations: {str(e)}")
            return {'error': 'Failed to create learning path with simulations'}
    
    def get_all_learning_paths(self, include_inactive=False):
        """Get all learning paths"""
        try:
            query = LearningPath.query
            
            if not include_inactive:
                query = query.filter_by(is_active=True)
            
            paths = query.order_by(LearningPath.created_at.desc()).all()
            
            return {
                'learning_paths': [path.to_dict() for path in paths],
                'total_count': len(paths)
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting learning paths: {str(e)}")
            return {'error': 'Failed to retrieve learning paths'}
    
    def get_learning_path_by_id(self, path_id, include_simulations=True):
        """Get learning path by ID"""
        try:
            path = LearningPath.query.get(path_id)
            if not path:
                return {'error': 'Learning path not found'}
            
            return {
                'learning_path': path.to_dict(include_simulations=include_simulations)
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting learning path {path_id}: {str(e)}")
            return {'error': 'Failed to retrieve learning path'}
    
    def update_learning_path(self, path_id, update_data):
        """Update existing learning path"""
        try:
            path = LearningPath.query.get(path_id)
            if not path:
                return {'error': 'Learning path not found'}
            
            # Update allowed fields
            allowed_fields = [
                'title', 'description', 'course_level', 'learning_objectives',
                'prerequisites', 'difficulty_level', 'is_active', 'is_published'
            ]
            
            for field in allowed_fields:
                if field in update_data:
                    setattr(path, field, update_data[field])
            
            path.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'success': True,
                'learning_path': path.to_dict(),
                'message': 'Learning path updated successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating learning path {path_id}: {str(e)}")
            return {'error': 'Failed to update learning path'}
    
    def add_simulation_to_path(self, path_id, simulation_id, order_index=None, is_required=True, unlock_criteria=None):
        """Add simulation to learning path"""
        try:
            path = LearningPath.query.get(path_id)
            if not path:
                return {'error': 'Learning path not found'}
            
            simulation = Simulation.query.get(simulation_id)
            if not simulation:
                return {'error': 'Simulation not found'}
            
            # Check if association already exists
            existing = LearningPathSimulation.query.filter_by(
                learning_path_id=path_id,
                simulation_id=simulation_id
            ).first()
            
            if existing:
                return {'error': 'Simulation already in learning path'}
            
            # Determine order index
            if order_index is None:
                max_order = db.session.query(
                    db.func.max(LearningPathSimulation.order_index)
                ).filter_by(learning_path_id=path_id).scalar() or -1
                order_index = max_order + 1
            
            # Create association
            association = LearningPathSimulation(
                learning_path_id=path_id,
                simulation_id=simulation_id,
                order_index=order_index,
                is_required=is_required,
                unlock_criteria=unlock_criteria or {}
            )
            
            db.session.add(association)
            
            # Update total duration
            path.estimated_total_duration += simulation.estimated_duration
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Simulation added to learning path successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding simulation to path: {str(e)}")
            return {'error': 'Failed to add simulation to learning path'}
    
    def remove_simulation_from_path(self, path_id, simulation_id):
        """Remove simulation from learning path"""
        try:
            association = LearningPathSimulation.query.filter_by(
                learning_path_id=path_id,
                simulation_id=simulation_id
            ).first()
            
            if not association:
                return {'error': 'Simulation not found in learning path'}
            
            # Update total duration
            path = LearningPath.query.get(path_id)
            if path and association.simulation:
                path.estimated_total_duration -= association.simulation.estimated_duration
            
            db.session.delete(association)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Simulation removed from learning path successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error removing simulation from path: {str(e)}")
            return {'error': 'Failed to remove simulation from learning path'}
    
    def reorder_simulations_in_path(self, path_id, simulation_order):
        """Reorder simulations in learning path"""
        try:
            path = LearningPath.query.get(path_id)
            if not path:
                return {'error': 'Learning path not found'}
            
            # Update order indices
            for i, simulation_id in enumerate(simulation_order):
                association = LearningPathSimulation.query.filter_by(
                    learning_path_id=path_id,
                    simulation_id=simulation_id
                ).first()
                
                if association:
                    association.order_index = i
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Simulations reordered successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error reordering simulations: {str(e)}")
            return {'error': 'Failed to reorder simulations'}
    
    def get_user_progress_in_path(self, user_id, path_id):
        """Get user's progress in a specific learning path"""
        try:
            path = LearningPath.query.get(path_id)
            if not path:
                return {'error': 'Learning path not found'}
            
            # Get user progress records
            progress_records = UserLearningProgress.query.filter_by(
                user_id=user_id,
                learning_path_id=path_id
            ).all()
            
            # Calculate overall progress
            path_progress = path.calculate_user_progress(user_id)
            
            # Get next simulation
            next_simulation = path.get_next_simulation_for_user(user_id)
            
            return {
                'learning_path': path.to_dict(),
                'user_progress': path_progress,
                'progress_records': [record.to_dict() for record in progress_records],
                'next_simulation': next_simulation.to_dict() if next_simulation else None
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting user progress: {str(e)}")
            return {'error': 'Failed to get user progress'}
    
    def update_user_progress(self, user_id, learning_path_id, simulation_id, attempt_data):
        """Update user progress based on simulation attempt"""
        try:
            # Get or create progress record
            progress = UserLearningProgress.query.filter_by(
                user_id=user_id,
                learning_path_id=learning_path_id,
                simulation_id=simulation_id
            ).first()
            
            if not progress:
                progress = UserLearningProgress(
                    user_id=user_id,
                    learning_path_id=learning_path_id,
                    simulation_id=simulation_id
                )
                db.session.add(progress)
            
            # Update progress
            progress.update_progress(attempt_data)
            
            # Update learning path enrollment/completion statistics
            path = LearningPath.query.get(learning_path_id)
            if path:
                # Check if this is a new enrollment
                user_progress_count = UserLearningProgress.query.filter_by(
                    user_id=user_id,
                    learning_path_id=learning_path_id
                ).count()
                
                if user_progress_count == 1:  # First simulation in path
                    path.total_enrollments += 1
                
                # Check if path is completed
                if attempt_data.get('completed', False):
                    user_path_progress = path.calculate_user_progress(user_id)
                    if user_path_progress['completion_percentage'] >= 100:
                        path.total_completions += 1
            
            db.session.commit()
            
            return {
                'success': True,
                'progress': progress.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating user progress: {str(e)}")
            return {'error': 'Failed to update user progress'}
    
    def get_simulation_recommendations(self, user_id, completed_simulation_id):
        """Get recommended simulations based on user progress"""
        try:
            completed_simulation = Simulation.query.get(completed_simulation_id)
            if not completed_simulation:
                return []
            
            # Get user's completed simulations
            user_progress = UserLearningProgress.query.filter_by(
                user_id=user_id,
                status='completed'
            ).all()
            
            completed_sim_ids = [p.simulation_id for p in user_progress]
            
            # Find similar simulations
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
                    'description': sim.description[:100] + '...' if len(sim.description) > 100 else sim.description,
                    'difficulty': sim.difficulty,
                    'estimated_duration': sim.estimated_duration,
                    'reason': f'Similar to {completed_simulation.title}'
                })
            
            return recommendations
            
        except Exception as e:
            current_app.logger.error(f"Error getting recommendations: {str(e)}")
            return []
    
    def delete_learning_path(self, path_id):
        """Soft delete learning path"""
        try:
            path = LearningPath.query.get(path_id)
            if not path:
                return {'error': 'Learning path not found'}
            
            path.is_active = False
            path.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Learning path deleted successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting learning path {path_id}: {str(e)}")
            return {'error': 'Failed to delete learning path'}
    
    def get_learning_path_analytics(self, path_id):
        """Get detailed analytics for a learning path"""
        try:
            path = LearningPath.query.get(path_id)
            if not path:
                return {'error': 'Learning path not found'}
            
            # Get progress records
            progress_records = UserLearningProgress.query.filter_by(
                learning_path_id=path_id
            ).all()
            
            # Calculate analytics
            total_users = len(set(record.user_id for record in progress_records))
            completed_users = len(set(
                record.user_id for record in progress_records 
                if record.status == 'completed'
            ))
            
            # Simulation-specific analytics
            simulation_analytics = {}
            for assoc in path.get_ordered_simulations():
                sim_progress = [r for r in progress_records if r.simulation_id == assoc.simulation_id]
                simulation_analytics[assoc.simulation_id] = {
                    'simulation_title': assoc.simulation.title,
                    'total_attempts': len(sim_progress),
                    'completions': len([r for r in sim_progress if r.status == 'completed']),
                    'average_score': sum(r.best_score for r in sim_progress) / len(sim_progress) if sim_progress else 0,
                    'average_time': sum(r.best_time or 0 for r in sim_progress) / len(sim_progress) if sim_progress else 0
                }
            
            analytics = {
                'basic_stats': path.to_dict(),
                'user_engagement': {
                    'total_users': total_users,
                    'completed_users': completed_users,
                    'completion_rate': (completed_users / total_users * 100) if total_users > 0 else 0,
                    'average_completion_time': path.average_completion_time
                },
                'simulation_analytics': simulation_analytics,
                'recent_activity': [record.to_dict() for record in progress_records[-10:]]
            }
            
            return analytics
            
        except Exception as e:
            current_app.logger.error(f"Error getting learning path analytics: {str(e)}")
            return {'error': 'Failed to get learning path analytics'}
