from database import SessionLocal, Project, WorkPackage, Risk, Compliance, Document
from services.audit_logging import create_audit_log
from services.risk_management import get_risks
from services.compliance_management import get_compliance_items
from services.document_management import get_documents
from services.llm_service import LLMService
import datetime

def create_project(name, description, pin_id=None, scope=None, milestones=None, start_date=None, end_date=None, effort_estimation=None, deliverables=None, team_members=None, team_size=None, roles_responsibilities=None, sdlc_model=None, ciso_approved=False, ciso_approval_date=None):
    """Creates a new project with detailed initiation information."""
    db = SessionLocal()
    project = Project(
        name=name,
        description=description,
        pin_id=pin_id,
        scope=scope,
        milestones=milestones,
        start_date=start_date,
        end_date=end_date,
        effort_estimation=effort_estimation,
        deliverables=deliverables,
        team_members=team_members,
        team_size=team_size,
        roles_responsibilities=roles_responsibilities,
        sdlc_model=sdlc_model,
        ciso_approved=ciso_approved,
        ciso_approval_date=ciso_approval_date
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    db.close()
    create_audit_log(project.id, "Project Created", f"Project '{name}' was created with PIN ID {pin_id}.")
    return project

def get_projects():
    """Gets all projects."""
    db = SessionLocal()
    projects = db.query(Project).all()
    db.close()
    return projects

def get_project_by_id(project_id):
    """Gets a project by its ID."""
    db = SessionLocal()
    project = db.query(Project).filter(Project.id == project_id).first()
    db.close()
    return project

def update_project(project_id, name=None, description=None, pin_id=None, scope=None, milestones=None, start_date=None, end_date=None, effort_estimation=None, deliverables=None, team_members=None, team_size=None, roles_responsibilities=None, sdlc_model=None, ciso_approved=None, ciso_approval_date=None):
    """Updates an existing project's details."""
    db = SessionLocal()
    project = db.query(Project).filter(Project.id == project_id).first()
    if project:
        if name: project.name = name
        if description: project.description = description
        if pin_id: project.pin_id = pin_id
        if scope: project.scope = scope
        if milestones: project.milestones = milestones
        if start_date: project.start_date = start_date
        if end_date: project.end_date = end_date
        if effort_estimation: project.effort_estimation = effort_estimation
        if deliverables: project.deliverables = deliverables
        if team_members: project.team_members = team_members
        if team_size: project.team_size = team_size
        if roles_responsibilities: project.roles_responsibilities = roles_responsibilities
        if sdlc_model: project.sdlc_model = sdlc_model
        if ciso_approved is not None: project.ciso_approved = ciso_approved
        if ciso_approval_date: project.ciso_approval_date = ciso_approval_date
        db.commit()
        db.refresh(project)
        db.close()
        create_audit_log(project_id, "Project Updated", f"Project '{project.name}' (ID: {project_id}) details updated.")
        return project
    db.close()
    return None

def create_work_package(project_id, subject, description):
    """Creates a new work package for a project."""
    db = SessionLocal()
    work_package = WorkPackage(project_id=project_id, subject=subject, description=description)
    db.add(work_package)
    db.commit()
    db.refresh(work_package)
    db.close()
    create_audit_log(project_id, "Work Package Created", f"Work package '{subject}' was created for project ID {project_id}.")
    return work_package

def get_work_packages(project_id):
    """Gets all work packages for a project."""
    db = SessionLocal()
    work_packages = db.query(WorkPackage).filter(WorkPackage.project_id == project_id).all()
    db.close()
    return work_packages

def generate_project_status_report(project_id: int) -> str:
    """
    Generates a comprehensive status report for a given project using LLM.
    The report includes project details, work packages, risks, compliance items, and documents.
    """
    db = SessionLocal()
    llm_service = LLMService()
    report_content = []

    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return f"Error: Project with ID {project_id} not found."

        report_content.append(f"Project Status Report for: {project.name} (ID: {project.id})")
        report_content.append("----------------------------------------------------")
        report_content.append("\n### Project Details:")
        report_content.append(f"- Description: {project.description}")
        report_content.append(f"- PIN ID: {project.pin_id or 'N/A'}")
        report_content.append(f"- Scope: {project.scope or 'N/A'}")
        report_content.append(f"- Milestones: {project.milestones or 'N/A'}")
        report_content.append(f"- Start Date: {project.start_date or 'N/A'}")
        report_content.append(f"- End Date: {project.end_date or 'N/A'}")
        report_content.append(f"- Effort Estimation: {project.effort_estimation or 'N/A'}")
        report_content.append(f"- Deliverables: {project.deliverables or 'N/A'}")
        report_content.append(f"- Team Members: {project.team_members or 'N/A'}")
        report_content.append(f"- Team Size: {project.team_size or 'N/A'}")
        report_content.append(f"- Roles & Responsibilities: {project.roles_responsibilities or 'N/A'}")
        report_content.append(f"- SDLC Model: {project.sdlc_model or 'N/A'}")
        report_content.append(f"- CISO Approved: {project.ciso_approved}")
        report_content.append(f"- CISO Approval Date: {project.ciso_approval_date or 'N/A'}")

        # Work Packages
        work_packages = get_work_packages(project_id)
        report_content.append("\n### Work Packages:")
        if work_packages:
            for wp in work_packages:
                report_content.append(f"- WP ID: {wp.id}, Subject: {wp.subject}, Description: {wp.description}")
        else:
            report_content.append("No work packages found.")

        # Risks
        risks = get_risks(project_id)
        report_content.append("\n### Risks:")
        if risks:
            for risk in risks:
                report_content.append(f"- Risk ID: {risk.id}, Name: {risk.name}, Severity: {risk.severity}, Likelihood: {risk.likelihood}, Status: {risk.status}")
        else:
            report_content.append("No risks found.")

        # Compliance Items
        compliance_items = get_compliance_items(project_id)
        report_content.append("\n### Compliance Items:")
        if compliance_items:
            for item in compliance_items:
                report_content.append(f"- Compliance ID: {item.id}, Name: {item.name}, Standard: {item.standard}, Status: {item.status}")
        else:
            report_content.append("No compliance items found.")

        # Documents
        documents = get_documents(project_id)
        report_content.append("\n### Documents:")
        if documents:
            for doc in documents:
                report_content.append(f"- Doc ID: {doc.id}, Name: {doc.name}, Type: {doc.type}, Version: {doc.version}, Link: {doc.link}, Approval: {doc.approval_status}")
        else:
            report_content.append("No documents found.")

        # Construct the prompt for the LLM
        full_context = "\n".join(report_content)
        prompt = f"""Based on the following project data, generate a concise and professional project status report. Highlight key progress, any significant risks or compliance issues, and overall project health. Focus on summarizing the provided information.

{full_context}"""

        # Generate report using LLM
        generated_report = llm_service.generate_document(prompt)
        create_audit_log(project_id, "Status Report Generated", f"Status report generated for project ID {project_id}.")
        return generated_report

    except Exception as e:
        create_audit_log(project_id, "Status Report Generation Failed", f"Failed to generate status report for project ID {project_id}: {e}")
        return f"An error occurred during report generation: {e}"
    finally:
        db.close()