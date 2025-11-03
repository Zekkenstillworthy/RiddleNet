"""
Quick Restore - Restore inactive modules without prompts
"""

from application import create_app
from __init__ import db
from instructor.models.module import Module
from datetime import datetime
import sys

app = create_app()

def restore_modules(class_id=None):
    """Restore all inactive modules"""
    with app.app_context():
        print("=" * 60)
        print("RESTORING INACTIVE MODULES")
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
            print("\n✅ No inactive modules found. All modules are already active!")
            return
        
        print(f"\n🔍 Found {len(inactive_modules)} inactive modules:")
        print("-" * 60)
        
        restored_count = 0
        for module in inactive_modules:
            print(f"\nRestoring:")
            print(f"  Module ID: {module.id}")
            print(f"  Title: {module.title}")
            print(f"  Class ID: {module.class_id}")
            
            # Restore it
            module.is_active = True
            module.updated_at = datetime.utcnow()
            restored_count += 1
            print(f"  ✅ RESTORED")
        
        # Commit all changes
        try:
            db.session.commit()
            print(f"\n{'=' * 60}")
            print(f"✅ SUCCESS! Restored {restored_count} modules")
            print(f"{'=' * 60}")
            print("\n📌 Your modules are now visible again!")
            print("💡 Refresh your browser to see them.")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR: Failed to restore modules")
            print(f"Error: {str(e)}")
            raise

if __name__ == "__main__":
    class_id = None
    if len(sys.argv) > 1:
        try:
            class_id = int(sys.argv[1])
        except ValueError:
            pass
    
    restore_modules(class_id)
