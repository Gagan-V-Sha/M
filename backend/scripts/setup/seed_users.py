from app.core.database import SessionLocal, create_tables
from app.core.models import User
from app.core.datatypes import UserRole
from app.security.auth import get_password_hash

# this script creates some default users so we can test the system
def seed():
    # make sure the database tables are ready
    create_tables()
    db = SessionLocal()
    
    # list of dummy users to create
    users = [
        {"email": "test@example.com", "password": "Password@123", "role": "viewer"},
        {"email": "admin@example.com", "password": "Admin@123", "role": "admin"},
        {"email": "editor@example.com", "password": "Password@123", "role": "editor"}
    ]
    
    for u in users:
        # check if the user is already there
        existing = db.query(User).filter(User.email == u["email"]).first()
        if not existing:
            # create and hash the password for security
            user = User(
                email=u["email"],
                hashed_password=get_password_hash(u["password"]),
                role=u["role"],
                is_active=True
            )
            db.add(user)
            print(f"Created user: {u['email']}")
        else:
            # if they exist, just make sure they have the right role
            if existing.role != u["role"]:
                existing.role = u["role"]
                print(f"Updated role for: {u['email']}")
            else:
                print(f"User exists: {u['email']}")
    
    db.commit()
    db.close()

if __name__ == "__main__":
    seed()
