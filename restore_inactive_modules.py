"""
Restore Inactive Modules Script
This script reactivates modules that were accidentally marked as inactive (is_active=False)
"""

from application import create_app
from __init__ import db
from instructor.models.module import Module
from datetime import datetime

app = create_app()

def restore_inactive_modules(class_id=None):
    """
    Restore modules that are marked as inactive
    
    Args:
        class_id: If provided, only restore modules for this class. Otherwise restore all.
    """ 
    with app.app_context():
        print("=" * 60)
        print("RESTORE INACTIVE MODULES")
        print("=" * 60)
        
        # Find inactive modules
        if class_id:
            inactive_modules = Module.query.filter_by(
                class_id=class_id,
                is_active=False
            ).all()
            print(f"\nSearching for inactive modules in class {class_id}...")
        else:
            inactive_modules = Module.query.filter_by(
                is_active=False
            ).all()
            print(f"\nSearching for ALL inactive modules...")
        
        if not inactive_modules:
            print("✅ No inactive modules found. All modules are active!")
            return
        
        print(f"\n🔍 Found {len(inactive_modules)} inactive modules:")
        print("-" * 60)
        
        for module in inactive_modules:
            print(f"\nModule ID: {module.id}")
            print(f"  Title: {module.title}")
            print(f"  Class ID: {module.class_id}")
            print(f"  Created: {module.created_at}")
            print(f"  Updated: {module.updated_at}")
        
        print("\n" + "=" * 60)
        response = input("\n⚠️  Do you want to RESTORE all these modules? (yes/no): ").strip().lower()
        
        if response != 'yes':
            print("\n❌ Restoration cancelled. No changes made.")
            return
        
        # Restore the modules
        restored_count = 0
        for module in inactive_modules:
            module.is_active = True
            module.updated_at = datetime.utcnow()
            restored_count += 1
            print(f"✅ Restored: {module.title} (ID: {module.id})")
        
        # Commit all changes
        try:
            db.session.commit()
            print(f"\n{'=' * 60}")
            print(f"✅ SUCCESS! Restored {restored_count} modules")
            print(f"{'=' * 60}")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR: Failed to restore modules")
            print(f"Error: {str(e)}")
            raise

def show_all_modules_status(class_id=None):
    """Show status of all modules"""
    with app.app_context():
        print("\n" + "=" * 60)
        print("ALL MODULES STATUS")
        print("=" * 60)
        
        if class_id:
            modules = Module.query.filter_by(class_id=class_id).all()
            print(f"\nShowing modules for class {class_id}:")
        else:
            modules = Module.query.all()
            print(f"\nShowing ALL modules:")
        
        active_count = 0
        inactive_count = 0
        
        for module in modules:
            status = "✅ ACTIVE" if module.is_active else "❌ INACTIVE"
            print(f"\n{status}")
            print(f"  ID: {module.id} | Class: {module.class_id}")
            print(f"  Title: {module.title}")
            
            if module.is_active:
                active_count += 1
            else:
                inactive_count += 1
        
        print(f"\n{'=' * 60}")
        print(f"Total: {len(modules)} modules")
        print(f"Active: {active_count} ✅")
        print(f"Inactive: {inactive_count} ❌")
        print(f"{'=' * 60}")

if __name__ == "__main__":
    import sys
    
    print("\n🔧 Module Restoration Tool")
    print("This tool helps restore modules that were accidentally deactivated\n")
    
    # Check if class_id was provided as argument
    class_id = None
    if len(sys.argv) > 1:
        try:
            class_id = int(sys.argv[1])
            print(f"📌 Focusing on class ID: {class_id}\n")
        except ValueError:
            print("⚠️  Invalid class_id provided. Showing all classes.\n")
    
    # Show current status
    show_all_modules_status(class_id)
    
    # Offer to restore
    print("\n" + "=" * 60)
    choice = input("\nWould you like to restore inactive modules? (yes/no): ").strip().lower()
    
    if choice == 'yes':
        restore_inactive_modules(class_id)
        print("\n")
        show_all_modules_status(class_id)
    else:
        print("\n✋ No changes made. Exiting.")
