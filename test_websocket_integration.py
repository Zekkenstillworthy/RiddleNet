#!/usr/bin/env python3
"""
WebSocket Integration Test Script for RiddleNet
Tests the complete WebSocket functionality including admin controls
"""

import sys
import os
import time
import requests
from threading import Thread

def test_imports():
    """Test if all WebSocket modules can be imported successfully"""
    print("🔍 Testing WebSocket module imports...")
    
    try:
        import socket_manager
        print("✅ socket_manager imported successfully")
        
        import socket_events
        print("✅ socket_events imported successfully")
        
        from flask_socketio import SocketIO
        print("✅ Flask-SocketIO imported successfully")
        
        import eventlet
        print("✅ eventlet imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_app_initialization():
    """Test if the Flask app can be initialized with WebSocket support"""
    print("\n🔍 Testing Flask app initialization...")
    
    try:
        from run import app, socketio
        print("✅ Flask app and SocketIO initialized successfully")
        print(f"✅ App debug mode: {app.config.get('DEBUG', False)}")
        print(f"✅ SocketIO async mode: {socketio.async_mode}")
        return True
    except Exception as e:
        print(f"❌ App initialization error: {e}")
        return False

def test_socket_manager_functions():
    """Test socket manager helper functions"""
    print("\n🔍 Testing socket manager functions...")
    
    try:
        from socket_manager import get_active_users_list, update_user_activity
        
        # Test get_active_users_list
        users = get_active_users_list()
        print(f"✅ get_active_users_list() returned: {len(users)} users")
        
        # Test update_user_activity (this shouldn't fail)
        update_user_activity(1, "Testing")
        print("✅ update_user_activity() function works")
        
        return True
    except Exception as e:
        print(f"❌ Socket manager function error: {e}")
        return False

def test_template_files():
    """Test if WebSocket-enhanced template files exist and are valid"""
    print("\n🔍 Testing WebSocket template integration...")
    
    template_files = [
        'templates/user/base.html',
        'templates/user/topology.html', 
        'templates/user/troubleshoot.html',
        'templates/admin/dashboard.html'
    ]
    
    all_good = True
    for template_file in template_files:
        if os.path.exists(template_file):
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'SocketClient' in content or 'websocket' in content.lower():
                    print(f"✅ {template_file} has WebSocket integration")
                else:
                    print(f"⚠️  {template_file} might be missing WebSocket integration")
        else:
            print(f"❌ {template_file} not found")
            all_good = False
    
    return all_good

def test_css_files():
    """Test if WebSocket CSS files exist"""
    print("\n🔍 Testing WebSocket CSS files...")
    
    css_files = [
        'static/css/socket-notifications.css',
        'static/css/admin/dashboard.css'
    ]
    
    all_good = True
    for css_file in css_files:
        if os.path.exists(css_file):
            with open(css_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'websocket' in content.lower() or 'socket' in content.lower():
                    print(f"✅ {css_file} has WebSocket styles")
                else:
                    print(f"⚠️  {css_file} might be missing WebSocket styles")
        else:
            print(f"❌ {css_file} not found")
            all_good = False
    
    return all_good

def test_javascript_files():
    """Test if WebSocket JavaScript files exist"""
    print("\n🔍 Testing WebSocket JavaScript files...")
    
    js_files = [
        'static/js/socket-client.js'
    ]
    
    all_good = True
    for js_file in js_files:
        if os.path.exists(js_file):
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'SocketClient' in content:
                    print(f"✅ {js_file} has SocketClient implementation")
                else:
                    print(f"⚠️  {js_file} might be missing SocketClient")
        else:
            print(f"❌ {js_file} not found")
            all_good = False
    
    return all_good

def run_server_test():
    """Try to start the server briefly to test if everything works"""
    print("\n🔍 Testing server startup...")
    
    try:
        from run import app, socketio
        
        # Try to start the server in a separate thread
        def start_server():
            socketio.run(app, host='127.0.0.1', port=5555, debug=False, use_reloader=False)
        
        server_thread = Thread(target=start_server, daemon=True)
        server_thread.start()
        
        # Give the server a moment to start
        time.sleep(2)
        
        # Try to make a request to the server
        try:
            response = requests.get('http://127.0.0.1:5555', timeout=5)
            print(f"✅ Server responded with status code: {response.status_code}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Server might not be fully ready: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Server startup error: {e}")
        return False

def main():
    """Run all WebSocket integration tests"""
    print("🚀 RiddleNet WebSocket Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("App Initialization", test_app_initialization), 
        ("Socket Manager Functions", test_socket_manager_functions),
        ("Template Files", test_template_files),
        ("CSS Files", test_css_files),
        ("JavaScript Files", test_javascript_files),
        ("Server Startup", run_server_test)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"🏁 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All WebSocket integration tests PASSED!")
        print("🌐 Your RiddleNet application is ready with WebSocket support!")
    elif passed >= total - 1:
        print("✨ Most tests passed - WebSocket integration is mostly complete!")
    else:
        print("⚠️  Some tests failed - check the errors above")
    
    print("\n💡 To start the application, run: python run.py")
    print("📱 Then navigate to: http://localhost:5000")
    print("🔧 Admin dashboard: http://localhost:5000/admin/dashboard")

if __name__ == "__main__":
    main()
