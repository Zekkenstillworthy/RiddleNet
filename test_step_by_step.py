#!/usr/bin/env python3
import sys
sys.path.append('.')

print("Testing imports step by step...")

try:
    print("1. Importing db...")
    from __init__ import db
    print("   ✅ SUCCESS: db imported")
    
    print("2. Importing user.models (should not trigger immediate imports)...")
    import user.models
    print("   ✅ SUCCESS: user.models imported")
    
    print("3. Testing lazy User import...")
    User = user.models.User
    print(f"   ✅ SUCCESS: User = {User}")
    
    print("4. Testing socket_events import...")
    import socket_events
    print("   ✅ SUCCESS: socket_events imported")
    
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\nTest complete!")
