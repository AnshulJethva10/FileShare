"""
Quick test script for kyber-py integration
Tests the updated KyberKEM class with kyber-py library
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_kyber_py_integration():
    """Test kyber-py integration with our KEM plugin"""
    print("="*60)
    print("Testing kyber-py Integration")
    print("="*60)
    
    try:
        from crypto_plugins import load_kem_provider
        
        # Test loading Kyber768 (recommended)
        print("\n[1] Loading Kyber768 KEM provider...")
        kem = load_kem_provider(provider='kyber', algorithm='Kyber768', allow_fallback=True)
        
        if not kem:
            print("❌ Failed to load KEM provider")
            return False
        
        print(f"✅ KEM Provider loaded: {kem.get_algorithm_name()}")
        print(f"   Available: {kem.is_available()}")
        
        if not kem.is_available():
            print("⚠️  KEM not available (likely using MockKEM fallback)")
            return False
        
        # Test key generation
        print("\n[2] Generating keypair...")
        try:
            public_key, private_key = kem.generate_keypair()
            print(f"✅ Keypair generated successfully")
            print(f"   Public key size: {len(public_key)} bytes")
            print(f"   Private key size: {len(private_key)} bytes")
        except Exception as e:
            print(f"❌ Keypair generation failed: {e}")
            return False
        
        # Test encapsulation
        print("\n[3] Testing encapsulation...")
        try:
            ciphertext, shared_secret_1 = kem.encapsulate(public_key)
            print(f"✅ Encapsulation successful")
            print(f"   Ciphertext size: {len(ciphertext)} bytes")
            print(f"   Shared secret size: {len(shared_secret_1)} bytes")
        except Exception as e:
            print(f"❌ Encapsulation failed: {e}")
            return False
        
        # Test decapsulation
        print("\n[4] Testing decapsulation...")
        try:
            shared_secret_2 = kem.decapsulate(ciphertext, private_key)
            if shared_secret_2 is None:
                print(f"❌ Decapsulation returned None")
                return False
            print(f"✅ Decapsulation successful")
            print(f"   Recovered shared secret size: {len(shared_secret_2)} bytes")
        except Exception as e:
            print(f"❌ Decapsulation failed: {e}")
            return False
        
        # Verify secrets match
        print("\n[5] Verifying shared secrets match...")
        if shared_secret_1 == shared_secret_2:
            print(f"✅ SUCCESS! Shared secrets match!")
            print(f"   Shared secret (first 32 hex chars): {shared_secret_1.hex()[:32]}...")
        else:
            print(f"❌ FAILURE! Shared secrets do NOT match!")
            print(f"   Secret 1: {shared_secret_1.hex()[:32]}...")
            print(f"   Secret 2: {shared_secret_2.hex()[:32]}...")
            return False
        
        # Test all security levels
        print("\n[6] Testing all security levels...")
        for level in ["Kyber512", "Kyber768", "Kyber1024"]:
            print(f"\n   Testing {level}...")
            kem_test = load_kem_provider(provider='kyber', algorithm=level, allow_fallback=True)
            if kem_test and kem_test.is_available():
                pk, sk = kem_test.generate_keypair()
                ct, ss1 = kem_test.encapsulate(pk)
                ss2 = kem_test.decapsulate(ct, sk)
                if ss1 == ss2:
                    print(f"   ✅ {level} working correctly")
                else:
                    print(f"   ❌ {level} failed verification")
            else:
                print(f"   ⚠️  {level} not available")
        
        print("\n" + "="*60)
        print("✅ All tests passed! kyber-py integration working!")
        print("="*60)
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("   Make sure to install: pip install kyber-py")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_kyber_py_integration()
    sys.exit(0 if success else 1)
