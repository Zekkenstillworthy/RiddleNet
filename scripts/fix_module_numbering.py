"""
Fix Module Numbering Script
Renumbers all modules in all classes to ensure sequential ordering
"""

import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from application import create_app
from instructor.models.module import Module
from instructor.models.class_model import Class
from __init__ import db

def fix_module_numbering():
    """Fix module numbering for all classes"""
    app = create_app()
    
    with app.app_context():
        # Get all classes
        classes = Class.query.all()
        
        print(f"[FIX] Fixing module numbering for {len(classes)} classes...\n")
        
        total_modules_fixed = 0
        
        for class_obj in classes:
            print(f"📚 Processing class: {class_obj.name} (ID: {class_obj.id})")
            
            # Get all active modules for this class, ordered by order_index
            modules = Module.query.filter_by(
                class_id=class_obj.id, 
                is_active=True
            ).order_by(Module.order_index.asc()).all()
            
            if not modules:
                print(f"   [WARNING]  No active modules found\n")
                continue
            
            # Show current state
            print(f"   Current module numbers and order:")
            for module in modules:
                print(f"      - Module #{module.module_number} (order_index: {module.order_index}): {module.title}")
            
            # Renumber sequentially
            changes_made = False
            for index, module in enumerate(modules, start=1):
                new_number = str(index)
                if module.module_number != new_number:
                    print(f"      ✏️  Renumbering module {module.id}: '{module.module_number}' → '{new_number}'")
                    module.module_number = new_number
                    changes_made = True
            
            if changes_made:
                db.session.commit()
                total_modules_fixed += len(modules)
                print(f"   [OK] Fixed {len(modules)} modules\n")
            else:
                print(f"   ✓  Already correctly numbered\n")
        
        print(f"\n🎉 Module numbering fix complete!")
        print(f"   Total modules renumbered: {total_modules_fixed}")

if __name__ == '__main__':
    print("=" * 60)
    print("MODULE NUMBERING FIX SCRIPT")
    print("=" * 60)
    print()
    
    fix_module_numbering()
