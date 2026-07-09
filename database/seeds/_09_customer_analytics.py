import sys
import os
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.database import SessionLocal
from app.models.user import User
from app.models.product import Product
from app.models.category import Category

# Dynamically import CustomerAnalytics from your core application models
try:
    from app.models.customer import CustomerAnalytics
except ImportError:
    from app.models.user import CustomerAnalytics

def seed_customer_analytics():
    print("📊 Seeding customer_analytics table using live application models...")
    db: Session = SessionLocal()
    try:
        # Prevent duplicate logs if run multiple times
        if db.query(CustomerAnalytics).first():
            print("⚠️ Customer analytics table already contains records. Skipping.")
            return

        # Fetch live records from your database
        customers = db.query(User).filter(User.role == "customer").all()
        products = db.query(Product).all()
        categories = db.query(Category).all()
        
        if not customers or not products or not categories:
            print("❌ Cannot seed analytics. Core dependencies (Users, Products, Categories) are missing!")
            return

        # Map metrics cleanly using existing database records
        analytics_entries = [
            CustomerAnalytics(
                customer_id=customers[0].id, 
                total_orders=5, 
                total_spent=Decimal("450.50"), 
                favorite_category=categories[0].id, 
                favorite_product=products[0].id, 
                segment="Loyal Shopper", 
                return_probability=Decimal("92.50"), 
                last_purchase=datetime.utcnow() - timedelta(days=2)
            ),
            CustomerAnalytics(
                customer_id=customers[1].id if len(customers) > 1 else customers[0].id, 
                total_orders=1, 
                total_spent=Decimal("95.00"), 
                favorite_category=categories[1].id if len(categories) > 1 else categories[0].id, 
                favorite_product=products[1].id if len(products) > 1 else products[0].id, 
                segment="New/At-Risk", 
                return_probability=Decimal("34.10"), 
                last_purchase=datetime.utcnow() - timedelta(days=12)
            )
        ]
        
        db.add_all(analytics_entries)
        db.commit()
        print("✅ Customer analytics table seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding metrics analytics: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_customer_analytics()