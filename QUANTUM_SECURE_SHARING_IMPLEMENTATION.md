# Quantum-Secure Private File Sharing Implementation

## Overview
This document describes the implementation of the new Quantum-Secure Private File Sharing feature in the FileShare application. This feature allows users to share files securely with specific users using post-quantum cryptography (Kyber-KEM).

## Workflow

### 1. User Registration
- **Kyber Key Generation**: When users create their account, a Kyber-KEM key pair is automatically generated for them.
- **Key Storage**: The public key is stored in plaintext, while the private key is encrypted with the user's password and stored securely.
- **Location**: `auth_routes.py` - signup route handles key generation via `key_mgmt.ensure_user_keys()`

### 2. File Upload
- **AES-256 Encryption**: When users upload a file, it is encrypted using AES-256-GCM.
- **User-Specific Keys**: Each file is encrypted with a unique key derived from the master key and user ID.
- **Location**: `services.py` - FileService handles file upload with encryption

### 3. File Sharing - Two Options

#### Option A: Public Share Link (Normal Share)
- Works as it currently does
- Anyone with the link can access the file
- The AES-256 key is embedded in the URL fragment
- No specific recipient required

#### Option B: Quantum-Secure Private Share
- **User Selection**: Sender selects a specific target user from a dropdown
- **Key Wrapping**: The AES-256 key is encapsulated using the target user's Kyber public key
- **Access Control**: Only the target user can access and decrypt the file
- **Link Creation**: A secure link is generated and copied to clipboard

### 4. Private Share Access (Claiming)
- **Link Pasting**: Target user pastes the private share link in the "Claim Share" page
- **Authentication**: User enters their account password
- **Key Decapsulation**: 
  1. User's password decrypts their Kyber private key
  2. Kyber private key decapsulates the wrapped AES-256 key
  3. AES-256 key decrypts the file
- **Download**: File is automatically downloaded after successful decryption

## Implementation Details

### Database Changes

#### Users Table (models.py)
Added columns for post-quantum keys:
- `pq_public_key` (BLOB) - Kyber public key
- `pq_private_key_encrypted` (BLOB) - Encrypted Kyber private key
- `pq_key_algorithm` (TEXT) - Algorithm name (e.g., "Kyber768")
- `pq_key_created_at` (TIMESTAMP) - Key generation timestamp

#### Shares Table (secure_sharing.py)
Added columns for private shares:
- `share_type` (TEXT) - "public" or "private"
- `target_user_id` (INTEGER) - ID of the recipient user
- `target_kem_ciphertext` (BLOB) - Kyber-wrapped AES key for target user
- `target_kem_algorithm` (TEXT) - KEM algorithm used

### Modified Files

#### 1. models.py
**Changes:**
- Added `get_all_users()` - Returns all active users (for user selection)
- Added `get_username_by_id()` - Get username by user ID

#### 2. routes.py
**Changes:**
- Added `/api/users` endpoint - Returns list of users for target selection (excludes current user)

#### 3. secure_sharing.py
**Major Changes:**
- Updated `_init_shares_table()` - Added private share columns
- Modified `create_share_from_file_id()`:
  - Added parameters: `share_type`, `target_user_id`, `user_password`
  - Added validation for private shares
  - Added Kyber-KEM key wrapping for target user
  - Different messaging for private vs public shares
- Modified `download_shared_file()`:
  - Added parameters: `current_user_id`, `user_password`
  - Added access control for private shares
  - Added Kyber-KEM decapsulation for private shares
  - Validates target user matches current user
- Updated `_get_share_record_with_encryption()` - Returns private share fields

#### 4. sharing_routes.py
**Major Changes:**
- Modified `/create-share` route:
  - Handles both public and private share types
  - Validates target user for private shares
  - Passes share type and target user to service
- Modified `/download-shared` route:
  - Passes user credentials for private share decryption
- Added `/received-shares` route:
  - Displays private shares received by the user
  - Shows sender information
- Added `/claim-share` route:
  - Allows users to paste private share links
  - Requires password for Kyber key decryption
  - Handles link parsing and file download
