"""
Utility functions for optimized media handling
"""
import os
import uuid
from werkzeug.utils import secure_filename
from flask import send_file, current_app, url_for

def save_uploaded_file(file, subfolder='uploads'):
    """
    Save an uploaded file to the static folder with a unique filename
    
    Args:
        file: Flask file upload object
        subfolder: Subfolder within static to save the file
        
    Returns:
        str: The URL path to the saved file
    """
    if not file or not file.filename:
        raise ValueError("No file provided")
    
    # Secure the filename and add UUID to prevent conflicts
    filename = secure_filename(file.filename)
    name, ext = os.path.splitext(filename)
    unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
    
    # Create upload directory if it doesn't exist
    upload_dir = os.path.join(current_app.static_folder, subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save the file
    file_path = os.path.join(upload_dir, unique_filename)
    file.save(file_path)
    
    # Return the URL path
    return url_for('static', filename=f'{subfolder}/{unique_filename}')

def serve_optimized_video(filename, cache_timeout=43200):
    """
    Serve video files with optimized settings for better performance with WebSockets
    
    Args:
        filename (str): The filename of the video to serve
        cache_timeout (int): Cache timeout in seconds, default 12 hours
        
    Returns:
        Response: Flask response with optimized video delivery settings
    """
    video_path = os.path.join(current_app.static_folder, 'video', filename)
    
    if not os.path.exists(video_path):
        return None
    
    return send_file(
        video_path,
        mimetype='video/mp4',
        conditional=True,  # Support for range requests
        max_age=cache_timeout
    )

def serve_optimized_audio(filename, cache_timeout=43200):
    """
    Serve audio files with optimized settings for better performance with WebSockets
    
    Args:
        filename (str): The filename of the audio to serve
        cache_timeout (int): Cache timeout in seconds, default 12 hours
        
    Returns:
        Response: Flask response with optimized audio delivery settings
    """
    audio_path = os.path.join(current_app.static_folder, 'audio', filename)
    
    if not os.path.exists(audio_path):
        return None
    
    return send_file(
        audio_path,
        mimetype='audio/mpeg',
        conditional=True,
        max_age=cache_timeout
    )
