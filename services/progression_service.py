"""
Sequential Progression Service - Handles unlock mechanics and progression logic
Learning Paths feature has been removed from the system.
"""

from __init__ import db
from instructor.models.simulation import Simulation
from user.models import User
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

class ProgressionService:
    """Manages sequential progression and unlock mechanics"""
    
    def __init__(self):
        self.db = db
    
    def is_simulation_unlocked(self, user_id, simulation_id, learning_path_id=None):
        """Check if a simulation is unlocked for a user - Learning Paths removed"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False
            
            simulation = Simulation.query.get(simulation_id)
            if not simulation:
                return False
            
            # Since Learning Paths are removed, all published simulations are unlocked
            return simulation.is_published and simulation.is_active
            
        except Exception as e:
            print(f"Error checking simulation unlock status: {e}")
            return True  # Default to unlocked on error
    
    def is_simulation_completed(self, user_id, simulation_id):
        """Check if a user has completed a simulation"""
        try:
            from instructor.models.simulation import SimulationAttempt
            
            attempt = SimulationAttempt.query.filter_by(
                user_id=user_id,
                simulation_id=simulation_id,
                is_completed=True
            ).first()
            
            return attempt is not None
            
        except Exception as e:
            print(f"Error checking simulation completion: {e}")
            return False
    
    def get_user_progress_in_path(self, user_id, learning_path_id):
        """Get user's progress in a learning path - Learning Paths removed"""
        # Learning Paths feature has been completely removed
        return {'completed': 0, 'total': 0, 'percentage': 0}
    
    def mark_simulation_completed(self, user_id, simulation_id, score=None):
        """Mark a simulation as completed for a user"""
        try:
            from instructor.models.simulation import SimulationAttempt
            
            # Check if already completed
            existing_attempt = SimulationAttempt.query.filter_by(
                user_id=user_id,
                simulation_id=simulation_id,
                is_completed=True
            ).first()
            
            if existing_attempt:
                return existing_attempt
            
            # Create new completion record
            attempt = SimulationAttempt(
                user_id=user_id,
                simulation_id=simulation_id,
                is_completed=True,
                score=score or 0,
                completed_at=datetime.utcnow()
            )
            
            self.db.session.add(attempt)
            self.db.session.commit()
            
            return attempt
            
        except SQLAlchemyError as e:
            self.db.session.rollback()
            print(f"Database error marking simulation completed: {e}")
            return None
        except Exception as e:
            print(f"Error marking simulation completed: {e}")
            return None
    
    def update_module_progress(self, user_id, module_id):
        """Update module progress based on completed lessons"""
        try:
            from instructor.models.module import Module, ModuleProgress, LessonProgress, Lesson
            
            # Get the module
            module = Module.query.get(module_id)
            if not module:
                return None
            
            # Count completed lessons
            completed_lessons = LessonProgress.query.join(
                Lesson, LessonProgress.lesson_id == Lesson.id
            ).filter(
                LessonProgress.user_id == user_id,
                LessonProgress.is_completed == True,
                Lesson.module_id == module_id
            ).count()
            
            # Get or create module progress
            module_progress = ModuleProgress.query.filter_by(
                user_id=user_id,
                module_id=module_id
            ).first()
            
            if not module_progress:
                module_progress = ModuleProgress(
                    user_id=user_id,
                    module_id=module_id
                )
                self.db.session.add(module_progress)
            
            # Update progress
            total_lessons = module.total_lessons
            if total_lessons > 0:
                module_progress.completed_lessons = completed_lessons
                module_progress.progress_percentage = (completed_lessons / total_lessons) * 100
                module_progress.is_completed = completed_lessons >= total_lessons
                
                if module_progress.is_completed and not module_progress.completed_at:
                    module_progress.completed_at = datetime.utcnow()
            
            # Note: Don't commit here - let the caller handle the transaction
            return module_progress
            
        except Exception as e:
            print(f"Error updating module progress: {e}")
            raise  # Re-raise the exception so the caller can handle it
    
    def get_next_unlocked_simulation(self, user_id, learning_path_id):
        """Get the next unlocked simulation in a learning path - Learning Paths removed"""
        # Learning Paths feature has been completely removed
        return None
    
    def get_user_achievements(self, user_id):
        """Get achievements for a user"""
        achievements = []
        
        try:
            # Count completed simulations
            from instructor.models.simulation import SimulationAttempt
            completed_count = SimulationAttempt.query.filter_by(
                user_id=user_id,
                is_completed=True
            ).count()
            
            # Achievement badges
            if completed_count >= 1:
                achievements.append("First Steps")
            if completed_count >= 5:
                achievements.append("Getting Started")
            if completed_count >= 10:
                achievements.append("Making Progress")
            if completed_count >= 20:
                achievements.append("Dedicated Learner")
            if completed_count >= 50:
                achievements.append("Master Student")
            
            # Check for perfect scores
            perfect_scores = SimulationAttempt.query.filter_by(
                user_id=user_id,
                is_completed=True
            ).filter(SimulationAttempt.score >= 95).count()
            
            if perfect_scores >= 3:
                achievements.append("Perfectionist")
            
            return achievements
            
        except Exception as e:
            print(f"Error getting achievements: {e}")
            return []

# Global instance
progression_service = ProgressionService()
