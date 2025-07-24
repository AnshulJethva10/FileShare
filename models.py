"""
Database models and operations for the File Sharing Application
"""
import sqlite3
import hashlib
from datetime import datetime

class UserModel:
    """Model for user database operations"""
    
    def __init__(self, db_name='file_sharing.db'):
        self.db_name = db_name
    
    def init_db(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create default admin user if no users exist
        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] == 0:
            # Create a default user for existing files
            default_password = hashlib.sha256('admin123'.encode()).hexdigest()
            cursor.execute('''
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            ''', ('admin', 'admin@fileshare.local', default_password))
            print("Created default admin user (username: admin, password: admin123)")
        
        conn.commit()
        conn.close()
    
    def create_user(self, username, email, password):
        """Create a new user"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            ''', (username, email, password_hash))
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            return None
    
    def authenticate_user(self, username, password):
        """Authenticate a user"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, email FROM users 
            WHERE username = ? AND password_hash = ? AND is_active = 1
        ''', (username, password_hash))
        user = cursor.fetchone()
        conn.close()
        return user
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, email FROM users WHERE id = ? AND is_active = 1
        ''', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user
    
    def user_exists(self, username=None, email=None):
        """Check if user exists"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        if username:
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        elif email:
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        else:
            return False
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

class FileModel:
    """Model for file database operations"""
    
    def __init__(self, db_name='file_sharing.db'):
        self.db_name = db_name
    
    def init_db(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Check if files table exists and has user_id column
        cursor.execute("PRAGMA table_info(files)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'user_id' not in columns:
            # If user_id column doesn't exist, add it
            try:
                cursor.execute('ALTER TABLE files ADD COLUMN user_id INTEGER DEFAULT 1')
                print("Added user_id column to existing files table")
            except sqlite3.OperationalError:
                # Table doesn't exist, create it
                pass
        
        # Create or update the files table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                file_hash TEXT NOT NULL,
                user_id INTEGER NOT NULL DEFAULT 1,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                download_count INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        conn.commit()
        conn.close()
    
    def add_file(self, filename, original_filename, file_size, file_hash, user_id):
        """Add a new file record to the database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO files (filename, original_filename, file_size, file_hash, user_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (filename, original_filename, file_size, file_hash, user_id))
        file_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return file_id
    
    def get_user_files(self, user_id):
        """Get all files belonging to a specific user"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, original_filename, file_size, upload_date, download_count
            FROM files WHERE user_id = ? ORDER BY upload_date DESC
        ''', (user_id,))
        files = cursor.fetchall()
        conn.close()
        return files
    
    def get_file_by_id(self, file_id, user_id=None):
        """Get a specific file by ID, optionally filtered by user"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        if user_id:
            cursor.execute('''
                SELECT id, filename, original_filename, file_size, file_hash
                FROM files WHERE id = ? AND user_id = ?
            ''', (file_id, user_id))
        else:
            cursor.execute('''
                SELECT id, filename, original_filename, file_size, file_hash
                FROM files WHERE id = ?
            ''', (file_id,))
        file_record = cursor.fetchone()
        conn.close()
        return file_record
    
    def increment_download_count(self, file_id):
        """Increment the download count for a file"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('UPDATE files SET download_count = download_count + 1 WHERE id = ?', (file_id,))
        conn.commit()
        conn.close()
    
    def delete_file(self, file_id):
        """Delete a file record from the database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM files WHERE id = ?', (file_id,))
        conn.commit()
        conn.close()
