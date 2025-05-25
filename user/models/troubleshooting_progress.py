# User-side entry point for troubleshooting progress
# This file avoids circular imports by not importing anything directly
from __init__ import db

# Define a function to get the model when needed
def get_troubleshooting_progress_model():
    """
    Get the TroubleshootingProgress model lazily to avoid circular imports
    """
    from admin.models.troubleshooting_progress import TroubleshootingProgress
    return TroubleshootingProgress
# This allows for sharing the same model between admin and user modules