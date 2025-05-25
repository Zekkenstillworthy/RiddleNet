#!/usr/bin/env python3
"""
Simple test script to check if the troubleshooting API works after migration
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_troubleshooting_api():
    """Test the troubleshooting API endpoints"""
    try:
        # Import Flask app and create app context
        from __init__ import create_app
        from admin.controllers.troubleshooting_controller import TroubleshootingController
        
        app = create_app()
        
        with app.app_context():
            print("Testing troubleshooting controller...")
            
            # Create controller instance
            controller = TroubleshootingController()
            
            # Test list_troubleshootings method
            print("Calling list_troubleshootings(1, 10, '', '')...")
            result = controller.list_troubleshootings(1, 10, '', '')
            
            print(f"Result type: {type(result)}")
            if hasattr(result, 'get_json'):
                # If it's a Flask Response object
                print(f"Status code: {result.status_code}")
                if result.status_code == 200:
                    data = result.get_json()
                    print(f"Success! Data: {data}")
                else:
                    print(f"Error response: {result.get_json()}")
            else:
                # If it's a tuple (data, status_code)
                data, status_code = result
                print(f"Status code: {status_code}")
                print(f"Data: {data}")
            
            return True
            
    except Exception as e:
        print(f"Error testing troubleshooting API: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing troubleshooting API after database migration...")
    if test_troubleshooting_api():
        print("Test completed successfully!")
    else:
        print("Test failed!")
