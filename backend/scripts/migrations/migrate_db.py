from app.core.database import engine
from sqlalchemy import text

# this script manually updates the database structure if we add new columns
def migrate():
    with engine.begin() as conn:
        # try to add the 'role' column to the users table
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'viewer'"))
            print("Migration successful: Added role column.")
        except Exception as e:
            # it might fail if the column is already there
            print(f"Migration failed for users (might already exist): {e}")

        # try to add columns needed for the password reset feature
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN reset_token VARCHAR"))
            conn.execute(text("ALTER TABLE users ADD COLUMN reset_token_expires DATETIME"))
            print("Migration successful: Added password reset columns to users.")
        except Exception as e:
            print(f"Migration failed for users password reset columns (might already exist): {e}")

        # add a column to help us sort the GSPR requirements in the right order
        try:
            conn.execute(text("ALTER TABLE gspr_requirements ADD COLUMN sort_order INTEGER DEFAULT 0"))
            print("Migration successful: Added sort_order column.")
        except Exception as e:
            print(f"Migration failed for gspr_requirements sort_order (might already exist): {e}")

        # add a column to support sub-requirements (hierarchy)
        try:
            conn.execute(text("ALTER TABLE gspr_requirements ADD COLUMN parent_id INTEGER"))
            print("Migration successful: Added parent_id column.")
        except Exception as e:
            print(f"Migration failed for gspr_requirements parent_id (might already exist): {e}")

        # add extra fields for the device profiles
        try:
            conn.execute(text("ALTER TABLE device_profiles ADD COLUMN model_code VARCHAR"))
            conn.execute(text("ALTER TABLE device_profiles ADD COLUMN document_number VARCHAR"))
            print("Migration successful: Added device profile metadata columns.")
        except Exception as e:
            print(f"Migration failed for device_profiles (might already exist): {e}")

        # OPTION A: per-user isolation
        # add owner_id so each device is linked to the user who created it
        # nullable so existing devices in the DB are not affected
        try:
            conn.execute(text("ALTER TABLE device_profiles ADD COLUMN owner_id INTEGER REFERENCES users(id)"))
            print("Migration successful: Added owner_id column to device_profiles.")
        except Exception as e:
            print(f"Migration failed for device_profiles owner_id (might already exist): {e}")

if __name__ == "__main__":
    migrate()
