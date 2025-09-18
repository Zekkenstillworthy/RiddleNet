#!/usr/bin/env python3
"""
Verify that simulation assignments have been successfully removed from Class 9 (Networking 2)
"""

import eventlet
eventlet.monkey_patch()

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from __init__ import create_app, db
from admin.models.simulation_assignment import SimulationAssignment
from admin.models.class_model import Class

def verify_cleanup():
    """Verify that Class 9 simulations have been properly removed"""
    app = create_app()
    
    with app.app_context():
        try:
            # Get class 9 info
            class_9 = Class.query.get(9)
            print(f"🔍 Verifying cleanup for: {class_9.name} (Class ID: {class_9.id})")
            print("=" * 60)
            
            # Check simulation assignments
            all_assignments = SimulationAssignment.query.filter_by(class_id=9).all()
            active_assignments = [a for a in all_assignments if a.is_active]
            available_assignments = [a for a in all_assignments if a.is_available]
            published_assignments = [a for a in all_assignments if a.is_published]
            
            print(f"📊 Assignment Status Summary:")
            print(f"   Total assignments: {len(all_assignments)}")
            print(f"   Active assignments: {len(active_assignments)}")
            print(f"   Available assignments: {len(available_assignments)}")
            print(f"   Published assignments: {len(published_assignments)}")
            
            # Check each assignment in detail
            if all_assignments:
                print(f"\n📋 Detailed Assignment Status:")
                for i, assignment in enumerate(all_assignments, 1):
                    status_icon = "🟢" if assignment.is_active else "🔴"
                    available_icon = "🟢" if assignment.is_available else "🔴"
                    print(f"  {i}. {assignment.title}")
                    print(f"     Active: {status_icon} {assignment.is_active}")
                    print(f"     Available: {available_icon} {assignment.is_available}")
                    print(f"     Published: {'Yes' if assignment.is_published else 'No'}")
            
            # Final assessment
            print(f"\n🎯 Cleanup Verification Results:")
            if len(active_assignments) == 0 and len(available_assignments) == 0:
                print("✅ SUCCESS: All simulation assignments have been deactivated")
                print("✅ No simulations will appear on Networking 2 module pages")
                print("✅ The issue 'Why does Networking 2 have available simulations?' has been resolved")
                return True
            else:
                print(f"❌ INCOMPLETE: {len(available_assignments)} assignments are still available")
                print("⚠️  Some simulations may still appear on module pages")
                return False
                
        except Exception as e:
            print(f"❌ Error during verification: {e}")
            return False

if __name__ == "__main__":
    print("🔍 Class 9 Simulation Cleanup Verification")
    print("=" * 60)
    
    success = verify_cleanup()
    
    print(f"\n{'='*60}")
    if success:
        print("🎉 VERIFICATION PASSED: Cleanup was successful!")
        print("📝 Summary: Networking 2 no longer has available simulations")
    else:
        print("❌ VERIFICATION FAILED: Cleanup needs attention")
        print("🔧 Please review the assignment status above")