from app.core.database import engine
from sqlalchemy import text

def add_mfa_columns():
    with engine.connect() as conn:
        try:
            # For SQLite (which seems likely based on the syntax used previously)
            conn.execute(text("ALTER TABLE users ADD COLUMN mfa_secret VARCHAR"))
            conn.execute(text("ALTER TABLE users ADD COLUMN mfa_enabled BOOLEAN DEFAULT 0"))
            print("Successfully added mfa_secret and mfa_enabled columns to users table.")
        except Exception as e:
            # Table might already have the columns, or it's a different dialect
            print(f"Error (or columns already exist): {e}")

if __name__ == "__main__":
    add_mfa_columns()
