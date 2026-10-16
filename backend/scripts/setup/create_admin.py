import sys
import os

BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.core.database import SessionLocal, engine
from app.core import models
from app.security import auth

def create_admin():
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        email = "admin@example.com"
        # check if this user is already in the database
        existing = db.query(models.User).filter(models.User.email == email).first()
        if existing:
            print(f"User {email} already exists.")
            return

        # hash the password for security
        hashed_pw = auth.get_password_hash("Admin@123")
        
        # setup the new admin user object
        new_user = models.User(
            email=email,
            name="Admin User",
            hashed_password=hashed_pw,
            role="admin",
            is_active=True
        )
        
        # save the user to the database
        db.add(new_user)
        db.commit()
        print(f"Successfully created admin user!")
        print(f"Email: {email}")
        print(f"Password: Admin@123")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
