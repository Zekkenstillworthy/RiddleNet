"""
Enhanced Class Template Generator for Dynamic Database Content
=============================================================

This service enhances class templates to show database simulations assigned to specific classes
with sequential learning path enforcement and Troubleshoot.html-based rendering.
"""

from datetime import datetime, timedelta
from instructor.services.enhanced_class_template_generator import EnhancedClassTemplateGenerator
from instructor.models.simulation_assignment import SimulationAssignment, SimulationAttempt
from instructor.models.simulation import Simulation
# Learning Path model removed - feature deprecated
# from instructor.models.learning_path import LearningPath
from instructor.models.class_model import Class
from __init__ import db
from socket_events import emit_assignment_created, emit_new_simulation_available
import json


class ClassAssignmentManager:
    """
    Manages simulation assignments to classes with sequential enforcement
    """
    
    def __init__(self):
        self.template_generator = EnhancedClassTemplateGenerator()
    
    def assign_simulation_to_class(self, simulation_id, class_id, assignment_type='explicit', 
                                 lesson_name=None, due_days=7, sequential_order=0):
        """
        Assign a simulation to a specific class
        
        Args:
            simulation_id: ID of simulation to assign
            class_id: ID of class to assign to
            assignment_type: 'lesson', 'category', 'explicit'
            lesson_name: Optional lesson grouping
            due_days: Days until due date
            sequential_order: Order for sequential enforcement (0 = no order)
        """
        try:
            # Create assignment
            if assignment_type == 'lesson':
                assignment = SimulationAssignment.create_lesson_assignment(
                    simulation_id, class_id, lesson_name, due_days, sequential_order
                )
            elif assignment_type == 'category':
                simulation = Simulation.query.get(simulation_id)
                assignment = SimulationAssignment.create_category_assignment(
                    simulation_id, class_id, simulation.category, auto_assign=True
                )
            else:  # explicit
                assignment = SimulationAssignment(
                    simulation_id=simulation_id,
                    class_id=class_id,
                    assignment_type='explicit',
                    due_date=datetime.utcnow() + timedelta(days=due_days),
                    sequential_order=sequential_order,
                    created_by=1  # Instructor user
                )
                db.session.add(assignment)
            
            db.session.commit()
            
            # Regenerate class template with new assignment
            self.regenerate_class_template(class_id)
            
            # Emit real-time notification
            emit_assignment_created(assignment.to_dict())
            
            return {'success': True, 'assignment_id': assignment.id}
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to assign simulation: {str(e)}'}
    
    def enable_auto_assignment_for_category(self, class_id, category):
        """
        Enable automatic assignment of all simulations in a category to a class
        """
        try:
            # Find all simulations in category
            simulations = Simulation.query.filter_by(
                category=category,
                is_published=True,
                is_active=True
            ).all()
            
            assignments_created = []
            for simulation in simulations:
                # Check if assignment already exists
                existing = SimulationAssignment.query.filter_by(
                    simulation_id=simulation.id,
                    class_id=class_id
                ).first()
                
                if not existing:
                    assignment = SimulationAssignment.create_category_assignment(
                        simulation.id, class_id, category, auto_assign=True
                    )
                    assignments_created.append(assignment)
            
            db.session.commit()
            
            # Regenerate class template
            self.regenerate_class_template(class_id)
            
            return {
                'success': True, 
                'assignments_created': len(assignments_created),
                'message': f'Auto-assignment enabled for {category}'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Failed to enable auto-assignment: {str(e)}'}
    
    def get_class_assignments(self, class_id, user_id=None):
        """
        Get all assignments for a class with user progress if user_id provided
        """
        try:
            assignments = SimulationAssignment.get_assignments_for_class(class_id)
            
            result = []
            for assignment in assignments:
                assignment_data = assignment.to_dict()
                
                # Add user progress if user_id provided
                if user_id:
                    attempts = SimulationAttempt.query.filter_by(
                        user_id=user_id,
                        simulation_id=assignment.simulation_id
                    ).all()
                    
                    assignment_data['user_progress'] = {
                        'attempts': len(attempts),
                        'best_score': max([a.score for a in attempts]) if attempts else 0,
                        'completed': any(a.is_completed for a in attempts),
                        'can_access': self.can_user_access_simulation(user_id, assignment)
                    }
                
                result.append(assignment_data)
            
            return {'success': True, 'assignments': result}
            
        except Exception as e:
            return {'error': f'Failed to get assignments: {str(e)}'}
    
    def can_user_access_simulation(self, user_id, assignment):
        """
        Check if user can access a simulation based on sequential requirements
        """
        try:
            # If no sequential order, user can access
            if assignment.sequential_order == 0:
                return True
            
            # Get all assignments for this class in order
            class_assignments = SimulationAssignment.query.filter_by(
                class_id=assignment.class_id,
                is_active=True
            ).filter(
                SimulationAssignment.sequential_order > 0,
                SimulationAssignment.sequential_order < assignment.sequential_order
            ).order_by(SimulationAssignment.sequential_order).all()
            
            # Check if user has completed all previous assignments
            for prev_assignment in class_assignments:
                completed = SimulationAttempt.query.filter_by(
                    user_id=user_id,
                    simulation_id=prev_assignment.simulation_id,
                    is_completed=True
                ).first()
                
                if not completed:
                    return False
                
                # Check minimum score if required
                if prev_assignment.min_score_required > 0:
                    if completed.score < prev_assignment.min_score_required:
                        return False
            
            return True
            
        except Exception as e:
            print(f"Error checking access: {e}")
            return False
    
    def regenerate_class_template(self, class_id):
        """
        Regenerate class template with current database assignments
        """
        try:
            class_obj = Class.query.get(class_id)
            if not class_obj:
                return {'error': 'Class not found'}
            
            # Get enhanced template with database content
            template_path = self.template_generator.regenerate_class_resources(class_id)
            
            return {'success': True, 'template_path': template_path}
            
        except Exception as e:
            return {'error': f'Failed to regenerate template: {str(e)}'}
    
    def get_assignment_statistics(self, class_id):
        """
        Get comprehensive statistics for class assignments
        """
        try:
            assignments = SimulationAssignment.get_assignments_for_class(class_id)
            
            # Get attempts for all assignments
            simulation_ids = [a.simulation_id for a in assignments]
            attempts = SimulationAttempt.query.filter(
                SimulationAttempt.simulation_id.in_(simulation_ids)
            ).all()
            
            stats = {
                'total_assignments': len(assignments),
                'assignment_types': {},
                'completion_stats': {
                    'total_attempts': len(attempts),
                    'completed_attempts': len([a for a in attempts if a.is_completed]),
                    'average_score': sum([a.score for a in attempts]) / len(attempts) if attempts else 0
                },
                'assignment_breakdown': []
            }
            
            # Count assignment types
            for assignment in assignments:
                assignment_type = assignment.assignment_type
                stats['assignment_types'][assignment_type] = stats['assignment_types'].get(assignment_type, 0) + 1
            
            # Individual assignment stats
            for assignment in assignments:
                assignment_attempts = [a for a in attempts if a.simulation_id == assignment.simulation_id]
                stats['assignment_breakdown'].append({
                    'assignment_id': assignment.id,
                    'simulation_title': assignment.simulation.title,
                    'assignment_type': assignment.assignment_type,
                    'total_attempts': len(assignment_attempts),
                    'completed_attempts': len([a for a in assignment_attempts if a.is_completed]),
                    'average_score': sum([a.score for a in assignment_attempts]) / len(assignment_attempts) if assignment_attempts else 0
                })
            
            return {'success': True, 'statistics': stats}
            
        except Exception as e:
            return {'error': f'Failed to get statistics: {str(e)}'}


# Global instance for easy access
assignment_manager = ClassAssignmentManager()
