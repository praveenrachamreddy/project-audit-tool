from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Date, Enum
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os
import enum

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///project_audit_tool.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ProjectRole(enum.Enum):
    Admin = "Admin"
    Editor = "Editor"
    Viewer = "Viewer"

class UserProjectRole(Base):
    __tablename__ = 'user_project_roles'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), primary_key=True)
    role = Column(Enum(ProjectRole), nullable=False)

    user = relationship("User", back_populates="projects")
    project = relationship("Project", back_populates="users")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)

    # New fields for Project Initiation Note (PIN) details
    pin_id = Column(String, unique=True, nullable=True) # Project Initiation Note ID
    scope = Column(Text, nullable=True)
    milestones = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    effort_estimation = Column(String, nullable=True)
    deliverables = Column(Text, nullable=True)
    team_members = Column(Text, nullable=True) # Store as comma-separated or JSON string
    team_size = Column(Integer, nullable=True)
    roles_responsibilities = Column(Text, nullable=True)
    sdlc_model = Column(String, nullable=True) # e.g., Agile, Waterfall
    ciso_approved = Column(Boolean, default=False)
    ciso_approval_date = Column(Date, nullable=True)

    users = relationship("UserProjectRole", back_populates="project")

class WorkPackage(Base):
    __tablename__ = "work_packages"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, index=True)
    description = Column(String)
    project_id = Column(Integer, ForeignKey("projects.id"))

    project = relationship("Project", back_populates="work_packages")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    action = Column(String)
    details = Column(String)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True) # Project ID can be null for global actions

    project = relationship("Project", back_populates="audit_logs")

class Risk(Base):
    __tablename__ = "risks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    severity = Column(String)
    likelihood = Column(String)
    status = Column(String)
    project_id = Column(Integer, ForeignKey("projects.id"))

    project = relationship("Project", back_populates="risks")

class Control(Base):
    __tablename__ = "controls"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    type = Column(String)
    status = Column(String)
    risk_id = Column(Integer, ForeignKey("risks.id"))

    risk = relationship("Risk", back_populates="controls")

class Compliance(Base):
    __tablename__ = "compliance_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    standard = Column(String) # e.g., GDPR, ISO 27001
    status = Column(String) # e.g., Compliant, Non-Compliant, In Progress
    project_id = Column(Integer, ForeignKey("projects.id"))

    project = relationship("Project", back_populates="compliance_items")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)

    projects = relationship("UserProjectRole", back_populates="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String)
    type = Column(String) # e.g., PIN, SRS, HLD, QAP, Email Approval
    version = Column(String, default="1.0")
    link = Column(String) # URL or path to file
    approval_status = Column(String, default="Pending") # e.g., Pending, Approved, Rejected
    approved_by = Column(String, nullable=True)
    approval_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="documents")

# Define relationships after all classes are defined
Project.work_packages = relationship("WorkPackage", back_populates="project")
Project.audit_logs = relationship("AuditLog", back_populates="project")
Project.risks = relationship("Risk", back_populates="project")
Project.compliance_items = relationship("Compliance", back_populates="project")
Project.documents = relationship("Document", back_populates="project")
Risk.controls = relationship("Control", back_populates="risk")

def assign_admin_to_orphan_projects():
    """Assigns the default admin user to any projects that have no users."""
    db = SessionLocal()
    admin_user = db.query(User).filter_by(username="admin").first()
    if not admin_user:
        return # No admin user to assign

    projects = db.query(Project).all()
    for project in projects:
        if not project.users:
            admin_role = UserProjectRole(user_id=admin_user.id, project_id=project.id, role=ProjectRole.Admin)
            db.add(admin_role)
            print(f"Assigned admin user to orphan project: {project.name}")
    db.commit()
    db.close()

def init_db():
    """Initializes the database and creates the tables."""
    Base.metadata.create_all(bind=engine)

    # Create a default admin user if one doesn't exist
    session = SessionLocal()
    if not session.query(User).filter_by(username="admin").first():
        admin_user = User(username="admin")
        admin_user.set_password("admin") # Default password is 'admin'
        session.add(admin_user)
        session.commit()
        print("Default admin user created (username: admin, password: admin)")
    session.close()
    
    # Assign admin to any projects that don't have a user
    assign_admin_to_orphan_projects()

if __name__ == "__main__":
    init_db()