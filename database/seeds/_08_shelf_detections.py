import sys
import os
from decimal import Decimal
from sqlalchemy.orm import Session

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.database import SessionLocal
from app.models.user import User

# Dynamically import ShelfDetection from your application's core models
try:
    from app.models.shelf import ShelfDetection
except ImportError:
    # Fallback checking if it was declared in the user module
    from app.models.user import ShelfDetection

def seed_shelf_detections():
    print("👁️ Seeding shelf_detections table using live database models...")
    db: Session = SessionLocal()
    try:
        # Prevent duplicate entries if the script is run multiple times
        if db.query(ShelfDetection).first():
            print("⚠️ Shelf detections table already contains records. Skipping.")
            return

        # Fetch the admin user you seeded in file 01
        admin = db.query(User).filter(User.role == "admin").first()
        admin_id = admin.id if admin else None

        if not admin_id:
            print("⚠️ Warning: No admin account found. 'uploaded_by' will be set to NULL.")

        # Build records mapping smoothly to your existing application properties
        detections = [
            ShelfDetection(
                uploaded_by=admin_id, 
                image_path="/storage/uploads/shelf_raw_01.jpg", 
                processed_image_path="/storage/detected_images/shelf_bbox_01.jpg", 
                total_products=85, 
                empty_spaces=15, 
                occupancy_percentage=Decimal("85.00")
            ),
            ShelfDetection(
                uploaded_by=admin_id, 
                image_path="/storage/uploads/shelf_raw_02.jpg", 
                processed_image_path="/storage/detected_images/shelf_bbox_02.jpg", 
                total_products=42, 
                empty_spaces=58, 
                occupancy_percentage=Decimal("42.00")
            )
        ]
        
        db.add_all(detections)
        db.commit()
        print("✅ Shelf Detections table seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding shelf detections: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_shelf_detections()