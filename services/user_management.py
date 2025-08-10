# user_management.py

from database import SessionLocal, User

def create_user(username, password, role="user"):
    """Creates a new user."""
    db = SessionLocal()
    user = User(username=username, role=role)
    user.set_password(password)
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

def authenticate_user(username, password):
    """Authenticates a user by username and password."""
    db = SessionLocal()
    user = db.query(User).filter_by(username=username).first()
    db.close()
    if user and user.check_password(password):
        return user
    return None

def get_user_by_username(username):
    """Retrieves a user by username."""
    db = SessionLocal()
    user = db.query(User).filter_by(username=username).first()
    db.close()
    return user

def get_all_users():
    """Retrieves all users."""
    db = SessionLocal()
    users = db.query(User).all()
    db.close()
    return users
