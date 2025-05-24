#!/usr/bin/env python3
"""
Debug script to identify import issues
"""

print("Starting debug script...")

try:
    print("1. Testing eventlet import...")
    import eventlet
    print("   ✓ Eventlet import successful")
    
    print("2. Applying eventlet monkey patch...")
    eventlet.monkey_patch()
    print("   ✓ Eventlet monkey patch successful")
    
    print("3. Testing __init__ import...")
    from __init__ import create_app
    print("   ✓ create_app import successful")
    
    print("4. Testing socketio import...")
    from socket_manager import socketio
    print("   ✓ socketio import successful")
    
    print("5. Creating app...")
    app = create_app()
    print("   ✓ App creation successful")
    
    print("6. Testing socket_events import...")
    import socket_events
    print("   ✓ socket_events import successful")
    
    print("7. All imports successful! The issue might be in the server startup.")
    
except Exception as e:
    print(f"Error at step: {e}")
    import traceback
    traceback.print_exc()
