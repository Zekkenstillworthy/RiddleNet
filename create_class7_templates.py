#!/usr/bin/env python3
"""
Quick script to generate templates for class 7 to fix routing issue
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the template generator
from admin.controllers.template_generator import ClassTemplateGenerator

def main():
    print("Creating templates for Class 7...")
    
    # Initialize the generator
    generator = ClassTemplateGenerator()
    
    # Generate both networking 1 and networking 2 templates for class 7
    class_id = 7
    
    print("Generating Networking 1 template...")
    result1 = generator.generate_class_template(class_id, 'networking1')
    if result1['success']:
        print(f"✓ Networking 1 template created: {result1['template_path']}")
    else:
        print(f"✗ Error creating Networking 1 template: {result1['error']}")
    
    print("Generating Networking 2 template...")
    result2 = generator.generate_class_template(class_id, 'networking2')
    if result2['success']:
        print(f"✓ Networking 2 template created: {result2['template_path']}")
    else:
        print(f"✗ Error creating Networking 2 template: {result2['error']}")
    
    print("\nDone! You should now be able to access:")
    print(f"http://127.0.0.1:5001/class/{class_id}/learning")

if __name__ == "__main__":
    main()
