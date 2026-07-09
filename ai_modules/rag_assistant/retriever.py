from ai_modules.rag_assistant.vector_store import get_vector_store

def retrieve_context(query: str, k: int = 3) -> str:
    """
    Searches the vector store for document chunks matching the user's inquiry
    and joins them together into a unified context block.
    """
    try:
        db = get_vector_store()
        
        # Pull top K matching documentation pieces
        docs = db.similarity_search(query, k=k)
        
        # Flatten documentation arrays into a unified text block
        context_block = "\n---\n".join([doc.page_content for doc in docs])
        return context_block
        
    except Exception as e:
        print(f"[RETRIEVER ERROR] Failed querying Chroma: {str(e)}")
        return ""