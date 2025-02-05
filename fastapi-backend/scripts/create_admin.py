from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import SQLALCHEMY_DATABASE_URL
from app.auth.models import Admin
from app.auth.security import get_password_hash

def create_admin(username: str, password: str):
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    # Check if admin already exists
    existing_admin = db.query(Admin).filter(Admin.username == username).first()
    if existing_admin:
        print(f"Admin user '{username}' already exists!")
        return
    
    # Create new admin
    hashed_password = get_password_hash(password)
    new_admin = Admin(username=username, hashed_password=hashed_password)
    
    db.add(new_admin)
    db.commit()
    print(f"Admin user '{username}' created successfully!")

if __name__ == "__main__":
    username = input("Enter admin username: ")
    password = input("Enter admin password: ")
    create_admin(username, password) 