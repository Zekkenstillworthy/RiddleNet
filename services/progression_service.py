"""
Sequential Progression Service - Handles unlock mechanics and progression logic
"""

from __init__ import db
from admin.models.simulation import Simulation
from admin.models.learning_path import LearningPath
from user.models import User
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

class ProgressionService:
    """Manages sequential progression and unlock mechanics"""
    
    def __init__(self):
        self.db = db
    
    def is_simulation_unlocked(self, user_id, simulation_id, learning_path_id=None):
        """Check if a simulation is unlocked for a user"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False
            
            simulation = Simulation.query.get(simulation_id)
            if not simulation:
                return False
            
            # If no learning path specified, simulation is unlocked
            if not learning_path_id:
                return True
            
            learning_path = LearningPath.query.get(learning_path_id)
            if not learning_path:
                return True
            
            # Get simulation order in the learning path
            path_simulations = learning_path.simulations
            sim_index = None
            
            for i, path_sim in enumerate(path_simulations):
                if path_sim.id == simulation_id:
                    sim_index = i
                    break
            
            if sim_index is None:
                return False
            
            # First simulation is always unlocked
            if sim_index == 0:
                return True
            
            # Check if previous simulation is completed
            previous_sim = path_simulations[sim_index - 1]
            return self.is_simulation_completed(user_id, previous_sim.id)
            
        except Exception as e:
            print(f"Error checking simulation unlock status: {e}")
            return True  # Default to unlocked on error
    
    def is_simulation_completed(self, user_id, simulation_id):
        """Check if a user has completed a simulation"""
        try:
            from admin.models.simulation import SimulationAttempt
            
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
        """Get user's progress in a learning path"""
        try:
            learning_path = LearningPath.query.get(learning_path_id)
            if not learning_path:
                return {'completed': 0, 'total': 0, 'percentage': 0}
            
            total_simulations = len(learning_path.simulations)
            completed_simulations = 0
            
            for simulation in learning_path.simulations:
                if self.is_simulation_completed(user_id, simulation.id):
                    completed_simulations += 1
            
            percentage = (completed_simulations / total_simulations * 100) if total_simulations > 0 else 0
            
            return {
                'completed': completed_simulations,
                'total': total_simulations,
                'percentage': round(percentage, 1)
            }
            
        except Exception as e:
            print(f"Error getting user progress: {e}")
            return {'completed': 0, 'total': 0, 'percentage': 0}
    
    def mark_simulation_completed(self, user_id, simulation_id, score=None):
        """Mark a simulation as completed for a user"""
        try:
            from admin.models.simulation import SimulationAttempt
            
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
    
    def get_next_unlocked_simulation(self, user_id, learning_path_id):
        """Get the next unlocked simulation in a learning path"""
        try:
            learning_path = LearningPath.query.get(learning_path_id)
            if not learning_path:
                return None
            
            for simulation in learning_path.simulations:
                if (self.is_simulation_unlocked(user_id, simulation.id, learning_path_id) and 
                    not self.is_simulation_completed(user_id, simulation.id)):
                    return simulation
            
            return None
            
        except Exception as e:
            print(f"Error getting next unlocked simulation: {e}")
            return None
    
    def get_user_achievements(self, user_id):
        """Get achievements for a user"""
        achievements = []
        
        try:
            # Count completed simulations
            from admin.models.simulation import SimulationAttempt
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
