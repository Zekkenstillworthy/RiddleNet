"""
Helper functions for admin templates rendering
"""
import os
from flask import current_app, render_template
from utils.template_utils import debug_template_paths

def render_admin_template(template_name, **context):
    """
    Render an admin template with guaranteed correct path
    """
    # Make sure template_name starts with 'admin/'
    if not template_name.startswith('admin/'):
        template_name = f'admin/{template_name}'
    
    # Debug the template lookup paths
    debug_template_paths(template_name)
    
    # Check if template exists in app's template folder
    app = current_app
    template_path = os.path.join(app.template_folder, template_name)
    if os.path.exists(template_path):
        print(f"Found admin template at: {template_path}")
    else:
        print(f"WARNING: Admin template does not exist at {template_path}")
        # Try to find in all jinja search paths
        found = False
        if hasattr(app.jinja_env, 'loader') and hasattr(app.jinja_env.loader, 'searchpath'):
            for path in app.jinja_env.loader.searchpath:
                alt_path = os.path.join(path, template_name)
                if os.path.exists(alt_path):
                    print(f"Found admin template at alternative path: {alt_path}")
                    found = True
                    break
        if not found:
            print("ERROR: Admin template cannot be found in any search path!")
    
    # Render the template with Flask's render_template
    return render_template(template_name, **context)
