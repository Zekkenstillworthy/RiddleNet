#!/usr/bin/env python3
"""
Remove unwanted simulation assignments from Class 9 (Networking 2)
This script will deactivate all simulation assignments for Class 9 to prevent
simulations from appearing on Networking 2 module pages.
"""

import eventlet
eventlet.monkey_patch()

import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from __init__ import create_app, db
from admin.models.simulation_assignment import SimulationAssignment
from admin.models.class_model import Class

def remove_class_9_simulation_assignments():
    """Remove simulation assignments from Class 9 (Networking 2)"""
    app = create_app()
    
    with app.app_context():
        try:
            # Get class 9 info
            class_9 = Class.query.get(9)
            if not class_9:
                print("❌ Class 9 not found!")
                return
                
            print(f"🎯 Target: {class_9.name} (Class ID: {class_9.id})")
            print("=" * 60)
            
            # Get all simulation assignments for class 9
            assignments = SimulationAssignment.query.filter_by(class_id=9).all()
            print(f"📊 Found {len(assignments)} simulation assignments for Class 9")
            
            if not assignments:
                print("✅ No simulation assignments found to remove")
                return
            
            # Show current status
            print(f"\n📋 Current Assignments:")
            for i, assignment in enumerate(assignments, 1):
                status = "🟢 ACTIVE" if assignment.is_active else "🔴 INACTIVE"
                available = "🟢 AVAILABLE" if assignment.is_available else "🔴 NOT AVAILABLE"
                print(f"  {i}. {assignment.title}")
                print(f"     Simulation: {assignment.simulation.title if assignment.simulation else 'None'}")
                print(f"     Status: {status} | {available}")
                print(f"     Published: {'Yes' if assignment.is_published else 'No'}")
            
            # Ask for confirmation
            print(f"\n⚠️  WARNING: This will deactivate ALL {len(assignments)} simulation assignments for Networking 2")
            print("   This will prevent simulations from appearing on Networking 2 module pages.")
            
            confirm = input("\n🤔 Do you want to proceed? (y/N): ").strip().lower()
            if confirm not in ['y', 'yes']:
                print("❌ Operation cancelled")
                return
            
            # Deactivate all assignments
            deactivated_count = 0
            for assignment in assignments:
                if assignment.is_active:
                    assignment.is_active = False
                    assignment.updated_at = datetime.utcnow()
                    deactivated_count += 1
                    print(f"🔄 Deactivated: {assignment.title}")
            
            # Commit changes
            if deactivated_count > 0:
                db.session.commit()
                print(f"✅ Successfully deactivated {deactivated_count} simulation assignments")
                print(f"📝 Database updated at {datetime.utcnow()}")
            else:
                print("ℹ️  All assignments were already inactive")
            
            # Verify the changes
            print(f"\n🔍 Verification:")
            updated_assignments = SimulationAssignment.query.filter_by(class_id=9).all()
            active_count = sum(1 for a in updated_assignments if a.is_active)
            available_count = sum(1 for a in updated_assignments if a.is_available)
            
            print(f"   Active assignments: {active_count}")
            print(f"   Available assignments: {available_count}")
            
            if active_count == 0 and available_count == 0:
                print("✅ SUCCESS: No simulations will now appear on Networking 2 pages")
            else:
                print(f"⚠️  WARNING: {available_count} assignments are still available")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

def show_status_only():
    """Show current status without making changes"""
    app = create_app()
    
    with app.app_context():
        try:
            class_9 = Class.query.get(9)
            if not class_9:
                print("❌ Class 9 not found!")
                return
                
            assignments = SimulationAssignment.query.filter_by(class_id=9).all()
            active_assignments = [a for a in assignments if a.is_active]
            available_assignments = [a for a in assignments if a.is_available]
            
            print(f"📊 Class 9 ({class_9.name}) Simulation Status:")
            print(f"   Total assignments: {len(assignments)}")
            print(f"   Active assignments: {len(active_assignments)}")
            print(f"   Available assignments: {len(available_assignments)}")
            
            if available_assignments:
                print(f"\n🔍 Available simulations:")
                for assignment in available_assignments:
                    print(f"   • {assignment.title}: {assignment.simulation.title if assignment.simulation else 'Unknown'}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Class 9 Simulation Assignment Cleanup Tool")
    print("=" * 60)
    
    # Show current status first
    show_status_only()
    
    print(f"\n{'='*60}")
    choice = input("Do you want to proceed with cleanup? (y/N): ").strip().lower()
    
    if choice in ['y', 'yes']:
        remove_class_9_simulation_assignments()
    else:
        print("ℹ️  Status check only - no changes made")