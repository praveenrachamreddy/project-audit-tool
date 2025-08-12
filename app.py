# app.py

import os
import argparse
from services.project_management import create_project, get_projects, create_work_package, get_work_packages, update_project, get_project_by_id, generate_project_status_report
from services.audit_logging import get_audit_logs
from services.risk_management import create_risk, get_risks, update_risk, delete_risk
from services.control_management import create_control, get_controls, update_control, delete_control
from services.compliance_management import create_compliance_item, get_compliance_items, update_compliance_item, delete_compliance_item, automate_compliance_check
from services.document_management import create_document, get_documents, update_document, delete_document
from services.llm_service import LLMService
from services.user_management import create_user, get_all_users
import datetime

def list_projects(args):
    """Lists all projects."""
    projects = get_projects()
    for project in projects:
        print(f"- {project.name} (ID: {project.id})")

def add_project(args):
    """Adds a new project."""
    # Convert date strings to date objects
    start_date = datetime.datetime.strptime(args.start_date, '%Y-%m-%d').date() if args.start_date else None
    end_date = datetime.datetime.strptime(args.end_date, '%Y-%m-%d').date() if args.end_date else None
    ciso_approval_date = datetime.datetime.strptime(args.ciso_approval_date, '%Y-%m-%d').date() if args.ciso_approval_date else None

    project = create_project(
        name=args.name,
        description=args.description,
        pin_id=args.pin_id,
        scope=args.scope,
        milestones=args.milestones,
        start_date=start_date,
        end_date=end_date,
        effort_estimation=args.effort_estimation,
        deliverables=args.deliverables,
        team_members=args.team_members,
        team_size=args.team_size,
        roles_responsibilities=args.roles_responsibilities,
        sdlc_model=args.sdlc_model,
        ciso_approved=args.ciso_approved,
        ciso_approval_date=ciso_approval_date
    )
    print(f"Successfully created project '{project.name}'.")

def update_project_cmd(args):
    """Updates an existing project."""
    # Convert date strings to date objects
    start_date = datetime.datetime.strptime(args.start_date, '%Y-%m-%d').date() if args.start_date else None
    end_date = datetime.datetime.strptime(args.end_date, '%Y-%m-%d').date() if args.end_date else None
    ciso_approval_date = datetime.datetime.strptime(args.ciso_approval_date, '%Y-%m-%d').date() if args.ciso_approval_date else None

    project = update_project(
        project_id=args.project_id,
        name=args.name,
        description=args.description,
        pin_id=args.pin_id,
        scope=args.scope,
        milestones=args.milestones,
        start_date=start_date,
        end_date=end_date,
        effort_estimation=args.effort_estimation,
        deliverables=args.deliverables,
        team_members=args.team_members,
        team_size=args.team_size,
        roles_responsibilities=args.roles_responsibilities,
        sdlc_model=args.sdlc_model,
        ciso_approved=args.ciso_approved,
        ciso_approval_date=ciso_approval_date
    )
    if project:
        print(f"Successfully updated project '{project.name}'.")
    else:
        print(f"Project with ID {args.project_id} not found.")

def list_work_packages(args):
    """Lists all work packages for a project."""
    work_packages = get_work_packages(args.project_id)
    for wp in work_packages:
        print(f"- {wp.subject} (ID: {wp.id})")

def add_work_package(args):
    """Adds a new work package to a project."""
    work_package = create_work_package(args.project_id, args.subject, args.description)
    print(f"Successfully created work package '{work_package.subject}'.")

def generate_project_report_cmd(args):
    """Generates a status report for a project."""
    print(f"Generating status report for project ID: {args.project_id}...")
    report = generate_project_status_report(args.project_id)
    print("\n--- Project Status Report ---\n")
    print(report)
    print("\n-----------------------------")

def list_audit_logs(args):
    """Lists all audit logs, optionally filtered by project."""
    logs = get_audit_logs(args.project_id)
    for log in logs:
        print(f"[{log.timestamp}] Project ID: {log.project_id}, Action: {log.action}, Details: {log.details}")

def add_risk(args):
    """Adds a new risk to a project."""
    risk = create_risk(args.project_id, args.name, args.description, args.severity, args.likelihood, args.status)
    print(f"Successfully created risk '{risk.name}'.")

