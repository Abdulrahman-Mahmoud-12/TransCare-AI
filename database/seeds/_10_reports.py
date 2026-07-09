import sys
import os
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Session

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.database import SessionLocal, Base
from app.models.user import User

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, autoincrement=True)
    generated_by = Column(Integer, ForeignKey("users.id"))
    report_type = Column(String(50)) # daily, weekly, monthly, custom
    file_path = Column(String(255))
    summary = Column(Text)

def seed_reports():
    print("📈 Seeding reports table...")
    db: Session = SessionLocal()
    try:
        admin = db.query(User).filter(User.role == "admin").first()
        if not admin:
            print("❌ Cannot seed reports. An admin account record is required.")
            return

        reports = [
            Report(generated_by=admin.id, report_type="daily", file_path="/storage/reports/daily_report_v1.pdf", summary="Sales tracking target reached. Category 'Dairy & Eggs' was the highest performer across store branches."),
            Report(generated_by=admin.id, report_type="weekly", file_path="/storage/reports/weekly_report_w24.pdf", summary="Weekly overview displays a healthy 8% profit margin growth.")
        ]
        db.add_all(reports)
        db.commit()
        print("✅ Reports table seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding reports: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_reports()