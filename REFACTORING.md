# Project Refactoring Notes

## Changes Made

1. **Removed batch files:**
   - Removed `start_servers.bat` and `start_production.bat` as they were not essential
   - The application is now started directly with `python run.py` 
   - Updated README.md to reflect this change

2. **Previous fix to start_servers.bat (now removed):**
   - Had removed reference to the non-existent `static_server.py` file
   - Updated to use only `run.py` which already includes both the WebSocket server and the static file server
   - Simplified the startup process to use a single command

## Architecture Overview

The application uses a dual-server architecture, but both servers are started from the same Python script (`run.py`):

1. **WebSocket Server (Port 5000)**
   - Handles real-time communication using Flask-SocketIO
   - Serves dynamic content and API endpoints
   - Uses eventlet as the async mode

2. **Static File Server (Port 5001)**
   - Integrated into `run.py` as a separate Flask application
   - Uses waitress WSGI server for better performance with static files
   - Runs in a separate thread within the same process

## How to Start the Application

Simply run `python run.py`, which will:
1. Initialize both servers
2. The static file server will be available at http://localhost:5001
3. The main application will be available at http://localhost:5000

## Previous Configuration

The previous configuration used batch files as convenience wrappers for starting the application on Windows. These have been removed as they weren't essential to the functionality of the application.
