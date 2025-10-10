# Quick Start Guide - Quantum-Secure Private File Sharing

## 🔧 Initial Setup (COMPLETED ✅)

The password encryption issue has been fixed! All users need to log in again to get new keys with correct password encryption.

### What Was Fixed?
- ✅ Kyber private keys are now encrypted with user's actual password (not user ID)
- ✅ All existing user keys have been reset
- ✅ New keys will be generated on next login

## 🚀 Testing the Feature

### Step 1: Create Test Users

1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Access**: Open browser to `http://127.0.0.1:5000`

3. **Create User 1 (Alice)**:
   - Click "Sign Up"
   - Username: `alice`
   - Email: `alice@test.com`
   - Password: `alice123` (remember this!)
   - Confirm Password: `alice123`
   - Click "Sign Up"
   - ✅ Kyber keys will be generated automatically

4. **Create User 2 (Bob)**:
   - Logout Alice
   - Sign up as Bob:
     - Username: `bob`
     - Email: `bob@test.com`
     - Password: `bob123` (remember this!)
   - ✅ Kyber keys generated for Bob

### Step 2: Test File Upload & Public Share

1. **Login as Alice** (`alice` / `alice123`)
2. **Upload a test file**:
   - Drag and drop or click to select a file
   - File will be encrypted with AES-256
3. **Create Public Share**:
   - Click "Share" button on the file
   - Leave as "Public Share"
   - Set expiration (e.g., 24 hours)
   - Click "Create Share"
   - ✅ Link copied to clipboard
4. **Test the link**:
   - Open in incognito/private window
   - File should download successfully

### Step 3: Test Quantum-Secure Private Share

1. **Login as Alice**
2. **Upload a file** (or use existing file)
3. **Create Private Share**:
   - Click "Share" button
   - Select "🔐 Quantum-Secure Private Share"
   - Select target user: **Bob**
   - Set expiration
   - Click "Create Share"
   - ✅ Success message: "Private share created for Bob!"
   - ✅ Link automatically copied to clipboard

4. **Copy the link** - It looks like:
   ```
   http://127.0.0.1:5000/share/abc123xyz#base64encodedkey
   ```

### Step 4: Claim Private Share as Bob

1. **Logout Alice**
2. **Login as Bob** (`bob` / `bob123`)
3. **Go to "Claim Share"** (in navigation)
4. **Paste the complete link** (including the `#` part)
5. **Enter Bob's password**: `bob123`
6. **Click "Claim and Download"**
7. ✅ File should download successfully!

### Step 5: Verify Security

**Test 1: Wrong User**
- Try to claim the share as Alice (file sender)
- Should get: "Access denied: This private share is not for you"

**Test 2: Wrong Password**
- Login as Bob
- Try to claim with wrong password
- Should get: "Failed to decrypt your private key"

**Test 3: View Received Shares**
- Login as Bob
- Click "Received" in navigation
- Should see the private share from Alice

## 🎯 Feature Summary

### Public Shares
- 🌐 Anyone with link can access
- 🔗 Share via any channel
- ⚡ Instant access

### Quantum-Secure Private Shares
- 🔐 Only target user can decrypt
- 🛡️ Post-quantum cryptography (Kyber-KEM)
- 🔑 Requires recipient's password
- 💪 Quantum computer resistant

## 📱 User Interface

### Navigation Menu
- **Home** - Upload and manage your files
- **My Shares** - View shares you've created
- **Received** - View private shares sent to you
- **Claim Share** - Paste and claim private share links

### Share Options
When clicking "Share" on a file:
- **Public Share**: Anyone with link
- **Quantum-Secure Private Share**: Select specific user

## 🔒 How It Works (Technical)

### Encryption Flow
1. **File Upload**: File encrypted with AES-256-GCM
2. **Public Share**: AES key embedded in URL
3. **Private Share**: 
   - AES key wrapped with recipient's Kyber public key
   - Only recipient's Kyber private key can unwrap it
   - Recipient's private key requires their password

### Key Generation
- **On Signup**: Kyber key pair generated automatically
- **Public Key**: Stored in database (unencrypted)
- **Private Key**: Encrypted with user's password + PBKDF2
- **Algorithm**: Kyber768 (NIST Level 3 security)

## 🐛 Troubleshooting

### "Failed to decrypt your private key"
**Cause**: Wrong password entered
**Solution**: Use the exact password you created during signup

### "Access denied: This private share is not for you"
**Cause**: Trying to access a share meant for another user
**Solution**: Only the designated recipient can access private shares

### "Share not found or expired"
**Cause**: Link expired or share was deactivated
**Solution**: Ask sender to create a new share

### Users have old keys
**Cause**: Keys were generated before the fix
**Solution**: Run migration script:
```bash
python migrate_user_keys.py
```
Then all users should log out and log back in.

## 📊 Testing Checklist

- [ ] Alice can signup and get Kyber keys
- [ ] Bob can signup and get Kyber keys
- [ ] Alice can upload encrypted file
- [ ] Alice can create public share (works for anyone)
- [ ] Alice can create private share for Bob
- [ ] Bob can see share in "Received"
- [ ] Bob can claim share with correct password
- [ ] Bob cannot claim with wrong password
- [ ] Alice cannot claim share meant for Bob
- [ ] File downloads and decrypts correctly

## 🎓 Best Practices

1. **For Senders**:
   - Use private shares for sensitive documents
   - Verify recipient user before creating share
   - Set appropriate expiration times
   - Deactivate shares when no longer needed

2. **For Recipients**:
   - Keep your password secure
   - Claim shares promptly before expiration
   - Verify sender identity before opening files

3. **Security**:
   - Never share your password
   - Use strong passwords (8+ characters)
   - Log out when done
   - Check "Received" regularly for new shares

## ✅ Success Criteria

You'll know everything is working when:
1. ✅ New users get Kyber keys on signup
2. ✅ Private shares can be created with user selection
3. ✅ Only target user can claim private shares
4. ✅ Correct password is required for claiming
5. ✅ Files download and decrypt successfully
6. ✅ Access control prevents unauthorized access

## 🎉 You're Ready!

The quantum-secure private file sharing feature is now fully functional and ready for use!

**Key Achievement**: Your file sharing app now supports post-quantum cryptography, making it secure against future quantum computer attacks! 🔐🚀
