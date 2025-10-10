# Bug Fix: Share Creation Error

## Issue
**Error**: "too many values to unpack (expected 11)"  
**Location**: `secure_sharing.py`, line 147-148  
**When**: Creating a share link for an existing file

## Root Cause

After adding KEM (Kyber) columns to the database schema, the `files` table now returns 14 columns instead of 11:

**Old format (11 columns):**
- id, filename, original_filename, file_size, file_hash, user_id, upload_date, download_count, is_encrypted, encryption_salt, encryption_method

**New format (14 columns):**
- id, filename, original_filename, file_size, file_hash, user_id, upload_date, download_count, is_encrypted, encryption_salt, encryption_method, **kem_ciphertext, kem_algorithm, kem_public_key_id**

The code in `create_share_from_file_id()` was trying to unpack the record into 11 variables, but received 14 values, causing the error.

## Solution

Updated `secure_sharing.py` to handle both old and new database formats:

```python
# Handle both old format (11 values) and new format (14 values) for backward compatibility
if len(file_record) == 14:
    (id, filename, original_filename, file_size, file_hash, 
     user_id_db, upload_date, download_count, is_encrypted, encryption_salt, encryption_method,
     kem_ciphertext, kem_algorithm, kem_public_key_id) = file_record
elif len(file_record) == 11:
    # Legacy format without KEM columns
    (id, filename, original_filename, file_size, file_hash, 
     user_id_db, upload_date, download_count, is_encrypted, encryption_salt, encryption_method) = file_record
else:
    # Try to unpack what we have (graceful fallback)
    id = file_record[0]
    filename = file_record[1]
    # ... etc
```

## Fix Applied

**File**: `secure_sharing.py`  
**Lines**: 145-170  
**Change**: Added flexible unpacking logic to handle both 11-column and 14-column formats

## Verification

Test results:
```bash
$ python test_share_fix.py

============================================================
Testing Share Creation Fix
============================================================

[1] Initializing database...
✅ Created test user (ID: 2)

[2] Creating test file record...
✅ Created test file record (ID: 1)

[3] Initializing secure sharing...
✅ Secure sharing initialized

[4] Creating share from file ID...
✅ Share created successfully!
   Share ID: rO36sJEenZb0Dxw0AZO55w
   Share URL: /share/rO36sJEenZb0Dxw0AZO55w#...
   Expiry: 2025-10-12T00:04:38.404739

[5] Cleaning up...
✅ Cleanup complete

============================================================
✅ Share creation test PASSED!
============================================================
```

## Impact

- ✅ Share creation now works with both old and new database schemas
- ✅ Backward compatible with databases before KEM columns were added
- ✅ Forward compatible with full Kyber-KEM implementation
- ✅ No data migration required
- ✅ Existing shares continue to work

## Files Modified

1. **secure_sharing.py** (lines 145-170)
   - Added flexible record unpacking
   - Handles 11, 14, or variable-length records

## Testing

Created `test_share_fix.py` to verify:
- ✅ Database initialization with new schema
- ✅ File record creation with KEM columns
- ✅ Share creation from file ID
- ✅ No unpacking errors
- ✅ Share URL generation works

## Status

**Fixed**: ✅ Share creation now works correctly  
**Tested**: ✅ Verified with test script  
**Ready**: ✅ Application can create share links

---

*Bug fixed: 2025-10-10*  
*Status: RESOLVED*
