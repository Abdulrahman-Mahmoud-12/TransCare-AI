import sys
import os
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import Session
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.database import SessionLocal, Base

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

def seed_categories():
    print("🗂️ Seeding comprehensive catalog categories...")
    db: Session = SessionLocal()
    try:
        categories = [
            # Your exact requested categories
            Category(name="Drinks", description="Carbonated sodas, juices, organic milk, premium mineral waters, energy drinks, and roasted coffees.", image_url="/static/images/cat-drinks.png"),
            Category(name="Personal Care", description="Shampoos, conditioners, skin lotions, luxury soaps, oral hygiene, and grooming items.", image_url="/static/images/cat-personal.png"),
            Category(name="Health", description="Over-the-counter medicines, vitamins, dietary supplements, first aid supplies, and wellness products.", image_url="/static/images/cat-health.png"),
            Category(name="Household", description="Surface cleaning sprays, laundry detergents, fabric softeners, trash bags, and home supplies.", image_url="/static/images/cat-household.png"),
            Category(name="Bakery & Fresh", description="Oven-fresh bread loaves, breakfast croissants, baguettes, muffins, and freshly baked pastry buns.", image_url="/static/images/cat-bakery.png"),
            Category(name="Snacks & Sweets", description="Crispy potato chips, pretzels, crackers, milk chocolate bars, and gummy candies.", image_url="/static/images/cat-snacks.png"),
            Category(name="Baby Care", description="Gentle baby diapers, sensitive skin wet wipes, infant formula milks, and baby lotion lotions.", image_url="/static/images/cat-baby.png")
        ]
        db.add_all(categories)
        db.commit()
        print("✅ Categories table seeded successfully with 7 total segments.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding categories: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_categories()