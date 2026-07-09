import os
from langchain_community.vectorstores import Chroma
from ai_modules.rag_assistant.embeddings import get_embedding_model

def get_vector_store():
    """
    Loads or references the existing local Chroma vector database instance.
    """
    # 1. Fetch your Gemini embedding model configurations
    embeddings = get_embedding_model()
    
    # 2. Define standard directory path pointing to your persistent store database
    base_dir = os.path.dirname(os.path.abspath(__file__))
    persist_directory = os.path.join(base_dir, "chroma_db")
    
    return Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )