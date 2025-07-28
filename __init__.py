"""
Application factory for the File Sharing Application
"""
from flask import Flask
from config import config
from models import FileModel, UserModel
from routes import main, init_routes
from auth_routes import auth
from sharing_routes import sharing, init_sharing_routes

def create_app(config_name='default'):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize database
    file_model = FileModel(app.config['DATABASE_NAME'])
    file_model.init_db()
    
    user_model = UserModel(app.config['DATABASE_NAME'])
    user_model.init_db()
    
    # Initialize routes
    init_routes(app)
    init_sharing_routes(app)
    
    # Register blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(sharing)
    app.register_blueprint(main)
    
    return app
