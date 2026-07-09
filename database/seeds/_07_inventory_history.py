import sys
import os
from sqlalchemy.orm import Session

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.database import SessionLocal
from app.models.product import Product
from app.models.user import User

# Dynamically import InventoryHistory directly from your existing application models
try:
    from app.models.inventory import InventoryHistory
except ImportError:
    from app.models.user import InventoryHistory

def seed_inventory_history():
    print("🪵 Seeding inventory_history table using live database instances...")
    db: Session = SessionLocal()
    try:
        # Prevent adding duplicate logs if ran multiple times
        if db.query(InventoryHistory).first():
            print("⚠️ Inventory history already contains records. Skipping.")
            return

        # Fetch the products and admin user that you already populated
        products = db.query(Product).all()
        admin = db.query(User).filter(User.role == "admin").first()
        
        if not products:
            print("❌ Cannot seed history. No products found in your database!")
            return
        if not admin:
            print("❌ Cannot seed history. No admin user found in your database!")
            return

        # Build records utilizing dynamic references to your existing IDs
        logs = [
            InventoryHistory(
                product_id=products[0].id, 
                change_type="restock", 
                quantity=50, 
                previous_stock=20, 
                new_stock=70, 
                changed_by=admin.id
            ),
            InventoryHistory(
                product_id=products[1].id, 
                change_type="manual_update", 
                quantity=10, 
                previous_stock=30, 
                new_stock=40, 
                changed_by=admin.id
            )
        ]
        
        db.add_all(logs)
        db.commit()
        print("✅ Inventory history table seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding inventory tracking: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_inventory_history()