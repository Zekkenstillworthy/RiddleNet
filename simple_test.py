"""Simple WebSocket validation"""
print("🚀 Testing WebSocket Integration for RiddleNet")

# Test basic imports
try:
    from socket_manager import socketio
    print("✅ SocketIO imported successfully")
except Exception as e:
    print(f"❌ SocketIO import failed: {e}")

try:
    import socket_events
    print("✅ Socket events imported successfully")
except Exception as e:
    print(f"❌ Socket events import failed: {e}")

try:
    from run import app
    print("✅ Flask app imported successfully")
except Exception as e:
    print(f"❌ Flask app import failed: {e}")

print("\n🎉 WebSocket integration validation complete!")
print("💡 To start the server: python run.py")
