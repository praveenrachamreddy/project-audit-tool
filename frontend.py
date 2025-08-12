# frontend.py

import os
import streamlit as st
import pandas as pd
from services.project_management import get_projects, create_project, create_work_package, get_work_packages, update_project, get_project_by_id, generate_project_status_report
from services.audit_logging import get_audit_logs
from services.risk_management import get_risks, create_risk, update_risk, delete_risk
from services.control_management import create_control, get_controls, update_control, delete_control
from services.compliance_management import create_compliance_item, get_compliance_items, update_compliance_item, delete_compliance_item, automate_compliance_check
from services.document_management import create_document, get_documents, update_document, delete_document
from services.llm_service import LLMService
from services.user_management import authenticate_user, create_user, get_all_users, add_user_to_project, remove_user_from_project, get_user_role_for_project, get_users_for_project
from database import init_db, ProjectRole
from dotenv import load_dotenv
import datetime
import io
import sys

# Load environment variables from .env file at the very beginning
load_dotenv()

# Initialize the database when the app starts
init_db()

st.set_page_config(layout="wide")

def login_page():
    st.title("Project Audit Tool")
    with st.form("login_form"):
        st.header("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            user = authenticate_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user.id
                st.session_state.username = user.username
                st.rerun()
            else:
                st.error("Invalid username or password")
                st.session_state.logged_in = False

def logout():
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.rerun()

def main_app():
    # --- Header ---
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title("Project Audit Tool")
    with col2:
        with st.popover("User", use_container_width=True):
            st.write(f"Logged in as **{st.session_state.username}**")
            if st.button("Logout"):
                logout()

    # --- Data Fetching ---
    all_projects = get_projects()
    all_risks = get_risks()
    all_controls = get_controls()
    all_compliance_items = get_compliance_items()
    all_audit_logs = get_audit_logs()
    all_users = get_all_users()

    def get_project_name(project_id):
        return next((p.name for p in all_projects if p.id == project_id), "Unknown Project")

    def get_risk_name(risk_id):
        return next((r.name for r in all_risks if r.id == risk_id), "Unknown Risk")

    # --- Tabs ---
    tab_dashboard, tab_projects, tab_risks, tab_audit, tab_llm, tab_reports, tab_users = st.tabs([
        "Dashboards",
        "Project Management",
        "Risk & Control Management",
        "Audit Logs",
        "LLM Integration",
        "Reports & Export",
        "User Management"
    ])

    # --- Dashboard Tab ---
    with tab_dashboard:
        st.header("Overall Dashboards")

        st.subheader("Overall Metrics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="📊 Total Projects", value=len(all_projects))
        with col2:
            st.metric(label="🚨 Total Risks", value=len(all_risks))
        with col3:
            st.metric(label="🛡️ Total Compliance Items", value=len(all_compliance_items))

        st.markdown("--- ")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Project Overview")
            if all_projects:
                project_data = pd.DataFrame([{"Project": p.name, "Work Packages": len(get_work_packages(p.id))} for p in all_projects]).set_index("Project")
                st.bar_chart(project_data)
                with st.container(height=200):
                    st.dataframe(project_data, use_container_width=True)
            else:
                st.info("No projects to display in dashboard.")

        with col2:
            st.subheader("Risk Overview")
            if all_risks:
                risk_severity_counts = pd.Series([r.severity for r in all_risks]).value_counts()
                st.bar_chart(risk_severity_counts)
                with st.container(height=200):
                    st.dataframe(risk_severity_counts, use_container_width=True)
            else:
                st.info("No risks to display in dashboard.")
        
        col3, col4 = st.columns(2)

        with col3:
            st.subheader("Compliance Overview")
            if all_compliance_items:
                compliance_status_counts = pd.Series([c.status for c in all_compliance_items]).value_counts()
                st.bar_chart(compliance_status_counts)
                with st.container(height=200):
                    st.dataframe(compliance_status_counts, use_container_width=True)
            else:
                st.info("No compliance items to display in dashboard.")
        
        with col4:
            st.subheader("Audit Log Overview")
            st.metric(label="Total Audit Log Entries", value=len(all_audit_logs))


    # --- Project Management Tab ---
    with tab_projects:
        st.header("Project Management")

        with st.expander("Create New Project / Project Initiation Note (PIN)"):
            with st.form("new_project_form"):
                st.subheader("Core Project Details")
                project_name = st.text_input("Project Name*")
                project_description = st.text_area("Project Description*")
                
                st.subheader("Project Initiation Note (PIN) Details")
                pin_id = st.text_input("PIN ID")
                scope = st.text_area("Project Scope")
                milestones = st.text_area("Key Milestones")
                start_date = st.date_input("Start Date", value=None)
                end_date = st.date_input("End Date", value=None)
                effort_estimation = st.text_input("Effort Estimation")
                deliverables = st.text_area("Deliverables")
                team_members = st.text_area("Team Members")
                team_size = st.number_input("Team Size", min_value=1, value=1)
                roles_responsibilities = st.text_area("Roles & Responsibilities")
                sdlc_model = st.selectbox("SDLC Model", ["Waterfall", "Agile", "DevOps", "Spiral", "V-Model", "Other"])
                ciso_approved = st.checkbox("CISO Approved")
                ciso_approval_date = st.date_input("CISO Approval Date", value=None) if ciso_approved else None
                
                submitted_project = st.form_submit_button("Create Project")
                if submitted_project:
                    if project_name and project_description:
                        try:
                            new_project = create_project(
                                name=project_name,
                                description=project_description,
                                pin_id=pin_id if pin_id else None,
                                scope=scope if scope else None,
                                milestones=milestones if milestones else None,
                                start_date=start_date,
                                end_date=end_date,
                                effort_estimation=effort_estimation if effort_estimation else None,
                                deliverables=deliverables if deliverables else None,
                                team_members=team_members if team_members else None,
                                team_size=team_size,
                                roles_responsibilities=roles_responsibilities if roles_responsibilities else None,
                                sdlc_model=sdlc_model,
                                ciso_approved=ciso_approved,
                                ciso_approval_date=ciso_approval_date
                            )
                            add_user_to_project(st.session_state.user_id, new_project.id, ProjectRole.Admin)
                            st.success(f"Project '{project_name}' created successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error creating project: {e}")
                    else:
                        st.error("Please fill in the project name and description.")

        st.subheader("Existing Projects")
        if all_projects:
            project_display_data = []
            for project in all_projects:
                project_display_data.append({
                    "ID": project.id,
                    "Name": project.name,
                    "Description": project.description,
                    "PIN ID": project.pin_id or 'N/A',
                    "Scope": project.scope or 'N/A',
                    "Start Date": project.start_date or 'N/A',
                    "End Date": project.end_date or 'N/A',
                    "CISO Approved": project.ciso_approved
                })
            st.dataframe(pd.DataFrame(project_display_data))

            st.markdown("### Detailed Project View")
            selected_project_id_detail = st.selectbox(
                "Select a Project for Detailed View and Management", 
                options=[p.id for p in all_projects], 
                format_func=lambda x: next((p.name for p in all_projects if p.id == x), ""), 
                key="detailed_project_select"
            )

            if selected_project_id_detail:
                project = next((p for p in all_projects if p.id == selected_project_id_detail), None)
                if project:
                    current_user_role = get_user_role_for_project(st.session_state.user_id, project.id)
                    if not current_user_role:
                        st.warning("You do not have access to this project.")
                    else:
                        st.markdown(f"### 📝 {project.name} (ID: {project.id})")
                        st.write(f"**Description:** {project.description}")

                        # --- Core Details ---
                        st.markdown("#### Core Details")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(label="PIN ID", value=project.pin_id or "N/A")
                        with col2:
                            st.metric(label="Start Date", value=str(project.start_date) if project.start_date else "N/A")
                        with col3:
                            st.metric(label="End Date", value=str(project.end_date) if project.end_date else "N/A")

                        # --- Scope and Milestones ---
                        st.markdown("#### Scope & Milestones")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Scope**")
                            st.info(project.scope or "Not defined")
                        with col2:
                            st.markdown("**Milestones**")
                            st.info(project.milestones or "Not defined")

                        # --- Team and Approvals ---
                        st.markdown("#### Team & Approvals")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(label="Team Size", value=project.team_size or "N/A")
                            st.markdown("**Team Members**")
                            st.info(project.team_members or "Not defined")
                        with col2:
                            st.markdown("**Roles & Responsibilities**")
                            st.info(project.roles_responsibilities or "Not defined")
                        with col3:
                            st.markdown("**CISO Approval**")
                            st.success(f"Approved: {project.ciso_approved}")
                            st.markdown("**Approval Date**")
                            st.info(str(project.ciso_approval_date) if project.ciso_approval_date else "N/A")

                        st.markdown("--- ")
                        
                        # --- User Management for this Project ---
                        if current_user_role == ProjectRole.Admin:
                            st.markdown("#### 👥 User Management for this Project")
                            project_users = get_users_for_project(project.id)
                            st.dataframe(pd.DataFrame([{"User": u.user.username, "Role": u.role.value} for u in project_users]))

                            with st.expander("Add User to Project"):
                                with st.form(f"add_user_form_{project.id}"):
                                    user_to_add = st.selectbox("Select User", options=[u.id for u in all_users], format_func=lambda x: next((u.username for u in all_users if u.id == x), ""))
                                    role_to_assign = st.selectbox("Select Role", options=[r.value for r in ProjectRole])
                                    submitted_add_user = st.form_submit_button("Add User")
                                    if submitted_add_user:
                                        add_user_to_project(user_to_add, project.id, ProjectRole(role_to_assign))
                                        st.success(f"User added to project!")
                                        st.rerun()

                        st.markdown("--- ")

                        col_wp, col_comp, col_docs = st.columns(3)

                        with col_wp:
                            st.markdown("#### 📦 Work Packages")
                            work_packages = get_work_packages(project.id)
                            if work_packages:
                                wp_data = []
                                for wp in work_packages:
                                    wp_data.append({"ID": wp.id, "Subject": wp.subject, "Description": wp.description})
                                with st.container(height=300):
                                    st.dataframe(pd.DataFrame(wp_data), use_container_width=True)
                            else:
                                st.info("No work packages for this project.")

                            if current_user_role in [ProjectRole.Admin, ProjectRole.Editor]:
                                with st.expander(f"Add Work Package to {project.name}"):
                                    with st.form(f"new_work_package_form_{project.id}"):
                                        wp_subject = st.text_input("Work Package Subject")
                                        wp_description = st.text_area("Work Package Description")
                                        submitted_wp = st.form_submit_button("Add Work Package")
                                        if submitted_wp:
                                            if wp_subject and wp_description:
                                                try:
                                                    create_work_package(project.id, wp_subject, wp_description)
                                                    st.success(f"Work package '{wp_subject}' added to {project.name}!")
                                                    st.rerun()
                                                except Exception as e:
                                                    st.error(f"Error creating work package: {e}")
                                            else:
                                                st.error("Please fill in both work package subject and description.")

                        with col_comp:
                            st.markdown("#### 🛡️ Compliance Items")
                            compliance_items = get_compliance_items(project.id)
                            if compliance_items:
                                comp_data = []
                                for item in compliance_items:
                                    comp_data.append({"ID": item.id, "Name": item.name, "Standard": item.standard, "Status": item.status})
                                with st.container(height=300):
                                    st.dataframe(pd.DataFrame(comp_data), use_container_width=True)
                            else:
                                st.info("No compliance items for this project.")

                            if current_user_role in [ProjectRole.Admin, ProjectRole.Editor]:
                                with st.expander(f"Add Compliance Item to {project.name}"):
                                    with st.form(f"new_compliance_item_form_{project.id}"):
                                        comp_name = st.text_input("Compliance Item Name")
                                        comp_description = st.text_area("Compliance Item Description")
                                        comp_standard = st.text_input("Compliance Standard (e.g., GDPR, ISO 27001)")
                                        comp_status = st.selectbox("Compliance Status", ["Compliant", "Non-Compliant", "In Progress"])
                                        submitted_comp = st.form_submit_button("Add Compliance Item")
                                        if submitted_comp:
                                            if comp_name and comp_description and comp_standard:
                                                try:
                                                    create_compliance_item(project.id, comp_name, comp_description, comp_standard, comp_status)
                                                    st.success(f"Compliance item '{comp_name}' added to {project.name}!")
                                                    st.rerun()
                                                except Exception as e:
                                                    st.error(f"Error creating compliance item: {e}")
                                            else:
                                                st.error("Please fill in all compliance item details.")
                        
                        with col_docs:
                            st.markdown("#### 📄 Documents")
                            documents = get_documents(project.id)
                            if documents:
                                doc_data = []
                                for doc in documents:
                                    # Extract original filename from the stored link (path)
                                    original_filename = os.path.basename(doc.link).split("_", 1)[-1] if doc.link else "N/A"
                                    doc_data.append({
                                        "ID": doc.id,
                                        "Name": doc.name,
                                        "Type": doc.type,
                                        "Version": doc.version,
                                        "Approval Status": doc.approval_status,
                                        "Approved By": doc.approved_by if doc.approved_by else 'N/A',
                                        "Approval Date": doc.approval_date if doc.approval_date else 'N/A',
                                        "Original Filename": original_filename,
                                        "Link": doc.link # Keep link for internal use, not directly displayed
                                    })
                                docs_df = pd.DataFrame(doc_data)
                                with st.container(height=300):
                                    st.dataframe(docs_df.drop(columns=["Link"]), use_container_width=True)

                                # Add download buttons for each document
                                st.markdown("**Download Documents:**")
                                for doc in documents:
                                    if doc.link and os.path.exists(doc.link):
                                        try:
                                            with open(doc.link, "rb") as f:
                                                bytes_data = f.read()
                                            original_filename = os.path.basename(doc.link).split("_", 1)[-1]
                                            st.download_button(
                                                label=f"Download {doc.name} ({original_filename})",
                                                data=bytes_data,
                                                file_name=original_filename,
                                                mime="application/octet-stream", # Generic mime type
                                                key=f"download_doc_{doc.id}"
                                            )
                                        except Exception as e:
                                            st.warning(f"Could not prepare {doc.name} for download: {e}")
                                    else:
                                        st.info(f"File for {doc.name} not found or not uploaded.")
                            else:
                                st.info("No documents for this project.")

                            if current_user_role in [ProjectRole.Admin, ProjectRole.Editor]:
                                with st.expander(f"Add New Document to {project.name}"):
                                    with st.form(f"new_document_form_{project.id}"):
                                        doc_name = st.text_input("Document Name*")
                                        doc_type = st.selectbox("Document Type", ["PIN", "Contract", "SRS", "URS", "RFP", "HLD", "LLD", "QAP", "PMP", "CMP", "Email Approval", "User Guidelines", "Other"])
                                        doc_version = st.text_input("Version", value="1.0")
                                        uploaded_file = st.file_uploader("Upload Document File* (PDF, TXT, CSV, Images, EML, MSG)", type=["pdf", "txt", "csv", "png", "jpg", "jpeg", "gif", "eml", "msg"], key=f"doc_uploader_{project.id}")
                                        doc_approval_status = st.selectbox("Approval Status", ["Pending", "Approved", "Rejected"])
                                        doc_approved_by = st.text_input("Approved By (Name)")
                                        doc_approval_date = st.date_input("Approval Date", value=None)
                                        submitted_doc = st.form_submit_button("Add Document")
                                        if submitted_doc:
                                            if doc_name and uploaded_file:
                                                try:
                                                    create_document(
                                                        project_id=project.id,
                                                        name=doc_name,
                                                        type=doc_type,
                                                        version=doc_version,
                                                        file_content=uploaded_file.read(),
                                                        original_filename=uploaded_file.name,
                                                        approval_status=doc_approval_status,
                                                        approved_by=doc_approved_by if doc_approved_by else None,
                                                        approval_date=doc_approval_date
                                                    )
                                                    st.success(f"Document '{doc_name}' added to {project.name}!")
                                                    st.rerun()
                                                except Exception as e:
                                                    st.error(f"Error creating document: {e}")
                                            else:
                                                st.error("Please fill in document name and upload a file.")

                                # Update Document Form (New Expander)
                                with st.expander(f"Update Existing Document for {project.name}"):
                                    if documents:
                                        doc_selection_options = {d.id: d.name for d in documents}
                                        selected_doc_id = st.selectbox("Select Document to Update", options=list(doc_selection_options.keys()), format_func=lambda x: doc_selection_options[x], key=f"update_doc_select_{project.id}")
                                        
                                        if selected_doc_id:
                                            selected_doc = next((d for d in documents if d.id == selected_doc_id), None)
                                            if selected_doc:
                                                with st.form(f"update_document_form_{selected_doc.id}"):
                                                    st.subheader(f"Update Details for {selected_doc.name}")
                                                    updated_doc_name = st.text_input("Document Name", value=selected_doc.name)
                                                    doc_types = ["PIN", "Contract", "SRS", "URS", "RFP", "HLD", "LLD", "QAP", "PMP", "CMP", "Email Approval", "User Guidelines", "Other"]
                                                    try:
                                                        doc_type_index = doc_types.index(selected_doc.type) if selected_doc.type in doc_types else 0
                                                    except:
                                                        doc_type_index = 0
                                                    updated_doc_type = st.selectbox("Document Type", doc_types, index=doc_type_index)
                                                    updated_doc_version = st.text_input("Version", value=selected_doc.version)
                                                    updated_uploaded_file = st.file_uploader("Upload New Document File (Optional)", type=["pdf", "txt", "csv", "png", "jpg", "jpeg", "gif", "eml", "msg"], key=f"update_doc_uploader_{selected_doc.id}")
                                                    approval_statuses = ["Pending", "Approved", "Rejected"]
                                                    try:
                                                        approval_status_index = approval_statuses.index(selected_doc.approval_status) if selected_doc.approval_status in approval_statuses else 0
                                                    except:
                                                        approval_status_index = 0
                                                    updated_doc_approval_status = st.selectbox("Approval Status", approval_statuses, index=approval_status_index)
                                                    updated_doc_approved_by = st.text_input("Approved By (Name)", value=selected_doc.approved_by if selected_doc.approved_by else "")
                                                    updated_doc_approval_date = st.date_input("Approval Date", value=selected_doc.approval_date if selected_doc.approval_date else None)

                                                    submitted_update_doc = st.form_submit_button("Update Document")
                                                    if submitted_update_doc:
                                                        file_content_to_pass = None
                                                        original_filename_to_pass = None
                                                        if updated_uploaded_file:
                                                            file_content_to_pass = updated_uploaded_file.read()
                                                            original_filename_to_pass = updated_uploaded_file.name

                                                        try:
                                                            update_document(
                                                                doc_id=selected_doc.id,
                                                                name=updated_doc_name,
                                                                type=updated_doc_type,
                                                                version=updated_doc_version,
                                                                file_content=file_content_to_pass,
                                                                original_filename=original_filename_to_pass,
                                                                approval_status=updated_doc_approval_status,
                                                                approved_by=updated_doc_approved_by if updated_doc_approved_by else None,
                                                                approval_date=updated_doc_approval_date
                                                            )
                                                            st.success(f"Document '{updated_doc_name}' updated successfully!")
                                                            st.rerun()
                                                        except Exception as e:
                                                            st.error(f"Error updating document: {e}")
                                    else:
                                        st.info("No documents to update for this project.")

                        if current_user_role == ProjectRole.Admin:
                            st.markdown("---")
                            # Automated Compliance Check Button
                            if st.button(f"Run Automated Compliance Check for {project.name}", key=f"auto_comp_check_{project.id}"):
                                with st.spinner(f"Running automated compliance checks for {project.name}..."):
                                    result = automate_compliance_check(project.id)
                                    st.success(result)
                                    st.rerun()
        else:
            st.info("No projects found. Create one above!")

    # --- Risk & Control Management Tab ---
    with tab_risks:
        st.header("🚨 Risk & Control Management")

        with st.expander("Create New Risk"):
            with st.form("new_risk_form"):
                if all_projects:
                    project_options = {p.id: p.name for p in all_projects}
                    risk_project_id = st.selectbox("Select Project for Risk", options=list(project_options.keys()), format_func=lambda x: project_options[x])
                else:
                    st.warning("Create a project first to add risks.")
                    risk_project_id = None

                risk_name = st.text_input("Risk Name")
                risk_description = st.text_area("Risk Description")
                risk_severity = st.selectbox("Severity", ["Low", "Medium", "High"])
                risk_likelihood = st.selectbox("Likelihood", ["Low", "Medium", "High"])
                risk_status = st.selectbox("Status", ["Open", "Mitigated", "Closed"])
                submitted_risk = st.form_submit_button("Create Risk")
                if submitted_risk:
                    if risk_project_id and risk_name and risk_description:
                        try:
                            create_risk(risk_project_id, risk_name, risk_description, risk_severity, risk_likelihood, risk_status)
                            st.success(f"Risk '{risk_name}' created successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error creating risk: {e}")
                    else:
                        st.error("Please fill in all risk details.")

        st.subheader("Existing Risks")
        if all_risks:
            risk_display_data = []
            for risk in all_risks:
                risk_display_data.append({
                    "ID": risk.id,
                    "Name": risk.name,
                    "Project": get_project_name(risk.project_id),
                    "Description": risk.description,
                    "Severity": risk.severity,
                    "Likelihood": risk.likelihood,
                    "Status": risk.status
                })
            st.dataframe(pd.DataFrame(risk_display_data), use_container_width=True)

            st.markdown("### Detailed Risk View")
            risk_selection_options = {r.id: r.name for r in all_risks}
            selected_risk_id_detail = st.selectbox("Select a Risk for Detailed View and Management", options=list(risk_selection_options.keys()), format_func=lambda x: risk_selection_options[x], key="detailed_risk_select")

            if selected_risk_id_detail:
                risk = next((r for r in all_risks if r.id == selected_risk_id_detail), None)
                if risk:
                    current_user_role = get_user_role_for_project(st.session_state.user_id, risk.project_id)
                    if not current_user_role:
                        st.warning("You do not have access to this risk.")
                    else:
                        st.markdown(f"#### {risk.name} (ID: {risk.id}) - Project: {get_project_name(risk.project_id)}")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(label="Severity", value=risk.severity)
                        with col2:
                            st.metric(label="Likelihood", value=risk.likelihood)
                        with col3:
                            st.metric(label="Status", value=risk.status)

                        st.markdown("**Description**")
                        st.info(risk.description)

                        st.markdown("--- ")
                        st.markdown("#### 🛡️ Controls")
                        controls = get_controls(risk.id)
                        if controls:
                            control_data = []
                            for control in controls:
                                control_data.append({"ID": control.id, "Name": control.name, "Description": control.description, "Type": control.type, "Status": control.status})
                            with st.container(height=300):
                                st.dataframe(pd.DataFrame(control_data), use_container_width=True)
                        else:
                            st.info("No controls for this risk.")

                        if current_user_role in [ProjectRole.Admin, ProjectRole.Editor]:
                            with st.expander(f"Add Control to {risk.name}"):
                                with st.form(f"new_control_form_{risk.id}"):
                                    control_name = st.text_input("Control Name")
                                    control_description = st.text_area("Control Description")
                                    control_type = st.selectbox("Control Type", ["Preventive", "Detective", "Corrective"])
                                    control_status = st.selectbox("Control Status", ["Implemented", "In Progress", "Not Implemented"])
                                    submitted_control = st.form_submit_button("Add Control")
                                    if submitted_control:
                                        if control_name and control_description:
                                            try:
                                                create_control(risk.id, control_name, control_description, control_type, control_status)
                                                st.success(f"Control '{control_name}' added to {risk.name}!")
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"Error creating control: {e}")
                                        else:
                                            st.error("Please fill in all control details.")
        else:
            st.info("No risks found. Create one above!")

    # --- Audit Logs Tab ---
    with tab_audit:
        st.header("📜 Audit Logs")
        
        project_options = ["All Projects"] + [p.name for p in all_projects]
        selected_project_name = st.selectbox("Filter by Project", options=project_options)

        if all_audit_logs:
            log_data = []
            for log in all_audit_logs:
                log_data.append({
                    "Timestamp": log.timestamp,
                    "Project ID": log.project_id,
                    "Project": get_project_name(log.project_id),
                    "Action": log.action,
                    "Details": log.details
                })
            
            log_df = pd.DataFrame(log_data)

            if selected_project_name != "All Projects":
                log_df = log_df[log_df["Project"] == selected_project_name]

            st.dataframe(log_df.drop(columns=["Project ID"]), use_container_width=True)
        else:
            st.info("No audit logs found.")

    # --- LLM Integration Tab ---
    with tab_llm:
        st.header("🧠 LLM Integration")

        llm_service = LLMService()

        project_options = {p.id: p.name for p in all_projects}
        selected_project_id_llm = st.selectbox("Select a Project for Context", options=[None] + list(project_options.keys()), format_func=lambda x: "General (No Context)" if x is None else project_options[x], key="llm_project_select")

        with st.expander("Generate Document"):
            with st.form("generate_document_form"):
                doc_prompt = st.text_area("Prompt for Document Generation")
                submitted_doc_prompt = st.form_submit_button("Generate Document")
                if submitted_doc_prompt and doc_prompt:
                    with st.spinner("Generating document..."):
                        try:
                            generated_doc = llm_service.generate_document(doc_prompt, selected_project_id_llm)
                            st.write(generated_doc)
                        except Exception as e:
                            st.error(f"Error generating document: {e}")

        with st.expander("Assess Risk with LLM"):
            with st.form("assess_risk_form"):
                risk_desc_llm = st.text_area("Risk Description for LLM Assessment")
                submitted_risk_desc = st.form_submit_button("Assess Risk")
                if submitted_risk_desc and risk_desc_llm:
                    with st.spinner("Assessing risk..."):
                        try:
                            risk_assessment = llm_service.assess_risk(risk_desc_llm, selected_project_id_llm)
                            st.write(risk_assessment)
                        except Exception as e:
                            st.error(f"Error assessing risk: {e}")

    # --- Reports & Export Tab ---
    with tab_reports:
        st.header("Reports & Export")

        st.subheader("Export Data to CSV")

        # Export Projects
        if all_projects:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("Projects Data Preview")
            with col2:
                st.download_button(
                    label="Download Projects as CSV",
                    data=pd.DataFrame([{"ID": p.id, "Name": p.name, "Description": p.description} for p in all_projects]).to_csv(index=False).encode('utf-8'),
                    file_name="projects.csv",
                    mime="text/csv",
                )
            projects_df = pd.DataFrame([{"ID": p.id, "Name": p.name, "Description": p.description} for p in all_projects])
            st.dataframe(projects_df)
        else:
            st.info("No projects to export.")

        # Export Risks
        if all_risks:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("Risks Data Preview")
            with col2:
                st.download_button(
                    label="Download Risks as CSV",
                    data=pd.DataFrame([{
                        "ID": r.id,
                        "Project ID": r.project_id,
                        "Project Name": get_project_name(r.project_id),
                        "Name": r.name,
                        "Description": r.description,
                        "Severity": r.severity,
                        "Likelihood": r.likelihood,
                        "Status": r.status
                    } for r in all_risks]).to_csv(index=False).encode('utf-8'),
                    file_name="risks.csv",
                    mime="text/csv",
                )
            risks_df = pd.DataFrame([{
                "ID": r.id,
                "Project ID": r.project_id,
                "Project Name": get_project_name(r.project_id),
                "Name": r.name,
                "Description": r.description,
                "Severity": r.severity,
                "Likelihood": r.likelihood,
                "Status": r.status
            } for r in all_risks])
            st.dataframe(risks_df)
        else:
            st.info("No risks to export.")

        # Export Controls
        if all_controls:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("Controls Data Preview")
            with col2:
                st.download_button(
                    label="Download Controls as CSV",
                    data=pd.DataFrame([{
                        "ID": c.id,
                        "Risk ID": c.risk_id,
                        "Risk Name": get_risk_name(c.risk_id),
                        "Name": c.name,
                        "Description": c.description,
                        "Type": c.type,
                        "Status": c.status
                    } for c in all_controls]).to_csv(index=False).encode('utf-8'),
                    file_name="controls.csv",
                    mime="text/csv",
                )
            controls_df = pd.DataFrame([{
                "ID": c.id,
                "Risk ID": c.risk_id,
                "Risk Name": get_risk_name(c.risk_id),
                "Name": c.name,
                "Description": c.description,
                "Type": c.type,
                "Status": c.status
            } for c in all_controls])
            st.dataframe(controls_df)
        else:
            st.info("No controls to export.")

        # Export Compliance Items
        if all_compliance_items:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("Compliance Items Data Preview")
            with col2:
                st.download_button(
                    label="Download Compliance Items as CSV",
                    data=pd.DataFrame([{
                        "ID": ci.id,
                        "Project ID": ci.project_id,
                        "Project Name": get_project_name(ci.project_id),
                        "Name": ci.name,
                        "Description": ci.description,
                        "Standard": ci.standard,
                        "Status": ci.status
                    } for ci in all_compliance_items]).to_csv(index=False).encode('utf-8'),
                    file_name="compliance_items.csv",
                    mime="text/csv",
                )
            compliance_df = pd.DataFrame([{
                "ID": ci.id,
                "Project ID": ci.project_id,
                "Project Name": get_project_name(ci.project_id),
                "Name": ci.name,
                "Description": ci.description,
                "Standard": ci.standard,
                "Status": ci.status
            } for ci in all_compliance_items])
            st.dataframe(compliance_df)
        else:
            st.info("No compliance items to export.")

        # Export Audit Logs
        if all_audit_logs:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("Audit Logs Data Preview")
            with col2:
                st.download_button(
                    label="Download Audit Logs as CSV",
                    data=pd.DataFrame([{
                        "ID": al.id,
                        "Timestamp": al.timestamp,
                        "Project ID": al.project_id,
                        "Project Name": get_project_name(al.project_id),
                        "Action": al.action,
                        "Details": al.details
                    } for al in all_audit_logs]).to_csv(index=False).encode('utf-8'),
                    file_name="audit_logs.csv",
                    mime="text/csv",
                )
            audit_logs_df = pd.DataFrame([{
                "ID": al.id,
                "Timestamp": al.timestamp,
                "Project ID": al.project_id,
                "Project Name": get_project_name(al.project_id),
                "Action": al.action,
                "Details": al.details
            } for al in all_audit_logs])
            st.dataframe(audit_logs_df)
        else:
            st.info("No audit logs to export.")

    # --- User Management Tab (Admin Only) ---
    with tab_users:
        st.header("User Management")
        if st.session_state.user_id == 1: # Only the first user (super admin) can create new users
            st.subheader("Create New User")
            with st.form("new_user_form"):
                new_username = st.text_input("Username")
                new_password = st.text_input("Password", type="password")
                submitted_user = st.form_submit_button("Create User")
                if submitted_user:
                    if new_username and new_password:
                        try:
                            create_user(new_username, new_password)
                            st.success(f"User '{new_username}' created successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error creating user: {e}")
                    else:
                        st.error("Please provide a username and password.")

            st.subheader("Existing Users")
            if all_users:
                user_data = []
                for user in all_users:
                    user_data.append({"ID": user.id, "Username": user.username})
                st.dataframe(pd.DataFrame(user_data))
            else:
                st.info("No users found.")
        else:
            st.warning("You do not have permission to access this page.")


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    main_app()
else:
    login_page()