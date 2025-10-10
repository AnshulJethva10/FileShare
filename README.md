# FileShare - Post-Quantum Secure File Sharing Application

A Flask-based file sharing application with **Kyber-KEM post-quantum encryption** for future-proof security against quantum adversaries.

## 🔐 Features

### Core Features
- **Hybrid Post-Quantum Encryption**: AES-256-GCM with Kyber-KEM key encapsulation
- **User Authentication**: Secure signup/login system
- **File Encryption**: All files encrypted at rest with per-user keys
- **Secure File Sharing**: Generate time-limited share links with embedded encryption keys
- **Key Management**: Automatic user and server key pair generation with rotation support
- **Legacy Compatibility**: Seamless support for files encrypted before PQ implementation

### Security Architecture
- **Hybrid PQ Design**: Combines battle-tested AES-256-GCM with post-quantum Kyber-KEM
- **Per-User Keys**: Each user gets their own Kyber key pair for file encryption
- **Server Keys**: Static server key pairs for securing share links
- **Key Rotation**: Configurable automatic rotation of server keys
- **Private Key Protection**: User private keys encrypted with password-derived keys

## 📋 Requirements

- Python 3.8+
- liboqs library (for Kyber support)
- Flask 3.0+
- cryptography 41.0+

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd FileShare
```

### 2. Install Dependencies

#### Option A: With Kyber Support (Recommended)

**On Linux/macOS:**
```bash
# Install liboqs system library
git clone https://github.com/open-quantum-safe/liboqs.git
cd liboqs
mkdir build && cd build
cmake -GNinja ..
ninja
sudo ninja install

# Install Python dependencies
cd ../../FileShare
pip install -r requirements.txt
```

**On Windows:**
```powershell
# Download prebuilt liboqs from https://github.com/open-quantum-safe/liboqs/releases
# Or build from source using Visual Studio

# Install Python dependencies
pip install -r requirements.txt
```

**Note**: If liboqs installation fails, the application will automatically fall back to MockKEM mode (development only).

#### Option B: Without Kyber (Legacy Mode)
```bash
pip install Flask==3.0.0 Werkzeug==3.0.1 python-dotenv==1.0.1 cryptography==41.0.7
```

### 3. Configuration

Create a `.env` file in the project root:

```bash
# Core Settings
SECRET_KEY=your-secret-key-change-this
FLASK_ENV=development
FLASK_DEBUG=True

# Database
DB_NAME=file_sharing.db

# Encryption
ENABLE_ENCRYPTION=True
ENCRYPTION_MASTER_KEY=your-master-encryption-key-change-this

# Post-Quantum Settings
PQ_KEM_PROVIDER=kyber  # Options: kyber, mock, none
PQ_KEM_ALGORITHM=Kyber768  # Options: Kyber512, Kyber768, Kyber1024
PQ_KEM_FALLBACK=True  # Fall back to MockKEM if Kyber unavailable
PQ_STATIC_KEY_ROTATION_DAYS=90  # Rotate server keys every 90 days
PQ_ENABLE_SHARE_LINKS=True
PQ_ENABLE_USER_KEYS=True

# File Limits
MAX_CONTENT_LENGTH=16777216  # 16MB
MAX_FILES_PER_USER=100
MAX_STORAGE_PER_USER=104857600  # 100MB

# Server
HOST=127.0.0.1
PORT=5000
```

### 4. Initialize Database

The database is automatically initialized on first run. No manual steps required.

### 5. Run the Application

```bash
python app.py
```

Access the application at `http://127.0.0.1:5000`

Default admin credentials:
- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Change these immediately in production!**

## 🔑 Kyber-KEM Configuration Guide

### Understanding the PQ Settings

#### `PQ_KEM_PROVIDER`
- **`kyber`**: Use real Kyber implementation via liboqs (production)
- **`mock`**: Use MockKEM for development/testing (NOT SECURE)
- **`none`**: Disable PQ encryption entirely (legacy AES-256-GCM only)

#### `PQ_KEM_ALGORITHM`
- **`Kyber512`**: NIST Security Level 1 (~128-bit security)
- **`Kyber768`**: NIST Security Level 3 (~192-bit security) - **Recommended**
- **`Kyber1024`**: NIST Security Level 5 (~256-bit security)

#### `PQ_KEM_FALLBACK`
- **`True`**: Fall back to MockKEM if Kyber unavailable (development)
- **`False`**: Fail hard if Kyber unavailable (production recommended)

### Production Recommendations

```bash
PQ_KEM_PROVIDER=kyber
PQ_KEM_ALGORITHM=Kyber768
PQ_KEM_FALLBACK=False
PQ_STATIC_KEY_ROTATION_DAYS=90
```

## 🔄 Key Management & Rotation

### User Keys
- Generated automatically on first login/signup
- Private keys encrypted with user password
- Stored securely in database

### Server Keys
- Generated automatically on application startup
- Used to protect share link encryption keys
- Automatically rotated based on `PQ_STATIC_KEY_ROTATION_DAYS`

### Manual Key Rotation

To force server key rotation, you can add an admin route or use Python:

