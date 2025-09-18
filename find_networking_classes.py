#!/usr/bin/env python3
"""
Find which class is Networking 2 and check its simulation assignments
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

def find_networking_classes():
    app = create_app()
    
    with app.app_context():
        try:
            # Find all classes with "Networking" in the name
            classes = Class.query.filter(Class.name.ilike('%networking%')).all()
            
            print("Classes with 'Networking' in the name:")
            print("=" * 50)
            
            for cls in classes:
                print(f"Class {cls.id}: {cls.name}")
                
                # Get simulation assignments for this class
                assignments = SimulationAssignment.query.filter_by(class_id=cls.id).all()
                active_assignments = [a for a in assignments if a.is_active]
                published_assignments = [a for a in assignments if a.is_published]
                available_assignments = [a for a in assignments if a.is_available]
                
                print(f"  - Total assignments: {len(assignments)}")
                print(f"  - Active assignments: {len(active_assignments)}")
                print(f"  - Published assignments: {len(published_assignments)}")
                print(f"  - Available assignments: {len(available_assignments)}")
                
                if available_assignments:
                    print("  - Available simulations:")
                    for assignment in available_assignments:
                        sim_title = assignment.simulation.title if assignment.simulation else "Unknown"
                        print(f"    • {assignment.title}: {sim_title}")
                
                print()
            
            # Check all classes that might have simulation assignments
            print("\nAll classes with simulation assignments:")
            print("=" * 50)
            
            classes_with_sims = db.session.query(Class).join(SimulationAssignment).distinct().all()
            for cls in classes_with_sims:
                assignments = SimulationAssignment.query.filter_by(class_id=cls.id).all()
                available_assignments = [a for a in assignments if a.is_available]
                print(f"Class {cls.id}: {cls.name} - {len(available_assignments)} available simulations")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    find_networking_classes()