#!/usr/bin/env python3
"""
Check detailed simulation assignments for Class 9 (Networking 2)
"""

import eventlet
eventlet.monkey_patch()

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from __init__ import create_app, db
from admin.models.simulation_assignment import SimulationAssignment
from admin.models.simulation import Simulation
from admin.models.class_model import Class
from admin.models.module import Module

def check_class_9_details():
    app = create_app()
    
    with app.app_context():
        try:
            # Get class 9 info
            class_9 = Class.query.get(9)
            print(f"Class 9: {class_9.name}")
            print("=" * 50)
            
            # Get simulation assignments for class 9
            assignments = SimulationAssignment.query.filter_by(class_id=9).all()
            print(f"\nAll simulation assignments for class 9: {len(assignments)}")
            
            for i, assignment in enumerate(assignments, 1):
                print(f"\n{i}. Assignment: {assignment.title}")
                print(f"   - Simulation: {assignment.simulation.title if assignment.simulation else 'None'}")
                print(f"   - Simulation Description: {assignment.simulation.description if assignment.simulation else 'None'}")
                print(f"   - Is Active: {assignment.is_active}")
                print(f"   - Is Published: {assignment.is_published}")
                print(f"   - Is Available: {assignment.is_available}")
                print(f"   - Assignment Type: {assignment.assignment_type}")
                print(f"   - Module ID: {assignment.module_id}")
                
            # Get modules for class 9
            modules = Module.query.filter_by(class_id=9, is_active=True).order_by(Module.order_index).all()
            print(f"\nModules in Class 9: {len(modules)}")
            
            for module in modules:
                print(f"\nModule {module.id}: {module.title}")
                print(f"  - Description: {module.description}")
                
                # Check which simulations would show up on this module page
                module_title_lower = module.title.lower()
                matching_simulations = []
                
                for assignment in assignments:
                    if assignment.simulation and assignment.simulation.is_published:
                        sim_title_lower = assignment.simulation.title.lower()
                        sim_description_lower = (assignment.simulation.description or '').lower()
                        
                        # Apply the same matching logic from the route
                        if (str(module.id) in sim_title_lower or 
                            any(word in sim_title_lower for word in module_title_lower.split()) or
                            any(word in sim_description_lower for word in module_title_lower.split())):
                            matching_simulations.append(assignment.simulation.title)
                
                if matching_simulations:
                    print(f"  - Matching simulations: {matching_simulations}")
                else:
                    print(f"  - No matching simulations")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    check_class_9_details()