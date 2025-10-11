import os
from werkzeug.utils import secure_filename
from flask import current_app

# Allowed file extensions
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_FILE_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'mp3', 'wav', 'mp4', 'avi', 'mov'}

def allowed_file(filename, file_type='image'):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    
    if file_type == 'image':
        return ext in ALLOWED_IMAGE_EXTENSIONS
    else:
        return ext in ALLOWED_FILE_EXTENSIONS

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
    """Save uploaded file"""
    if file and allowed_file(file.filename, 'file'):
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