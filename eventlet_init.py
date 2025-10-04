"""
Eventlet Initialization Module
===============================
This module MUST be imported first, before any other modules.
It sets up eventlet monkey patching to ensure compatibility with SQLAlchemy and Flask.
"""
import warnings

# Suppress warnings before any other imports
warnings.filterwarnings('ignore', message='.*monkey_patch.*')
warnings.filterwarnings('ignore', message='.*Working outside of.*context.*')
warnings.filterwarnings('ignore', message='.*Working outside of.*request.*')
warnings.filterwarnings('ignore', message='.*RLock.*')

# Import and patch IMMEDIATELY
import eventlet

# Apply monkey patching with only commonly supported parameters
# Note: 'ssl' parameter is not supported in all eventlet versions
eventlet.monkey_patch(
    socket=True,
    select=True,
    time=True,
    thread=True,  # Required for SQLAlchemy threading.Lock compatibility
    os=True
)

print("✓ Eventlet monkey patching completed successfully")
