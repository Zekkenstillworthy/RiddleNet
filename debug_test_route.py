#!/usr/bin/env python3
"""
Test route to verify our debug logging is working without authentication
"""

from flask import Blueprint, render_template
import os
from datetime import datetime

# Create test blueprint
test_bp = Blueprint('debug_test', __name__)

@test_bp.route('/debug-topology-test')
def test_topology_debug():
    """Test route to verify debug logging works"""
    
    # Debug logging test
    debug_file_path = r'c:\Users\gilbe\OneDrive\Desktop\RiddleNet\debug_test.txt'
    try:
        debug_msg = "DEBUG TEST: Route was accessed successfully!\n"
        debug_msg += f"DEBUG TEST: Time = {datetime.now().isoformat()}\n"
        debug_msg += "DEBUG TEST: This confirms our debug logging mechanism works\n"
        
        print("TEST ROUTE DEBUG:")
        print(debug_msg)
        print("=" * 80)
        
        # Write to file
        with open(debug_file_path, 'w', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()}: TEST ROUTE\n")
            f.write(debug_msg + "\n")
            f.write("=" * 50 + "\n")
            
    except Exception as e:
        error_msg = f"DEBUG TEST: Error logging: {e}"
        print("TEST ROUTE ERROR:")
        print(error_msg)
        try:
            with open(debug_file_path, 'w', encoding='utf-8') as f:
                f.write(f"{datetime.now().isoformat()}: TEST ERROR: {error_msg}\n")
        except Exception as e2:
            print(f"Could not write error to file: {e2}")
    
    return f"<h1>Debug Test Route</h1><p>Check for debug_test.txt file and console output</p><p>Time: {datetime.now()}</p>"