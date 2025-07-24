# File Sharing Application

A modular Flask-based file sharing application with upload, download, and management capabilities.

## Project Structure

```
File-Sharing/
├── app.py              # Main application entry point
├── __init__.py         # Application factory
├── config.py           # Configuration settings
├── models.py           # Database models and operations
├── routes.py           # Route handlers (controllers)
├── services.py         # Business logic layer
├── utils.py            # Utility functions
├── templates.py        # HTML templates
├── requirements.txt    # Python dependencies
├── file_sharing.db     # SQLite database
└── uploads/           # Upload directory
```

## Modular Architecture

### 1. **config.py** - Configuration Management
- Centralized configuration settings
- Environment-specific configurations (development, production)
- Secret keys, upload settings, database configuration

### 2. **models.py** - Data Layer
- Database models and operations
- SQLite database interactions
- CRUD operations for file records

### 3. **services.py** - Business Logic Layer
- File upload processing
- File download handling
- File deletion logic
- Separation of business logic from routes

### 4. **routes.py** - Route Handlers (Controllers)
- Flask route definitions
- Request/response handling
- Blueprint-based organization
- API endpoints

### 5. **utils.py** - Utility Functions
- File hash calculation
- File size formatting
- Unique filename generation
- Reusable helper functions

### 6. **templates.py** - Frontend Templates
- HTML templates
- Separated from route logic
- Responsive design

### 7. **__init__.py** - Application Factory
- Flask application creation
- Configuration loading
- Database initialization
- Blueprint registration

## Features

- ✅ File upload with size limits (16MB)
- ✅ File download with tracking
- ✅ File deletion
- ✅ File listing with metadata
- ✅ SQLite database storage
- ✅ Responsive web interface
- ✅ API endpoints for JSON data
- ✅ Modular architecture

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Access at: http://localhost:5000

## Benefits of Modular Structure

1. **Maintainability**: Each module has a single responsibility
2. **Testability**: Easy to unit test individual components
3. **Scalability**: Easy to extend and add new features
4. **Readability**: Clear separation of concerns
5. **Reusability**: Components can be reused across projects
6. **Team Development**: Multiple developers can work on different modules

## API Endpoints

- `GET /` - Main interface with upload form and file list
- `POST /` - Upload a new file
- `GET /download/<file_id>` - Download a specific file
- `GET /delete/<file_id>` - Delete a specific file
- `GET /api/files` - JSON API to get file list

## Database Schema

```sql
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    file_hash TEXT NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    download_count INTEGER DEFAULT 0
);
```

## TODO

### 🔒 Security Enhancements
- [ ] **File Encryption**: Implement AES-256 encryption for uploaded files
  - [ ] Encrypt files at rest using unique keys per file
  - [ ] Automatic decryption on download

- [ ] **Authentication & Authorization**
  - [x] User registration and login system
  - [x] Session-based authentication
  - [ ] Role-based access control (Admin/User)
