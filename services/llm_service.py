# llm_service.py

import google.generativeai as genai
import os
from dotenv import load_dotenv

class LLMService:
    def __init__(self):
        load_dotenv() # Load environment variables from .env file
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('models/gemini-2.5-pro') # Using the specified model

    def generate_document(self, prompt):
        """Generates a document based on the given prompt."""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating document: {e}"

    def assess_risk(self, risk_description):
        """Assesses a risk based on its description."""
        prompt = f"""Assess the following risk and provide a severity and likelihood rating (e.g., Severity: High, Likelihood: Medium). Also, provide a brief justification.

Risk: {risk_description}"""
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