"""
Migration script: Add pdf_path, mapping_json_path, parse_status, parse_error columns to standards table.
Run once with: backend\venv\Scripts\python backend\scripts\migrate_standards_columns.py
"""
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "data.db")

def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())

def migrate():
    print(f"Migrating DB at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    new_columns = [
        ("pdf_path",          "TEXT"),
        ("mapping_json_path", "TEXT"),
        ("parse_status",      "TEXT DEFAULT 'none'"),
        ("parse_error",       "TEXT"),
    ]

    for col_name, col_def in new_columns:
        if not column_exists(cursor, "standards", col_name):
            cursor.execute(f"ALTER TABLE standards ADD COLUMN {col_name} {col_def}")
            print(f"  Added column: {col_name}")
        else:
            print(f"  Already exists: {col_name} (skipped)")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
