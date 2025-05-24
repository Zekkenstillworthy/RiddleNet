# filepath: c:\Users\gilbe\Documents\Flask_Main_Official_2 - Copy\user\models\troubleshooting_progress.py
from datetime import datetime
from __init__ import db
from admin.models.troubleshooting_progress import TroubleshootingProgress

# Re-export the TroubleshootingProgress model for use in the user side
# This allows for sharing the same model between admin and user modules