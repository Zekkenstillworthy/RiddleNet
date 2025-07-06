#!/usr/bin/env python3
"""
Generate a sample class template to show where HTML files are created
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from admin.services.enhanced_class_template_generator import enhanced_template_generator

def create_sample_html():
    """Generate a sample HTML file to show where it gets created"""
    print("📝 Generating Sample Class HTML")
    print("=" * 40)
    
    # Create Flask app
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    db = SQLAlchemy(app)
    
    with app.app_context():
        # Initialize directories
        enhanced_template_generator._ensure_app_context_directories()
        
        # Create a mock class
        class MockClass:
            def __init__(self):
                self.id = 999
                self.name = "Sample Introduction to Networking"
                self.code = "SAMPLE101"
                self.section = "Demo"
                self.description = "This is a sample class to demonstrate HTML generation"
                self.question_groups = []
        
        sample_class = MockClass()
        
        print(f"Creating sample class: {sample_class.name}")
        print(f"Class ID: {sample_class.id}")
        print(f"Class Code: {sample_class.code}")
        
        # Generate the template
        try:
            template_filename = enhanced_template_generator.generate_class_template(sample_class)
            template_path = os.path.join(enhanced_template_generator.templates_dir, template_filename)
            
            print(f"\n✅ Sample HTML generated successfully!")
            print(f"📁 Location: {template_path}")
            print(f"📄 Filename: {template_filename}")
            
            # Show file size
            if os.path.exists(template_path):
                file_size = os.path.getsize(template_path)
                print(f"📊 File size: {file_size:,} bytes")
                
                # Show first few lines
                print(f"\n📖 First few lines of the generated HTML:")
                print("-" * 50)
                with open(template_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:10]
                    for i, line in enumerate(lines, 1):
                        print(f"{i:2}: {line.rstrip()}")
                print("-" * 50)
            
            # Also generate routes
            routes_filename = enhanced_template_generator.generate_class_routes(sample_class)
            routes_path = os.path.join(enhanced_template_generator.routes_dir, routes_filename)
            
            print(f"\n✅ Sample routes generated!")
            print(f"📁 Location: {routes_path}")
            print(f"📄 Filename: {routes_filename}")
            
            return template_path, routes_path
            
        except Exception as e:
            print(f"❌ Error generating sample: {e}")
            return None, None

if __name__ == "__main__":
    template_path, routes_path = create_sample_html()
    
    if template_path and routes_path:
        print(f"\n🎉 Sample files created successfully!")
        print(f"\n📂 HTML Templates Location:")
        print(f"   {os.path.dirname(template_path)}")
        print(f"\n📂 Routes Location:")
        print(f"   {os.path.dirname(routes_path)}")
        print(f"\n💡 When you create real classes through /admin/classes,")
        print(f"   the HTML files will appear in these same directories!")
    else:
        print(f"\n❌ Failed to create sample files")
    
    sys.exit(0)
