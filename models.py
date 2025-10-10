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
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = cursor.fetchone() is not None
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                pq_public_key BLOB,
                pq_private_key_encrypted BLOB,
                pq_key_algorithm TEXT,
                pq_key_created_at TIMESTAMP
            )
        ''')
        
        # Migrate existing users table if needed
        if table_exists:
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            
            pq_columns = [
                ('pq_public_key', 'BLOB'),
                ('pq_private_key_encrypted', 'BLOB'),
                ('pq_key_algorithm', 'TEXT'),
                ('pq_key_created_at', 'TIMESTAMP')
            ]
            
            for col_name, col_type in pq_columns:
                if col_name not in columns:
                    try:
                        cursor.execute(f'ALTER TABLE users ADD COLUMN {col_name} {col_type}')
                        print(f"Added {col_name} column to users table")
                    except sqlite3.OperationalError as e:
                        print(f"Warning: Could not add {col_name}: {e}")
        
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
        
        # Create server_kem_keys table for static server keys
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS server_kem_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_id TEXT UNIQUE NOT NULL,
                public_key BLOB NOT NULL,
                private_key_encrypted BLOB NOT NULL,
                algorithm TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def update_user_pq_keys(self, user_id, public_key, private_key_encrypted, algorithm):
        """Update or set user's post-quantum keys"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET pq_public_key = ?, pq_private_key_encrypted = ?,
                           pq_key_algorithm = ?, pq_key_created_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (public_key, private_key_encrypted, algorithm, user_id))
        conn.commit()
        conn.close()
    
    def get_user_pq_keys(self, user_id):
        """Get user's post-quantum keys"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT pq_public_key, pq_private_key_encrypted, pq_key_algorithm, pq_key_created_at
            FROM users WHERE id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
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
        
        # Check and add encryption columns if they don't exist
        encryption_columns = ['is_encrypted', 'encryption_salt', 'encryption_method']
        for col in encryption_columns:
            if col not in columns:
                try:
                    if col == 'is_encrypted':
                        cursor.execute(f'ALTER TABLE files ADD COLUMN {col} BOOLEAN DEFAULT 0')
                    elif col == 'encryption_method':
                        cursor.execute(f'ALTER TABLE files ADD COLUMN {col} TEXT DEFAULT "none"')
                    else:
                        cursor.execute(f'ALTER TABLE files ADD COLUMN {col} TEXT')
                    print(f"Added {col} column to files table")
                except sqlite3.OperationalError:
                    pass
        
        # Check and add Kyber-KEM columns if they don't exist
        kem_columns = ['kem_ciphertext', 'kem_algorithm', 'kem_public_key_id']
        for col in kem_columns:
            if col not in columns:
                try:
                    if col == 'kem_ciphertext':
                        cursor.execute(f'ALTER TABLE files ADD COLUMN {col} BLOB')
                    else:
                        cursor.execute(f'ALTER TABLE files ADD COLUMN {col} TEXT')
                    print(f"Added {col} column to files table")
                except sqlite3.OperationalError:
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
                is_encrypted BOOLEAN DEFAULT 0,
                encryption_salt TEXT,
                encryption_method TEXT DEFAULT "none",
                kem_ciphertext BLOB,
                kem_algorithm TEXT,
                kem_public_key_id TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        conn.commit()
        conn.close()
    
    def add_file(self, filename, original_filename, file_size, file_hash, user_id, 
                 is_encrypted=False, encryption_salt=None, encryption_method="none",
                 kem_ciphertext=None, kem_algorithm=None, kem_public_key_id=None):
        """Add a new file record to the database with encryption and KEM metadata"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO files (filename, original_filename, file_size, file_hash, user_id, 
                             is_encrypted, encryption_salt, encryption_method,
                             kem_ciphertext, kem_algorithm, kem_public_key_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (filename, original_filename, file_size, file_hash, user_id, 
              is_encrypted, encryption_salt, encryption_method,
              kem_ciphertext, kem_algorithm, kem_public_key_id))
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
        
        # Check if encryption columns exist in the table
        cursor.execute("PRAGMA table_info(files)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Build SELECT query based on available columns
        base_columns = "id, filename, original_filename, file_size, file_hash, user_id, upload_date, download_count"
        
        if 'is_encrypted' in columns and 'encryption_salt' in columns and 'encryption_method' in columns:
            select_columns = f"{base_columns}, is_encrypted, encryption_salt, encryption_method"
        else:
            select_columns = f"{base_columns}, 0 as is_encrypted, NULL as encryption_salt, 'none' as encryption_method"
        
        # Add KEM columns if available
        if 'kem_ciphertext' in columns:
            select_columns += ", kem_ciphertext, kem_algorithm, kem_public_key_id"
        else:
            select_columns += ", NULL as kem_ciphertext, NULL as kem_algorithm, NULL as kem_public_key_id"
        
        if user_id:
            cursor.execute(f'''
                SELECT {select_columns}
                FROM files WHERE id = ? AND user_id = ?
            ''', (file_id, user_id))
        else:
            cursor.execute(f'''
                SELECT {select_columns}
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


class ServerKEMModel:
    """Model for server KEM key operations"""
    
    def __init__(self, db_name='file_sharing.db'):
        self.db_name = db_name
    
    def save_server_key(self, key_id, public_key, private_key_encrypted, algorithm):
        """Save a new server KEM key pair"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Deactivate any existing keys for this key_id
        cursor.execute('UPDATE server_kem_keys SET is_active = 0 WHERE key_id = ?', (key_id,))
        
        # Insert new key
        cursor.execute('''
            INSERT INTO server_kem_keys (key_id, public_key, private_key_encrypted, algorithm)
            VALUES (?, ?, ?, ?)
        ''', (key_id, public_key, private_key_encrypted, algorithm))
        
        conn.commit()
        conn.close()
    
    def get_active_server_key(self, key_id='default'):
        """Get the active server key for a given key_id"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT key_id, public_key, private_key_encrypted, algorithm, created_at
            FROM server_kem_keys
            WHERE key_id = ? AND is_active = 1
            ORDER BY created_at DESC
            LIMIT 1
        ''', (key_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def check_key_rotation_needed(self, key_id='default', rotation_days=90):
        """Check if server key rotation is needed"""
        key_info = self.get_active_server_key(key_id)
        if not key_info:
            return True  # No key exists, rotation needed
        
        created_at = key_info[4]  # created_at timestamp
        from datetime import datetime, timedelta
        
        created_date = datetime.fromisoformat(created_at)
        rotation_threshold = datetime.now() - timedelta(days=rotation_days)
        
        return created_date < rotation_threshold
