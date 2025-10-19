"""
Safe template rendering utilities
"""
import os
from flask import render_template as flask_render_template, current_app
from utils.template_utils import debug_template_paths

def render_safe_template(template_name, **context):
    """
    Safely render a template with debug information if template is not found
    
    This function helps debug template rendering issues by providing detailed
    information about template search paths when a template is not found.
    """
    # Add debug information about template lookup
    app = current_app
    
    # Check if template exists in expected locations
    print(f"\nRendering template: {template_name}")
    
    # Debug the template paths
    debug_template_paths(template_name)
    
    # Now try to render the template
    try:
        return flask_render_template(template_name, **context)
    except Exception as e:
        print(f"ERROR rendering template {template_name}: {str(e)}")
        
        # Special handling for admin templates
        if template_name.startswith('instructor/'):
            try:
                # Try extracting just the filename without the instructor/ prefix
                base_name = os.path.basename(template_name)
                print(f"Trying alternate template name: {base_name}")
                return flask_render_template(base_name, **context)
            except Exception as e2:
                print(f"Also failed with alternate name: {str(e2)}")
                
        # Return error template or raise the exception
        raise e
