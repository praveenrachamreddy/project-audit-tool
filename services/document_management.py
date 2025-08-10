# document_management.py

import os
import uuid
from database import SessionLocal, Document
from services.audit_logging import create_audit_log
import datetime

# Define the directory for storing uploaded documents
DOCUMENT_STORAGE_DIR = "./documents_storage"

def _save_file_to_storage(file_content: bytes, original_filename: str) -> str:
    """Saves the file content to local storage and returns the full path."""
    os.makedirs(DOCUMENT_STORAGE_DIR, exist_ok=True)
    unique_filename = f"{uuid.uuid4()}_{original_filename}"
    file_path = os.path.join(DOCUMENT_STORAGE_DIR, unique_filename)
    with open(file_path, "wb") as f:
        f.write(file_content)
    return file_path

def _delete_file_from_storage(file_path: str):
    """Deletes a file from local storage if it exists."""
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"DEBUG: Deleted file: {file_path}")
        except Exception as e:
            print(f"ERROR: Could not delete file {file_path}: {e}")

def create_document(project_id, name, type, version, file_content=None, original_filename=None, approval_status="Pending", approved_by=None, approval_date=None):
    """Creates a new document record and saves the file content to storage.
    If file_content is provided, link will be the path to the stored file.
    Otherwise, link will be None or an empty string.
    """
    db = SessionLocal()
    file_path = None
    if file_content and original_filename:
        try:
            file_path = _save_file_to_storage(file_content, original_filename)
        except Exception as e:
            db.close()
            create_audit_log(project_id, "Document Creation Failed", f"Failed to save document file for '{name}': {e}")
            raise RuntimeError(f"Failed to save document file: {e}")

    doc = Document(
        project_id=project_id,
        name=name,
        type=type,
        version=version,
        link=file_path, # Store the path to the saved file
        approval_status=approval_status,
        approved_by=approved_by,
        approval_date=approval_date
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    db.close()
    create_audit_log(project_id, "Document Created", f"Document '{name}' (Type: {type}, Version: {version}) created for project ID {project_id}. File saved at {file_path or 'N/A'}.")
    return doc

def get_documents(project_id=None):
    """Gets all document records, optionally filtered by project."""
    db = SessionLocal()
    if project_id:
        docs = db.query(Document).filter(Document.project_id == project_id).all()
    else:
        docs = db.query(Document).all()
    db.close()
    return docs

def update_document(doc_id, name=None, type=None, version=None, file_content=None, original_filename=None, approval_status=None, approved_by=None, approval_date=None):
    """Updates an existing document record and its associated file content.
    If new file_content is provided, the old file will be deleted and a new one saved.
    """
    db = SessionLocal()
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if doc:
        original_file_path = doc.link # Store old path for deletion

        if name: doc.name = name
        if type: doc.type = type
        if version: doc.version = version
        
        # Handle file content update
        if file_content and original_filename:
            try:
                new_file_path = _save_file_to_storage(file_content, original_filename)
                doc.link = new_file_path # Update link to new file
                _delete_file_from_storage(original_file_path) # Delete old file
            except Exception as e:
                db.close()
                create_audit_log(doc.project_id, "Document Update Failed", f"Failed to update document file for '{doc.name}' (ID: {doc.id}): {e}")
                raise RuntimeError(f"Failed to update document file: {e}")
        # If link is explicitly set to None/empty string, and no new file, delete old file
        elif link == "" and original_file_path:
            _delete_file_from_storage(original_file_path)
            doc.link = ""

        if approval_status: doc.approval_status = approval_status
        if approved_by: doc.approved_by = approved_by
        if approval_date: doc.approval_date = approval_date
        
        db.commit()
        db.refresh(doc)
        db.close()
        create_audit_log(doc.project_id, "Document Updated", f"Document '{doc.name}' (ID: {doc.id}) updated. File path: {doc.link or 'N/A'}.")
        return doc
    db.close()
    return None

def delete_document(doc_id):
    """Deletes a document record and its associated file from storage."""
    db = SessionLocal()
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if doc:
        project_id = doc.project_id
        doc_name = doc.name
        file_path_to_delete = doc.link # Get file path before deleting record

        db.delete(doc)
        db.commit()
        db.close()
        
        _delete_file_from_storage(file_path_to_delete) # Delete the actual file

        create_audit_log(project_id, "Document Deleted", f"Document '{doc_name}' (ID: {doc_id}) deleted. File {file_path_to_delete or 'N/A'} removed.")
        return True
    db.close()
    return False
