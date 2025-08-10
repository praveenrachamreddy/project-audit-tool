# audit_logging.py

from database import SessionLocal, AuditLog

def create_audit_log(project_id, action, details):
    """Creates a new audit log entry."""
    db = SessionLocal()
    audit_log = AuditLog(project_id=project_id, action=action, details=details)
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    db.close()
    return audit_log

def get_audit_logs(project_id=None):
    """Gets all audit log entries, optionally filtered by project."""
    db = SessionLocal()
    if project_id:
        logs = db.query(AuditLog).filter(AuditLog.project_id == project_id).all()
    else:
        logs = db.query(AuditLog).all()
    db.close()
    return logs
