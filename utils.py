"""
Utility functions for the File Sharing Application
"""
import os
import hashlib

def calculate_file_hash(filepath):
    """Calculate SHA256 hash of a file"""
    hash_sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def format_file_size(size_bytes):
    """Format file size in human-readable format"""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    return f"{size_bytes:.1f}{size_names[i]}"

def get_unique_filename(original_filename):
    """Generate a unique filename with timestamp prefix"""
    from datetime import datetime
    from werkzeug.utils import secure_filename
    
    safe_filename = secure_filename(original_filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
    return timestamp + safe_filename
