"""
Configuration settings for the File Sharing Application
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this-in-production'
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16777216))  # 16MB default
    DATABASE_NAME = os.environ.get('DB_NAME') or 'file_sharing.db'
    
    # Security settings
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    PERMANENT_SESSION_LIFETIME = int(os.environ.get('PERMANENT_SESSION_LIFETIME', 3600))
    
    # File limits
    MAX_FILES_PER_USER = int(os.environ.get('MAX_FILES_PER_USER', 100))
    MAX_STORAGE_PER_USER = int(os.environ.get('MAX_STORAGE_PER_USER', 104857600))  # 100MB default
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = os.environ.get('ALLOWED_EXTENSIONS', 'txt,pdf,png,jpg,jpeg,gif,doc,docx,xls,xlsx,ppt,pptx,zip,rar').split(',')
    
    # Encryption settings
    ENABLE_ENCRYPTION = os.environ.get('ENABLE_ENCRYPTION', 'True').lower() == 'true'
    ENCRYPTION_MASTER_KEY = os.environ.get('ENCRYPTION_MASTER_KEY', 'default-change-in-production')
    
    # Server settings
    HOST = os.environ.get('HOST', '127.0.0.1')
    PORT = int(os.environ.get('PORT', 5000))
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        # Ensure upload directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # Force HTTPS in production

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
