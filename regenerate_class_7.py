#!/usr/bin/env python3
"""
Regenerate Class 7 route file using the enhanced template generator
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from run import app
from admin.models.class_model import Class
from admin.services.enhanced_class_template_generator import EnhancedClassTemplateGenerator

def regenerate_class_7():
    """Regenerate the missing route file for Class 7"""
    
    with app.app_context():
        # Get Class 7 from database
        class_7 = Class.query.get(7)
        
        if not class_7:
            print("❌ Class 7 not found in database!")
            return False
        
        print(f"📝 Found Class 7: {class_7.name} ({class_7.code})")
        
        # Initialize enhanced template generator
        generator = EnhancedClassTemplateGenerator()
        
        try:
            # Generate all class resources
            print("🔄 Regenerating class resources...")
            result = generator.generate_all_class_resources(class_7.id)
            
            print("✅ Successfully regenerated Class 7 resources!")
            print(f"   - Template: {result['template']}")
            print(f"   - Routes: {result['routes']}")
            
            # Verify the route file was created
            routes_path = os.path.join(project_root, "user", "routes", "generated", result['routes'])
            if os.path.exists(routes_path):
                print(f"✅ Route file created: {routes_path}")
                return True
            else:
                print(f"❌ Route file not found: {routes_path}")
                return False
                
        except Exception as e:
            print(f"❌ Error regenerating Class 7: {str(e)}")
            return False

if __name__ == "__main__":
    print("🔄 Regenerating Class 7 Resources")
    print("=" * 40)
    
    success = regenerate_class_7()
    
    if success:
        print("\n🎉 Class 7 regeneration complete!")
        print("The server should now be able to register the route for Class 7.")
    else:
        print("\n❌ Class 7 regeneration failed!")
        print("Please check the error messages above.")
