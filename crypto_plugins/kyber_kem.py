"""
Kyber KEM implementation using liboqs (Open Quantum Safe)
Provides post-quantum secure key encapsulation mechanism
"""
from typing import Tuple, Optional
from .base_kem import BaseKEM


class KyberKEM(BaseKEM):
    """Kyber KEM implementation using liboqs"""
    
    def __init__(self, algorithm: str = "Kyber768"):
        """
        Initialize Kyber KEM
        
        Args:
            algorithm: Kyber variant (Kyber512, Kyber768, Kyber1024)
        """
        self.algorithm = algorithm
        self._kem = None
        self._available = False
        
        try:
            import oqs
            self._kem = oqs.KeyEncapsulation(algorithm)
            self._available = True
        except ImportError:
            print(f"⚠️  Warning: liboqs-python not available. Kyber KEM disabled.")
        except Exception as e:
            print(f"⚠️  Warning: Failed to initialize Kyber KEM: {e}")
    
    def get_algorithm_name(self) -> str:
        """Return the name of the KEM algorithm"""
        return self.algorithm
    
    def is_available(self) -> bool:
        """Check if the KEM implementation is available and functional"""
        return self._available and self._kem is not None
    
    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """
        Generate a new Kyber key pair
        
        Returns:
            Tuple[bytes, bytes]: (public_key, private_key)
            
        Raises:
            RuntimeError: If Kyber is not available
        """
        if not self.is_available():
            raise RuntimeError(f"Kyber KEM ({self.algorithm}) is not available")
        
        public_key = self._kem.generate_keypair()
        private_key = self._kem.export_secret_key()
        
        return public_key, private_key
    
    def encapsulate(self, public_key: bytes) -> Tuple[bytes, bytes]:
        """
        Encapsulate a shared secret using the public key
        
        Args:
            public_key: The recipient's public key
            
        Returns:
            Tuple[bytes, bytes]: (ciphertext, shared_secret)
            
        Raises:
            RuntimeError: If Kyber is not available
        """
        if not self.is_available():
            raise RuntimeError(f"Kyber KEM ({self.algorithm}) is not available")
        
        ciphertext, shared_secret = self._kem.encap_secret(public_key)
        
        return ciphertext, shared_secret
    
    def decapsulate(self, ciphertext: bytes, private_key: bytes) -> Optional[bytes]:
        """
        Decapsulate the shared secret using the private key
        
        Args:
            ciphertext: The encapsulated ciphertext
            private_key: The recipient's private key
            
        Returns:
            Optional[bytes]: The shared secret, or None if decapsulation fails
        """
        if not self.is_available():
            return None
        
        try:
            shared_secret = self._kem.decap_secret(ciphertext)
            return shared_secret
        except Exception as e:
            print(f"Decapsulation error: {e}")
            return None
    
    def get_public_key_size(self) -> int:
        """Return the size of public keys in bytes"""
        if not self.is_available():
            return 0
        return self._kem.details['length_public_key']
    
    def get_private_key_size(self) -> int:
        """Return the size of private keys in bytes"""
        if not self.is_available():
            return 0
        return self._kem.details['length_secret_key']
    
    def get_ciphertext_size(self) -> int:
        """Return the size of ciphertext in bytes"""
        if not self.is_available():
            return 0
        return self._kem.details['length_ciphertext']
    
    def get_shared_secret_size(self) -> int:
        """Return the size of shared secret in bytes"""
        if not self.is_available():
            return 0
        return self._kem.details['length_shared_secret']


class MockKEM(BaseKEM):
    """
    Mock KEM for testing and fallback when liboqs is not available
    WARNING: This is NOT secure and should only be used for development/testing
    """
    
    def __init__(self, algorithm: str = "MockKEM"):
        self.algorithm = algorithm
        print("⚠️  WARNING: Using MockKEM - NOT SECURE, DEVELOPMENT ONLY!")
    
    def get_algorithm_name(self) -> str:
        return f"Mock-{self.algorithm}"
    
    def is_available(self) -> bool:
        return True
    
    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """Generate mock keypair (insecure)"""
        import os
        public_key = os.urandom(800)  # Approximate Kyber768 public key size
        private_key = os.urandom(1632)  # Approximate Kyber768 private key size
        return public_key, private_key
    
    def encapsulate(self, public_key: bytes) -> Tuple[bytes, bytes]:
        """Mock encapsulation (insecure)"""
        import os
        ciphertext = os.urandom(768)  # Approximate Kyber768 ciphertext size
        shared_secret = os.urandom(32)  # 256-bit shared secret
        return ciphertext, shared_secret
    
    def decapsulate(self, ciphertext: bytes, private_key: bytes) -> Optional[bytes]:
        """Mock decapsulation (insecure)"""
        import os
        # In mock mode, just return a random shared secret
        # This is obviously insecure but allows testing without liboqs
        return os.urandom(32)
    
    def get_public_key_size(self) -> int:
        return 800
    
    def get_private_key_size(self) -> int:
        return 1632
    
    def get_ciphertext_size(self) -> int:
        return 768
    
    def get_shared_secret_size(self) -> int:
        return 32
