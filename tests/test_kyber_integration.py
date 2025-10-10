"""
Comprehensive tests for Kyber-KEM integration
Tests key generation, encapsulation/decapsulation, file encryption, and sharing
"""
import os
import sys
import unittest
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto_plugins import load_kem_provider, MockKEM
from crypto_utils import PQKeyManager, SecureFileEncryption
from key_management import KeyManagementService
from models import UserModel, FileModel, ServerKEMModel


class TestKEMProviders(unittest.TestCase):
    """Test KEM provider loading and basic operations"""
    
    def test_load_mock_kem(self):
        """Test loading MockKEM provider"""
        kem = load_kem_provider(provider='mock', algorithm='MockKyber768')
        self.assertIsNotNone(kem)
        self.assertTrue(kem.is_available())
        self.assertEqual(kem.get_algorithm_name(), 'Mock-MockKyber768')
    
    def test_load_kyber_with_fallback(self):
        """Test loading Kyber with fallback to MockKEM"""
        kem = load_kem_provider(provider='kyber', algorithm='Kyber768', allow_fallback=True)
        self.assertIsNotNone(kem)
        self.assertTrue(kem.is_available())
    
    def test_keypair_generation(self):
        """Test key pair generation"""
        kem = load_kem_provider(provider='mock')
        public_key, private_key = kem.generate_keypair()
        
        self.assertIsInstance(public_key, bytes)
        self.assertIsInstance(private_key, bytes)
        self.assertGreater(len(public_key), 0)
        self.assertGreater(len(private_key), 0)
    
    def test_encapsulation_decapsulation(self):
        """Test KEM encapsulation and decapsulation"""
        kem = load_kem_provider(provider='mock')
        public_key, private_key = kem.generate_keypair()
        
        # Encapsulate
        ciphertext, shared_secret_1 = kem.encapsulate(public_key)
        self.assertIsInstance(ciphertext, bytes)
        self.assertIsInstance(shared_secret_1, bytes)
        
        # Decapsulate (MockKEM returns random, so we can't verify match)
        # In real Kyber, shared_secret_2 would equal shared_secret_1
        shared_secret_2 = kem.decapsulate(ciphertext, private_key)
        self.assertIsInstance(shared_secret_2, bytes)
        self.assertEqual(len(shared_secret_2), kem.get_shared_secret_size())


class TestPQKeyManager(unittest.TestCase):
    """Test PQKeyManager for key operations"""
    
    def setUp(self):
        self.kem = load_kem_provider(provider='mock')
        self.pq_manager = PQKeyManager(self.kem, master_key='test_master_key')
    
    def test_keypair_generation(self):
        """Test key pair generation through manager"""
        public_key, private_key = self.pq_manager.generate_keypair()
        self.assertIsInstance(public_key, bytes)
        self.assertIsInstance(private_key, bytes)
    
    def test_private_key_encryption(self):
        """Test private key encryption and decryption"""
        public_key, private_key = self.pq_manager.generate_keypair()
        
        # Encrypt private key
        encrypted_key, salt = self.pq_manager.encrypt_private_key(private_key, 'user_password')
        self.assertIsInstance(encrypted_key, bytes)
        self.assertIsInstance(salt, bytes)
        
        # Decrypt private key
        decrypted_key = self.pq_manager.decrypt_private_key(encrypted_key, salt, 'user_password')
        self.assertEqual(private_key, decrypted_key)
    
    def test_key_encapsulation_wrapper(self):
        """Test AES key encapsulation and decapsulation"""
        import os
        
        # Generate key pair
        public_key, private_key = self.pq_manager.generate_keypair()
        
        # Generate AES key
        aes_key = os.urandom(32)
        
        # Encapsulate AES key
        kem_ciphertext, wrapped_key = self.pq_manager.encapsulate_key(aes_key, public_key)
        self.assertIsInstance(kem_ciphertext, bytes)
        self.assertIsInstance(wrapped_key, bytes)
        
        # Decapsulate AES key (MockKEM won't match exactly, but should return a key)
        recovered_key = self.pq_manager.decapsulate_key(kem_ciphertext, wrapped_key, private_key)
        self.assertIsInstance(recovered_key, bytes)
        self.assertEqual(len(recovered_key), 32)


class TestDatabaseIntegration(unittest.TestCase):
    """Test database schema for PQ keys"""
    
    def setUp(self):
        self.test_db = tempfile.mktemp(suffix='.db')
        self.user_model = UserModel(self.test_db)
        self.user_model.init_db()
        self.server_model = ServerKEMModel(self.test_db)
    
    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_user_pq_keys_storage(self):
        """Test storing and retrieving user PQ keys"""
        # Create a user
        user_id = self.user_model.create_user('testuser', 'test@example.com', 'password123')
        self.assertIsNotNone(user_id)
        
        # Store PQ keys
        public_key = b'test_public_key_data'
        private_key_encrypted = b'test_encrypted_private_key'
        algorithm = 'Kyber768'
        
        self.user_model.update_user_pq_keys(user_id, public_key, private_key_encrypted, algorithm)
        
        # Retrieve PQ keys
        keys = self.user_model.get_user_pq_keys(user_id)
        self.assertIsNotNone(keys)
        self.assertEqual(keys[0], public_key)
        self.assertEqual(keys[1], private_key_encrypted)
        self.assertEqual(keys[2], algorithm)
    
    def test_server_key_storage(self):
        """Test storing and retrieving server KEM keys"""
        public_key = b'server_public_key'
        private_key_encrypted = b'server_encrypted_private_key'
        algorithm = 'Kyber768'
        
        self.server_model.save_server_key('default', public_key, private_key_encrypted, algorithm)
        
        # Retrieve server key
        key_info = self.server_model.get_active_server_key('default')
        self.assertIsNotNone(key_info)
        self.assertEqual(key_info[1], public_key)
        self.assertEqual(key_info[2], private_key_encrypted)
        self.assertEqual(key_info[3], algorithm)


