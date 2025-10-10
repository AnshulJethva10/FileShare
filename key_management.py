"""
Key Management Utilities for Post-Quantum Cryptography
Handles user key pair generation, storage, and server key rotation
"""
import os
import base64
from typing import Optional, Tuple
from models import UserModel, ServerKEMModel
from crypto_utils import PQKeyManager
from crypto_plugins import BaseKEM


class KeyManagementService:
    """Service for managing user and server PQ keys"""
    
    def __init__(self, db_name: str, kem_provider: Optional[BaseKEM], master_key: str):
        self.db_name = db_name
        self.user_model = UserModel(db_name)
        self.server_model = ServerKEMModel(db_name)
        self.pq_manager = PQKeyManager(kem_provider, master_key) if kem_provider else None
        self.kem = kem_provider
    
    def ensure_user_keys(self, user_id: int, user_password: str) -> bool:
        """
        Ensure user has PQ keys, generate if not present
        Returns True if keys exist or were generated successfully
        """
        if not self.pq_manager or not self.kem:
            return False
        
        # Check if user already has keys
        existing_keys = self.user_model.get_user_pq_keys(user_id)
        if existing_keys and existing_keys[0] is not None:  # pq_public_key exists
            return True
        
        try:
            # Generate new key pair
            public_key, private_key = self.pq_manager.generate_keypair()
            
            # Encrypt private key with user password
            encrypted_private_key, salt = self.pq_manager.encrypt_private_key(private_key, user_password)
            
            # Store keys in database (combine salt with encrypted private key for storage)
            private_key_blob = salt + encrypted_private_key
            
            self.user_model.update_user_pq_keys(
                user_id=user_id,
                public_key=public_key,
                private_key_encrypted=private_key_blob,
                algorithm=self.kem.get_algorithm_name()
            )
            
            print(f"✅ Generated PQ keys for user {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate user keys: {e}")
            return False
    
    def get_user_public_key(self, user_id: int) -> Optional[bytes]:
        """Get user's public key"""
        keys = self.user_model.get_user_pq_keys(user_id)
        if keys and keys[0]:
            return keys[0]  # pq_public_key
        return None
    
    def get_user_private_key(self, user_id: int, user_password: str) -> Optional[bytes]:
        """
        Get and decrypt user's private key
        """
        if not self.pq_manager:
            return None
        
        keys = self.user_model.get_user_pq_keys(user_id)
        if not keys or not keys[1]:  # pq_private_key_encrypted
            return None
        
        try:
            # Extract salt and encrypted data
            private_key_blob = keys[1]
            salt = private_key_blob[:16]
            encrypted_private_key = private_key_blob[16:]
            
            # Decrypt private key
            private_key = self.pq_manager.decrypt_private_key(
                encrypted_private_key, salt, user_password
            )
            
            return private_key
            
        except Exception as e:
            print(f"❌ Failed to decrypt private key: {e}")
            return None
    
    def ensure_server_key(self, key_id: str = 'default', rotation_days: int = 90) -> bool:
        """
        Ensure server has an active KEM key, generate if needed or rotation required
        """
        if not self.pq_manager or not self.kem:
            return False
        
        # Check if rotation is needed
        if not self.server_model.check_key_rotation_needed(key_id, rotation_days):
            return True  # Key exists and is still valid
        
        try:
            # Generate new server key pair
            public_key, private_key = self.pq_manager.generate_keypair()
            
            # Encrypt private key with master key (using empty password since it's server key)
            encrypted_private_key, salt = self.pq_manager.encrypt_private_key(
                private_key, "server_static_key"
            )
            
            # Combine salt with encrypted private key
            private_key_blob = salt + encrypted_private_key
            
            # Save to database
            self.server_model.save_server_key(
                key_id=key_id,
                public_key=public_key,
                private_key_encrypted=private_key_blob,
                algorithm=self.kem.get_algorithm_name()
            )
            
            print(f"✅ Generated/rotated server KEM key: {key_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate server key: {e}")
            return False
    
    def get_server_public_key(self, key_id: str = 'default') -> Optional[bytes]:
        """Get server's active public key"""
        key_info = self.server_model.get_active_server_key(key_id)
        if key_info:
            return key_info[1]  # public_key
        return None
    
    def get_server_private_key(self, key_id: str = 'default') -> Optional[bytes]:
        """Get and decrypt server's private key"""
        if not self.pq_manager:
            return None
        
        key_info = self.server_model.get_active_server_key(key_id)
        if not key_info:
            return None
        
        try:
            # Extract salt and encrypted data
            private_key_blob = key_info[2]  # private_key_encrypted
            salt = private_key_blob[:16]
            encrypted_private_key = private_key_blob[16:]
            
            # Decrypt private key
            private_key = self.pq_manager.decrypt_private_key(
                encrypted_private_key, salt, "server_static_key"
            )
            
            return private_key
            
        except Exception as e:
            print(f"❌ Failed to decrypt server private key: {e}")
            return None
    
    def rotate_server_key(self, key_id: str = 'default') -> bool:
        """Force rotation of server key"""
        if not self.pq_manager or not self.kem:
            return False
        
        try:
            # Generate new key pair
            public_key, private_key = self.pq_manager.generate_keypair()
            
            # Encrypt private key
            encrypted_private_key, salt = self.pq_manager.encrypt_private_key(
                private_key, "server_static_key"
            )
            
            # Combine salt with encrypted private key
            private_key_blob = salt + encrypted_private_key
            
            # Save to database (this will deactivate old keys)
            self.server_model.save_server_key(
                key_id=key_id,
                public_key=public_key,
                private_key_encrypted=private_key_blob,
                algorithm=self.kem.get_algorithm_name()
            )
            
            print(f"✅ Rotated server KEM key: {key_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to rotate server key: {e}")
            return False