def list_risks(args):
    """Lists all risks, optionally filtered by project."""
    risks = get_risks(args.project_id)
    for risk in risks:
        print(f"- {risk.name} (ID: {risk.id}) - Severity: {risk.severity}, Likelihood: {risk.likelihood}, Status: {risk.status}")

def update_risk_cmd(args):
    """Updates an existing risk."""
    risk = update_risk(args.risk_id, args.name, args.description, args.severity, args.likelihood, args.status)
    if risk:
        print(f"Successfully updated risk '{risk.name}'.")
    else:
        print(f"Risk with ID {args.risk_id} not found.")

def delete_risk_cmd(args):
    """Deletes a risk."""
    if delete_risk(args.risk_id):
        print(f"Successfully deleted risk with ID {args.risk_id}.")
    else:
        print(f"Risk with ID {args.risk_id} not found.")

def add_control(args):
    """Adds a new control to a risk."""
    control = create_control(args.risk_id, args.name, args.description, args.type, args.status)
    print(f"Successfully created control '{control.name}'.")

def list_controls(args):
    """Lists all controls, optionally filtered by risk."""
    controls = get_controls(args.risk_id)
    for control in controls:
        print(f"- {control.name} (ID: {control.id}) - Type: {control.type}, Status: {control.status}")

def update_control_cmd(args):
    """Updates an existing control."""
    control = update_control(args.control_id, args.name, args.description, args.type, args.status)
    if control:
        print(f"Successfully updated control '{control.name}'.")
    else:
        print(f"Control with ID {args.control_id} not found.")

def delete_control_cmd(args):
    """Deletes a control."""
    if delete_control(args.control_id):
        print(f"Successfully deleted control with ID {args.control_id}.")
    else:
        print(f"Control with ID {args.control_id} not found.")

def add_compliance_item(args):
    """Adds a new compliance item to a project."""
    compliance_item = create_compliance_item(args.project_id, args.name, args.description, args.standard, args.status)
    print(f"Successfully created compliance item '{compliance_item.name}'.")

def list_compliance_items(args):
    """Lists all compliance items, optionally filtered by project."""
    compliance_items = get_compliance_items(args.project_id)
    for item in compliance_items:
        print(f"- {item.name} (ID: {item.id}) - Standard: {item.standard}, Status: {item.status}")

def update_compliance_item_cmd(args):
    """Updates an existing compliance item."""
    item = update_compliance_item(args.compliance_item_id, args.name, args.description, args.standard, args.status)
    if item:
        print(f"Successfully updated compliance item '{item.name}'.")
    else:
        print(f"Compliance item with ID {args.compliance_item_id} not found.")

def delete_compliance_item_cmd(args):
    """Deletes a compliance item."""
    if delete_compliance_item(args.compliance_item_id):
        print(f"Successfully deleted compliance item with ID {args.compliance_item_id}.")
    else:
        print(f"Compliance item with ID {args.compliance_item_id} not found.")

def automate_compliance_check_cmd(args):
    """Automates compliance checks, optionally for a specific project."""
    print("Running automated compliance checks...")
    result = automate_compliance_check(args.project_id)
    print(result)

def add_document(args):
    """Adds a new document to a project."""
    approval_date = datetime.datetime.strptime(args.approval_date, '%Y-%m-%d').date() if args.approval_date else None
    file_content = None
    original_filename = None
    if args.file_path:
        try:
            with open(args.file_path, "rb") as f:
                file_content = f.read()
            original_filename = os.path.basename(args.file_path)
        except FileNotFoundError:
            print(f"Error: File not found at {args.file_path}")
            return
        except Exception as e:
            print(f"Error reading file {args.file_path}: {e}")
            return

    doc = create_document(
        project_id=args.project_id,
        name=args.name,
        type=args.type,
        version=args.version,
        file_content=file_content,
        original_filename=original_filename,
        approval_status=args.approval_status,
        approved_by=args.approved_by,
        approval_date=approval_date
    )
    print(f"Successfully added document '{doc.name}'.")

def list_documents(args):
    """Lists all documents, optionally filtered by project."""
    docs = get_documents(args.project_id)
    for doc in docs:
        print(f"- {doc.name} (ID: {doc.id}) - Type: {doc.type}, Version: {doc.version}, Status: {doc.approval_status}")

