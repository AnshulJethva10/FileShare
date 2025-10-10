"""
Secure File Sharing Service with encrypted links
Implements secure file sharing with embedded keys in shareable links
"""
import os
import secrets
import base64
import json
import sqlite3
from urllib.parse import quote, unquote
from datetime import datetime, timedelta
from crypto_utils import SecureFileEncryption
from models import FileModel

class SecureFileSharing:
    """Secure file sharing with encrypted links"""
    
    def __init__(self, upload_folder, db_name='file_sharing.db', kem_provider=None, key_mgmt=None):
        self.upload_folder = upload_folder
        self.db_name = db_name
        self.file_model = FileModel(db_name)
        self.kem_provider = kem_provider
        self.key_mgmt = key_mgmt
        self.crypto = SecureFileEncryption(kem_provider=kem_provider)
        self.pq_enabled = kem_provider is not None and kem_provider.is_available()
        self._init_shares_table()
        
    def create_shareable_file(self, file, user_id, expiry_hours=24, max_downloads=None):
        """
        Create a shareable encrypted file with embedded key link
        Returns a secure shareable URL
        """
        try:
            # Save uploaded file temporarily
            original_filename = file.filename
            temp_filename = f"temp_{secrets.token_hex(16)}_{original_filename}"
            temp_filepath = os.path.join(self.upload_folder, temp_filename)
            file.save(temp_filepath)
            
            # Read file content
            with open(temp_filepath, 'rb') as f:
                file_content = f.read()
            
            file_size = len(file_content)
            
            # Generate cryptographic materials
            salt = os.urandom(16)
            nonce = os.urandom(12)
            share_key = os.urandom(32)  # Unique key for this share
            
            # Encrypt file with share-specific key
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.backends import default_backend
            
            cipher = Cipher(
                algorithms.AES(share_key),
                modes.GCM(nonce),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            ciphertext = encryptor.update(file_content) + encryptor.finalize()
            auth_tag = encryptor.tag
            
            # Create encrypted filename
            encrypted_filename = f"share_{secrets.token_hex(16)}.dat"
            encrypted_filepath = os.path.join(self.upload_folder, encrypted_filename)
            
            # Write encrypted file (nonce + auth_tag + ciphertext)
            with open(encrypted_filepath, 'wb') as f:
                f.write(nonce + auth_tag + ciphertext)
            
            # Calculate expiry
            expiry_time = datetime.now() + timedelta(hours=expiry_hours)
            
            # Create share token (contains all decryption info)
            share_data = {
                'key': base64.b64encode(share_key).decode('utf-8'),
                'nonce': base64.b64encode(nonce).decode('utf-8'),
                'filename': original_filename,
                'size': file_size,
                'expiry': expiry_time.isoformat(),
                'max_downloads': max_downloads
            }
            
            # Encode share data into URL-safe token
            share_token = base64.urlsafe_b64encode(
                json.dumps(share_data).encode('utf-8')
            ).decode('utf-8')
            
            # Generate unique share ID
            share_id = secrets.token_urlsafe(16)
            
            # Save share record to database
            share_record_id = self._save_share_record(
                share_id=share_id,
                encrypted_filename=encrypted_filename,
                original_filename=original_filename,
                file_size=file_size,
                user_id=user_id,
                expiry_time=expiry_time,
                max_downloads=max_downloads,
                share_token=share_token
            )
            
            # Clean up temp file
            os.remove(temp_filepath)
            
            return {
                'success': True,
                'share_id': share_id,
                'share_url': f"/share/{share_id}#{share_token}",
                'expiry': expiry_time.isoformat(),
                'message': f'File "{original_filename}" ready for secure sharing!'
            }
            
        except Exception as e:
            # Clean up files if error occurs
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
            if 'encrypted_filepath' in locals() and os.path.exists(encrypted_filepath):
                os.remove(encrypted_filepath)
            
            return {
                'success': False,
                'message': f'Error creating shareable file: {str(e)}'
            }
    
    def create_share_from_file_id(self, file_id, user_id, expiry_hours=24, max_downloads=None):
        """
        Create a share from an existing file ID in the database
        """
        try:
            from models import FileModel
            file_model = FileModel(self.db_name)
            
            # Get file info from database
            file_record = file_model.get_file_by_id(file_id, user_id)
            if not file_record:
                return {
                    'success': False,
                    'message': 'File not found or access denied'
                }
            
            # Extract file information (adjusted for actual db structure)
            # Structure: id, filename, original_filename, file_size, file_hash, user_id, upload_date, download_count, 
            #           is_encrypted, encryption_salt, encryption_method, kem_ciphertext, kem_algorithm, kem_public_key_id
            
            # Handle both old format (11 values) and new format (14 values) for backward compatibility
            if len(file_record) == 14:
                (id, filename, original_filename, file_size, file_hash, 
                 user_id_db, upload_date, download_count, is_encrypted, encryption_salt, encryption_method,
                 kem_ciphertext, kem_algorithm, kem_public_key_id) = file_record
            elif len(file_record) == 11:
                # Legacy format without KEM columns
                (id, filename, original_filename, file_size, file_hash, 
                 user_id_db, upload_date, download_count, is_encrypted, encryption_salt, encryption_method) = file_record
            else:
                # Try to unpack what we have
                id = file_record[0]
                filename = file_record[1]
                original_filename = file_record[2]
                file_size = file_record[3]
                file_hash = file_record[4]
                user_id_db = file_record[5]
                upload_date = file_record[6]
                download_count = file_record[7]
                is_encrypted = file_record[8] if len(file_record) > 8 else False
                encryption_salt = file_record[9] if len(file_record) > 9 else None
                encryption_method = file_record[10] if len(file_record) > 10 else 'none'
            
            # Check if file exists on disk
            file_path = os.path.join(self.upload_folder, filename)
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'message': 'File not found on disk'
                }
            
            # Generate share identifiers and encryption key
            share_id = self._generate_share_id()
            share_key = self.crypto.generate_share_key()
            
            # Read and, if necessary, decrypt original file data before sharing
            if is_encrypted and encryption_salt:
                # File is encrypted at rest; decrypt with per-user key prior to sharing
                decrypted_data = self.crypto.decrypt_file(file_path, encryption_salt, user_id_db)
                if decrypted_data is None:
                    return {
                        'success': False,
                        'message': 'Failed to decrypt original file for sharing'
                    }
                file_data = decrypted_data
            else:
                # File is stored unencrypted; read bytes directly
                with open(file_path, 'rb') as f:
                    file_data = f.read()
            
            # Encrypt file data for sharing using encrypt_data which returns format: nonce + auth_tag + ciphertext
            encrypted_data, salt_b64, nonce_b64 = self.crypto.encrypt_data(file_data, share_key)
            if encrypted_data is None:
                return {
                    'success': False,
                    'message': 'Failed to encrypt file for sharing'
                }
            
            # Initialize KEM data
            kem_ciphertext = None
            kem_algorithm = None
            kem_key_id = None
            
            # Wrap share key with server's Kyber public key if PQ is enabled
            if self.pq_enabled and self.key_mgmt:
                try:
                    server_public_key = self.key_mgmt.get_server_public_key('default')
                    if server_public_key:
                        # Encapsulate share key with server's public key
                        kem_ct, wrapped_share_key = self.crypto.pq_manager.encapsulate_key(
                            share_key, server_public_key
                        )
                        
                        # Combine KEM ciphertext parts
                        kem_ciphertext = kem_ct + b'||' + wrapped_share_key
                        kem_algorithm = self.kem_provider.get_algorithm_name()
                        kem_key_id = 'default'
                        
                        print(f"✅ Share key wrapped with Kyber-KEM ({kem_algorithm})")
                except Exception as e:
                    print(f"⚠️  KEM encapsulation for share failed: {e}")
            
            # Save encrypted file for sharing
            share_filename = f"share_{share_id}.dat"
            share_filepath = os.path.join(self.upload_folder, share_filename)
            
            with open(share_filepath, 'wb') as f:
                f.write(encrypted_data)
            
            # Create share record in database
            expiry_time = datetime.now() + timedelta(hours=expiry_hours)
            
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Check if KEM columns exist
            cursor.execute("PRAGMA table_info(shares)")
            columns = [column[1] for column in cursor.fetchall()]
            has_kem_columns = 'kem_ciphertext' in columns
            
            if has_kem_columns:
                cursor.execute('''
                    INSERT INTO shares (share_id, encrypted_filename, original_filename, 
                                      file_size, user_id, expiry_time, max_downloads,
                                      encryption_key, salt, nonce, kem_ciphertext, kem_algorithm, kem_key_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (share_id, share_filename, original_filename or filename, file_size, user_id,
                      expiry_time.isoformat(), max_downloads, 
                      base64.b64encode(share_key).decode('utf-8'), salt_b64, nonce_b64,
                      kem_ciphertext, kem_algorithm, kem_key_id))
            else:
                cursor.execute('''
                    INSERT INTO shares (share_id, encrypted_filename, original_filename, 
                                      file_size, user_id, expiry_time, max_downloads,
                                      encryption_key, salt, nonce)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (share_id, share_filename, original_filename or filename, file_size, user_id,
                      expiry_time.isoformat(), max_downloads, 
                      base64.b64encode(share_key).decode('utf-8'), salt_b64, nonce_b64))
            
            conn.commit()
            conn.close()
            
            # Create share token (base64 encoded key for URL fragment)
            share_token = base64.b64encode(share_key).decode('utf-8')
            
            return {
                'success': True,
                'share_id': share_id,
                'share_url': f"/share/{share_id}#{share_token}",
                'expiry': expiry_time.isoformat(),
                'message': f'File "{original_filename or filename}" ready for secure sharing!'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating share: {str(e)}'
            }
    
    def download_shared_file(self, share_id, share_token):
        """
        Download and decrypt shared file using embedded key
        """
        try:
            # Get share record from database with encryption info
            share_record = self._get_share_record_with_encryption(share_id)
            if not share_record:
                return None, 'Share not found or expired'
            
            # Parse share record with encryption details (now includes KEM fields)
            record_len = len(share_record)
            (id, share_id_db, encrypted_filename, original_filename, 
             file_size, user_id, created_at, expiry_time, max_downloads, 
             download_count, is_active, encryption_key_b64, salt_b64, nonce_b64) = share_record[:14]
            
            # Get KEM fields if available
            kem_ciphertext = share_record[14] if record_len > 14 else None
            kem_algorithm = share_record[15] if record_len > 15 else None
            kem_key_id = share_record[16] if record_len > 16 else None
            
            # Check if share is still valid
            if not is_active:
                return None, 'Share has been deactivated'
            
            # Check expiry
            expiry = datetime.fromisoformat(expiry_time)
            if datetime.now() > expiry:
                return None, 'Share has expired'
            
            # Check download limit
            if max_downloads and download_count >= max_downloads:
                return None, 'Download limit reached'
            
            # Verify share token matches stored encryption key
            try:
                token_key = base64.b64decode(share_token.encode('utf-8'))
                stored_key = base64.b64decode(encryption_key_b64.encode('utf-8'))
                
                # If KEM is enabled and ciphertext exists, try to decapsulate
                actual_share_key = stored_key
                
                if kem_ciphertext and kem_algorithm and self.pq_enabled:
                    try:
                        # Split KEM ciphertext parts
                        parts = kem_ciphertext.split(b'||')
                        if len(parts) == 2:
                            kem_ct, wrapped_key = parts
                            
                            # Get server's private key
                            server_private_key = self.key_mgmt.get_server_private_key(kem_key_id or 'default')
                            
                            if server_private_key:
                                # Decapsulate to recover share key
                                decapsulated_key = self.crypto.pq_manager.decapsulate_key(
                                    kem_ct, wrapped_key, server_private_key
                                )
                                
                                if decapsulated_key:
                                    actual_share_key = decapsulated_key
                                    print(f"✅ Share key recovered via Kyber-KEM ({kem_algorithm})")
                                else:
                                    print("⚠️  KEM decapsulation failed, using legacy key")
                    except Exception as e:
                        print(f"⚠️  KEM decryption error: {e}, using legacy key")
                
                # Verify token matches
                if token_key != stored_key and token_key != actual_share_key:
                    return None, 'Invalid share link - key mismatch'
                    
            except Exception as e:
                return None, 'Invalid share link - corrupted key'
            
            # Read encrypted file
            encrypted_filepath = os.path.join(self.upload_folder, encrypted_filename)
            if not os.path.exists(encrypted_filepath):
                return None, 'Shared file not found on disk'
            
            with open(encrypted_filepath, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt using the actual share key (which may have been decapsulated via KEM)
            import sys
            print(f"Debug: About to decrypt file {encrypted_filename}", file=sys.stderr)
            print(f"Debug: Encrypted data length: {len(encrypted_data)}", file=sys.stderr)
            print(f"Debug: Using key length: {len(actual_share_key)}", file=sys.stderr)
            print(f"Debug: Salt: {salt_b64}", file=sys.stderr)
            print(f"Debug: Nonce: {nonce_b64}", file=sys.stderr)
            
            decrypted_data = self.crypto.decrypt_data(encrypted_data, actual_share_key, salt_b64, nonce_b64)
            print(f"Debug: Decryption result: {decrypted_data is not None}", file=sys.stderr)
            if decrypted_data:
                print(f"Debug: Decrypted data length: {len(decrypted_data)}", file=sys.stderr)
            
            if decrypted_data is None:
                print(f"Debug: Decryption failed!", file=sys.stderr)
                return None, 'Failed to decrypt file - decryption error'
            
            # Create temporary file for download
            import tempfile
            temp_fd, temp_path = tempfile.mkstemp(suffix=f"_{original_filename}")
            try:
                with os.fdopen(temp_fd, 'wb') as temp_file:
                    temp_file.write(decrypted_data)
                
                # Update download count
                self._increment_download_count(share_id)
                
                return {
                    'filepath': temp_path,
                    'original_filename': original_filename,
                    'is_temp': True
                }, None
                
            except Exception as e:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return None, f'Error preparing download: {str(e)}'
            
        except Exception as e:
            return None, f'Error downloading file: {str(e)}'
    
    def get_share_info(self, share_id, include_stats=False):
        """Get information about a shared file (without downloading)"""
        share_record = self._get_share_record(share_id)
        if not share_record:
            return None
        
        (id, share_id_db, encrypted_filename, original_filename, 
         file_size, user_id, created_at, expiry_time, max_downloads, 
         download_count, is_active) = share_record
        
        info = {
            'share_id': share_id,
            'filename': original_filename,
            'file_size': file_size,
            'created_at': created_at,
            'expiry_time': expiry_time,
            'is_active': is_active,
            'is_expired': datetime.now() > datetime.fromisoformat(expiry_time)
        }
        
        if include_stats:
            info.update({
                'download_count': download_count,
                'max_downloads': max_downloads,
                'downloads_remaining': max_downloads - download_count if max_downloads else None
            })
        
        return info
    
    def deactivate_share(self, share_id, user_id):
        """Deactivate a share (only owner can do this)"""
        return self._deactivate_share(share_id, user_id)
    
    def get_user_shares(self, user_id):
        """Get all shares created by a user"""
        return self._get_user_shares(user_id)
    
    # Database operations
    def _save_share_record(self, share_id, encrypted_filename, original_filename, 
                          file_size, user_id, expiry_time, max_downloads, share_token):
        """Save share record to database"""
        import sqlite3
        conn = sqlite3.connect(self.file_model.db_name)
        cursor = conn.cursor()
        
        # Create shares table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                share_id TEXT UNIQUE NOT NULL,
                encrypted_filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expiry_time TIMESTAMP NOT NULL,
                max_downloads INTEGER,
                download_count INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                share_token TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            INSERT INTO shares (share_id, encrypted_filename, original_filename, file_size, 
                              user_id, expiry_time, max_downloads, share_token)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (share_id, encrypted_filename, original_filename, file_size, 
              user_id, expiry_time.isoformat(), max_downloads, share_token))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return record_id
    
    def _get_share_record(self, share_id):
        """Get share record from database"""
        import sqlite3
        conn = sqlite3.connect(self.file_model.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, share_id, encrypted_filename, original_filename, file_size,
                   user_id, created_at, expiry_time, max_downloads, download_count, is_active
            FROM shares WHERE share_id = ? AND is_active = 1
        ''', (share_id,))
        
        record = cursor.fetchone()
        conn.close()
        return record
    
    def _increment_download_count(self, share_id):
        """Increment download count for a share"""
        import sqlite3
        conn = sqlite3.connect(self.file_model.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE shares SET download_count = download_count + 1 
            WHERE share_id = ?
        ''', (share_id,))
        
        conn.commit()
        conn.close()
    
    def _deactivate_share(self, share_id, user_id):
        """Deactivate a share (only owner can do this)"""
        import sqlite3
        conn = sqlite3.connect(self.file_model.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE shares SET is_active = 0 
            WHERE share_id = ? AND user_id = ?
        ''', (share_id, user_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def _get_user_shares(self, user_id):
        """Get all shares created by a user"""
        import sqlite3
        conn = sqlite3.connect(self.file_model.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT share_id, original_filename, file_size, created_at, expiry_time,
                   max_downloads, download_count, is_active
            FROM shares WHERE user_id = ? ORDER BY created_at DESC
        ''', (user_id,))
        
        records = cursor.fetchall()
        conn.close()
        return records
    
    def _init_shares_table(self):
        """Initialize the shares table if it doesn't exist"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shares'")
        table_exists = cursor.fetchone() is not None
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                share_id TEXT UNIQUE NOT NULL,
                encrypted_filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expiry_time TIMESTAMP NOT NULL,
                max_downloads INTEGER,
                download_count INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                encryption_key TEXT NOT NULL,
                salt TEXT NOT NULL,
                nonce TEXT NOT NULL,
                kem_ciphertext BLOB,
                kem_algorithm TEXT,
                kem_key_id TEXT
            )
        ''')
        
        # Add KEM columns if table exists but doesn't have them
        if table_exists:
            cursor.execute("PRAGMA table_info(shares)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'kem_ciphertext' not in columns:
                try:
                    cursor.execute('ALTER TABLE shares ADD COLUMN kem_ciphertext BLOB')
                    cursor.execute('ALTER TABLE shares ADD COLUMN kem_algorithm TEXT')
                    cursor.execute('ALTER TABLE shares ADD COLUMN kem_key_id TEXT')
                    print("Added KEM columns to shares table")
                except sqlite3.OperationalError as e:
                    print(f"Warning: Could not add KEM columns: {e}")
        
        conn.commit()
        conn.close()
    
    def _generate_share_id(self):
        """Generate a unique share ID"""
        return secrets.token_urlsafe(16)
    
    def _generate_share_token(self):
        """Generate a share token for URL embedding"""
        return secrets.token_urlsafe(32)
    
    def _get_share_record(self, share_id):
        """Get share record from database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, share_id, encrypted_filename, original_filename, file_size,
                   user_id, created_at, expiry_time, max_downloads, download_count, is_active
            FROM shares WHERE share_id = ?
        ''', (share_id,))
        record = cursor.fetchone()
        conn.close()
        return record
    
    def _get_share_record_with_encryption(self, share_id):
        """Get share record from database including encryption details"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Check if KEM columns exist
        cursor.execute("PRAGMA table_info(shares)")
        columns = [column[1] for column in cursor.fetchall()]
        has_kem_columns = 'kem_ciphertext' in columns
        
        if has_kem_columns:
            cursor.execute('''
                SELECT id, share_id, encrypted_filename, original_filename, file_size,
                       user_id, created_at, expiry_time, max_downloads, download_count, is_active,
                       encryption_key, salt, nonce, kem_ciphertext, kem_algorithm, kem_key_id
                FROM shares WHERE share_id = ?
            ''', (share_id,))
        else:
            cursor.execute('''
                SELECT id, share_id, encrypted_filename, original_filename, file_size,
                       user_id, created_at, expiry_time, max_downloads, download_count, is_active,
                       encryption_key, salt, nonce, NULL as kem_ciphertext, NULL as kem_algorithm, NULL as kem_key_id
                FROM shares WHERE share_id = ?
            ''', (share_id,))
        
        record = cursor.fetchone()
        conn.close()
        return record
    
    def _increment_download_count(self, share_id):
        """Increment download count for a share"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE shares SET download_count = download_count + 1 
            WHERE share_id = ?
        ''', (share_id,))
        conn.commit()
        conn.close()
