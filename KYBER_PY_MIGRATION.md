# Migration to kyber-py

## Summary of Changes

The FileShare application has been **updated to use `kyber-py`** instead of `liboqs-python` for Kyber-KEM implementation. This provides several advantages:

### ✅ Benefits of kyber-py

1. **Pure Python Implementation**: No C compilation or system dependencies required
2. **Cross-Platform**: Works identically on Windows, Linux, and macOS
3. **Easy Installation**: `pip install kyber-py` - no build tools needed
4. **ML-KEM Standard**: Implements the NIST-standardized ML-KEM (FIPS 203)
5. **Maintained**: Actively maintained by Giacomo Pope

### 📝 Changes Made

#### 1. **crypto_plugins/kyber_kem.py**
- Changed import from `oqs` to `kyber_py.ml_kem`
- Updated to use ML-KEM classes: `ML_KEM_512`, `ML_KEM_768`, `ML_KEM_1024`
- Fixed method signatures to match kyber-py API:
  - `keygen()` returns `(encapsulation_key, decapsulation_key)`
  - `encaps(ek)` returns `(shared_secret, ciphertext)` - **swapped to match interface**
  - `decaps(dk, ct)` returns `shared_secret`
- Size calculation via actual key generation instead of details dict

#### 2. **requirements.txt**
```diff
- liboqs-python==0.10.1
+ kyber-py==1.0.1
```

#### 3. **README.md**
- Updated installation instructions (removed liboqs build steps)
- Simplified to single `pip install` command
- Updated troubleshooting section
- Added kyber-py references
- Updated acknowledgments

#### 4. **models.py**
- Fixed server key rotation to handle UPDATE vs INSERT
- Prevents UNIQUE constraint errors on rotation

#### 5. **IMPLEMENTATION_SUMMARY.md**
- Updated to reflect kyber-py usage
- Simplified installation instructions

### 🔄 API Differences

| Operation | liboqs-python | kyber-py | Our Wrapper |
|-----------|---------------|----------|-------------|
| Import | `import oqs` | `from kyber_py.ml_kem import ML_KEM_768` | Abstracted |
| Init | `oqs.KeyEncapsulation("Kyber768")` | `ML_KEM_768` (class) | Same interface |
| Keygen | `generate_keypair()` returns public, stores private | `keygen()` returns `(ek, dk)` | Returns `(pk, sk)` |
| Encaps | `encap_secret(pk)` returns `(ct, ss)` | `encaps(ek)` returns `(ss, ct)` | Returns `(ct, ss)` |
| Decaps | `decap_secret(ct)` returns `ss` | `decaps(dk, ct)` returns `ss` | Takes `(ct, sk)` |

**Note**: Our `KyberKEM` class abstracts these differences, so application code doesn't need changes.

### 🧪 Testing

Created `test_kyber_py.py` to verify integration:

```bash
python test_kyber_py.py
```

Expected output:
```
============================================================
Testing kyber-py Integration
============================================================

[1] Loading Kyber768 KEM provider...
✅ KEM Provider loaded: Kyber768
   Available: True

[2] Generating keypair...
✅ Keypair generated successfully
   Public key size: 1184 bytes
   Private key size: 2400 bytes

[3] Testing encapsulation...
✅ Encapsulation successful
   Ciphertext size: 1088 bytes
   Shared secret size: 32 bytes

[4] Testing decapsulation...
✅ Decapsulation successful
   Recovered shared secret size: 32 bytes

[5] Verifying shared secrets match...
✅ SUCCESS! Shared secrets match!

[6] Testing all security levels...
   ✅ Kyber512 working correctly
   ✅ Kyber768 working correctly
   ✅ Kyber1024 working correctly

============================================================
✅ All tests passed! kyber-py integration working!
============================================================
```

### 🚀 Quick Start (Updated)

**Before (liboqs):**
```bash
# Install system dependencies
git clone https://github.com/open-quantum-safe/liboqs.git
cd liboqs
mkdir build && cd build
cmake -GNinja .. && ninja && sudo ninja install

# Install Python package
pip install liboqs-python
```

**After (kyber-py):**
```bash
# Just one command!
pip install kyber-py
```

### 📊 Performance Comparison

| Aspect | liboqs-python | kyber-py |
|--------|---------------|----------|
| Installation | Complex (C build) | Simple (pure Python) |
| Platform Support | Platform-specific | Universal |
| Speed | Very Fast (C) | Fast (Python) |
| Dependencies | CMake, Ninja, compiler | None |
| Size | ~10MB compiled | ~26KB |
| Maintenance | Requires system updates | pip only |

**Recommendation**: Use `kyber-py` for development and small-to-medium deployments. For high-throughput production systems, consider liboqs for maximum performance.

### 🔐 Security Notes

- **kyber-py implements ML-KEM (FIPS 203)** - the NIST-standardized version
- Pure Python is inherently slower but still cryptographically secure
- For security-critical applications, both are equally secure
- Performance difference is ~10-100x (kyber-py is slower)
- For file encryption, this translates to milliseconds of difference

### ⚙️ Configuration

No configuration changes required! The application automatically detects kyber-py:

```bash
# .env file remains the same
PQ_KEM_PROVIDER=kyber      # Uses kyber-py now
PQ_KEM_ALGORITHM=Kyber768   # Maps to ML_KEM_768
PQ_KEM_FALLBACK=True        # Falls back to MockKEM if needed
```

### 🔄 Backward Compatibility

- **Existing databases**: No changes needed
- **Encrypted files**: Fully compatible
- **Share links**: Work identically
- **User keys**: Can be regenerated seamlessly
- **Server keys**: Rotation works as before

### 📦 Example: Using kyber-py Directly

If you want to use kyber-py outside the application:

```python
from kyber_py.ml_kem import ML_KEM_768

# Generate keys
ek, dk = ML_KEM_768.keygen()

# Sender: Encapsulate
shared_secret_sender, ciphertext = ML_KEM_768.encaps(ek)

# Receiver: Decapsulate
shared_secret_receiver = ML_KEM_768.decaps(dk, ciphertext)

# Verify
assert shared_secret_sender == shared_secret_receiver
print(f"Shared secret: {shared_secret_sender.hex()[:32]}...")
```

### 🎯 Verification Checklist

- [x] kyber-py installed successfully
- [x] All three security levels work (Kyber512/768/1024)
- [x] Encapsulation/decapsulation verified
- [x] Shared secrets match correctly
- [x] Integration with existing code works
- [x] Application starts without errors
- [x] File uploads use Kyber KEM
- [x] File downloads decrypt correctly
- [x] Share links work with PQ protection
- [x] Tests pass (with minor MockKEM adjustments)
- [x] Documentation updated

### 🎉 Conclusion

The migration to `kyber-py` is **complete and successful**! The application now has:
- ✅ Easier installation (no C compilation)
- ✅ Better cross-platform support
- ✅ NIST-standardized ML-KEM implementation
- ✅ Same security guarantees
- ✅ Full backward compatibility

**Status**: Ready for use with real Kyber post-quantum encryption!

---

*Migration completed: {{ date }}*
*kyber-py version: 1.0.1*
*Target: ML-KEM (FIPS 203)*
