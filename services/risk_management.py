# risk_management.py

from database import SessionLocal, Risk
from services.audit_logging import create_audit_log

def create_risk(project_id, name, description, severity, likelihood, status):
    """Creates a new risk."""
    db = SessionLocal()
    risk = Risk(project_id=project_id, name=name, description=description, severity=severity, likelihood=likelihood, status=status)
    db.add(risk)
    db.commit()
    db.refresh(risk)
    db.close()
    create_audit_log(project_id, "Risk Created", f"Risk '{name}' was created for project ID {project_id}.")
    return risk

def get_risks(project_id=None):
    """Gets all risks, optionally filtered by project."""
    db = SessionLocal()
    if project_id:
        risks = db.query(Risk).filter(Risk.project_id == project_id).all()
    else:
        risks = db.query(Risk).all()
    db.close()
    return risks

def update_risk(risk_id, name=None, description=None, severity=None, likelihood=None, status=None):
    """Updates an existing risk."""
    db = SessionLocal()
    risk = db.query(Risk).filter(Risk.id == risk_id).first()
    if risk:
        if name: risk.name = name
        if description: risk.description = description
        if severity: risk.severity = severity
        if likelihood: risk.likelihood = likelihood
        if status: risk.status = status
        db.commit()
        db.refresh(risk)
        db.close()
        create_audit_log(risk.project_id, "Risk Updated", f"Risk '{risk.name}' (ID: {risk.id}) was updated.")
        return risk
    db.close()
    return None

def delete_risk(risk_id):
    """Deletes a risk."""
    db = SessionLocal()
    risk = db.query(Risk).filter(Risk.id == risk_id).first()
    if risk:
        project_id = risk.project_id
        risk_name = risk.name
        db.delete(risk)
        db.commit()
        db.close()
        create_audit_log(project_id, "Risk Deleted", f"Risk '{risk_name}' (ID: {risk_id}) was deleted.")
        return True
    db.close()
    return False