- Added templates:
  - `RECEIVED_SHARES_TEMPLATE` - View received private shares
  - `CLAIM_SHARE_TEMPLATE` - Claim a private share by pasting link

#### 5. templates.py
**Changes:**
- Updated navigation header:
  - Added "Received" link - View received private shares
  - Added "Claim Share" link - Claim a private share
- Modified share modal:
  - Added share type dropdown (Public/Private)
  - Added target user selection dropdown
  - Shows/hides options based on share type
- Updated JavaScript:
  - `loadUsers()` - Fetches available users from API
  - `togglePrivateShareOptions()` - Shows/hides private share options
  - Modified share form submission to handle both types
  - Different success handling for private shares

### Security Features

#### End-to-End Encryption for Private Shares
1. **File Encryption**: AES-256-GCM with authenticated encryption
2. **Key Wrapping**: Kyber-KEM (post-quantum secure)
3. **Private Key Protection**: Encrypted with user's password using PBKDF2
4. **Access Control**: Server validates target user before decryption

#### Key Security Properties
- **Quantum Resistance**: Kyber-KEM is resistant to quantum computer attacks
- **Forward Secrecy**: Each share uses unique encryption keys
- **Authentication**: GCM mode provides authentication
- **Password-Protected**: Private keys require user password
- **Access Control**: Only designated recipient can decrypt

## User Interface

### Navigation
- **Home** - Upload and manage files
- **My Shares** - View shares you've created
- **Received** - View private shares sent to you
- **Claim Share** - Paste and claim a private share link

### Share Creation Flow
1. Click "Share" button on a file
2. Select share type:
   - **Public Share** - Anyone with link
   - **Quantum-Secure Private Share** - Specific user only
3. If private, select target user from dropdown
4. Set expiration and download limits
5. Create share
6. Link is automatically copied to clipboard

### Private Share Claiming Flow
1. Sender copies private share link
2. Sender shares link with recipient (via secure channel)
3. Recipient goes to "Claim Share" page
4. Paste the complete share link
5. Enter account password
6. File is decrypted and downloaded

## Testing Checklist

### User Registration
- [ ] New user registration generates Kyber key pair
- [ ] Existing users get keys on first login (if enabled)
- [ ] Keys are properly stored in database

### File Upload
- [ ] Files are encrypted with AES-256
- [ ] Encrypted files are stored properly
- [ ] Files can be downloaded and decrypted

### Public Shares
- [ ] Public shares can be created
- [ ] Public share links work for anyone
- [ ] Expiration and download limits work

### Private Shares
- [ ] Can create private share with target user selection
- [ ] Private share uses Kyber-KEM key wrapping
- [ ] Only target user can access the share
- [ ] Non-target users get "Access denied" error
- [ ] Password is required for claiming
- [ ] Incorrect password fails gracefully
- [ ] File downloads successfully after claim

### Navigation
- [ ] All navigation links work
- [ ] "Received Shares" shows incoming private shares
- [ ] "Claim Share" page accepts and processes links

### Security
- [ ] Private keys are encrypted with user password
- [ ] KEM decapsulation requires correct password
- [ ] Access control prevents unauthorized access
- [ ] File integrity is verified after decryption

## Configuration

The feature requires:
- `PQ_KEM_PROVIDER` set to "kyber" in config
- `PQ_KEM_ALGORITHM` set to desired variant (Kyber512/768/1024)
- `kyber-py` package installed: `pip install kyber-py`

## Error Handling

The implementation includes comprehensive error handling:
- Invalid target user selection
- Missing Kyber keys for target user
- Incorrect password during claiming
- KEM decapsulation failures
- Access control violations
- Expired or deactivated shares

## Future Enhancements

Potential improvements:
1. Bulk private sharing to multiple users
2. Share revocation notifications
3. Share access audit logs
4. Key rotation for enhanced security
5. Integration with external key management systems

## Conclusion

This implementation provides a complete quantum-secure private file sharing system using post-quantum cryptography (Kyber-KEM) for key encapsulation. The workflow is user-friendly while maintaining high security standards suitable for protecting sensitive data against future quantum computing threats.
