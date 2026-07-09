import sys
import os
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.database import SessionLocal
from app.models.product import Offer, Product

def seed_offers():
    print("🏷️ Seeding offers table...")
    db: Session = SessionLocal()
    try:
        products = db.query(Product).all()
        if not products:
            print("❌ Cannot seed offers. Please seed products first!")
            return

        now = datetime.utcnow()
        offers = [
            # Drinks Offers
            Offer(product_id=products[0].id, discount_percentage=Decimal("15.00"), description="Premium Coffee Promotion", start_date=now - timedelta(days=2), end_date=now + timedelta(days=4), is_active=True),
            Offer(product_id=products[3].id, discount_percentage=Decimal("25.00"), description="Summer Refreshing Juices", start_date=now - timedelta(days=1), end_date=now + timedelta(days=7), is_active=True),
            Offer(product_id=products[11].id, discount_percentage=Decimal("20.00"), description="Herbal Wellness Week", start_date=now - timedelta(days=1), end_date=now + timedelta(days=5), is_active=True),

            # Personal Care Offers
            Offer(product_id=products[13].id, discount_percentage=Decimal("18.00"), description="Skincare Summer Sale", start_date=now - timedelta(days=3), end_date=now + timedelta(days=6), is_active=True),
            Offer(product_id=products[17].id, discount_percentage=Decimal("30.00"), description="Sunscreen Protection Deal", start_date=now - timedelta(days=1), end_date=now + timedelta(days=4), is_active=True),

            # Household Offers
            Offer(product_id=products[36].id, discount_percentage=Decimal("20.00"), description="Clean Home Essentials", start_date=now - timedelta(days=2), end_date=now + timedelta(days=4), is_active=True),

            # Bakery & Fresh Offers
            Offer(product_id=products[48].id, discount_percentage=Decimal("10.00"), description="Fresh Bakery Daily Deal", start_date=now - timedelta(days=1), end_date=now + timedelta(days=1), is_active=True),

            # Snacks & Sweets Offers
            Offer(product_id=products[60].id, discount_percentage=Decimal("20.00"), description="Snack Attack Promotion", start_date=now - timedelta(days=1), end_date=now + timedelta(days=6), is_active=True),
            Offer(product_id=products[70].id, discount_percentage=Decimal("15.00"), description="Movie Night Snacks", start_date=now - timedelta(hours=10), end_date=now + timedelta(days=4), is_active=True),

            # Baby Care Offers
            Offer(product_id=products[73].id, discount_percentage=Decimal("18.00"), description="Baby Diaper Mega Save", start_date=now - timedelta(days=3), end_date=now + timedelta(days=5), is_active=True),
            Offer(product_id=products[78].id, discount_percentage=Decimal("22.00"), description="Gentle Baby Care Week", start_date=now - timedelta(days=1), end_date=now + timedelta(days=7), is_active=True)
        ]
        db.add_all(offers)
        db.commit()
        print("✅ Offers table seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding offers: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_offers()