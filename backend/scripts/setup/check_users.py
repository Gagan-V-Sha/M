from app.core.database import SessionLocal
from app.core.models import User
from app.security import auth

# simple script to see all the users in our database and check their status
db = SessionLocal()
users = db.query(User).all()

# print a nice table of the users
print(f"{'Email':<30} | {'Role':<10} | {'Lockout Until':<20} | {'Attempts':<10}")
print("-" * 80)
for u in users:
    # showing email, role, and if they are currently locked out of their account
    print(f"{u.email:<30} | {u.role:<10} | {str(u.lockout_until):<20} | {u.failed_login_attempts:<10}")

# small test to make sure our password checking logic is working
user = db.query(User).filter(User.email == "test@example.com").first()
if user:
    pwd = "Password@123"
    # this calls our auth helper to check the hashed password
    result = auth.verify_password(pwd, user.hashed_password)
    print(f"\nVerification test for test@example.com / Password@123: {result}")
    
db.close()
