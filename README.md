# Project Audit Tool

## Project Vision

The **Project Audit Tool** is an ambitious, integrated application designed to unify the core functionalities typically found in separate project management (like OpenProject), audit and compliance (like Eramba), and audit logging (like Auditum) platforms. Our goal is to create a single, seamless Python-based system that combines project tracking, audit workflows, compliance management, and comprehensive audit logging for internal use.

A key differentiator of this application is its deep integration with Large Language Models (LLMs) via the Gemini API. These LLMs are leveraged to intelligently process data, enabling features like automated document generation and intelligent risk assessment, providing enhanced insights and automation across the platform.

This project aims to provide a self-contained solution, meaning all functionalities are built directly into this application, eliminating the need to run or integrate with external instances of OpenProject, Eramba, or Auditum.

## Setup and Installation

To get the Project Audit Tool up and running, follow these steps:

1.  **Navigate to the Project Directory:**
    Open your terminal or command prompt and change to the `project_audit_tool` directory:
    ```bash
    cd project_audit_tool
    ```

2.  **Create a Python Virtual Environment:**
    It's highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    python -m venv venv
    ```

3.  **Activate the Virtual Environment:**
    *   **Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

4.  **Install Dependencies:**
    Install all required Python packages using `pip`:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Set up Gemini API Key:**
    The application uses the Gemini API for LLM functionalities. You need to set your API key as an environment variable. Create a file named `.env` in the `project_audit_tool` directory (the same directory as `app.py` and `frontend.py`) with the following content:
    ```
    GEMINI_API_KEY=YOUR_ACTUAL_GEMINI_API_KEY
    ```
    Replace `YOUR_ACTUAL_GEMINI_API_KEY` with your real Gemini API key.

6.  **Initialize the Database:**
    The application uses an SQLite database (`project_audit_tool.db`). The database and its tables will be automatically created when you run the `frontend.py` for the first time. A default `admin` user with password `admin` will also be created if no users exist.

## Features Implemented

The Project Audit Tool currently includes the following core modules:

### 1. Project Management

This module allows you to manage projects and their associated work packages (tasks, issues, etc.), similar to OpenProject. It includes detailed project initiation and document tracking.

*   **Projects:**
    *   Create new projects with a name, description, and detailed Project Initiation Note (PIN) fields (PIN ID, scope, milestones, dates, effort, deliverables, team, roles, SDLC model, CISO approval).
    *   List all existing projects with their detailed information.
*   **Work Packages:**
    *   Create work packages linked to a specific project, with a subject and description.
    *   List all work packages for a given project.
*   **Documents:**
    *   Track various project-related documents (PIN, SRS, HLD, QAP, etc.) with name, type, version, link, and approval status.
    *   Associate documents with specific projects.

### 2. Audit Logging

Every significant action performed within the application (e.g., creating a project, adding a risk, updating a control) is automatically logged. This provides a comprehensive audit trail.

*   **Automatic Logging:** Actions are logged with a timestamp, the action performed, and relevant details.
*   **View Audit Logs:** List all audit log entries, with an option to filter by project.

### 3. Risk Management

Inspired by Eramba's capabilities, this module allows you to identify, assess, and track risks associated with your projects.

*   **Risks:**
    *   Create new risks linked to a project, including name, description, severity, likelihood, and status.
    *   List all risks, with an option to filter by project.
    *   Update existing risk details.
    *   Delete risks.
*   **LLM-Powered Risk Assessment:** Utilize the integrated LLM to get an automated assessment of a risk's severity and likelihood based on its description.

### 4. Control Management

This module enables you to define and manage controls designed to mitigate identified risks.

*   **Controls:**
    *   Create new controls linked to a specific risk, including name, description, type (e.g., Preventive, Detective), and status.
    *   List all controls, with an option to filter by the risk they mitigate.
    *   Update existing control details.
    *   Delete controls.

### 5. Compliance Management

This module helps track compliance requirements and their status within your projects.

*   **Compliance Items:**
    *   Create new compliance items linked to a project, including name, description, the standard it relates to (e.g., GDPR, ISO 27001), and its status.
    *   List all compliance items, with an option to filter by project.
    *   Update existing compliance item details.
    *   Delete compliance items.

### 6. LLM Integration (Gemini API)

The application integrates with the Gemini API to provide intelligent automation.

*   **Automated Document Generation:** Provide a prompt to the LLM to generate various types of documents or text.
*   **Intelligent Risk Assessment:** Leverage the LLM to analyze risk descriptions and provide automated severity/likelihood ratings and justifications.

### 7. User Management & Authentication

This module provides basic user authentication and authorization, securing access to the application.

*   **Login/Logout:** Users must log in to access the application's features.
*   **Role-Based Access:** Supports different user roles (e.g., `admin`, `user`).
*   **User Creation (Admin Only):** Administrators can create new user accounts and assign roles.
*   **Default Admin:** A default `admin` user is created upon first database initialization (username: `admin`, password: `admin`).

### 8. Dashboards & Reporting

Provides a high-level overview of project, risk, and compliance data through interactive dashboards and allows data export.

*   **Overall Metrics:** Displays total counts for projects, risks, and compliance items.
*   **Visualizations:** Bar charts for project work packages, risk severity/status, and compliance status/standards.
*   **Data Export:** Allows downloading all data (Projects, Risks, Controls, Compliance Items, Audit Logs) as CSV files.

## How to Use

The Project Audit Tool can be interacted with via both a Command-Line Interface (CLI) and a Web Frontend.

### Command-Line Interface (CLI)

All core functionalities can be accessed via `app.py`.

**General Usage:**

```bash
python app.py [command] [arguments]
```

**Examples:**

*   **Add a new project:**
    ```bash
    python app.py add-project "Website Redesign" "Redesign of the company's main website." --pin-id "PIN-WR-001" --sdlc-model "Agile"
    ```
*   **List all projects:**
    ```bash
    python app.py list-projects
    ```
*   **Add a work package to Project ID 1:**
    ```bash
    python app.py add-work-package 1 "Design Mockups" "Create initial design mockups for the new website."
    ```
*   **Add a risk to Project ID 1:**
    ```bash
    python app.py add-risk 1 "Data Breach" "Sensitive customer data could be exposed." "High" "Medium" "Open"
    ```
*   **List audit logs for Project ID 1:**
    ```bash
    python app.py list-audit-logs --project-id 1
    ```
*   **Add a control to Risk ID 1:**
    ```bash
    python app.py add-control 1 "Access Control" "Implement strong access controls." "Preventive" "Implemented"
    ```
*   **Add a compliance item to Project ID 1:**
    ```bash
    python app.py add-compliance-item 1 "GDPR Data Processing" "Ensure all data processing complies with GDPR." "GDPR" "Compliant"
    ```
*   **Add a document to Project ID 1:**
    ```bash
    python app.py add-document 1 "Website Redesign SRS" "SRS" "1.0" "https://example.com/srs-v1.0.pdf" --approval-status "Approved" --approved-by "John Doe" --approval-date "2023-01-15"
    ```
*   **Generate a document using LLM:**
    ```bash
    python app.py generate-document "Write a project summary for the 'Website Redesign' project, highlighting key milestones and risks."
    ```
*   **Assess a risk using LLM:**
    ```bash
    python app.py assess-risk "Our server infrastructure is outdated and prone to failures."
    ```

For a full list of commands and their arguments, run:
```bash
python app.py --help
```
And for specific command help:
```bash
python app.py [command] --help
```

### Web Frontend

A simple web interface built with Streamlit provides a more visual way to interact with the tool.

**To run the frontend:**

1.  Ensure your virtual environment is activated.
2.  Run the Streamlit command from the `project_audit_tool` directory:
    ```bash
    streamlit run frontend.py
    ```
    This will open the application in your default web browser.

**Login:**
Upon launching the frontend, you will be presented with a login screen. Use the default `admin` credentials:
*   **Username:** `admin`
*   **Password:** `admin`

Once logged in, the frontend allows you to:
*   Create and view Projects, Work Packages, Risks, Controls, and Compliance Items through interactive forms and displays.
*   View all Audit Logs.
*   Utilize the LLM for document generation and risk assessment via dedicated input fields.
*   **User Management (Admin Only):** If logged in as an `admin`, you can access the "User Management" tab to create new users and view existing ones.
*   **Dashboards & Reports:** Access the "Dashboards" tab for an overview and the "Reports & Export" tab to download data.

## Future Enhancements

This project is designed to be modular and extensible. Potential future enhancements include:

*   **Advanced RAG System:** Re-implementing a robust RAG system with Milvus, advanced embedding models, and document parsing (e.g., Docling) for intelligent querying over all project data.
*   **Notifications:** Real-time alerts for critical events (e.g., high-risk changes, compliance breaches).
*   **Integration with External Systems:** While currently self-contained, future versions could offer optional integrations with external tools for data import/export.
*   **Enhanced LLM Features:** More complex LLM interactions, such as automated compliance validation, intelligent query answering over project data, or generating mitigation strategies.
*   **Testing Framework:** Adding unit and integration tests to ensure robustness.
*   **Improved UI/UX:** Further refining the Streamlit frontend for better usability and aesthetics.
*   **Data Export/Import:** Functionality to export data (e.g., to CSV, JSON) and import existing data.
