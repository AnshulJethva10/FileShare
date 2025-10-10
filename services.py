"""
File service layer for business logic with encryption support
"""
import os
import tempfile
from models import FileModel
from utils import calculate_file_hash, get_unique_filename
from crypto_utils import SecureFileEncryption

class FileService:
    """Service class for file operations with encryption"""
    
    def __init__(self, upload_folder, db_name='file_sharing.db', enable_encryption=True, kem_provider=None, key_mgmt=None):
        self.upload_folder = upload_folder
        self.file_model = FileModel(db_name)
        self.enable_encryption = enable_encryption
        self.kem_provider = kem_provider
        self.key_mgmt = key_mgmt
        self.crypto = SecureFileEncryption(kem_provider=kem_provider) if enable_encryption else None
        self.pq_enabled = kem_provider is not None and kem_provider.is_available()
    
    def upload_file(self, file, user_id):
        """Handle file upload process with optional encryption"""
        try:
            original_filename = file.filename
            filename = get_unique_filename(original_filename)
            filepath = os.path.join(self.upload_folder, filename)
            
            # Save file temporarily
            file.save(filepath)
            
            # Calculate original file properties
            original_file_size = os.path.getsize(filepath)
            
            # Encrypt file if encryption is enabled
            if self.enable_encryption and self.crypto:
                encryption_result = self.crypto.encrypt_file(filepath, user_id)
                
                if encryption_result:
                    # File was encrypted and original was removed
                    encrypted_path = os.path.join(self.upload_folder, encryption_result['encrypted_filename'])
                    final_file_size = os.path.getsize(encrypted_path)
                    
                    # Initialize KEM metadata
                    kem_ciphertext = None
                    kem_algorithm = None
                    kem_public_key_id = None
                    
                    # Use Kyber-KEM to wrap the AES key if PQ is enabled
                    if self.pq_enabled and self.key_mgmt:
                        try:
                            # Ensure user has PQ keys
                            # Note: In production, you'd pass the actual user password
                            # For now, we'll use user_id as a proxy
                            user_public_key = self.key_mgmt.get_user_public_key(user_id)
                            
                            if user_public_key:
                                # Derive the AES key that was used for encryption
                                # (we need to store this for decapsulation)
                                import base64
                                salt = base64.b64decode(encryption_result['salt'])
                                aes_key = self.crypto._derive_key(salt, f"{self.crypto.master_password}_{user_id}")
                                
                                # Encapsulate the AES key with user's Kyber public key
                                kem_ct, wrapped_key = self.crypto.pq_manager.encapsulate_key(aes_key, user_public_key)
                                
                                # Store KEM ciphertext (combining both parts)
                                kem_ciphertext = kem_ct + b'||' + wrapped_key  # Simple separator
                                kem_algorithm = self.kem_provider.get_algorithm_name()
                                kem_public_key_id = str(user_id)  # Track which key was used
                                
                                print(f"✅ File key wrapped with Kyber-KEM ({kem_algorithm})")
                        except Exception as e:
                            print(f"⚠️  KEM encapsulation failed, falling back to legacy: {e}")
                    
                    # Save to database with encryption and KEM metadata
                    file_id = self.file_model.add_file(
                        filename=encryption_result['encrypted_filename'],
                        original_filename=original_filename,
                        file_size=original_file_size,  # Store original file size
                        file_hash=encryption_result['file_hash'],
                        user_id=user_id,
                        is_encrypted=True,
                        encryption_salt=encryption_result['salt'],
                        encryption_method="AES-256-GCM" if not kem_ciphertext else "AES-256-GCM+Kyber",
                        kem_ciphertext=kem_ciphertext,
                        kem_algorithm=kem_algorithm,
                        kem_public_key_id=kem_public_key_id
                    )
                    
                    return {
                        'success': True,
                        'file_id': file_id,
                        'message': f'File "{original_filename}" uploaded and encrypted successfully!',
                        'encrypted': True
                    }
                else:
                    # Encryption failed, remove temporary file
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    return {
                        'success': False,
                        'message': 'File encryption failed. Upload cancelled for security.'
                    }
            else:
                # No encryption - store file as-is
                file_hash = calculate_file_hash(filepath)
                
                # Save to database without encryption
                file_id = self.file_model.add_file(
                    filename=filename,
                    original_filename=original_filename,
                    file_size=original_file_size,
                    file_hash=file_hash,
                    user_id=user_id,
                    is_encrypted=False,
                    encryption_method="none"
                )
                
                return {
                    'success': True,
                    'file_id': file_id,
                    'message': f'File "{original_filename}" uploaded successfully!',
                    'encrypted': False
                }
            
        except Exception as e:
            # Clean up file if anything failed
            if os.path.exists(filepath):
                os.remove(filepath)
            return {
                'success': False,
                'message': f'Error uploading file: {str(e)}'
            }
    
    def get_file_for_download(self, file_id, user_id=None, user_password=None):
        """Get file information for download with decryption support"""
        file_record = self.file_model.get_file_by_id(file_id, user_id)
        if not file_record:
            return None, 'File not found'
        
        # file_record format with KEM fields: (id, filename, original_filename, file_size, file_hash, user_id, 
        # upload_date, download_count, is_encrypted, encryption_salt, encryption_method, 
        # kem_ciphertext, kem_algorithm, kem_public_key_id)
        stored_filename = file_record[1]
        original_filename = file_record[2]
        file_user_id = file_record[5]
        
        # Safely get encryption fields with defaults
        is_encrypted = file_record[8] if len(file_record) > 8 and file_record[8] is not None else False
        encryption_salt = file_record[9] if len(file_record) > 9 else None
        encryption_method = file_record[10] if len(file_record) > 10 else "none"
        
        # Get KEM fields if available
        kem_ciphertext = file_record[11] if len(file_record) > 11 else None
        kem_algorithm = file_record[12] if len(file_record) > 12 else None
        kem_public_key_id = file_record[13] if len(file_record) > 13 else None
        
        filepath = os.path.join(self.upload_folder, stored_filename)
        if not os.path.exists(filepath):
            return None, 'File not found on disk'
        
        if is_encrypted and self.crypto and encryption_salt:
            # Decrypt the file for download
            try:
                # Check if file uses Kyber-KEM for key protection
                if kem_ciphertext and kem_algorithm and self.pq_enabled:
                    try:
                        # Split KEM ciphertext parts
                        parts = kem_ciphertext.split(b'||')
                        if len(parts) == 2:
                            kem_ct, wrapped_key = parts
                            
                            # Get user's private key for decapsulation
                            # Note: In production, user_password would be from session or re-auth
                            private_key = self.key_mgmt.get_user_private_key(file_user_id, str(user_id))
                            
                            if private_key:
                                # Decapsulate to get AES key
                                aes_key = self.crypto.pq_manager.decapsulate_key(kem_ct, wrapped_key, private_key)
                                
                                if aes_key:
                                    # Use decapsulated key to decrypt file
                                    # Read encrypted file
                                    with open(filepath, 'rb') as f:
                                        encrypted_data = f.read()
                                    
                                    # Extract components
                                    nonce = encrypted_data[:12]
                                    auth_tag = encrypted_data[12:28]
                                    ciphertext = encrypted_data[28:]
                                    
                                    # Decrypt with recovered AES key
                                    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
                                    from cryptography.hazmat.backends import default_backend
                                    
                                    cipher = Cipher(
                                        algorithms.AES(aes_key),
                                        modes.GCM(nonce, auth_tag),
                                        backend=default_backend()
                                    )
                                    decryptor = cipher.decryptor()
                                    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
                                    
                                    print(f"✅ File decrypted using Kyber-KEM")
                                else:
                                    # Fall back to legacy decryption
                                    print("⚠️  KEM decapsulation failed, trying legacy decryption")
                                    decrypted_data = self.crypto.decrypt_file(filepath, encryption_salt, file_user_id)
                            else:
                                # No private key, fall back to legacy
                                decrypted_data = self.crypto.decrypt_file(filepath, encryption_salt, file_user_id)
                        else:
                            # Invalid KEM format, fall back
                            decrypted_data = self.crypto.decrypt_file(filepath, encryption_salt, file_user_id)
                    except Exception as e:
                        print(f"⚠️  KEM decryption error: {e}, falling back to legacy")
                        decrypted_data = self.crypto.decrypt_file(filepath, encryption_salt, file_user_id)
                else:
                    # No KEM, use legacy decryption
                    decrypted_data = self.crypto.decrypt_file(filepath, encryption_salt, file_user_id)
                
                if decrypted_data is None:
                    return None, 'Failed to decrypt file'
                
                # Verify file integrity
                expected_hash = file_record[4]  # file_hash from database
                if not self.crypto.verify_file_integrity(decrypted_data, expected_hash):
                    return None, 'File integrity check failed'
                
                # Create temporary file for download
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{original_filename}")
                temp_file.write(decrypted_data)
                temp_file.close()
                
                # Increment download count
                self.file_model.increment_download_count(file_id)
                
                return {
                    'filepath': temp_file.name,
                    'original_filename': original_filename,
                    'file_record': file_record,
                    'is_temp': True,  # Flag to indicate this file should be cleaned up
                    'decrypted': True
                }, None
                
            except Exception as e:
                return None, f'Decryption error: {str(e)}'
        else:
            # File is not encrypted, serve directly
            # Increment download count
            self.file_model.increment_download_count(file_id)
            
            return {
                'filepath': filepath,
                'original_filename': original_filename,
                'file_record': file_record,
                'is_temp': False,
                'decrypted': False
            }, None
    
    def delete_file(self, file_id, user_id=None):
        """Delete a file and its record (handles both encrypted and unencrypted files)"""
        try:
            file_record = self.file_model.get_file_by_id(file_id, user_id)
            if not file_record:
                return False, 'File not found'
            
            stored_filename = file_record[1]
            original_filename = file_record[2]
            filepath = os.path.join(self.upload_folder, stored_filename)
            
            # Remove file from disk (works for both encrypted and unencrypted)
            if os.path.exists(filepath):
                os.remove(filepath)
            
            # Remove from database
            self.file_model.delete_file(file_id)
            
            return True, f'File "{original_filename}" deleted successfully!'
            
        except Exception as e:
            return False, f'Error deleting file: {str(e)}'
    
    def get_user_files(self, user_id):
        """Get all files belonging to a user"""
        return self.file_model.get_user_files(user_id)
