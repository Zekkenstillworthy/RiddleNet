# WinError 10053 Connection Aborted Solution

## Problem Summary

When serving large files (especially videos) in a Flask application with WebSocket support using eventlet on Windows, connection errors occur with error message `WinError 10053: An established connection was aborted by the software in your host machine`.

This error happens because:

1. Windows has limitations in its socket implementation
2. Eventlet's monkey patching can cause issues with Windows socket handling
3. Large file transfers interfere with long-lived WebSocket connections
4. The combination of video streaming and WebSocket communication overwhelms the socket handling

## Solution: Dual-Server Architecture

We've implemented a "separation of concerns" architecture that uses two separate web servers:

1. **Main WebSocket Server (Port 5000)**
   - Handles all dynamic content and WebSocket connections
   - Uses eventlet for WebSocket support
   - No longer responsible for serving large static files

2. **Dedicated Static File Server (Port 5001)**
   - Only serves static files (CSS, JS, images, videos)
   - Uses waitress instead of eventlet for better Windows compatibility
   - Optimized for file serving with proper headers and caching

## Implementation Details

### 1. Static File Server (static_server.py)

```python
from flask import Flask, send_from_directory, request
import os
from waitress import serve

app = Flask(__name__)
STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(STATIC_FOLDER, path)

@app.route('/media/video/<path:filename>')
def serve_video(filename):
    video_path = os.path.join(STATIC_FOLDER, 'video', filename)
    response = send_from_directory(os.path.dirname(video_path), os.path.basename(video_path))
    response.headers['Cache-Control'] = 'public, max-age=43200'
    return response

@app.route('/media/audio/<path:filename>')
def serve_audio(filename):
    audio_path = os.path.join(STATIC_FOLDER, 'audio', filename)
    response = send_from_directory(os.path.dirname(audio_path), os.path.basename(audio_path))
    response.headers['Cache-Control'] = 'public, max-age=43200'
    return response

if __name__ == '__main__':
    print("Starting static file server on port 5001...")
    serve(app, host='127.0.0.1', port=5001, threads=8)
```

### 2. Context Processors for URL Generation

Added to __init__.py:

```python
@app.context_processor
def utility_processor():
    def static_url(path):
        return f"http://localhost:5001/static/{path}"
        
    def media_url(type, path):
        return f"http://localhost:5001/media/{type}/{path}"
        
    return dict(static_url=static_url, media_url=media_url)
```

### 3. HTML Template Updates

```html
<!-- Before -->
<video class="video-background" autoplay muted loop playsinline>
    <source src="{{ url_for('static', filename='video/RiddleNet.mp4') }}" type="video/mp4">
</video>

<!-- After -->
<video class="video-background" autoplay muted loop playsinline>
    <source data-src="{{ media_url('video', 'RiddleNet.mp4') }}" type="video/mp4">
</video>
```

### 4. Client-Side JavaScript Optimization

Added to socket-client.js:

```javascript
optimizeVideoLoading() {
    // Find all videos on the page
    const videos = document.querySelectorAll('video');
    
    videos.forEach(video => {
        // For background videos, only load when needed
        if (video.classList.contains('video-background')) {
            // Replace src with data-src to prevent immediate loading
            const sources = video.querySelectorAll('source');
            sources.forEach(source => {
                if (source.src) {
                    source.dataset.src = source.src;
                    source.removeAttribute('src');
                }
            });
            
            // Only load the video when user has been on page for a few seconds
            setTimeout(() => {
                sources.forEach(source => {
                    const src = source.dataset.src;
                    if (src) {
                        source.src = src;
                    }
                });
                video.load();
            }, 3000); // 3 second delay to prioritize WebSocket
        }
    });
}
```

### 5. Server Monitoring and Health Checks

```python
from utils.static_server_monitor import static_server_monitor
if not static_server_monitor.check_availability():
    print("\n⚠️ WARNING: Static file server is not running!")
    print("Media files and static assets will not load correctly.")
```

## Why This Works

1. **Architectural Separation**: Each server handles what it's best at
   - WebSocket server only manages real-time connections
   - Static server only manages resource delivery

2. **Technology Separation**: Using the right tool for each job
   - Eventlet for WebSockets (optimized for long-lived connections)
   - Waitress for static files (optimized for Windows compatibility)

3. **Resource Management**: Better handling of system resources
   - No competition between large file transfers and WebSocket connections
   - Reduced chance of exhausting socket buffers

4. **Client-Side Optimization**: Smarter resource loading
   - Delayed video loading
   - Prioritization of WebSocket connectivity

## Running the Application

Run the application directly:

```bash
python run.py
```

This will start both the WebSocket server and static file server in a single process, with the static server running in a separate thread.

REM Start the main WebSocket server
start "RiddleNet WebSocket Server" cmd /k "python run.py"
```

## Limitations and Future Improvements

1. **Production Deployment**: For production, consider:
   - Using Nginx as a reverse proxy in front of both servers
   - Setting up a CDN for static content
   - Using environment variables for configuration

2. **Dynamic Configuration**: Currently, URLs are hardcoded to localhost. This could be made more flexible.

3. **Better Coordination**: Additional health checks and coordination between the servers could be implemented.

4. **Video Optimization**: Consider implementing video transcoding for different resolutions and formats.

## References

1. Flask-SocketIO documentation: https://flask-socketio.readthedocs.io/
2. Windows Socket errors: https://docs.microsoft.com/en-us/windows/win32/winsock/windows-sockets-error-codes-2
3. Eventlet documentation: https://eventlet.net/doc/