def update_document_cmd(args):
    """Updates an existing document."""
    approval_date = datetime.datetime.strptime(args.approval_date, '%Y-%m-%d').date() if args.approval_date else None
    file_content = None
    original_filename = None
    if args.file_path:
        try:
            with open(args.file_path, "rb") as f:
                file_content = f.read()
            original_filename = os.path.basename(args.file_path)
        except FileNotFoundError:
            print(f"Error: File not found at {args.file_path}")
            return
        except Exception as e:
            print(f"Error reading file {args.file_path}: {e}")
            return

    doc = update_document(
        doc_id=args.doc_id,
        name=args.name,
        type=args.type,
        version=args.version,
        file_content=file_content,
        original_filename=original_filename,
        approval_status=args.approval_status,
        approved_by=args.approved_by,
        approval_date=approval_date
    )
    if doc:
        print(f"Successfully updated document '{doc.name}'.")
    else:
        print(f"Document with ID {args.doc_id} not found.")

def delete_document_cmd(args):
    """Deletes a document."""
    if delete_document(args.doc_id):
        print(f"Successfully deleted document with ID {args.doc_id}.")
    else:
        print(f"Document with ID {args.doc_id} not found.")

def generate_document_cmd(args):
    """Generates a document using the LLM."""
    llm_service = LLMService()
    document = llm_service.generate_document(args.prompt, args.project_id)
    print("\nGenerated Document:\n")
    print(document)

def assess_risk_cmd(args):
    """Assesses a risk using the LLM."""
    llm_service = LLMService()
    assessment = llm_service.assess_risk(args.risk_description, args.project_id)
    print("\nRisk Assessment:\n")
    print(assessment)

def list_llm_models_cmd(args):
    """Lists available LLM models."""
    LLMService.list_available_models()

def create_user_cmd(args):
    """Creates a new user (Admin only)."""
    user = create_user(args.username, args.password, args.role)
    print(f"User '{user.username}' ({user.role}) created successfully.")

def list_users_cmd(args):
    """Lists all users (Admin only)."""
    users = get_all_users()
    for user in users:
        print(f"- {user.username} (ID: {user.id}, Role: {user.role})")

