# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

Project: FileShare (Flask-based modular file sharing app with optional AES-256-GCM encryption and secure sharing links)

Common commands (Windows PowerShell)
- Create and activate a virtual environment, then install dependencies:
  - python -m venv .venv
  - .\.venv\Scripts\Activate.ps1
  - pip install -r requirements.txt

- Run the application (dotenv is supported; these env vars are optional):
  - $env:FLASK_ENV = 'development'
  - $env:FLASK_DEBUG = 'true'
  - python app.py
  - App defaults: HOST=127.0.0.1, PORT=5000, DB=file_sharing.db, UPLOAD_FOLDER=uploads

- Override host/port if needed:
  - $env:HOST = '0.0.0.0'
  - $env:PORT = '8000'
  - python app.py

- Configure encryption (optional; defaults are development-friendly):
  - $env:ENABLE_ENCRYPTION = 'true'
  - $env:ENCRYPTION_MASTER_KEY = '{{ENCRYPTION_MASTER_KEY}}'  (set to a strong secret locally)

- Run the existing test scripts individually:
  - python test_encryption.py
  - python test_sharing.py
  Notes:
  - These are ad-hoc scripts that print results; they don’t require pytest.
  - test_sharing.py expects the SQLite DB (file_sharing.db) and uploads/ to be present; it will insert a test row if necessary.

Important environment variables
- SECRET_KEY: Flask secret key (default is development-only)
- UPLOAD_FOLDER: Directory for stored files (default: uploads)
- MAX_CONTENT_LENGTH: Upload size limit in bytes (default: 16777216)
- DB_NAME: SQLite file name (default: file_sharing.db)
- ENABLE_ENCRYPTION: Toggle encryption-at-rest for uploads (default: True)
- ENCRYPTION_MASTER_KEY: Base secret used in per-user key derivation
- HOST, PORT, FLASK_ENV, FLASK_DEBUG: Server runtime options

High-level architecture and flow
- Entry point: app.py
  - Loads dotenv, reads FLASK_ENV, constructs the app via __init__.create_app, and runs the server using values from config.

- Application factory: __init__.py
  - Loads configuration (config.py) via a mapping: development/production/default
  - Initializes SQLite schema through models.UserModel.init_db() and models.FileModel.init_db()
    - A default admin user (admin/admin123) is created if no users exist
  - Initializes and registers Blueprints:
    - auth (auth_routes.py)
    - sharing (sharing_routes.py)
    - main (routes.py)

- Configuration: config.py
  - Centralizes runtime settings (UPLOAD_FOLDER, DB_NAME, size limits, cookie settings, toggles)
  - Development vs. Production classes; production enforces secure cookies
  - init_app ensures the upload directory exists

- Data layer: models.py
  - UserModel: users table CRUD and auth (username/email uniqueness, SHA-256 password hashing)
  - FileModel: files table CRUD; tracks user ownership, upload timestamp, download counts
  - Migration-like safeguards: adds columns (user_id, is_encrypted, encryption_salt, encryption_method) if missing; creates tables if absent

- Services
  - FileService (services.py)
    - Upload flow: saves file, computes size/hash; if ENABLE_ENCRYPTION=True, uses crypto to encrypt and stores metadata; persists record in files table
    - Download flow: looks up record, decrypts to a temp file when needed, increments download_count, returns a send_file response
    - Delete flow: removes file from disk and deletes DB record
  - SecureFileSharing (secure_sharing.py)
    - Creates shareable, encrypted artifacts for existing files and stores a share record (shares table)
    - Issues links of the form /share/<share_id>#<token>; the token encodes a key, and client JS passes it to the backend as a query param for download
    - Enforces expiry times, optional max downloads, and active/inactive status; increments download counts per share

- Cryptography utilities: crypto_utils.py
  - SecureFileEncryption: AES-256-GCM, PBKDF2 key derivation (per-user keys for encryption-at-rest), integrity verification via SHA-256 on plaintext
  - For secure sharing, uses per-share keys and AES-GCM; encrypted content layout is nonce + auth_tag + ciphertext

- HTTP/UI layer
  - routes.py (main):
    - ‘/’ redirects to login if unauthenticated; ‘/dashboard’ shows upload/list with actions; ‘/download/<id>’, ‘/delete/<id>’; ‘/api/files’ returns JSON list
    - Uses FileService for operations; uses in-module HTML_TEMPLATE (templates.py) rendered with render_template_string
  - auth_routes.py (auth):
    - ‘/auth/login’, ‘/auth/signup’, ‘/auth/logout’; simple session-based auth; decorator login_required used by main/sharing routes
  - sharing_routes.py (sharing):
    - POST ‘/create-share’ returns a JSON object with share_url; GET ‘/share/<share_id>’ renders a download page; GET ‘/download-shared/<share_id>?token=...’ streams the decrypted file
    - Templates for share UI are embedded in sharing_routes.py

- Templates and assets
  - Tailwind CSS via CDN; icons via Font Awesome; HTML templates embedded as strings (templates.py and auth_templates.py)

- Database schema (effective)
  - users: id, username, email, password_hash, created_at, is_active
  - files: id, filename, original_filename, file_size, file_hash, user_id, upload_date, download_count, is_encrypted, encryption_salt, encryption_method
  - shares: id, share_id, encrypted_filename, original_filename, file_size, user_id, created_at, expiry_time, max_downloads, download_count, is_active, encryption_key, salt, nonce (created by SecureFileSharing)

Operational notes
- First run initializes the SQLite schema and creates a default admin user (username: admin, password: admin123). Change credentials in production.
- The upload directory is created automatically if missing.
- For secure sharing, recipients visit /share/<share_id> and client-side JS extracts the token (from URL fragment) and calls the download endpoint with it.
- When downloading encrypted files owned by a user, a temporary decrypted file is created and cleaned up after response using atexit hooks.
