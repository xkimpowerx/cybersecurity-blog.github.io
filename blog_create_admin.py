from blog_db import SessionLocal, init_db
from blog_models import AdminUser
from passlib.context import CryptContext
import sys

init_db()

def create_admin(username, password):
    db = SessionLocal()
    if db.query(AdminUser).filter(AdminUser.username == username).first():
        print(f"Admin user '{username}' already exists.")
        return
    try:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_pw = pwd_context.hash(password)
    except Exception as e:
        # Fallback to using bcrypt directly if passlib has issues
        import bcrypt
        password_bytes = password.encode('utf-8')
        hashed_pw = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
        print(f"Note: Used bcrypt directly due to passlib compatibility issue")
    
    admin = AdminUser(username=username, hashed_password=hashed_pw)
    db.add(admin)
    db.commit()
    db.close()
    print(f"Admin user '{username}' created successfully!")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        # Command line arguments provided
        username = sys.argv[1]
        password = sys.argv[2]
        create_admin(username, password)
    else:
        # Interactive mode
        print("Admin User Creation")
        print("=" * 30)
        username = input("Enter admin username: ")
        password = input("Enter admin password: ")
        create_admin(username, password)
