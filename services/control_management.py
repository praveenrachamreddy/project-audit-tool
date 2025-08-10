# control_management.py

from database import SessionLocal, Control, Risk
from services.audit_logging import create_audit_log

def create_control(risk_id, name, description, type, status):
    """Creates a new control."""
    db = SessionLocal()
    risk = db.query(Risk).filter(Risk.id == risk_id).first()
    project_id = risk.project_id if risk else None

    control = Control(risk_id=risk_id, name=name, description=description, type=type, status=status)
    db.add(control)
    db.commit()
    db.refresh(control)
    db.close()
    create_audit_log(project_id, "Control Created", f"Control '{name}' was created for risk ID {risk_id}.")
    return control

def get_controls(risk_id=None):
    """Gets all controls, optionally filtered by risk."""
    db = SessionLocal()
    if risk_id:
        controls = db.query(Control).filter(Control.risk_id == risk_id).all()
    else:
        controls = db.query(Control).all()
    db.close()
    return controls

def update_control(control_id, name=None, description=None, type=None, status=None):
    """Updates an existing control."""
    db = SessionLocal()
    control = db.query(Control).filter(Control.id == control_id).first()
    if control:
        project_id = control.risk.project_id if control.risk else None
        if name: control.name = name
        if description: control.description = description
        if type: control.type = type
        if status: control.status = status
        db.commit()
        db.refresh(control)
        db.close()
        create_audit_log(project_id, "Control Updated", f"Control '{control.name}' (ID: {control.id}) was updated.")
        return control
    db.close()
    return None

def delete_control(control_id):
    """Deletes a control."""
    db = SessionLocal()
    control = db.query(Control).filter(Control.id == control_id).first()
    if control:
        project_id = control.risk.project_id if control.risk else None
        control_name = control.name
        db.delete(control)
        db.commit()
        db.close()
        create_audit_log(project_id, "Control Deleted", f"Control '{control_name}' (ID: {control_id}) was deleted.")
        return True
    db.close()
    return False
