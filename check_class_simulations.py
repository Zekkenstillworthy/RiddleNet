#!/usr/bin/env python3
"""
Check simulation assignments for class 7 (Networking 2)
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from __init__ import create_app, db
from admin.models.simulation_assignment import SimulationAssignment
from admin.models.simulation import Simulation
from admin.models.class_model import Class

def check_class_simulations():
    app = create_app()
    
    with app.app_context():
        # Get class 7 info
        class_7 = Class.query.get(7)
        if not class_7:
            print("Class 7 not found!")
            return
        
        print(f"Class 7: {class_7.name}")
        print("=" * 50)
        
        # Get simulation assignments for class 7
        assignments = SimulationAssignment.query.filter_by(class_id=7).all()
        print(f"\nTotal simulation assignments for class 7: {len(assignments)}")
        
        if assignments:
            print("\nDetailed assignment information:")
            for i, assignment in enumerate(assignments, 1):
                print(f"\n{i}. Assignment: {assignment.title}")
                print(f"   - Simulation ID: {assignment.simulation_id}")
                if assignment.simulation:
                    print(f"   - Simulation Title: {assignment.simulation.title}")
                    print(f"   - Simulation Type: {assignment.simulation.simulation_type}")
                print(f"   - Assignment Type: {assignment.assignment_type}")
                print(f"   - Is Active: {assignment.is_active}")
                print(f"   - Is Published: {assignment.is_published}")
                print(f"   - Is Available: {assignment.is_available}")
                print(f"   - Module ID: {assignment.module_id}")
                print(f"   - Due Date: {assignment.due_date}")
                print(f"   - Available From: {assignment.available_from}")
                print(f"   - Available Until: {assignment.available_until}")
        
        # Also check active assignments specifically
        active_assignments = SimulationAssignment.query.filter_by(
            class_id=7, 
            is_active=True
        ).all()
        print(f"\nActive assignments: {len(active_assignments)}")
        
        # Check published assignments
        published_assignments = SimulationAssignment.query.filter_by(
            class_id=7, 
            is_published=True
        ).all()
        print(f"Published assignments: {len(published_assignments)}")
        
        # Check available assignments (using property)
        available_assignments = [a for a in assignments if a.is_available]
        print(f"Currently available assignments: {len(available_assignments)}")
        
        # Check class modules for context
        print(f"\nClass 7 Modules:")
        if hasattr(class_7, 'modules'):
            for module in class_7.modules:
                print(f"  - Module {module.id}: {module.title}")
                
                # Check if any assignments are tied to this module
                module_assignments = SimulationAssignment.query.filter_by(module_id=module.id).all()
                if module_assignments:
                    print(f"    Assignments: {len(module_assignments)}")

if __name__ == "__main__":
    check_class_simulations()