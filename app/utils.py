import os
from werkzeug.utils import secure_filename
from flask import current_app

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'book': {'pdf', 'doc', 'docx', 'txt', 'epub'},
    'video': {'mp4', 'avi', 'mov', 'mkv', 'webm'},
    'audio': {'mp3', 'wav', 'ogg', 'm4a'},
    'document': {'pdf', 'doc', 'docx', 'txt', 'ppt', 'pptx', 'xls', 'xlsx'},
    'other': {'pdf', 'doc', 'docx', 'txt', 'zip', 'rar'}
}

def allowed_file(filename, resource_type='other'):
    """Check if file extension is allowed for the resource type"""
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    
    if resource_type in ALLOWED_EXTENSIONS:
        return ext in ALLOWED_EXTENSIONS[resource_type]
    else:
        return ext in ALLOWED_EXTENSIONS['other']

def save_image(file, folder='uploads'):
    """Save uploaded image file"""
    if file and allowed_file(file.filename, 'image'):
        filename = secure_filename(file.filename)
        # Create unique filename
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        
        # Create directory if it doesn't exist
        upload_folder = os.path.join(current_app.root_path, 'static', folder)
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        return filename
    return None

def save_file(file, folder='resources'):
    """Save uploaded file and return filename"""
    if file and file.filename:
        filename = secure_filename(file.filename)
        # Create unique filename
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        
        # Create directory if it doesn't exist
        upload_folder = os.path.join(current_app.root_path, 'static', folder)
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        return filename
    return None

def get_file_size(file):
    """Get file size in bytes"""
    if file:
        # Go to end of file to get size
        file.seek(0, 2)  # Seek to end
        size = file.tell()
        file.seek(0)  # Reset to beginning
        return size
    return 0

def get_file_extension(filename):
    """Get file extension from filename"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''