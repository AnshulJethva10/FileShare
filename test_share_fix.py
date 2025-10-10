"""
Test share creation after fixing the unpacking issue
"""
import os
import sys
import tempfile

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_share_creation():
    """Test that share creation works with the fix"""
    print("="*60)
    print("Testing Share Creation Fix")
    print("="*60)
    
    try:
        from models import FileModel, UserModel
        from secure_sharing import SecureFileSharing
        from crypto_plugins import load_kem_provider
        
        # Create temp database
        test_db = tempfile.mktemp(suffix='.db')
        test_uploads = tempfile.mkdtemp()
        
        print("\n[1] Initializing database...")
        user_model = UserModel(test_db)
        user_model.init_db()
        
        file_model = FileModel(test_db)
        file_model.init_db()
        
        # Create test user
        user_id = user_model.create_user('testuser', 'test@example.com', 'password123')
        print(f"✅ Created test user (ID: {user_id})")
        
        # Create test file record
        print("\n[2] Creating test file record...")
        test_file_path = os.path.join(test_uploads, 'test.txt')
        with open(test_file_path, 'w') as f:
            f.write('Test file content for sharing')
        
        file_id = file_model.add_file(
            filename='test.txt',
            original_filename='test.txt',
            file_size=100,
            file_hash='abc123',
            user_id=user_id,
            is_encrypted=False,
            encryption_method='none'
        )
        print(f"✅ Created test file record (ID: {file_id})")
        
        # Initialize secure sharing (with or without KEM)
        print("\n[3] Initializing secure sharing...")
        kem = load_kem_provider(provider='mock', allow_fallback=True)
        secure_sharing = SecureFileSharing(
            upload_folder=test_uploads,
            db_name=test_db,
            kem_provider=kem,
            key_mgmt=None  # Not testing key management here
        )
        print("✅ Secure sharing initialized")
        
        # Test share creation
        print("\n[4] Creating share from file ID...")
        try:
            result = secure_sharing.create_share_from_file_id(
                file_id=file_id,
                user_id=user_id,
                expiry_hours=24,
                max_downloads=5
            )
            
            if result['success']:
                print(f"✅ Share created successfully!")
                print(f"   Share ID: {result['share_id']}")
                print(f"   Share URL: {result['share_url']}")
                print(f"   Expiry: {result['expiry']}")
            else:
                print(f"❌ Share creation failed: {result['message']}")
                return False
                
        except Exception as e:
            print(f"❌ Exception during share creation: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Cleanup
        print("\n[5] Cleaning up...")
        import shutil
        if os.path.exists(test_db):
            os.remove(test_db)
        if os.path.exists(test_uploads):
            shutil.rmtree(test_uploads)
        print("✅ Cleanup complete")
        
        print("\n" + "="*60)
        print("✅ Share creation test PASSED!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_share_creation()
    sys.exit(0 if success else 1)
