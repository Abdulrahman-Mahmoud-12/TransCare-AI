import sys
import os
import random
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.database import SessionLocal
from app.models.user import User
from app.models.purchase import Order

def seed_orders():
    print("🛒 Seeding orders table...")
    db: Session = SessionLocal()
    try:
        customers = db.query(User).filter(User.role == "customer").all()
        if not customers:
            print("❌ Cannot seed orders. Please seed users first!")
            return

        now = datetime.utcnow()
        for idx, cust in enumerate(customers):
            ord_entry = Order(
                customer_id=cust.id,
                total_price=Decimal(random.randint(100, 300)),
                total_discount=Decimal("5.00"),
                payment_method=random.choice(["cash", "credit_card", "wallet"]),
                status="completed",
                created_at=now - timedelta(days=random.randint(1, 10))
            )
            db.add(ord_entry)
        db.commit()
        print("✅ Orders table seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding orders: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_orders()