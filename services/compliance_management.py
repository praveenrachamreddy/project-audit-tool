# compliance_management.py

from database import SessionLocal, Compliance, Project, Risk, Document
from services.audit_logging import create_audit_log
from services.risk_management import get_risks
from services.document_management import get_documents

def create_compliance_item(project_id, name, description, standard, status):
    """Creates a new compliance item."""
    db = SessionLocal()
    compliance_item = Compliance(project_id=project_id, name=name, description=description, standard=standard, status=status)
    db.add(compliance_item)
    db.commit()
    db.refresh(compliance_item)
    db.close()
    create_audit_log(project_id, "Compliance Item Created", f"Compliance item '{name}' was created for project ID {project_id}.")
    return compliance_item

def get_compliance_items(project_id=None):
    """Gets all compliance items, optionally filtered by project."""
    db = SessionLocal()
    if project_id:
        compliance_items = db.query(Compliance).filter(Compliance.project_id == project_id).all()
    else:
        compliance_items = db.query(Compliance).all()
    db.close()
    return compliance_items

def update_compliance_item(compliance_item_id, name=None, description=None, standard=None, status=None):
    """Updates an existing compliance item."""
    db = SessionLocal()
    compliance_item = db.query(Compliance).filter(Compliance.id == compliance_item_id).first()
    if compliance_item:
        if name: compliance_item.name = name
        if description: compliance_item.description = description
        if standard: compliance_item.standard = standard
        if status: compliance_item.status = status
        db.commit()
        db.refresh(compliance_item)
        db.close()
        create_audit_log(compliance_item.project_id, "Compliance Item Updated", f"Compliance item '{compliance_item.name}' (ID: {compliance_item.id}) was updated.")
        return compliance_item
    db.close()
    return None

def delete_compliance_item(compliance_item_id):
    """Deletes a compliance item."""
    db = SessionLocal()
    compliance_item = db.query(Compliance).filter(Compliance.id == compliance_item_id).first()
    if compliance_item:
        project_id = compliance_item.project_id
        compliance_item_name = compliance_item.name
        db.delete(compliance_item)
        db.commit()
        db.close()
        create_audit_log(project_id, "Compliance Item Deleted", f"Compliance item '{compliance_item_name}' (ID: {compliance_item_id}) was deleted.")
        return True
    db.close()
    return False

def automate_compliance_check(project_id: int = None):
    """
    Automates compliance checks for a given project or all projects.
    Rules:
    - If a compliance item is linked to a document and that document is 'Approved', mark compliance item as 'Compliant'.
    - If a compliance item is linked to a risk and that risk is 'Mitigated' or 'Closed', mark compliance item as 'Compliant'.
    """
    db = SessionLocal()
    updated_count = 0
    try:
        query = db.query(Compliance)
        if project_id:
            query = query.filter(Compliance.project_id == project_id)
        
        compliance_items = query.all()
        print(f"DEBUG: Processing {len(compliance_items)} compliance items for project ID {project_id if project_id else 'all'}.")

        for item in compliance_items:
            print(f"DEBUG: Checking compliance item: {item.name} (ID: {item.id}), Current Status: {item.status}")
            original_status = item.status
            new_status = original_status

            # Rule 1: Check linked documents
            documents = get_documents(item.project_id) # Get all documents for the project
            print(f"DEBUG: Found {len(documents)} documents for project ID {item.project_id}.")
            for doc in documents:
                print(f"DEBUG: Comparing '{item.name.lower()}' with document '{doc.name.lower()}', Approval Status: {doc.approval_status}")
                if item.name.lower() in doc.name.lower() and doc.approval_status == "Approved":
                    print(f"DEBUG: Document match found! '{doc.name}' is approved and contains '{item.name}'. Setting status to Compliant.")
                    new_status = "Compliant"
                    break
            
            if new_status == "Compliant": # If already compliant by document, no need to check risks
                if original_status != new_status:
                    item.status = new_status
                    db.add(item)
                    updated_count += 1
                    print(f"DEBUG: Updated compliance item {item.name} to {new_status} due to document.")
                    create_audit_log(item.project_id, "Compliance Auto-Checked", f"Compliance item '{item.name}' (ID: {item.id}) status automatically updated to '{new_status}' due to linked approved document.")
                continue # Move to next compliance item

            # Rule 2: Check linked risks
            risks = get_risks(item.project_id) # Get all risks for the project
            print(f"DEBUG: Found {len(risks)} risks for project ID {item.project_id}.")
            for risk in risks:
                print(f"DEBUG: Comparing '{item.name.lower()}' with risk '{risk.name.lower()}', Risk Status: {risk.status}")
                if item.name.lower() in risk.name.lower() and risk.status in ["Mitigated", "Closed"]:
                    print(f"DEBUG: Risk match found! '{risk.name}' is mitigated/closed and contains '{item.name}'. Setting status to Compliant.")
                    new_status = "Compliant"
                    break
            
            if original_status != new_status:
                item.status = new_status
                db.add(item)
                updated_count += 1
                print(f"DEBUG: Updated compliance item {item.name} to {new_status} due to risk.")
                create_audit_log(item.project_id, "Compliance Auto-Checked", f"Compliance item '{item.name}' (ID: {item.id}) status automatically updated to '{new_status}' due to linked mitigated/closed risk.")

        db.commit()
        return f"Automated compliance check completed. {updated_count} compliance items updated."
    except Exception as e:
        db.rollback()
        create_audit_log(project_id, "Compliance Auto-Check Failed", f"Automated compliance check failed for project ID {project_id}: {e}")
        return f"An error occurred during automated compliance check: {e}"
    finally:
        db.close()
