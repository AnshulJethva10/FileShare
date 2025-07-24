"""
Main application entry point for the File Sharing Application
"""
import os
from dotenv import load_dotenv
from __init__ import create_app

# Load environment variables
load_dotenv()

if __name__ == '__main__':
    # Get environment or default to development
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Create the application
    app = create_app(config_name)
    
    print("🚀 Starting File Sharing Application...")
    print("📂 Upload folder:", app.config['UPLOAD_FOLDER'])
    print("💾 Database:", app.config['DATABASE_NAME'])
    print(f"🌐 Access at: http://{app.config['HOST']}:{app.config['PORT']}")
    
    # Run the application
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )