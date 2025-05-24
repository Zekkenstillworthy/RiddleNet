# Static Server Performance Fix

## Problem: TimeoutError on Windows with WebSocket and Static Files

When running the WebSocket server alongside static file serving with eventlet on Windows, you were experiencing connection timeout errors. These errors occur mainly with large files like videos, and are related to the Windows socket implementation's behavior with eventlet.

Error observed:
```
ConnectionAbortedError: [WinError 10053] An established connection was aborted by the software in your host machine
```

Ultimately resulting in:
```
TimeoutError: timed out
```

## Solution: Use waitress for Static File Serving

We have implemented a solution that uses:

1. **Eventlet** for WebSocket connections (required by Flask-SocketIO)
2. **Waitress** for static file serving (more reliable on Windows)

### Key Changes Made:

1. **Static File Server** in a separate thread using waitress:
   ```python
   def run_static_server():
       """Run the static file server with waitress instead of eventlet"""
       from waitress import serve
       print("Starting static file server on port 5001...")
       serve(static_app, host='127.0.0.1', port=5001, threads=8)
   ```

2. **WebSocket Server** running in the main thread with eventlet:
   ```python
   def run_websocket_server():
       """Run the WebSocket server"""
       print("Starting WebSocket server on port 5000...")
       socketio.run(
           app, 
           debug=True, 
           host='127.0.0.1',
           port=5000,
           use_reloader=False
       )
   ```

3. **Thread Management**:
   - Static server runs in a background daemon thread
   - WebSocket server runs in the main thread
   - Health check to verify static server is running

### Why This Fixes the Issue:

1. **Separation of Concerns**: Each server uses the technology best suited for its purpose
2. **Waitress Reliability**: Waitress is more stable for serving static files on Windows
3. **Resource Isolation**: Large file transfers don't interfere with WebSocket connections

## How to Run

Simply use the `run_fixed_server.bat` script which:
1. Installs waitress if needed
2. Runs the application with the combined servers

Alternatively, directly run:
```
python run.py
```

## Ports Used

- **5000**: WebSocket server (Flask-SocketIO)
- **5001**: Static file server (Waitress)

Your application UI should continue to work as before, but without the connection errors.
