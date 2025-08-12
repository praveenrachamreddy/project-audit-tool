# user_management.py

from database import SessionLocal, User, UserProjectRole, ProjectRole
from sqlalchemy.orm import joinedload

def create_user(username, password):
    """Creates a new user."""
    db = SessionLocal()
    user = User(username=username)
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

def get_all_users():
    """Retrieves all users."""
    db = SessionLocal()
    users = db.query(User).all()
    db.close()
    return users

def add_user_to_project(user_id, project_id, role: ProjectRole):
    """Adds a user to a project with a specific role."""
    db = SessionLocal()
    user_project_role = UserProjectRole(user_id=user_id, project_id=project_id, role=role)
    db.add(user_project_role)
    db.commit()
    db.close()

def remove_user_from_project(user_id, project_id):
    """Removes a user from a project."""
    db = SessionLocal()
    user_project_role = db.query(UserProjectRole).filter_by(user_id=user_id, project_id=project_id).first()
    if user_project_role:
        db.delete(user_project_role)
        db.commit()
    db.close()

def get_user_role_for_project(user_id, project_id):
    """Gets a user's role for a specific project."""
    db = SessionLocal()
    user_project_role = db.query(UserProjectRole).filter_by(user_id=user_id, project_id=project_id).first()
    db.close()
    return user_project_role.role if user_project_role else None

def get_users_for_project(project_id):
    """Gets all users and their roles for a specific project."""
    db = SessionLocal()
    users_for_project = db.query(UserProjectRole).options(joinedload(UserProjectRole.user)).filter_by(project_id=project_id).all()
    db.close()
    return users_for_project
