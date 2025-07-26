"""
Enhanced cryptographic utilities for secure file encryption
Uses AES-256-GCM for authenticated encryption
"""
import os
import hashlib
import secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import json

class SecureFileEncryption:
    """Enhanced file encryption with proper key management"""
    
    def __init__(self, master_password=None):
        """Initialize with master password for key derivation"""
        self.master_password = master_password or os.environ.get('ENCRYPTION_MASTER_KEY', 'default-change-in-production')
        
    def _derive_key(self, salt, password=None):
        """Derive encryption key using PBKDF2"""
        password = password or self.master_password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=100000,  # OWASP recommended minimum
            backend=default_backend()
        )
        return kdf.derive(password.encode())
    
    def encrypt_file(self, input_file_path, user_id):
        """
        Encrypt file using AES-256-GCM with authenticated encryption
        Returns encryption metadata for database storage
        """
        try:
            # Generate unique salt and nonce for this file
            salt = os.urandom(16)
            nonce = os.urandom(12)  # GCM recommended nonce size
            
            # Derive unique key for this file
            key = self._derive_key(salt, f"{self.master_password}_{user_id}")
            
            # Read file content
            with open(input_file_path, 'rb') as f:
                plaintext = f.read()
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(nonce),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Encrypt and get authentication tag
            ciphertext = encryptor.update(plaintext) + encryptor.finalize()
            auth_tag = encryptor.tag
            
            # Create encrypted file path
            encrypted_filename = f"enc_{secrets.token_hex(16)}.dat"
            encrypted_path = os.path.join(os.path.dirname(input_file_path), encrypted_filename)
            
            # Write encrypted data (nonce + auth_tag + ciphertext)
            with open(encrypted_path, 'wb') as f:
                f.write(nonce + auth_tag + ciphertext)
            
            # Remove original file for security
            os.remove(input_file_path)
            
            # Return encryption metadata
            return {
                'encrypted_filename': encrypted_filename,
                'salt': base64.b64encode(salt).decode('utf-8'),
                'file_hash': hashlib.sha256(plaintext).hexdigest(),
                'is_encrypted': True
            }
            
        except Exception as e:
            print(f"Encryption error: {e}")
            return None
    
    def decrypt_file(self, encrypted_file_path, salt_b64, user_id, output_path=None):
        """
        Decrypt file using stored salt and user-specific key derivation
        """
        try:
            # Decode salt
            salt = base64.b64decode(salt_b64)
            
            # Derive the same key used for encryption
            key = self._derive_key(salt, f"{self.master_password}_{user_id}")
            
            # Read encrypted data
            with open(encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Extract components
            nonce = encrypted_data[:12]
            auth_tag = encrypted_data[12:28]
            ciphertext = encrypted_data[28:]
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(nonce, auth_tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            # Decrypt and verify authentication
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Write decrypted data if output path specified
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(plaintext)
                return output_path
            else:
                return plaintext  # Return data directly for downloads
                
        except Exception as e:
            print(f"Decryption error: {e}")
            return None
    
    def verify_file_integrity(self, decrypted_data, expected_hash):
        """Verify file integrity using stored hash"""
        actual_hash = hashlib.sha256(decrypted_data).hexdigest()
        return actual_hash == expected_hash

# Backward compatibility with your existing encrypt.py
def encrypt_file_legacy(input_file, output_file):
    """Legacy function for backward compatibility"""
    crypto = SecureFileEncryption()
    result = crypto.encrypt_file(input_file, "default_user")
    if result:
        # Move the encrypted file to the desired output location
        import shutil
        shutil.move(os.path.join(os.path.dirname(input_file), result['encrypted_filename']), output_file)
        return result['salt'], result['file_hash']
    return None, None

def decrypt_file_legacy(salt, file_hash, input_file, output_file):
    """Legacy function for backward compatibility"""
    crypto = SecureFileEncryption()
    return crypto.decrypt_file(input_file, salt, "default_user", output_file)

if __name__ == "__main__":
    # Test the enhanced encryption
    crypto = SecureFileEncryption("test-master-key")
    
    # Test file path
    test_file = "HelloWorld.txt"
    
    if os.path.exists(test_file):
        print("🔒 Testing Enhanced File Encryption...")
        
        # Encrypt
        result = crypto.encrypt_file(test_file, user_id="test_user_123")
        if result:
            print("✅ File encrypted successfully!")
            print(f"📁 Encrypted file: {result['encrypted_filename']}")
            print(f"🧂 Salt: {result['salt'][:20]}...")
            print(f"🔍 Hash: {result['file_hash'][:20]}...")
            
            # Decrypt
            encrypted_path = os.path.join(os.path.dirname(test_file), result['encrypted_filename'])
            decrypted_data = crypto.decrypt_file(
                encrypted_path, 
                result['salt'], 
                "test_user_123"
            )
            
            if decrypted_data:
                print("✅ File decrypted successfully!")
                
                # Verify integrity
                if crypto.verify_file_integrity(decrypted_data, result['file_hash']):
                    print("✅ File integrity verified!")
                else:
                    print("❌ File integrity check failed!")
                    
                # Save decrypted file
                with open("Decrypted_HelloWorld.txt", 'wb') as f:
                    f.write(decrypted_data)
                print("💾 Decrypted file saved as 'Decrypted_HelloWorld.txt'")
            else:
                print("❌ Decryption failed!")
        else:
            print("❌ Encryption failed!")
    else:
        print(f"❌ Test file '{test_file}' not found!")
