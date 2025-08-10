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
from services.rag_service import RAGService
from services.user_management import authenticate_user, create_user, get_all_users # Import user management functions
from database import init_db # Import init_db
from dotenv import load_dotenv
import datetime
import io
import sys

# Load environment variables from .env file at the very beginning
load_dotenv()

# Initialize the database when the app starts
init_db()

st.set_page_config(layout="wide")
st.title("Project Audit Tool")

# --- Authentication Logic ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None

def login():
    st.sidebar.subheader("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        user = authenticate_user(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.username = user.username
            st.session_state.role = user.role
            st.sidebar.success(f"Logged in as {user.username} ({user.role})")
            st.rerun()
        else:
            st.sidebar.error("Invalid username or password")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.rerun()

if not st.session_state.logged_in:
    login()
else:
    st.sidebar.write(f"Logged in as: **{st.session_state.username}** ({st.session_state.role})")
    st.sidebar.button("Logout", on_click=logout)

    # --- Data Fetching (once at the top for all sections) ---
    all_projects = get_projects()
    all_risks = get_risks()
    all_controls = get_controls()
    all_compliance_items = get_compliance_items()
    all_audit_logs = get_audit_logs()

    # Helper function to get project name by ID
    def get_project_name(project_id):
        return next((p.name for p in all_projects if p.id == project_id), "Unknown Project")

    # Helper function to get risk name by ID
    def get_risk_name(risk_id):
        return next((r.name for r in all_risks if r.id == risk_id), "Unknown Risk")

    # --- Dashboard Tab ---
    def render_dashboard_tab():
        st.header("Overall Dashboards")

        st.subheader("Overall Metrics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Total Projects", value=len(all_projects))
        with col2:
            st.metric(label="Total Risks", value=len(all_risks))
        with col3:
            st.metric(label="Total Compliance Items", value=len(all_compliance_items))

        st.subheader("Project Overview")
        if all_projects:
            project_data = []
            for p in all_projects:
                project_data.append({"Project": p.name, "Work Packages": len(get_work_packages(p.id))})
            project_overview_df = pd.DataFrame(project_data).set_index("Project")
            st.bar_chart(project_overview_df)
            st.markdown("**Project Overview Data:**")
            st.dataframe(project_overview_df)
        else:
            st.info("No projects to display in dashboard.")

        st.subheader("Risk Overview")
        if all_risks:
            risk_severity_counts = pd.Series([r.severity for r in all_risks]).value_counts()
            st.bar_chart(risk_severity_counts)
            st.markdown("**Risk Severity Data:**")
            st.dataframe(risk_severity_counts)

            risk_status_counts = pd.Series([r.status for r in all_risks]).value_counts()
            st.bar_chart(risk_status_counts)
            st.markdown("**Risk Status Data:**")
            st.dataframe(risk_status_counts)
        else:
            st.info("No risks to display in dashboard.")

        st.subheader("Compliance Overview")
        if all_compliance_items:
            compliance_status_counts = pd.Series([c.status for c in all_compliance_items]).value_counts()
            st.bar_chart(compliance_status_counts)
            st.markdown("**Compliance Status Data:**")
            st.dataframe(compliance_status_counts)

            compliance_standard_counts = pd.Series([c.standard for c in all_compliance_items]).value_counts()
            st.bar_chart(compliance_standard_counts)
            st.markdown("**Compliance Standard Data:**")
            st.dataframe(compliance_standard_counts)
        else:
            st.info("No compliance items to display in dashboard.")

        st.subheader("Audit Log Overview")
        st.write(f"Total Audit Log Entries: {len(all_audit_logs)}")

    # --- Project Management Tab ---
    def render_project_management_tab():
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
                            create_project(
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
                    st.markdown(f"### {project.name} (ID: {project.id})")
                    st.write(f"Description: {project.description}")
                    
                    st.markdown("**PIN Details:**")
                    st.write(f"PIN ID: {project.pin_id if project.pin_id else 'N/A'}")
                    st.write(f"Scope: {project.scope if project.scope else 'N/A'}")
                    st.write(f"Milestones: {project.milestones if project.milestones else 'N/A'}")
                    st.write(f"Start Date: {project.start_date if project.start_date else 'N/A'}")
                    st.write(f"End Date: {project.end_date if project.end_date else 'N/A'}")
                    st.write(f"Effort Estimation: {project.effort_estimation if project.effort_estimation else 'N/A'}")
                    st.write(f"Deliverables: {project.deliverables if project.deliverables else 'N/A'}")
                    st.write(f"Team Members: {project.team_members if project.team_members else 'N/A'}")
                    st.write(f"Team Size: {project.team_size if project.team_size else 'N/A'}")
                    st.write(f"Roles & Responsibilities: {project.roles_responsibilities if project.roles_responsibilities else 'N/A'}")
                    st.write(f"SDLC Model: {project.sdlc_model if project.sdlc_model else 'N/A'}")
                    st.write(f"CISO Approved: {project.ciso_approved}")
                    st.write(f"CISO Approval Date: {project.ciso_approval_date if project.ciso_approval_date else 'N/A'}")

                    col_wp, col_comp, col_docs = st.columns(3)

                    with col_wp:
                        st.markdown("**Work Packages**")
                        work_packages = get_work_packages(project.id)
                        if work_packages:
                            wp_data = []
                            for wp in work_packages:
                                wp_data.append({"ID": wp.id, "Subject": wp.subject, "Description": wp.description})
                            st.dataframe(pd.DataFrame(wp_data))
                        else:
                            st.info("No work packages for this project.")

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
                        st.markdown("**Compliance Items**")
                        compliance_items = get_compliance_items(project.id)
                        if compliance_items:
                            comp_data = []
                            for item in compliance_items:
                                comp_data.append({"ID": item.id, "Name": item.name, "Standard": item.standard, "Status": item.status})
                            st.dataframe(pd.DataFrame(comp_data))
                        else:
                            st.info("No compliance items for this project.")

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
                        st.markdown("**Documents**")
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
                            st.dataframe(docs_df.drop(columns=["Link"])) # Display all columns except the internal link

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
    def render_risk_control_tab():
        st.header("Risk & Control Management")

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
            st.dataframe(pd.DataFrame(risk_display_data))

            st.markdown("### Detailed Risk View")
            risk_selection_options = {r.id: r.name for r in all_risks}
            selected_risk_id_detail = st.selectbox("Select a Risk for Detailed View and Management", options=list(risk_selection_options.keys()), format_func=lambda x: risk_selection_options[x], key="detailed_risk_select")

            if selected_risk_id_detail:
                risk = next((r for r in all_risks if r.id == selected_risk_id_detail), None)
                if risk:
                    st.markdown(f"### {risk.name} (ID: {risk.id}) - Project: {get_project_name(risk.project_id)}")
                    st.write(f"Description: {risk.description}")
                    st.write(f"Severity: {risk.severity}, Likelihood: {risk.likelihood}, Status: {risk.status}")

                    st.markdown("**Controls**")
                    controls = get_controls(risk.id)
                    if controls:
                        control_data = []
                        for control in controls:
                            control_data.append({"ID": control.id, "Name": control.name, "Description": control.description, "Type": control.type, "Status": control.status})
                        st.dataframe(pd.DataFrame(control_data))
                    else:
                        st.info("No controls for this risk.")

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
                    st.markdown("---")
        else:
            st.info("No risks found. Create one above!")

    # --- Audit Logs Tab ---
    def render_audit_logs_tab():
        st.header("Audit Logs")
        if all_audit_logs:
            # Convert audit logs to a DataFrame for better display
            log_data = []
            for log in all_audit_logs:
                log_data.append({
                    "Timestamp": log.timestamp,
                    "Project": get_project_name(log.project_id),
                    "Action": log.action,
                    "Details": log.details
                })
            st.dataframe(pd.DataFrame(log_data))
        else:
            st.info("No audit logs found.")

    # --- LLM Integration Tab ---
    def render_llm_integration_tab():
        st.header("LLM Integration with LangChain")

        # Initialize services at the start of the render function
        llm_service = LLMService()
        
        # Use a try-except block for robustness, in case of connection errors etc.
        try:
            if 'rag_service' not in st.session_state:
                st.session_state.rag_service = RAGService()
            rag_service = st.session_state.rag_service
        except Exception as e:
            st.error(f"Failed to initialize RAG Service. Please ensure backend services (Milvus, etc.) are running. Error: {e}")
            return # Stop rendering this tab if RAG service fails

        st.markdown("### Ask Questions About Your Projects (RAG)")
        st.info("This feature uses a LangChain-powered RAG pipeline to answer questions about your projects. It connects to external services for embeddings (Sentence Transformers) and vector storage (Milvus).")

        # RAG System Management
        with st.expander("RAG System Management"):
            st.write("Synchronize the application's database with the Milvus vector store.")
            if st.button("Sync & Index Data"):
                with st.spinner("Orchestrating data synchronization via LangChain..."):
                    try:
                        rag_service.sync_and_index_data()
                        summary = rag_service.get_vector_store_summary()
                        st.success("Data synchronization with LangChain and Milvus complete!")
                        st.info(summary)
                    except Exception as e:
                        st.error
        #RAG System Management
        with st.expander("RAG System Management"):
            st.write("Synchronize the application's database with the Milvus vector store.")
            if st.button("Sync & Index Data"):
                with st.spinner("Orchestrating data synchronization via LangChain..."):
                    try:
                        rag_service.sync_and_index_data()
                        summary = rag_service.get_vector_store_summary()
                        st.success("Data synchronization with LangChain and Milvus complete!")
                        st.info(summary)
                    except Exception as e:
                        st.error(f"An error occurred during data synchronization: {e}")
        
        # Chat UI for RAG
        with st.form("rag_query_form"):
            rag_question = st.text_area("Your Question:")
            submitted_rag_question = st.form_submit_button("Get Answer")

            if submitted_rag_question and rag_question:
                with st.spinner("Searching for answers with LangChain..."):
                    try:
                        # Query the RAG system to get the answer and context
                        response = rag_service.query_rag_system(rag_question)
                        
                        if not response or not response.get("answer"):
                            st.warning("Could not find relevant information to answer the question.")
                        else:
                            st.markdown("### Answer")
                            st.markdown(response["answer"])
                            with st.expander("Show Retrieved Context"):
                                st.json(response["context"])

                    except Exception as e:
                        st.error(f"An error occurred while getting the answer: {e}")
            elif submitted_rag_question:
                st.error("Please enter a question.")

        with st.expander("Legacy: Generate Document"):
            with st.form("generate_document_form"):
                doc_prompt = st.text_area("Prompt for Document Generation")
                submitted_doc_prompt = st.form_submit_button("Generate Document")
                if submitted_doc_prompt and doc_prompt:
                    with st.spinner("Generating document..."):
                        try:
                            generated_doc = llm_service.generate_document(doc_prompt)
                            st.write(generated_doc)
                        except Exception as e:
                            st.error(f"Error generating document: {e}")

        with st.expander("Legacy: Assess Risk with LLM"):
            with st.form("assess_risk_form"):
                risk_desc_llm = st.text_area("Risk Description for LLM Assessment")
                submitted_risk_desc = st.form_submit_button("Assess Risk")
                if submitted_risk_desc and risk_desc_llm:
                    with st.spinner("Assessing risk..."):
                        try:
                            risk_assessment = llm_service.assess_risk(risk_desc_llm)
                            st.write(risk_assessment)
                        except Exception as e:
                            st.error(f"Error assessing risk: {e}")

    # --- Reports & Export Tab ---
    def render_reports_export_tab():
        st.header("Reports & Export")

        st.subheader("Export Data to CSV")

        # Export Projects
        if all_projects:
            projects_df = pd.DataFrame([{"ID": p.id, "Name": p.name, "Description": p.description} for p in all_projects])
            st.subheader("Projects Data Preview")
            st.dataframe(projects_df)
            st.download_button(
                label="Download Projects as CSV",
                data=projects_df.to_csv(index=False).encode('utf-8'),
                file_name="projects.csv",
                mime="text/csv",
            )
        else:
            st.info("No projects to export.")

        # Export Risks
        if all_risks:
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
            st.subheader("Risks Data Preview")
            st.dataframe(risks_df)
            st.download_button(
                label="Download Risks as CSV",
                data=risks_df.to_csv(index=False).encode('utf-8'),
                file_name="risks.csv",
                mime="text/csv",
            )
        else:
            st.info("No risks to export.")

        # Export Controls
        if all_controls:
            controls_df = pd.DataFrame([{
                "ID": c.id,
                "Risk ID": c.risk_id,
                "Risk Name": get_risk_name(c.risk_id),
                "Name": c.name,
                "Description": c.description,
                "Type": c.type,
                "Status": c.status
            } for c in all_controls])
            st.subheader("Controls Data Preview")
            st.dataframe(controls_df)
            st.download_button(
                label="Download Controls as CSV",
                data=controls_df.to_csv(index=False).encode('utf-8'),
                file_name="controls.csv",
                mime="text/csv",
            )
        else:
            st.info("No controls to export.")

        # Export Compliance Items
        if all_compliance_items:
            compliance_df = pd.DataFrame([{
                "ID": ci.id,
                "Project ID": ci.project_id,
                "Project Name": get_project_name(ci.project_id),
                "Name": ci.name,
                "Description": ci.description,
                "Standard": ci.standard,
                "Status": ci.status
            } for ci in all_compliance_items])
            st.subheader("Compliance Items Data Preview")
            st.dataframe(compliance_df)
            st.download_button(
                label="Download Compliance Items as CSV",
                data=compliance_df.to_csv(index=False).encode('utf-8'),
                file_name="compliance_items.csv",
                mime="text/csv",
            )
        else:
            st.info("No compliance items to export.")

        # Export Audit Logs
        if all_audit_logs:
            audit_logs_df = pd.DataFrame([{
                "ID": al.id,
                "Timestamp": al.timestamp,
                "Project ID": al.project_id,
                "Project Name": get_project_name(al.project_id),
                "Action": al.action,
                "Details": al.details
            } for al in all_audit_logs])
            st.subheader("Audit Logs Data Preview")
            st.dataframe(audit_logs_df)
            st.download_button(
                label="Download Audit Logs as CSV",
                data=audit_logs_df.to_csv(index=False).encode('utf-8'),
                file_name="audit_logs.csv",
                mime="text/csv",
            )
        else:
            st.info("No audit logs to export.")

    # --- User Management Tab (Admin Only) ---
    def render_user_management_tab():
        st.header("User Management")
        if st.session_state.role == "admin":
            st.subheader("Create New User")
            with st.form("new_user_form"):
                new_username = st.text_input("Username")
                new_password = st.text_input("Password", type="password")
                new_role = st.selectbox("Role", ["user", "admin"])
                submitted_user = st.form_submit_button("Create User")
                if submitted_user:
                    if new_username and new_password:
                        try:
                            create_user(new_username, new_password, new_role)
                            st.success(f"User '{new_username}' ({new_role}) created successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error creating user: {e}")
                    else:
                        st.error("Please provide a username and password.")

            st.subheader("Existing Users")
            users = get_all_users()
            if users:
                user_data = []
                for user in users:
                    user_data.append({"ID": user.id, "Username": user.username, "Role": user.role})
                st.dataframe(pd.DataFrame(user_data))
            else:
                st.info("No users found.")
        else:
            st.warning("You do not have permission to access User Management.")

    # --- Main App Layout with Tabs (only if logged in) ---
    if st.session_state.logged_in:
        tab_dashboard, tab_projects, tab_risks, tab_audit, tab_llm, tab_reports, tab_users = st.tabs([
            "Dashboards", 
            "Project Management", 
            "Risk & Control Management", 
            "Audit Logs", 
            "LLM Integration",
            "Reports & Export",
            "User Management"
        ])

        with tab_dashboard:
            render_dashboard_tab()

        with tab_projects:
            render_project_management_tab()

        with tab_risks:
            render_risk_control_tab()

        with tab_audit:
            render_audit_logs_tab()

        with tab_llm:
            render_llm_integration_tab()

        with tab_reports:
            render_reports_export_tab()

        with tab_users:
            render_user_management_tab()