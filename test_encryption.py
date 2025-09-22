#!/usr/bin/env python3
"""
Test script to verify encryption/decryption is working correctly
"""

import os
import tempfile
import base64
from crypto_utils import SecureFileEncryption

def test_basic_encryption_decryption():
    """Test basic encrypt_data/decrypt_data cycle"""
    print("Testing basic encryption/decryption...")
    
    crypto = SecureFileEncryption()
    
    # Test data
    test_content = b"Hello, this is a test file!\nWith some special chars: \xf0\x9f\x94\x92\n"
    print(f"Original content: {test_content}")
    print(f"Original length: {len(test_content)} bytes")
    
    # Generate a key
    share_key = crypto.generate_share_key()
    print(f"Generated key length: {len(share_key)} bytes")
    
    # Encrypt data
    encrypted_data, salt_b64, nonce_b64 = crypto.encrypt_data(test_content, share_key)
    if encrypted_data is None:
        print("❌ Encryption failed!")
        return False
    
    print(f"✅ Encryption successful!")
    print(f"   Encrypted length: {len(encrypted_data)} bytes")
    print(f"   Salt: {salt_b64}")
    print(f"   Nonce: {nonce_b64}")
    
    # Decrypt data
    decrypted_data = crypto.decrypt_data(encrypted_data, share_key, salt_b64, nonce_b64)
    if decrypted_data is None:
        print("❌ Decryption failed!")
        return False
    
    print(f"✅ Decryption successful!")
    print(f"   Decrypted content: {decrypted_data}")
    print(f"   Decrypted length: {len(decrypted_data)} bytes")
    
    # Verify content matches
    if decrypted_data == test_content:
        print("✅ Content matches perfectly!")
        return True
    else:
        print("❌ Content doesn't match!")
        print(f"   Expected: {test_content}")
        print(f"   Got:      {decrypted_data}")
        return False

def test_file_to_temp_file_cycle():
    """Test creating a temp file from decrypted data"""
    print("\n" + "="*50)
    print("Testing temp file creation...")
    
    crypto = SecureFileEncryption()
    
    # Create test content
    test_content = b"This is test file content!\nLine 2 with unicode: \xf0\x9f\x91\x8d\n"
    
    # Encrypt
    share_key = crypto.generate_share_key()
    encrypted_data, salt_b64, nonce_b64 = crypto.encrypt_data(test_content, share_key)
    
    # Decrypt
    decrypted_data = crypto.decrypt_data(encrypted_data, share_key, salt_b64, nonce_b64)
    
    if decrypted_data != test_content:
        print("❌ Decryption doesn't match original!")
        return False
    
    # Create temp file (simulating download process)
    import tempfile
    temp_fd, temp_path = tempfile.mkstemp(suffix="_test_download.txt")
    
    try:
        with os.fdopen(temp_fd, 'wb') as temp_file:
            temp_file.write(decrypted_data)
        
        print(f"✅ Temp file created: {temp_path}")
        
        # Read it back
        with open(temp_path, 'rb') as f:
            read_back_data = f.read()
        
        if read_back_data == test_content:
            print("✅ Temp file read back successfully!")
            print(f"   Content: {read_back_data}")
            return True
        else:
            print("❌ Temp file content doesn't match!")
            return False
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    print("Starting encryption/decryption tests...")
    
    success1 = test_basic_encryption_decryption()
    success2 = test_file_to_temp_file_cycle()
    
    if success1 and success2:
        print("\n🎉 All basic tests passed!")
    else:
        print("\n❌ Some tests failed!")
