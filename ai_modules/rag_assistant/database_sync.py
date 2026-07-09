import sys
import os
from langchain_core.documents import Document

# Append the project root directory so we can import the app modules smoothly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.database import SessionLocal  # Your session builder
from app.models.product import Product  # Adjust imports based on exact filenames
from app.models.category import Category  #

def sync_database_to_vector_store():
    """
    Queries SQL tables, transforms rows into clear contextual descriptions, 
    and saves them to the Vector Store for semantic lookup.
    """
    db_session = SessionLocal()
    documents_to_index = []
    
    try:
        # 1. Fetch products joined with their parent category
        products = db_session.query(Product).all()
        
        for p in products:
            # Create a rich natural language context sentence for the LLM to understand
            text_context = (
                f"Product: {p.name}. "
                f"Category: {p.category.name if p.category else 'General'}. "
                f"Price: {p.price} EGP. "
                f"Description: {p.description or 'No further description available.'} "
                f"Stock Status: {'In Stock' if p.stock_quantity > 0 else 'Out of Stock'}."
            )
            
            # The metadata dict holds structural data we can map directly to your JS rich components!
            metadata = {
                "kind": "product",
                "id": p.id,
                "name": p.name,
                "price": float(p.price),
                "category": p.category.name if p.category else "General"
            }
            
            doc = Document(page_content=text_context, metadata=metadata)
            documents_to_index.append(doc)
            
        # 2. (Optional) Fetch and process running promotional offers similarly
        # Add your Offer model loops here if needed...
        
        if documents_to_index:
            from vector_store import add_documents_to_store
            add_documents_to_store(documents_to_index)
            print(f"Successfully synced {len(documents_to_index)} database records to Vector Store.")
        else:
            print("No records found in the SQL database to sync.")
            
    except Exception as e:
        print(f"Error compiling syncing database records: {str(e)}")
    finally:
        db_session.close()

if __name__ == "__main__":
    print("Starting database ingestion sync pipeline...")
    sync_database_to_vector_store()