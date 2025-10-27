"""
Admin-specific template utilities
"""
from flask import render_template as flask_render_template, current_app
from utils.template_utils import debug_template_paths, check_template_exists
import os

def render_instructor_template(template_name, **context):
    """
    Render an admin template with debugging
    """
    # Add debugging for template paths
    debug_template_paths(template_name)
    
    # Print existing template paths
    app = current_app
    print("\nADMIN TEMPLATE DEBUG:")
    print(f"Looking for template: {template_name}")
    if hasattr(app.jinja_env, 'loader') and hasattr(app.jinja_env.loader, 'searchpath'):
        for path in app.jinja_env.loader.searchpath:
            template_path = os.path.join(path, template_name)
            exists = os.path.exists(template_path)
            print(f"Path: {template_path} -> {'EXISTS' if exists else 'NOT FOUND'}")
    
    # Actually render the template
    return flask_render_template(template_name, **context)
