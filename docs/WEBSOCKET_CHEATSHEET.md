# WebSocket Quick Reference

## Starting the Server

### Development Mode
```
python run.py
```

### Production Mode
```
FLASK_ENV=production python run.py
```

### Production Mode (Linux/MacOS with Gunicorn)
```
gunicorn --worker-class eventlet -w 1 production:app
```

## Testing WebSocket Functionality

### Basic Connection Test
```
python test_websocket.py
```

### Client Simulation
```
python test_websocket_client.py
```

### Stress Testing
```
python test_websocket_stress.py --concurrent 5 --duration 30 --download
```

### Run All Tests
```
run_connection_tests.bat
```

## Key Files

- `socket_manager.py` - WebSocket server configuration
- `socket_events.py` - WebSocket event handlers
- `utils/socket_monitor.py` - Connection monitoring utilities
- `utils/media_utils.py` - Optimized media file serving
- `static/js/socket-client.js` - Client-side WebSocket implementation

## Documentation

- `WEBSOCKET_GUIDE.md` - General WebSocket implementation guide
- `WEBSOCKET_OPTIMIZATION.md` - Optimization recommendations
- `WEBSOCKET_DEPLOYMENT.md` - Production deployment guide
- `WINERROR_10053_SOLUTION.md` - Specific fixes for connection issues

## Common Issues

1. **WinError 10053** - Connection aborted during large file transfers
   - Solution: Use dedicated media routes and optimized settings
   
2. **Connection timeouts**
   - Solution: Increase ping_timeout and ping_interval in socket_manager.py
   
3. **Multiple connections failing**
   - Solution: Use Redis message queue for multi-process deployments
