from flask import Flask
from flask_login import LoginManager
import os
import sys

# Add parent directory to path so we can import from main app
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import db from main app to use a single SQLAlchemy instance
from __init__ import db, login_manager

# This module now just provides shared database and login manager instances
# The admin app creation is handled by admin.app.AdminApp class

