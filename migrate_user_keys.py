"""
Migration Script: Regenerate Kyber Keys for Existing Users
This script resets all user Kyber keys so they can be regenerated with correct passwords on next login
"""
import sqlite3
import sys

def migrate_user_keys(db_name='file_sharing.db'):
    """Reset all user PQ keys so they will be regenerated on next login"""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Check if PQ key columns exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'pq_public_key' not in columns:
            print("❌ PQ key columns don't exist in users table. No migration needed.")
            conn.close()
            return False
        
        # Count users with existing PQ keys
        cursor.execute('''
            SELECT COUNT(*) FROM users 
            WHERE pq_public_key IS NOT NULL
        ''')
        users_with_keys = cursor.fetchone()[0]
        
        if users_with_keys == 0:
            print("✅ No users have PQ keys yet. No migration needed.")
            conn.close()
            return True
        
        print(f"Found {users_with_keys} user(s) with existing PQ keys")
        print("Resetting PQ keys for all users...")
        
        # Reset all PQ keys to NULL
        cursor.execute('''
            UPDATE users 
            SET pq_public_key = NULL,
                pq_private_key_encrypted = NULL,
                pq_key_algorithm = NULL,
                pq_key_created_at = NULL
        ''')
        
        rows_updated = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"✅ Successfully reset PQ keys for {rows_updated} user(s)")
        print("📝 Users will get new keys on next login with correct password encryption")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Kyber Key Migration Script")
    print("=" * 60)
    print()
    print("This script will reset all user Kyber keys.")
    print("Users will get new keys on next login.")
    print()
    
    response = input("Continue? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        success = migrate_user_keys()
        if success:
            print()
            print("=" * 60)
            print("✅ Migration completed successfully!")
            print("=" * 60)
            print()
            print("Next steps:")
            print("1. Restart the application")
            print("2. Users should log out and log back in")
            print("3. New Kyber keys will be generated with correct passwords")
            sys.exit(0)
        else:
            print()
            print("❌ Migration failed!")
            sys.exit(1)
    else:
        print("Migration cancelled.")
        sys.exit(0)