```python
from key_management import KeyManagementService
from crypto_plugins import load_kem_provider

kem = load_kem_provider('kyber', 'Kyber768')
key_mgmt = KeyManagementService('file_sharing.db', kem, 'your-master-key')
key_mgmt.rotate_server_key('default')
```

## 📊 How It Works

### Upload Flow with Kyber-KEM

1. **User uploads file**
2. **Generate AES-256 key** from user password + salt
3. **Encrypt file** with AES-256-GCM
4. **Encapsulate AES key** using user's Kyber public key
5. **Store**:
   - Encrypted file on disk
   - Kyber ciphertext in database
   - Salt and metadata

### Download Flow with Kyber-KEM

1. **User requests file**
2. **Retrieve Kyber ciphertext** from database
3. **Decrypt user's private key** with password
4. **Decapsulate** to recover AES key
5. **Decrypt file** with recovered AES key
6. **Serve file** to user

### Share Link Flow

1. **Create share** for existing file
2. **Generate unique share key**
3. **Encrypt file** with share key
4. **Encapsulate share key** with server's Kyber public key
5. **Generate URL** with embedded token
6. **Download**: Decapsulate share key → decrypt file

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python tests/test_kyber_integration.py

# Or using pytest
pytest tests/ -v
```

Test coverage includes:
- ✅ KEM provider loading and initialization
- ✅ Key pair generation and storage
- ✅ Encapsulation/decapsulation operations
- ✅ Hybrid encryption workflows
- ✅ File upload/download with PQ
- ✅ Secure sharing with Kyber
- ✅ Legacy compatibility
- ✅ Key rotation
- ✅ Database migrations

## 🏗️ Architecture

```
FileShare/
├── app.py                 # Application entry point
├── __init__.py           # App factory with KEM initialization
├── config.py             # Configuration including PQ settings
├── models.py             # Database models (Users, Files, Server Keys)
├── crypto_utils.py       # Encryption utilities + PQKeyManager
├── key_management.py     # User/server key management service
├── services.py           # File service with hybrid PQ encryption
├── secure_sharing.py     # Secure sharing with Kyber support
├── routes.py             # Main routes
├── auth_routes.py        # Authentication routes
├── sharing_routes.py     # Sharing routes
├── crypto_plugins/       # KEM plugin architecture
│   ├── __init__.py      # Plugin loader
│   ├── base_kem.py      # Abstract KEM interface
│   └── kyber_kem.py     # Kyber implementation + MockKEM
├── tests/                # Comprehensive test suite
│   ├── __init__.py
│   └── test_kyber_integration.py
└── uploads/              # Encrypted file storage
```

## 🔒 Security Considerations

### Post-Quantum Security
- **Kyber**: NIST-standardized post-quantum KEM (ML-KEM)
- **Hybrid Design**: Maintains classical security while adding PQ protection
- **Forward Secrecy**: Per-file and per-share encryption keys

### Best Practices
1. **Always use HTTPS** in production
2. **Change default credentials** immediately
3. **Set strong `ENCRYPTION_MASTER_KEY`** (256-bit entropy minimum)
4. **Enable `PQ_KEM_FALLBACK=False`** in production
5. **Regularly rotate server keys**
6. **Monitor key rotation logs**

### Threat Model
- ✅ Protected against quantum computer attacks on key exchange
- ✅ Protected against classical attacks (AES-256-GCM)
- ✅ Forward secrecy for individual files and shares
- ⚠️ Private keys still require user password strength
- ⚠️ Server compromise still exposes server static keys

## 🐛 Troubleshooting

### Kyber Not Available
**Error**: "Kyber KEM unavailable and fallback disabled"

**Solutions**:
1. Install liboqs library (see installation section)
2. Enable fallback: `PQ_KEM_FALLBACK=True`
3. Use MockKEM: `PQ_KEM_PROVIDER=mock` (development only)

### Legacy Files Not Working
**Issue**: Old files can't be decrypted after PQ upgrade

**Solution**: The application automatically handles legacy files. If issues persist:
- Check encryption method in database: should be "AES-256-GCM" for legacy
- Ensure `ENCRYPTION_MASTER_KEY` hasn't changed
- Check database migrations ran successfully

### Performance Issues
**Issue**: Slow uploads/downloads with Kyber

**Solutions**:
- Use Kyber768 instead of Kyber1024 (balanced security/performance)
- Ensure liboqs compiled with optimizations
- Consider caching decrypted private keys in memory (security tradeoff)

## 📝 License

[Your License Here]

## 🤝 Contributing

Contributions welcome! Please ensure:
- All tests pass
- New features include tests
- Code follows existing style
- PQ security considerations documented

## 📚 References

- [NIST PQC Standardization](https://csrc.nist.gov/projects/post-quantum-cryptography)
- [Open Quantum Safe](https://openquantumsafe.org/)
- [Kyber Specification](https://pq-crystals.org/kyber/)
- [ML-KEM (FIPS 203)](https://csrc.nist.gov/pubs/fips/203/final)

## 🙏 Acknowledgments

- Open Quantum Safe project for liboqs
- CRYSTALS-Kyber team
- Flask and cryptography library maintainers

---

**⚡ Built with quantum resistance in mind ⚡**
