import sqlite3
import os

def run_migrations():
    db_path = "ak_lumora.db"
    print(f"Connecting to database: {db_path}")
    if not os.path.exists(db_path):
        print(f"Error: {db_path} does not exist!")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Alter drive_configs
    try:
        cursor.execute("ALTER TABLE drive_configs ADD COLUMN cleanup_enabled BOOLEAN DEFAULT 0")
        cursor.execute("ALTER TABLE drive_configs ADD COLUMN cleanup_keep_count INTEGER DEFAULT 50")
        print("Migrated drive_configs columns successfully!")
    except sqlite3.OperationalError as e:
        print("drive_configs columns migration skipped (already exists or error):", e)
        
    # Alter watched_folders
    try:
        cursor.execute("ALTER TABLE watched_folders ADD COLUMN cleanup_enabled BOOLEAN DEFAULT 0")
        cursor.execute("ALTER TABLE watched_folders ADD COLUMN cleanup_keep_count INTEGER DEFAULT 50")
        print("Migrated watched_folders columns successfully!")
    except sqlite3.OperationalError as e:
        print("watched_folders columns migration skipped (already exists or error):", e)
        
    conn.commit()
    conn.close()
    print("Database migration complete.")

if __name__ == "__main__":
    run_migrations()
