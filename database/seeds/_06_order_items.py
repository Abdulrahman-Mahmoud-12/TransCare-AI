import sys
import os
from decimal import Decimal
from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import Session

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.database import SessionLocal, Base
from app.models.purchase import Order
from app.models.product import Product

try:
    from app.models.purchase import OrderItem
except ImportError:
    class OrderItem(Base):
        __tablename__ = "order_items"
        id = Column(Integer, primary_key=True, autoincrement=True)
        order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
        product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
        quantity = Column(Integer, nullable=False)
        unit_price = Column(Numeric(10, 2), nullable=False)
        discount = Column(Numeric(10, 2), default=0)
        subtotal = Column(Numeric(12, 2), nullable=False)

def seed_order_items():
    print("🛍️ Seeding order_items table...")
    db: Session = SessionLocal()
    try:
        orders = db.query(Order).all()
        products = db.query(Product).all()
        if not orders or not products:
            print("❌ Cannot seed order items. Ensure orders and products tables are seeded!")
            return

        for o in orders:
            p1 = random.choice(products)
            p2 = random.choice(products)
            
            item1 = OrderItem(order_id=o.id, product_id=p1.id, quantity=2, unit_price=p1.price, discount=Decimal("2.50"), subtotal=Decimal((p1.price * 2) - Decimal("2.50")))
            item2 = OrderItem(order_id=o.id, product_id=p2.id, quantity=1, unit_price=p2.price, discount=Decimal("0.00"), subtotal=Decimal(p2.price))
            db.add_all([item1, item2])
        db.commit()
        print("✅ Order Items table seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding order items: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import random
    seed_order_items()