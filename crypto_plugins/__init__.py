"""
Crypto Plugins Package
Provides modular KEM implementations for post-quantum cryptography
"""
from typing import Optional
from .base_kem import BaseKEM
from .kyber_kem import KyberKEM, MockKEM


def load_kem_provider(provider: str = "kyber", algorithm: str = "Kyber768", 
                      allow_fallback: bool = True) -> Optional[BaseKEM]:
    """
    Load a KEM provider with specified algorithm
    
    Args:
        provider: Provider name ("kyber", "mock")
        algorithm: Algorithm variant (e.g., "Kyber768", "Kyber1024")
        allow_fallback: If True, fall back to MockKEM if provider unavailable
        
    Returns:
        Optional[BaseKEM]: KEM instance or None if unavailable and no fallback
    """
    provider = provider.lower()
    
    if provider == "kyber":
        kem = KyberKEM(algorithm)
        if kem.is_available():
            print(f"✅ Kyber KEM ({algorithm}) loaded successfully")
            return kem
        elif allow_fallback:
            print(f"⚠️  Kyber unavailable, falling back to MockKEM (INSECURE!)")
            return MockKEM(algorithm)
        else:
            print(f"❌ Kyber KEM unavailable and fallback disabled")
            return None
    
    elif provider == "mock":
        print(f"⚠️  Loading MockKEM - FOR TESTING ONLY!")
        return MockKEM(algorithm)
    
    else:
        print(f"❌ Unknown KEM provider: {provider}")
        if allow_fallback:
            print(f"⚠️  Falling back to MockKEM (INSECURE!)")
            return MockKEM(algorithm)
        return None


__all__ = ['BaseKEM', 'KyberKEM', 'MockKEM', 'load_kem_provider']
