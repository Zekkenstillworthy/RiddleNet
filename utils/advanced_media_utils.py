"""
Advanced Media Utilities for Lesson Editor
Provides secure file handling, validation, and processing
"""

import os
import uuid
import mimetypes
from PIL import Image, ImageDraw, ImageFont
from werkzeug.utils import secure_filename
from flask import current_app
import logging

logger = logging.getLogger(__name__)

def ensure_upload_directory(lesson_id):
    """Ensure upload directory structure exists"""
    try:
        upload_base = os.path.join(current_app.static_folder, 'uploads', 'lessons', str(lesson_id))
        thumbnails_dir = os.path.join(upload_base, 'thumbnails')
        
        os.makedirs(upload_base, exist_ok=True)
        os.makedirs(thumbnails_dir, exist_ok=True)
        
        return upload_base
    except Exception as e:
        logger.error(f"Error creating upload directories: {str(e)}")
        raise

def validate_file_security(file):
    """Validate file for security issues"""
    filename = file.filename.lower()
    
    # Block dangerous file extensions
    dangerous_extensions = {
        'exe', 'bat', 'cmd', 'com', 'pif', 'scr', 'vbs', 'js', 
        'jar', 'php', 'asp', 'aspx', 'jsp', 'py', 'rb', 'pl'
    }
    
    ext = filename.rsplit('.', 1)[1] if '.' in filename else ''
    if ext in dangerous_extensions:
        raise ValueError(f"File type '{ext}' is not allowed for security reasons")
    
    # Check for double extensions
    if filename.count('.') > 1:
        parts = filename.split('.')
        if len(parts) > 2 and parts[-2] in dangerous_extensions:
            raise ValueError("Double extension detected - potential security risk")
    
    return True

def generate_secure_filename(original_filename):
    """Generate a secure, unique filename"""
    # Secure the filename
    secure_name = secure_filename(original_filename)
    
    # Add UUID to prevent conflicts and directory traversal
    name, ext = os.path.splitext(secure_name)
    unique_filename = f"{name}_{uuid.uuid4().hex[:12]}{ext}"
    
    return unique_filename

def get_file_info(file_path):
    """Get comprehensive file information"""
    try:
        stat = os.stat(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        
        return {
            'size': stat.st_size,
            'mime_type': mime_type or 'application/octet-stream',
            'created': stat.st_ctime,
            'modified': stat.st_mtime
        }
    except Exception as e:
        logger.error(f"Error getting file info: {str(e)}")
        return None

def create_image_thumbnail_advanced(image_path, thumbnail_dir, size=(300, 300)):
    """Create optimized image thumbnail with error handling"""
    try:
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Create thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            thumbnail_filename = f"thumb_{os.path.basename(image_path)}"
            # Ensure thumbnail has jpg extension for consistency
            thumbnail_filename = os.path.splitext(thumbnail_filename)[0] + '.jpg'
            thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)
            
            img.save(thumbnail_path, 'JPEG', quality=85, optimize=True)
            return thumbnail_path
            
    except Exception as e:
        logger.error(f"Error creating image thumbnail: {str(e)}")
        return create_placeholder_thumbnail(thumbnail_dir, "Image", image_path)

def create_video_thumbnail_advanced(video_path, thumbnail_dir):
    """Create video thumbnail with fallback options"""
    try:
        # Try using ffmpeg-python if available
        try:
            import ffmpeg
            
            thumbnail_filename = f"thumb_{os.path.splitext(os.path.basename(video_path))[0]}.jpg"
            thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)
            
            (
                ffmpeg
                .input(video_path, ss=1)  # Extract frame at 1 second
                .output(thumbnail_path, vframes=1, format='image2', vcodec='mjpeg')
                .overwrite_output()
                .run(quiet=True)
            )
            
            return thumbnail_path
            
        except ImportError:
            logger.warning("ffmpeg-python not available, creating placeholder video thumbnail")
            return create_placeholder_thumbnail(thumbnail_dir, "Video", video_path)
            
    except Exception as e:
        logger.error(f"Error creating video thumbnail: {str(e)}")
        return create_placeholder_thumbnail(thumbnail_dir, "Video", video_path)

def create_placeholder_thumbnail(thumbnail_dir, media_type, original_path):
    """Create a placeholder thumbnail for unsupported media types"""
    try:
        # Create a simple placeholder image
        img = Image.new('RGB', (300, 200), color='#f0f0f0')
        draw = ImageDraw.Draw(img)
        
        # Try to load a font, fall back to default if not available
        try:
            # Try to use a system font
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Draw media type text
        text = media_type.upper()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (300 - text_width) // 2
        y = (200 - text_height) // 2
        
        draw.text((x, y), text, fill='#666666', font=font)
        
        # Add file name if short enough
        filename = os.path.basename(original_path)
        if len(filename) < 30:
            try:
                small_font = ImageFont.truetype("arial.ttf", 12)
            except:
                small_font = ImageFont.load_default()
            
            bbox = draw.textbbox((0, 0), filename, font=small_font)
            text_width = bbox[2] - bbox[0]
            x = (300 - text_width) // 2
            draw.text((x, y + 40), filename, fill='#999999', font=small_font)
        
        # Save thumbnail
        thumbnail_filename = f"thumb_{os.path.splitext(os.path.basename(original_path))[0]}.jpg"
        thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)
        img.save(thumbnail_path, 'JPEG', quality=85)
        
        return thumbnail_path
        
    except Exception as e:
        logger.error(f"Error creating placeholder thumbnail: {str(e)}")
        return None

def clean_up_file(file_path):
    """Safely remove a file"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        logger.error(f"Error cleaning up file {file_path}: {str(e)}")
    return False

def format_file_size(size_bytes):
    """Convert bytes to human readable file size"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def validate_image_content(file_path):
    """Validate that an image file is actually an image"""
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False

def get_media_metadata(file_path, file_type):
    """Extract metadata from media files"""
    metadata = {
        'file_type': file_type,
        'file_size': os.path.getsize(file_path)
    }
    
    try:
        if file_type == 'images':
            with Image.open(file_path) as img:
                metadata.update({
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode
                })
        # Additional metadata extraction for videos/audio could be added here
        # using libraries like mutagen for audio or opencv for video
                
    except Exception as e:
        logger.warning(f"Could not extract metadata from {file_path}: {str(e)}")
    
    return metadata
