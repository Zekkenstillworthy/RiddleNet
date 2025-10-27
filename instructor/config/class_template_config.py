"""
Class Template Configuration

This configuration controls how class templates are generated and which system is used.
"""

# UNIVERSAL TEMPLATE SYSTEM CONFIGURATION
# Set to True to use only the universal template for all classes
USE_UNIVERSAL_TEMPLATE_ONLY = True

# LEGACY TEMPLATE GENERATION
# Set to True to generate class-specific templates (old behavior)
GENERATE_CLASS_SPECIFIC_TEMPLATES = False

# UNIVERSAL TEMPLATE SETTINGS
UNIVERSAL_TEMPLATE_PATH = "user/dynamic_class_universal.html"
UNIVERSAL_ROUTE_BLUEPRINT = "universal_class"

# CONFIGURATION EXPLANATION
CONFIG_INFO = {
    "universal_template_mode": USE_UNIVERSAL_TEMPLATE_ONLY,
    "description": "When universal template mode is enabled, all classes use the same dynamic template that adapts based on database content",
    "benefits": [
        "Single template to maintain",
        "Automatic adaptation to class content",
        "No need to regenerate templates",
        "Consistent user experience",
        "Database-driven content"
    ],
    "template_file": UNIVERSAL_TEMPLATE_PATH,
    "route_handling": "All classes use /class/<id> handled by universal_class_routes.py"
}

def get_template_config():
    """Get the current template configuration"""
    return {
        "use_universal_only": USE_UNIVERSAL_TEMPLATE_ONLY,
        "generate_specific": GENERATE_CLASS_SPECIFIC_TEMPLATES,
        "universal_template": UNIVERSAL_TEMPLATE_PATH,
        "config_info": CONFIG_INFO
    }

def should_use_universal_template():
    """Check if new classes should use the universal template"""
    return USE_UNIVERSAL_TEMPLATE_ONLY

def should_generate_class_specific_template():
    """Check if class-specific templates should be generated"""
    return GENERATE_CLASS_SPECIFIC_TEMPLATES and not USE_UNIVERSAL_TEMPLATE_ONLY
