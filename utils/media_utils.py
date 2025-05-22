"""
Utility functions for optimized media handling
"""
import os
from flask import send_file, current_app

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
        add_etags=True,
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
        add_etags=True,
        max_age=cache_timeout
    )