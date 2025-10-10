"""
Kyber KEM implementation using kyber-py (ML-KEM)
Provides post-quantum secure key encapsulation mechanism
"""
from typing import Tuple, Optional
from .base_kem import BaseKEM


class KyberKEM(BaseKEM):
    """Kyber KEM implementation using kyber-py (ML-KEM standard)"""
    
    def __init__(self, algorithm: str = "Kyber768"):
        """
        Initialize Kyber KEM
        
        Args:
            algorithm: Kyber variant (Kyber512, Kyber768, Kyber1024)
                      Maps to ML-KEM-512, ML-KEM-768, ML-KEM-1024
        """
        self.algorithm = algorithm
        self._kem = None
        self._available = False
        
        # Map algorithm names to ML-KEM classes
        algorithm_map = {
            "Kyber512": "ML_KEM_512",
            "Kyber768": "ML_KEM_768",
            "Kyber1024": "ML_KEM_1024"
        }
        
        try:
            from kyber_py.ml_kem import ML_KEM_512, ML_KEM_768, ML_KEM_1024
            
            kem_classes = {
                "ML_KEM_512": ML_KEM_512,
                "ML_KEM_768": ML_KEM_768,
                "ML_KEM_1024": ML_KEM_1024
            }
            
            ml_kem_name = algorithm_map.get(algorithm)
            if ml_kem_name:
                self._kem = kem_classes[ml_kem_name]
                self._available = True
                
                # Get size information
                # Generate temporary keys to determine sizes
                temp_ek, temp_dk = self._kem.keygen()
                temp_ss, temp_ct = self._kem.encaps(temp_ek)
                
                self._public_key_size = len(temp_ek)
                self._private_key_size = len(temp_dk)
                self._ciphertext_size = len(temp_ct)
                self._shared_secret_size = len(temp_ss)
            else:
                print(f"⚠️  Warning: Unknown algorithm {algorithm}")
                
        except ImportError:
            print(f"⚠️  Warning: kyber-py not available. Kyber KEM disabled.")
            print(f"    Install with: pip install kyber-py")
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
            Tuple[bytes, bytes]: (encapsulation_key/public_key, decapsulation_key/private_key)
            
        Raises:
            RuntimeError: If Kyber is not available
        """
        if not self.is_available():
            raise RuntimeError(f"Kyber KEM ({self.algorithm}) is not available")
        
        # kyber-py returns (encapsulation_key, decapsulation_key)
        encapsulation_key, decapsulation_key = self._kem.keygen()
        
        return encapsulation_key, decapsulation_key
    
    def encapsulate(self, public_key: bytes) -> Tuple[bytes, bytes]:
        """
        Encapsulate a shared secret using the public key
        
        Args:
            public_key: The recipient's encapsulation key (public key)
            
        Returns:
            Tuple[bytes, bytes]: (ciphertext, shared_secret)
            
        Raises:
            RuntimeError: If Kyber is not available
        """
        if not self.is_available():
            raise RuntimeError(f"Kyber KEM ({self.algorithm}) is not available")
        
        # kyber-py returns (shared_secret, ciphertext) - we swap to match our interface
        shared_secret, ciphertext = self._kem.encaps(public_key)
        
        return ciphertext, shared_secret
    
    def decapsulate(self, ciphertext: bytes, private_key: bytes) -> Optional[bytes]:
        """
        Decapsulate the shared secret using the private key
        
        Args:
            ciphertext: The encapsulated ciphertext
            private_key: The recipient's decapsulation key (private key)
            
        Returns:
            Optional[bytes]: The shared secret, or None if decapsulation fails
        """
        if not self.is_available():
            return None
        
        try:
            # kyber-py expects (decapsulation_key, ciphertext)
            shared_secret = self._kem.decaps(private_key, ciphertext)
            return shared_secret
        except Exception as e:
            print(f"Decapsulation error: {e}")
            return None
    
    def get_public_key_size(self) -> int:
        """Return the size of public keys in bytes"""
        if not self.is_available():
            return 0
        return self._public_key_size
    
    def get_private_key_size(self) -> int:
        """Return the size of private keys in bytes"""
        if not self.is_available():
            return 0
        return self._private_key_size
    
    def get_ciphertext_size(self) -> int:
        """Return the size of ciphertext in bytes"""
        if not self.is_available():
            return 0
        return self._ciphertext_size
    
    def get_shared_secret_size(self) -> int:
        """Return the size of shared secret in bytes"""
        if not self.is_available():
            return 0
        return self._shared_secret_size


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