def main():
    """The main function of the application."""
    parser = argparse.ArgumentParser(description="Project Audit Tool")
    subparsers = parser.add_subparsers(dest="command")

    # Project Management Commands
    list_projects_parser = subparsers.add_parser("list-projects", help="Lists all projects.")
    list_projects_parser.set_defaults(func=list_projects)

    add_project_parser = subparsers.add_parser("add-project", help="Adds a new project with detailed initiation.")
    add_project_parser.add_argument("name", help="The name of the project.")
    add_project_parser.add_argument("description", help="The description of the project.")
    add_project_parser.add_argument("--pin-id", help="Project Initiation Note ID.", required=False)
    add_project_parser.add_argument("--scope", help="Project scope.", required=False)
    add_project_parser.add_argument("--milestones", help="Project milestones.", required=False)
    add_project_parser.add_argument("--start-date", help="Project start date (YYYY-MM-DD).", required=False)
    add_project_parser.add_argument("--end-date", help="Project end date (YYYY-MM-DD).", required=False)
    add_project_parser.add_argument("--effort-estimation", help="Effort estimation.", required=False)
    add_project_parser.add_argument("--deliverables", help="Project deliverables.", required=False)
    add_project_parser.add_argument("--team-members", help="Comma-separated team members.", required=False)
    add_project_parser.add_argument("--team-size", type=int, help="Size of the team.", required=False)
    add_project_parser.add_argument("--roles-responsibilities", help="Roles and responsibilities.", required=False)
    add_project_parser.add_argument("--sdlc-model", help="SDLC model (e.g., Agile, Waterfall).", required=False)
    add_project_parser.add_argument("--ciso-approved", type=bool, help="CISO approval status (True/False).", required=False, default=False)
    add_project_parser.add_argument("--ciso-approval-date", help="CISO approval date (YYYY-MM-DD).", required=False)
    add_project_parser.set_defaults(func=add_project)

    update_project_parser = subparsers.add_parser("update-project", help="Updates an existing project with detailed initiation.")
    update_project_parser.add_argument("project_id", type=int, help="The ID of the project to update.")
    update_project_parser.add_argument("--name", help="The name of the project.", required=False)
    update_project_parser.add_argument("--description", help="The description of the project.", required=False)
    update_project_parser.add_argument("--pin-id", help="Project Initiation Note ID.", required=False)
    update_project_parser.add_argument("--scope", help="Project scope.", required=False)
    update_project_parser.add_argument("--milestones", help="Project milestones.", required=False)
    update_project_parser.add_argument("--start-date", help="Project start date (YYYY-MM-DD).", required=False)
    update_project_parser.add_argument("--end-date", help="Project end date (YYYY-MM-DD).", required=False)
    update_project_parser.add_argument("--effort-estimation", help="Effort estimation.", required=False)
    update_project_parser.add_argument("--deliverables", help="Project deliverables.", required=False)
    update_project_parser.add_argument("--team-members", help="Comma-separated team members.", required=False)
    update_project_parser.add_argument("--team-size", type=int, help="Size of the team.", required=False)
    update_project_parser.add_argument("--roles-responsibilities", help="Roles and responsibilities.", required=False)
    update_project_parser.add_argument("--sdlc-model", help="SDLC model (e.g., Agile, Waterfall).", required=False)
    update_project_parser.add_argument("--ciso-approved", type=bool, help="CISO approval status (True/False).", required=False)
    update_project_parser.add_argument("--ciso-approval-date", help="CISO approval date (YYYY-MM-DD).", required=False)
    update_project_parser.set_defaults(func=update_project_cmd)

    list_work_packages_parser = subparsers.add_parser("list-work-packages", help="Lists all work packages for a project.")
    list_work_packages_parser.add_argument("project_id", type=int, help="The ID of the project.")
    list_work_packages_parser.set_defaults(func=list_work_packages)

    add_work_package_parser = subparsers.add_parser("add-work-package", help="Adds a new work package to a project.")
    add_work_package_parser.add_argument("project_id", type=int, help="The ID of the project.")
    add_work_package_parser.add_argument("subject", help="The subject of the work package.")
    add_work_package_parser.add_argument("description", help="The description of the work package.")
    add_work_package_parser.set_defaults(func=add_work_package)

    generate_report_parser = subparsers.add_parser("generate-project-report", help="Generates a status report for a project using LLM.")
    generate_report_parser.add_argument("project_id", type=int, help="The ID of the project to generate report for.")
    generate_report_parser.set_defaults(func=generate_project_report_cmd)

    # Audit Logging Commands
    list_audit_logs_parser = subparsers.add_parser("list-audit-logs", help="Lists all audit logs, optionally filtered by project.")
    list_audit_logs_parser.add_argument("--project-id", type=int, help="The ID of the project to filter by.", required=False)
    list_audit_logs_parser.set_defaults(func=list_audit_logs)

    # Risk Management Commands
    add_risk_parser = subparsers.add_parser("add-risk", help="Adds a new risk to a project.")
    add_risk_parser.add_argument("project_id", type=int, help="The ID of the project.")
    add_risk_parser.add_argument("name", help="The name of the risk.")
    add_risk_parser.add_argument("description", help="The description of the risk.")
    add_risk_parser.add_argument("severity", help="The severity of the risk (e.g., High, Medium, Low).")
    add_risk_parser.add_argument("likelihood", help="The likelihood of the risk (e.g., High, Medium, Low).")
    add_risk_parser.add_argument("status", help="The status of the risk (e.g., Open, Closed, Mitigated).")
    add_risk_parser.set_defaults(func=add_risk)

    list_risks_parser = subparsers.add_parser("list-risks", help="Lists all risks, optionally filtered by project.")
    list_risks_parser.add_argument("--project-id", type=int, help="The ID of the project to filter by.", required=False)
    list_risks_parser.set_defaults(func=list_risks)

    update_risk_parser = subparsers.add_parser("update-risk", help="Updates an existing risk.")
    update_risk_parser.add_argument("risk_id", type=int, help="The ID of the risk to update.")
    update_risk_parser.add_argument("--name", help="The new name of the risk.", required=False)
    update_risk_parser.add_argument("--description", help="The new description of the risk.", required=False)
    update_risk_parser.add_argument("--severity", help="The new severity of the risk.", required=False)
    update_risk_parser.add_argument("--likelihood", help="The new likelihood of the risk.", required=False)
    update_risk_parser.add_argument("--status", help="The new status of the risk.", required=False)
    update_risk_parser.set_defaults(func=update_risk_cmd)

    delete_risk_parser = subparsers.add_parser("delete-risk", help="Deletes a risk.")
    delete_risk_parser.add_argument("risk_id", type=int, help="The ID of the risk to delete.")
    delete_risk_parser.set_defaults(func=delete_risk_cmd)

    # Control Management Commands
    add_control_parser = subparsers.add_parser("add-control", help="Adds a new control to a risk.")
    add_control_parser.add_argument("risk_id", type=int, help="The ID of the risk this control mitigates.")
    add_control_parser.add_argument("name", help="The name of the control.")
    add_control_parser.add_argument("description", help="The description of the control.")
    add_control_parser.add_argument("type", help="The type of control (e.g., Preventive, Detective).")
    add_control_parser.add_argument("status", help="The status of the control (e.g., Implemented, In Progress, Not Implemented).")
    add_control_parser.set_defaults(func=add_control)

    list_controls_parser = subparsers.add_parser("list-controls", help="Lists all controls, optionally filtered by risk.")
    list_controls_parser.add_argument("--risk-id", type=int, help="The ID of the risk to filter by.", required=False)
    list_controls_parser.set_defaults(func=list_controls)

    update_control_parser = subparsers.add_parser("update-control", help="Updates an existing control.")
    update_control_parser.add_argument("control_id", type=int, help="The ID of the control to update.")
    update_control_parser.add_argument("--name", help="The new name of the control.", required=False)
    update_control_parser.add_argument("--description", help="The new description of the control.", required=False)
    update_control_parser.add_argument("--type", help="The new type of control.", required=False)
    update_control_parser.add_argument("--status", help="The new status of the control.", required=False)
    update_control_parser.set_defaults(func=update_control_cmd)

    delete_control_parser = subparsers.add_parser("delete-control", help="Deletes a control.")
    delete_control_parser.add_argument("control_id", type=int, help="The ID of the control to delete.")
    delete_control_parser.set_defaults(func=delete_control_cmd)

    # Compliance Management Commands
    add_compliance_item_parser = subparsers.add_parser("add-compliance-item", help="Adds a new compliance item to a project.")
    add_compliance_item_parser.add_argument("project_id", type=int, help="The ID of the project this compliance item belongs to.")
    add_compliance_item_parser.add_argument("name", help="The name of the compliance item.")
    add_compliance_item_parser.add_argument("description", help="The description of the compliance item.")
    add_compliance_item_parser.add_argument("standard", help="The compliance standard (e.g., GDPR, ISO 27001).")
    add_compliance_item_parser.add_argument("status", help="The status of the compliance item (e.g., Compliant, Non-Compliant, In Progress).")
    add_compliance_item_parser.set_defaults(func=add_compliance_item)

    list_compliance_items_parser = subparsers.add_parser("list-compliance-items", help="Lists all compliance items, optionally filtered by project.")
    list_compliance_items_parser.add_argument("--project-id", type=int, help="The ID of the project to filter by.", required=False)
    list_compliance_items_parser.set_defaults(func=list_compliance_items)

    update_compliance_item_parser = subparsers.add_parser("update-compliance-item", help="Updates an existing compliance item.")
    update_compliance_item_parser.add_argument("compliance_item_id", type=int, help="The ID of the compliance item to update.")
    update_compliance_item_parser.add_argument("--name", help="The new name of the compliance item.", required=False)
    update_compliance_item_parser.add_argument("--description", help="The new description of the compliance item.", required=False)
    update_compliance_item_parser.add_argument("--standard", help="The new compliance standard.", required=False)
    update_compliance_item_parser.add_argument("--status", help="The new status of the compliance item.", required=False)
    update_compliance_item_parser.set_defaults(func=update_compliance_item_cmd)

    delete_compliance_item_parser = subparsers.add_parser("delete-compliance-item", help="Deletes a compliance item.")
    delete_compliance_item_parser.add_argument("compliance_item_id", type=int, help="The ID of the compliance item to delete.")
    delete_compliance_item_parser.set_defaults(func=delete_compliance_item_cmd)

    automate_compliance_parser = subparsers.add_parser("automate-compliance", help="Automates compliance checks based on predefined rules.")
    automate_compliance_parser.add_argument("--project-id", type=int, help="Optional: The ID of the project to run checks for. If omitted, checks all projects.", required=False)
    automate_compliance_parser.set_defaults(func=automate_compliance_check_cmd)

    # Document Management Commands
    add_document_parser = subparsers.add_parser("add-document", help="Adds a new document record to a project.")
    add_document_parser.add_argument("project_id", type=int, help="The ID of the project this document belongs to.")
    add_document_parser.add_argument("name", help="The name of the document.")
    add_document_parser.add_argument("type", help="The type of document (e.g., PIN, SRS, HLD, QAP, Email Approval).")
    add_document_parser.add_argument("--version", help="The version of the document.", default="1.0")
    add_document_parser.add_argument("--file-path", help="Path to the document file.", required=False)
    add_document_parser.add_argument("--approval-status", help="Approval status (e.g., Pending, Approved, Rejected).", default="Pending", required=False)
    add_document_parser.add_argument("--approved-by", help="Name of the approver.", required=False)
    add_document_parser.add_argument("--approval-date", help="Approval date (YYYY-MM-DD).", required=False)
    add_document_parser.set_defaults(func=add_document)

    list_documents_parser = subparsers.add_parser("list-documents", help="Lists all documents, optionally filtered by project.")
    list_documents_parser.add_argument("--project-id", type=int, help="The ID of the project to filter by.", required=False)
    list_documents_parser.set_defaults(func=list_documents)

    update_document_parser = subparsers.add_parser("update-document", help="Updates an existing document record.")
    update_document_parser.add_argument("doc_id", type=int, help="The ID of the document to update.")
    update_document_parser.add_argument("--name", help="The new name of the document.", required=False)
    update_document_parser.add_argument("--type", help="The new type of document.", required=False)
    update_document_parser.add_argument("--version", help="The new version of the document.", required=False)
    update_document_parser.add_argument("--file-path", help="Path to the new document file (optional).", required=False)
    update_document_parser.add_argument("--approval-status", help="The new approval status.", required=False)
    update_document_parser.add_argument("--approved-by", help="The new approver.", required=False)
    update_document_parser.add_argument("--approval-date", help="The new approval date (YYYY-MM-DD).", required=False)
    update_document_parser.set_defaults(func=update_document_cmd)

    delete_document_parser = subparsers.add_parser("delete-document", help="Deletes a document record.")
    delete_document_parser.add_argument("doc_id", type=int, help="The ID of the document to delete.")
    delete_document_parser.set_defaults(func=delete_document_cmd)

    # LLM Integration Commands
    generate_document_parser = subparsers.add_parser("generate-document", help="Generates a document using the LLM.")
    generate_document_parser.add_argument("prompt", help="The prompt for document generation.")
    generate_document_parser.add_argument("--project-id", type=int, help="The ID of the project to use for context.", required=False)
    generate_document_parser.set_defaults(func=generate_document_cmd)

    assess_risk_parser = subparsers.add_parser("assess-risk", help="Assesses a risk using the LLM.")
    assess_risk_parser.add_argument("risk_description", help="The description of the risk to assess.")
    assess_risk_parser.add_argument("--project-id", type=int, help="The ID of the project to use for context.", required=False)
    assess_risk_parser.set_defaults(func=assess_risk_cmd)

    list_llm_models_parser = subparsers.add_parser("list-llm-models", help="Lists available LLM models.")
    list_llm_models_parser.set_defaults(func=list_llm_models_cmd)

    # User Management Commands
    create_user_parser = subparsers.add_parser("create-user", help="Creates a new user (Admin only).")
    create_user_parser.add_argument("username", help="The username for the new user.")
    create_user_parser.add_argument("password", help="The password for the new user.")
    create_user_parser.add_argument("--role", help="The role of the new user (user or admin).", default="user", required=False)
    create_user_parser.set_defaults(func=create_user_cmd)

    list_users_parser = subparsers.add_parser("list-users", help="Lists all users (Admin only).")
    list_users_parser.set_defaults(func=list_users_cmd)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
