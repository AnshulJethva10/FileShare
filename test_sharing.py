#!/usr/bin/env python3
"""
Test the complete share workflow to identify the issue
"""

import os
import tempfile
import sqlite3
from secure_sharing import SecureFileSharing

def test_share_creation_and_download():
    """Test the complete share workflow"""
    print("Testing complete share workflow...")
    
    # Create test content
    test_content = b"This is a test file for sharing!\nIt should be decrypted properly.\nSpecial chars: \xf0\x9f\x94\x92"
    print(f"Original content: {test_content}")
    print(f"Original length: {len(test_content)} bytes")
    
    # Create a test file in uploads directory
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
    
    # Create temp file in uploads directory
    import tempfile
    import time
    test_filename = f"test_{int(time.time())}.txt"
    test_file_path = os.path.join(uploads_dir, test_filename)
    
    with open(test_file_path, 'wb') as f:
        f.write(test_content)
    
    try:
        # Add file to database
        conn = sqlite3.connect('file_sharing.db')
        cursor = conn.cursor()
        
        # Make sure files table exists and insert test file
        cursor.execute("""
            INSERT INTO files (filename, original_filename, file_size, file_hash, user_id, upload_date, download_count, is_encrypted, encryption_salt, encryption_method)
            VALUES (?, ?, ?, ?, ?, datetime('now'), 0, 0, NULL, NULL)
        """, (test_filename, 'test_share.txt', len(test_content), 'test_hash', 1))
        
        file_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ Test file added to database with ID: {file_id}")
        
        # Initialize secure sharing
        sharing = SecureFileSharing(upload_folder="uploads")
        
        # Create share
        share_result = sharing.create_share_from_file_id(file_id, user_id=1, expiry_hours=24)
        
        if not share_result['success']:
            print(f"❌ Failed to create share: {share_result['message']}")
            return False
        
        print(f"✅ Share created successfully!")
        print(f"   Share ID: {share_result['share_id']}")
        print(f"   Share URL: {share_result['share_url']}")
        
        # Extract token from URL
        import re
        url_match = re.search(r'#(.+)$', share_result['share_url'])
        if not url_match:
            print("❌ No token found in URL!")
            return False
        
        share_token = url_match.group(1)
        print(f"   Extracted token: {share_token[:30]}...")
        
        # Download the file
        file_info, error = sharing.download_shared_file(share_result['share_id'], share_token)
        
        if error:
            print(f"❌ Download failed: {error}")
            return False
        
        print(f"✅ Download successful!")
        print(f"   Temp file: {file_info['filepath']}")
        print(f"   Original name: {file_info['original_filename']}")
        
        # Read the downloaded file
        with open(file_info['filepath'], 'rb') as f:
            downloaded_content = f.read()
        
        print(f"   Downloaded content length: {len(downloaded_content)} bytes")
        print(f"   Downloaded content: {downloaded_content}")
        
        # Verify content
        if downloaded_content == test_content:
            print("✅ Downloaded content matches original perfectly!")
            return True
        else:
            print("❌ Downloaded content doesn't match!")
            print(f"   Expected: {test_content}")
            print(f"   Got:      {downloaded_content}")
            
            # Let's also check if it's base64 encoded or something
            try:
                import base64
                decoded = base64.b64decode(downloaded_content)
                print(f"   Base64 decoded attempt: {decoded}")
            except:
                print("   Not base64 encoded data")
            
            return False
        
    finally:
        # Cleanup
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
        if 'file_info' in locals() and file_info.get('is_temp') and os.path.exists(file_info['filepath']):
            os.remove(file_info['filepath'])

if __name__ == "__main__":
    test_share_creation_and_download()
