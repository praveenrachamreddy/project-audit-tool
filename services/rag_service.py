# services/rag_service.py

import os
from database import SessionLocal, Project, Document, Risk, Control, Compliance
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_milvus.vectorstores import Milvus
from langchain_core.documents import Document as LangchainDocument
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# --- Placeholder for Docling Client ---
# In a real scenario, this would be a proper client making HTTP requests.
def docling_client_placeholder(document_url: str) -> str:
    """Simulates calling a document extraction API."""
    print(f"--- [DoclingClient] -> Simulating extraction for URL: {document_url}")
    return f"This is the dummy extracted text from the document at {document_url}."
# -----------------------------------------

class RAGService:
    def __init__(self):
        """
        This service orchestrates the RAG pipeline using LangChain.
        """
        print("Initializing RAGService with LangChain components...")
        
        # --- Core Components ---
        # 1. Embedding Model (using a local Sentence Transformer via LangChain)
        self.embedding_model = SentenceTransformerEmbeddings(
            model_name=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        )
        
        # 2. Vector Store (connecting to Milvus via LangChain)
        milvus_host = os.getenv("MILVUS_HOST", "milvus-service.praveen.svc.cluster.local")
        milvus_port = os.getenv("MILVUS_PORT", "19530")

        self.vector_store = Milvus(
            embedding_function=self.embedding_model,
            connection_args={
                "host": milvus_host,
                "port": milvus_port
            },
            collection_name="project_audit_rag_lc"
        )

        # 3. LLM (using Gemini via LangChain)
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", convert_system_message_to_human=True)
        
        # 4. Retriever (for fetching relevant documents from Milvus)
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})

        # 5. Prompt Template
        template = """
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
        self.prompt = ChatPromptTemplate.from_template(template)

        # 6. The RAG Chain
        # This defines the entire query process:
        # - The user's question is passed through.
        # - The retriever fetches context based on the question.
        # - The question and context are formatted by the prompt.
        # - The prompt is sent to the LLM.
        # - The LLM's response is parsed as a string.
        self.rag_chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        
        print("RAGService initialized successfully.")

    def sync_and_index_data(self):
        """
        Fetches data from the application's database, converts it to LangChain
        Documents, and indexes it in the Milvus vector store.
        """
        print("\n[RAGService] Starting data synchronization and indexing with LangChain...")
        db = SessionLocal()
        
        try:
            # 1. Clear existing data
            self.clear_vector_store()

            # 2. Fetch and prepare data
            print("[RAGService] Fetching and preparing data from local database...")
            langchain_docs = []
            
            # Projects
            for project in db.query(Project).all():
                doc = LangchainDocument(
                    page_content=f"Project Name: {project.name}. Description: {project.description}. Scope: {project.scope}.",
                    metadata={"source": "project", "id": project.id}
                )
                langchain_docs.append(doc)

            # Risks
            for risk in db.query(Risk).all():
                doc = LangchainDocument(
                    page_content=f"Risk: {risk.name}. Description: {risk.description}. Severity: {risk.severity}. Project: {risk.project.name}.",
                    metadata={"source": "risk", "id": risk.id, "project_id": risk.project_id}
                )
                langchain_docs.append(doc)

            # Documents (with placeholder extraction)
            for doc_record in db.query(Document).all():
                extracted_text = docling_client_placeholder(doc_record.link)
                doc = LangchainDocument(
                    page_content=f"Document Name: {doc_record.name}. Type: {doc_record.type}. Content: {extracted_text}",
                    metadata={"source": "document", "id": doc_record.id, "project_id": doc_record.project_id}
                )
                langchain_docs.append(doc)
            
            print(f"[RAGService] Prepared {len(langchain_docs)} documents for indexing.")

            # 3. Index the documents in Milvus
            if langchain_docs:
                print("[RAGService] Indexing documents in Milvus... This may take a moment.")
                self.vector_store.add_documents(langchain_docs)
                print("[RAGService] Indexing complete.")
            else:
                print("[RAGService] No documents to index.")

        finally:
            db.close()

    def query_rag_system(self, query_text: str) -> dict:
        """
        Queries the RAG system using the pre-built LangChain chain.
        Returns the answer and the retrieved context.
        """
        print(f"\n[RAGService] Querying LangChain RAG system for: '{query_text}'")
        
        # We need to get the context separately to return it for display
        retrieved_docs = self.retriever.invoke(query_text)
        
        if not retrieved_docs:
            return {
                "answer": "Could not find relevant information to answer the question.",
                "context": []
            }
            
        # Now invoke the full chain to get the final answer
        answer = self.rag_chain.invoke(query_text)
        
        return {
            "answer": answer,
            "context": [doc.to_json() for doc in retrieved_docs] # Return context for inspection
        }

    def clear_vector_store(self):
        """Clears the entire Milvus collection."""
        print("\n[RAGService] Clearing vector store collection...")
        try:
            # This is a simplified way; a more robust way might use the Milvus SDK (pymilvus)
            # to drop the collection if the LangChain wrapper doesn't expose a clear method.
            # For now, we assume we can get a client and clear it.
            collection_name = self.vector_store.collection_name
            if self.vector_store.col:
                 self.vector_store.col.drop() 
                 print(f"Dropped Milvus collection: {collection_name}")
            else:
                 print("No active collection to drop.")
        except Exception as e:
            print(f"Could not clear collection (it may not exist yet): {e}")

    def get_vector_store_summary(self) -> str:
        """Gets a summary of the vector store's state."""
        try:
            count = self.vector_store.col.num_entities if self.vector_store.col else 0
            summary = f"Milvus collection '{self.vector_store.collection_name}' currently has {count} items."
            return summary
        except Exception as e:
            return f"Could not retrieve summary from Milvus: {e}"