# llm_service.py

import google.generativeai as genai
import os
from dotenv import load_dotenv
from services.project_management import get_project_by_id, get_work_packages
from services.risk_management import get_risks
from services.document_management import get_documents

class LLMService:
    def __init__(self):
        load_dotenv() # Load environment variables from .env file
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('models/gemini-2.5-pro') # Using a standard model

    def _get_project_context(self, project_id):
        """Helper function to gather context for a given project."""
        project = get_project_by_id(project_id)
        if not project:
            return ""

        work_packages = get_work_packages(project_id)
        risks = get_risks(project_id)
        documents = get_documents(project_id)

        context = f"""Project Name: {project.name}
Project Description: {project.description}

Work Packages:
"""
        for wp in work_packages:
            context += f"- {wp.subject}\n"
        
        context += "\nRisks:\n"
        for risk in risks:
            context += f"- {risk.name} (Severity: {risk.severity}, Likelihood: {risk.likelihood}, Status: {risk.status})\n"

        context += "\nDocuments:\n"
        for doc in documents:
            context += f"- {doc.name} (Type: {doc.type}, Status: {doc.approval_status})\n"
        
        return context

    def generate_document(self, prompt, project_id=None):
        """Generates a document based on the given prompt, with optional project context."""
        final_prompt = prompt
        if project_id:
            context = self._get_project_context(project_id)
            final_prompt = f"""You are a project management assistant. Based on the following project context, generate the requested document.

**Project Context:**
---
{context}
---

**User's Request:**
{prompt}

**Generated Document:**
"""
        try:
            response = self.model.generate_content(final_prompt)
            return response.text
        except Exception as e:
            return f"Error generating document: {e}"

    def assess_risk(self, risk_description, project_id=None):
        """Assesses a risk based on its description, with optional project context."""
        context_prompt = ""
        if project_id:
            context = self._get_project_context(project_id)
            context_prompt = f"""
**Project Context:**
---
{context}
---
"""

        prompt = f"""You are a risk assessment expert. Assess the following risk and provide a severity and likelihood rating (e.g., Severity: High, Likelihood: Medium). Also, provide a brief justification.

{context_prompt}

**Risk to Assess:**
{risk_description}

**Assessment:**
"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error assessing risk: {e}"

    def answer_project_question(self, question, context):
        """Answers a question based on the provided context using RAG."""
        prompt = f"""
        You are an expert assistant for the Project Audit Tool. Your task is to answer the user's question based *only* on the context provided below.
        Do not use any external knowledge or make assumptions. If the context does not contain the answer, state that clearly.

        **Context:**
        ---
        {context}
        ---

        **Question:**
        {question}

        **Answer:**
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error answering question: {e}"

    @staticmethod
    def list_available_models():
        """Lists all available Gemini models and their supported methods."""
        load_dotenv() # Ensure .env is loaded for this static method too
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        genai.configure(api_key=api_key)

        print("\n--- Available Gemini Models ---")
        found_generative_model = False
        for m in genai.list_models():
            print(f"Name: {m.name}")
            print(f"  Display Name: {m.display_name}")
            print(f"  Supported Methods: {m.supported_generation_methods}")
            print(f"  Description: {m.description}")
            print("-------------------------------")
            if 'generateContent' in m.supported_generation_methods:
                found_generative_model = True
        
        if not found_generative_model:
            print("No models found that support 'generateContent'. Please check your API key and region.")
        print("-------------------------------")
