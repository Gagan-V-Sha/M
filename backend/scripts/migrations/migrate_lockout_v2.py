import sqlite3
import os

# The actual database name is data.db as per database.py
db_path = "data.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"Adding failed_login_attempts and lockout_until columns to {db_path}...")
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0")
        print("Added failed_login_attempts")
    except sqlite3.OperationalError as e:
        print(f"failed_login_attempts already exists or error: {e}")
        
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN lockout_until DATETIME")
        print("Added lockout_until")
    except sqlite3.OperationalError as e:
        print(f"lockout_until already exists or error: {e}")
        
    conn.commit()
    conn.close()
    print("Migration complete.")
else:
    print(f"Database not found at {db_path}")