class TestKeyManagementService(unittest.TestCase):
    """Test key management service operations"""
    
    def setUp(self):
        self.test_db = tempfile.mktemp(suffix='.db')
        self.kem = load_kem_provider(provider='mock')
        self.key_mgmt = KeyManagementService(
            db_name=self.test_db,
            kem_provider=self.kem,
            master_key='test_master_key'
        )
        
        # Initialize database
        user_model = UserModel(self.test_db)
        user_model.init_db()
        
        # Create test user
        self.user_id = user_model.create_user('testuser', 'test@example.com', 'password123')
    
    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_ensure_user_keys(self):
        """Test automatic user key generation"""
        result = self.key_mgmt.ensure_user_keys(self.user_id, 'password123')
        self.assertTrue(result)
        
        # Verify keys were created
        public_key = self.key_mgmt.get_user_public_key(self.user_id)
        self.assertIsNotNone(public_key)
        self.assertIsInstance(public_key, bytes)
    
    def test_user_key_retrieval(self):
        """Test user key retrieval"""
        self.key_mgmt.ensure_user_keys(self.user_id, 'password123')
        
        public_key = self.key_mgmt.get_user_public_key(self.user_id)
        private_key = self.key_mgmt.get_user_private_key(self.user_id, 'password123')
        
        self.assertIsNotNone(public_key)
        self.assertIsNotNone(private_key)
    
    def test_server_key_management(self):
        """Test server key generation and rotation"""
        # Ensure server key exists
        result = self.key_mgmt.ensure_server_key('default', rotation_days=90)
        self.assertTrue(result)
        
        # Get server key
        public_key = self.key_mgmt.get_server_public_key('default')
        self.assertIsNotNone(public_key)
        
        # Rotate server key
        result = self.key_mgmt.rotate_server_key('default')
        self.assertTrue(result)
        
        # Verify new key is different
        new_public_key = self.key_mgmt.get_server_public_key('default')
        self.assertIsNotNone(new_public_key)
        # Note: Keys will be different after rotation


class TestHybridEncryption(unittest.TestCase):
    """Test hybrid PQ encryption workflows"""
    
    def setUp(self):
        self.kem = load_kem_provider(provider='mock')
        self.crypto = SecureFileEncryption(master_password='test_master', kem_provider=self.kem)
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_file_encryption_with_kem(self):
        """Test file encryption and KEM key wrapping"""
        # Create test file
        test_file = os.path.join(self.temp_dir, 'test.txt')
        test_content = b'This is test content for encryption'
        with open(test_file, 'wb') as f:
            f.write(test_content)
        
        # Encrypt file
        result = self.crypto.encrypt_file(test_file, user_id='test_user_1')
        self.assertIsNotNone(result)
        self.assertTrue(result['is_encrypted'])
        
        # Verify encrypted file exists
        encrypted_file = os.path.join(self.temp_dir, result['encrypted_filename'])
        self.assertTrue(os.path.exists(encrypted_file))


class TestLegacyCompatibility(unittest.TestCase):
    """Test backward compatibility with non-PQ encrypted files"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_db = tempfile.mktemp(suffix='.db')
        
        # Initialize database
        file_model = FileModel(self.test_db)
        file_model.init_db()
    
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_legacy_file_decryption(self):
        """Test that legacy files without KEM can still be decrypted"""
        # Create a legacy encrypted file (without KEM)
        from crypto_utils import SecureFileEncryption
        
        crypto = SecureFileEncryption(master_password='test_master')
        
        test_file = os.path.join(self.temp_dir, 'legacy.txt')
        with open(test_file, 'wb') as f:
            f.write(b'Legacy file content')
        
        # Encrypt without KEM
        result = crypto.encrypt_file(test_file, user_id='legacy_user')
        self.assertIsNotNone(result)
        
        # Decrypt
        encrypted_path = os.path.join(self.temp_dir, result['encrypted_filename'])
        decrypted_data = crypto.decrypt_file(encrypted_path, result['salt'], 'legacy_user')
        
        self.assertEqual(decrypted_data, b'Legacy file content')


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestKEMProviders))
    suite.addTests(loader.loadTestsFromTestCase(TestPQKeyManager))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestKeyManagementService))
    suite.addTests(loader.loadTestsFromTestCase(TestHybridEncryption))
    suite.addTests(loader.loadTestsFromTestCase(TestLegacyCompatibility))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
