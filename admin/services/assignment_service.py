"""
Week 2 Enhanced Assignment Service

Provides multi-level assignment logic and real-time notification integration
for the dynamic simulation system.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from admin import db
from admin.models.simulation_assignment import SimulationAssignment, SimulationAssignmentAttempt
from admin.models.simulation import Simulation
from admin.models.class_model import Class
from socket_events import (
    emit_assignment_created,
    emit_new_simulation_available,
    emit_assignment_notification
)

class EnhancedAssignmentService:
    """Service for managing assignments with Week 2 enhancements"""
    
    def create_lesson_assignment(self, simulation_id: int, class_id: int, lesson_name: str, 
                               due_date: Optional[datetime] = None, max_attempts: int = 3) -> SimulationAssignment:
        """Create a lesson-based assignment"""
        assignment = SimulationAssignment(
            title=f"Lesson Assignment: {lesson_name}",
            description=f"Complete the simulation for lesson: {lesson_name}",
            simulation_id=simulation_id,
            class_id=class_id,
            assignment_type='lesson',
            lesson_name=lesson_name,
            due_date=due_date or (datetime.utcnow() + timedelta(days=7)),
            max_attempts=max_attempts,
            assigned_by=1,  # TODO: Get current admin user
            is_active=True,
            is_published=True
        )
        
        db.session.add(assignment)
        db.session.commit()
        
        # Real-time notification
        emit_assignment_created(assignment.id, class_id, 'lesson')
        
        return assignment
    
    def create_category_auto_assignment(self, category: str, class_ids: List[int]) -> List[SimulationAssignment]:
        """Automatically assign all simulations in a category to specified classes"""
        assignments = []
        
        # Get all simulations in the category
        simulations = Simulation.query.filter_by(
            category=category,
            is_published=True,
            is_active=True
        ).all()
        
        for class_id in class_ids:
            class_obj = Class.query.get(class_id)
            if not class_obj:
                continue
                
            for simulation in simulations:
                # Check if assignment already exists
                existing = SimulationAssignment.query.filter_by(
                    simulation_id=simulation.id,
                    class_id=class_id,
                    assignment_type='category'
                ).first()
                
                if not existing:
                    assignment = SimulationAssignment(
                        title=f"Auto-Assignment: {simulation.title}",
                        description=f"Automatically assigned from {category} category",
                        simulation_id=simulation.id,
                        class_id=class_id,
                        assignment_type='category',
                        category_match=category,
                        auto_assign=True,
                        due_date=datetime.utcnow() + timedelta(days=14),
                        max_attempts=3,
                        assigned_by=1,  # TODO: Get current admin user
                        is_active=True,
                        is_published=True
                    )
                    
                    db.session.add(assignment)
                    assignments.append(assignment)
        
        db.session.commit()
        
        # Notify affected classes
        for class_id in class_ids:
            emit_assignment_created(assignments[0].id if assignments else None, class_id, 'category')
        
        return assignments
    
    def create_explicit_assignment(self, simulation_id: int, class_id: int, title: str,
                                 description: str = "", due_date: Optional[datetime] = None,
                                 max_attempts: int = 3) -> SimulationAssignment:
        """Create an explicit assignment with custom settings"""
        assignment = SimulationAssignment(
            title=title,
            description=description,
            simulation_id=simulation_id,
            class_id=class_id,
            assignment_type='explicit',
            due_date=due_date or (datetime.utcnow() + timedelta(days=7)),
            max_attempts=max_attempts,
            assigned_by=1,  # TODO: Get current admin user
            is_active=True,
            is_published=True
        )
        
        db.session.add(assignment)
        db.session.commit()
        
        # Real-time notification
        emit_assignment_created(assignment.id, class_id, 'explicit')
        
        return assignment
    
    def auto_assign_new_simulation(self, simulation_id: int) -> List[SimulationAssignment]:
        """Automatically assign a new simulation to relevant classes based on category"""
        simulation = Simulation.query.get(simulation_id)
        if not simulation:
            return []
            
        assignments = []
        
        # Find classes that match the simulation category
        matching_classes = Class.query.filter(
            Class.name.ilike(f'%{simulation.category}%')
        ).all()
        
        for class_obj in matching_classes:
            # Check if auto-assignment is enabled for this category
            existing_auto = SimulationAssignment.query.filter_by(
                class_id=class_obj.id,
                assignment_type='category',
                category_match=simulation.category,
                auto_assign=True
            ).first()
            
            if existing_auto:  # Auto-assignment is enabled for this category
                assignment = SimulationAssignment(
                    title=f"Auto-Assignment: {simulation.title}",
                    description=f"Automatically assigned based on {simulation.category} category",
                    simulation_id=simulation_id,
                    class_id=class_obj.id,
                    assignment_type='category',
                    category_match=simulation.category,
                    auto_assign=True,
                    due_date=datetime.utcnow() + timedelta(days=14),
                    max_attempts=3,
                    assigned_by=1,  # TODO: Get current admin user
                    is_active=True,
                    is_published=True
                )
                
                db.session.add(assignment)
                assignments.append(assignment)
        
        db.session.commit()
        
        # Send real-time notifications
        if assignments:
            class_ids = [a.class_id for a in assignments]
            emit_new_simulation_available(simulation_id, simulation.category, class_ids)
        
        return assignments
    
    def get_assignments_for_class(self, class_id: int, assignment_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all assignments for a class with detailed information"""
        query = SimulationAssignment.query.filter_by(
            class_id=class_id,
            is_active=True
        )
        
        if assignment_type:
            query = query.filter_by(assignment_type=assignment_type)
        
        assignments = query.all()
        
        result = []
        for assignment in assignments:
            simulation = Simulation.query.get(assignment.simulation_id)
            
            assignment_data = {
                'id': assignment.id,
                'title': assignment.title,
                'description': assignment.description,
                'assignment_type': assignment.assignment_type,
                'lesson_name': assignment.lesson_name,
                'category_match': assignment.category_match,
                'auto_assign': assignment.auto_assign,
                'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
                'max_attempts': assignment.max_attempts,
                'created_at': assignment.created_at.isoformat(),
                'simulation': {
                    'id': simulation.id,
                    'title': simulation.title,
                    'description': simulation.description,
                    'category': simulation.category,
                    'difficulty': simulation.difficulty
                } if simulation else None
            }
            
            result.append(assignment_data)
        
        return result
    
    def enable_category_auto_assignment(self, class_id: int, category: str) -> bool:
        """Enable automatic assignment for all simulations in a category"""
        try:
            # Create a master auto-assignment record
            auto_assignment = SimulationAssignment(
                title=f"Auto-Assignment Master: {category}",
                description=f"Master record for auto-assigning {category} simulations",
                simulation_id=1,  # Placeholder - will be overridden by individual assignments
                class_id=class_id,
                assignment_type='category',
                category_match=category,
                auto_assign=True,
                due_date=datetime.utcnow() + timedelta(days=365),  # Far future
                max_attempts=3,
                assigned_by=1,  # TODO: Get current admin user
                is_active=True,
                is_published=True
            )
            
            db.session.add(auto_assignment)
            
            # Auto-assign existing simulations in this category
            self.create_category_auto_assignment(category, [class_id])
            
            db.session.commit()
            return True
            
        except Exception as e:
            print(f"Error enabling category auto-assignment: {e}")
            db.session.rollback()
            return False
    
    def get_assignment_statistics(self, class_id: int) -> Dict[str, Any]:
        """Get comprehensive assignment statistics for a class"""
        assignments = SimulationAssignment.query.filter_by(
            class_id=class_id,
            is_active=True
        ).all()
        
        total_assignments = len(assignments)
        lesson_assignments = len([a for a in assignments if a.assignment_type == 'lesson'])
        category_assignments = len([a for a in assignments if a.assignment_type == 'category'])
        explicit_assignments = len([a for a in assignments if a.assignment_type == 'explicit'])
        auto_assignments = len([a for a in assignments if a.auto_assign])
        
        # Calculate due dates
        overdue = len([a for a in assignments if a.due_date and a.due_date < datetime.utcnow()])
        due_soon = len([a for a in assignments if a.due_date and 
                       datetime.utcnow() <= a.due_date <= datetime.utcnow() + timedelta(days=3)])
        
        return {
            'total_assignments': total_assignments,
            'by_type': {
                'lesson': lesson_assignments,
                'category': category_assignments,
                'explicit': explicit_assignments,
                'auto_assigned': auto_assignments
            },
            'by_status': {
                'overdue': overdue,
                'due_soon': due_soon,
                'upcoming': total_assignments - overdue - due_soon
            },
            'assignment_details': [a.to_dict() for a in assignments]
        }

# Global service instance
assignment_service = EnhancedAssignmentService()
