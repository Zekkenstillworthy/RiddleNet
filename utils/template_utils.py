"""
Utility functions for template handling and debugging
"""
import os
from flask import render_template as flask_render_template, current_app
import jinja2
from jinja2 import FileSystemLoader, ChoiceLoader

def debug_template_paths(template_name):
    """
    Debug helper to print all paths being searched for a template
    """
    app = current_app
    if not app:
        print("No current Flask application context")
        return False
        
    print(f"\nDEBUG: Looking for template: {template_name}")
    print(f"Current app template folder: {app.template_folder}")
    
    search_paths = []
    if hasattr(app.jinja_loader, 'searchpath'):
        search_paths.extend(app.jinja_loader.searchpath)
    elif hasattr(app.jinja_loader, 'loaders'):
        # Handle ChoiceLoader
        for loader in app.jinja_loader.loaders:
            if hasattr(loader, 'searchpath'):
                search_paths.extend(loader.searchpath)
    
    print(f"Search paths: {search_paths}")
    
    # Check each path to see if the template exists
    for path in search_paths:
        full_path = os.path.join(path, template_name)
        exists = os.path.exists(full_path)
        print(f"Checking: {full_path} -> {'EXISTS' if exists else 'NOT FOUND'}")
    
    # Try loading the template explicitly
    try:
        template = app.jinja_env.get_template(template_name)
        print(f"Template found at: {template.filename}")
        return True
    except jinja2.exceptions.TemplateNotFound:
        print(f"Template not found: {template_name}")
        return False

def check_template_exists(template_name):
    """
    Check if a template exists in any of the template search paths
    """
    app = current_app
    if not app:
        return False
        
    try:
        app.jinja_env.get_template(template_name)
        return True
    except jinja2.exceptions.TemplateNotFound:
        return False

def ensure_blueprint_can_find_templates(blueprint, template_folders):
    """
    Ensure a blueprint can find templates in the specified folders
    """
    if not hasattr(blueprint, 'jinja_loader'):
        print(f"Blueprint {blueprint.name} has no jinja_loader")
        return
    
    # Check if we're dealing with a FileSystemLoader
    if hasattr(blueprint.jinja_loader, 'searchpath'):
        # Add each folder to the searchpath if it's not already there
        for folder in template_folders:
            if os.path.exists(folder):
                if folder not in blueprint.jinja_loader.searchpath:
                    blueprint.jinja_loader.searchpath.append(folder)
                    print(f"Added {folder} to blueprint {blueprint.name}'s template search paths")
            else:
                print(f"Warning: Template folder does not exist: {folder}")
    else:
        # For other types of loaders, create a new ChoiceLoader
        from jinja2 import FileSystemLoader, ChoiceLoader
        loaders = [blueprint.jinja_loader]  # Keep the original loader
        
        # Add a FileSystemLoader for each template folder
        for folder in template_folders:
            if os.path.exists(folder):
                loaders.append(FileSystemLoader(folder))
                print(f"Added {folder} to blueprint {blueprint.name}'s loaders")
            else:
                print(f"Warning: Template folder does not exist: {folder}")
        
        # Set the new loader if we have more than one
        if len(loaders) > 1:
            blueprint.jinja_loader = ChoiceLoader(loaders)
            print(f"Created ChoiceLoader for blueprint {blueprint.name}")
