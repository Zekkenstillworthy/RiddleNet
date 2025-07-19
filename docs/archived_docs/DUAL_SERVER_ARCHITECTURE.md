# Dual-Server Architecture for WebSocket Optimization

This document explains the dual-server architecture implemented to solve the `WinError 10053` connection issues when serving large files alongside WebSocket connections.

## Overview

We've implemented a dual-server architecture:

1. **WebSocket Server (Port 5000)**: Handles all dynamic content and WebSocket connections
2. **Static File Server (Port 5001)**: Dedicated server for static files (CSS, JS, images, videos)

This separation ensures that large file transfers don't interfere with WebSocket connections.

## Architecture Diagram

```
Client Browser
     │
     ├───────────────────┬─────────────────┐
     │                   │                 │
     ▼                   ▼                 ▼
WebSocket            HTML/API          Static Files
Connections         Requests           Requests
(Port 5000)        (Port 5000)        (Port 5001)
     │                   │                 │
     ▼                   ▼                 ▼
┌─────────────────────────────┐    ┌─────────────┐
│                             │    │             │
│     Flask WebSocket Server  │    │ Static File │
│      (Main Application)     │    │   Server    │
│                             │    │             │
└─────────────────────────────┘    └─────────────┘
```

## Implementation Details

### 1. Static File Server (static_server.py)

A simple Flask application with waitress WSGI server that only serves static files:
- Optimized for file transfers
- Handles range requests for video streaming
- Adds proper caching headers
- Uses waitress for better Windows compatibility

### 2. Context Processors for URL Generation

The main application includes context processors that generate URLs for the static server:

```python
@app.context_processor
def utility_processor():
    def static_url(path):
        return f"http://localhost:5001/static/{path}"
        
    def media_url(type, path):
        return f"http://localhost:5001/media/{type}/{path}"
        
    return dict(static_url=static_url, media_url=media_url)
```

### 3. Template Updates

Templates use these helper functions:

```html
<!-- For static files -->
<link rel="stylesheet" href="{{ static_url('css/style.css') }}">

<!-- For media files -->
<video>
    <source data-src="{{ media_url('video', 'example.mp4') }}" type="video/mp4">
</video>
```

### 4. Optimized Video Loading

JavaScript in socket-client.js optimizes video loading:
- Delays video loading until after WebSocket connection is established
- Uses data-src attribute to prevent immediate loading
- Creates placeholders until videos are ready to load
- Staggers loading to prevent network congestion

## Benefits

1. **Improved Stability**: WebSocket connections remain stable even when serving large files
2. **Better Performance**: Each server is optimized for its specific purpose
3. **Scalability**: Each server can be scaled independently
4. **Fault Isolation**: Issues with static file serving won't impact WebSocket functionality

## Running the Application

Start the application with:

```
python run.py
```

This will launch:
- Static File Server on http://localhost:5001
- WebSocket Server on http://localhost:5000

## Production Deployment

For production, consider:

1. Using Nginx as a reverse proxy in front of both servers
2. Setting up a CDN for static content
3. Using environment variables to configure server addresses
4. Running the servers as systemd services on Linux
