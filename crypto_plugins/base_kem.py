"""
Base interface for Key Encapsulation Mechanism (KEM) plugins
Provides abstract class that all KEM implementations must follow
"""
from abc import ABC, abstractmethod
from typing import Tuple, Optional


class BaseKEM(ABC):
    """Abstract base class for KEM implementations"""
    
    @abstractmethod
    def get_algorithm_name(self) -> str:
        """Return the name of the KEM algorithm"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the KEM implementation is available and functional"""
        pass
    
    @abstractmethod
    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """
        Generate a new KEM key pair
        
        Returns:
            Tuple[bytes, bytes]: (public_key, private_key)
        """
        pass
    
    @abstractmethod
    def encapsulate(self, public_key: bytes) -> Tuple[bytes, bytes]:
        """
        Encapsulate a shared secret using the public key
        
        Args:
            public_key: The recipient's public key
            
        Returns:
            Tuple[bytes, bytes]: (ciphertext, shared_secret)
        """
        pass
    
    @abstractmethod
    def decapsulate(self, ciphertext: bytes, private_key: bytes) -> Optional[bytes]:
        """
        Decapsulate the shared secret using the private key
        
        Args:
            ciphertext: The encapsulated ciphertext
            private_key: The recipient's private key
            
        Returns:
            Optional[bytes]: The shared secret, or None if decapsulation fails
        """
        pass
    
    @abstractmethod
    def get_public_key_size(self) -> int:
        """Return the size of public keys in bytes"""
        pass
    
    @abstractmethod
    def get_private_key_size(self) -> int:
        """Return the size of private keys in bytes"""
        pass
    
    @abstractmethod
    def get_ciphertext_size(self) -> int:
        """Return the size of ciphertext in bytes"""
        pass
    
    @abstractmethod
    def get_shared_secret_size(self) -> int:
        """Return the size of shared secret in bytes"""
        pass
