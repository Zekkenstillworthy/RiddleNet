#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import the main Flask app factory
    from __init__ import create_app
    from admin.controllers.troubleshooting_controller import TroubleshootingController
    
    print("Creating Flask app...")
    app = create_app()
    
    with app.app_context():
        print("Testing list_troubleshootings method...")
        controller = TroubleshootingController()
        result = controller.list_troubleshootings()
        if not result[0]:
            print("No troubleshooting data returned.")
        print('Success!')
        print('Status Code:', result[1])
        print('Response:', result[0].get_json() if (result[0] and hasattr(result[0], 'get_json')) else str(result[0]))
        
except Exception as e:
    print('Error:', e)
    import traceback
    traceback.print_exc()
