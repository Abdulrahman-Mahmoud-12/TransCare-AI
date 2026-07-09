import sys
import os
from datetime import datetime
from sqlalchemy.orm import Session

# Add project root to path to ensure app imports work seamlessly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.database import SessionLocal, Base, engine
from app.models.user import User

def seed_users():
    print("👥 Seeding users table...")
    db: Session = SessionLocal()
    try:
        # plain text password: 'password123'
        pwd_hash = "$2b$12$SoakfPKBeu4NvaNsCShgfu5nMXFNP1rccOZdwliNIW81e6VrmZj8q"
        
        users = [
            User(full_name="Abdelrahman Mahmoud", email="admin.abdelrahman@retailiq.com", password_hash=pwd_hash, role="admin", admin_id="ADM-001", is_active=True),
            User(full_name="Menna Hany", email="admin.menna@retailiq.com", password_hash=pwd_hash, role="admin", admin_id="ADM-010", is_active=True),
            User(full_name="Omar Alaa", email="customer.omaralaa@retailiq.com", password_hash=pwd_hash, role="customer", customer_category="Regular", is_active=True),
            User(full_name="Farida Ahmed", email="customer.faridaahmed@retailiq.com", password_hash=pwd_hash, role="customer", customer_category="Churn Risk", is_active=True),
            User(full_name="Salma Ali", email="customer.salmaali@retailiq.com", password_hash=pwd_hash, role="customer", customer_category="New", is_active=True),
            User(full_name="Mohammed Ebrahim", email="customer.mohammedebrahim@retailiq.com", password_hash=pwd_hash, role="customer", customer_category="Regular", is_active=True),
            User(full_name="Nada Adel", email="customer.nadaadel@retailiq.com", password_hash=pwd_hash, role="customer",customer_category="VIP",  is_active=True),
            User(full_name="Youssef Helmy", email="customer.youssefhelmy@retailiq.com", password_hash=pwd_hash, role="customer", customer_category="Regular", is_active=True)
        ]
        db.add_all(users)
        db.commit()
        print("✅ Users table seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding users: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()