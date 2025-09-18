#!/usr/bin/env python3
"""
Automatically remove all simulation assignments from Class 9 (Networking 2)
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

def cleanup_class_9_simulations():
    """Remove all simulation assignments from Class 9 (Networking 2)"""
    app = create_app()
    
    with app.app_context():
        try:
            # Get class 9 info
            class_9 = Class.query.get(9)
            if not class_9:
                print("❌ Class 9 not found!")
                return False
                
            print(f"🎯 Target: {class_9.name} (Class ID: {class_9.id})")
            print("=" * 60)
            
            # Get all simulation assignments for class 9
            assignments = SimulationAssignment.query.filter_by(class_id=9).all()
            print(f"📊 Found {len(assignments)} simulation assignments for Class 9")
            
            if not assignments:
                print("✅ No simulation assignments found to remove")
                return True
            
            # Show current status
            print(f"\n📋 Current Assignments:")
            active_count = 0
            for i, assignment in enumerate(assignments, 1):
                status = "🟢 ACTIVE" if assignment.is_active else "🔴 INACTIVE"
                available = "🟢 AVAILABLE" if assignment.is_available else "🔴 NOT AVAILABLE"
                print(f"  {i}. {assignment.title}")
                print(f"     Simulation: {assignment.simulation.title if assignment.simulation else 'None'}")
                print(f"     Status: {status} | {available}")
                print(f"     Published: {'Yes' if assignment.is_published else 'No'}")
                if assignment.is_active:
                    active_count += 1
            
            print(f"\n🔄 Processing {len(assignments)} assignments...")
            
            # Deactivate all assignments
            deactivated_count = 0
            for assignment in assignments:
                if assignment.is_active:
                    assignment.is_active = False
                    assignment.updated_at = datetime.utcnow()
                    deactivated_count += 1
                    print(f"   ✅ Deactivated: {assignment.title}")
                else:
                    print(f"   ⚪ Already inactive: {assignment.title}")
            
            # Commit changes
            if deactivated_count > 0:
                db.session.commit()
                print(f"\n✅ Successfully deactivated {deactivated_count} simulation assignments")
                print(f"📝 Database updated at {datetime.utcnow()}")
            else:
                print(f"\nℹ️  All {len(assignments)} assignments were already inactive")
            
            # Verify the changes
            print(f"\n🔍 Verification:")
            updated_assignments = SimulationAssignment.query.filter_by(class_id=9).all()
            final_active_count = sum(1 for a in updated_assignments if a.is_active)
            final_available_count = sum(1 for a in updated_assignments if a.is_available)
            
            print(f"   Total assignments: {len(updated_assignments)}")
            print(f"   Active assignments: {final_active_count}")
            print(f"   Available assignments: {final_available_count}")
            
            if final_active_count == 0 and final_available_count == 0:
                print("\n🎉 SUCCESS: No simulations will now appear on Networking 2 pages!")
                return True
            else:
                print(f"\n⚠️  WARNING: {final_available_count} assignments are still available")
                return False
                
        except Exception as e:
            print(f"\n❌ Error during cleanup: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("🚀 Automatic Class 9 Simulation Assignment Cleanup")
    print("=" * 60)
    
    success = cleanup_class_9_simulations()
    
    if success:
        print(f"\n✅ Cleanup completed successfully!")
        print("📋 Networking 2 class pages will no longer show simulation buttons")
    else:
        print(f"\n❌ Cleanup failed or incomplete")
        print("🔧 Please check the errors above and try again")