"""
Application factory for the File Sharing Application
"""
from flask import Flask
from config import config
from models import FileModel, UserModel, ServerKEMModel
from routes import main, init_routes
from auth_routes import auth
from sharing_routes import sharing, init_sharing_routes
from crypto_plugins import load_kem_provider
from key_management import KeyManagementService

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
    
    # Initialize Post-Quantum KEM provider
    kem_provider = None
    if app.config.get('PQ_KEM_PROVIDER', 'none').lower() != 'none':
        try:
            kem_provider = load_kem_provider(
                provider=app.config['PQ_KEM_PROVIDER'],
                algorithm=app.config['PQ_KEM_ALGORITHM'],
                allow_fallback=app.config['PQ_KEM_FALLBACK']
            )
            
            if kem_provider and kem_provider.is_available():
                print(f"🔐 Post-Quantum KEM enabled: {kem_provider.get_algorithm_name()}")
                
                # Initialize key management service
                key_mgmt = KeyManagementService(
                    db_name=app.config['DATABASE_NAME'],
                    kem_provider=kem_provider,
                    master_key=app.config['ENCRYPTION_MASTER_KEY']
                )
                
                # Ensure server static key exists (for shares)
                if app.config.get('PQ_ENABLE_SHARE_LINKS', True):
                    key_mgmt.ensure_server_key(
                        key_id='default',
                        rotation_days=app.config['PQ_STATIC_KEY_ROTATION_DAYS']
                    )
                
                # Store in app context for access by routes
                app.kem_provider = kem_provider
                app.key_mgmt = key_mgmt
            else:
                print("⚠️  Post-Quantum KEM not available, using legacy encryption only")
                app.kem_provider = None
                app.key_mgmt = None
        except Exception as e:
            print(f"⚠️  Failed to initialize PQ KEM: {e}")
            app.kem_provider = None
            app.key_mgmt = None
    else:
        print("ℹ️  Post-Quantum KEM disabled in configuration")
        app.kem_provider = None
        app.key_mgmt = None
    
    # Initialize routes
    init_routes(app)
    init_sharing_routes(app)
    
    # Register blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(sharing)
    app.register_blueprint(main)
    
    return app
